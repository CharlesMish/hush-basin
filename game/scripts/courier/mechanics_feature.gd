extends Node3D
## One Works service crossing; render and collision use the same dimensions.
var gate: P1AWorldGate
var center:=Vector3.ZERO
var forward:=Vector3.FORWARD
var body: StaticBody3D
func _ready() -> void:
 name="WorksServiceCrossing"
 var cfg: Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://presentation/mechanics_range_v1.json")).works
 var points: Array=gate.data.routes[cfg.route].points_xz_m
 var i:=int((points.size()-1)*float(cfg.fraction))
 var p:=P1AWorldData.xz(points[i]);var d: Vector2=(P1AWorldData.xz(points[i+1])-p).normalized()
 forward=Vector3(d.x,0,d.y)
 center=Vector3(p.x,gate.data.terrain_height_at(p.x,p.y),p.y)
 var yaw:=atan2(-d.x,-d.y)
 var dims:=Vector3(float(cfg.width_m),float(cfg.height_m),float(cfg.depth_m))
 body=StaticBody3D.new();body.name="ServiceBar";body.collision_layer=1;body.collision_mask=0
 body.set_meta("source_geometry_id","WORKS_SERVICE_CROSSING_V1")
 body.position=center+Vector3.UP*dims.y*.5;body.rotation.y=yaw;add_child(body)
 var shape:=BoxShape3D.new();shape.size=dims
 var collider:=CollisionShape3D.new();collider.shape=shape;body.add_child(collider)
 var mesh:=BoxMesh.new();mesh.size=dims
 var visual:=MeshInstance3D.new();visual.mesh=mesh;visual.material_override=material(Color(cfg.color));visual.layers=3;body.add_child(visual)
 for n in ["ProbeLeft","ProbeRight","ProbeRear"]:gate.craft.get_node(n).add_exception(body)
 # Shallow amber bands on the near face keep the solid readable in gray light.
 for x in [-4.0,-2.0,0.0,2.0,4.0]:
  var band:=MeshInstance3D.new();var box:=BoxMesh.new();box.size=Vector3(.7,.72,.014);band.mesh=box;band.material_override=material(Color(cfg.accent));band.position=Vector3(x,0,dims.z*.5+.009);band.layers=3;body.add_child(band)
 var cap:=MeshInstance3D.new();var cover:=BoxMesh.new();cover.size=Vector3(dims.x-.3,.012,dims.z-.25);cap.mesh=cover;cap.material_override=material(Color("53615b"));cap.position.y=dims.y*.5+.007;cap.layers=3;body.add_child(cap)
 var warning_index:=maxi(0,i-int(float(cfg.warning_distance_m)/.25))
 var wp:=P1AWorldData.xz(points[warning_index])
 var label:=Label3D.new();label.text="WORKS\nSERVICE CROSSING";label.font_size=48;label.pixel_size=.014;label.modulate=Color(cfg.accent);label.outline_size=2;label.no_depth_test=false
 label.position=Vector3(wp.x,gate.data.terrain_height_at(wp.x,wp.y)+.06,wp.y);label.rotation=Vector3(-PI/2,yaw,0);add_child(label)
 set_meta("dimensions",dims);set_meta("route_sample",i)
func material(color: Color) -> StandardMaterial3D:
 var m:=StandardMaterial3D.new();m.albedo_color=color;m.roughness=.8;return m
