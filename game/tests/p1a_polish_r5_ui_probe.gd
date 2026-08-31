extends SceneTree

const MAIN_SCENE := preload("res://scenes/district_zero_p1a.tscn")
const EXACT_ENGINE := "4.7.1.stable.official.a13da4feb"


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
	var tour: Dictionary = gate._tour_by_id("T01_WEST_GATE")
	var spawn: Dictionary = tour.spawn_transform
	var position: Array = spawn.position_xyz_m
	gate.craft.global_transform = Transform3D(
		Basis.IDENTITY.rotated(Vector3.UP, float(spawn.yaw_rad)),
		Vector3(float(position[0]), float(position[1]), float(position[2]))
	)
	gate.craft.velocity = Vector3.ZERO
	gate.craft.fold_amount = 1.0
	gate.craft.reset_physics_interpolation()
	gate.camera_rig.snap_to_target()
	await process_frame
	await process_frame

	var captures := {}
	captures["default"] = _capture(output_dir, "polish-r5-default-ui.png")
	gate.menu_panel.visible = true
	await process_frame
	captures["routes_open"] = _capture(output_dir, "polish-r5-routes-open-ui.png")
	gate.menu_panel.visible = false
	paused = true
	await process_frame
	captures["paused"] = _capture(output_dir, "polish-r5-paused-ui.png")
	paused = false

	var passed := (
		String(gate.status_label.text).contains("P1A POLISH R5")
		and String(gate.status_label.text).contains("WORLD v1.2.3")
		and String((gate.get_node("UI/DiagnosticIdentityPanel/Label") as Label).text).contains("DEVELOPMENT REVIEW")
		and gate.map.highlighted_route_ids == ["A0"]
		and captures.values().all(func(record): return record.get("size_px") == [1280, 720] and String(record.get("sha256", "")).length() == 64)
	)
	var result := {
		"schema": "district_zero.p1a.polish_r5_ui_probe.v1",
		"status": "PASS" if passed else "FAIL",
		"engine_identity": _engine_identity(),
		"captures": captures,
		"status_text": gate.status_label.text,
		"highlighted_routes": gate.map.highlighted_route_ids,
	}
	var result_file := FileAccess.open(output_dir.path_join("ui_probe_result.json"), FileAccess.WRITE)
	result_file.store_string(JSON.stringify(result, "  ") + "\n")
	result_file.close()
	print("P1A_POLISH_R5_UI_RESULT " + JSON.stringify(result))
	gate.queue_free()
	await process_frame
	quit(0 if passed else 1)


func _capture(output_dir: String, filename: String) -> Dictionary:
	var path := output_dir.path_join(filename)
	var image := root.get_viewport().get_texture().get_image()
	image.save_png(path)
	return {"image": filename, "size_px": [image.get_width(), image.get_height()], "sha256": FileAccess.get_sha256(path)}


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
