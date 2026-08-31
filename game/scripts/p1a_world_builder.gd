class_name P1AWorldBuilder
extends Node3D

const RENDER_SOLIDS_PATH := "res://presentation/generated/solid_render_meshes_v1_2_6.json"
const WALL_FACE_PRESENTATION_IDS := ["CORE_WALL", "OUTER_CLOSURE_MASK", "OUTER_WALL"]
const WALL_SIDE_LIGHTEN := 0.18
const WALL_TOP_LIGHTEN := 0.34
const WALL_BOTTOM_DARKEN := 0.08
const TERRAIN_RENDER_BOUNDARY_BLEND := 0.22
const TERRAIN_RENDER_SMOOTHABLE_CLASS_MAX := 9

const SURFACE_COLORS := {
	0: Color(0.085, 0.105, 0.12),
	1: Color(0.19, 0.24, 0.21),
	2: Color(0.24, 0.34, 0.38),
	3: Color(0.30, 0.31, 0.28),
	4: Color(0.26, 0.34, 0.27),
	5: Color(0.48, 0.32, 0.13),
	6: Color(0.52, 0.50, 0.42),
	7: Color(0.17, 0.22, 0.19),
	8: Color(0.28, 0.38, 0.41),
	9: Color(0.24, 0.40, 0.34),
	10: Color(0.85, 0.58, 0.16),
	11: Color(0.11, 0.13, 0.14),
}

var data: P1AWorldData
var _render_solids: Dictionary = {}
var _solid_convex_shapes: Array[ConvexPolygonShape3D] = []
var _hard_bodies: Array[StaticBody3D] = []


func build(source_data: P1AWorldData) -> void:
	data = source_data
	_render_solids = _load_render_solids()
	_build_terrain()
	_build_solids()
	_build_landmarks()
	_build_node_markers()


func _build_terrain() -> void:
	var grid: Dictionary = data.terrain_meta.grid
	var width := int(grid.vertex_count_x)
	var depth := int(grid.vertex_count_z)
	var spacing := float(grid.spacing_m)
	var origin := P1AWorldData.xz(grid.origin_xz_m)
	var vertices := PackedVector3Array()
	var normals := PackedVector3Array()
	var colors := PackedColorArray()
	vertices.resize(width * depth)
	normals.resize(width * depth)
	colors.resize(width * depth)
	for iz in depth:
		for ix in width:
			var index := iz * width + ix
			vertices[index] = Vector3(origin.x + float(ix) * spacing, data.height_at_index(index), origin.y + float(iz) * spacing)
			colors[index] = _terrain_render_color(ix, iz, width, depth)
	for iz in depth:
		for ix in width:
			var index := iz * width + ix
			var left := data.height_at_index(iz * width + maxi(ix - 1, 0))
			var right := data.height_at_index(iz * width + mini(ix + 1, width - 1))
			var back := data.height_at_index(maxi(iz - 1, 0) * width + ix)
			var front := data.height_at_index(mini(iz + 1, depth - 1) * width + ix)
			normals[index] = Vector3(left - right, 2.0 * spacing, back - front).normalized()
	var indices := PackedInt32Array()
	indices.resize((width - 1) * (depth - 1) * 6)
	var write := 0
	for iz in depth - 1:
		for ix in width - 1:
			var a := iz * width + ix
			var b := a + 1
			var c := a + width
			var d := c + 1
			# Both triangles use the frozen a->d diagonal and face upward.
			indices[write] = a; indices[write + 1] = d; indices[write + 2] = b
			indices[write + 3] = a; indices[write + 4] = c; indices[write + 5] = d
			write += 6
	var arrays := []
	arrays.resize(Mesh.ARRAY_MAX)
	arrays[Mesh.ARRAY_VERTEX] = vertices
	arrays[Mesh.ARRAY_NORMAL] = normals
	arrays[Mesh.ARRAY_COLOR] = colors
	arrays[Mesh.ARRAY_INDEX] = indices
	var mesh := ArrayMesh.new()
	mesh.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES, arrays)
	var material := StandardMaterial3D.new()
	material.vertex_color_use_as_albedo = true
	material.metallic = 0.0
	material.roughness = 0.88
	material.shading_mode = BaseMaterial3D.SHADING_MODE_PER_PIXEL
	material.transparency = BaseMaterial3D.TRANSPARENCY_DISABLED
	# The frozen heightfield collision is explicitly two-sided. Matching the
	# render consumer keeps aperture/support pixels visible without changing a
	# single source vertex, triangle, normal, or collision face.
	material.cull_mode = BaseMaterial3D.CULL_DISABLED
	mesh.surface_set_material(0, material)
	var visual := MeshInstance3D.new()
	visual.name = "FrozenHeightfieldVisual"
	visual.mesh = mesh
	add_child(visual)
	var body := StaticBody3D.new()
	body.name = "FrozenHeightfieldCollision"
	body.collision_layer = 1
	body.set_meta("source_geometry_id", "HEIGHTFIELD_SUPPORT")
	var shape_node := CollisionShape3D.new()
	var terrain_shape := mesh.create_trimesh_shape() as ConcavePolygonShape3D
	terrain_shape.backface_collision = true
	shape_node.shape = terrain_shape
	body.add_child(shape_node)
	add_child(body)


