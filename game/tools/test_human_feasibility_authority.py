#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, pathlib

def load(p): return json.loads(p.read_text(encoding='utf-8'))
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--root',required=True);a=ap.parse_args();r=pathlib.Path(a.root)
 p=load(r/'tests/fixtures/human_feasibility_protocol.json');rv=load(r/'tests/fixtures/runtime_vectors.json');ch=load(r/'P1A_ACTIVE_AUTHORITY_CHAIN.json');ser=load(r/'tests/fixtures/human_trace_serialization_contract.json');inp=load(r/'tests/fixtures/human_input_trace.schema.json');impl=load(r/'tests/fixtures/human_capture_implementation_contract.json')
 cases=[]
 def case(name,ok): cases.append({'name':name,'pass':bool(ok)})
 case('route order',p['route_order']==['A1','A2','X0'])
 case('five attempts',all(p['route_specs'][x]['max_attempts']==5 for x in p['route_order']))
 case('five-minute familiarization',p['familiarization']['maximum_seconds_per_route']==300)
 case('first pass selection',p['recorded_attempts']['selection_rule']=='FIRST_FULL_PASS_IN_ATTEMPT_ORDER')
 case('three replays',p['replay']['required_repetitions']==3)
 case('no metric override',p['evidence_policy']['human_judgment_cannot_override_hard_metric'] is True)
 case('human gate separate',p['evidence_policy']['later_human_world_gate_remains_separate'] is True)
 case('autonomous retired',p['autonomous_controller_development']=='RETIRED_AFTER_V7_FAMILY_EXHAUSTION' and ch['autonomous_controller_development']=='RETIRED_V4_THROUGH_V7')
 case('no human trace input required',ch['human_trace_required_as_input'] is False and 'No human trace is a required input' in p['implementation_gate'])
 expected={'A1':(64.372840,190.291358,11.0),'A2':(88.456389,289.825556,11.0),'X0':(99.976210,342.304838,8.0)}
 m={v['controller_commands']['route_id']:v for v in rv['vectors'] if v['id'] in {'RT_ROUTE_A1','RT_ROUTE_A2','RT_ROUTE_X0'}}
 case('three replay vectors',set(m)==set(expected) and all(v['controller_commands']['type']=='NORMALIZED_INPUT_TRACE_REPLAY_V1' for v in m.values()))
 case('unchanged thresholds',all(abs(m[k]['thresholds']['minimum_distance_at_or_above_fast_route_speed_m']-x[0])<1e-9 and abs(m[k]['thresholds']['minimum_genuine_classified_distance_m']-x[1])<1e-9 and abs(m[k]['thresholds']['maximum_test_driver_path_deviation_m']-x[2])<1e-9 for k,x in expected.items()))
 case('normal inputs only',all(m[k]['controller_commands']['input_actions_only']==['throttle','brake','steer_left','steer_right','transform'] for k in expected))
 case('P1B frozen',p['P1B']=='FROZEN')
 case('detached raw hashes',ser['self_hashing_fields']=='FORBIDDEN' and 'raw_trace_sha256' not in inp['properties']['terminal']['properties'])
 case('canonical serialization exact',ser['json_document']['encoding']=='UTF-8' and ser['json_document']['line_endings']=='LF' and ser['json_document']['terminal_newline']=='REQUIRED')
 case('attempt evidence complete',set(impl['canonical_artifacts_per_attempt'])=={'argv.json','engine_identity.json','project_identity.json','input_trace.json','telemetry.json','state_trace.json','attempt_result.json','stdout.txt','stderr.txt','engine.txt','SHA256SUMS.txt'})
 case('terminal evidence before cleanup',impl['evidence_packaging']['every_terminal_path_requires_standalone_zip'] is True and impl['evidence_packaging']['finalize_before_disposable_cleanup'] is True)
 case('schemas all present',all((r/x).is_file() for x in ['tests/fixtures/human_input_trace.schema.json','tests/fixtures/human_state_trace.schema.json','tests/fixtures/human_capture_telemetry.schema.json','tests/fixtures/human_capture_attempt_result.schema.json','tests/fixtures/human_replay_result.schema.json','tests/fixtures/selected_human_trace_manifest.schema.json']))
 bad=[c for c in cases if not c['pass']]
 out={'schema':'district_zero.p1a.v1_2_5.human_feasibility_semantic_tests.v1','status':'PASS' if not bad else 'FAIL','case_count':len(cases),'pass_count':len(cases)-len(bad),'fail_count':len(bad),'cases':cases}
 print(json.dumps(out,indent=2,sort_keys=True));return 0 if not bad else 1
if __name__=='__main__': raise SystemExit(main())
