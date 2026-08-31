#!/usr/bin/env python3
from __future__ import annotations
import argparse, ast, hashlib, json, pathlib, re, subprocess, sys
OVERLAY='v1.2.5'
WORLD='v1.2.3'
EVIDENCE_SHA='227f3aa338040f02487fea189c03a3158f97af7df9b864c8324e4b1d6685ac30'
J_PACKET_SHA='6000296b93ee9f941afb2751061b30982ae3d1587b3949aedc11c04240a64557'
ROUTE_SHA='f26283b6cd314ba1d27aebea0bf80d82fbf2426ee5f22b610b38c273fec73330'
FORBIDDEN={'.godot','__MACOSX','__pycache__','.pytest_cache','.mypy_cache'}
DELTA_PATH='evidence/v1_2_5_j_to_v1_2_5_delta_manifest.json'
CHECKSUM_PATH='PACKET_SHA256SUMS.txt'

def sha(p:pathlib.Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p:pathlib.Path):return json.loads(p.read_text(encoding='utf-8'))
def inventory(p:pathlib.Path):
 out={}
 for n,line in enumerate(p.read_text(encoding='utf-8').splitlines(),1):
  if not line:continue
  m=re.fullmatch(r'([0-9a-f]{64})  (.+)',line)
  if not m:raise ValueError(f'{p}:{n}: malformed checksum line')
  if m.group(2) in out:raise ValueError(f'{p}:{n}: duplicate path')
  out[m.group(2)]=m.group(1)
 return out
def substantive(p:pathlib.Path):
 out={}
 for n,line in enumerate(p.read_text(encoding='utf-8').splitlines(),1):
  if not line:continue
  m=re.fullmatch(r'([0-9a-f]{64})\t([0-9]+)\t(.+)',line)
  if not m:raise ValueError(f'{p}:{n}: malformed substantive line')
  out[m.group(3)]=(m.group(1),int(m.group(2)))
 return out
def find_p0(p:pathlib.Path):
 for q in (p/'District-Zero-P0-Source(1)',p/'District-Zero-P0-Source',p):
  if (q/'project.godot').is_file():return q
 return p
def all_files(root:pathlib.Path):return {p.relative_to(root).as_posix():p for p in root.rglob('*') if p.is_file()}
def delta_truth(root:pathlib.Path,base:pathlib.Path):
 cur=all_files(root);old=all_files(base);skip={CHECKSUM_PATH,DELTA_PATH};records=[]
 for path in sorted((set(cur)|set(old))-skip):
  op=old.get(path);np=cur.get(path);oh=sha(op) if op else None;nh=sha(np) if np else None
  if oh==nh:continue
  change='ADDED' if op is None else 'DELETED' if np is None else 'MODIFIED'
  records.append((path,change,oh,nh))
 return records

