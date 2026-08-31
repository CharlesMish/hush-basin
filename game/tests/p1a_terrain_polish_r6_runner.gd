extends SceneTree

const MAIN_SCENE := preload("res://scenes/district_zero_p1a.tscn")
const EXACT_ENGINE := "4.7.1.stable.official.a13da4feb"
const HEIGHT_SHA := "f377a1034406ee2f35232c01f6cb80be8dd43d13267e3821d1edcab9a9735b88"
const SURFACE_SHA := "3d7466384a52bb8033e5fad5acd014a2daedec76475d5ad21ff13a94cee73949"
const COLOR_STORAGE_TOLERANCE := 0.0041

var checks: Array[Dictionary] = []
var failures: Array[String] = []


func _initialize() -> void:
	call_deferred("_run")


func _run() -> void:
	_record("EXACT_ENGINE", _engine_identity() == EXACT_ENGINE, _engine_identity())
	_record("HEIGHT_BYTES_FROZEN", FileAccess.get_sha256("res://world/generated/heightfield_i16le.bin") == HEIGHT_SHA)
	_record("SURFACE_CLASS_BYTES_FROZEN", FileAccess.get_sha256("res://world/generated/surface_classes_u8.bin") == SURFACE_SHA)
	var gate := MAIN_SCENE.instantiate() as P1AWorldGate
	root.add_child(gate)
	await process_frame
	gate.craft.set_physics_process(false)
	gate.telemetry.set_physics_process(false)
	var grid: Dictionary = gate.data.terrain_meta.grid
	var width := int(grid.vertex_count_x)
	var depth := int(grid.vertex_count_z)
	var spacing := float(grid.spacing_m)
	var origin := P1AWorldData.xz(grid.origin_xz_m)
	var visual := gate.world.get_node("FrozenHeightfieldVisual") as MeshInstance3D
	var arrays := visual.mesh.surface_get_arrays(0)
	var vertices: PackedVector3Array = arrays[Mesh.ARRAY_VERTEX]
	var normals: PackedVector3Array = arrays[Mesh.ARRAY_NORMAL]
	var colors: PackedColorArray = arrays[Mesh.ARRAY_COLOR]
	var indices: PackedInt32Array = arrays[Mesh.ARRAY_INDEX]
	var expected_samples := width * depth
	_record("TERRAIN_VERTEX_COUNT_FROZEN", vertices.size() == expected_samples, {"observed": vertices.size(), "expected": expected_samples})
	_record("TERRAIN_NORMAL_COUNT_FROZEN", normals.size() == expected_samples)
	_record("TERRAIN_COLOR_COUNT_FROZEN", colors.size() == expected_samples)
	_record("TERRAIN_INDEX_COUNT_FROZEN", indices.size() == (width - 1) * (depth - 1) * 6, indices.size())
	var maximum_position_delta := 0.0
	var maximum_color_delta := 0.0
	var changed_boundary_vertices := 0
	var protected_color_mismatches := 0
	var interior_color_mismatches := 0
	for iz in depth:
		for ix in width:
			var index := iz * width + ix
			var expected_position := Vector3(origin.x + float(ix) * spacing, gate.data.height_at_index(index), origin.y + float(iz) * spacing)
			var position_delta := (vertices[index] - expected_position).abs()
			maximum_position_delta = maxf(maximum_position_delta, maxf(position_delta.x, maxf(position_delta.y, position_delta.z)))
			var surface_class := int(gate.data.surface_bytes[index])
			var base: Color = P1AWorldBuilder.SURFACE_COLORS.get(surface_class, Color.MAGENTA)
			var expected_color := _expected_color(gate.data.surface_bytes, ix, iz, width, depth)
			var delta := _color_delta(colors[index], expected_color)
			maximum_color_delta = maxf(maximum_color_delta, delta)
			if surface_class > P1AWorldBuilder.TERRAIN_RENDER_SMOOTHABLE_CLASS_MAX and _color_delta(colors[index], base) > COLOR_STORAGE_TOLERANCE:
				protected_color_mismatches += 1
			if expected_color.is_equal_approx(base):
				if _color_delta(colors[index], base) > COLOR_STORAGE_TOLERANCE:
					interior_color_mismatches += 1
			elif _color_delta(colors[index], base) > COLOR_STORAGE_TOLERANCE:
				changed_boundary_vertices += 1
	_record("TERRAIN_POSITIONS_FROZEN", maximum_position_delta == 0.0, maximum_position_delta)
	_record("DETERMINISTIC_EXPECTED_RENDER_COLORS", maximum_color_delta <= COLOR_STORAGE_TOLERANCE, maximum_color_delta)
	_record("PROTECTED_GATE_HARD_COLORS_EXACT", protected_color_mismatches == 0, protected_color_mismatches)
	_record("SAME_CLASS_INTERIORS_EXACT", interior_color_mismatches == 0, interior_color_mismatches)
	_record("ORDINARY_BOUNDARIES_ACTUALLY_SMOOTHED", changed_boundary_vertices > 0, changed_boundary_vertices)
	var collision := gate.world.get_node("FrozenHeightfieldCollision") as StaticBody3D
	var shape_node := collision.get_child(0) as CollisionShape3D
	var terrain_shape := shape_node.shape as ConcavePolygonShape3D
	_record("TERRAIN_COLLISION_CONSUMER_FROZEN", PhysicsServer3D.body_get_shape_count(collision.get_rid()) == 1 and terrain_shape.backface_collision)
	var result := {
		"schema": "district_zero.p1a.terrain_polish_r6_behavior.v1",
		"status": "PASS" if failures.is_empty() else "FAIL",
		"engine_identity": _engine_identity(),
		"blend": P1AWorldBuilder.TERRAIN_RENDER_BOUNDARY_BLEND,
		"changed_boundary_vertices": changed_boundary_vertices,
		"checks": checks,
		"failure_count": failures.size(),
		"failures": failures,
	}
	print("P1A_TERRAIN_POLISH_R6_RESULT " + JSON.stringify(result))
	gate.queue_free()
	await process_frame
	quit(0 if failures.is_empty() else 1)


