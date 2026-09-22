extends RefCounted
## Additive, fixed presentation. No physics objects or gameplay callbacks.
const CONFIG := "res://presentation/world_identity_detail_v2.json"
const DATA := "res://presentation/generated/world_identity_detail_v2.json"

func build(world: Node3D, data: P1AWorldData) -> void:
	var cfg: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(CONFIG))
	var definition: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(DATA))
	assert(definition.config_sha256 == FileAccess.get_sha256(CONFIG))
	var parent := Node3D.new()
	parent.name = "WorldIdentityDetailV2"
	parent.set_meta("presentation_identity", cfg.version)
	parent.set_meta("definition", definition)
	world.add_child(parent)
	var groups: Dictionary = {}
	for part in definition.parts:
		var key := String(part.district) + "_" + String(part.kind)
		if not groups.has(key):
			groups[key] = []
		groups[key].append(part)
	for key in groups:
		var rows: Array = groups[key]
		var mesh: PrimitiveMesh
		if String(key).ends_with("cylinder"):
			var cylinder := CylinderMesh.new()
			cylinder.top_radius = 0.5
			cylinder.bottom_radius = 0.5
			cylinder.height = 1.0
			cylinder.radial_segments = 12
			mesh = cylinder
		else:
			var cube := BoxMesh.new()
			cube.size = Vector3.ONE
			mesh = cube
		var mm := MultiMesh.new()
		mm.transform_format = MultiMesh.TRANSFORM_3D
		mm.use_colors = true
		mm.mesh = mesh
		mm.instance_count = rows.size()
		for i in rows.size():
			var p: Dictionary = rows[i]
			var basis := Basis.from_euler(Vector3(p.rotation[0],p.rotation[1],p.rotation[2])) * Basis.from_scale(Vector3(p.size[0],p.size[1],p.size[2]))
			mm.set_instance_transform(i,Transform3D(basis,Vector3(p.p[0],p.p[1],p.p[2])))
			mm.set_instance_color(i, tint(cfg,p.color))
		var node := MultiMeshInstance3D.new()
		node.name = String(key)
		node.multimesh = mm
		node.material_override = material(cfg)
		# The unchanged particle-only heightfield sees roof equipment too.
		node.layers = 3
		node.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		parent.add_child(node)
	for p in definition.labels:
		var label := Label3D.new()
		label.name = "Identifier_" + String(p.owner)
		label.text = p.text
		label.font_size = 64
		label.pixel_size = minf(float(p.height)/64.0,float(p.width)/(maxf(1,String(p.text).length())*40.0))
		label.outline_size = 0
		label.modulate = tint(cfg,"letter")
		label.position = Vector3(p.p[0],p.p[1],p.p[2])
		label.rotation.y = p.yaw
		parent.add_child(label)
	build_bands(parent,data,cfg)

func tint(cfg: Dictionary, key: String) -> Color:
	var c: Array = cfg.palette[key]
	return Color(c[0],c[1],c[2])

func material(cfg: Dictionary) -> StandardMaterial3D:
	var mat := StandardMaterial3D.new()
	mat.vertex_color_use_as_albedo = true
	mat.vertex_color_is_srgb = true
	mat.roughness = cfg.roughness
	return mat

func build_bands(parent: Node3D, data: P1AWorldData, cfg: Dictionary) -> void:
	var vertices := PackedVector3Array()
	var normals := PackedVector3Array()
	var colors := PackedColorArray()
	var transition: Dictionary = cfg.transitions
	for e in data.polish.wall_edges:
		if String(e[0]) == "OUTER_WALL" or not preload("res://scripts/world_polish_presentation.gd").drawable_edge(e):
			continue
		var a := Vector3(e[1][0],0,e[1][1])
		var b := Vector3(e[2][0],0,e[2][1])
		var midpoint := (a+b)*0.5
		var best := 1.0
		var district := ""
		for area in transition.areas:
			var ratio := Vector2(midpoint.x,midpoint.z).distance_to(Vector2(area.center[0],area.center[1]))/float(area.radius)
			if ratio < best:
				best = ratio
				district = area.district
		if district.is_empty():
			continue
		var along := (b-a).normalized()
		var normal := Vector3(along.z,0,-along.x)
		a += normal*float(transition.offset_m)
		b += normal*float(transition.offset_m)
		var y := float(e[3])-float(transition.height_below_top_m)
		var hh := float(transition.band_height_m)*0.5
		var c := tint(cfg,district).lerp(tint(cfg,"repair"),best*0.65)
		for v in [Vector3(a.x,y-hh,a.z),Vector3(b.x,y+hh,b.z),Vector3(b.x,y-hh,b.z),Vector3(a.x,y-hh,a.z),Vector3(a.x,y+hh,a.z),Vector3(b.x,y+hh,b.z)]:
			vertices.append(v)
			normals.append(normal)
			colors.append(c)
	var arrays := []
	arrays.resize(Mesh.ARRAY_MAX)
	arrays[Mesh.ARRAY_VERTEX] = vertices
	arrays[Mesh.ARRAY_NORMAL] = normals
	arrays[Mesh.ARRAY_COLOR] = colors
	var mesh := ArrayMesh.new()
	mesh.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES,arrays)
	var node := MeshInstance3D.new()
	node.name = "DistrictServiceBands"
	node.mesh = mesh
	var mat := material(cfg)
	mat.cull_mode = BaseMaterial3D.CULL_DISABLED
	node.material_override = mat
	node.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	parent.add_child(node)
