#!/usr/bin/env python3
from __future__ import annotations
import argparse, importlib.util, json, pathlib, sys

def load_module(path,name):
    spec=importlib.util.spec_from_file_location(name,path); mod=importlib.util.module_from_spec(spec); assert spec and spec.loader; spec.loader.exec_module(mod); return mod

def main()->int:
    ap=argparse.ArgumentParser();ap.add_argument('--root',required=True);a=ap.parse_args();root=pathlib.Path(a.root).resolve();cases=[]
    def case(name,cond,detail=''):cases.append({'id':name,'pass':bool(cond),'detail':detail if not cond else ''})
    runner=load_module(root/'tools/run_v1_2_7_calibration.py','v127runner');metrics=load_module(root/'tools/p1a_v1_2_7_metrics.py','v127metrics');reg=json.loads((root/'tests/fixtures/v1_2_7_calibration_registry.json').read_text());acc=json.loads((root/'tests/fixtures/v1_2_6_visual_acceptance.json').read_text())
    ev=root/'director_inputs/v1_2_6_run1_validation_evidence/NATIVE_VISUALS'
    images={'FREE_ROAM:on':ev/'free-roam-after-native.png','FREE_ROAM:off':ev/'free-roam-after-shadow-off-reference.png','A1_FAMILIARIZATION:on':ev/'a1-after-native.png','A1_FAMILIARIZATION:off':ev/'a1-after-shadow-off-reference.png'}
    recomputed=metrics.compute(acc,images); original=json.loads((ev/'native-visual-metric-result.json').read_text())
    case('METRIC_CHECK_COUNT_21',len(recomputed['checks'])==21)
    case('METRIC_EXACT_REPRODUCTION',all(x['id']==y['id'] and x['pass']==y['pass'] and abs(x['observed']-y['observed'])<1e-15 for x,y in zip(recomputed['checks'],original['checks'])))
    fails=[c['id'] for c in recomputed['checks'] if not c['pass']]
    case('RUN1_FAILURE_SET_EXACT',fails==['A1_FAMILIARIZATION:left_outer_closure:shadow_on_min','A1:right_obstacle_separation'])
    case('OUTER_FEASIBLE_INTERVAL',reg['outer_closure']['measured_Y_feasible_interval']==[0.075,0.0791557292161208] and abs(reg['outer_closure']['balanced_target_Y']-0.0770778646080604)<1e-15)
    case('CANDIDATE_CAP_82',reg['absolute_candidate_engine_launch_cap']==82)
    case('FALLBACK_IS_SINGLE_LOCAL_SHADED_FAMILY',reg['fallback']['family']=='MATERIAL_LOCAL_LOW_EMISSION_WHILE_NORMALLY_SHADED' and reg['fallback']['unlit_forbidden'] is True)
    p={'OUTER_CLOSURE_MASK':{'albedo_scale':1.1,'emission_multiplier':0.0},'CORE_WALL':{'albedo_scale':1.2,'emission_multiplier':0.0}}
    case('CANDIDATE_ID_DETERMINISTIC',runner.candidate_id('X',1,p)==runner.candidate_id('X',1,json.loads(json.dumps(p))))
    complete={'candidate_id':'x','parameters':p,'engine_identity':runner.EXACT,'command':['x'],'project_material_source_sha256':'0'*64,'images':{str(i):{} for i in range(4)},'metrics':{},'ray_result':{},'stdout_sha256':'1','stderr_sha256':'2'}
    case('EVIDENCE_COMPLETENESS_TRUE',runner.evidence_complete(complete))
    incomplete=dict(complete);incomplete.pop('stderr_sha256');case('EVIDENCE_COMPLETENESS_FALSE',not runner.evidence_complete(incomplete))
    case('NO_INTERVAL_STOP_LITERAL',runner.stop_status('no_candidate')=='NO_PRESENTATION_ONLY_INTERVAL')
    # Patch test: baseline must change only the registered material literals, with optional marker-scoped emission.
    baseline=(root/'tests/fixtures/v1_2_7_v1_2_6_world_builder.gd').read_text();patched=runner.patch_builder(baseline,p,reg)
    case('PATCH_OUTER_LITERAL', 'return Color(0.41800000, 0.46200000, 0.48400000)' in patched)
    case('PATCH_WALL_LITERAL', 'return Color(0.72000000, 0.75600000, 0.81600000)' in patched)
    # Synthetic combined-selection records.
    def record(cid,os,ws,y,right,allpass=True,rays=True):
        checks=[{'id':f'C{i}','observed':1.0,'pass':allpass} for i in range(21)]
        return {'candidate_id':cid,'parameters':{'OUTER_CLOSURE_MASK':{'albedo_scale':os,'emission_multiplier':0.0},'CORE_WALL':{'albedo_scale':ws,'emission_multiplier':0.0}},'metrics':{'status':'PASS' if allpass else 'FAIL','checks':checks,'views':{'A1_FAMILIARIZATION':{'left_outer_closure':{'shadow_on_Y':y},'obstacle_separation':{'right_absolute_Y':right}}}},'ray_result':{'status':'PASS' if rays else 'FAIL','sample_count':14,'mismatch_count':0 if rays else 1}}
    boundary=record('A-boundary',1.01,1.01,0.0751,0.126);center=record('B-center',1.10,1.10,reg['outer_closure']['balanced_target_Y'],0.126)
    case('SELECTION_PREFERS_OUTER_INTERIOR',runner.select_combined([boundary,center],reg)['candidate_id']=='B-center')
    weak=record('A-weak-wall',1.08,1.08,reg['outer_closure']['balanced_target_Y'],0.121);robust=record('B-robust-wall',1.10,1.10,reg['outer_closure']['balanced_target_Y'],0.126)
    case('SELECTION_PREFERS_WALL_MARGIN_WHERE_FEASIBLE',runner.select_combined([weak,robust],reg)['candidate_id']=='B-robust-wall')
    small=record('A-small-delta',1.05,1.05,reg['outer_closure']['balanced_target_Y'],0.127);large=record('B-large-delta',1.10,1.10,reg['outer_closure']['balanced_target_Y'],0.127)
    case('SELECTION_MINIMIZES_PRESENTATION_DELTA',runner.select_combined([large,small],reg)['candidate_id']=='A-small-delta')
    bad=record('bad',1.0,1.0,reg['outer_closure']['balanced_target_Y'],0.13,allpass=False);case('SELECTION_REJECTS_VISUAL_FAILURE',runner.select_combined([bad],reg) is None)
    badray=record('badray',1.0,1.0,reg['outer_closure']['balanced_target_Y'],0.13,rays=False);case('SELECTION_REJECTS_RAY_FAILURE',runner.select_combined([badray],reg) is None)
    status='PASS' if all(c['pass'] for c in cases) else 'FAIL';result={'schema':'district_zero.p1a.v1_2_7.calibration_semantic_test_result.v1','status':status,'case_count':len(cases),'pass_count':sum(c['pass'] for c in cases),'cases':cases};print(json.dumps(result,indent=2,sort_keys=True));return 0 if status=='PASS' else 1
if __name__=='__main__':raise SystemExit(main())
