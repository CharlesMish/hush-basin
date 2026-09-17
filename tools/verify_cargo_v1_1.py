#!/usr/bin/env python3
"""ZIP-safe full accepted-source preservation and narrow cargo-policy binding."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
def main():
    inventory = json.loads((ROOT/'docs/courier_v1_1_inventory.json').read_text())
    changed = []
    for name, old in inventory['files'].items():
        expected = inventory['permitted_changes'].get(name,old)
        if not (ROOT/name).is_file() or hashlib.sha256((ROOT/name).read_bytes()).hexdigest()!=expected:
            changed.append(name)
    rules = (ROOT/'game/scripts/courier/courier_rules.gd').read_text()
    observer = (ROOT/'game/scripts/courier/cargo_observer.gd').read_text()
    checks = {'accepted_inventory_except_two_bound_cargo_files':not changed,
              'damage_curve_constants_unchanged':all(s in rules for s in ['SEVERITY_DEAD_ZONE := 0.20','EPISODE_MAX_LOSS := 240','EPISODE_EXPONENT := 1.5']),
              'no_rng_in_cargo':not any(s in rules+observer for s in ['randf','randi','RandomNumberGenerator','randomize']),
              'review_separate_from_main':'cargo_review' not in (ROOT/'game/project.godot').read_text()}
    result={'status':'PASS' if all(checks.values()) else 'FAIL','baseline':inventory['baseline'],'file_count':len(inventory['files']),'checks':checks,'unexpected_changes':changed}
    print(json.dumps(result,indent=2))
    return 0 if result['status']=='PASS' else 1
if __name__=='__main__': raise SystemExit(main())
