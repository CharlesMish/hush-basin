#!/usr/bin/env python3
from __future__ import annotations
import argparse, datetime as dt, json, pathlib, subprocess, sys
EXACT='4.7.1.stable.official.a13da4feb'
def load(p): return json.loads(p.read_text())
def dump(p,v): p.parent.mkdir(parents=True,exist_ok=True); p.write_text(json.dumps(v,indent=2,sort_keys=True)+'\n')
def main()->int:
    ap=argparse.ArgumentParser(); ap.add_argument('--session-root',required=True); a=ap.parse_args(); session=pathlib.Path(a.session_root).resolve(); project=session/'project'
    manifest=load(session/'SESSION_MANIFEST.json'); state=load(session/'session_state.json'); errors=[]
    if manifest.get('schema')!='district_zero.p1a.v1_2_7.prepared_a1_session_manifest.v1': errors.append('manifest schema mismatch')
    if manifest.get('route_binding')!='A1': errors.append('route binding mismatch')
    if not state.get('prepared') or state.get('human_attempts_consumed')!=0: errors.append('session not pristine')
    if (session/'LAUNCH_USED.json').exists(): errors.append('single-use launcher already consumed')
    godot=pathlib.Path(manifest.get('godot_path',''))
    try: v=subprocess.run([str(godot),'--version'],capture_output=True,text=True,check=False).stdout.strip()
    except OSError as e: v=str(e)
    if v!=EXACT: errors.append(f'exact engine mismatch: {v}')
    if errors:
        dump(session/'launcher_evidence/preflight_result.json',{'status':'BLOCKED/NOT TESTABLE','errors':errors,'attempts_consumed':0}); print(json.dumps({'status':'BLOCKED/NOT TESTABLE','errors':errors})); return 2
    dump(session/'LAUNCH_USED.json',{'schema':'district_zero.p1a.v1_2_7.launch_used.v1','created_utc':dt.datetime.now(dt.timezone.utc).isoformat(),'route':'A1'})
    out=session/'launcher_evidence/A1_CAPTURE_EVIDENCE.zip'
    cmd=[sys.executable,'-B',str(project/'tools/run_human_feasibility_session.py'),'--stage','capture','--route','A1','--godot',str(godot),'--baseline-root',str(project),'--p0-root',str(project),'--session-root',str(session),'--standalone-evidence-zip',str(out)]
    dump(session/'launcher_evidence/argv.json',{'argv':cmd,'cwd':str(project)})
    p=subprocess.run(cmd,cwd=project,check=False)
    return p.returncode
if __name__=='__main__': raise SystemExit(main())
