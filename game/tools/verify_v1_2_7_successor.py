#!/usr/bin/env python3
from __future__ import annotations
import argparse, ast, fnmatch, hashlib, json, pathlib, re, subprocess, sys

EXACT='4.7.1.stable.official.a13da4feb'
SOURCE_SHA='e59647e98f119405614718c5c20193dec25565ca2b186c25e083edbfd282bac8'
EVIDENCE_SHA='13b024c56932e0b83b858ca6453b66dbd84b28b556ebcb38611ddc8d30277437'
MUTABLE={'AGENTS.md','README_FIRST.md','STATUS.md','P1A_ACTIVE_AUTHORITY_CHAIN.json','P1A_CODEX_SENDOFF.md','PACKET_SHA256SUMS.txt','scripts/p1a_world_builder.gd'}

def sha(p:pathlib.Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p:pathlib.Path):return json.loads(p.read_text(encoding='utf-8'))

def verify_inventory(root:pathlib.Path, inv:pathlib.Path, exclude:set[str]|None=None)->list[str]:
    errors=[]; seen=set(); exclude=exclude or set()
    if not inv.is_file(): return [f'missing inventory {inv}']
    for n,line in enumerate(inv.read_text(encoding='utf-8').splitlines(),1):
        if not line: continue
        m=re.fullmatch(r'([0-9a-f]{64})  (.+)',line)
        if not m: errors.append(f'malformed inventory row {n}'); continue
        digest,rel=m.groups()
        if rel in seen: errors.append(f'duplicate inventory path {rel}')
        seen.add(rel); p=root/rel
        if not p.is_file() or sha(p)!=digest: errors.append(f'checksum mismatch {rel}')
    actual={p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file() and '.godot' not in p.parts and '__pycache__' not in p.parts and not p.name.endswith(('.pyc','.pyo'))}-exclude
    if seen!=actual: errors.append(f'inventory coverage mismatch missing={sorted(actual-seen)[:5]} extra={sorted(seen-actual)[:5]}')
    return errors

def normalize_builder(text:str)->str:
    text=re.sub(r'(?m)^(\s*if source_id == "OUTER_CLOSURE_MASK":\n\s*)return Color\([^\n]+\)',r'\1return Color(__OUTER_CALIBRATED__)',text)
    # CORE_WALL is the default return at the end of _solid_color.
    text=re.sub(r'(?m)^\s*return Color\(0\.60, 0\.63, 0\.68\)\s*$', '    return Color(__CORE_CALIBRATED__)', text)
    text=re.sub(r'(?ms)^\s*# V1_2_7_CALIBRATION_EMISSION_BEGIN\n.*?^\s*# V1_2_7_CALIBRATION_EMISSION_END\n?', '', text)
    return text

