#!/usr/bin/env python3
"""ZIP-safe accepted-source audit; historical cargo and movement are untouched."""
import hashlib
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main():
    inv=json.loads((ROOT/'docs/alpha_loop_inventory.json').read_text())
    unexpected=[]
    for name,old in inv['files'].items():
        p=ROOT/name
        if not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest()!=inv['permitted_changes'].get(name,old):unexpected.append(name)
    checks={'accepted_inventory_except_four_bound_integration_files':not unexpected,
            'v11_grouping_and_curve_byte_identical':all(name not in inv['permitted_changes'] for name in ['game/scripts/courier/cargo_observer.gd','game/scripts/courier/courier_rules.gd']),
            'unchanged_controller_and_brrr':all(name not in inv['permitted_changes'] for name in ['game/scripts/craft_controller.gd','game/scripts/run/brrr_seed.gd'])}
    result={'status':'PASS' if all(checks.values()) else 'FAIL','baseline':inv['commit'],'files':len(inv['files']),'checks':checks,'unexpected':unexpected}
    print(json.dumps(result,indent=2))
    return 0 if result['status']=='PASS' else 1
if __name__=='__main__':raise SystemExit(main())
