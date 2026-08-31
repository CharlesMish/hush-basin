extends SceneTree

const WALL_IDS := {
	"MESH_CORE_WALL": "CORE_WALL",
	"MESH_OUTER_CLOSURE": "OUTER_CLOSURE_MASK",
	"MESH_OUTER_WALL": "OUTER_WALL",
}

var failures: Array[String] = []
var checks: Array[Dictionary] = []


func _initialize() -> void:
	call_deferred("_run")


func _run() -> void:
	await _test_wall_face_presentation()
	await _test_solid_render_collision_parity()
	await _test_camera_obstruction()
	var result := {
		"schema": "district_zero.p1a.visibility_repair_test_result.v1",
		"status": "PASS" if failures.is_empty() else "FAIL",
		"checks": checks,
		"failure_count": failures.size(),
		"failures": failures,
	}
	print("P1A_VISIBILITY_REPAIR_RESULT " + JSON.stringify(result))
	quit(0 if failures.is_empty() else 1)


func _record(id: String, passed: bool, detail = null) -> void:
	checks.append({"id": id, "status": "PASS" if passed else "FAIL", "detail": detail})
	if not passed:
		failures.append(id + (": " + str(detail) if detail != null else ""))


func _test_wall_face_presentation() -> void:
	var scene := load("res://scenes/district_zero_p1a.tscn") as PackedScene
	var gate := scene.instantiate()
	root.add_child(gate)
	await process_frame
	await physics_frame
	var artifact = JSON.parse_string(FileAccess.get_file_as_string("res://presentation/generated/solid_render_meshes_v1_2_6.json"))
	for mesh_name in WALL_IDS:
		var node := gate.get_node("World/" + mesh_name + "_Visual") as MeshInstance3D
		var arrays := node.mesh.surface_get_arrays(0)
		var record: Dictionary = artifact.meshes[mesh_name]
		var expected_positions := _packed_vectors(record.render_positions_xyz_m)
		var expected_normals := _packed_vectors(record.render_normals_xyz)
		var expected_indices := PackedInt32Array(record.render_indices)
		var baseline_arrays := []
		baseline_arrays.resize(Mesh.ARRAY_MAX)
		baseline_arrays[Mesh.ARRAY_VERTEX] = expected_positions
		baseline_arrays[Mesh.ARRAY_NORMAL] = expected_normals
		baseline_arrays[Mesh.ARRAY_INDEX] = expected_indices
		var baseline_mesh := ArrayMesh.new()
		baseline_mesh.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES, baseline_arrays)
		var baseline_runtime_arrays := baseline_mesh.surface_get_arrays(0)
		var baseline_runtime_normals: PackedVector3Array = baseline_runtime_arrays[Mesh.ARRAY_NORMAL]
		var positions: PackedVector3Array = arrays[Mesh.ARRAY_VERTEX]
		var normals: PackedVector3Array = arrays[Mesh.ARRAY_NORMAL]
		var indices: PackedInt32Array = arrays[Mesh.ARRAY_INDEX]
		var colors: PackedColorArray = arrays[Mesh.ARRAY_COLOR]
		var material := node.mesh.surface_get_material(0) as StandardMaterial3D
		_record(mesh_name + "_POSITIONS_FROZEN", positions == expected_positions)
		var normal_artifact_decode_delta := _max_vector_delta(normals, expected_normals)
		_record(mesh_name + "_NORMALS_FROZEN", normals == baseline_runtime_normals, {"artifact_to_runtime_decode_delta": normal_artifact_decode_delta})
		_record(mesh_name + "_TRIANGLES_FROZEN", indices == expected_indices)
		_record(mesh_name + "_FACE_COLOR_COVERAGE", colors.size() == positions.size(), {"colors": colors.size(), "vertices": positions.size()})
		var source_record: Dictionary = gate.data.solids[mesh_name]
		var top_luminance := -1.0
		var side_luminance := -1.0
		for triangle_index in source_record.triangles.size():
			var surface := String(source_record.triangles[triangle_index].surface)
			var color: Color = colors[indices[triangle_index * 3]]
			var luminance := color.get_luminance()
			if surface == "TOP":
				top_luminance = luminance
			elif surface == "SIDE":
				side_luminance = luminance
		_record(mesh_name + "_TOP_READS_ABOVE_SIDE", top_luminance > side_luminance and side_luminance > 0.0, {"top": top_luminance, "side": side_luminance})
	var status_text := String(gate.get_node("UI/StatusPanel/Status").text)
	var identity_text := String(gate.get_node("UI/DiagnosticIdentityPanel/Label").text)
	_record("REVIEW_BUILD_IDENTITY_UNAMBIGUOUS", status_text.contains("v1.2.8 VISIBILITY R3") and status_text.contains("WORLD v1.2.3") and identity_text.contains("VISIBILITY R3"), {"status": status_text, "identity": identity_text})
	gate.queue_free()
	await process_frame


