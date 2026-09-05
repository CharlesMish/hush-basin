extends RefCounted

const MIN_DECORATIVE_EDGE_M := 0.0001

static func drawable_edge(edge: Array) -> bool:
	# Keep the threshold in the source data's double precision, before Vector2
	# storage rounds coordinates to the engine's single-precision real_t.
	var dx := float(edge[1][0]) - float(edge[2][0])
	var dz := float(edge[1][1]) - float(edge[2][1])
	return sqrt(dx * dx + dz * dz) >= MIN_DECORATIVE_EDGE_M
## Static presentation, batched by primitive. Nothing here reads input or writes
## craft state. Reachable solid volumes are owned by the shared world geometry.

var boxes: Array = []
var cylinders: Array = []
var palette: Dictionary
var band_vertices := PackedVector3Array()
var band_normals := PackedVector3Array()
var band_colors := PackedColorArray()

func color(key: String) -> Color:
	var c: Array = palette[key]
	return Color(c[0], c[1], c[2])

func box(p: Vector3, size: Vector3, key: String, yaw: float = 0.0) -> void:
	boxes.append([Transform3D(Basis(Vector3.UP, yaw) * Basis.from_scale(size), p), color(key)])

func cylinder(p: Vector3, radius: float, height: float, key: String) -> void:
	cylinders.append([Transform3D(Basis.IDENTITY.scaled(Vector3(radius * 2, height, radius * 2)), p), color(key)])

func build(world: Node3D, data: P1AWorldData) -> void:
	palette = data.polish_config.palette
	var detail: Dictionary = data.polish_config.detail
	# Remaining walls: real edges from the clipped data, with top coping and a
	# narrow recessed panel seam. Tall foundation sides read as retaining faces.
	var counts: Dictionary = {}
	var phases: Dictionary = {}
	for e in data.polish.wall_edges:
		var family := String(e[0])
		var a := Vector3(float(e[1][0]), 0, float(e[1][1]))
		var b := Vector3(float(e[2][0]), 0, float(e[2][1]))
		var length := a.distance_to(b)
		if not drawable_edge(e):
			continue
		var along := (b - a).normalized()
		var outward := Vector3(along.z, 0, -along.x)
		var yaw := atan2(-along.z, along.x)
		var top := float(e[3])
		a += outward * float(detail.wall_detail_offset_m)
		b += outward * float(detail.wall_detail_offset_m)
		band(a, b, top * float(detail.wall_band_relative_height), float(detail.wall_band_height_m), outward, "steel")
		band(a, b, top - float(detail.cap_band_height_m) * 0.5, float(detail.cap_band_height_m), outward, "trim")
		# Sample by accumulated boundary length, including finely tessellated
		# curves. The old per-edge 8 m filter omitted almost every sweep face.
		var phase := float(phases.get(family, 0.0))
		var used := int(counts.get(family, 0))
		var spacing := float(detail.panel_spacing_m)
		var next := spacing - phase
		while next < length:
			if used < int(detail.max_wall_panels) / 4:
				var p := a + along * next
				box(Vector3(p.x, top * 0.5, p.z), Vector3(float(detail.panel_width_m), top - 0.3, 0.02), "steel", yaw)
				used += 1
			next += spacing
		phases[family] = fmod(phase + length, spacing)
		counts[family] = used
	var presentation := Node3D.new()
	presentation.name = "WorldPolishArchitecture"
	world.add_child(presentation)
	var band_mesh := ArrayMesh.new()
	var arrays := []
	arrays.resize(Mesh.ARRAY_MAX)
	arrays[Mesh.ARRAY_VERTEX] = band_vertices
	arrays[Mesh.ARRAY_NORMAL] = band_normals
	arrays[Mesh.ARRAY_COLOR] = band_colors
	band_mesh.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES, arrays)
	var band_material := StandardMaterial3D.new()
	band_material.vertex_color_use_as_albedo = true
	band_material.roughness = 0.85
	band_material.cull_mode = BaseMaterial3D.CULL_DISABLED
	var bands := MeshInstance3D.new()
	bands.name = "RetainingWallBands"
	bands.mesh = band_mesh
	bands.material_override = band_material
	bands.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	presentation.add_child(bands)
	var cube := BoxMesh.new()
	cube.size = Vector3.ONE
	batch(presentation, "ConcreteAndMetalDetails", cube, boxes)
	var round_mesh := CylinderMesh.new()
	round_mesh.top_radius = 0.5
	round_mesh.bottom_radius = 0.5
	round_mesh.height = 1.0
	round_mesh.radial_segments = 16
	batch(presentation, "MastAndStackDetails", round_mesh, cylinders)

func band(a: Vector3, b: Vector3, y: float, height: float, normal: Vector3, key: String) -> void:
	var low := Vector3.UP * (y - height * 0.5)
	var high := Vector3.UP * (y + height * 0.5)
	for v in [a + low, b + low, b + high, a + low, b + high, a + high]:
		band_vertices.append(v)
		band_normals.append(normal)
		band_colors.append(color(key))

func batch(parent: Node3D, name: String, mesh: Mesh, instances: Array) -> void:
	if instances.is_empty():
		return
	var material := StandardMaterial3D.new()
	material.vertex_color_use_as_albedo = true
	material.roughness = 0.82
	var mm := MultiMesh.new()
	mm.transform_format = MultiMesh.TRANSFORM_3D
	mm.use_colors = true
	mm.mesh = mesh
	mm.instance_count = instances.size()
	for i in instances.size():
		mm.set_instance_transform(i, instances[i][0])
		mm.set_instance_color(i, instances[i][1])
	var node := MultiMeshInstance3D.new()
	node.name = name
	node.multimesh = mm
	node.material_override = material
	parent.add_child(node)

func environment(gate: Node3D, data: P1AWorldData) -> void:
	palette = data.polish_config.palette
	var env: Environment = gate.get_node("WorldEnvironment").environment
	var sky_material := ProceduralSkyMaterial.new()
	sky_material.sky_top_color = color("sky_top")
	sky_material.sky_horizon_color = color("sky_horizon")
	sky_material.ground_horizon_color = color("sky_horizon")
	sky_material.ground_bottom_color = color("ground")
	var light: Dictionary = data.polish_config.lighting
	sky_material.sky_curve = float(light.sky_curve)
	sky_material.sun_angle_max = 0.0
	var sky := Sky.new()
	sky.sky_material = sky_material
	env.sky = sky
	var ambient: Array = light.ambient_color
	env.ambient_light_color = Color(ambient[0], ambient[1], ambient[2])
	env.ambient_light_energy = float(light.ambient_energy)
	var sun: DirectionalLight3D = gate.get_node("Sun")
	var angles: Array = light.sun_rotation_degrees
	var sunlight: Array = light.sun_color
	sun.rotation_degrees = Vector3(angles[0], angles[1], angles[2])
	sun.light_color = Color(sunlight[0], sunlight[1], sunlight[2])
	sun.light_energy = float(light.sun_energy)
