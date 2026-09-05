#!/usr/bin/env python3
"""Author the presentation-only Quarto derivative as explicit native nodes and triangles.

No gameplay input is read or written. Run from any directory; the existing eleven
material blocks in vehicle_visual.tscn are retained verbatim. The JSON is also the
portable mesh/pose source used by the comparison viewer, not a second model.
"""
from __future__ import annotations

import json
import math
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
SCENE = ROOT / "scenes/vehicle_visual.tscn"
DATA = ROOT / "presentation/quarto_native_v1.json"


def sub(a, b):
    return [a[i] - b[i] for i in range(3)]


def cross(a, b):
    return [a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0]]


def dot(a, b):
    return sum(a[i]*b[i] for i in range(3))


def unit(a):
    length = math.sqrt(dot(a, a))
    return [v / length for v in a]


def clean(value):
    if isinstance(value, float):
        return round(value, 9)
    if isinstance(value, list):
        return [clean(x) for x in value]
    if isinstance(value, dict):
        return {k: clean(v) for k, v in value.items()}
    return value


class Mesh:
    def __init__(self):
        self.vertices, self.normals, self.indices = [], [], []

    def face(self, points, outward):
        points = list(points)
        normal = cross(sub(points[1], points[0]), sub(points[2], points[0]))
        if dot(normal, outward) < 0:
            points.reverse()
            normal = cross(sub(points[1], points[0]), sub(points[2], points[0]))
        normal = unit(normal)
        start = len(self.vertices)
        self.vertices.extend(points)
        self.normals.extend([normal] * len(points))
        # Godot front faces are clockwise; outward normals are explicit.
        for index in range(1, len(points) - 1):
            self.indices.extend([start, start + index + 1, start + index])

    def data(self):
        return {"vertices": self.vertices, "normals": self.normals, "indices": self.indices}


def prism(outline, bottom, top, bevel=0.0):
    """Convex XZ outline, optional inset top bevel, all faces closed."""
    mesh = Mesh()
    cx = sum(p[0] for p in outline)/len(outline)
    cz = sum(p[1] for p in outline)/len(outline)
    lower = [[x, bottom, z] for x, z in outline]
    upper = [[x, top-bevel, z] for x, z in outline]
    for i in range(len(outline)):
        j = (i+1) % len(outline)
        a, b = outline[i], outline[j]
        outward = [(a[0]+b[0])/2-cx, 0, (a[1]+b[1])/2-cz]
        mesh.face([lower[i], lower[j], upper[j], upper[i]], outward)
    mesh.face(lower, [0, -1, 0])
    if bevel:
        cap = []
        # A homothetic cap keeps every bevel quad planar and the solid convex.
        # Per-corner radial distances would subtly twist those quads.
        inset_ratio = max(0.1, 1-bevel/min(math.hypot(x-cx,z-cz) for x,z in outline))
        for x, z in outline:
            cap.append([cx+(x-cx)*inset_ratio, top, cz+(z-cz)*inset_ratio])
        for i in range(len(outline)):
            j = (i+1) % len(outline)
            mesh.face([upper[i], upper[j], cap[j], cap[i]],
                      [(outline[i][0]+outline[j][0])/2-cx, bevel, (outline[i][1]+outline[j][1])/2-cz])
        mesh.face(cap, [0, 1, 0])
    else:
        mesh.face(upper, [0, 1, 0])
    return mesh.data()


def box(size, bevel=0.0):
    x, y, z = [v/2 for v in size]
    return prism([[-x,-z],[x,-z],[x,z],[-x,z]], -y, y, bevel)


