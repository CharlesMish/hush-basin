#!/usr/bin/env python3
"""Bind this additive successor to the exact reviewed game source."""
import hashlib
import json
from pathlib import Path
import subprocess

ROOT=Path(__file__).resolve().parents[1]
BASE='1afd28a253a3dbc0387cd3f339e5a56ab29dabf4'
ALLOWED={'game/project.godot','tools/export_web.py','README.md','AGENTS.md','game/AGENTS.md','STATUS.md'}

def main():
    names=subprocess.check_output(['git','ls-tree','-r','--name-only',BASE],cwd=ROOT,text=True).splitlines()
    checked=[];changed=[]
    for name in names:
        before=subprocess.check_output(['git','show',f'{BASE}:{name}'],cwd=ROOT)
        path=ROOT/name
        same=path.is_file() and path.read_bytes()==before
        if not same:changed.append(name)
        checked.append({'path':name,'same':same,'allowed':name in ALLOWED})
    project=(ROOT/'game/project.godot').read_text()
    baseline=subprocess.check_output(['git','show',f'{BASE}:game/project.godot'],cwd=ROOT,text=True)
    exact_project=project.replace('config/name="Hush Basin — Narrative Presence Lab"','config/name="Hush Basin — Ren\'s Receiver"').replace('run/main_scene="res://review/narrative_presence/review.tscn"','run/main_scene="res://review/relay_consequence/relay_review.tscn"')==baseline
    result={'status':'PASS' if set(changed)<=ALLOWED and exact_project else 'FAIL',
            'baseline':BASE,'baseline_file_count':len(names),'unchanged':len(names)-len(changed),
            'changed_existing':changed,'native_settings_exact_except_title_entry':exact_project,
            'scope':'All pre-existing movement, tuning, camera, world, routes, cargo, BRRR, drift, vehicle and original courier/Relay code must remain byte-identical.'}
    print(json.dumps(result,indent=2))
    return 0 if result['status']=='PASS' else 1

if __name__=='__main__':raise SystemExit(main())
