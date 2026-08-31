extends SceneTree

const MAIN_SCENE := preload("res://scenes/district_zero_p1a.tscn")
const EXACT_ENGINE := "4.7.1.stable.official.a13da4feb"
const POSES := {"spread": 0.0, "mid": 0.5, "drive": 1.0}


func _initialize() -> void:
	call_deferred("_run")


func _run() -> void:
	var output_dir := _arg("--output-dir")
	if output_dir.is_empty() or _engine_identity() != EXACT_ENGINE:
		quit(2)
		return
	DirAccess.make_dir_recursive_absolute(output_dir)
	var gate := MAIN_SCENE.instantiate() as P1AWorldGate
	root.add_child(gate)
	await process_frame
	gate.craft.set_physics_process(false)
	gate.telemetry.set_physics_process(false)
	gate.get_node("UI").visible = false
	var tour: Dictionary = gate._tour_by_id("T01_WEST_GATE")
	var spawn: Dictionary = tour.spawn_transform
	var xyz: Array = spawn.position_xyz_m
	gate.craft.global_transform = Transform3D(
		Basis.IDENTITY.rotated(Vector3.UP, float(spawn.yaw_rad)),
		Vector3(float(xyz[0]), float(xyz[1]), float(xyz[2]))
	)
	gate.craft.velocity = Vector3.ZERO
	gate.camera_rig.snap_to_target()
	var rig := gate.craft.get_node("VisualRoot") as VehicleVisualRig
	var camera := gate.camera_rig.get_node("Camera") as Camera3D
	var records: Array[Dictionary] = []
	var passed := rig != null and camera != null and not _has_physics_descendant(rig)
	for label in POSES:
		var amount: float = POSES[label]
		gate.craft.fold_amount = amount
		gate.craft.call("_update_visuals", 0.0, 1.0 / 60.0)
		gate.craft.reset_physics_interpolation()
		gate.camera_rig.snap_to_target()
		await process_frame
		await process_frame
		var frame_check := _visual_in_frame(rig, camera)
		passed = passed and is_equal_approx(rig.form_amount, amount) and bool(frame_check.passed)
		var filename := "vehicle-r7-%s-world.png" % label
		var path := output_dir.path_join(filename)
		var image := root.get_viewport().get_texture().get_image()
		image.save_png(path)
		records.append({
			"form_amount": amount,
			"image": filename,
			"image_sha256": FileAccess.get_sha256(path),
			"rig_form_amount": rig.form_amount,
			"size_px": [image.get_width(), image.get_height()],
			"visual_in_frame": frame_check,
		})
	var result := {
		"engine_identity": _engine_identity(),
		"physics_descendant_absent": not _has_physics_descendant(rig),
		"records": records,
		"schema": "district_zero.p1a.vehicle_r7.pose_probe.v1",
		"status": "PASS" if passed else "FAIL",
	}
	var result_file := FileAccess.open(output_dir.path_join("pose_probe_result.json"), FileAccess.WRITE)
	result_file.store_string(JSON.stringify(result, "  ") + "\n")
	result_file.close()
	print("P1A_VEHICLE_R7_POSE_RESULT " + JSON.stringify(result))
	gate.queue_free()
	await process_frame
	quit(0 if passed else 1)


func _visual_in_frame(rig: Node3D, camera: Camera3D) -> Dictionary:
	var meshes: Array[MeshInstance3D] = []
	_collect_meshes(rig, meshes)
	var viewport_size := Vector2(1280.0, 720.0)
	var minimum := Vector2(INF, INF)
	var maximum := Vector2(-INF, -INF)
	var all_visible := not meshes.is_empty()
	for instance in meshes:
		if instance.mesh == null:
			continue
		var bounds := instance.mesh.get_aabb()
		for corner_index in 8:
			var local := Vector3(
				bounds.position.x + bounds.size.x * float(corner_index & 1),
				bounds.position.y + bounds.size.y * float((corner_index >> 1) & 1),
				bounds.position.z + bounds.size.z * float((corner_index >> 2) & 1)
			)
			var world := instance.global_transform * local
			if camera.is_position_behind(world):
				all_visible = false
				continue
			var screen := camera.unproject_position(world)
			minimum = minimum.min(screen)
			maximum = maximum.max(screen)
			if screen.x < 0.0 or screen.y < 0.0 or screen.x > viewport_size.x or screen.y > viewport_size.y:
				all_visible = false
	return {
		"mesh_count": meshes.size(),
		"passed": all_visible,
		"screen_max_xy": [maximum.x, maximum.y],
		"screen_min_xy": [minimum.x, minimum.y],
	}


func _collect_meshes(node: Node, output: Array[MeshInstance3D]) -> void:
	if node is MeshInstance3D:
		output.append(node as MeshInstance3D)
	for child in node.get_children():
		_collect_meshes(child, output)


func _has_physics_descendant(node: Node) -> bool:
	for child in node.get_children():
		if child is CollisionObject3D or child is CollisionShape3D or child is RayCast3D or child is ShapeCast3D:
			return true
		if _has_physics_descendant(child):
			return true
	return false


func _arg(name: String) -> String:
	var args := OS.get_cmdline_user_args()
	for index in args.size():
		if args[index] == name and index + 1 < args.size():
			return args[index + 1]
	return ""


func _engine_identity() -> String:
	var info := Engine.get_version_info()
	return "%d.%d.%d.%s.%s.%s" % [
		int(info.get("major", 0)), int(info.get("minor", 0)), int(info.get("patch", 0)),
		String(info.get("status", "")), String(info.get("build", "")),
		String(info.get("hash", "")).substr(0, 9),
	]
