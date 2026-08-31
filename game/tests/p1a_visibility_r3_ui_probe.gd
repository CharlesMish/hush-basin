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
	var tour: Dictionary = {}
	for value in gate.data.diagnostic.get("tours", []):
		if String(value.id) == "T01_WEST_GATE":
			tour = value
			break
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
	gate.menu_panel.visible = true
	await process_frame
	await process_frame
	var image_path := output_dir.path_join("visibility-r3-west-threshold-ui.png")
	root.get_viewport().get_texture().get_image().save_png(image_path)
	var status_text := String(gate.status_label.text)
	var identity_text := String(gate.get_node("UI/DiagnosticIdentityPanel/Label").text)
	var passed := status_text.contains("v1.2.8 VISIBILITY R3") and status_text.contains("WORLD v1.2.3") and identity_text.contains("VISIBILITY R3")
	var result := {
		"schema": "district_zero.p1a.visibility_r3_ui_probe.v1",
		"status": "PASS" if passed else "FAIL",
		"engine_identity": _engine_identity(),
		"image": image_path.get_file(),
		"image_sha256": FileAccess.get_sha256(image_path),
		"status_text": status_text,
		"identity_text": identity_text,
	}
	var file := FileAccess.open(output_dir.path_join("ui_probe_result.json"), FileAccess.WRITE)
	file.store_string(JSON.stringify(result, "  ") + "\n")
	file.close()
	print("P1A_VISIBILITY_R3_UI_RESULT " + JSON.stringify(result))
	gate.queue_free()
	await process_frame
	quit(0 if passed else 1)


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
