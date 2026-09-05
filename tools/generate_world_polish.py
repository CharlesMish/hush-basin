#!/usr/bin/env python3
"""Deterministic World Polish v1 overlay. Python standard library only.

The original source triangles are the geometric input. Convex half-plane
clipping subtracts authored yards, except protected foundations. Remaining
top polygons drive closed visual faces and exact triangular collision prisms.
No baseline generated file is overwritten.
"""
from pathlib import Path
import argparse
import hashlib
import json
import math
import struct

ROOT = Path(__file__).resolve().parents[1]
GAME = ROOT / 'game'
EPS = 1e-8

def read(p):
    return json.loads(p.read_text())

def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def area(p):
    return sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(p,p[1:]+p[:1]))/2

def cross(a,b,p):
    return (b[0]-a[0])*(p[1]-a[1])-(b[1]-a[1])*(p[0]-a[0])

def clean(p):
    q=[]
    for v in p:
        v=(round(v[0],7),round(v[1],7))
        if not q or math.dist(q[-1],v)>EPS:q.append(v)
    if len(q)>1 and math.dist(q[0],q[-1])<EPS:q.pop()
    return q if len(q)>=3 and abs(area(q))>1e-8 else []

def half(p,a,b,inside=True):
    result=[]
    for u,v in zip(p,p[1:]+p[:1]):
        du,dv=cross(a,b,u),cross(a,b,v)
        iu=du>=-EPS if inside else du<=EPS
        iv=dv>=-EPS if inside else dv<=EPS
        if iu:result.append(u)
        if iu!=iv and abs(du-dv)>EPS:
            t=du/(du-dv);result.append((u[0]+t*(v[0]-u[0]),u[1]+t*(v[1]-u[1])))
    return clean(result)

def bounds(p):
    return min(v[0] for v in p),min(v[1] for v in p),max(v[0] for v in p),max(v[1] for v in p)

def overlap(a,b):
    return not (a[2]<b[0] or b[2]<a[0] or a[3]<b[1] or b[3]<a[1])

def subtract(p,cut):
    if not overlap(bounds(p),bounds(cut)):return [p]
    rest=p;outside=[]
    for a,b in zip(cut,cut[1:]+cut[:1]):
        piece=half(rest,a,b,False)
        if piece:outside.append(piece)
        rest=half(rest,a,b)
        if not rest:break
    return outside

def contains(p,x,z):
    return all(cross(a,b,(x,z))>=-EPS for a,b in zip(p,p[1:]+p[:1]))

def distance_edge(p,x,z):
    result=math.inf
    for a,b in zip(p,p[1:]+p[:1]):
        dx,dz=b[0]-a[0],b[1]-a[1]
        t=max(0,min(1,((x-a[0])*dx+(z-a[1])*dz)/(dx*dx+dz*dz)))
        result=min(result,math.hypot(x-a[0]-t*dx,z-a[1]-t*dz))
    return result

def rectangle(x,z,w,d):
    return [(x-w/2,z-d/2),(x+w/2,z-d/2),(x+w/2,z+d/2),(x-w/2,z+d/2)]

def make_mesh(record,polygons):
    vertices=[];triangles=[];rv=[];rn=[];ri=[];boundary={}
    base=float(record['base_y_m']);top=max(v[1] for v in record['vertices_xyz_m'])
    def face(points,surface,normal):
        start=len(vertices);vertices.extend(points)
        for i in range(1,len(points)-1):
            ids=[start,start+i,start+i+1]
            triangles.append({'indices':ids,'surface':surface})
            for j in ids:
                ri.append(len(rv));rv.append(vertices[j]);rn.append(normal)
    for p in polygons:
        face([[x,top,z] for x,z in reversed(p)],'TOP',[0,1,0])
        face([[x,base,z] for x,z in p],'BOTTOM',[0,-1,0])
        for a,b in zip(p,p[1:]+p[:1]):
            # Opposite directed edges cancel internal top triangulation seams.
            key=(tuple(a),tuple(b));op=(tuple(b),tuple(a))
            if op in boundary:del boundary[op]
            else:boundary[key]=True
    edges=[]
    for a,b in sorted(boundary):
        dx,dz=b[0]-a[0],b[1]-a[1];length=math.hypot(dx,dz)
        if length<EPS:continue
        face([[a[0],base,a[1]],[a[0],top,a[1]],[b[0],top,b[1]],[b[0],base,b[1]]], 'SIDE',[dz/length,0,-dx/length])
        edges.append([list(a),list(b),top])
    result=dict(record,vertices_xyz_m=vertices,triangles=triangles)
    return result,{'render_positions_xyz_m':rv,'render_normals_xyz':rn,'render_indices':ri},edges

