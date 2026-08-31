extends SceneTree

const MAIN_SCENE := preload("res://scenes/district_zero_p1a.tscn")
const EXACT_ENGINE := "4.7.1.stable.official.a13da4feb"

var output_dir := ""


func _initialize() -> void:
	call_deferred("_run")


func _run() -> void:
	output_dir = _arg("--output-dir")
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
	var records: Array[Dictionary] = []
	for value in gate.data.diagnostic.get("tours", []):
		var tour: Dictionary = value
		var spawn: Dictionary = tour.spawn_transform
		var position: Array = spawn.position_xyz_m
		gate.craft.global_transform = Transform3D(
			Basis.IDENTITY.rotated(Vector3.UP, float(spawn.yaw_rad)),
			Vector3(float(position[0]), float(position[1]), float(position[2]))
		)
		gate.craft.velocity = Vector3.ZERO
		gate.craft.fold_amount = 1.0 if String(tour.initial_mode) == "DRIVE" else 0.0
		gate.craft.reset_physics_interpolation()
		gate.camera_rig.snap_to_target()
		await process_frame
		await process_frame
		var desired := _desired_camera_position(gate.craft, gate.camera_rig.tuning)
		var actual := gate.camera_rig.global_position
		var filename := String(tour.id).to_lower() + ".png"
		var path := output_dir.path_join(filename)
		root.get_viewport().get_texture().get_image().save_png(path)
		records.append({
			"tour_id": String(tour.id),
			"display_label": String(tour.display_label),
			"image": filename,
			"desired_camera_position": [desired.x, desired.y, desired.z],
			"actual_camera_position": [actual.x, actual.y, actual.z],
			"camera_pull_in_m": desired.distance_to(actual),
		})
	var result := {
		"schema": "district_zero.p1a.visibility_capture_probe.v1",
		"status": "PASS",
		"engine_identity": _engine_identity(),
		"records": records,
	}
	var result_file := FileAccess.open(output_dir.path_join("probe_result.json"), FileAccess.WRITE)
	result_file.store_string(JSON.stringify(result, "  ") + "\n")
	result_file.close()
	print("P1A_VISIBILITY_CAPTURE_RESULT " + JSON.stringify(result))
	gate.queue_free()
	await process_frame
	quit(0)


static func _desired_camera_position(craft: CraftController, tuning: CraftTuning) -> Vector3:
	var forward := -craft.global_transform.basis.z
	forward.y = 0.0
	forward = MotionMath.safe_normalize(forward, Vector3.FORWARD)
	return craft.global_position - forward * tuning.camera_distance + Vector3.UP * tuning.camera_height


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
