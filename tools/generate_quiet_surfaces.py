#!/usr/bin/env python3
"""Offline, dependency-free scanline surface atlas; world geometry is read-only."""
from pathlib import Path
import argparse, hashlib, json, math, struct, zlib, subprocess

ROOT=Path(__file__).resolve().parents[1]
GAME=ROOT/'game'
CONFIG=GAME/'presentation/quiet_surfaces_v1.json'
OUT=GAME/'presentation/generated'
read=lambda p:json.loads(p.read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def png(path,w,h,channels,data):
    def chunk(kind,b):return struct.pack('>I',len(b))+kind+b+struct.pack('>I',zlib.crc32(kind+b)&0xffffffff)
    rows=b''.join(b'\0'+data[y*w*channels:(y+1)*w*channels] for y in range(h))
    path.write_bytes(b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',w,h,8,2 if channels==3 else 0,0,0,0))+chunk(b'IDAT',zlib.compress(rows,9))+chunk(b'IEND',b''))

class Raster:
    def __init__(self,n,bounds):
        self.n=n;self.x0,self.z0,self.x1,self.z1=bounds
        self.sx=n/(self.x1-self.x0);self.sz=n/(self.z1-self.z0)
    def spans(self,poly):
        # Bucket crossings by scanline: work is bounded by covered rows/edges,
        # rather than comparing every texel to every baked road segment.
        p=[((x-self.x0)*self.sx,(z-self.z0)*self.sz) for x,z in poly];rows={}
        for (ax,ay),(bx,by) in zip(p,p[1:]+p[:1]):
            if ay==by:continue
            if ay>by:ax,ay,bx,by=bx,by,ax,ay
            for y in range(max(0,math.ceil(ay-.5)),min(self.n,math.ceil(by-.5))):
                rows.setdefault(y,[]).append(ax+(y+.5-ay)*(bx-ax)/(by-ay))
        for y,xs in sorted(rows.items()):
            xs.sort()
            for i in range(0,len(xs)-1,2):
                a=max(0,math.ceil(xs[i]-.5));b=min(self.n,math.ceil(xs[i+1]-.5))
                if b>a:yield y*self.n+a,y*self.n+b
    def fill(self,target,poly,value,maximum=False):
        for a,b in self.spans(poly):
            if maximum:
                for i in range(a,b):
                    if target[i]<value:target[i]=value
            else:target[a:b]=bytes([value])*(b-a)

def ribbon(points,half):
    left=[];right=[]
    for i,(x,z) in enumerate(points):
        a=points[max(0,i-1)];b=points[min(len(points)-1,i+1)]
        dx,dz=b[0]-a[0],b[1]-a[1];length=math.hypot(dx,dz)
        nx,nz=-dz/length,dx/length
        left.append((x+nx*half,z+nz*half));right.append((x-nx*half,z-nz*half))
    return left+right[::-1]

def circle(center,radius):
    return [(center[0]+radius*math.cos(i*math.tau/128),center[1]+radius*math.sin(i*math.tau/128)) for i in range(128)]

def sample_route(points,fraction):
    lengths=[math.dist(a,b) for a,b in zip(points,points[1:])];wanted=sum(lengths)*fraction
    for a,b,length in zip(points,points[1:],lengths):
        if wanted<=length:
            t=wanted/length;return (a[0]+(b[0]-a[0])*t,a[1]+(b[1]-a[1])*t),((b[0]-a[0])/length,(b[1]-a[1])/length)
        wanted-=length
    raise ValueError('Invalid chainage')

def route_interval(points,start,end):
    result=[];distance=0
    for a,b in zip(points,points[1:]):
        length=math.dist(a,b)
        lo=max(start,distance);hi=min(end,distance+length)
        if hi>lo:
            for at in [lo,hi]:
                t=(at-distance)/length;p=(a[0]+(b[0]-a[0])*t,a[1]+(b[1]-a[1])*t)
                if not result or math.dist(result[-1],p)>1e-8:result.append(p)
        distance+=length
    return result

def noise_value(x,z,seed):
    h=(x*374761393+z*668265263+seed*1447)&0xffffffff
    h=((h^(h>>13))*1274126177)&0xffffffff
    return ((h^(h>>16))&65535)/32767.5-1

def generate(output=OUT,details=True):
    cfg=read(CONFIG);n=cfg['resolution'];size=n*n;r=Raster(n,cfg['bounds_xz_m'])
    world=read(GAME/'world/p1a_world_manifest.json');bake=read(GAME/'world/generated/route_bake.json')['routes']
    polish=read(GAME/'world/world_polish_v1.json');meta=read(GAME/'world/generated/terrain_metadata.json')
    names=list(cfg['palette_linear']);kind=bytearray(size);shoulder=bytearray(size);road=bytearray(size);road_kind=bytearray(size)
    idx={v:i for i,v in enumerate(names)}
    for yard in polish['yards']:r.fill(kind,yard['polygon'],idx['yard'])
    for route_id,route in world['routes'].items():
        points=bake[route_id]['points_xz_m'];half=route['roadbed_width_m']/2
        outer=half+route['shoulder_each_side_m'];transition=cfg['shoulder_transition_m']
        for band in range(8):
            r.fill(shoulder,ribbon(points,outer+transition*(1-band/7)),round(255*(band+1)/8),True)
        name={'SMOOTH_PAVE':'asphalt','SMOOTH_FIRM':'firm','COMPACTED_SMOOTH':'compacted','ROUGH_R2':'compacted'}[route['surface_authority']]
        # Outer-to-inner coverage gives a 0.6 m worn material edge.
        for band in range(5):
            radius=half+cfg['road_transition_m']*(.5-band/4)
            poly=ribbon(points,radius);r.fill(road,poly,round(255*(band+1)/5),True);r.fill(road_kind,poly,idx[name])
    # Actual terrain material radii come from the evaluator, not the larger
    # junction navigation-region radii in the world manifest.
    for node in world['junctions'].values():
        for band in range(5):
            poly=circle(node['center_xz_m'],meta['evaluator']['junctions']['outer_radius_m']-cfg['road_transition_m']*band/4)
            r.fill(road,poly,round(255*(band+1)/5),True);r.fill(road_kind,poly,idx['asphalt'])
    for pad in world['destination_pads'].values():
        for band in range(5):
            poly=circle(pad['center_xz_m'],pad['outer_blend_radius_m']-cfg['road_transition_m']*band/4)
            r.fill(road,poly,round(255*(band+1)/5),True);r.fill(road_kind,poly,idx['asphalt'])
    # Preserve the existing authored rough section and gate rings as material cues.
    special=bytearray(size)
    start,end=meta['evaluator']['rough_R0']['chainage_m']
    for band in range(5):
        inset=cfg['road_transition_m']*band/4
        points=route_interval(bake['R0']['points_xz_m'],start+inset,end-inset)
        r.fill(special,ribbon(points,world['routes']['R0']['roadbed_width_m']/2-inset),round(255*(band+1)/5),True)
    for gate in world['gates'].values():
        cx,cz=gate['center_xz_m'];outer=gate['visual_marker']['outer_radius_m'];inner=gate['visual_marker']['inner_radius_m']
        for y in range(max(0,math.floor((cz-outer-r.z0)*r.sz)),min(n,math.ceil((cz+outer-r.z0)*r.sz))):
            for x in range(max(0,math.floor((cx-outer-r.x0)*r.sx)),min(n,math.ceil((cx+outer-r.x0)*r.sx))):
                distance=math.hypot(r.x0+(x+.5)/r.sx-cx,r.z0+(y+.5)/r.sz-cz)
                coverage=max(0,min(1,min(distance-inner,outer-distance)/(cfg['road_transition_m']/2)))
                special[y*n+x]=max(special[y*n+x],round(255*coverage))
    # Broad bilinear value noise, fixed seed; no runtime randomness or fine grain.
    variation=bytearray(size);scales=cfg['variation']['scales_m'];grids=[]
    for scale in scales:
        xs=[(r.x0+(x+.5)/r.sx)/scale for x in range(n)]
        grids.append([(math.floor(v),v-math.floor(v)) for v in xs])
    colors=bytearray(size*3);rough=bytearray(size)
    srgb=[round(255*(12.92*(i/65535) if i/65535<=.0031308 else 1.055*(i/65535)**(1/2.4)-.055)) for i in range(65536)]
    palette=[cfg['palette_linear'][k] for k in names];roughs=[cfg['roughness'][k] for k in names]
    for y in range(n):
        if y%512==0:print('surface rows',y,flush=True)
        z=r.z0+(y+.5)/r.sz;noise_rows=[]
        for scale in scales:
            q=z/scale;iz=math.floor(q);tz=q-iz;tz=tz*tz*(3-2*tz)
            noise_rows.append((iz,tz))
        for x in range(n):
            i=y*n+x;c=palette[kind[i]];rv=roughs[kind[i]]
            t=shoulder[i]/255
            if t:c=[v+(q-v)*t for v,q in zip(c,palette[idx['shoulder']])];rv=rv+(cfg['roughness']['shoulder']-rv)*t
            t=road[i]/255
            if t:c=[v+(q-v)*t for v,q in zip(c,palette[road_kind[i]])];rv=rv+(roughs[road_kind[i]]-rv)*t
            if special[i]:
                t=special[i]/255;c=[v+(q-v)*t for v,q in zip(c,palette[idx['amber']])];rv=rv+(cfg['roughness']['amber']-rv)*t
            value=0
            for j,(iz,tz) in enumerate(noise_rows):
                ix,tx=grids[j][x];tx=tx*tx*(3-2*tx);seed=cfg['seed']+j*101
                a=noise_value(ix,iz,seed);b=noise_value(ix+1,iz,seed);cc=noise_value(ix,iz+1,seed);d=noise_value(ix+1,iz+1,seed)
                value+=(a+(b-a)*tx)*(1-tz)+(cc+(d-cc)*tx)*tz
            mul=1+value/len(scales)*cfg['variation']['amplitude'];variation[i]=round(128+value*35)
            for k in range(3):colors[i*3+k]=srgb[max(0,min(65535,round(c[k]*mul*65535)))]
            # Keep roughness uniform within each material: broad albedo variation
            # supplies the wear without another changing sheen pattern.
            rough[i]=round(255*min(1,max(0,rv)))
    detail_records=[]
    def tint(poly,mult,roughness=None,color=None):
        for a,b in r.spans(poly):
            for i in range(a,b):
                if special[i]:continue
                for k in range(3):colors[i*3+k]=round(min(255,colors[i*3+k]*mult)) if color is None else srgb[round(color[k]*65535)]
                if roughness is not None:rough[i]=round(roughness*255)
    if details:
        for j,p in enumerate(cfg['patches']):
            center,direction=sample_route(bake[p['route']]['points_xz_m'],p['fraction']);dx,dz=direction;nx,nz=-dz,dx;cx,cz=center;cx+=nx*p['offset_m'];cz+=nz*p['offset_m'];w,l=p['size_m']
            outline=[(-.5,-.5),(.36,-.5),(.5,-.32),(.5,.5),(-.40,.5),(-.5,.30)]
            if j%2:outline=[(-x,z) for x,z in outline][::-1]
            poly=[(cx+nx*x*w+dx*z*l,cz+nz*x*w+dz*z*l) for x,z in outline]
            tint(poly,p['value']**cfg['maintenance']['patch_contrast_exponent'],.66)
            detail_records.append({'kind':'patch','route':p['route'],'polygon':poly})
        for cover in cfg['covers']:
            cx,cz=cover['center_xz_m'];w,l=cover['size_m'];a=math.radians(cover['angle_deg']);c,s=math.cos(a),math.sin(a)
            def rect(scale):return [(cx+(x*w*c-z*l*s)*scale,cz+(x*w*s+z*l*c)*scale) for x,z in [(-.5,-.5),(.5,-.5),(.5,.5),(-.5,.5)]]
            tint(rect(1.0),cfg['maintenance']['cover_frame_multiplier'],.8);tint(rect(.72),1,.75,cfg['palette_linear']['cover'])
            detail_records.append({'kind':'cover','owner':cover['owner'],'polygon':rect(1)})
    output.mkdir(parents=True,exist_ok=True)
    png(output/'quiet_surfaces_albedo.png',n,n,3,colors);png(output/'quiet_surfaces_roughness.png',n,n,1,rough)
    from launch import resolve_engine
    engine,_=resolve_engine(None)
    subprocess.run([str(engine),'--headless','--path',str(GAME),'--script','res://tools/bake_quiet_surface_resources.gd','--log-file',str(output/'quiet_surface_bake.log'),'--','--folder',str(output.resolve())],check=True)
    # Conservative RGBA8+R8 accounting includes a full mip pyramid.
    memory=sum(max(1,n>>level)**2*5 for level in range(int(math.log2(n))+1))
    index={'version':cfg['version'],'config_sha256':sha(CONFIG),'details_enabled':details,'size':[n,n],'bounds_xz_m':cfg['bounds_xz_m'],'resident_texture_bytes_upper_bound':memory,'artifacts':{k:sha(output/k) for k in ['quiet_surfaces_albedo.png','quiet_surfaces_roughness.png','quiet_surfaces_albedo.res','quiet_surfaces_roughness.res']},'details':detail_records,'inputs':{str(p.relative_to(ROOT)):sha(p) for p in [GAME/'world/p1a_world_manifest.json',GAME/'world/generated/route_bake.json',GAME/'world/generated/terrain_metadata.json',GAME/'world/generated/world_polish_v1_surface.bin',GAME/'world/world_polish_v1.json']}}
    (output/'quiet_surfaces_index.json').write_text(json.dumps(index,indent=2,sort_keys=True)+'\n');print('Generated',len(detail_records),'details;',memory,'resident bytes',flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,default=OUT);p.add_argument('--edges-only',action='store_true');args=p.parse_args();generate(args.output,not args.edges_only)
