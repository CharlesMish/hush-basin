extends SceneTree

const REQUIRED_GODOT_VERSION := "4.7.1.stable.official.a13da4feb"
const TRACE_TICKS := 1260
const TRACE_ACTIONS := ["throttle", "brake", "steer_left", "steer_right", "transform", "hop"]
const CRAFT_SCENE := preload("res://scenes/craft.tscn")
const CAMERA_SCRIPT := preload("res://scripts/camera_rig.gd")
const DEFAULT_TUNING := preload("res://resources/default_tuning.tres")

var _craft: CraftController
var _camera_rig: Node3D
var _output_path := ""


func _init() -> void:
	call_deferred("_run")


func _run() -> void:
	if not _engine_identity_matches():
		_fail("expected Godot %s, found %s" % [REQUIRED_GODOT_VERSION, Engine.get_version_info()])
		return
	_output_path = _parse_output_path()
	if _output_path.is_empty():
		_fail("required CLI: --output <JSONL_PATH>")
		return
	var fixture_root := _build_fixture()
	root.add_child(fixture_root)
	await process_frame
	_release_all_actions()
	var spawn := Transform3D(Basis.IDENTITY, Vector3(0.0, 1.65, 0.0))
	_craft.set_spawn_transform(spawn)
	_craft.reset_craft("P1A C1 baseline alignment")
	var file_path := _output_path if _output_path.is_absolute_path() else ProjectSettings.globalize_path("res://" + _output_path)
	var trace_file := FileAccess.open(file_path, FileAccess.WRITE)
	if trace_file == null:
		_fail("cannot open trace output: %s" % file_path)
		return
	for physics_tick in TRACE_TICKS:
		_apply_tick_actions(physics_tick)
		await physics_frame
		trace_file.store_line(JSON.stringify(_sample_trace(physics_tick)))
	trace_file.close()
	_release_all_actions()
	print("P1A C1 BASELINE TRACE: %d ticks -> %s" % [TRACE_TICKS, file_path])
	fixture_root.free()
	quit(0)


func _build_fixture() -> Node3D:
	var fixture_root := Node3D.new()
	fixture_root.name = "BaselineFlatSupport"
	var support := StaticBody3D.new()
	support.name = "BaselineSmooth"
	support.collision_layer = 1
	support.collision_mask = 1
	support.position = Vector3(0.0, -0.5, 0.0)
	fixture_root.add_child(support)
	var box_shape := BoxShape3D.new()
	box_shape.size = Vector3(160.0, 1.0, 160.0)
	var collision := CollisionShape3D.new()
	collision.name = "Collision"
	collision.shape = box_shape
	support.add_child(collision)
	var box_mesh := BoxMesh.new()
	box_mesh.size = Vector3(160.0, 1.0, 160.0)
	var visual := MeshInstance3D.new()
	visual.name = "VisibleSupport"
	visual.mesh = box_mesh
	support.add_child(visual)
	_craft = CRAFT_SCENE.instantiate() as CraftController
	_craft.name = "Craft"
	_craft.transform = Transform3D(Basis.IDENTITY, Vector3(0.0, 1.65, 0.0))
	fixture_root.add_child(_craft)
	_camera_rig = Node3D.new()
	_camera_rig.name = "CameraRig"
	_camera_rig.set_script(CAMERA_SCRIPT)
	_camera_rig.set("target_path", NodePath("../Craft"))
	_camera_rig.set("tuning", DEFAULT_TUNING)
	var camera := Camera3D.new()
	camera.name = "Camera"
	camera.current = true
	camera.fov = 68.0
	camera.far = 700.0
	_camera_rig.add_child(camera)
	fixture_root.add_child(_camera_rig)
	return fixture_root


func _parse_output_path() -> String:
	var arguments := OS.get_cmdline_user_args()
	var index := arguments.find("--output")
	if index < 0 or index + 1 >= arguments.size():
		return ""
	return arguments[index + 1]


func _engine_identity_matches() -> bool:
	var version := Engine.get_version_info()
	return (
		int(version.get("major", -1)) == 4
		and int(version.get("minor", -1)) == 7
		and int(version.get("patch", -1)) == 1
		and str(version.get("status", "")) == "stable"
		and str(version.get("build", "")) == "official"
		and str(version.get("hash", "")).begins_with("a13da4feb")
	)


func _apply_tick_actions(physics_tick: int) -> void:
	_release_all_actions()
	if physics_tick >= 120 and physics_tick <= 359:
		Input.action_press("throttle", 1.0)
	elif physics_tick >= 360 and physics_tick <= 479:
		Input.action_press("throttle", 1.0)
		Input.action_press("steer_right", 0.6)
	elif physics_tick >= 480 and physics_tick <= 599:
		Input.action_press("brake", 1.0)
	elif physics_tick >= 600 and physics_tick <= 659:
		Input.action_press("transform", 1.0)
	elif physics_tick >= 660 and physics_tick <= 899:
		Input.action_press("throttle", 1.0)
		Input.action_press("transform", 1.0)
	elif physics_tick >= 900 and physics_tick <= 1019:
		Input.action_press("throttle", 1.0)
		Input.action_press("steer_left", 0.35)
		Input.action_press("transform", 1.0)
	elif physics_tick >= 1020 and physics_tick <= 1079:
		Input.action_press("brake", 1.0)
		Input.action_press("transform", 1.0)
	elif physics_tick == 1140:
		Input.action_press("hop", 1.0)


func _release_all_actions() -> void:
	for action in TRACE_ACTIONS:
		Input.action_release(action)


func _sample_trace(physics_tick: int) -> Dictionary:
	var craft_basis := _craft.global_basis
	var camera_basis := _camera_rig.global_basis
	return {
		"physics_tick": physics_tick,
		"global_position_xyz": _vector(_craft.global_position),
		"global_basis_x_xyz": _vector(craft_basis.x),
		"global_basis_y_xyz": _vector(craft_basis.y),
		"global_basis_z_xyz": _vector(craft_basis.z),
		"velocity_xyz": _vector(_craft.velocity),
		"fold_amount": _craft.fold_amount,
		"probe_hit_count": _craft.probe_hit_count,
		"measured_height": _craft.measured_height,
		"support_normal_xyz": _vector(_craft.support_normal),
		"support_reacquire_blend": _craft.support_reacquire_blend,
		"hop_count": _craft.hop_count,
		"hop_cooldown_remaining": _craft.hop_cooldown_remaining,
		"impact_count": _craft.impact_count,
		"last_impact_strength": _craft.last_impact_severity,
		"camera_global_position_xyz": _vector(_camera_rig.global_position),
		"camera_global_basis_x_xyz": _vector(camera_basis.x),
		"camera_global_basis_y_xyz": _vector(camera_basis.y),
		"camera_global_basis_z_xyz": _vector(camera_basis.z),
	}


func _vector(value: Vector3) -> Array[float]:
	return [value.x, value.y, value.z]


func _fail(message: String) -> void:
	printerr("P1A C1 BASELINE ERROR: ", message)
	_release_all_actions()
	quit(1)
