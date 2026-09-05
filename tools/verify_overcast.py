#!/usr/bin/env python3
"""Verify the narrowly authorized delta from the complete World Polish v1 ZIP."""
from pathlib import Path
import hashlib
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
CHANGED = {
    'AGENTS.md', 'game/AGENTS.md', 'README.md', 'STATUS.md', 'game/STATUS.md',
    'game/project.godot', 'game/scripts/p1a_world_builder.gd',
    'game/scripts/p1a_world_gate.gd', 'game/scripts/p1a_map.gd',
    'game/scripts/world_polish_presentation.gd', 'game/scripts/run/run_map_overlay.gd',
    'game/tests/world_polish_runtime.gd', 'tools/verify_repo.py',
    'tools/verify_world_polish.py', 'tools/package_world_polish.py',
}


def main():
    checks = []
    def check(name, passed):
        checks.append({'id': name, 'pass': bool(passed)})
    for row in (ROOT/'WORLD_POLISH_V1_SHA256SUMS.txt').read_text().splitlines():
        expected, name = row.split('  ', 1)
        if name not in CHANGED:
            path = ROOT/name
            check('V1_UNCHANGED:'+name, path.is_file() and hashlib.sha256(path.read_bytes()).hexdigest() == expected)
    cfg = json.loads((ROOT/'game/presentation/warm_overcast_v1.json').read_text())
    check('PRESENTATION_IDENTITY', cfg['version'] == 'warm-overcast-v1')
    check('BOUNDED_RAIN', cfg['rain']['amount'] == 384 and cfg['rain']['footprint_m'] == 48)
    check('SKY_SIZE', [cfg['sky']['width'], cfg['sky']['height']] == [1024, 512])
    check('DAMP_CONTRAST', 0.50 <= cfg['damp']['paving_roughness'] < cfg['damp']['mineral_roughness'] and 0.90 <= cfg['damp']['paving_value'] <= 1.0)
    for name in ['overcast_resources.gd', 'overcast_weather.gd']:
        source = (ROOT/'game/scripts'/name).read_text()
        check('NATIVE_MATERIALS:'+name, 'ShaderMaterial' not in source and 'load("http' not in source)
    failures = [v['id'] for v in checks if not v['pass']]
    result = {'status': 'FAIL' if failures else 'PASS', 'check_count': len(checks), 'checks': checks, 'failures': failures}
    if '--result' in sys.argv:
        Path(sys.argv[sys.argv.index('--result')+1]).write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k != 'checks'}, indent=2))
    return bool(failures)


if __name__ == '__main__':
    sys.exit(main())
