#!/usr/bin/env python3
"""One bounded successor integration run. Saves and logs stay in explicit evidence."""
import argparse, json, subprocess
from pathlib import Path
from launch import ROOT, resolve_engine

def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True)
    p.add_argument('--phase',default='full');p.add_argument('--native',action='store_true')
    p.add_argument('--resume',type=Path);a=p.parse_args()
    out=a.output.resolve();out.mkdir(parents=True,exist_ok=False)
    engine,version=resolve_engine(None);save=out/'save.json'
    if a.resume:save.write_bytes(a.resume.read_bytes())
    cmd=[str(engine)]+([] if a.native else ['--headless','--fixed-fps','60'])
    cmd+=['--path',str(ROOT/'game'),'--log-file',str(out/'engine.log'),'--script','res://tests/slices_native.gd','--','--save',str(save),'--result',str(out/'result.json'),'--phase',a.phase,'--captures',str(out/'captures'),'--cargo-log',str(out/'cargo.jsonl')]
    try:
        code=subprocess.run(cmd,cwd=ROOT,stdout=(out/'stdout.log').open('w'),stderr=subprocess.STDOUT,timeout=900).returncode
    except subprocess.TimeoutExpired:code='TIMEOUT'
    data=json.loads((out/'result.json').read_text()) if (out/'result.json').exists() else {}
    record={'engine':version,'command':cmd,'exit':code,'status':data.get('status','NO_RESULT'),'checks':len(data.get('checks',{})),'failed':[k for k,v in data.get('checks',{}).items() if not v]}
    (out/'command.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(record,indent=2))
    return 0 if code==0 and record['status']=='PASS' else 1
if __name__=='__main__':raise SystemExit(main())