def hull(sections):
    """Convex stations (z, half-width, bottom, shoulder, crown-width, crown-y)."""
    rings = []
    for z, w, b, s, cw, cy in sections:
        rings.append([[-w*.65,b,z],[w*.65,b,z],[w,s,z],[cw,cy,z],[-cw,cy,z],[-w,s,z]])
    mesh = Mesh()
    mesh.face(rings[0], [0,0,-1])
    mesh.face(rings[-1], [0,0,1])
    for k in range(len(rings)-1):
        for i in range(6):
            j = (i+1)%6
            points = [rings[k][i],rings[k][j],rings[k+1][j],rings[k+1][i]]
            center = [sum(p[c] for p in points)/4 for c in range(3)]
            # The radial cross-section normal, independent of fore/aft taper.
            normals = [[0,-1,0],[1,-.4,0],[1,1,0],[0,1,0],[-1,1,0],[-1,-.4,0]]
            mesh.face(points, normals[i])
    return mesh.data()


def tube(outer, inner, length, segments=16):
    """Closed positive-thickness annular solid, open axial passage along Z."""
    mesh = Mesh()
    for i in range(segments):
        a, b = 2*math.pi*i/segments, 2*math.pi*(i+1)/segments
        radial = [math.cos((a+b)/2),math.sin((a+b)/2),0]
        def p(r, ang, z):
            return [r*math.cos(ang),r*math.sin(ang),z]
        ofa, ofb = p(outer,a,-length/2),p(outer,b,-length/2)
        oba, obb = p(outer,a,length/2),p(outer,b,length/2)
        ifa, ifb = p(inner,a,-length/2),p(inner,b,-length/2)
        iba, ibb = p(inner,a,length/2),p(inner,b,length/2)
        mesh.face([ofa,ofb,obb,oba], radial)
        mesh.face([ifa,ifb,ibb,iba], [-v for v in radial])
        mesh.face([ofa,ofb,ifb,ifa], [0,0,-1])
        mesh.face([oba,obb,ibb,iba], [0,0,1])
    return mesh.data()


def shaft(radius, length, segments=8):
    mesh = Mesh()
    front = [[radius*math.cos(2*math.pi*i/segments),radius*math.sin(2*math.pi*i/segments),-length/2] for i in range(segments)]
    rear = [[p[0],p[1],length/2] for p in front]
    mesh.face(front,[0,0,-1]); mesh.face(rear,[0,0,1])
    for i in range(segments):
        j=(i+1)%segments
        mesh.face([front[i],front[j],rear[j],rear[i]],[(front[i][0]+front[j][0])/2,(front[i][1]+front[j][1])/2,0])
    return mesh.data()


