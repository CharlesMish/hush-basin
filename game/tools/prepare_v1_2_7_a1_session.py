#!/usr/bin/env python3
from __future__ import annotations
import argparse, datetime as dt, hashlib, json, pathlib, shutil, subprocess, uuid
EXACT='4.7.1.stable.official.a13da4feb'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,v): p.parent.mkdir(parents=True,exist_ok=True); p.write_text(json.dumps(v,indent=2,sort_keys=True)+'\n')
def copy_clean(src,dst):
    def ign(_d,names): return {n for n in names if n in {'.godot','__pycache__','director_inputs'} or n.endswith(('.pyc','.pyo'))}
    shutil.copytree(src,dst,ignore=ign)
def inventory(root,out):
    files=sorted((p for p in root.rglob('*') if p.is_file() and p!=out),key=lambda p:p.relative_to(root).as_posix().encode())
    out.write_text(''.join(f'{sha(p)}  {p.relative_to(root).as_posix()}\n' for p in files)); return len(files)
def main()->int:
    ap=argparse.ArgumentParser(); ap.add_argument('--root',required=True); ap.add_argument('--godot',required=True); ap.add_argument('--session-root',required=True); a=ap.parse_args()
    root=pathlib.Path(a.root).resolve(); session=pathlib.Path(a.session_root).resolve(); godot=pathlib.Path(a.godot).resolve()
    try: v=subprocess.run([str(godot),'--version'],cwd=root,capture_output=True,text=True,check=False).stdout.strip()
    except OSError as e: v=str(e)
    if v!=EXACT: print(json.dumps({'status':'BLOCKED/NOT TESTABLE','blocker':'exact engine mismatch','observed':v})); return 2
    if session.exists() and any(session.iterdir()): print(json.dumps({'status':'BLOCKED/NOT TESTABLE','blocker':'session root nonempty'})); return 2
    session.mkdir(parents=True,exist_ok=True); project=session/'project'; copy_clean(root,project)
    sid=str(uuid.uuid4())
    state={'schema':'district_zero.p1a.v1_2_7.session_state.v1','authority_version':'v1.2.5','presentation_version':'v1.2.7','prepared':True,'prepared_utc':dt.datetime.now(dt.timezone.utc).isoformat(),'human_attempts_consumed':0,'routes':{r:{'capture':'NOT PERFORMED','replay':'NOT PERFORMED'} for r in ['A1','A2','X0']},'human_world_gate':'NOT PERFORMED','P1B':'FROZEN'}
    dump(session/'session_state.json',state)
    manifest={'schema':'district_zero.p1a.v1_2_7.prepared_a1_session_manifest.v1','session_uuid':sid,'route_binding':'A1','godot_path':str(godot),'engine_identity':EXACT,'capture_semantics_version':'v1.2.5','presentation_version':'v1.2.7','human_attempts_consumed':0,'human_world_gate':'NOT PERFORMED','P1B':'FROZEN'}
    dump(session/'SESSION_MANIFEST.json',manifest)
    launcher=session/'START_A1_CAPTURE.command'; launcher.write_text('#!/bin/zsh\nset -euo pipefail\nSESSION_ROOT="${0:A:h}"\nexec /usr/bin/env python3 "$SESSION_ROOT/project/tools/launch_a1_capture_v1_2_7.py" --session-root "$SESSION_ROOT" "$@"\n'); launcher.chmod(0o755)
    count=inventory(session,session/'SESSION_SHA256SUMS.txt')
    result={'schema':'district_zero.p1a.v1_2_7.prepared_a1_session_result.v1','status':'READY FOR A1 HUMAN FEASIBILITY CAPTURE','session_uuid':sid,'engine_identity':EXACT,'checksum_records':count,'human_attempts_consumed':0,'human_world_gate':'NOT PERFORMED','P1B':'FROZEN'}
    dump(session/'PREPARED_RESULT.json',result); print(json.dumps(result,sort_keys=True)); return 0
if __name__=='__main__': raise SystemExit(main())
