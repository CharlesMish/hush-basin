#!/usr/bin/env python3
"""Narrow surface successor inventory, immutable inputs and repeatable atlas."""
from pathlib import Path
import argparse, hashlib, json, math, tempfile
from generate_quiet_surfaces import generate
ROOT=Path(__file__).resolve().parents[1]
CHANGED={'AGENTS.md','game/AGENTS.md','README.md','STATUS.md','game/STATUS.md','game/project.godot','game/scripts/p1a_world_builder.gd','game/scripts/p1a_world_gate.gd','game/tests/world_polish_runtime.gd','tools/verify_world_polish.py','tools/verify_repo.py','tools/package_world_polish.py'}
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('--result',type=Path);p.add_argument('--regenerate',action='store_true');args=p.parse_args();checks=[]
 def check(id,ok,detail=None):checks.append({'id':id,'pass':bool(ok),'detail':detail})
 for row in (ROOT/'NEIGHBORHOOD_V1_SHA256SUMS.txt').read_text().splitlines():
  expected,name=row.split('  ',1)
  if name not in CHANGED:check('UNCHANGED:'+name,(ROOT/name).is_file() and sha(ROOT/name)==expected)
 folder=ROOT/'game/presentation/generated';index=json.loads((folder/'quiet_surfaces_index.json').read_text());cfg=json.loads((ROOT/'game/presentation/quiet_surfaces_v1.json').read_text())
 check('CONFIG_BINDING',index['config_sha256']==sha(ROOT/'game/presentation/quiet_surfaces_v1.json'))
 for name,h in index['artifacts'].items():check('GENERATED:'+name,sha(folder/name)==h)
 for name,h in index['inputs'].items():check('INPUT:'+name,sha(ROOT/name)==h)
 check('SIZE_2048',index['size']==[2048,2048]);check('MEMORY_CAP',index['resident_texture_bytes_upper_bound']<=32*1024*1024,index['resident_texture_bytes_upper_bound'])
 check('TWELVE_PATCHES',len(cfg['patches'])==12 and sum(d['kind']=='patch' for d in index['details'])==12)
 check('SIX_COVERS',len(cfg['covers'])==6 and sum(d['kind']=='cover' for d in index['details'])==6)
 check('FINITE_IN_BOUNDS',all(math.isfinite(x) and math.isfinite(z) and -330<=x<=330 and -315<=z<=285 for d in index['details'] for x,z in d['polygon']))
 check('MATERIAL_ONLY_LOADER',all(s not in (ROOT/'game/scripts/quiet_surfaces.gd').read_text() for s in ['generate(', 'generate_mipmaps(', 'add_child(', 'craft.', 'Shader.new(', 'Decal.new(']))
 if args.regenerate:
  with tempfile.TemporaryDirectory(prefix='quiet-repro-') as temp:
   generate(Path(temp))
   for name in list(index['artifacts'])+['quiet_surfaces_index.json']:check('REPEATABLE:'+name,sha(Path(temp)/name)==sha(folder/name))
 result={'status':'PASS' if all(c['pass'] for c in checks) else 'FAIL','check_count':len(checks),'checks':checks,'failures':[c['id'] for c in checks if not c['pass']]}
 if args.result:args.result.write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps({k:v for k,v in result.items() if k!='checks'},indent=2));return result['status']!='PASS'
if __name__=='__main__':raise SystemExit(main())
