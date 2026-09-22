extends Node3D
## One physical rooftop lantern, anchored to existing authoritative architecture.
var manifest: Dictionary
var crown_center := Vector3.ZERO
var _batches: Dictionary={}
func _ready() -> void:
	name="MarketHomeLantern"
	var config: Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://presentation/market_lantern.json"))
	var owner: Dictionary={}
	for item in manifest.landmarks:
		if item.id==config.owner:owner=item
	assert(not owner.is_empty())
	var ground:=Vector3(float(owner.center_xz_m[0]),float(owner.base_y_m)+float(owner.height_m)+float(config.roof_offset_m),float(owner.center_xz_m[1]))
	var steel:=material(Color(config.steel))
	var teal:=material(Color(config.market))
	var warm:=material(Color(config.warm),float(config.emission_energy))
	var rise:=float(config.mast_rise_m)
	var radius:=float(config.crown_radius_m)
	var height:=float(config.crown_height_m)
	crown_center=ground+Vector3.UP*rise
	beam(ground,ground+Vector3.UP*(rise+height*.5),float(config.mast_radius_m),steel)
	for i in 8:
		var angle:=i*TAU/8
		var next:=(i+1)*TAU/8
		var p:=crown_center+Vector3(cos(angle)*radius,0,sin(angle)*radius)
		var q:=crown_center+Vector3(cos(next)*radius,0,sin(next)*radius)
		beam(p,q,.16,warm)
		beam(p+Vector3.UP*height,q+Vector3.UP*height,.12,teal)
		beam(p,p+Vector3.UP*height,.095,steel)
		beam(ground+Vector3.UP*(rise-2),p,.09,steel)
		if i%2==0:beam(p+Vector3.UP*.35,p+Vector3.UP*(height-.35),.17,warm)
	set_meta("presentation_identity",config.identity)
	set_meta("collision_free",true)
	# Three native material batches keep the small skyline addition inexpensive.
	for mat in _batches:
		var transforms: Array=_batches[mat]
		var unit:=CylinderMesh.new()
		unit.top_radius=1;unit.bottom_radius=1;unit.height=1;unit.radial_segments=8
		var instances:=MultiMesh.new();instances.transform_format=MultiMesh.TRANSFORM_3D;instances.mesh=unit;instances.instance_count=transforms.size()
		for i in transforms.size():instances.set_instance_transform(i,transforms[i])
		var batch:=MultiMeshInstance3D.new();batch.multimesh=instances;batch.material_override=mat;batch.layers=3;add_child(batch)
func material(color: Color, emission: float=0.0) -> StandardMaterial3D:
	var result:=StandardMaterial3D.new()
	result.albedo_color=color;result.roughness=.72
	if emission>0:
		result.emission_enabled=true;result.emission=color;result.emission_energy_multiplier=emission
	return result
func beam(a: Vector3,b: Vector3,radius: float,mat: Material) -> void:
	var up:=(b-a).normalized()
	var right:=up.cross(Vector3.FORWARD).normalized()
	if right.length_squared()<.1:right=up.cross(Vector3.RIGHT).normalized()
	var basis:=Basis(right*radius,up*a.distance_to(b),right.cross(up).normalized()*radius)
	if not _batches.has(mat):_batches[mat]=[]
	_batches[mat].append(Transform3D(basis,(a+b)*.5))
