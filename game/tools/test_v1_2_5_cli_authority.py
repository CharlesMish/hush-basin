#!/usr/bin/env python3
from __future__ import annotations
import argparse, importlib.util, json, pathlib, re, shlex, sys

def load_module(path):
    spec=importlib.util.spec_from_file_location('v125_gate',path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--root',required=True);a=ap.parse_args();root=pathlib.Path(a.root)
    gate=load_module(root/'tools/run_v1_2_5_gate.py');cases=[]
    def case(n,v):cases.append({'name':n,'pass':bool(v)})
    def ns(stage,**kw):
        d=dict(stage=stage,godot=None,baseline_root='/b',p0_root='/p',session_root=None,route=None,standalone_evidence_zip=None);d.update(kw);return argparse.Namespace(**d)
    case('implementation check needs no runtime-only flags',gate.validate_cli(ns('implementation-check'))==[])
    case('prepare requires godot session evidence',len(gate.validate_cli(ns('prepare')))==3)
    case('capture requires route',any('--route' in x for x in gate.validate_cli(ns('capture',godot='/g',session_root='/s',standalone_evidence_zip='/e.zip'))))
    case('replay requires route',any('--route' in x for x in gate.validate_cli(ns('replay',godot='/g',session_root='/s',standalone_evidence_zip='/e.zip'))))
    case('continue forbids route',any('forbidden' in x for x in gate.validate_cli(ns('continue',godot='/g',session_root='/s',standalone_evidence_zip='/e.zip',route='A1'))))
    case('valid prepare',gate.validate_cli(ns('prepare',godot='/g',session_root='/s',standalone_evidence_zip='/e.zip'))==[])
    case('valid capture',gate.validate_cli(ns('capture',godot='/g',session_root='/s',standalone_evidence_zip='/e.zip',route='A1'))==[])
    case('valid replay',gate.validate_cli(ns('replay',godot='/g',session_root='/s',standalone_evidence_zip='/e.zip',route='X0'))==[])
    case('valid continue',gate.validate_cli(ns('continue',godot='/g',session_root='/s',standalone_evidence_zip='/e.zip'))==[])
    help_text=gate.build_parser().format_help();allowed=set(re.findall(r'--[a-z0-9-]+',help_text))
    expected={'--stage','--godot','--baseline-root','--p0-root','--session-root','--route','--standalone-evidence-zip'}
    case('help exposes exact flags',expected<=allowed and '--output-root' not in allowed)
    send=(root/'P1A_CODEX_SENDOFF.md').read_text(encoding='utf-8')
    blocks=re.findall(r'```bash\n(.*?)\n```',send,re.S);unknown=[]
    for b in blocks:
        toks=shlex.split(b.replace('\\\n',' '));
        for t in toks:
            if t.startswith('--') and t not in allowed and t not in {'--root','--phase'}:unknown.append(t)
    case('documented wrapper flags recognized',not unknown)
    case('sendoff has all five stages',all(f'--stage {x}' in send for x in ['implementation-check','prepare','capture','replay','continue']))
    bad=[x for x in cases if not x['pass']];out={'schema':'district_zero.p1a.v1_2_5.cli_semantic_tests.v1','status':'PASS' if not bad else 'FAIL','case_count':len(cases),'pass_count':len(cases)-len(bad),'fail_count':len(bad),'cases':cases}
    print(json.dumps(out,indent=2,sort_keys=True));return 0 if not bad else 1
if __name__=='__main__':raise SystemExit(main())
