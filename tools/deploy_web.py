#!/usr/bin/env python3
"""Explicit Pages/R2 preview, verification, promotion, and rollback of Web builds."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request

from export_web import source_files, TEMPLATE_SHA256
from web_shell import render as render_shell

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / 'hosting/production'
PROJECT = 'hush-basin'
BUCKET = 'hush-basin-artifacts'
ORIGIN = 'https://hush-basin.pages.dev'
LARGE = {'index.wasm', 'index.pck'}
POLICY = 'public, max-age=31536000, immutable, no-transform'
ENGINE = '4.7.1.stable.official.a13da4feb'


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':')).encode()


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n')


def wrangler(work, *args, allow_missing=False):
    node = os.environ.get('HUSH_NODE') or shutil.which('node')
    require(node, 'Node >=22 required; set HUSH_NODE to an installed executable')
    cli = ROOT / 'hosting/cloudflare/node_modules/wrangler/bin/wrangler.js'
    require(cli.is_file(), 'Run npm --prefix hosting/cloudflare ci first')
    run = subprocess.run([node, str(cli), *args], cwd=work, text=True,
                         stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    print(run.stdout, flush=True)
    if run.returncode:
        if allow_missing and 'The specified key does not exist.' in run.stdout:
            return None
        raise RuntimeError('Wrangler failed; no later deployment step executed')
    return run.stdout


def fetch(url, destination=None, method='GET'):
    request = urllib.request.Request(url, method=method, headers={
        'User-Agent': 'Hush-Basin-Hosting-Proof/1.0', 'Accept-Encoding': 'identity',
    })
    failures = []
    for attempt in range(3):
        try:
            response = urllib.request.urlopen(request, timeout=180)
            break
        except urllib.error.HTTPError as error:
            failures.append({'status': error.code, 'headers': dict(error.headers)})
            print(f'HTTP attempt {attempt + 1}: {error.code} {url}', flush=True)
            if error.code < 500 or attempt == 2:
                raise
            time.sleep(5)
    with response:
        if destination:
            with destination.open('wb') as output:
                shutil.copyfileobj(response, output, 1024 * 1024)
            body = None
        else:
            body = response.read()
        return body, {'url': url, 'status': response.status, 'prior_http_failures': failures,
                      'headers': {k.lower(): v for k, v in response.headers.items()}}


def current_release(work):
    deployments = json.loads(wrangler(work, 'pages', 'deployment', 'list',
                                     '--project-name', PROJECT, '--environment', 'production', '--json'))
    if not deployments:
        return None
    body, _ = fetch(ORIGIN + '/production.json')
    return json.loads(body)


def validate_manifest(manifest):
    require(manifest['engine'] == ENGINE, 'Wrong Godot version')
    require(manifest['template_sha256'] == TEMPLATE_SHA256, 'Wrong export template')
    require(not manifest.get('diagnostic_entry'), 'Diagnostic exports cannot be promoted')
    files = manifest['files']
    names = [f['name'] for f in files]
    require(names == sorted(set(names)), 'File inventory must be unique and sorted')
    require({'index.html', 'index.js', *LARGE}.issubset(names), 'Missing game files')
    for entry in files:
        require(re.fullmatch(r'index[.a-zA-Z0-9_-]*', entry['name']), 'Unsafe artifact name')
        require(re.fullmatch(r'[0-9a-f]{64}', entry['sha256']), 'Invalid SHA-256')
        require(entry['bytes'] > 0, 'Empty artifact')
    require(manifest['build_id'] == hashlib.sha256(canonical(files)).hexdigest(), 'Build ID mismatch')


def inventory(work):
    paths = [work / 'wrangler.jsonc', work / 'builds.json']
    paths += [p for directory in ('site', 'functions') for p in (work / directory).rglob('*') if p.is_file()]
    return {str(p.relative_to(work)): digest(p) for p in sorted(paths)}


def stage(work, release):
    site = work / 'site'
    site.mkdir()
    write_json(work / 'builds.json', release['builds'])
    write_json(site / 'production.json', release)
    shutil.copyfile(CONFIG / 'wrangler.jsonc', work / 'wrangler.jsonc')
    function = work / 'functions/builds/[build]/[file].js'
    function.parent.mkdir(parents=True)
    shutil.copyfile(CONFIG / 'artifact.js', function)
    write_json(site / '_routes.json', {'version': 1,
               'include': ['/builds/*/index.wasm', '/builds/*/index.pck'], 'exclude': []})
    (site / '_redirects').write_text(f"/ /builds/{release['current_build_id']}/ 302\n")
    (site / '_headers').write_text(
        '/*\n  X-Robots-Tag: noindex, nofollow, noarchive\n  X-Content-Type-Options: nosniff\n'
        '/production.json\n  Cache-Control: no-store\n'
        '/builds/*\n  Cache-Control: ' + POLICY + '\n')
    (site / '404.html').write_text('<!doctype html><title>Not found</title>Not found\n')


def verify(origin, work, release, label):
    evidence = work / label
    evidence.mkdir(exist_ok=False)
    remote, _ = fetch(origin + '/production.json')
    require(json.loads(remote) == release, 'Served release manifest mismatch')
    results = []
    for shell, entry in release.get('shells', {}).items():
        path = evidence / (shell + '-shell.html')
        _, result = fetch(origin + f'/shells/{shell}/index.html', path)
        result.update(bytes=path.stat().st_size, sha256=digest(path))
        require(result['sha256'] == shell and result['bytes'] == entry['bytes'], 'Shell identity differs')
        results.append(result)
        write_json(evidence / 'responses.json', results)
    for build, manifest in release['builds'].items():
        for entry in manifest['files']:
            url = origin + f"/builds/{build}/{entry['name']}"
            if build != release['current_build_id'] and entry['name'] in LARGE:
                _, result = fetch(url, method='HEAD')
                require(result['headers'].get('x-hush-sha256') == entry['sha256'], 'Old large artifact identity changed')
            else:
                path = evidence / (build + '-' + entry['name'])
                _, result = fetch(url, path)
                result.update(bytes=path.stat().st_size, sha256=digest(path))
                require(result['bytes'] == entry['bytes'] and result['sha256'] == entry['sha256'], 'Served bytes differ: ' + url)
            if entry['name'] in LARGE:
                h = result['headers']
                require(h.get('content-type') == ('application/wasm' if entry['name'].endswith('.wasm') else 'application/octet-stream'), 'Wrong MIME')
                require(h.get('content-length') == str(entry['bytes']), 'Wrong length')
                require(h.get('cache-control') == POLICY, 'Wrong cache policy')
            results.append(result)
            write_json(evidence / 'responses.json', results)
    return results


def deploy(work, branch, source):
    output = wrangler(work, 'pages', 'deploy', '--project-name', PROJECT,
                      '--branch', branch, '--commit-hash', source, '--commit-dirty=false')
    match = re.search(r'https://[0-9a-f]{8}\.' + re.escape(PROJECT) + r'\.pages\.dev', output)
    require(match, 'Wrangler did not return a unique deployment URL')
    return match[0]


def prepare(args):
    work = args.work.resolve()
    work.mkdir(parents=True, exist_ok=False)
    previous = current_release(work)
    if args.bootstrap:
        require(previous is None, 'Bootstrap refused: production already exists')
    else:
        require(previous is not None, 'Production manifest missing; bootstrap is only for first promotion')
    builds = previous['builds'].copy() if previous else {}
    for manifest in builds.values():
        validate_manifest(manifest)
    exported = None
    if args.rollback_build:
        require(args.rollback_build in builds, 'Rollback target not in retained registry')
        build = args.rollback_build
    else:
        exported = args.export.resolve() if args.export else work / 'export'
        if not args.export:
            subprocess.run([sys.executable, str(ROOT / 'tools/export_web.py'), '--output', str(exported)], check=True)
        record = json.loads((exported / 'build.json').read_text())
        require(record['engine'] == ENGINE and not record['diagnostic_entry'], 'Not an exact full-game export')
        require({str(p.relative_to(ROOT / 'game')) for p in source_files()} == set(record['source_sha256']), 'Export source inventory differs from current game')
        for name, sha in record['source_sha256'].items():
            path = ROOT / 'game' / name
            require(path.resolve().is_relative_to(ROOT / 'game'), 'Unsafe source path')
            require(digest(path) == sha, 'Export source differs from working game: ' + name)
        files = [{k: entry[k] for k in ('name', 'bytes', 'sha256')} for entry in record['files']]
        build = hashlib.sha256(canonical(files)).hexdigest()
        manifest = {'build_id': build, 'export_source_commit': record['source_commit'],
                    'engine': record['engine'], 'template_sha256': record['template_sha256'],
                    'diagnostic_entry': False, 'files': files}
        validate_manifest(manifest)
        if build in builds:
            require(builds[build]['files'] == files, 'Existing build inventory differs')
        else:
            builds[build] = manifest
        for entry in files:
            path = exported / 'web' / entry['name']
            require(path.stat().st_size == entry['bytes'] and digest(path) == entry['sha256'], 'Export artifact mismatch')
    source = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    release = {'schema': 'hush-basin.production.v1', 'current_build_id': build,
               'source_commit': builds[build]['export_source_commit'], 'builds': builds}
    stage(work, release)
    for bid, manifest in builds.items():
        folder = work / 'site/builds' / bid
        folder.mkdir(parents=True)
        for entry in manifest['files']:
            name = entry['name']
            if name in LARGE:
                if exported and bid == build:
                    key = f'{BUCKET}/builds/{bid}/{name}'
                    existing = work / ('existing-' + name)
                    found = wrangler(work, 'r2', 'object', 'get', key, '--remote', '--file', str(existing), allow_missing=True)
                    if found is not None:
                        require(digest(existing) == entry['sha256'] and existing.stat().st_size == entry['bytes'], 'Immutable R2 key has different bytes; refusing overwrite')
                    else:
                        wrangler(work, 'r2', 'object', 'put', key, '--remote', '--file', str(exported / 'web' / name),
                                 '--content-type', 'application/wasm' if name.endswith('.wasm') else 'application/octet-stream', '--cache-control', POLICY)
                continue
            require(entry['bytes'] <= 25 * 1024 * 1024, 'Small asset exceeds Pages limit')
            if exported and bid == build:
                shutil.copyfile(exported / 'web' / name, folder / name)
            else:
                fetch(ORIGIN + f'/builds/{bid}/{name}', folder / name)
            require(digest(folder / name) == entry['sha256'], 'Retained small asset mismatch')
        write_json(folder / 'build-manifest.json', manifest)
    # Presentation versions have their own identities. Original /builds files
    # and R2 objects remain unchanged, including the generated index.html.
    shells = previous.get('shells', {}).copy() if previous else {}
    for sid, entry in shells.items():
        require(re.fullmatch(r'[0-9a-f]{64}', sid), 'Unsafe shell ID')
        target = work / 'site/shells' / sid / 'index.html'
        target.parent.mkdir(parents=True)
        fetch(ORIGIN + f'/shells/{sid}/index.html', target)
        require(digest(target) == sid and target.stat().st_size == entry['bytes'], 'Retained shell mismatch')
    content = render_shell((work / 'site/builds' / build / 'index.html').read_text(), build)
    sid = hashlib.sha256(content).hexdigest()
    target = work / 'site/shells' / sid / 'index.html'
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(content)
    shells[sid] = {'build_id': build, 'bytes': len(content), 'sha256': sid}
    release.update(shells=shells, current_shell_id=sid)
    write_json(work / 'site/production.json', release)
    (work / 'site/_redirects').write_text(f'/ /shells/{sid}/ 302\n')
    with (work / 'site/_headers').open('a') as headers:
        headers.write('/shells/*\n  Cache-Control: ' + POLICY + '\n')
    candidate = {'release': release, 'previous': previous, 'deployment_source_commit': source, 'inventory': inventory(work)}
    write_json(work / 'candidate.json', candidate)
    url = deploy(work, 'candidate-' + build[:16], source)
    verify(url, work, release, 'preview-http')
    candidate.update(preview_url=url, http_verified=True)
    write_json(work / 'candidate.json', candidate)
    print('Preview verified:', url, '\nSmoke-test this URL, then explicitly run promote with --confirm-playable.')


def promote(args):
    work = args.work.resolve()
    candidate = json.loads((work / 'candidate.json').read_text())
    require(args.confirm_playable, 'Play the exact preview first; promotion requires --confirm-playable')
    require(candidate.get('http_verified'), 'Preview HTTP verification missing')
    require(inventory(work) == candidate['inventory'], 'Candidate files changed after preview verification')
    require(current_release(work) == candidate['previous'], 'Production changed since preview; create a new candidate preserving its registry')
    url = deploy(work, 'production', candidate['deployment_source_commit'])
    write_json(work / 'deployment.json', {'status': 'DEPLOYED_AWAITING_HTTP_VERIFICATION',
               'deployment_url': url, 'current_build_id': candidate['release']['current_build_id']})
    verify(url, work, candidate['release'], 'production-http')
    write_json(work / 'promotion.json', {'status': 'PROMOTED_HTTP_VERIFIED', 'deployment_url': url,
               'preview_url': candidate['preview_url'], 'current_build_id': candidate['release']['current_build_id'],
               'source_commit': candidate['release']['source_commit'], 'playable_confirmed_by_operator': True})
    print('Production deployment verified:', url)


def recheck(args):
    work = args.work.resolve()
    candidate = json.loads((work / 'candidate.json').read_text())
    require(inventory(work) == candidate['inventory'], 'Candidate files changed after preview verification')
    require(re.fullmatch(r'[a-zA-Z0-9_-]+', args.label), 'Use a simple new evidence label')
    verify(args.origin.rstrip('/'), work, candidate['release'], args.label)
    print('HTTP identity verified:', args.origin)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    subs = parser.add_subparsers(dest='command', required=True)
    preview = subs.add_parser('preview')
    preview.add_argument('--work', type=Path, required=True)
    group = preview.add_mutually_exclusive_group()
    group.add_argument('--export', type=Path, help='Existing export output containing build.json and web/')
    group.add_argument('--rollback-build', help='Retained build ID to make current without dropping newer URLs')
    preview.add_argument('--bootstrap', action='store_true')
    promotion = subs.add_parser('promote')
    promotion.add_argument('--work', type=Path, required=True)
    promotion.add_argument('--confirm-playable', action='store_true')
    check = subs.add_parser('verify', help='Independently check a deployed origin without publishing again')
    check.add_argument('--work', type=Path, required=True)
    check.add_argument('--origin', required=True)
    check.add_argument('--label', required=True, help='New evidence directory name')
    args = parser.parse_args()
    {'preview': prepare, 'promote': promote, 'verify': recheck}[args.command](args)


if __name__ == '__main__':
    main()
