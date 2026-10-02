#!/usr/bin/env python3
"""Exact accepted-source preservation, with narrowly named successor exceptions."""
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
BASE = 'd8e921068819a86ca888aaa26d9bfbb9fb8e4476'
ALLOWED = {'AGENTS.md', 'game/AGENTS.md', 'README.md', 'STATUS.md',
           'game/project.godot', 'tools/export_web.py', 'tools/play_narrative.py'}

def main():
    names = subprocess.check_output(['git', 'ls-tree', '-r', '--name-only', BASE], cwd=ROOT, text=True).splitlines()
    changed, bad = [], []
    for name in names:
        old = subprocess.check_output(['git', 'show', f'{BASE}:{name}'], cwd=ROOT)
        new = (ROOT/name).read_bytes() if (ROOT/name).exists() else b''
        if old != new:
            changed.append(name)
            if name not in ALLOWED:
                bad.append(name)
    def native_settings(data):
        return '\n'.join(line for line in data.decode().splitlines() if not line.startswith(('config/name=', 'run/main_scene=')))
    old = subprocess.check_output(['git', 'show', f'{BASE}:game/project.godot'], cwd=ROOT)
    same = native_settings(old) == native_settings((ROOT/'game/project.godot').read_bytes())
    result = {'status': 'PASS' if not bad and same else 'FAIL', 'baseline': BASE,
              'baseline_files': len(names), 'unchanged': len(names)-len(changed),
              'changed_existing': changed, 'unexpected': bad,
              'native_settings_except_name_entry_exact': same,
              'scope': 'All original controller, tuning, collision, camera, rig, world, routes, scoring, cargo and narrative fixtures remain byte-identical.'}
    print(json.dumps(result, indent=2))
    return 0 if result['status'] == 'PASS' else 1

if __name__ == '__main__':
    raise SystemExit(main())
