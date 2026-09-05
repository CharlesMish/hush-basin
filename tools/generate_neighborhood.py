#!/usr/bin/env python3
"""Deterministic native primitive architecture; no external packages or RNG."""
from pathlib import Path
import argparse, hashlib, json, math, struct

ROOT=Path(__file__).resolve().parents[1]
def read(p): return json.loads(p.read_text())
def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()

def generate(output):
    cfg=read(ROOT/'game/presentation/neighborhood_v1.json');m=read(ROOT/'game/world/p1a_world_manifest.json')
    old=read(ROOT/'game/world/generated/world_polish_v1.json');mod=cfg['modules']
    parts=[];labels=[];owners=[];service=[];frontages=[]
    plots={v['id']:v['polygon'] for v in old['protection']}
    angles={'S':0,'E':math.pi/2,'N':math.pi,'W':-math.pi/2}
    def part(owner,p,size,key,solid=False,kind='box',yaw=0,emission=False,role='detail'):
        parts.append(dict(owner=owner,p=[round(v,6) for v in p],size=[round(v,6) for v in size],color=key,solid=solid,kind=kind,yaw=round(yaw,9),emission=emission,role=role))
    def label(owner,p,text,width,yaw=0):
        labels.append(dict(owner=owner,p=[round(v,6) for v in p],text=text,width_m=width,yaw=round(yaw,9)))
    def facade(owner,c,w,d,yaw):
        sn,cs=math.sin(yaw),math.cos(yaw)
        def pos(u,y,depth=0): return [c[0]+cs*u+sn*(d/2+depth),c[1]+y,c[2]-sn*u+cs*(d/2+depth)]
        def box(u,y,sx,sy,key,depth=0.025,sz=0.04,solid=False,emission=False,role='facade'):
            part(owner,pos(u,y,depth),[sx,sy,sz],key,solid,yaw=yaw,emission=emission,role=role)
        return pos,box
    for spec in cfg['buildings']:
        b=next(v for v in m['building_masses'] if v['id']==spec['id']);oid=b['id'];x,z=b['center_xz_m'];w,d=b['footprint_xz_m'];base=b['base_y_m'];h=b['height_m'];lower=h*mod['lower_fraction']
        owners.append(dict(id=oid,kind='building',use=spec['use'],plot=plots[oid],base=base,principal_top=base+h))
        part(oid,[x,base+lower/2,z],[w,lower,d],spec['material'],True,role='lower_mass')
        uw=w*mod['upper_width_fraction'];ud=d*mod['upper_depth_fraction']
        part(oid,[x,base+lower+(h-lower)/2,z],[uw,h-lower,ud],spec['material'],True,role='upper_mass')
        # Actual structural roof shoulders and plant remain inside each plot.
        for sign in [-1,1]:
            part(oid,[x+sign*(w/2-0.25),base+lower+0.18,z],[0.3,0.36,d], 'trim',True,role='parapet')
        part(oid,[x,base+h-0.12,z],[uw+0.2,0.24,ud+0.2],'trim',True,role='coping')
        py=base+lower+0.6
        for sign in [-1,1]:
            part(oid,[x+sign*(w/2-1.1),py,z],[1.5,1.2,min(d*0.32,3.5)],'steel',True,role='roof_plant')
            for k in [-0.4,0,0.4]:part(oid,[x+sign*(w/2-1.1)+k,py+0.62,z],[0.12,0.04,min(d*0.28,3)],'frame')
        for yaw in [0,math.pi/2,math.pi, -math.pi/2]:
            fw,fd=(w,d) if abs(math.sin(yaw))<0.5 else (d,w)
            pos,box=facade(oid,[x,base,z],fw,fd,yaw)
            box(0,0.25,fw,0.3,'trim');box(0,lower-0.22,fw,0.22,'frame')
            pitch=spec['window_pitch_m'];count=max(1,int((fw-2)/pitch))
            for row in range(max(1,int((lower-1.5)/mod['floor_pitch_m']))):
                y=2.2+row*mod['floor_pitch_m']
                for i in range(count):
                    u=(i-(count-1)/2)*pitch;ww=min(mod['window_width_m'],pitch-0.8);wh=mod['window_height_m']
                    box(u,y,ww+0.28,wh+0.24,'frame')
                    warm=spec['use'] in ['market','clinic'] and row==0 and i%3==1
                    box(u,y,ww,wh,'warm' if warm else 'glass',depth=0.053,emission=warm)
                    box(u,y,0.07,wh,'trim',depth=0.08)
                    box(u,y-wh/2-0.1,ww+0.35,0.14,'trim',depth=0.08,sz=0.16)
            # Upper clerestory follows the setback rather than floating at old wall.
            ufw,ufd=(uw,ud) if abs(math.sin(yaw))<0.5 else (ud,uw)
            _,upper=facade(oid,[x,base,z],ufw,ufd,yaw)
            upper(0,lower+(h-lower)*0.50,ufw*0.65,min(1.1,(h-lower)*0.5),'glass')
            for u in [-fw*0.42,fw*0.42]:box(u,lower/2,0.13,lower,'frame',depth=0.09,sz=0.13)
        yaw=angles[spec['front']];fw,fd=(w,d) if spec['front'] in ['N','S'] else (d,w)
        pos,box=facade(oid,[x,base,z],fw,fd,yaw)
        sy=min(lower-0.7,3.9);sign_width=min(fw*0.74,12.0)
        box(0,sy,sign_width,0.90,'teal' if spec['use'] in ['market','clinic'] else 'steel',depth=0.1,sz=0.16)
        label(oid,pos(0,sy,0.19),spec['name'],sign_width*0.84,yaw)
        for u in spec['wear']:
            box(u*fw,lower*0.37,0.44,lower*0.64,'stain',depth=0.049,sz=0.014)
            box(u*fw+0.35,1.0,1.0,0.8,'repair',depth=0.06,sz=0.04)
        # Find a real exposed plinth edge entirely within the protected plot.
        poly=plots[oid];xmin=min(p[0] for p in poly);xmax=max(p[0] for p in poly);zmin=min(p[1] for p in poly);zmax=max(p[1] for p in poly)
        choices=[]
        for e in old['wall_edges']:
            if e[0]!='CORE_PLINTH_MASK':continue
            a,t=e[1:3];length=math.dist(a,t)
            if length<4:continue
            mx,mz=(a[0]+t[0])/2,(a[1]+t[1])/2
            if not (xmin+0.2<mx<xmax-0.2 and zmin-0.1<=mz<=zmax+0.1) and not (zmin+0.2<mz<zmax-0.2 and xmin-0.1<=mx<=xmax+0.1):continue
            nx,nz=(t[1]-a[1])/length,-(t[0]-a[0])/length
            width=min(5.5,length-0.4)
            if all(xmin-0.15<=mx+s*nz*width/2<=xmax+0.15 and zmin-0.15<=mz-s*nx*width/2<=zmax+0.15 for s in [-1,1]):
                facing=nx*math.sin(yaw)+nz*math.cos(yaw)
                choices.append((facing,length,mx,mz,nx,nz,width))
        if choices:
            _,length,mx,mz,nx,nz,bw=max(choices);fyaw=math.atan2(nx,nz)
            # Foundation service fronts are shut panels, never fake open portals.
            fpos,fb=facade(oid,[mx,0,mz],bw,0,fyaw)
            fb(0,2.25,bw,3.2,'frame',depth=0.03)
            fb(0,2.25,bw-0.35,2.9,'teal' if spec['use']=='clinic' else 'steel',depth=0.055)
            for j in range(8):fb(0,0.92+j*0.35,bw-0.4,0.055,'frame',depth=0.079)
            fb(0,4.4,bw,0.75,'teal' if spec['use'] in ['clinic','market'] else 'amber',depth=0.08)
            label(oid,fpos(0,4.4,0.13),spec['name'] if spec['use'] in ['market','clinic'] else 'BAY '+oid[1:],bw*0.93,fyaw)
            service.append(dict(owner=oid,p=[mx,0,mz],width=bw,yaw=fyaw,closed=True))
    for i,l in enumerate(m['landmarks']):
        oid=l['id'];role=l['role'];spec=cfg['landmarks'][role];x,z=l['center_xz_m'];base=l['base_y_m'];h=l['height_m'];top=base+h
        owners.append(dict(id=oid,kind='landmark',use=role,plot=plots[oid],base=base,principal_top=top))
        if l['shape']=='CYLINDER':
            r=l['radius_m'];part(oid,[x,base+h/2,z],[r*2,h,r*2],spec['material'],True,'cylinder',role='landmark_mass')
            for rise in [h*0.2,h*0.65,h-0.45]:part(oid,[x,base+rise,z],[r*2+0.12,0.24,r*2+0.12],'amber' if role=='WORKS_STACKS' else 'trim',True,'cylinder',role='collar')
            if role=='RELAY_MAST':
                for rise,span in [(h-2,8),(h-5,6)]:part(oid,[x,base+rise,z],[span,0.25,0.4],'frame',True,role='antenna')
                for sign in [-1,1]:part(oid,[x+sign*3,top-2,z],[0.9,1.5,0.35],'teal',True,role='receiver')
                part(oid,[x+3,base+1.3,z],[1.4,2.6,1.5],'frame',True,role='relay_cabinet')
                part(oid,[x+3,base+1.3,z+0.78],[1.1,2.2,0.05],'steel',role='closed_service_panel')
                label(oid,[x+3,base+2.1,z+0.82],'SERVICE',1.0)
            else:
                part(oid,[x,top-0.08,z],[r*1.7,0.2,r*1.7],'steel',False,'cylinder')
                part(oid,[x+r+0.28,base+h*0.45,z],[0.3,h*0.85,0.3],'frame',True,role='service_pipe')
                part(oid,[x+r,base+h*0.85,z],[0.8,0.3,0.3],'frame',True,role='pipe_return')
        else:
            w,d=l['footprint_xz_m'];part(oid,[x,base+h/2,z],[w,h,d],spec['material'],True,role='landmark_mass')
            part(oid,[x,top-0.18,z],[w+0.25,0.36,d+0.25],'trim',True,role='coping')
            for yaw in [0,math.pi/2,math.pi,-math.pi/2]:
                fw,fd=(w,d) if abs(math.sin(yaw))<0.5 else (d,w);pos,box=facade(oid,[x,base,z],fw,fd,yaw)
                if role=='QUARRY_STEPS':
                    for rise in range(1,int(h),2):box(0,rise,fw,0.18,'stain')
                    box(0,h*0.55,fw*0.65,1.3,'steel',depth=0.06)
                    if yaw==0:label(oid,pos(0,h*0.55,0.10),'QUARRY '+str(i+1),fw*0.48,yaw)
                else:
                    for rise in range(2,int(h)-1,3):
                        for u in ([0] if role=='DEPOT_TWINS' else [-fw*0.25,0,fw*0.25]):
                            box(u,rise,fw*0.19,1.45,'frame')
                            warm=role in ['MARKET_CANOPY','CLINIC_TOWER'] and rise==2 and u==0
                            box(u,rise,fw*0.16,1.2,'warm' if warm else 'glass',depth=0.05,emission=warm)
                    box(0,h-1.5,fw*0.90,1.2,'teal' if role!='DEPOT_TWINS' else 'amber',depth=0.08)
                    if yaw==0:
                        title={'MRK_FIN_W':'PANTRY','MRK_FIN_E':'REPAIRS','MRK_FIN_S':'TEA'}.get(oid,spec['name'])
                        label(oid,pos(0,h-1.5,0.14),title,fw*0.65,yaw)
                    if role=='MARKET_CANOPY':
                        box(0,3.4,fw+0.5,0.3,'teal',depth=0.5,sz=1.0,solid=True,role='awning')
                    if role=='CLINIC_TOWER':
                        # Original care mark: paired vertical bars inside a frame.
                        box(0,h-4,2.1,2.1,'teal',depth=0.05)
                        for u in [-0.45,0.45]:box(u,h-4,0.25,1.4,'letter',depth=0.09)
    # Clinic and Depot occupy larger retained compounds. Their closed entry
    # fronts sit directly on existing outer retaining faces nearest the pad;
    # they do not add a solid, cut a passage, or spread objects onto the road.
    used_edges=[]
    for spec in cfg['compound_frontages']:
        node_id,oid,title=spec['node'],spec['owner'],spec['title']
        target=m['nodes'][node_id]['xz_m'];choices=[];width=cfg['compound_door_width_m']
        for edge in old['wall_edges']:
            if edge[0] not in ['CORE_PLINTH_MASK','CORE_WALL','OUTER_CLOSURE_MASK'] or float(edge[3])<5.1:continue
            a,b=edge[1:3];length=math.dist(a,b)
            if length<width+0.3 or edge in used_edges:continue
            dx,dz=b[0]-a[0],b[1]-a[1];nx,nz=dz/length,-dx/length
            t=max((width/2+0.15)/length,min(1-(width/2+0.15)/length,((target[0]-a[0])*dx+(target[1]-a[1])*dz)/(length*length)))
            x,z=a[0]+t*dx,a[1]+t*dz
            if nx*(target[0]-x)+nz*(target[1]-z)<=0:continue
            choices.append((math.dist([x,z],target),x,z,math.atan2(nx,nz),edge))
        _,x,z,yaw,edge=min(choices);used_edges.append(edge);start=len(parts);index=len(frontages)
        pos,box=facade(oid,[x,0,z],width,0,yaw)
        box(0,2.05,width,3.9,'trim',depth=0.04)
        box(0,1.9,width-0.25,3.5,'teal' if node_id=='CLN' else 'steel',depth=0.07)
        for j in range(8):box(0,0.5+j*0.4,width-0.35,0.05,'frame',depth=0.10)
        box(0,4.65,width+0.2,0.8,'teal' if node_id=='CLN' else 'amber',depth=0.07)
        label(oid,pos(0,4.65,0.13),title,width*0.84,yaw)
        for item in parts[start:]:item['frontage']=index
        frontages.append(dict(owner=oid,node=node_id,title=title,source_edge=edge,p=[x,0,z],width=width+0.2,yaw=yaw,closed=True))
    data=dict(version=cfg['version'],config_sha256=digest(ROOT/'game/presentation/neighborhood_v1.json'),owners=owners,parts=parts,labels=labels,service_fronts=service,compound_frontages=frontages)
    output.mkdir(parents=True,exist_ok=True)
    p=output/'neighborhood_v1.json';p.write_text(json.dumps(data,sort_keys=True,separators=(',',':'))+'\n')
    (output/'neighborhood_v1_index.json').write_text(json.dumps(dict(version=cfg['version'],sha256=digest(p),config_sha256=data['config_sha256']),sort_keys=True,indent=2)+'\n')
    return data

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,default=ROOT/'game/presentation/generated');a=p.parse_args();d=generate(a.output);print('Generated',len(d['parts']),'parts,',len(d['labels']),'labels,',len(d['service_fronts']),'ground service fronts')
