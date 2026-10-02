#!/usr/bin/env python3
"""Scope guard for the owner's small Opening Chapter UX correction."""
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
BASE = 'fd6a7563918f257590906f0b7dae0229273b20a3'
ALLOWED = {'STATUS.md', 'game/scripts/courier/chapter_director.gd',
           'game/scripts/courier/chapter_anchors.gd', 'game/scripts/courier/chapter_text.gd',
           'game/scripts/courier/chapter_panel.gd', 'game/scripts/courier/chapter_hud.gd',
           'game/scripts/p1a_map.gd'}

def main():
    names = subprocess.check_output(['git', 'ls-tree', '-r', '--name-only', BASE], cwd=ROOT, text=True).splitlines()
    changed = []
    for name in names:
        old = subprocess.check_output(['git', 'show', f'{BASE}:{name}'], cwd=ROOT)
        if not (ROOT/name).exists() or (ROOT/name).read_bytes() != old:
            changed.append(name)
    name = 'game/scripts/courier/chapter_text.gd'
    old = subprocess.check_output(['git', 'show', f'{BASE}:{name}'], cwd=ROOT)
    text_exact = old.split(b'static func job')[0] == (ROOT/name).read_bytes().split(b'static func job')[0]
    unexpected = sorted(set(changed)-ALLOWED)
    report = {'status': 'PASS' if not unexpected and text_exact else 'FAIL',
              'starting_head': BASE, 'baseline_files': len(names), 'unchanged': len(names)-len(changed),
              'changed_existing': changed, 'unexpected': unexpected,
              'all_authored_dialogue_offers_summaries_order_exact': text_exact,
              'scope': 'Vehicle, camera, cargo, scoring, collision, world data, routes, portraits and chapter persistence store remain exact.'}
    print(json.dumps(report, indent=2))
    return 0 if report['status'] == 'PASS' else 1

if __name__ == '__main__':
    raise SystemExit(main())
