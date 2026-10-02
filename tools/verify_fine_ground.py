#!/usr/bin/env python3
"""Versioned Fine Ground v1 checks; never substitutes or installs Godot.

Default: source/data checks against the recorded baseline commit (requires Git).
--native additionally requires the exact engine and runs disposable baseline and
successor copies on the same host: import/parse, matched 1,260-tick C1 movement,
terrain/collision identity, current world/Run/vehicle fixtures, shader-error log
scan and gameplay-camera captures. Evidence goes to a new --evidence directory.
"""
from __future__ import annotations

import argparse, hashlib, io, json, math, re, shutil, struct, subprocess, sys, tarfile, tempfile, zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASELINE_COMMIT = 'df221870b45de53e4ebb5ea8889b6cf1114054c6'
CONFIG = ROOT / 'game/presentation/fine_ground_v1.json'
FOLDER = ROOT / 'game/presentation/fine_ground'
LOADER = ROOT / 'game/scripts/fine_ground.gd'
# Baseline files this successor may change; everything else tracked at the
# baseline commit must be byte-identical.
CHANGED = {'AGENTS.md', 'README.md', 'game/AGENTS.md', 'game/project.godot',
           'game/scripts/p1a_world_builder.gd', 'game/scripts/p1a_world_gate.gd'}
ADDED = {'FINE_GROUND_V1_AUTHORITY.md', 'docs/FINE_GROUND_V1.md', 'game/presentation/fine_ground_v1.json',
         'game/presentation/fine_ground/.gdignore', 'game/presentation/fine_ground/fine_ground_detail.png',
         'game/presentation/fine_ground/fine_ground_index.json', 'game/scripts/fine_ground.gd',
         'game/scripts/fine_ground.gd.uid', 'game/tests/fine_ground_runtime.gd', 'game/tests/fine_ground_runtime.gd.uid',
         'tools/generate_fine_ground.py', 'tools/verify_fine_ground.py'}
PNG_BUDGET = 512 * 1024
RESIDENT_BUDGET = 1024 * 1024
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT)


def read_rgba(path):
    b = path.read_bytes(); pos = 8; idat = b''; w = h = 0
    while pos < len(b):
        n, = struct.unpack('>I', b[pos:pos + 4]); kind = b[pos + 4:pos + 8]; body = b[pos + 8:pos + 8 + n]; pos += 12 + n
        if kind == b'IHDR':
            w, h, depth, color = struct.unpack('>IIBB', body[:10]); assert depth == 8 and color == 6
        elif kind == b'IDAT':
            idat += body
    raw = zlib.decompress(idat); stride = w * 4
    # The generator writes filter 0 only; any other filter means foreign bytes.
    assert all(raw[y * (stride + 1)] == 0 for y in range(h))
    return w, h, b''.join(raw[y * (stride + 1) + 1:(y + 1) * (stride + 1)] for y in range(h))