func _expected_color(surface_bytes: PackedByteArray, ix: int, iz: int, width: int, depth: int) -> Color:
	var surface_class := int(surface_bytes[iz * width + ix])
	var base: Color = P1AWorldBuilder.SURFACE_COLORS.get(surface_class, Color.MAGENTA)
	if surface_class > P1AWorldBuilder.TERRAIN_RENDER_SMOOTHABLE_CLASS_MAX:
		return base
	var total := Color(0.0, 0.0, 0.0, 0.0)
	var count := 0
	for offset in [Vector2i(-1, 0), Vector2i(1, 0), Vector2i(0, -1), Vector2i(0, 1)]:
		var nx: int = ix + offset.x
		var nz: int = iz + offset.y
		if nx < 0 or nx >= width or nz < 0 or nz >= depth:
			continue
		var neighbor_class := int(surface_bytes[nz * width + nx])
		if neighbor_class > P1AWorldBuilder.TERRAIN_RENDER_SMOOTHABLE_CLASS_MAX or neighbor_class == surface_class:
			continue
		total += P1AWorldBuilder.SURFACE_COLORS.get(neighbor_class, Color.MAGENTA)
		count += 1
	if count == 0:
		return base
	var target := total / float(count)
	target.a = base.a
	return base.lerp(target, P1AWorldBuilder.TERRAIN_RENDER_BOUNDARY_BLEND)


func _color_delta(a: Color, b: Color) -> float:
	return maxf(absf(a.r - b.r), maxf(absf(a.g - b.g), maxf(absf(a.b - b.b), absf(a.a - b.a))))


func _record(id: String, passed: bool, detail = null) -> void:
	checks.append({"id": id, "status": "PASS" if passed else "FAIL", "detail": detail})
	if not passed:
		failures.append(id)


func _engine_identity() -> String:
	var info := Engine.get_version_info()
	return "%d.%d.%d.%s.%s.%s" % [
		int(info.get("major", 0)), int(info.get("minor", 0)), int(info.get("patch", 0)),
		String(info.get("status", "")), String(info.get("build", "")),
		String(info.get("hash", "")).substr(0, 9),
	]
