#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, pathlib, re, shutil, subprocess, sys, tempfile
EXACT='4.7.1.stable.official.a13da4feb'
ERRORS=tuple(re.compile(x,re.I) for x in (r'SCRIPT ERROR',r'Parse Error',r'Failed to load script',r'not declared in the current scope',r'Could not find type',r'Cannot infer the type'))
def dump(p,v): p.parent.mkdir(parents=True,exist_ok=True); p.write_text(json.dumps(v,indent=2,sort_keys=True)+'\n')
def write(p,s): p.parent.mkdir(parents=True,exist_ok=True); p.write_text(s)
def run(cmd,cwd): return subprocess.run(cmd,cwd=cwd,capture_output=True,text=True,check=False)
def copy_clean(src,dst):
    def ign(_d,names): return {n for n in names if n in {'.godot','__pycache__','director_inputs'} or n.endswith(('.pyc','.pyo'))}
    shutil.copytree(src,dst,ignore=ign)
def main()->int:
    ap=argparse.ArgumentParser(); ap.add_argument('--root',required=True); ap.add_argument('--godot',required=True); ap.add_argument('--evidence-dir',required=True); ap.add_argument('--work-root')
    a=ap.parse_args(); root=pathlib.Path(a.root).resolve(); ev=pathlib.Path(a.evidence_dir).resolve();
    if ev.exists(): shutil.rmtree(ev)
    ev.mkdir(parents=True)
    v=run([a.godot,'--version'],root); version=v.stdout.strip(); dump(ev/'engine_identity.json',{'required':EXACT,'observed':version,'match':version==EXACT})
    if version!=EXACT: dump(ev/'C1_result.json',{'status':'BLOCKED/NOT TESTABLE','blocker':'exact engine mismatch'}); return 2
    work=pathlib.Path(a.work_root).resolve() if a.work_root else pathlib.Path(tempfile.mkdtemp(prefix='dz-v127-c1-'))
    if work.exists(): shutil.rmtree(work)
    work.mkdir(parents=True)
    try:
        base=work/'v1_2_6_runtime_baseline'; final=work/'v1_2_7_final'
        copy_clean(root,base); copy_clean(root,final)
        shutil.copy2(root/'tests/fixtures/v1_2_7_v1_2_6_world_builder.gd',base/'scripts/p1a_world_builder.gd')
        traces=[]
        for name,project in [('v1_2_6_runtime_baseline',base),('v1_2_7_final',final)]:
            idir=ev/name; idir.mkdir()
            for stage,cmd in [
              ('import',[a.godot,'--headless','--path',str(project),'--import','--log-file',str(idir/'import-engine.txt')]),
              ('parse',[a.godot,'--headless','--editor','--quit','--path',str(project),'--log-file',str(idir/'parse-engine.txt')])]:
                p=run(cmd,project); dump(idir/f'{stage}-argv.json',{'argv':cmd,'cwd':str(project)}); write(idir/f'{stage}-stdout.txt',p.stdout); write(idir/f'{stage}-stderr.txt',p.stderr)
                log=(idir/f'{stage}-engine.txt').read_text(errors='replace') if (idir/f'{stage}-engine.txt').is_file() else ''
                bad=[line for line in '\n'.join((p.stdout,p.stderr,log)).splitlines() if any(r.search(line) for r in ERRORS)]
                if p.returncode!=0 or bad: dump(ev/'C1_result.json',{'status':'BLOCKED/NOT TESTABLE','stage':f'{name}:{stage}','errors':bad}); return 2
            trace=idir/'trace.jsonl'; traces.append(trace); engine=idir/'run-engine.txt'
            cmd=[a.godot,'--headless','--log-file',str(engine),'--path',str(project),'--fixed-fps','60','--script','res://tests/p1a_baseline_runner.gd','--','--output',str(trace)]
            p=run(cmd,project); dump(idir/'run-argv.json',{'argv':cmd,'cwd':str(project)}); write(idir/'run-stdout.txt',p.stdout); write(idir/'run-stderr.txt',p.stderr)
            if p.returncode!=0 or not trace.is_file(): dump(ev/'C1_result.json',{'status':'BLOCKED/NOT TESTABLE','stage':f'{name}:run','returncode':p.returncode}); return 2
        cmd=[sys.executable,'-B',str(root/'tools/compare_p1a_baseline.py'),str(traces[0]),str(traces[1]),str(root/'tests/fixtures/baseline_flat_support.json')]
        p=run(cmd,root); dump(ev/'compare-argv.json',{'argv':cmd,'cwd':str(root)}); write(ev/'compare-stdout.txt',p.stdout); write(ev/'compare-stderr.txt',p.stderr)
        try: result=json.loads(p.stdout.strip().splitlines()[-1])
        except Exception: result={'status':'FAIL','error':'unparseable comparator output'}
        result.update({'schema':'district_zero.p1a.v1_2_7.c1_result.v1','required_ticks':1260,'exact_engine':EXACT,'comparison':'v1.2.7 final vs exact v1.2.6 runtime baseline embedded in successor'})
        dump(ev/'C1_result.json',result)
        return 0 if p.returncode==0 and result.get('status')=='PASS' and result.get('ticks_compared')==1260 and float(result.get('maximum_absolute_difference',1))==0.0 else 1
    finally:
        if not a.work_root: shutil.rmtree(work,ignore_errors=True)
if __name__=='__main__': raise SystemExit(main())
