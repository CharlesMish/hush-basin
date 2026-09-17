#!/usr/bin/env python3
"""Verify and stage the recorded export without rebuilding or rewriting it."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]
HOSTING = ROOT / 'hosting/cloudflare'


def sha256(path):
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('export', type=Path, help='Web export directory containing index.html')
    args = parser.parse_args()
    manifest = json.loads((HOSTING / 'build-manifest.json').read_text())
    exported = args.export.resolve()
    expected = {entry['name'] for entry in manifest['files']}
    assert {p.name for p in exported.iterdir() if p.is_file()} == expected, 'Unexpected file inventory'
    for entry in manifest['files']:
        path = exported / entry['name']
        assert path.stat().st_size == entry['bytes'], f'Size mismatch: {path}'
        assert sha256(path) == entry['sha256'], f'Hash mismatch: {path}'

    site = HOSTING / 'site'
    assert not site.exists(), f'Remove or archive previous generated staging directory first: {site}'
    prefix = f"/builds/{manifest['build_id']}"
    destination = site / prefix.lstrip('/')
    destination.mkdir(parents=True)
    for entry in manifest['files']:
        if entry['name'] not in ('index.wasm', 'index.pck'):
            assert entry['bytes'] <= 25 * 1024 * 1024
            shutil.copyfile(exported / entry['name'], destination / entry['name'])
    shutil.copyfile(HOSTING / 'build-manifest.json', destination / 'build-manifest.json')
    (site / '_routes.json').write_text(json.dumps({
        'version': 1, 'include': ['/builds/*/index.wasm', '/builds/*/index.pck'], 'exclude': []
    }, indent=2) + '\n')
    (site / '_headers').write_text(
        '/*\n  X-Robots-Tag: noindex, nofollow, noarchive\n'
        '  X-Content-Type-Options: nosniff\n'
        f'{prefix}/*\n  Cache-Control: public, max-age=31536000, immutable, no-transform\n'
    )
    (site / '_redirects').write_text(f'/ {prefix}/ 302\n')
    (site / '404.html').write_text('<!doctype html><title>Not found</title>Not found\n')
    print(json.dumps({'site': str(site), 'path': prefix + '/', 'verified_files': len(expected),
                      'raw_export_bytes': sum(e['bytes'] for e in manifest['files'])}, indent=2))


if __name__ == '__main__':
    main()
