#!/usr/bin/env python3
"""Narrow architecture successor preservation, generation and spatial checks."""
from pathlib import Path
import argparse, hashlib, json, math, tempfile
from generate_neighborhood import generate, read, digest
ROOT=Path(__file__).resolve().parents[1]
CHANGED={'AGENTS.md','game/AGENTS.md','README.md','STATUS.md','game/STATUS.md','game/project.godot','game/scripts/p1a_world_builder.gd','game/scripts/world_polish_presentation.gd','game/scripts/p1a_world_gate.gd','game/tests/world_polish_runtime.gd','tools/verify_world_polish.py','tools/verify_repo.py','tools/package_world_polish.py'}
def main():
 p=argparse.ArgumentParser();p.add_argument('--result',type=Path);args=p.parse_args();checks=[]
 def check(name,ok,detail=None):checks.append(dict(id=name,pass_=bool(ok),detail=detail))
 for line in (ROOT/'WARM_OVERCAST_V1_SHA256SUMS.txt').read_text().splitlines():
  sha,name=line.split('  ',1)
  if name not in CHANGED:check('UNCHANGED:'+name,(ROOT/name).is_file() and digest(ROOT/name)==sha)
 cfg=read(ROOT/'game/presentation/neighborhood_v1.json');folder=ROOT/'game/presentation/generated';d=read(folder/'neighborhood_v1.json')
 with tempfile.TemporaryDirectory() as tmp:
  generate(Path(tmp))
  for f in Path(tmp).iterdir():check('REPEATABLE:'+f.name,digest(f)==digest(folder/f.name))
 check('ALL_BUILDINGS',len(cfg['buildings'])==14 and len(set(x['id'] for x in cfg['buildings']))==14)
 check('ALL_LANDMARK_FAMILIES',len(cfg['landmarks'])==6)
 check('BOUNDED_RESOURCE_COUNT',len(d['parts'])<=4000 and len(d['labels'])<=100)
 owners={x['id']:x for x in d['owners']};bad=[];finite=True
 for i,v in enumerate(d['parts']):
  finite=finite and all(math.isfinite(x) for x in v['p']+v['size']+[v['yaw']]) and min(v['size'])>0
  poly=owners[v['owner']]['plot'];xmin=min(x[0] for x in poly);xmax=max(x[0] for x in poly);zmin=min(x[1] for x in poly);zmax=max(x[1] for x in poly)
  x,y,z=v['p'];w,h,l=v['size'];c,s=abs(math.cos(v['yaw'])),abs(math.sin(v['yaw']));dx=(w*c+l*s)/2;dz=(w*s+l*c)/2
  if 'frontage' in v:
   f=d['compound_frontages'][v['frontage']];edge=f['source_edge'];a,b=edge[1:3];length=math.dist(a,b);nx,nz=(b[1]-a[1])/length,-(b[0]-a[0])/length
   valid=edge in read(ROOT/'game/world/generated/world_polish_v1.json')['wall_edges'] and not v['solid']
   for sx in [-1,1]:
    px=x+sx*math.cos(v['yaw'])*w/2;pz=z-sx*math.sin(v['yaw'])*w/2
    along=((px-a[0])*(b[0]-a[0])+(pz-a[1])*(b[1]-a[1]))/length
    valid=valid and -0.001<=along<=length+0.001 and abs((px-a[0])*nx+(pz-a[1])*nz)<=0.18
   if not valid:bad.append([i,'compound_frontage'])
  elif x-dx<xmin-0.18 or x+dx>xmax+0.18 or z-dz<zmin-0.18 or z+dz>zmax+0.18:bad.append([i,v['owner'],v['role']])
 check('FINITE_POSITIVE_PRIMITIVES',finite)
 check('OCCUPIED_PLOT_BOUNDS',not bad,bad[:20])
 check('CLOSED_SERVICE_FRONTS',len(d['service_fronts'])>=8 and all(v['closed'] for v in d['service_fronts']))
 for oid,o in owners.items():
  mass=[v for v in d['parts'] if v['owner']==oid and v['role'] in ['lower_mass','upper_mass','landmark_mass']]
  check('BASE_AND_HEIGHT:'+oid,bool(mass) and abs(min(v['p'][1]-v['size'][1]/2 for v in mass)-o['base'])<1e-5 and abs(max(v['p'][1]+v['size'][1]/2 for v in mass)-o['principal_top'])<1e-5)
 check('NO_WEATHER_OR_MECHANICAL_WRITES','craft' not in (ROOT/'game/scripts/neighborhood_architecture.gd').read_text())
 result={'status':'PASS' if all(v['pass_'] for v in checks) else 'FAIL','check_count':len(checks),'checks':[{'id':v['id'],'pass':v['pass_'],'detail':v['detail']} for v in checks]}
 result['failures']=[v['id'] for v in result['checks'] if not v['pass']]
 if args.result:args.result.write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps({k:v for k,v in result.items() if k!='checks'},indent=2));return result['status']!='PASS'
if __name__=='__main__':raise SystemExit(main())
