#!/usr/bin/env python3
from __future__ import annotations
import argparse, datetime as dt, hashlib, json, math, pathlib, re, shutil, subprocess, sys, zipfile
from typing import Any

ROOT_DEFAULT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT_DEFAULT/'tools'))
from p1a_v1_2_7_metrics import compute as compute_metrics

EXACT='4.7.1.stable.official.a13da4feb'
BASE_BUILDER='tests/fixtures/v1_2_7_v1_2_6_world_builder.gd'
ACCEPTANCE='tests/fixtures/v1_2_6_visual_acceptance.json'
PROBE='res://tests/p1a_v1_2_7_visual_probe.gd'

class StopRun(RuntimeError):
    def __init__(self,status:str,detail:str): super().__init__(detail); self.status=status; self.detail=detail

def sha(p:pathlib.Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p:pathlib.Path,v:Any)->None:p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,indent=2,sort_keys=True,ensure_ascii=False)+'\n',encoding='utf-8')
def write(p:pathlib.Path,s:str)->None:p.parent.mkdir(parents=True,exist_ok=True);p.write_text(s,encoding='utf-8')
def run(cmd:list[str],cwd:pathlib.Path)->subprocess.CompletedProcess[str]:return subprocess.run(cmd,cwd=cwd,capture_output=True,text=True,check=False)
def quantize(value:float,q:float)->float:return round(round(value/q)*q,10)
def candidate_id(stage:str,index:int,params:dict[str,Any])->str:
    key=json.dumps(params,sort_keys=True,separators=(',',':')).encode(); return f'{stage}-{index:03d}-{hashlib.sha256(key).hexdigest()[:10]}'
def evidence_complete(record:dict[str,Any])->bool:
    required={'candidate_id','parameters','engine_identity','command','project_material_source_sha256','images','metrics','ray_result','stdout_sha256','stderr_sha256'}
    return required.issubset(record) and record.get('engine_identity')==EXACT and len(record.get('images',{}))==4

def metric_map(record:dict[str,Any])->dict[str,dict[str,Any]]:return {c['id']:c for c in record['metrics']['checks']}
def local_pass(record:dict[str,Any],material:str,registry:dict[str,Any])->bool:
    if record.get('ray_result',{}).get('status')!='PASS' or record['ray_result'].get('sample_count')!=14:return False
    allowed=set(registry['outer_closure' if material=='OUTER_CLOSURE_MASK' else 'core_wall']['allowed_unresolved_check_during_independent_stage'])
    if any((not c['pass']) and c['id'] not in allowed for c in record['metrics']['checks']):return False
    m=record['metrics']['views']['A1_FAMILIARIZATION']
    if material=='OUTER_CLOSURE_MASK':
        y=m['left_outer_closure']['shadow_on_Y']; lo,hi=registry['outer_closure']['measured_Y_feasible_interval']; return lo<=y<=hi
    return m['obstacle_separation']['right_absolute_Y']>=registry['core_wall']['required_separation_Y']
def target_value(record:dict[str,Any],material:str)->float:
    m=record['metrics']['views']['A1_FAMILIARIZATION']
    return m['left_outer_closure']['shadow_on_Y'] if material=='OUTER_CLOSURE_MASK' else m['obstacle_separation']['right_absolute_Y']
def presentation_delta(params:dict[str,Any],registry:dict[str,Any])->float:
    total=0.0
    for material in ('OUTER_CLOSURE_MASK','CORE_WALL'):
        base=registry['base_materials'][material]['rgb']; p=params[material]; scale=float(p.get('albedo_scale',1.0)); emission=float(p.get('emission_multiplier',0.0)); rgb=[x*scale for x in base]
        total+=sum(abs(a-b) for a,b in zip(rgb,base)); total+=sum(abs(x*emission) for x in rgb)
    return total
