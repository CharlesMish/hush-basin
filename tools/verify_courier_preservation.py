#!/usr/bin/env python3
"""Audit the complete accepted inventory with precisely scoped successor edits."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def main():
    inventory = json.loads((ROOT/'docs/courier_baseline_inventory.json').read_text())
    authorized = json.loads((ROOT/'docs/courier_changed_files.json').read_text())
    changed = []
    for name, expected in inventory['files'].items():
        data = (ROOT/name).read_bytes() if (ROOT/name).is_file() else b''
        if name == 'game/project.godot':
            data = data.replace(b'res://scenes/district_zero_courier.tscn', b'res://scenes/district_zero_run.tscn')
        if name == 'tools/export_web.py':
            expected = authorized[name]
        if hashlib.sha256(data).hexdigest() != expected:
            changed.append(name)
    diff = (ROOT/'docs/courier_web_export.diff').read_text()
    checks = {'accepted_inventory_preserved_except_main_and_diagnostic_export':not changed,
              'one_job_main':(ROOT/'game/project.godot').read_text().count('run/main_scene="res://scenes/district_zero_courier.tscn"')==1,
              'old_run_available':(ROOT/'PLAY_RUN_V0.command').is_file(),
              'no_courier_dependency_in_controller':'courier' not in (ROOT/'game/scripts/craft_controller.gd').read_text().lower(),
              'historical_study_unchanged':not any(p.startswith('design/') for p in changed)}
    result={'status':'PASS' if all(checks.values()) else 'FAIL','baseline':inventory['baseline'],'inventory_count':len(inventory['files']),'checks':checks,'unexpected_changes':changed,'review_required_export_diff':diff}
    print(json.dumps(result,indent=2))
    return 0 if result['status']=='PASS' else 1

if __name__=='__main__': raise SystemExit(main())
