#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, pathlib, statistics, struct, zlib
from typing import Any


def _read_png_rgb8(path: pathlib.Path) -> tuple[int,int,list[bytes]]:
    b=path.read_bytes()
    if b[:8] != b'\x89PNG\r\n\x1a\n': raise ValueError(f'{path}: not PNG')
    pos=8; chunks=[]; width=height=None
    while pos < len(b):
        n=struct.unpack('>I',b[pos:pos+4])[0]; typ=b[pos+4:pos+8]; data=b[pos+8:pos+8+n]; pos += 12+n
        if typ == b'IHDR':
            width,height,depth,color_type,compression,filter_method,interlace=struct.unpack('>IIBBBBB',data)
            if (depth,color_type,compression,filter_method,interlace)!=(8,2,0,0,0):
                raise ValueError(f'{path}: expected noninterlaced RGB8 PNG')
        elif typ == b'IDAT': chunks.append(data)
        elif typ == b'IEND': break
    if width is None: raise ValueError(f'{path}: IHDR absent')
    raw=zlib.decompress(b''.join(chunks)); bpp=3; stride=width*bpp; rows=[]; prev=bytearray(stride); off=0
    for _ in range(height):
        ft=raw[off]; off+=1; scan=bytearray(raw[off:off+stride]); off+=stride
        for x in range(stride):
            a=scan[x-bpp] if x>=bpp else 0; b0=prev[x]; c=prev[x-bpp] if x>=bpp else 0
            if ft==0: pass
            elif ft==1: scan[x]=(scan[x]+a)&255
            elif ft==2: scan[x]=(scan[x]+b0)&255
            elif ft==3: scan[x]=(scan[x]+((a+b0)//2))&255
            elif ft==4:
                p=a+b0-c; pa=abs(p-a); pb=abs(p-b0); pc=abs(p-c)
                pr=a if pa<=pb and pa<=pc else b0 if pb<=pc else c
                scan[x]=(scan[x]+pr)&255
            else: raise ValueError(f'{path}: unsupported PNG filter {ft}')
        rows.append(bytes(scan)); prev=scan
    return width,height,rows


def _linear(c:int)->float:
    v=c/255.0
    return v/12.92 if v<=0.04045 else ((v+0.055)/1.055)**2.4


def patch_y(path:pathlib.Path, normalized_xy:list[float]) -> float:
    width,height,rows=_read_png_rgb8(path)
    cx=min(width-1,max(0,int(float(normalized_xy[0])*width)))
    cy=min(height-1,max(0,int(float(normalized_xy[1])*height)))
    values=[]
    for y in range(max(0,cy-4),min(height,cy+5)):
        row=rows[y]
        for x in range(max(0,cx-4),min(width,cx+5)):
            i=x*3; r,g,b=row[i],row[i+1],row[i+2]
            values.append(0.2126*_linear(r)+0.7152*_linear(g)+0.0722*_linear(b))
    if len(values)!=81: raise ValueError(f'{path}: sample patch clipped at {normalized_xy}')
    return statistics.median(values)


def compute(acceptance:dict[str,Any], images:dict[str,pathlib.Path]) -> dict[str,Any]:
    samples=acceptance['samples']; t=acceptance['hard_thresholds']; views={}
    for view in ('FREE_ROAM','A1_FAMILIARIZATION'):
        on=images[f'{view}:on']; off=images[f'{view}:off']; rec={}
        for name,xy in samples[view].items():
            on_y=patch_y(on,xy); off_y=patch_y(off,xy); ratio=on_y/off_y if off_y>0 else float('inf')
            rec[name]={'shadow_on_Y':on_y,'shadow_off_Y':off_y,'on_to_off_ratio':ratio}
        views[view]=rec
    checks=[]
    def add(cid,observed,passed): checks.append({'id':cid,'observed':observed,'pass':bool(passed)})
    fr=views['FREE_ROAM']; bg=fr['background']['shadow_on_Y']
    for name in ('aperture_ground','left_ground','right_ground'):
        diff=fr[name]['shadow_on_Y']-bg; fr[name]['minus_background_Y']=diff
        add(f'FREE_ROAM:{name}:minus_background',diff,diff>=t['each_ground_minus_same_view_background_Y_min'])
    for name in ('aperture_ground','left_ground','right_ground'):
        add(f'FREE_ROAM:{name}:shadow_on_min',fr[name]['shadow_on_Y'],fr[name]['shadow_on_Y']>=t['shadow_on_Y_min'])
        add(f'FREE_ROAM:{name}:shadow_ratio',fr[name]['on_to_off_ratio'],fr[name]['on_to_off_ratio']>=t['shadow_on_to_shadow_off_Y_ratio_min'])
    a1=views['A1_FAMILIARIZATION']; bg=a1['background']['shadow_on_Y']
    for name in ('between_structures_ground','right_ground'):
        diff=a1[name]['shadow_on_Y']-bg; a1[name]['minus_background_Y']=diff
        add(f'A1_FAMILIARIZATION:{name}:minus_background',diff,diff>=t['each_ground_minus_same_view_background_Y_min'])
    for name in ('between_structures_ground','left_outer_closure','right_core_wall','right_ground'):
        add(f'A1_FAMILIARIZATION:{name}:shadow_on_min',a1[name]['shadow_on_Y'],a1[name]['shadow_on_Y']>=t['shadow_on_Y_min'])
        add(f'A1_FAMILIARIZATION:{name}:shadow_ratio',a1[name]['on_to_off_ratio'],a1[name]['on_to_off_ratio']>=t['shadow_on_to_shadow_off_Y_ratio_min'])
    left=abs(a1['between_structures_ground']['shadow_on_Y']-a1['left_outer_closure']['shadow_on_Y'])
    right=abs(a1['right_core_wall']['shadow_on_Y']-a1['right_ground']['shadow_on_Y'])
    a1['obstacle_separation']={'left_absolute_Y':left,'right_absolute_Y':right}
    add('A1:left_obstacle_separation',left,left>=t['left_outer_closure_minus_adjacent_ground_absolute_Y_min'])
    add('A1:right_obstacle_separation',right,right>=t['right_core_wall_minus_adjacent_ground_absolute_Y_min'])
    return {'schema':'district_zero.p1a.v1_2_7.native_visual_metric_result.v1','status':'PASS' if all(c['pass'] for c in checks) else 'FAIL','checks':checks,'views':views}


def main()->int:
    ap=argparse.ArgumentParser(); ap.add_argument('--acceptance',required=True); ap.add_argument('--image-dir',required=True); ap.add_argument('--output')
    a=ap.parse_args(); acc=json.loads(pathlib.Path(a.acceptance).read_text()); d=pathlib.Path(a.image_dir)
    images={
      'FREE_ROAM:on':d/'free-roam-after-native.png','FREE_ROAM:off':d/'free-roam-after-shadow-off-reference.png',
      'A1_FAMILIARIZATION:on':d/'a1-after-native.png','A1_FAMILIARIZATION:off':d/'a1-after-shadow-off-reference.png'}
    result=compute(acc,images); text=json.dumps(result,indent=2,sort_keys=True)+'\n'
    if a.output: pathlib.Path(a.output).write_text(text)
    print(text,end=''); return 0 if result['status']=='PASS' else 1
if __name__=='__main__': raise SystemExit(main())