def select_combined(records:list[dict[str,Any]],registry:dict[str,Any])->dict[str,Any]|None:
    eligible=[r for r in records if r.get('metrics',{}).get('status')=='PASS' and r.get('ray_result',{}).get('status')=='PASS' and r['ray_result'].get('sample_count')==14 and r['ray_result'].get('mismatch_count')==0]
    if not eligible:return None
    center=registry['outer_closure']['balanced_target_Y']; half=registry['outer_closure']['preferred_interior_half_width_Y']
    interior=[r for r in eligible if abs(r['metrics']['views']['A1_FAMILIARIZATION']['left_outer_closure']['shadow_on_Y']-center)<=half]
    if interior: eligible=interior
    else:
        lo,hi=registry['outer_closure']['measured_Y_feasible_interval']
        def outer_margin(r):
            y=r['metrics']['views']['A1_FAMILIARIZATION']['left_outer_closure']['shadow_on_Y']; return min(y-lo,hi-y)
        best=max(outer_margin(r) for r in eligible); eligible=[r for r in eligible if abs(outer_margin(r)-best)<=1e-15]
    robust=[r for r in eligible if r['metrics']['views']['A1_FAMILIARIZATION']['obstacle_separation']['right_absolute_Y']>=registry['core_wall']['bisection_target_separation_Y']]
    if robust: eligible=robust
    lo,hi=registry['outer_closure']['measured_Y_feasible_interval']
    def key(r):
        y=r['metrics']['views']['A1_FAMILIARIZATION']['left_outer_closure']['shadow_on_Y']; outer=min(y-lo,hi-y); right=r['metrics']['views']['A1_FAMILIARIZATION']['obstacle_separation']['right_absolute_Y']-registry['core_wall']['required_separation_Y']
        return (presentation_delta(r['parameters'],registry),-outer,-right,r['candidate_id'])
    return sorted(eligible,key=key)[0]
def stop_status(reason:str)->str:
    return 'NO_PRESENTATION_ONLY_INTERVAL' if reason=='no_candidate' else reason

def patch_builder(baseline:str,params:dict[str,Any],registry:dict[str,Any])->str:
    out=baseline
    colors={}
    for material in ('OUTER_CLOSURE_MASK','CORE_WALL'):
        scale=float(params[material].get('albedo_scale',1.0)); base=registry['base_materials'][material]['rgb']; rgb=[x*scale for x in base]
        if any(x<0 or x>1 for x in rgb): raise ValueError(f'{material} channel outside [0,1]: {rgb}')
        colors[material]=rgb
    o=', '.join(f'{x:.8f}' for x in colors['OUTER_CLOSURE_MASK']); c=', '.join(f'{x:.8f}' for x in colors['CORE_WALL'])
    old='\t\treturn Color(0.38, 0.42, 0.44)'; new=f'\t\treturn Color({o})'
    if old not in out: raise ValueError('OUTER_CLOSURE_MASK baseline literal not found')
    out=out.replace(old,new,1)
    old='\treturn Color(0.60, 0.63, 0.68)'; new=f'\treturn Color({c})'
    if old not in out: raise ValueError('CORE_WALL baseline literal not found')
    out=out.replace(old,new,1)
    emission=[]
    for material in ('OUTER_CLOSURE_MASK','CORE_WALL'):
        e=float(params[material].get('emission_multiplier',0.0))
        if e>0:
            emission += [f'\tif source_id == "{material}":', '\t\tmaterial.emission_enabled = true', f'\t\tmaterial.emission = material.albedo_color * {e:.8f}']
    if emission:
        anchor='\t\tmaterial.transparency = BaseMaterial3D.TRANSPARENCY_DISABLED\n'
        block='\t\tmaterial.transparency = BaseMaterial3D.TRANSPARENCY_DISABLED\n\t# V1_2_7_CALIBRATION_EMISSION_BEGIN\n'+'\n'.join(emission)+'\n\t# V1_2_7_CALIBRATION_EMISSION_END\n'
        if anchor not in out: raise ValueError('material insertion anchor absent')
        out=out.replace(anchor,block,1)
    return out

def copy_project(root:pathlib.Path,dst:pathlib.Path)->None:
    def ign(_d,names):return {n for n in names if n in {'.godot','__pycache__','director_inputs'} or n.endswith(('.pyc','.pyo'))}
    shutil.copytree(root,dst,ignore=ign)
