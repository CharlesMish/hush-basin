#!/usr/bin/env python3
"""Complete Warm Overcast verification. Use a new evidence directory per run."""
from pathlib import Path
import argparse
import hashlib
import json
import re
import statistics
import subprocess
import sys
from launch import resolve_engine

ROOT=Path(__file__).resolve().parents[1]

def main():
    p=argparse.ArgumentParser();p.add_argument('--evidence',required=True,type=Path);p.add_argument('--native',action='store_true');args=p.parse_args()
    evidence=args.evidence.resolve();evidence.mkdir(parents=True,exist_ok=False)
    engine,version=resolve_engine(None);records=[]
    def run(name,cmd,expected=None):
        print(name,flush=True)
        r=subprocess.run(cmd,cwd=ROOT,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=600)
        (evidence/(name+'.stdout')).write_text(r.stdout)
        ok=r.returncode==0 and not re.search(r'SCRIPT ERROR:|Parse Error:|Failed to load script',r.stdout)
        if expected is not None:ok=ok and expected in r.stdout
        records.append({'name':name,'argv':[str(v) for v in cmd],'cwd':str(ROOT),'returncode':r.returncode,'pass':ok})
        print(('PASS ' if ok else 'FAIL ')+name,flush=True)
        return ok
    def godot(name,script,tail,headless=True):
        cmd=[str(engine)]
        if headless:cmd+=['--headless']
        else:cmd+=['--resolution','1280x720','--disable-vsync']
        cmd+=['--path',str(ROOT/'game'),'--script',script,'--log-file',str(evidence/(name+'.log')),'--',*tail]
        return run(name,cmd)
    run('static',[sys.executable,'tools/verify_world_polish.py','--regenerate','--result',str(evidence/'static.json')])
    run('preservation',[sys.executable,'tools/verify_overcast.py','--result',str(evidence/'preservation.json')])
    run('import',[str(engine),'--headless','--editor','--path',str(ROOT/'game'),'--import','--quit','--log-file',str(evidence/'import.log')])
    run('parse',[str(engine),'--headless','--editor','--path',str(ROOT/'game'),'--quit-after','2','--log-file',str(evidence/'parse.log')])
    godot('c1','res://tests/world_polish_c1.gd',['--output',str(evidence/'c1.jsonl')])
    expected=json.loads((ROOT/'docs/world_polish_baseline.json').read_text())
    c1=evidence/'c1.jsonl';match=c1.exists() and hashlib.sha256(c1.read_bytes()).hexdigest()==expected['synchronized_c1_trace_sha256']
    records.append({'name':'c1_exact_1260_tick_comparison','pass':match})
    godot('vehicle','res://tools/validate_vehicle_r7.gd',[])
    godot('run_v0','res://tests/run_v0_probe.gd',['--result',str(evidence/'run_v0.json')])
    godot('paused_retry','res://tests/paused_retry_addendum.gd',['--result',str(evidence/'paused_retry.json')])
    godot('runtime','res://tests/world_polish_runtime.gd',['--result',str(evidence/'runtime.json')],not args.native)
    godot('weather','res://tests/overcast_runtime.gd',['--result',str(evidence/'weather.json')],not args.native)
    for arm in ['enabled','disabled']:
        tail=['--output',str(evidence/('weather-motion-'+arm))]
        if arm=='disabled':tail+=['--weather-disabled']
        godot('weather_motion_'+arm,'res://tests/overcast_motion.gd',tail)
    a_path=evidence/'weather-motion-enabled/motion.json';b_path=evidence/'weather-motion-disabled/motion.json'
    if a_path.exists() and b_path.exists():
        a=json.loads(a_path.read_text())['records'];b=json.loads(b_path.read_text())['records']
        delta=max(abs(x-y) for va,vb in zip(a,b) for xa,xb in zip(va['trace'],vb['trace']) for x,y in zip(xa,xb))
        records.append({'name':'weather_enabled_disabled_motion','pass':delta==0.0,'maximum_component_difference':delta,'scope':'Same successor resources/collider construction, five input sequences including retained-obstacle contact; only weather processing/visibility differs.'})
    else:records.append({'name':'weather_enabled_disabled_motion','pass':False})
    for name in ['static','preservation','run_v0','paused_retry','runtime','weather']:
        result=evidence/(name+'.json')
        records.append({'name':name+'_result','pass':result.exists() and json.loads(result.read_text()).get('status')=='PASS'})
    if args.native:
        weather_baseline=json.loads((ROOT/'docs/overcast_baseline.json').read_text())
        godot('rain_contact','res://tests/overcast_rain_contact.gd',['--result',str(evidence/'rain-contact.json')],False)
        contact_path=evidence/'rain-contact.json'
        records.append({'name':'rain_contact_result','pass':contact_path.exists() and json.loads(contact_path.read_text()).get('status')=='PASS'})
        godot('survey','res://tests/world_polish_survey.gd',['--output',str(evidence/'survey')],False)
        after_path=evidence/'survey/survey.json'
        if after_path.exists():
            before=weather_baseline['survey']['records'];after=json.loads(after_path.read_text())['records']
            b=statistics.median(v['p95_ms'] for v in before);a=statistics.median(v['p95_ms'] for v in after)
            perf={'baseline_median_view_p95_ms':b,'successor_median_view_p95_ms':a,'ratio':a/b,'pass':a<=b*1.10,'scope':'Median of 25 matched static native views; desktop/compositor wall-clock sampling, not an uncapped GPU benchmark.','per_view':[{'id':v['id'],'before_ms':before[i]['p95_ms'],'after_ms':v['p95_ms']} for i,v in enumerate(after)]}
            (evidence/'performance.json').write_text(json.dumps(perf,indent=2)+'\n')
            records.append({'name':'native_performance_target','pass':perf['pass']})
        else:records.append({'name':'native_survey_result','pass':False})
        godot('motion_performance','res://tests/overcast_motion.gd',['--output',str(evidence/'motion-performance')],False)
        motion_path=evidence/'motion-performance/motion.json'
        if motion_path.exists():
            before=weather_baseline['motion']['records'];after=json.loads(motion_path.read_text())['records']
            def p95(rows):
                frames=sorted(v for row in rows for v in row['frame_times_ms'])
                return frames[int(len(frames)*.95)]
            b=p95(before);a=p95(after)
            perf={'baseline_p95_ms':b,'successor_p95_ms':a,'ratio':a/b,'pass':a<=b*1.10,'scope':'Pooled frame times across five matched scripted native drives, no capture I/O; desktop/compositor pacing included.','per_clip':[{'id':v['id'],'before_ms':before[i]['p95_ms'],'after_ms':v['p95_ms']} for i,v in enumerate(after)]}
            (evidence/'moving-performance.json').write_text(json.dumps(perf,indent=2)+'\n')
            records.append({'name':'moving_performance_target','pass':perf['pass']})
            max_delta=max(abs(x-y) for old,new in zip(before,after) for va,vb in zip(old['trace'],new['trace']) for x,y in zip(va,vb))
            (evidence/'cross-version-motion-diagnostic.json').write_text(json.dumps({'max_component_difference':max_delta,'note':'Diagnostic only: v1 and successor construct different render resources. Strict weather influence is tested with identical successor construction in enabled/disabled arms. The exact unchanged C1 fixture remains a required gate.'},indent=2)+'\n')
        else:records.append({'name':'moving_performance_result','pass':False})
        godot('motion_capture','res://tests/overcast_motion.gd',['--output',str(evidence/'motion-capture'),'--capture'],False)
    success=all(r['pass'] for r in records)
    result={'status':'PASS' if success else 'FAIL','engine':version,'native':args.native,'records':records}
    (evidence/'suite.json').write_text(json.dumps(result,indent=2)+'\n')
    print(result['status'],flush=True)
    return 0 if success else 1

if __name__=='__main__':sys.exit(main())
