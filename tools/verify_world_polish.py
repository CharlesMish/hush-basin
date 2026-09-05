#!/usr/bin/env python3
"""Verify successor geometry and preserved R7/Run v0 mechanics, offline."""
import collections
import hashlib
import json
import math
from pathlib import Path
import struct
import sys
import tempfile
from generate_world_polish import contains, bounds, digest, generate, read

ROOT=Path(__file__).resolve().parents[1];GAME=ROOT/'game'
MODIFIED={'AGENTS.md','STATUS.md','project.godot','scripts/p1a_world_data.gd','scripts/p1a_world_builder.gd','scripts/p1a_world_gate.gd','scripts/p1a_telemetry.gd','scripts/p1a_map.gd'}

def main():
    failures=[];checks=[]
    def check(name,passed,detail=None):
        checks.append({'id':name,'pass':bool(passed),'detail':detail})
        if not passed:failures.append(name)
    baseline=read(ROOT/'docs/world_polish_baseline.json')
    # Warm Overcast authority permits only the Run map projection repair.
    for name,sha in baseline['run_files'].items():
        if name != 'game/scripts/run/run_map_overlay.gd':check('RUN_V0_PRESERVED:'+name,digest(ROOT/name)==sha)
    inventory=ROOT/'QUIET_SURFACES_V1_SHA256SUMS.txt'
    if inventory.exists():
        for row in inventory.read_text().splitlines():
            sha,name=row.split('  ',1)
            check('PACKAGE:'+name,(ROOT/name).is_file() and digest(ROOT/name)==sha)
    for row in (GAME/'VEHICLE_R7_SHA256SUMS.txt').read_text().splitlines():
        expected,name=row.split('  ',1)
        if name not in MODIFIED:check('PRESERVED:'+name,digest(GAME/name)==expected)
    cfg=read(GAME/'world/world_polish_v1.json');out=GAME/'world/generated'
    overlay=read(out/'world_polish_v1.json');idx=read(out/'world_polish_v1_index.json')
    check('CONFIG_IDENTITY',idx['config_sha256']==digest(GAME/'world/world_polish_v1.json'))
    for name,sha in idx['artifacts'].items():check('GENERATED_IDENTITY:'+name,digest(out/name)==sha)
    if '--regenerate' in sys.argv:
        with tempfile.TemporaryDirectory(prefix='world-polish-repro-') as temp:
            generate(Path(temp))
            for p in Path(temp).iterdir():check('REPRODUCIBLE:'+p.name,digest(p)==digest(out/p.name))
    original=read(out/'solid_meshes.json')['meshes'];combined={**original,**overlay['meshes']}
    bins=collections.defaultdict(list)
    for mid,mesh in combined.items():
        vertices=mesh['vertices_xyz_m'];polys=[]
        for tri in mesh['triangles']:
            if tri['surface']!='TOP':continue
            p=[(vertices[i][0],vertices[i][2]) for i in tri['indices']]
            if sum(p[i][0]*p[(i+1)%3][1]-p[(i+1)%3][0]*p[i][1] for i in range(3))<0:p.reverse()
            if abs(sum(p[i][0]*p[(i+1)%3][1]-p[(i+1)%3][0]*p[i][1] for i in range(3)))<1e-7:continue
            x0,z0,x1,z1=bounds(p)
            for x in range(math.floor(x0/10),math.floor(x1/10)+1):
                for z in range(math.floor(z0/10),math.floor(z1/10)+1):bins[x,z].append((mid,p))
        if mid in overlay['meshes']:
            r=overlay['render_meshes'][mid]
            match=True
            for j,tri in enumerate(mesh['triangles']):
                for k,i in enumerate(tri['indices']):
                    v=r['render_positions_xyz_m'][r['render_indices'][j*3+k]]
                    if v!=vertices[i]:match=False
            check('VISUAL_COLLISION_TRIANGLES:'+mid,match)
            check('FINITE_NORMALS:'+mid,all(abs(sum(v*v for v in n)-1)<1e-6 for n in r['render_normals_xyz']))
    def obstacle(x,z):
        return next((mid for mid,p in bins[math.floor(x/10),math.floor(z/10)] if contains(p,x,z)),None)
    for yard in cfg['yards']:
        cx,cz=yard['clear_square_center'];bad=[]
        for ix in range(-20,21,2):
            for iz in range(-20,21,2):
                x,z=cx+ix,cz+iz;hit=obstacle(x,z)
                if hit or not contains(yard['polygon'],x,z):bad.append([x,z,hit])
        check('40M_CLEAR_SQUARE:'+yard['id'],not bad,bad[:5])
        for i,(a,b) in enumerate(yard['entrances']):
            dx,dz=b[0]-a[0],b[1]-a[1];length=math.hypot(dx,dz);bad=[]
            for j in range(math.ceil(length)+1):
                t=min(1,j/length)
                for off in range(-12,13,2):
                    x=a[0]+t*dx-off*dz/length;z=a[1]+t*dz+off*dx/length
                    hit=obstacle(x,z)
                    if hit:bad.append([round(x,2),round(z,2),hit])
            check('24M_CLEAR_ENTRANCE:'+yard['id']+':'+str(i),not bad,bad[:5])
    old_h=(out/'heightfield_i16le.bin').read_bytes();new_h=(out/'world_polish_v1_height.bin').read_bytes()
    old_s=(out/'surface_classes_u8.bin').read_bytes();new_s=(out/'world_polish_v1_surface.bin').read_bytes()
    check('TERRAIN_LENGTH',len(old_h)==len(new_h) and len(old_s)==len(new_s))
    protected=[j for j,v in enumerate(old_s) if v in (2,3,4,5,8,9,10)]
    check('ROADBEDS_JUNCTIONS_PADS_EXACT',all(old_h[2*j:2*j+2]==new_h[2*j:2*j+2] and old_s[j]==new_s[j] for j in protected),len(protected))
    meta=read(out/'terrain_metadata.json');g=meta['grid'];w=g['vertex_count_x'];d=g['vertex_count_z']
    check('SOUTH_FIXTURE_SUPPORT_EXACT',all(old_h[2*j:2*j+2]==new_h[2*j:2*j+2] and old_s[j]==new_s[j] for j in range(w*d) if g['origin_xz_m'][1]+(j//w)*g['spacing_m']>=123))
    check('OUTER_WALL_UNCHANGED','MESH_OUTER_WALL' not in overlay['meshes'])
    check('HOP_UNCHANGED',all(m['source_geometry_id']!='HOP_BAR_01' for m in overlay['meshes'].values()))
    # Protected building and landmark centers still sit on their original solid.
    check('FOUNDATIONS_PRESENT',all(obstacle(sum(v[0] for v in p['polygon'])/4,sum(v[1] for v in p['polygon'])/4) for p in overlay['protection']))
    result={'status':'PASS' if not failures else 'FAIL','checks':checks,'check_count':len(checks),'failures':failures}
    if '--result' in sys.argv:Path(sys.argv[sys.argv.index('--result')+1]).write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='checks'},indent=2))
    for c in checks:
        if not c['pass']:print(c)
    return bool(failures)

if __name__=='__main__':sys.exit(main())
