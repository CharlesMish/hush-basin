#!/usr/bin/env python3
"""Narrow successor preservation and authored detail bounds, standard library."""
import hashlib
import itertools
import json
import math
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
BASE = 'ce48769fd648a44dd0b28c975b8fe4bf78bd3cb1'
HOOK = b'\tpreload("res://scripts/world_identity_detail_v2.gd").new().build(self, data)\n'

def main():
    inventory=json.loads((ROOT/'docs/world_identity_v2_baseline_inventory.json').read_text())
    assert inventory['baseline']==BASE
    files=inventory['files']
    changes=[]
    hook_count=(ROOT/'game/scripts/p1a_world_builder.gd').read_bytes().count(HOOK)
    for p in files:
        current=(ROOT/p).read_bytes() if (ROOT/p).is_file() else b''
        if p=='game/scripts/p1a_world_builder.gd': current=current.replace(HOOK,b'')
        if hashlib.sha256(current).hexdigest()!=files[p]: changes.append(p)
    cfg=json.loads((ROOT/'game/presentation/world_identity_detail_v2.json').read_text())
    generated=ROOT/'game/presentation/generated/world_identity_detail_v2.json'
    before=generated.read_bytes()
    subprocess.run([sys.executable,str(ROOT/'tools/generate_world_identity_v2.py')],check=True,stdout=subprocess.DEVNULL)
    repeat=before==generated.read_bytes()
    j=json.loads(before)
    old=json.loads((ROOT/'game/presentation/generated/neighborhood_v1.json').read_text())
    owners={p['id']:p for p in old['owners']}
    bounds_failures=[]; finite=True; roof_support=True
    for i,p in enumerate(j['parts']):
        owner=owners[p['owner']]; xs=[v[0] for v in owner['plot']]; zs=[v[1] for v in owner['plot']]
        rx,ry,rz=p['rotation']
        minimum_y=math.inf
        for signs in itertools.product([-1,1],repeat=3):
            x,y,z=[p['size'][k]*signs[k]/2 for k in range(3)]
            # Modules rotate about at most one axis; avoid implicit Euler-order assumptions.
            assert sum(abs(a)>1e-10 for a in [rx,ry,rz])<=1
            x,y=x*math.cos(rz)-y*math.sin(rz),x*math.sin(rz)+y*math.cos(rz)
            y,z=y*math.cos(rx)-z*math.sin(rx),y*math.sin(rx)+z*math.cos(rx)
            x,z=x*math.cos(ry)+z*math.sin(ry),-x*math.sin(ry)+z*math.cos(ry)
            x+=p['p'][0]; y+=p['p'][1]; z+=p['p'][2]
            minimum_y=min(minimum_y,y)
            finite &= all(math.isfinite(v) for v in [x,y,z]) and min(p['size'])>0
            if not (min(xs)-.001<=x<=max(xs)+.001 and min(zs)-.001<=z<=max(zs)+.001 and owner['base']<=y<=owner['principal_top']+cfg['limits']['max_roof_rise_m']+.001):
                bounds_failures.append({'part':i,'owner':p['owner'],'role':p['role'],'corner':[x,y,z]});break
        if p['role']=='roof' and p['owner'].startswith('B'):
            roof_support &= minimum_y>=owner['principal_top']-.12
    checks={'all_baseline_files_preserved_except_exact_hook':not changes and hook_count==1,'generator_repeatable':repeat,'finite_positive_geometry':finite,'occupied_plot_bounds':not bounds_failures,'building_roof_detail_above_existing_roofs':roof_support,'bounded_parts':len(j['parts'])<=cfg['limits']['max_parts'],'bounded_labels':len(j['labels'])<=cfg['limits']['max_labels'],'config_hash_bound':j['config_sha256']==hashlib.sha256((ROOT/'game/presentation/world_identity_detail_v2.json').read_bytes()).hexdigest()}
    result={'status':'PASS' if all(checks.values()) else 'FAIL','baseline':BASE,'baseline_inventory_count':len(files),'checks':checks,'unexpected_changes':changes,'bounds_failures':bounds_failures,'parts':len(j['parts']),'labels':len(j['labels']),'generated_sha256':hashlib.sha256(before).hexdigest()}
    print(json.dumps(result,indent=2))
    return 0 if all(checks.values()) else 1

if __name__=='__main__': sys.exit(main())