func _terrain_render_color(ix: int, iz: int, width: int, depth: int) -> Color:
	var index := iz * width + ix
	var surface_class := int(data.surface_bytes[index])
	var base: Color = SURFACE_COLORS.get(surface_class, Color.MAGENTA)
	if surface_class > TERRAIN_RENDER_SMOOTHABLE_CLASS_MAX:
		return base
	var different_neighbor_sum := Color(0.0, 0.0, 0.0, 0.0)
	var different_neighbor_count := 0
	for offset in [Vector2i(-1, 0), Vector2i(1, 0), Vector2i(0, -1), Vector2i(0, 1)]:
		var nx: int = ix + offset.x
		var nz: int = iz + offset.y
		if nx < 0 or nx >= width or nz < 0 or nz >= depth:
			continue
		var neighbor_class := int(data.surface_bytes[nz * width + nx])
		if neighbor_class > TERRAIN_RENDER_SMOOTHABLE_CLASS_MAX or neighbor_class == surface_class:
			continue
		different_neighbor_sum += SURFACE_COLORS.get(neighbor_class, Color.MAGENTA)
		different_neighbor_count += 1
	if different_neighbor_count == 0:
		return base
	var boundary_color := different_neighbor_sum / float(different_neighbor_count)
	boundary_color.a = base.a
	return base.lerp(boundary_color, TERRAIN_RENDER_BOUNDARY_BLEND)


func _build_solids() -> void:
	var mesh_ids: Array = data.solids.keys()
	mesh_ids.sort()
	for mesh_id_value in mesh_ids:
		var mesh_id := String(mesh_id_value)
		var record: Dictionary = data.solids[mesh_id]
		var render_record: Dictionary = _render_solids.get(mesh_id, {})
		assert(not render_record.is_empty(), "Missing canonical v1.2.6 render mesh: %s" % mesh_id)
		var source_id := String(record.source_geometry_id)
		var raw_vertices: Array = record.vertices_xyz_m
		var source_vertices := PackedVector3Array()
		source_vertices.resize(raw_vertices.size())
		for index in raw_vertices.size():
			var value: Array = raw_vertices[index]
			source_vertices[index] = Vector3(float(value[0]), float(value[1]), float(value[2]))
		var render_vertices := _packed_vectors(render_record.render_positions_xyz_m)
		var render_normals := _packed_vectors(render_record.render_normals_xyz)
		var indices := PackedInt32Array()
		var render_indices: Array = render_record.render_indices
		indices.resize(render_indices.size())
		for index in render_indices.size():
			indices[index] = int(render_indices[index])
		var triangles: Array = record.triangles
		var faces := PackedVector3Array()
		faces.resize(triangles.size() * 3)
		for triangle_index in triangles.size():
			var raw_indices: Array = triangles[triangle_index].indices
			for corner in 3:
				var vertex_index := int(raw_indices[corner])
				faces[triangle_index * 3 + corner] = source_vertices[vertex_index]
		var arrays := []
		arrays.resize(Mesh.ARRAY_MAX)
		arrays[Mesh.ARRAY_VERTEX] = render_vertices
		arrays[Mesh.ARRAY_NORMAL] = render_normals
		arrays[Mesh.ARRAY_INDEX] = indices
		if source_id in WALL_FACE_PRESENTATION_IDS:
			arrays[Mesh.ARRAY_COLOR] = _wall_face_colors(source_id, record, indices, render_vertices.size())
		var mesh := ArrayMesh.new()
		mesh.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES, arrays)
		var material := StandardMaterial3D.new()
		if source_id in WALL_FACE_PRESENTATION_IDS:
			material.albedo_color = Color.WHITE
			material.vertex_color_use_as_albedo = true
		else:
			material.albedo_color = _solid_color(source_id)
		# Every solid created below has an active collision peer. Rendering the
		# exact authored triangles from both sides keeps the visible surface in
		# parity with closed prisms and backface-enabled concave collision.
		material.cull_mode = BaseMaterial3D.CULL_DISABLED
		material.metallic = 0.0
		material.roughness = 0.74
		material.shading_mode = BaseMaterial3D.SHADING_MODE_PER_PIXEL
		material.transparency = BaseMaterial3D.TRANSPARENCY_DISABLED
		mesh.surface_set_material(0, material)
		var visual := MeshInstance3D.new()
		visual.name = "%s_Visual" % mesh_id
		visual.mesh = mesh
		add_child(visual)
		var body := StaticBody3D.new()
		body.name = "%s_Collision" % mesh_id
		body.collision_layer = 1
		body.set_meta("source_geometry_id", source_id)
		add_child(body)
		if source_id in ["CORE_PLINTH_MASK", "CORE_WALL", "HOP_BAR_01", "OUTER_CLOSURE_MASK", "OUTER_WALL"]:
			_hard_bodies.append(body)
			_add_exact_solid_prisms(body, record, source_vertices)
		else:
			var shape_node := CollisionShape3D.new()
			var shape := ConcavePolygonShape3D.new()
			shape.backface_collision = true
			shape.set_faces(faces)
			shape_node.shape = shape
			body.add_child(shape_node)