def write_inventory(root:pathlib.Path)->int:
    inv=root/'PACKET_SHA256SUMS.txt'; files=sorted((p for p in root.rglob('*') if p.is_file() and p!=inv and '.godot' not in p.parts and '__pycache__' not in p.parts),key=lambda p:p.relative_to(root).as_posix().encode())
    write(inv,''.join(f'{sha(p)}  {p.relative_to(root).as_posix()}\n' for p in files)); return len(files)
def deterministic_zip(source:pathlib.Path,output:pathlib.Path,exclude_names:set[str]|None=None)->dict[str,Any]:
    exclude_names=exclude_names or set(); output.parent.mkdir(parents=True,exist_ok=True)
    if output.exists():output.unlink()
    with zipfile.ZipFile(output,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for p in sorted((x for x in source.rglob('*') if x.is_file() and x.name not in exclude_names and '.godot' not in x.parts and '__pycache__' not in x.parts),key=lambda x:x.relative_to(source).as_posix().encode()):
            info=zipfile.ZipInfo(source.name+'/'+p.relative_to(source).as_posix(),(1980,1,1,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=(0o100755 if p.stat().st_mode&0o111 else 0o100644)<<16;z.writestr(info,p.read_bytes())
    with zipfile.ZipFile(output) as z: bad=z.testzip(); names=z.namelist()
    return {'path':str(output),'sha256':sha(output),'byte_size':output.stat().st_size,'integrity':'PASS' if bad is None and len(names)==len(set(names)) else 'FAIL','entry_count':len(names)}

class Director:
    def __init__(self,args):
        self.root=pathlib.Path(args.root).resolve(); self.godot=str(pathlib.Path(args.godot).resolve()); self.work=pathlib.Path(args.work_root).resolve(); self.evidence=pathlib.Path(args.evidence_root).resolve(); self.session=pathlib.Path(args.prepared_session_root).resolve()
        self.registry=json.loads((self.root/'tests/fixtures/v1_2_7_calibration_registry.json').read_text()); self.acceptance=json.loads((self.root/ACCEPTANCE).read_text()); self.baseline=(self.root/BASE_BUILDER).read_text(); self.launches=0; self.index=0; self.cache={}; self.records=[]
    def preflight(self):
        if self.work.exists():shutil.rmtree(self.work)
        if self.evidence.exists():shutil.rmtree(self.evidence)
        self.work.mkdir(parents=True);self.evidence.mkdir(parents=True)
        v=run([self.godot,'--version'],self.root); dump(self.evidence/'ENGINE_IDENTITY.json',{'argv':[self.godot,'--version'],'stdout':v.stdout,'stderr':v.stderr,'required':EXACT,'observed':v.stdout.strip(),'match':v.stdout.strip()==EXACT})
        if v.stdout.strip()!=EXACT: raise StopRun('BLOCKED/NOT TESTABLE — EXACT ENGINE','exact engine unavailable')
        check=run([sys.executable,'-B',str(self.root/'tools/verify_v1_2_7_successor.py'),'--root',str(self.root),'--phase','director'],self.root); write(self.evidence/'DIRECTOR_PREFLIGHT.stdout.txt',check.stdout);write(self.evidence/'DIRECTOR_PREFLIGHT.stderr.txt',check.stderr)
        if check.returncode!=0: raise StopRun('BLOCKED/NOT TESTABLE — SOURCE OR EVIDENCE IDENTITY','director verifier failed')
    def evaluate(self,stage:str,params:dict[str,Any])->dict[str,Any]:
        key=json.dumps(params,sort_keys=True,separators=(',',':'))
        cachekey=stage+'|'+key
        if cachekey in self.cache:return self.cache[cachekey]
        if self.launches>=int(self.registry['absolute_candidate_engine_launch_cap']):raise StopRun('NO_PRESENTATION_ONLY_INTERVAL','candidate engine launch cap reached')
        self.index+=1; cid=candidate_id(stage,self.index,params); cdir=self.evidence/'CANDIDATES'/cid; project=self.work/cid
        copy_project(self.root,project); patched=patch_builder(self.baseline,params,self.registry); write(project/'scripts/p1a_world_builder.gd',patched)
        cmd=[self.godot,'--log-file',str(cdir/'engine.txt'),'--path',str(project),'--fixed-fps','60','--script',PROBE,'--','--output-dir',str(cdir)]
        cdir.mkdir(parents=True,exist_ok=True);dump(cdir/'argv.json',{'argv':cmd,'cwd':str(project)}); p=run(cmd,project); self.launches+=1;write(cdir/'stdout.txt',p.stdout);write(cdir/'stderr.txt',p.stderr)
        probe={}
        if (cdir/'probe_result.json').is_file():
            try:probe=json.loads((cdir/'probe_result.json').read_text())
            except Exception:pass
        images={'free_roam_on':'free-roam-after-native.png','free_roam_off':'free-roam-after-shadow-off-reference.png','a1_on':'a1-after-native.png','a1_off':'a1-after-shadow-off-reference.png'}
        paths={
          'FREE_ROAM:on':cdir/images['free_roam_on'],'FREE_ROAM:off':cdir/images['free_roam_off'],
          'A1_FAMILIARIZATION:on':cdir/images['a1_on'],'A1_FAMILIARIZATION:off':cdir/images['a1_off']}
        metrics={}
        if all(x.is_file() for x in paths.values()):
            try:metrics=compute_metrics(self.acceptance,paths);dump(cdir/'native-visual-metric-result.json',metrics)
            except Exception as e:metrics={'status':'FAIL','error':str(e)}
        image_records={name:{'path':fn,'sha256':sha(cdir/fn) if (cdir/fn).is_file() else None} for name,fn in images.items()}
        record={'candidate_id':cid,'stage':stage,'parameters':params,'engine_identity':EXACT,'command':cmd,'returncode':p.returncode,'project_material_source_sha256':sha(project/'scripts/p1a_world_builder.gd'),'images':image_records,'metrics':metrics,'ray_result':probe.get('ray_result',{}),'stdout_sha256':sha(cdir/'stdout.txt'),'stderr_sha256':sha(cdir/'stderr.txt'),'evaluated_utc':dt.datetime.now(dt.timezone.utc).isoformat()}
        record['evidence_complete']=evidence_complete(record);record['status']='PASS' if record['evidence_complete'] and p.returncode in (0,1) and metrics else 'BLOCKED/NOT TESTABLE';dump(cdir/'candidate_record.json',record)
        shutil.rmtree(project,ignore_errors=True);self.cache[cachekey]=record;self.records.append(record);return record
    def params(self,outer_scale=1.0,outer_em=0.0,wall_scale=1.0,wall_em=0.0):return {'OUTER_CLOSURE_MASK':{'albedo_scale':outer_scale,'emission_multiplier':outer_em},'CORE_WALL':{'albedo_scale':wall_scale,'emission_multiplier':wall_em}}
    def search_albedo(self,material:str)->dict[str,Any]|None:
        cfg=self.registry['outer_closure' if material=='OUTER_CLOSURE_MASK' else 'core_wall']; lo,hi=map(float,cfg['albedo_scale_domain']); q=float(cfg['albedo_scale_quantum']); target=float(cfg['balanced_target_Y'] if material=='OUTER_CLOSURE_MASK' else cfg['bisection_target_separation_Y']); maxeval=int(cfg['max_albedo_evaluations']); stage='OUTER_ALBEDO' if material=='OUTER_CLOSURE_MASK' else 'WALL_ALBEDO'; recs=[]
        def ev(s):
            s=quantize(min(hi,max(lo,s)),q); p=self.params(outer_scale=s) if material=='OUTER_CLOSURE_MASK' else self.params(wall_scale=s); r=self.evaluate(stage,p); recs.append(r); return r
        rlo=ev(lo); rhi=ev(hi)
        if not rlo.get('metrics') or not rhi.get('metrics'):return None
        vlo,vhi=target_value(rlo,material),target_value(rhi,material)
        if vhi<vlo:raise StopRun('NO_PRESENTATION_ONLY_INTERVAL',f'{material} albedo response non-monotonic at bracket')
        while len({r['candidate_id'] for r in recs})<maxeval:
            mid=quantize((lo+hi)/2,q)
            if mid in {quantize(lo,q),quantize(hi,q)}:break
            r=ev(mid); v=target_value(r,material)
            if v<target:lo=mid
            else:hi=mid
        passes=[r for r in recs if local_pass(r,material,self.registry)]
        if not passes:return None
        if material=='OUTER_CLOSURE_MASK':
            center=self.registry['outer_closure']['balanced_target_Y']; return sorted(passes,key=lambda r:(abs(target_value(r,material)-center),presentation_delta(r['parameters'],self.registry),r['candidate_id']))[0]
        robust=[r for r in passes if target_value(r,material)>=target]; pool=robust or passes; return sorted(pool,key=lambda r:(presentation_delta(r['parameters'],self.registry),-target_value(r,material),r['candidate_id']))[0]
    def search_fallback(self,material:str)->dict[str,Any]|None:
        # Single preregistered family: retain the best sub-target albedo candidate, then add low local emission.
        prior=[r for r in self.records if r['stage']==('OUTER_ALBEDO' if material=='OUTER_CLOSURE_MASK' else 'WALL_ALBEDO') and r.get('metrics')]
        if not prior:return None
        target=float(self.registry['outer_closure']['balanced_target_Y'] if material=='OUTER_CLOSURE_MASK' else self.registry['core_wall']['bisection_target_separation_Y'])
        below=[r for r in prior if target_value(r,material)<=target]; anchor=max(below,key=lambda r:target_value(r,material)) if below else min(prior,key=lambda r:target_value(r,material)); scale=float(anchor['parameters'][material]['albedo_scale'])
        f=self.registry['fallback']; lo,hi=map(float,f['emission_multiplier_domain']);q=float(f['emission_multiplier_quantum']);maxeval=int(f['max_evaluations_per_material']);stage='OUTER_EMISSION_FALLBACK' if material=='OUTER_CLOSURE_MASK' else 'WALL_EMISSION_FALLBACK';recs=[]
        def ev(e):
            e=quantize(min(hi,max(lo,e)),q); p=self.params(outer_scale=scale,outer_em=e) if material=='OUTER_CLOSURE_MASK' else self.params(wall_scale=scale,wall_em=e);r=self.evaluate(stage,p);recs.append(r);return r
        rlo=ev(lo);rhi=ev(hi)
        if target_value(rhi,material)<target_value(rlo,material):raise StopRun('NO_PRESENTATION_ONLY_INTERVAL',f'{material} emission response non-monotonic')
        while len({r['candidate_id'] for r in recs})<maxeval:
            mid=quantize((lo+hi)/2,q)
            if mid in {quantize(lo,q),quantize(hi,q)}:break
            r=ev(mid)
            if target_value(r,material)<target:lo=mid
            else:hi=mid
        passes=[r for r in recs if local_pass(r,material,self.registry)]
        if not passes:return None
        if material=='OUTER_CLOSURE_MASK':
            center=self.registry['outer_closure']['balanced_target_Y'];return sorted(passes,key=lambda r:(abs(target_value(r,material)-center),presentation_delta(r['parameters'],self.registry),r['candidate_id']))[0]
        robust=[r for r in passes if target_value(r,material)>=target];return sorted(robust or passes,key=lambda r:(presentation_delta(r['parameters'],self.registry),-target_value(r,material),r['candidate_id']))[0]
    def combined(self,outer:dict[str,Any],wall:dict[str,Any])->dict[str,Any]:
        base={'OUTER_CLOSURE_MASK':dict(outer['parameters']['OUTER_CLOSURE_MASK']),'CORE_WALL':dict(wall['parameters']['CORE_WALL'])}; variants=[]; offsets=self.registry['combined_validation']['guard_offsets_quanta']
        for oo in offsets:
            for wo in offsets:
                p=json.loads(json.dumps(base))
                for material,off in [('OUTER_CLOSURE_MASK',oo),('CORE_WALL',wo)]:
                    if p[material]['emission_multiplier']>0:
                        q=float(self.registry['fallback']['emission_multiplier_quantum']);lo,hi=self.registry['fallback']['emission_multiplier_domain'];p[material]['emission_multiplier']=quantize(min(hi,max(lo,p[material]['emission_multiplier']+off*q)),q)
                    else:
                        cfg=self.registry['outer_closure' if material=='OUTER_CLOSURE_MASK' else 'core_wall'];q=float(cfg['albedo_scale_quantum']);lo,hi=cfg['albedo_scale_domain'];p[material]['albedo_scale']=quantize(min(hi,max(lo,p[material]['albedo_scale']+off*q)),q)
                variants.append(p)
        uniq=[];seen=set()
        for p in variants:
            k=json.dumps(p,sort_keys=True)
            if k not in seen:seen.add(k);uniq.append(p)
        if len(uniq)>int(self.registry['combined_validation']['maximum_grid_evaluations']):raise StopRun('NO_PRESENTATION_ONLY_INTERVAL','combined grid exceeds preregistered cap')
        records=[self.evaluate('COMBINED',p) for p in uniq]; selected=select_combined(records,self.registry)
        if selected is None:raise StopRun('NO_PRESENTATION_ONLY_INTERVAL','no combined candidate passed all 21 visuals and 14 rays')
        return selected
    def materialize(self,selected):
        write(self.root/'scripts/p1a_world_builder.gd',patch_builder(self.baseline,selected['parameters'],self.registry))
        record={'schema':'district_zero.p1a.v1_2_7.selected_presentation.v1','status':'PASS','selected_candidate_id':selected['candidate_id'],'parameters':selected['parameters'],'selection_rule':self.registry['selection_rule'],'presentation_delta':presentation_delta(selected['parameters'],self.registry),'selected_metrics':selected['metrics'],'selected_ray_result':selected['ray_result'],'source_material_file_sha256':sha(self.root/'scripts/p1a_world_builder.gd')}
        dump(self.root/'presentation/p1a_v1_2_7_selected_presentation.json',record)
        write(self.root/'STATUS.md',f'''# District Zero P1A status — v1.2.7 calibration selected\n\n**Outcome:** `CALIBRATION SELECTED — FINAL VERIFICATION REQUIRED`\n\nSelected candidate: `{selected['candidate_id']}`. Literal material values are materialized. Human attempts consumed: `0`. Human World Gate: `NOT PERFORMED`. P1B: `FROZEN`.\n''')
        write_inventory(self.root)
    def final_probe(self):
        d=self.evidence/'FINAL_NATIVE_VISUALS'; d.mkdir(parents=True,exist_ok=True);cmd=[self.godot,'--log-file',str(d/'engine.txt'),'--path',str(self.root),'--fixed-fps','60','--script',PROBE,'--','--output-dir',str(d)];dump(d/'argv.json',{'argv':cmd,'cwd':str(self.root)});p=run(cmd,self.root);write(d/'stdout.txt',p.stdout);write(d/'stderr.txt',p.stderr)
        pr=json.loads((d/'probe_result.json').read_text()) if (d/'probe_result.json').is_file() else {};paths={'FREE_ROAM:on':d/'free-roam-after-native.png','FREE_ROAM:off':d/'free-roam-after-shadow-off-reference.png','A1_FAMILIARIZATION:on':d/'a1-after-native.png','A1_FAMILIARIZATION:off':d/'a1-after-shadow-off-reference.png'}
        if not all(x.is_file() for x in paths.values()):raise StopRun('BLOCKED/NOT TESTABLE — FINAL NATIVE VISUALS','final images incomplete')
        metrics=compute_metrics(self.acceptance,paths);dump(d/'native-visual-metric-result.json',metrics)
        if p.returncode!=0 or metrics['status']!='PASS' or pr.get('ray_result',{}).get('status')!='PASS' or pr.get('ray_result',{}).get('sample_count')!=14:raise StopRun('BLOCKED/NOT TESTABLE — FINAL NATIVE VISUALS','final visuals/rays failed')
    def final_verifiers(self):
        write_inventory(self.root);cmd=[sys.executable,'-B',str(self.root/'tools/verify_v1_2_7_successor.py'),'--root',str(self.root),'--phase','final'];p=run(cmd,self.root);write(self.evidence/'FINAL_STATIC_VERIFIER.stdout.txt',p.stdout);write(self.evidence/'FINAL_STATIC_VERIFIER.stderr.txt',p.stderr);dump(self.evidence/'FINAL_STATIC_VERIFIER.argv.json',{'argv':cmd,'cwd':str(self.root)})
        if p.returncode!=0:raise StopRun('BLOCKED/NOT TESTABLE — PRESERVATION','final static/preservation verifier failed')
        cdir=self.evidence/'C1';cmd=[sys.executable,'-B',str(self.root/'tools/run_v1_2_7_c1.py'),'--root',str(self.root),'--godot',self.godot,'--evidence-dir',str(cdir),'--work-root',str(self.work/'final-c1')];p=run(cmd,self.root);write(self.evidence/'C1_WRAPPER.stdout.txt',p.stdout);write(self.evidence/'C1_WRAPPER.stderr.txt',p.stderr);dump(self.evidence/'C1_WRAPPER.argv.json',{'argv':cmd,'cwd':str(self.root)})
        result=json.loads((cdir/'C1_result.json').read_text()) if (cdir/'C1_result.json').is_file() else {}
        if p.returncode!=0 or result.get('status')!='PASS' or result.get('ticks_compared')!=1260 or float(result.get('maximum_absolute_difference',1))!=0.0:raise StopRun('BLOCKED/NOT TESTABLE — C1','C1 final comparison failed')
    def smoke(self):
        smoke_session=self.work/'launcher-smoke-session';smoke_session.mkdir(parents=True,exist_ok=True);d=self.evidence/'LAUNCHER_SMOKE_75S';cmd=[sys.executable,'-B',str(self.root/'tools/run_v1_2_6_launcher_smoke.py'),'--godot',self.godot,'--project-root',str(self.root),'--session-root',str(smoke_session),'--output-dir',str(d),'--session-id','v1.2.7-final-smoke','--minimum-wall-duration-s','75'];dump(d/'wrapper_argv.json',{'argv':cmd,'cwd':str(self.root)});p=run(cmd,self.root);write(d/'wrapper_stdout.txt',p.stdout);write(d/'wrapper_stderr.txt',p.stderr);r=json.loads((d/'smoke_result.json').read_text()) if (d/'smoke_result.json').is_file() else {}
        if p.returncode!=0 or r.get('status')!='PASS' or r.get('attempts_consumed')!=0:raise StopRun('BLOCKED/NOT TESTABLE — LAUNCHER SMOKE','75-second launcher smoke failed')
    def prepare_session(self):
        cmd=[sys.executable,'-B',str(self.root/'tools/prepare_v1_2_7_a1_session.py'),'--root',str(self.root),'--godot',self.godot,'--session-root',str(self.session)];p=run(cmd,self.root);write(self.evidence/'PREPARE_SESSION.stdout.txt',p.stdout);write(self.evidence/'PREPARE_SESSION.stderr.txt',p.stderr);dump(self.evidence/'PREPARE_SESSION.argv.json',{'argv':cmd,'cwd':str(self.root)})
        if p.returncode!=0:raise StopRun('BLOCKED/NOT TESTABLE — PREPARED SESSION','prepared session creation failed')
    def packages(self):
        write(self.root/'STATUS.md','# District Zero P1A status — v1.2.7 final preparation\n\n**Outcome:** `READY FOR A1 HUMAN FEASIBILITY CAPTURE`\n\nAll bounded calibration and final prerequisites passed under the exact engine; the prepared A1 session has been created. Human attempts consumed: `0`. Human World Gate: `NOT PERFORMED`. P1B: `FROZEN`.\n')
        write_inventory(self.root)
        dump(self.evidence/'TERMINAL_RESULT.json',{'schema':'district_zero.p1a.v1_2_7.calibration_terminal_result.v1','status':'READY FOR A1 HUMAN FEASIBILITY CAPTURE','candidate_engine_launches':self.launches,'selected_presentation':json.loads((self.root/'presentation/p1a_v1_2_7_selected_presentation.json').read_text()),'human_attempts_consumed':0,'human_world_gate':'NOT PERFORMED','P1B':'FROZEN'})
        # Evidence inventory before packaging.
        inv=self.evidence/'SHA256SUMS.txt';files=sorted((p for p in self.evidence.rglob('*') if p.is_file() and p!=inv),key=lambda p:p.relative_to(self.evidence).as_posix().encode());write(inv,''.join(f'{sha(p)}  {p.relative_to(self.evidence).as_posix()}\n' for p in files))
        parent=self.evidence.parent;reports={
          'implemented_source':deterministic_zip(self.root,parent/'District-Zero-P1A-v1.2.7-Implemented-Source.zip'),
          'validation_evidence':deterministic_zip(self.evidence,parent/'District-Zero-P1A-v1.2.7-Calibration-Validation-Evidence.zip'),
          'prepared_session':deterministic_zip(self.session,parent/'District-Zero-P1A-v1.2.7-Prepared-A1-Human-Session.zip')}
        dump(parent/'District-Zero-P1A-v1.2.7-PACKAGE-REPORT.json',reports);return reports
    def execute(self):
        self.preflight();outer=self.search_albedo('OUTER_CLOSURE_MASK') or self.search_fallback('OUTER_CLOSURE_MASK');
        if outer is None:raise StopRun('NO_PRESENTATION_ONLY_INTERVAL','outer closure has no authorized robust interval')
        wall=self.search_albedo('CORE_WALL') or self.search_fallback('CORE_WALL');
        if wall is None:raise StopRun('NO_PRESENTATION_ONLY_INTERVAL','core wall has no authorized robust interval')
        selected=self.combined(outer,wall);self.materialize(selected);self.final_probe();self.final_verifiers();self.smoke();self.prepare_session();return self.packages()

def main()->int:
    ap=argparse.ArgumentParser(description='District Zero P1A v1.2.7 bounded exact-engine presentation calibration')
    ap.add_argument('--root',default=str(ROOT_DEFAULT));ap.add_argument('--godot',required=True);ap.add_argument('--work-root',required=True);ap.add_argument('--evidence-root',required=True);ap.add_argument('--prepared-session-root',required=True);a=ap.parse_args();d=Director(a)
    try:
        reports=d.execute();print(json.dumps({'status':'READY FOR A1 HUMAN FEASIBILITY CAPTURE','candidate_engine_launches':d.launches,'packages':reports},indent=2,sort_keys=True));return 0
    except StopRun as e:
        d.evidence.mkdir(parents=True,exist_ok=True);dump(d.evidence/'TERMINAL_RESULT.json',{'schema':'district_zero.p1a.v1_2_7.calibration_terminal_result.v1','status':e.status,'detail':e.detail,'candidate_engine_launches':d.launches,'human_attempts_consumed':0,'human_world_gate':'NOT PERFORMED','P1B':'FROZEN'});print(json.dumps({'status':e.status,'detail':e.detail,'candidate_engine_launches':d.launches},sort_keys=True));return 2
    except Exception as e:
        d.evidence.mkdir(parents=True,exist_ok=True);dump(d.evidence/'TERMINAL_RESULT.json',{'schema':'district_zero.p1a.v1_2_7.calibration_terminal_result.v1','status':'BLOCKED/NOT TESTABLE — HARNESS','detail':str(e),'candidate_engine_launches':d.launches,'human_attempts_consumed':0,'human_world_gate':'NOT PERFORMED','P1B':'FROZEN'});print(json.dumps({'status':'BLOCKED/NOT TESTABLE — HARNESS','detail':str(e)},sort_keys=True));return 2
if __name__=='__main__':raise SystemExit(main())
