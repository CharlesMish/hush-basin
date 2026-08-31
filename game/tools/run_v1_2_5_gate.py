#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, pathlib, subprocess, sys
REQUIRED_IMPL=['tests/p1a_human_feasibility_runner.gd','tools/run_human_feasibility_session.py','tools/validate_human_feasibility_evidence.py']
RUNTIME_STAGES={'prepare','capture','replay','continue'}
ROUTE_STAGES={'capture','replay'}

def build_parser():
    ap=argparse.ArgumentParser(description='District Zero P1A v1.2.5 human-feasibility gate orchestrator')
    ap.add_argument('--stage',required=True,choices=['implementation-check','prepare','capture','replay','continue'])
    ap.add_argument('--godot')
    ap.add_argument('--baseline-root',required=True)
    ap.add_argument('--p0-root',required=True)
    ap.add_argument('--session-root')
    ap.add_argument('--route',choices=['A1','A2','X0'])
    ap.add_argument('--standalone-evidence-zip')
    return ap

def validate_cli(a):
    errors=[]
    if a.stage in RUNTIME_STAGES:
        if not a.godot: errors.append('--godot is required for runtime stages')
        if not a.session_root: errors.append('--session-root is required for runtime stages')
        if not a.standalone_evidence_zip: errors.append('--standalone-evidence-zip is required for runtime stages')
    if a.stage in ROUTE_STAGES and not a.route: errors.append('--route is required for capture/replay')
    if a.stage not in ROUTE_STAGES and a.route: errors.append('--route is forbidden outside capture/replay')
    return errors

def emit(obj): print(json.dumps(obj,indent=2,sort_keys=True))

def main(argv=None):
    a=build_parser().parse_args(argv)
    errors=validate_cli(a)
    if errors:
        emit({'status':'BLOCKED/NOT TESTABLE','stage':'CLI_CONTRACT','errors':errors})
        return 2
    root=pathlib.Path(__file__).resolve().parents[1]
    if a.stage=='implementation-check':
        cmd=[sys.executable,'-B',str(root/'tools/verify_p1a_implementation.py'),'--root',str(root),'--baseline-root',a.baseline_root,'--p0-root',a.p0_root,'--phase','implementation']
        return subprocess.run(cmd,cwd=root).returncode
    missing=[p for p in REQUIRED_IMPL if not (root/p).is_file()]
    manifest=root/'evidence/v1_2_5_capture_implementation_manifest.json'
    status='MISSING'
    if manifest.is_file():
        try: status=json.loads(manifest.read_text(encoding='utf-8')).get('status','MISSING')
        except Exception: status='INVALID'
    if missing or status!='PASS':
        emit({'status':'CODEX_IMPLEMENTATION_REQUIRED','stage':a.stage,'missing_files':missing,'implementation_manifest_status':status})
        return 2
    cmd=[sys.executable,'-B',str(root/'tools/run_human_feasibility_session.py'),'--stage',a.stage,'--godot',a.godot,'--baseline-root',a.baseline_root,'--p0-root',a.p0_root,'--session-root',a.session_root,'--standalone-evidence-zip',a.standalone_evidence_zip]
    if a.route: cmd+=['--route',a.route]
    return subprocess.run(cmd,cwd=root).returncode
if __name__=='__main__': raise SystemExit(main())
