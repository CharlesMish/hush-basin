#!/usr/bin/env python3
"""Fixed native detail modules, anchored to unchanged occupied architecture.

No dependencies or random state. Config is the authoring surface; this compiler
writes plain, reviewable primitive definitions. No collision output is created.
"""
import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / 'game/presentation/world_identity_detail_v2.json'
OUTPUT = ROOT / 'game/presentation/generated/world_identity_detail_v2.json'


def generate():
    cfg = json.loads(CONFIG.read_text())
    old = json.loads((ROOT/'game/presentation/generated/neighborhood_v1.json').read_text())
    parts, labels = [], []
    for site in cfg['buildings'] + cfg['landmarks']:
        owner, district = site['owner'], site['district']
        mass = next(p for p in old['parts'] if p['owner'] == owner and p['role'] in ['upper_mass', 'landmark_mass'])
        x, y, z = mass['p']; w, h, d = mass['size']; top = y+h/2
        def box(dx, dy, dz, sx, sy, sz, color='steel', rz=0, rx=0, role='roof', kind='box'):
            parts.append(dict(owner=owner,district=district,p=[x+dx,top+dy,z+dz],size=[sx,sy,sz],
                              rotation=[rx,0,rz],color=color,role=role,kind=kind))
        def cylinder(dx,dy,dz,radius,height,color='steel',rx=0):
            box(dx,dy,dz,radius*2,height,radius*2,color,rx=rx,kind='cylinder')
        roof = site['roof']
        rw, rd = min(w-0.8,10), min(d-0.8,8)
        if roof == 'sawtooth':
            # Three small northlight hoods, not a replacement roof volume.
            for dx in [-rw*.3,0,rw*.3]:
                box(dx,.7,0,1.5,1.4,rd*.65,'frame')
                box(dx,1.46,0,1.8,.16,rd*.7,district,rz=-.16)
                box(dx-.765,.8,0,.06,.65,rd*.5,'relay')
        elif roof in ['ventbank','ducts']:
            for dx in [-rw*.26,rw*.26]:
                if roof == 'ducts':
                    cylinder(dx,.65,0,.52,rd*.7,'frame',math.pi/2)
                    box(dx,.16,0,1.25,.32,rd*.78)
                    cylinder(dx,1.05,-rd*.29,.55,1.5,'frame')
                    cylinder(dx,1.82,-rd*.29,.69,.16,district)
                else:
                    box(dx,.65,0,2,1.3,rd*.62,'frame')
                    for dz in [-.7,0,.7]:
                        box(dx,1.34,dz,1.65,.12,.3)
            box(0,.24,0,rw*.7,.18,.22,district)
        elif roof == 'aerial':
            box(0,1.7,0,.2,3.4,.2,'frame')
            for dy,sx in [(1.5,4.8),(2.7,6.3)]:
                box(0,dy,0,min(sx,rw),.16,.22,'frame')
                for dx in [-min(sx,rw)*.4,min(sx,rw)*.4]:
                    box(dx,dy+.3,0,.65,1.15,.25,'relay')
            box(1.2,.65,0,1,1.3,1.3,'frame')
        elif roof in ['screen','civic']:
            # Open-ended louver enclosure keeps a calm, horizontal skyline.
            for dx in [-rw*.35,rw*.35]:
                box(dx,1,0,.15,2,rd*.7,'cream')
            for dy in [.3,.8,1.3,1.8]:
                for dz in [-rd*.35,rd*.35]:
                    box(0,dy,dz,rw*.72,.22,.12,district)
            box(0,.55,0,rw*.45,1.1,rd*.36,'frame')
            if roof == 'civic':
                # Paired civic fins echo the existing original medical mark.
                for dx in [-1.3,1.3]:
                    box(dx,2.6,0,.45,3.4,.65,'clinic')
        elif roof == 'lantern':
            box(0,.55,0,rw*.7,1.1,rd*.48,'frame')
            box(0,1.15,0,rw*.78,.18,rd*.58,'market')
            for dx in [-rw*.25,0,rw*.25]:
                box(dx,.62,rd*.245,rw*.18,.6,.06,'cream')
                box(dx,.62,-rd*.245,rw*.18,.6,.06,'cream')
        elif roof in ['gantry','freight']:
            gh = 2.7 if roof == 'gantry' else 2.1
            for dz in [-rd*.36,rd*.36]:
                for dx in [-rw*.38,rw*.38]:
                    box(dx,gh*.5,dz,.24,gh,.24,'frame')
                box(0,gh,dz,rw*.84,.35,.34,district)
                box(0,gh*.61,dz,rw*.77,.14,.15,'frame',rz=.21)
            box(0,gh+.1,0,.28,.32,rd*.82,'frame')
            if roof == 'freight':
                box(0,gh-.6,0,.6,.8,.7,district)
        elif roof == 'relay':
            # Side-mounted panels keep the existing mast's principal height.
            for dy in [-8,-4]:
                for dx in [-2.7,2.7]:
                    box(dx,dy,0,.65,2.1,.42,'relay')
                    box(dx*.5,dy-.5,0,2.7,.14,.2,'frame')
            cylinder(0,1.1,0,.09,2.2,'frame')
        elif roof == 'stack':
            # A spare cap and external ladder-like service ribs, no new plume.
            cylinder(0,.28,0,2.12,.48,'frame')
            for dz in [-.38,.38]:
                box(2.24,-h*.32,dz,.10,h*.64,.10,'frame')
            for i in range(7):
                box(2.24,-1.1-i*.72,0,.12,.09,.85,district)

        # Larger identifiers occupy upper fascia; small old door signs remain.
        title = site['sign']
        if title:
            face = site['front']; yaw = {'S':0,'E':math.pi/2,'N':math.pi,'W':-math.pi/2}[face]
            width = (w if face in ['N','S'] else d)*.84
            depth = cfg['limits']['facade_depth_m']
            fy = top-min(h*.5,1.15)
            nx,nz = math.sin(yaw),math.cos(yaw)
            face_dist = (d if face in ['N','S'] else w)/2
            if roof == 'freight':
                # Mount the number on the hoist frame, clear of the retained
                # DEPOT lettering and office windows below it.
                fy = top+1.25
                face_dist = rd*.36
            p=[x+nx*(face_dist+depth/2),fy,z+nz*(face_dist+depth/2)]
            parts.append(dict(owner=owner,district=district,p=p,size=[width,1.5,depth],rotation=[0,yaw,0],color=district,role='fascia',kind='box'))
            labels.append(dict(owner=owner,district=district,text=title,p=[p[0]+nx*(depth/2+.012),fy,p[2]+nz*(depth/2+.012)],yaw=yaw,width=width*.92,height=.85))
            # Large end-tab repair plate, one deliberate mismatch per fascia.
            sx,sz=math.cos(yaw),-math.sin(yaw)
            parts.append(dict(owner=owner,district=district,p=[p[0]+sx*(width*.45)+nx*.08,fy,p[2]+sz*(width*.45)+nz*.08],size=[width*.06,1.1,.06],rotation=[0,yaw,0],color='repair',role='fascia',kind='box'))

        # Human frontage uses existing shallow awnings; attach simple valances
        # within their already occupied dimensions rather than new street props.
        if district == 'market':
            for awning in [p for p in old['parts'] if p['owner']==owner and p['role']=='awning']:
                ax,ay,az=awning['p']; yaw=awning['yaw']; aw=awning['size'][0]
                for i in range(5):
                    shift=(i-2)*aw/5
                    parts.append(dict(owner=owner,district=district,p=[ax+math.cos(yaw)*shift+math.sin(yaw)*.48,ay-.22,az-math.sin(yaw)*shift+math.cos(yaw)*.48],size=[aw/5-.04,.34,.06],rotation=[0,yaw,0],color='cream' if i%2==0 else 'market',role='awning_trim',kind='box'))

    result=dict(version=cfg['version'],config_sha256=hashlib.sha256(CONFIG.read_bytes()).hexdigest(),parts=parts,labels=labels)
    assert len(parts)<=cfg['limits']['max_parts'] and len(labels)<=cfg['limits']['max_labels']
    OUTPUT.write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
    print(json.dumps(dict(parts=len(parts),labels=len(labels),sha256=hashlib.sha256(OUTPUT.read_bytes()).hexdigest())))


if __name__ == '__main__':
    generate()
