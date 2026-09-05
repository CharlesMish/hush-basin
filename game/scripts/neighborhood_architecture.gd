extends RefCounted
## One generated primitive definition drives each structural visual and collider.
const CONFIG := "res://presentation/neighborhood_v1.json"
const DATA := "res://presentation/generated/neighborhood_v1.json"
const INDEX := "res://presentation/generated/neighborhood_v1_index.json"

func build(world: Node3D) -> void:
	var cfg: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(CONFIG))
	var index: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(INDEX))
	assert(FileAccess.get_sha256(CONFIG) == index.config_sha256)
	assert(FileAccess.get_sha256(DATA) == index.sha256)
	var data: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(DATA))
	var parent := Node3D.new()
	parent.name = "WorkingNeighborhood"
	parent.set_meta("definition", data)
	world.add_child(parent)
	var bodies: Dictionary = {}
	for owner in data.owners:
		var body := StaticBody3D.new()
		body.name = owner.id
		body.collision_layer = 1
		body.set_meta("source_geometry_id", owner.id)
		parent.add_child(body)
		bodies[owner.id] = body
	var groups: Dictionary = {}
	for p in data.parts:
		var size := Vector3(p.size[0], p.size[1], p.size[2])
		var origin := Vector3(p.p[0], p.p[1], p.p[2])
		var rotation := Basis(Vector3.UP, float(p.yaw))
		var transform := Transform3D(rotation * Basis.from_scale(size), origin)
		var key := "%s_%s_%s" % [p.kind, p.emission, p.solid]
		if not groups.has(key):
			groups[key] = []
		groups[key].append([transform, p.color])
		if p.solid:
			var node := CollisionShape3D.new()
			if p.kind == "cylinder":
				var shape := CylinderShape3D.new()
				shape.radius = size.x * 0.5
				shape.height = size.y
				node.shape = shape
			else:
				var shape := BoxShape3D.new()
				shape.size = size
				node.shape = shape
			node.transform = Transform3D(rotation, origin)
			node.set_meta("definition_index", data.parts.find(p))
			bodies[p.owner].add_child(node)
	for key in groups:
		var rows: Array = groups[key]
		var mesh: PrimitiveMesh
		if String(key).begins_with("cylinder"):
			var cylinder := CylinderMesh.new()
			cylinder.top_radius = 0.5
			cylinder.bottom_radius = 0.5
			cylinder.height = 1.0
			cylinder.radial_segments = 24
			mesh = cylinder
		else:
			var cube := BoxMesh.new()
			cube.size = Vector3.ONE
			mesh = cube
		var material := StandardMaterial3D.new()
		material.vertex_color_use_as_albedo = true
		material.vertex_color_is_srgb = true
		material.roughness = float(cfg.modules.roughness)
		if "true" in String(key).split("_")[1]:
			material.emission_enabled = true
			material.emission = Color(0.70, 0.53, 0.29)
			material.emission_energy_multiplier = float(cfg.modules.window_emission)
		var mm := MultiMesh.new()
		mm.transform_format = MultiMesh.TRANSFORM_3D
		mm.use_colors = true
		mm.mesh = mesh
		mm.instance_count = rows.size()
		for i in rows.size():
			mm.set_instance_transform(i, rows[i][0])
			var c: Array = cfg.palette[rows[i][1]]
			mm.set_instance_color(i, Color(c[0], c[1], c[2]))
		var node := MultiMeshInstance3D.new()
		node.name = "Architecture_" + String(key)
		node.multimesh = mm
		node.material_override = material
		# Explicitly join the unchanged static precipitation mask, including
		# MultiMesh geometry which the older mesh-only scanner does not visit.
		node.layers = 3
		if not String(key).ends_with("true"):
			node.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		parent.add_child(node)
	for p in data.labels:
		var label := Label3D.new()
		label.name = "Sign_" + String(p.owner)
		label.text = p.text
		label.font_size = 64
		label.pixel_size = minf(0.013, float(p.width_m) / maxf(1.0, float(String(p.text).length()) * 40.0))
		label.outline_size = 0
		label.modulate = Color(0.85, 0.82, 0.67)
		label.position = Vector3(p.p[0], p.p[1], p.p[2])
		label.rotation.y = float(p.yaw)
		label.no_depth_test = false
		parent.add_child(label)
