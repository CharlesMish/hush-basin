#!/usr/bin/env python3
"""Exact public-review preservation, with explicitly bound successor changes."""
import hashlib,json
from pathlib import Path
root=Path(__file__).resolve().parents[1]
a=json.loads((root/'docs/mechanics_range_v1_1_inventory.json').read_text())
bad=[f for f,h in a['files'].items() if not (root/f).is_file() or hashlib.sha256((root/f).read_bytes()).hexdigest()!=a['permitted_changes'].get(f,h)]
result={'status':'PASS' if not bad else 'FAIL','baseline':a['commit'],'files':len(a['files']),'changed_existing':list(a['permitted_changes']),'unexpected':bad}
print(json.dumps(result,indent=2))
raise SystemExit(bool(bad))
