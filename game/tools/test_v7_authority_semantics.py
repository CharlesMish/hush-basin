#!/usr/bin/env python3
from __future__ import annotations
import argparse, importlib.util, json, pathlib, tempfile, shutil
from typing import Any

def load_module(path:pathlib.Path):
 spec=importlib.util.spec_from_file_location('v7_gate',path); assert spec and spec.loader
 mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod); return mod

def write_events(root:pathlib.Path,candidate:str,rows:list[dict[str,Any]])->None:
 p=root/'V7_AXIS_SENSITIVITY'/candidate/'runtime_vectors'/'RT_ROUTE_A1'/'events.jsonl'; p.parent.mkdir(parents=True,exist_ok=True)
 p.write_text(''.join(json.dumps(r,sort_keys=True)+'\n' for r in rows),encoding='utf-8',newline='\n')

def base_rows()->list[dict[str,Any]]:
 return [
  {'event':'TEST_DRIVER_ROUTE_PROJECTION','vector_tick':i,'physics_tick':i+1,'commanded_throttle':0.4,'commanded_brake':0.0,'commanded_steer':0.1,'observed_speed_mps':18.0+i*.01,'chainage_m':float(i),'signed_lateral_error_m':0.0,'velocity_course_angle_rad':0.0}
  for i in range(20)
 ]

def main()->int:
 ap=argparse.ArgumentParser();ap.add_argument('--root',required=True);args=ap.parse_args();root=pathlib.Path(args.root).resolve()
 gate=load_module(root/'tools/run_v1_2_4j_gate.py')
 reg=json.loads((root/'tests/fixtures/fast_route_driver_v7_candidates.json').read_text())
 static=json.loads((root/'tests/fixtures/fast_route_driver_v7_static_reference.json').read_text())
 errors=[]
 def check(c,m):
  if not c:errors.append(m)
 check(reg['candidate_count']==11,'candidate count')
 check(reg['maximum_total_new_a1_executions']==12,'A1 budget')
 check(len(reg['axis_sensitivity_stage']['candidate_order'])==4,'sensitivity count')
 check(len(reg['bounded_selection_stage']['candidate_order'])==7,'selection count')
 check(static['record_count']==33,'static record count')
 # Static plan axes P and L must alter at least one record on every tested route.
 rec={(r['candidate_id'],r['route_id']):r for r in static['records']}
 base='V7_SENS_BASE_P36_L40_H10'
 for axis,probe in {'P':'V7_SENS_P52_L40_H10','L':'V7_SENS_P36_L30_H10'}.items():
  changed=[]
  for route in ('A1','A2','X0'):
   a=rec[(base,route)];b=rec[(probe,route)]
   changed.append(any(a[k]!=b[k] for k in ('minimum_raw_cap_mps','first_planned_cap_below_21_chainage_m','first_planned_cap_below_18_chainage_m')))
  check(any(changed),f'{axis} static plan axis inactive')
 h=static['axis_operational_synthetic_fixtures']['H'];check(h['base_release'] is True and h['probe_release'] is False,'H synthetic decision inactive')
 # Exercise real wrapper sensitivity evaluator with command then trajectory differences.
 tmp=pathlib.Path(tempfile.mkdtemp(prefix='v7-semantic-'))
 try:
  rows=base_rows();write_events(tmp,base,rows)
  probes={'P':'V7_SENS_P52_L40_H10','L':'V7_SENS_P36_L30_H10','H':'V7_SENS_P36_L40_H20'}
  for j,(axis,cid) in enumerate(probes.items(),2):
   pr=json.loads(json.dumps(rows)); pr[j]['commanded_steer']+=0.01*j; pr[j+2]['observed_speed_mps']+=0.02*j; write_events(tmp,cid,pr)
  result=gate.evaluate_axis_sensitivity(tmp,base,probes,1e-6,1e-4,30)
  check(result['status']=='PASS' and all(v['active'] for v in result['axes'].values()),'active sensitivity case')
  dead=json.loads(json.dumps(rows));write_events(tmp,probes['H'],dead)
  result_dead=gate.evaluate_axis_sensitivity(tmp,base,probes,1e-6,1e-4,30)
  check(result_dead['status']=='STOP/RETHINK — AUTOMATED A1 GATE' and result_dead['axes']['H']['active'] is False,'dead axis stop case')
 finally:shutil.rmtree(tmp)
 source=(root/'tests/p1a_runtime_runner.gd').read_text()
 check('if commanded_throttle > 0.0 and commanded_brake > 0.0:' in source,'phase overlap guard absent')
 check('var commanded_throttle := 0.0' in source and 'if v7_phase == \"BRAKE_COMMIT\":\n\t\tcommanded_brake = 1.0' in source,'brake phase not zero-throttle/full-brake')
 check('DZP1A_PHASE_SEPARATED_BRAKE_CAPTURE_V1' in source,'V7 algorithm absent')
 output={'schema':'district_zero.p1a.v1_2_4j.v7_semantic_tests.v1','status':'PASS' if not errors else 'FAIL','error_count':len(errors),'errors':errors,'case_count':9,'pass_count':9-len(errors)}
 print(json.dumps(output,indent=2,sort_keys=True));return 0 if not errors else 1
if __name__=='__main__':raise SystemExit(main())