def static_checks():
    checks = []
    def check(id, ok, detail=None): checks.append({'id': id, 'pass': bool(ok), 'detail': detail})
    tracked = {}
    for line in git('ls-tree', '-r', BASELINE_COMMIT).decode().splitlines():
        meta, name = line.split('\t', 1); tracked[name] = meta.split()[2]
    for name, blob in sorted(tracked.items()):
        if name in CHANGED:
            continue
        path = ROOT / name
        check('UNCHANGED:' + name, path.is_file() and git('hash-object', str(path)).decode().strip() == blob)
    for name in sorted(CHANGED):
        check('DECLARED_CHANGE_EXISTS:' + name, (ROOT / name).is_file() and name in tracked)
    current = set(git('ls-files', '--cached', '--others', '--exclude-standard').decode().splitlines())
    extra = sorted(current - set(tracked) - ADDED)
    check('NO_UNDECLARED_FILES', not extra, extra)
    check('DECLARED_ADDITIONS_PRESENT', all((ROOT / n).is_file() for n in ADDED), sorted(n for n in ADDED if not (ROOT / n).is_file()))

    cfg = json.loads(CONFIG.read_text()); index = json.loads((FOLDER / 'fine_ground_index.json').read_text())
    check('CONFIG_BINDING', index['config_sha256'] == sha(CONFIG))
    for name, digest in index['artifacts'].items():
        check('GENERATED:' + name, sha(FOLDER / name) == digest)
    png = FOLDER / 'fine_ground_detail.png'
    check('PNG_BUDGET', png.stat().st_size <= PNG_BUDGET, png.stat().st_size)
    check('RESIDENT_BUDGET', index['resident_texture_bytes_upper_bound'] <= RESIDENT_BUDGET, index['resident_texture_bytes_upper_bound'])
    w, h, data = read_rgba(png); n = cfg['detail']['resolution']
    check('TILE_SIZE', (w, h) == (n, n) == tuple(index['size']), [w, h])
    # Signed channels are centred so they redistribute, not shift, macro tone.
    means = [sum(data[k::4]) / (w * h) for k in range(4)]
    check('ZERO_MEAN_SIGNED_CHANNELS', all(abs(m - 127.5) <= 4.0 for m in means), [round(m, 2) for m in means])
    # Seamless: wrap-edge steps match ordinary interior neighbour steps.
    def step(a, b): return sum(abs(data[a * 4 + k] - data[b * 4 + k]) for k in range(4))
    interior = sum(step(y * w + x, y * w + x + 1) for y in range(h) for x in range(w - 1)) / (h * (w - 1))
    seam_x = sum(step(y * w + w - 1, y * w) for y in range(h)) / h
    seam_z = sum(step((h - 1) * w + x, x) for x in range(w)) / w
    check('SEAMLESS_TILE', seam_x <= interior * 1.35 and seam_z <= interior * 1.35, {'interior': round(interior, 3), 'seam_u': round(seam_x, 3), 'seam_v': round(seam_z, 3)})
    s = cfg['shader']
    check('FADE_ORDER', 0 < s['fade_start_m'] < s['fade_end_m'] <= 120)
    check('BOUNDED_STRENGTHS', all(0 <= s[k] <= 0.35 for k in ['mineral_albedo', 'asphalt_albedo']) and all(0 <= s[k] <= 0.6 for k in ['mineral_relief', 'asphalt_relief']))
    check('NON_ALIGNED_TILES', abs(s['far_tile_m'] / s['near_tile_m'] - round(s['far_tile_m'] / s['near_tile_m'])) > 0.1)
    loader = LOADER.read_text()
    d = cfg['display']
    check('BOUNDED_DISPLAY', d['msaa_3d'] in (0, 1, 2) and isinstance(d['debanding'], bool) and 'msaa_3d' in loader and 'use_debanding' in loader, d)
    declared = set(re.findall(r'uniform\s+\w+\s+(\w+)', loader))
    check('CONFIG_UNIFORMS_DECLARED', set(s) <= declared, sorted(set(s) - declared))
    check('PRESENTATION_ONLY_LOADER', all(t not in loader for t in ['add_child(', 'craft', 'Collision', 'PhysicsBody', 'StaticBody3D', 'Area3D', 'RayCast', 'Input.', 'telemetry']))
    check('NO_SIDE_EFFECT_ASSERT', 'assert(' not in loader)
    builder = (ROOT / 'game/scripts/p1a_world_builder.gd').read_text(); gate = (ROOT / 'game/scripts/p1a_world_gate.gd').read_text()
    check('TERRAIN_MATERIAL_WIRED', 'preload("res://scripts/fine_ground.gd").material()' in builder and 'quiet_surfaces.gd").material()' not in builder)
    check('ATMOSPHERE_AFTER_WEATHER_LIGHTING', gate.index('fine_ground.gd").atmosphere(self)') > gate.index('overcast_resources.gd").environment(self)'))
    check('ANISOTROPIC_SETTING', 'textures/default_filters/anisotropic_filtering_level=4' in (ROOT / 'game/project.godot').read_text())
    # Wiring diff is exactly the intended lines; any other playable edit fails.
    def diff(name):
        return [l for l in git('diff', '-U0', BASELINE_COMMIT, '--', name).decode().splitlines() if l[:1] in '+-' and not l.startswith(('+++', '---'))]
    check('BUILDER_DIFF_BOUNDED', diff('game/scripts/p1a_world_builder.gd') == ['-\tmesh.surface_set_material(0, preload("res://scripts/quiet_surfaces.gd").material())', '+\t# Fine Ground v1 keeps the Quiet Surfaces macro maps and adds near detail.', '+\tmesh.surface_set_material(0, preload("res://scripts/fine_ground.gd").material())'])
    check('GATE_DIFF_BOUNDED', diff('game/scripts/p1a_world_gate.gd') == ['+\tpreload("res://scripts/fine_ground.gd").atmosphere(self)'])
    check('PROJECT_DIFF_BOUNDED', diff('game/project.godot') == ['+textures/default_filters/anisotropic_filtering_level=4'])
    return checks


