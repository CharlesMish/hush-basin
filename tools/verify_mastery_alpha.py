#!/usr/bin/env python3
"""Exact accepted V1.1 inventory with six explicitly bound successor edits."""
import hashlib
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
inventory = json.loads((root / 'docs/mastery_alpha_v1_inventory.json').read_text())
bad = []
for name, old_hash in inventory['files'].items():
    path = root / name
    expected = inventory['permitted_changes'].get(name, old_hash)
    if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != expected:
        bad.append(name)
print(json.dumps({'status': 'FAIL' if bad else 'PASS',
    'baseline': inventory['baseline_commit'], 'files': len(inventory['files']),
    'changed_existing': list(inventory['permitted_changes']), 'unexpected': bad}, indent=2))
raise SystemExit(bool(bad))