def main()->int:
    ap=argparse.ArgumentParser(); ap.add_argument('--root',required=True); ap.add_argument('--phase',choices=['director','final'],default='director')
    a=ap.parse_args(); root=pathlib.Path(a.root).resolve(); errors=[]; counts={}
    def check(c,m):
        if not c: errors.append(m)
    base=load(root/'tests/fixtures/v1_2_7_v1_2_6_base_manifest.json')
    records={x['path']:x for x in base['records']}; counts['v1_2_6_base_records']=len(records)
    check(base.get('source_transport_sha256')==SOURCE_SHA,'base transport identity wrong')
    frozen=[rel for rel in records if rel not in MUTABLE and '__pycache__' not in pathlib.PurePosixPath(rel).parts and '.godot' not in pathlib.PurePosixPath(rel).parts and not rel.endswith(('.pyc','.pyo'))]
    bad=[]
    for rel in frozen:
        p=root/rel; rec=records[rel]
        if not p.is_file() or p.stat().st_size!=rec['byte_size'] or sha(p)!=rec['sha256']: bad.append(rel)
    check(not bad,f'frozen v1.2.6 bytes changed: {bad[:10]}'); counts['strict_frozen_preexisting_files']=len(frozen)
    baseline=(root/'tests/fixtures/v1_2_7_v1_2_6_world_builder.gd').read_text(encoding='utf-8')
    current=(root/'scripts/p1a_world_builder.gd').read_text(encoding='utf-8')
    if a.phase=='director': check(current==baseline,'director packet preselects a material value')
    else: check(normalize_builder(current)==normalize_builder(baseline),'final material source changed outside authorized two-material presentation literals/fallback block')
    # Original acceptance/ray/normal contracts must remain exact v1.2.6 bytes.
    for rel in ['tests/fixtures/v1_2_6_visual_acceptance.json','tests/fixtures/v1_2_6_ray_classification_baseline.json','presentation/p1a_v1_2_6_normal_contract.json','presentation/generated/solid_render_meshes_v1_2_6.json','world/generated/solid_meshes.json']:
        check(rel in records and (root/rel).is_file() and sha(root/rel)==records[rel]['sha256'],f'frozen contract/artifact changed {rel}')
    chain=load(root/'P1A_ACTIVE_AUTHORITY_CHAIN.json'); status=(root/'STATUS.md').read_text(encoding='utf-8'); reg=load(root/'tests/fixtures/v1_2_7_calibration_registry.json')
    check(chain.get('active_director_authority')=='v1.2.7','active authority not v1.2.7')
    check(chain.get('world_data_authority')=='v1.2.3' and chain.get('capture_replay_semantics_authority')=='v1.2.5' and chain.get('presentation_baseline_authority')=='v1.2.6','authority chain changed frozen version')
    check(reg.get('exact_engine')==EXACT and reg.get('absolute_candidate_engine_launch_cap')==82,'registry engine/cap mismatch')
    check(reg.get('candidate_mutable')==['OUTER_CLOSURE_MASK presentation','CORE_WALL presentation'],'candidate mutable set wrong')
    if a.phase=='director': check('**Outcome:** `READY FOR CODEX — BOUNDED PRESENTATION CALIBRATION`' in status,'director status wrong')
    # Retained evidence transport and substantive inventory.
    ez=root/'director_inputs/District-Zero-P1A-v1.2.6-Run-1-Validation-Evidence.transport.zip'
    check(ez.is_file() and sha(ez)==EVIDENCE_SHA,'retained Run-1 evidence transport mismatch')
    evroot=root/'director_inputs/v1_2_6_run1_validation_evidence'; everrors=verify_inventory(evroot,evroot/'SHA256SUMS.txt',{'SHA256SUMS.txt'})
    check(not everrors,'retained Run-1 substantive inventory failed: '+str(everrors[:3])); counts['run1_substantive_records']=72 if not everrors else None
    term=load(evroot/'TERMINAL_RESULT.json'); metric=load(evroot/'NATIVE_VISUALS/native-visual-metric-result.json')
    check(term.get('engine_identity')==EXACT and term.get('c1',{}).get('ticks_compared')==1260 and term.get('c1',{}).get('maximum_absolute_difference')==0.0,'Run-1 terminal anchor mismatch')
    fails=[c for c in metric.get('checks',[]) if not c.get('pass')]
    check(len(metric.get('checks',[]))==21 and [c['id'] for c in fails]==['A1_FAMILIARIZATION:left_outer_closure:shadow_on_min','A1:right_obstacle_separation'],'Run-1 visual anchor mismatch')
    # Syntax and semantic suite.
    pybad=[]
    for p in root.rglob('*.py'):
        try: ast.parse(p.read_text(encoding='utf-8'))
        except Exception as e: pybad.append(f'{p.relative_to(root)}:{e}')
    check(not pybad,'Python parse errors '+str(pybad[:5])); counts['python_files']=len(list(root.rglob('*.py')))
    jbad=[]
    for p in root.rglob('*.json'):
        try: load(p)
        except Exception as e: jbad.append(f'{p.relative_to(root)}:{e}')
    check(not jbad,'JSON parse errors '+str(jbad[:5])); counts['json_files']=len(list(root.rglob('*.json')))
    sem=subprocess.run([sys.executable,'-B',str(root/'tools/test_v1_2_7_calibration_semantics.py'),'--root',str(root)],cwd=root,capture_output=True,text=True)
    try: sj=json.loads(sem.stdout)
    except Exception: sj={}
    check(sem.returncode==0 and sj.get('status')=='PASS','v1.2.7 semantic tests failed'); counts['semantic_cases']=sj.get('case_count')
    # Fresh packet inventory if present.
    if (root/'PACKET_SHA256SUMS.txt').is_file():
        inv_errors=verify_inventory(root,root/'PACKET_SHA256SUMS.txt',{'PACKET_SHA256SUMS.txt'})
        check(not inv_errors,'packet inventory mismatch: '+str(inv_errors[:3]))
    if a.phase=='final':
        selected=root/'presentation/p1a_v1_2_7_selected_presentation.json'
        check(selected.is_file(),'selected presentation record absent')
        if selected.is_file(): check(load(selected).get('status')=='PASS','selected presentation record not PASS')
    result={'schema':'district_zero.p1a.v1_2_7.successor_static_verifier_result.v1','status':'PASS' if not errors else 'FAIL','phase':a.phase,'error_count':len(errors),'errors':errors,'counts':counts}
    print(json.dumps(result,indent=2,sort_keys=True)); return 0 if not errors else 1
if __name__=='__main__': raise SystemExit(main())