def regenerate_checks():
    sys.path.insert(0, str(ROOT / 'tools')); from generate_fine_ground import generate
    with tempfile.TemporaryDirectory(prefix='fine-ground-repro-') as temp:
        generate(Path(temp))
        return [{'id': 'REPEATABLE:' + name, 'pass': sha(Path(temp) / name) == sha(FOLDER / name)} for name in ['fine_ground_detail.png', 'fine_ground_index.json', '.gdignore']]


def execute_native(args, evidence):
    sys.path.insert(0, str(ROOT / 'tools')); from launch import LaunchError, resolve_engine
    try:
        engine, version = resolve_engine(args.godot)
    except LaunchError as error:
        return {'status': 'BLOCKED', 'reason': str(error), 'records': []}
    records = []
    window = ['--resolution', '1280x720', '--rendering-method', 'forward_plus']

    def run(name, command, cwd):
        command = [str(x) for x in command]
        at = command.index('--') if '--' in command else len(command)
        command[at:at] = ['--log-file', str(evidence / (name + '.log'))]
        try:
            p = subprocess.run(command, cwd=cwd, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=600); output, code = p.stdout, p.returncode
        except (OSError, subprocess.TimeoutExpired) as error:
            output, code = str(error), -1
        log = evidence / (name + '.log'); output += '\n' + (log.read_text(errors='replace') if log.is_file() else '')
        (evidence / (name + '.stdout')).write_text(output)
        ok = code == 0 and not re.search(r'SCRIPT ERROR:|SHADER ERROR:|Parse Error:|Failed to load script|Cannot get class', output, re.I)
        records.append({'name': name, 'argv': command, 'returncode': code, 'pass': ok}); print(('PASS ' if ok else 'FAIL ') + name, flush=True)
        return ok

    def result(path):
        try:
            return json.loads(path.read_text())
        except (OSError, ValueError):
            return {}

    with tempfile.TemporaryDirectory(prefix='fine-ground-native-') as temporary:
        before, after = Path(temporary) / 'baseline', Path(temporary) / 'successor'
        with tarfile.open(fileobj=io.BytesIO(git('archive', BASELINE_COMMIT))) as source:
            for member in source:
                target = before / member.name
                if not target.resolve().is_relative_to(before.resolve()) or member.issym() or member.islnk():
                    return {'status': 'FAIL', 'reason': 'Unsafe baseline archive member', 'records': records}
                if member.isdir():
                    target.mkdir(parents=True, exist_ok=True)
                elif member.isfile():
                    target.parent.mkdir(parents=True, exist_ok=True); target.write_bytes(source.extractfile(member).read())
        # The probe is test-only; the baseline copy receives it to report identity.
        shutil.copy2(ROOT / 'game/tests/fine_ground_runtime.gd', before / 'game/tests/fine_ground_runtime.gd')
        shutil.copytree(ROOT / 'game', after / 'game', ignore=shutil.ignore_patterns('.godot', '__pycache__'))
        for label, project in [('baseline', before), ('successor', after)]:
            if not run(label + '_import', [engine, '--headless', '--editor', '--path', project / 'game', '--import', '--quit'], project):
                return {'status': 'FAIL', 'engine': version, 'records': records}
            run(label + '_parse', [engine, '--headless', '--editor', '--path', project / 'game', '--quit-after', '2'], project)
            run(label + '_c1', [engine, '--headless', '--path', project / 'game', '--script', 'res://tests/world_polish_c1.gd', '--', '--output', evidence / (label + '-c1.jsonl')], project)
            flag = ['--baseline'] if label == 'baseline' else []
            run(label + '_fine_ground', [engine, *window, '--path', project / 'game', '--script', 'res://tests/fine_ground_runtime.gd', '--', '--result', evidence / (label + '-fine-ground.json'), '--capture-dir', evidence / (label + '-captures'), *flag], project)
        traces = [evidence / (n + '-c1.jsonl') for n in ['baseline', 'successor']]
        records.append({'name': 'C1_MATCHED_SAME_HOST_1260_TICKS', 'pass': all(p.is_file() and len(p.read_text().splitlines()) == 1260 for p in traces) and traces[0].read_bytes() == traces[1].read_bytes(), 'hashes': {p.name: sha(p) for p in traces if p.is_file()}})
        a, b = result(evidence / 'baseline-fine-ground.json'), result(evidence / 'successor-fine-ground.json')
        same = bool(a.get('identity')) and a.get('identity') == b.get('identity')
        records.append({'name': 'TERRAIN_COLLISION_UV_NODE_IDENTITY', 'pass': same, 'baseline': a.get('identity'), 'successor': b.get('identity')})
        records.append({'name': 'successor_fine_ground_result', 'pass': b.get('status') == 'PASS'})
        for name, script, headless in [('quarto_vehicle', 'quarto_vehicle_v1.gd', True), ('run_v0', 'run_v0_probe.gd', True), ('paused_retry', 'paused_retry_addendum.gd', True), ('world_and_entrances', 'world_polish_runtime.gd', False)]:
            out = evidence / (name + '.json')
            run(name, [engine, *(['--headless'] if headless else window), '--path', after / 'game', '--script', 'res://tests/' + script, '--', '--result', out], after)
            records.append({'name': name + '_result', 'pass': result(out).get('status') == 'PASS'})
    return {'status': 'PASS' if all(r['pass'] for r in records) else 'FAIL', 'engine': version, 'records': records,
            'scope': 'Native same-host functional checks and captures. Visual preference, comfort, shimmer and performance are judged separately.'}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--evidence', type=Path, help='New empty evidence directory (required with --native)')
    p.add_argument('--regenerate', action='store_true', help='Regenerate the tile in a temporary folder and compare bytes')
    p.add_argument('--native', action='store_true', help='Require the exact installed engine and a display')
    p.add_argument('--godot', help='Exact installed executable; no substitution or installation')
    args = p.parse_args()
    if args.native and not args.evidence:
        p.error('--native requires --evidence')
    try:
        checks = static_checks() + (regenerate_checks() if args.regenerate else [])
    except (OSError, ValueError, KeyError, AssertionError, subprocess.CalledProcessError) as error:
        checks = [{'id': 'STATIC_COMPLETION', 'pass': False, 'detail': str(error)}]
    report = {'schema': 'hush_basin.fine_ground_v1.v1', 'baseline_commit': BASELINE_COMMIT,
              'static': {'status': 'PASS' if all(c['pass'] for c in checks) else 'FAIL', 'check_count': len(checks),
                         'failures': [c['id'] for c in checks if not c['pass']]},
              'native': {'status': 'NOT_RUN', 'reason': 'Pass --native with the exact engine.'}}
    if args.evidence:
        evidence = args.evidence.resolve(); evidence.mkdir(parents=True, exist_ok=False)
        if args.native:
            report['native'] = execute_native(args, evidence)
        (evidence / 'fine_ground_result.json').write_text(json.dumps({**report, 'checks': checks}, indent=2) + '\n')
    print(json.dumps(report, indent=2))
    native_ok = report['native']['status'] == 'PASS' if args.native else True
    return 0 if report['static']['status'] == 'PASS' and native_ok else 1


if __name__ == '__main__':
    raise SystemExit(main())