def build():
    source = SCENE.read_text()
    material_blocks = re.findall(r'\[sub_resource type="StandardMaterial3D" id="Material_[^"]+"\]\n.*?(?=\n\[|\Z)', source, re.S)
    assert len(material_blocks) == 11, "Retain the exact eleven inherited materials."
    materials = {}
    for block in material_blocks:
        key = re.search(r'id="([^"]+)"',block).group(1)
        values = {}
        for line in block.splitlines()[1:]:
            if " = " not in line: continue
            name,value=line.split(" = ",1)
            if value.startswith("Color("):
                values[name]=[float(v.strip()) for v in value[6:-1].split(',')]
            elif value in ("true","false"):
                values[name]=value=="true"
            else:
                values[name]=float(value)
        materials[key]=values

    meshes, nodes, channels = {}, [], []
    def node(path, position=(0,0,0), rotation=(0,0,0), mesh=None, material=None, mesh_data=None):
        if mesh_data is not None: meshes[mesh]=mesh_data
        record={"path":path,"parent":path.rpartition('/')[0] or ".", "type":"MeshInstance3D" if mesh else "Node3D", "position":list(position),"rotation_degrees":list(rotation)}
        if mesh: record.update(mesh=mesh,material="Material_"+material)
        nodes.append(record)
    def solid(path,size,position,material,bevel=0.0):
        node(path,position,mesh=path.replace('/','__'),material=material,mesh_data=box(size,bevel))
    def channel(path,prop,component,start,end,travel):
        channels.append({"path":path,"property":prop,"component":component,"start":start,"end":end,"travel":travel})

    node("CentralStructure")
    # Long articulated-looking shell stops before the stern's open annular passage.
    node("CentralStructure/ForwardBody",mesh="forebody",material="shell",mesh_data=hull([
        (-1.15,.10,-.035,.015,.065,.075),(-.92,.285,-.11,.08,.19,.19),
        (-.72,.215,-.12,.09,.13,.20),(-.56,.145,-.12,.10,.09,.22),
        (-.40,.135,-.12,.12,.085,.24),(.14,.135,-.09,.105,.08,.235)]))
    node("CentralStructure/VentralKeel",mesh="ventral_keel",material="structure",mesh_data=hull([
        (-1.10,.055,-.13,-.08,.04,-.055),(-.72,.12,-.145,-.075,.07,-.045),
        (.70,.10,-.145,-.085,.06,-.06),(1.15,.07,-.13,-.08,.045,-.045)]))
    node("CentralStructure/DorsalSpine",mesh="dorsal_spine",material="structure",mesh_data=hull([
        (-.81,.04,.185,.205,.024,.225),(-.22,.065,.20,.25,.035,.278),
        (.22,.045,.205,.25,.025,.275)]))
    solid("CentralStructure/EnergyCore",(.105,.04,.19),(0,.278,-.22),"energy",.007)
    for side,label in [(-1,"Port"),(1,"Starboard")]:
        node("CentralStructure/Chine"+label,mesh="chine_"+label,material="shell",mesh_data=hull([
            (-.89,.038,-.02,.035,.022,.075),(-.50,.035,-.035,.005,.021,.035),
            (.18,.035,.015,.16,.021,.20),(.73,.035,.01,.18,.021,.22)]))
        nodes[-1]["position"]=[side*.155,0,0]
        solid("CentralStructure/AftRail"+label,(.064,.08,.72),(side*.23,-.065,.64),"structure",.009)
        solid("CentralStructure/AftShoulder"+label,(.058,.13,.38),(side*.175,.075,.72),"shell",.012)
        # Slim mint facets identify the rising shoulder without becoming luminous trim everywhere.
        solid("CentralStructure/ChineIndex"+label,(.015,.018,.24),(side*.173,.203,.31),"joint",.003)

    node("CentralStructure/DriveBay")
    node("CentralStructure/DriveBay/FixedCore",(0,0,.645),mesh="fixed_core",material="energy",mesh_data=shaft(.052,.75,8))
    for side,label in [(-1,"Port"),(1,"Starboard")]:
        solid("CentralStructure/DriveBay/Guide"+label,(.032,.035,.88),(side*.184,-.062,.62),"joint",.004)
    node("CentralStructure/DriveBay/Receiver",(0,0,.77),mesh="receiver",material="joint",mesh_data=tube(.177,.137,.048))
    node("CentralStructure/DriveBay/ReceiverIndex",(0,0,.801),mesh="receiver_index",material="panel_seam",mesh_data=tube(.167,.142,.008))
    node("CentralStructure/DriveBay/MovingCan",(0,0,.47))
    node("CentralStructure/DriveBay/MovingCan/CanBody",mesh="can_tube",material="can",mesh_data=tube(.125,.092,.51,20))
    node("CentralStructure/DriveBay/MovingCan/CaptureFlange",(0,0,-.2675),mesh="capture_flange",material="joint",mesh_data=tube(.147,.092,.025,20))
    node("CentralStructure/DriveBay/MovingCan/NozzleRing",(0,0,.265),mesh="nozzle_ring",material="nozzle",mesh_data=tube(.135,.092,.020,20))
    node("CentralStructure/DriveBay/MovingCan/NozzleBore",(0,0,.222),mesh="nozzle_bore",material="bore",mesh_data=tube(.091,.086,.066,20))
    channel("CentralStructure/DriveBay/MovingCan","position",2,.88,1,.51)
    for label,axis,side in [("Port",0,-1),("Starboard",0,1),("Top",1,1),("Bottom",1,-1)]:
        parent="CentralStructure/DriveBay/Capture"+label
        p=[0,0,.717]; p[axis]=side*.190
        node(parent,p)
        size=[.050,.034,.052] if axis==0 else [.034,.050,.052]
        solid(parent+"/Housing",size,(0,0,.045),"structure",.006)
        size=[.038,.026,.023] if axis==0 else [.026,.038,.023]
        solid(parent+"/Jaw",size,(0,0,0),"joint",.004)
        channel(parent+"/Jaw","position",axis,.965,1,-side*.022)

    for family,rootx,rooty,rootz,inner,outer,chord,thickness,yaw,cant,slide,windows in [
        ("Front",.385,.13,-.60,.45,.39,.36,.052,78,70,.080,(.04,.26,.58,.80,.70)),
        ("Rear",.37,.35,.28,.50,.46,.52,.056,84,-70,.070,(.08,.34,.66,.86,.76)),
    ]:
        fold_start,fold_end,yaw_end,cant_end,slide_start=windows
        gap=.022
        hinge_y=-(thickness+gap)/2
        for side,label in [(-1,"Port"),(1,"Starboard")]:
            rig=family+label+"Rig"
            node(rig,(side*rootx,rooty,rootz))
            socket=rig+"/SocketSlide"; node(socket)
            yaw_path=socket+"/YawPivot"; node(yaw_path)
            cant_path=yaw_path+"/HaunchPivot"; node(cant_path)
            # A tapered six-corner leaf silhouette, with literal thickness.
            def leaf(span,cw):
                outline=[(side*.018,-cw*.40),(side*(span-.045),-cw*.5),(side*span,-cw*.33),
                         (side*span,cw*.29),(side*(span-.055),cw*.5),(side*.018,cw*.42)]
                return prism(outline,-thickness/2,thickness/2,.010)
            node(cant_path+"/InnerLeaf",mesh=family+label+"_inner",material="lift",mesh_data=leaf(inner,chord))
            fold=cant_path+"/OuterFold"
            node(fold,(side*inner,hinge_y,0))
            node(fold+"/OuterLeaf",(0,-hinge_y,0),mesh=family+label+"_outer",material="lift",mesh_data=leaf(outer,chord*.92))
            # Underlays are a distinct solid layer; they never disappear in the fold.
            for part,parent,span,cw,y in [("Inner",cant_path,inner,chord,0),("Outer",fold,outer,chord*.92,-hinge_y)]:
                outline=[(side*.055,-cw*.32),(side*(span-.075),-cw*.39),(side*(span-.032),0),
                         (side*(span-.075),cw*.35),(side*.055,cw*.31)]
                node(parent+"/"+part+"Underlay",(0,y-thickness/2-.0035,0),mesh=family+label+part+"_underlay",material="lift_underlay",mesh_data=prism(outline,-.0035,.0035,.001))
                # One strong seam forward, two aft; readable at the chase camera scale.
                seam_z=[0] if family=="Front" else [-cw*.18,cw*.18]
                for number,z in enumerate(seam_z):
                    solid(parent+"/"+part+"Seam"+str(number),(.62*span,.009,.013),(side*span*.53,y+thickness/2+.0045,z),"panel_seam",.002)
                solid(parent+"/"+part+"Tip",(.035,.018,cw*.50),(side*(span-.032),y+.018,0),"lift_edge",.005)
            # Positive-scale hinge barrel shared by both members.
            node(cant_path+"/FoldHinge",(side*inner,hinge_y,0),mesh=family+label+"_hinge",material="joint",mesh_data=shaft(.028,chord*.89,12))
            solid(cant_path+"/RootBridge",(.115,.055,.12),(side*.025,-.030,0),"joint",.008)
            channel(fold,"rotation_degrees",2,fold_start,fold_end,-side*180)
            channel(yaw_path,"rotation_degrees",1,fold_end,yaw_end,-side*yaw)
            channel(cant_path,"rotation_degrees",0,yaw_end,cant_end,cant)
            channel(socket,"position",0,slide_start,cant_end,-side*slide)

            # Fixed three-wall C receiver. Its open end owns the seated folio;
            # the far portion remains proud instead of vanishing into a hull.
            pocket="CentralStructure/"+family+label+"Pocket"
            node(pocket,(side*(rootx-slide-.055),rooty,rootz))
            seat_yaw=pocket+"/SeatYaw"; node(seat_yaw,rotation=(0,-side*yaw,0))
            seat=seat_yaw+"/SeatCant"; node(seat,rotation=(cant,0,0))
            depth=inner*.55
            lower_side=1 if cant>0 else -1
            shelf_drop=.115 if family=="Front" else .065
            shelf_y=-.145-shelf_drop*math.cos(math.radians(cant))
            shelf_z=lower_side*chord*.25+shelf_drop*math.sin(math.radians(cant))
            frame_bottom=shelf_y-.01
            frame_top=-.023
            solid(seat+"/LowerLip",(depth,frame_top-frame_bottom,.022),(side*depth*.50,(frame_bottom+frame_top)/2,lower_side*(chord/2+.022)),"shell",.006)
            solid(seat+"/Back",(.034,frame_top-frame_bottom,chord*.5+.09),(-side*.015,(frame_bottom+frame_top)/2,lower_side*(chord*.25+.035)),"structure",.006)
            solid(seat+"/Shelf",(depth,.020,chord*.5),(side*depth*.50,shelf_y,shelf_z),"shell",.005)
            solid(seat+"/SeatIndex",(.040,.014,.07),(-side*.018,-.015,lower_side*chord*.15),"panel_seam",.003)

    asset={
        "schema":"hush_basin.quarto_native_visual.v1", "units":"metres", "forward":"-Z", "up":"+Y",
        "winding":"clockwise", "rotation_order":"YXZ", "participates_in_authority":False,
        "materials":materials,"meshes":meshes,"nodes":nodes,"pose_channels":channels,
        "energy_colors":{"SPREAD":[1.0,.58,.16,1.0],"DRIVE":[.2,.95,1.0,1.0],
                         "CAUTION":[1.0,.72,.12,1.0],"STRIKE":[1.0,.12,.08,1.0]},
        "propulsion_window":[.88,1.0],
        "energy_material_paths":["CentralStructure/EnergyCore","CentralStructure/DriveBay/FixedCore"],
        "propulsion_material_paths":["CentralStructure/DriveBay/MovingCan/NozzleRing"],
        "notes":["Presentation-only native derivative; no physics descendants or proof transfer.",
                 "Pose channels add smoothstep travel to authored rest transforms; never scale/hide geometry.",
                 "Mesh arrays and native hierarchy generated together; same JSON drives comparison preview."]
    }
    DATA.parent.mkdir(parents=True,exist_ok=True)
    DATA.write_text(json.dumps(clean(asset),indent=2)+"\n")
    lines=['[gd_scene load_steps=13 format=3]','',
           '[ext_resource type="Script" path="res://scripts/vehicle_visual_rig.gd" id="1_rig"]','']
    lines.extend(block.strip()+"\n" for block in material_blocks)
    lines.extend(['[node name="VisualRoot" type="Node3D"]','script = ExtResource("1_rig")',''])
    def vector(v): return "Vector3("+", ".join(str(round(x,9)) for x in v)+")"
    for record in nodes:
        name=record['path'].split('/')[-1]
        lines.append(f'[node name="{name}" type="{record["type"]}" parent="{record["parent"]}"]')
        if any(record['position']):lines.append("position = "+vector(record['position']))
        if any(record['rotation_degrees']):lines.append("rotation = "+vector([math.radians(x) for x in record['rotation_degrees']]))
        if record.get('mesh'):
            lines.append('metadata/quarto_mesh = "'+record['mesh']+'"')
            lines.append('material_override = SubResource("'+record['material']+'")')
        lines.append('')
    SCENE.write_text("\n".join(lines))
    print(json.dumps({"mesh_count":len(meshes),"node_count":len(nodes),"pose_channel_count":len(channels),"triangle_count":sum(len(m['indices'])//3 for m in meshes.values())}))


if __name__ == "__main__":
    build()