func _test_solid_render_collision_parity() -> void:
	var scene := load("res://scenes/district_zero_p1a.tscn") as PackedScene
	var gate := scene.instantiate()
	root.add_child(gate)
	await process_frame
	await physics_frame
	var mesh_ids: Array = gate.data.solids.keys()
	mesh_ids.sort()
	for mesh_id_value in mesh_ids:
		var mesh_id := String(mesh_id_value)
		var visual := gate.get_node("World/%s_Visual" % mesh_id) as MeshInstance3D
		var body := gate.get_node("World/%s_Collision" % mesh_id) as StaticBody3D
		var material := visual.mesh.surface_get_material(0) as StandardMaterial3D
		var collision_shape_count := PhysicsServer3D.body_get_shape_count(body.get_rid())
		_record(
			mesh_id + "_COLLISION_RENDER_TWO_SIDED",
			material != null
				and material.cull_mode == BaseMaterial3D.CULL_DISABLED
				and collision_shape_count > 0,
			{
				"cull_mode": material.cull_mode if material != null else null,
				"collision_shape_count": collision_shape_count,
				"source_geometry_id": String(body.get_meta("source_geometry_id", "")),
			}
		)
	gate.queue_free()
	await process_frame


func _test_camera_obstruction() -> void:
	var stage := Node3D.new()
	root.add_child(stage)
	var craft := (load("res://scenes/craft.tscn") as PackedScene).instantiate() as CraftController
	craft.name = "Craft"
	craft.position = Vector3(0.0, 1.65, 0.0)
	craft.set_physics_process(false)
	stage.add_child(craft)
	var wall := StaticBody3D.new()
	wall.name = "SyntheticWall"
	wall.collision_layer = 1
	var shape_node := CollisionShape3D.new()
	var box := BoxShape3D.new()
	box.size = Vector3(6.0, 10.0, 0.5)
	shape_node.shape = box
	wall.add_child(shape_node)
	wall.position = Vector3(0.0, 4.0, 4.0)
	stage.add_child(wall)
	var rig := StableCameraRig.new()
	rig.name = "CameraRig"
	rig.target_path = NodePath("../Craft")
	rig.tuning = load("res://resources/default_tuning.tres") as CraftTuning
	var camera := Camera3D.new()
	camera.name = "Camera"
	rig.add_child(camera)
	stage.add_child(rig)
	await process_frame
	await physics_frame
	var craft_before := craft.global_transform
	rig.snap_to_target()
	var blocked_position := rig.global_position
	_record("CAMERA_BLOCKED_STAYS_CRAFT_SIDE", blocked_position.z < wall.global_position.z - 0.25, {"camera_z": blocked_position.z, "wall_z": wall.global_position.z})
	_record("CAMERA_OBSTRUCTION_DOES_NOT_MOVE_CRAFT", craft.global_transform.is_equal_approx(craft_before))
	wall.collision_layer = 0
	await physics_frame
	rig.snap_to_target()
	var expected_clear := craft.global_position + Vector3(0.0, rig.tuning.camera_height, rig.tuning.camera_distance)
	_record("CAMERA_CLEAR_FRAME_UNCHANGED", rig.global_position.is_equal_approx(expected_clear), {"observed": rig.global_position, "expected": expected_clear})
	_record("CAMERA_CLEAR_FOV_UNCHANGED", is_equal_approx(camera.fov, rig.tuning.spread_camera_fov))
	stage.queue_free()
	await process_frame


static func _packed_vectors(values: Array) -> PackedVector3Array:
	var packed := PackedVector3Array()
	packed.resize(values.size())
	for index in values.size():
		var value: Array = values[index]
		packed[index] = Vector3(float(value[0]), float(value[1]), float(value[2]))
	return packed


static func _max_vector_delta(actual: PackedVector3Array, expected: PackedVector3Array) -> float:
	if actual.size() != expected.size():
		return INF
	var result := 0.0
	for index in actual.size():
		var delta := (actual[index] - expected[index]).abs()
		result = maxf(result, maxf(delta.x, maxf(delta.y, delta.z)))
	return result