func _build_landmarks() -> void:
	for value in data.manifest.get("landmarks", []):
		var record: Dictionary = value
		var mesh: PrimitiveMesh
		if String(record.shape) == "CYLINDER":
			var cylinder := CylinderMesh.new()
			cylinder.top_radius = float(record.radius_m)
			cylinder.bottom_radius = float(record.radius_m)
			cylinder.height = float(record.height_m)
			mesh = cylinder
		else:
			var box := BoxMesh.new()
			box.size = Vector3(float(record.footprint_xz_m[0]), float(record.height_m), float(record.footprint_xz_m[1]))
			mesh = box
		var material := StandardMaterial3D.new()
		material.albedo_color = Color(0.72, 0.56, 0.26)
		material.roughness = 0.70
		mesh.material = material
		var visual := MeshInstance3D.new()
		visual.name = String(record.id)
		visual.mesh = mesh
		visual.position = Vector3(float(record.center_xz_m[0]), float(record.base_y_m) + float(record.height_m) * 0.5, float(record.center_xz_m[1]))
		add_child(visual)


func exclude_hard_geometry_from_support(craft: CraftController) -> void:
	for probe_name in ["ProbeLeft", "ProbeRight", "ProbeRear"]:
		var probe := craft.get_node(probe_name) as RayCast3D
		for body in _hard_bodies:
			probe.add_exception(body)


func _add_exact_solid_prisms(body: StaticBody3D, record: Dictionary, vertices: PackedVector3Array) -> void:
	if String(record.source_geometry_id) == "HOP_BAR_01":
		var exact_bar := ConvexPolygonShape3D.new()
		exact_bar.points = vertices
		_solid_convex_shapes.append(exact_bar)
		PhysicsServer3D.body_add_shape(body.get_rid(), exact_bar.get_rid())
		return
	var base_y := float(record.base_y_m)
	for triangle_value in record.triangles:
		var triangle: Dictionary = triangle_value
		if String(triangle.surface) != "TOP":
			continue
		var raw_indices: Array = triangle.indices
		var points := PackedVector3Array()
		points.resize(6)
		for corner in 3:
			var top := vertices[int(raw_indices[corner])]
			points[corner] = top
			points[corner + 3] = Vector3(top.x, base_y, top.z)
		var prism := ConvexPolygonShape3D.new()
		prism.points = points
		_solid_convex_shapes.append(prism)
		PhysicsServer3D.body_add_shape(body.get_rid(), prism.get_rid())


func _build_node_markers() -> void:
	for node_id_value in data.manifest.nodes:
		var node_id := String(node_id_value)
		var record: Dictionary = data.manifest.nodes[node_id]
		var marker := MeshInstance3D.new()
		marker.name = "%s_Marker" % node_id
		var material := StandardMaterial3D.new()
		material.albedo_color = Color(0.95, 0.68, 0.18) if String(record.kind) == "GATE" else Color(0.20, 0.80, 0.68)
		material.emission_enabled = true
		material.emission = material.albedo_color * 0.10
		material.roughness = 0.58
		material.cull_mode = BaseMaterial3D.CULL_DISABLED
		marker.mesh = _node_marker_mesh(material)
		marker.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		marker.position = Vector3(float(record.xz_m[0]), float(record.elevation_m) + 0.12, float(record.xz_m[1]))
		add_child(marker)