def main():
 ap=argparse.ArgumentParser(description='District Zero P1A v1.2.5 authority/implementation verifier')
 ap.add_argument('--root',required=True);ap.add_argument('--baseline-root',required=True);ap.add_argument('--p0-root',required=True);ap.add_argument('--phase',choices=['authority','implementation'],default='authority')
 a=ap.parse_args();root=pathlib.Path(a.root).resolve();base=pathlib.Path(a.baseline_root).resolve();p0=find_p0(pathlib.Path(a.p0_root).resolve());errors=[];counts={}
 def check(c,m):
  if not c:errors.append(m)
 # Packet identity.
 try:
  inv=inventory(root/CHECKSUM_PATH);files=all_files(root);expected=set(files)-{CHECKSUM_PATH};bad=[r for r,d in inv.items() if r not in files or sha(files[r])!=d]
  check(not bad and set(inv)==expected,'packet inventory mismatch');counts['packet_records']=len(inv)
 except Exception as e:errors.append('packet inventory '+str(e))
 try:
  binv=inventory(base/CHECKSUM_PATH);check(len(binv)==1795 and all((base/r).is_file() and sha(base/r)==d for r,d in binv.items()),'J baseline inventory mismatch');counts['j_baseline_records']=len(binv)
 except Exception as e:errors.append('J baseline '+str(e))
 try:
  pinv=substantive(root/'P0_SUBSTANTIVE_SHA256SUMS.txt');check(len(pinv)==147 and all((p0/r).is_file() and (p0/r).stat().st_size==s and sha(p0/r)==d for r,(d,s) in pinv.items()),'P0 mismatch');counts['p0_files']=len(pinv)
 except Exception as e:errors.append('P0 '+str(e))
 # Active authority and truthful status.
 chain=load(root/'P1A_ACTIVE_AUTHORITY_CHAIN.json');status=(root/'STATUS.md').read_text(encoding='utf-8');send=(root/'P1A_CODEX_SENDOFF.md').read_text(encoding='utf-8');world=(root/'P1A_WORLD_AUTHORITY.md').read_text(encoding='utf-8');play=(root/'P1A_PLAYTEST_CARD.md').read_text(encoding='utf-8')
 check(chain.get('active_test_overlay_authority')==OVERLAY,'overlay not v1.2.5');check(chain.get('world_data_authority')==WORLD,'world authority changed')
 check(chain.get('active_replay_algorithm_id')=='DZP1A_NORMALIZED_HUMAN_INPUT_REPLAY_V1','replay identity wrong');check(chain.get('active_replay_controller')=='NORMALIZED_INPUT_TRACE_REPLAY_V1','replay controller wrong')
 check(chain.get('autonomous_controller_development')=='RETIRED_V4_THROUGH_V7','autonomous lane not retired');check(chain.get('operative_gate_wrapper')=='tools/run_v1_2_5_gate.py','wrapper not v1.2.5')
 check(chain.get('human_trace_required_as_input') is False,'packet incorrectly requires pre-existing human trace')
 check('READY FOR CODEX — INSTRUMENTED HUMAN FEASIBILITY CAPTURE' in status,'status outcome wrong')
 check('Human feasibility attempts: `NOT PERFORMED`' in status and 'Human World Gate: `NOT PERFORMED`' in status and 'P1B: `FROZEN`' in status,'truthful status/boundary missing')
 check('run_v1_2_4j_gate.py' not in send and '--output-root' not in send,'stale/unsupported operative sendoff')
 check('v1.2.4J V7 sensitivity gate passes' not in play,'future Human World Gate retains stale J unlock')
 check('run_v1_2_4j_gate.py' not in (root/'tools/run_selected_c1.py').read_text(encoding='utf-8'),'selected C1 retains stale cleanup owner')
 check('No V8' in world and 'Human World Gate and P1B boundaries' in world,'scope boundary missing')
 # Historical exact-engine J evidence.
 hist=root/'evidence/historical/v1_2_4j_automated_a1_stop'
 try:
  hinv=inventory(hist/'SHA256SUMS.txt');check(len(hinv)==225 and all((hist/r).is_file() and sha(hist/r)==d for r,d in hinv.items()),'J evidence not 225/225');counts['j_evidence_records']=len(hinv)
  g=load(hist/'gate_result.json');check(g.get('status')=='STOP/RETHINK — AUTOMATED A1 GATE' and g.get('terminal_stage')=='FAST_ROUTE_GATE' and g.get('details',{}).get('primary_failure_class')=='TEST_DRIVER','J terminal mismatch')
  ax=load(hist/'FAST_ROUTE_GATE/v7_axis_sensitivity_result.json');check(ax.get('status')=='PASS' and all(ax.get('axes',{}).get(x,{}).get('active') for x in ('P','L','H')),'J axes not active')
  cp=load(hist/'COPY_SELECTED_PROJECT/result.json');check(cp.get('status')=='PASS' and cp.get('byte_identical_file_count')==1796 and cp.get('source_file_count')==1796,'J source copy mismatch')
 except Exception as e:errors.append('J evidence '+str(e))
 jv=load(root/'evidence/v1_2_5_j_executed_evidence_verification.json')
 check(jv.get('evidence',{}).get('transport_sha256')==EVIDENCE_SHA and jv.get('evidence',{}).get('root_checksum_records')==225,'J verification transport identity mismatch')
 check(jv.get('source_packet',{}).get('transport_sha256')==J_PACKET_SHA and jv.get('source_packet',{}).get('executed_copy_byte_identical')==1796,'J source verification mismatch')
 check(jv.get('bounded_selection',{}).get('candidate_count')==7 and jv.get('bounded_selection',{}).get('executed_fail_count')==7 and jv.get('bounded_selection',{}).get('selected_candidate') is None,'J bounded selection mismatch')
 closest=jv.get('closest_to_full_A1_pass',{});check(closest.get('candidate_id')=='V7_P36_L30_H20' and abs(closest.get('maximum_chainage_m',0)-186.663087596163)<1e-9 and abs(closest.get('maximum_lateral_distance_m',0)-11.0017594750954)<1e-9,'closest J failure mismatch')
 # Frozen bytes against executed J.
 pres=load(base/'evidence/v1_2_4j_preservation_assertions.json')
 for key,n in [('formal_frozen_file_sha256',19),('selected_project_world_file_sha256',41)]:
  tab=pres[key];bad=[r for r,d in tab.items() if not (root/r).is_file() or sha(root/r)!=d];check(len(tab)==n and not bad,f'{key} preservation failed {bad[:5]}');counts[key]=len(tab)
 # Vectors: 37 exact, 3 only evidence-controller replacement.
 old=load(base/'tests/fixtures/runtime_vectors.json');new=load(root/'tests/fixtures/runtime_vectors.json');om={x['id']:x for x in old['vectors']};nm={x['id']:x for x in new['vectors']};fast={'RT_ROUTE_A1','RT_ROUTE_A2','RT_ROUTE_X0'}
 check(set(om)==set(nm) and len(nm)==40,'vector count/IDs changed')
 for vid in nm:
  if vid not in fast:check(nm[vid]==om[vid],f'non-fast vector changed {vid}')
  else:
   for fld in ('spawn_transform','termination','thresholds','expected_events','initial_mode','initial_linear_velocity_xyz_mps','reset_rule','fixed_physics_timestep_s','authority_claim'):
    check(nm[vid].get(fld)==om[vid].get(fld),f'{vid} protected {fld} changed')
   cc=nm[vid]['controller_commands'];check(cc.get('type')=='NORMALIZED_INPUT_TRACE_REPLAY_V1' and cc.get('position_or_velocity_writes')=='FORBIDDEN' and cc.get('input_actions_only')==['throttle','brake','steer_left','steer_right','transform'],f'{vid} replay authority missing')
 counts['runtime_vectors']=len(nm);counts['non_fast_vectors_unchanged']=37
 # Protocol and CLI semantic suites.
 for script,key,expected in [('tools/test_human_feasibility_authority.py','human_feasibility_semantic_cases',18),('tools/test_v1_2_5_cli_authority.py','cli_semantic_cases',12)]:
  run=subprocess.run([sys.executable,'-B',str(root/script),'--root',str(root)],capture_output=True,text=True,cwd=root)
  try:rj=json.loads(run.stdout)
  except Exception as e:rj={};errors.append(f'{script} output '+str(e))
  check(run.returncode==0 and rj.get('status')=='PASS' and rj.get('pass_count')==expected,f'{script} failed');counts[key]=rj.get('case_count',0)
 protocol=load(root/'tests/fixtures/human_feasibility_protocol.json');check(protocol.get('route_order')==['A1','A2','X0'] and protocol.get('replay',{}).get('required_repetitions')==3,'protocol order/replays wrong');check(protocol.get('P1B')=='FROZEN','P1B changed')
 ser=load(root/'tests/fixtures/human_trace_serialization_contract.json');inp=load(root/'tests/fixtures/human_input_trace.schema.json');check(ser.get('self_hashing_fields')=='FORBIDDEN' and 'raw_trace_sha256' not in inp['properties']['terminal']['properties'],'circular trace identity')
 # Authority versus implementation phase.
 impl=load(root/'evidence/v1_2_5_capture_implementation_manifest.json')
 if a.phase=='implementation':
  check(impl.get('status')=='PASS','capture implementation manifest not PASS')
  check(impl.get('exact_godot')=='4.7.1.stable.official.a13da4feb','implementation exact engine missing')
  check(impl.get('instrumentation_inactive_c1',{}).get('maximum_delta')==0.0 and impl.get('instrumentation_inactive_c1',{}).get('status')=='PASS','instrumentation-inactive C1 not zero-delta')
  for p in ['tests/p1a_human_feasibility_runner.gd','tools/run_human_feasibility_session.py','tools/validate_human_feasibility_evidence.py']:
   check((root/p).is_file(),f'missing implementation {p}')
 else:
  check(impl.get('status')=='CODEX_IMPLEMENTATION_REQUIRED','director packet implementation status not pending')
  check(not (root/'tests/p1a_human_feasibility_runner.gd').exists() and not (root/'tools/run_human_feasibility_session.py').exists() and not (root/'tools/validate_human_feasibility_evidence.py').exists(),'director packet misleadingly contains unverified capture implementation')
 # Syntax, schemas, route identity.
 pybad=[]
 for p in root.rglob('*.py'):
  try:ast.parse(p.read_text(encoding='utf-8'))
  except Exception as e:pybad.append(str(p.relative_to(root))+':'+str(e))
 check(not pybad,'Python parse errors '+str(pybad[:5]));counts['python_files']=len(list(root.rglob('*.py')))
 jbad=[]
 for p in root.rglob('*.json'):
  try:load(p)
  except Exception as e:jbad.append(str(p.relative_to(root))+':'+str(e))
 check(not jbad,'JSON parse errors '+str(jbad[:5]));counts['json_files']=len(list(root.rglob('*.json')))
 for p in ['tests/fixtures/human_input_trace.schema.json','tests/fixtures/human_state_trace.schema.json','tests/fixtures/human_capture_telemetry.schema.json','tests/fixtures/human_capture_attempt_result.schema.json','tests/fixtures/human_replay_result.schema.json','tests/fixtures/selected_human_trace_manifest.schema.json']:
  check((root/p).is_file() and load(root/p).get('$schema')=='https://json-schema.org/draft/2020-12/schema',f'schema absent/invalid {p}')
 bake=load(root/'world/generated/route_bake.json');check(bake.get('total_point_count')==11252 and bake.get('fixed_global_compact_array_sha256')==ROUTE_SHA,'route bake changed');counts['routes']=len(bake.get('routes',{}));counts['route_points']=bake.get('total_point_count')
 # Exact J→v1.2.5 delta manifest.
 delta=root/DELTA_PATH;check(delta.is_file(),'delta manifest absent')
 if delta.is_file():
  d=load(delta);truth=delta_truth(root,base);recs=d.get('records',[]);got={(x.get('path'),x.get('change'),x.get('old_sha256'),x.get('new_sha256')) for x in recs};want=set(truth)
  check(d.get('source_authority')=='v1.2.4J' and d.get('successor_authority')=='v1.2.5','delta identities wrong')
  check(d.get('record_count')==len(recs) and got==want and all(x.get('purpose') for x in recs),'delta manifest does not exactly match bytes');counts['delta_records']=len(recs)
  check(any(x.get('path')=='P1A_WORLD_AUTHORITY.md' and x.get('change')=='MODIFIED' for x in recs),'no substantive authority delta')
 # Forbidden package contents.
 bad=[]
 for p in root.rglob('*'):
  rel=p.relative_to(root)
  if any(x in FORBIDDEN for x in rel.parts) or p.name=='.DS_Store' or p.name.startswith('._') or (p.is_file() and p.suffix.lower() in {'.zip','.tar','.gz','.7z','.rar'}):bad.append(rel.as_posix())
 check(not bad,'forbidden entries '+str(bad[:10]))
 out={'schema':'district_zero.p1a.v1_2_5.static_verifier_result.v1','status':'PASS' if not errors else 'FAIL','phase':a.phase,'error_count':len(errors),'errors':errors,'anti_duplication_gate':'PASS' if not errors else 'FAIL','counts':counts}
 print(json.dumps(out,indent=2,sort_keys=True));return 0 if not errors else 1
if __name__=='__main__':raise SystemExit(main())