def generate(output):
    cfg=read(GAME/'world/world_polish_v1.json')
    manifest=read(GAME/'world/p1a_world_manifest.json')
    source=read(GAME/'world/generated/solid_meshes.json')['meshes']
    protection=[]
    for item in manifest['building_masses']+manifest['landmarks']:
        x,z=item['center_xz_m']; w,d=item.get('footprint_xz_m',[2*item.get('radius_m',2)]*2)
        margin=cfg['foundation_margin_m']
        protection.append({'id':item['id'],'polygon':rectangle(x,z,w+2*margin,d+2*margin)})
    cuts=[]
    for yard in cfg['yards']:
        p=clean(yard['polygon'])
        if area(p)<0:p.reverse()
        assert all(cross(p[i-1],p[i],p[(i+1)%len(p)])>=-EPS for i in range(len(p))), 'yard must be convex'
        yard['polygon']=p
        pieces=[p]
        for protect in protection:
            pieces=[q for part in pieces for q in subtract(part,protect['polygon'])]
        cuts.extend(pieces)
    cut_bounds=[bounds(p) for p in cuts]
    meshes={};renders={};edges=[];changed=[]
    for mid,record in sorted(source.items()):
        if record['source_geometry_id'] not in cfg['cut_solid_ids']:
            if record['source_geometry_id']=='OUTER_WALL':
                polys=[]
                for tri in record['triangles']:
                    if tri['surface']!='TOP':continue
                    p=clean([(record['vertices_xyz_m'][i][0],record['vertices_xyz_m'][i][2]) for i in tri['indices']])
                    if not p:continue
                    if area(p)<0:p.reverse()
                    polys.append(p)
                _,_,ee=make_mesh(record,polys)
                edges.extend([record['source_geometry_id'],*e] for e in ee)
            continue
        polys=[]
        for tri in record['triangles']:
            if tri['surface']!='TOP':continue
            p=clean([(record['vertices_xyz_m'][i][0],record['vertices_xyz_m'][i][2]) for i in tri['indices']])
            if not p:continue
            if area(p)<0:p.reverse()
            fragments=[p];pb=bounds(p)
            for cut,cb in zip(cuts,cut_bounds):
                if overlap(pb,cb):fragments=[q for f in fragments for q in subtract(f,cut)]
            polys.extend(fragments)
        meshes[mid],renders[mid],ee=make_mesh(record,polys)
        edges.extend([record['source_geometry_id'],*e] for e in ee)
        changed.append({'id':mid,'remaining_top_area_m2':sum(area(p) for p in polys),'top_polygons':len(polys)})
    # Preserve every roadbed, junction and pad sample. Shoulder/bank samples
    # inside opened yards may blend into the newly exposed ground.
    meta=read(GAME/'world/generated/terrain_metadata.json');g=meta['grid']
    w,d=g['vertex_count_x'],g['vertex_count_z'];s=g['spacing_m'];ox,oz=g['origin_xz_m']
    raw=(GAME/'world/generated/heightfield_i16le.bin').read_bytes()
    old=list(struct.unpack('<'+'h'*(len(raw)//2),raw));heights=[v/1000 for v in old]
    surfaces=bytearray((GAME/'world/generated/surface_classes_u8.bin').read_bytes())
    mutable=[];yard_samples=0
    for iz in range(d):
        for ix in range(w):
            j=iz*w+ix;x,z=ox+ix*s,oz+iz*s
            yd=next((y for y in cfg['yards'] if contains(y['polygon'],x,z)),None)
            if yd is None or any(contains(p['polygon'],x,z) for p in protection):continue
            yard_samples+=1
            if surfaces[j] in (0,1,6,7,11):
                if surfaces[j] in (0,1,11):surfaces[j]=12
                if 0<ix<w-1 and 0<iz<d-1:
                    blend=min(1,distance_edge(yd['polygon'],x,z)/cfg['terrain_blend_distance_m'])
                    mutable.append((j,blend))
    for _ in range(cfg['terrain_smoothing_passes']):
        nxt=heights.copy()
        for j,blend in mutable:
            avg=(heights[j-w]+heights[j+w]+heights[j-1]+heights[j+1])/4
            nxt[j]=heights[j]+(avg-heights[j])*.45*blend
        heights=nxt
    final=[int(math.copysign(math.floor(abs(v)*1000+.5),v)) for v in heights]
    output.mkdir(parents=True,exist_ok=True)
    payload={'version':cfg['version'],'meshes':meshes,'render_meshes':renders,'wall_edges':edges,'yards':cfg['yards'],'protection':protection,'geometry_changes':changed,'yard_samples':yard_samples}
    (output/'world_polish_v1.json').write_text(json.dumps(payload,separators=(',',':'),sort_keys=True)+'\n')
    (output/'world_polish_v1_height.bin').write_bytes(struct.pack('<'+'h'*len(final),*final))
    (output/'world_polish_v1_surface.bin').write_bytes(surfaces)
    index={'version':cfg['version'],'config_sha256':digest(GAME/'world/world_polish_v1.json'),'artifacts':{p.name:digest(p) for p in sorted(output.glob('world_polish_v1*')) if p.name!='world_polish_v1_index.json'}}
    (output/'world_polish_v1_index.json').write_text(json.dumps(index,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'status':'GENERATED','changes':changed,'yard_samples':yard_samples,'changed_height_samples':sum(a!=b for a,b in zip(old,final)),'index':index},indent=2))

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,default=GAME/'world/generated')
    generate(parser.parse_args().output)