func _node_marker_mesh(material: StandardMaterial3D) -> ArrayMesh:
	const SEGMENTS := 40
	# The outer band includes the frozen A1 GW owner ray at radius 2.421 m;
	# the center keeps the frozen free-roam MRK owner ray at radius 0.314 m.
	const OUTER_RADIUS := 2.65
	const INNER_RADIUS := 2.0
	const CENTER_RADIUS := 0.46
	var vertices := PackedVector3Array()
	var normals := PackedVector3Array()
	for segment in SEGMENTS:
		var next := (segment + 1) % SEGMENTS
		var angle_a := TAU * float(segment) / float(SEGMENTS)
		var angle_b := TAU * float(next) / float(SEGMENTS)
		var outer_a := Vector3(cos(angle_a) * OUTER_RADIUS, 0.0, sin(angle_a) * OUTER_RADIUS)
		var outer_b := Vector3(cos(angle_b) * OUTER_RADIUS, 0.0, sin(angle_b) * OUTER_RADIUS)
		var inner_a := Vector3(cos(angle_a) * INNER_RADIUS, 0.0, sin(angle_a) * INNER_RADIUS)
		var inner_b := Vector3(cos(angle_b) * INNER_RADIUS, 0.0, sin(angle_b) * INNER_RADIUS)
		var center_a := Vector3(cos(angle_a) * CENTER_RADIUS, 0.0, sin(angle_a) * CENTER_RADIUS)
		var center_b := Vector3(cos(angle_b) * CENTER_RADIUS, 0.0, sin(angle_b) * CENTER_RADIUS)
		for point in [outer_a, inner_b, inner_a, outer_a, outer_b, inner_b, Vector3.ZERO, center_b, center_a]:
			vertices.append(point)
			normals.append(Vector3.UP)
	var arrays := []
	arrays.resize(Mesh.ARRAY_MAX)
	arrays[Mesh.ARRAY_VERTEX] = vertices
	arrays[Mesh.ARRAY_NORMAL] = normals
	var mesh := ArrayMesh.new()
	mesh.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES, arrays)
	mesh.surface_set_material(0, material)
	return mesh


func _solid_color(source_id: String) -> Color:
	if source_id.begins_with("B"):
		return Color(0.48, 0.52, 0.58)
	if source_id == "HOP_BAR_01":
		return Color(0.82, 0.44, 0.10)
	if source_id == "OUTER_CLOSURE_MASK":
		return Color(0.39615000, 0.43785000, 0.45870000)
	if source_id == "OUTER_WALL":
		return Color(0.44, 0.47, 0.50)
	if source_id == "CORE_PLINTH_MASK":
		return Color(0.54, 0.58, 0.63)
	return Color(0.70650000, 0.74182500, 0.80070000)


func _wall_face_colors(source_id: String, record: Dictionary, render_indices: PackedInt32Array, vertex_count: int) -> PackedColorArray:
	var base := _solid_color(source_id)
	var face_colors := {
		"BOTTOM": base.darkened(WALL_BOTTOM_DARKEN),
		"SIDE": base.lightened(WALL_SIDE_LIGHTEN),
		"TOP": base.lightened(WALL_TOP_LIGHTEN),
	}
	var colors := PackedColorArray()
	colors.resize(vertex_count)
	colors.fill(base)
	var roles := PackedInt32Array()
	roles.resize(vertex_count)
	roles.fill(-1)
	var triangles: Array = record.triangles
	assert(render_indices.size() == triangles.size() * 3)
	for triangle_index in triangles.size():
		var surface := String(triangles[triangle_index].surface)
		assert(face_colors.has(surface), "Unknown solid face class: %s" % surface)
		var role := 0 if surface == "BOTTOM" else (1 if surface == "SIDE" else 2)
		for corner in 3:
			var vertex_index := render_indices[triangle_index * 3 + corner]
			assert(roles[vertex_index] == -1 or roles[vertex_index] == role, "Canonical render vertex crosses wall face classes")
			roles[vertex_index] = role
			colors[vertex_index] = face_colors[surface]
	return colors


func _load_render_solids() -> Dictionary:
	var parsed = JSON.parse_string(FileAccess.get_file_as_string(RENDER_SOLIDS_PATH))
	assert(parsed is Dictionary, "Canonical v1.2.6 render mesh artifact is unreadable")
	var artifact: Dictionary = parsed
	assert(String(artifact.get("presentation_overlay_authority_version", "")) == "v1.2.6")
	var meshes = artifact.get("meshes", {})
	assert(meshes is Dictionary and meshes.size() == 19)
	return meshes


static func _packed_vectors(values: Array) -> PackedVector3Array:
	var packed := PackedVector3Array()
	packed.resize(values.size())
	for index in values.size():
		var value: Array = values[index]
		packed[index] = Vector3(float(value[0]), float(value[1]), float(value[2]))
	return packed
