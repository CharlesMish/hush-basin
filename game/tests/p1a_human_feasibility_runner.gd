extends SceneTree

const MAIN_SCENE := preload("res://scenes/district_zero_p1a.tscn")
const VECTOR_PATH := "res://tests/fixtures/runtime_vectors.json"
const EXACT_ENGINE := "4.7.1.stable.official.a13da4feb"
const AUTHORITY := "v1.2.5"
const SERIALIZATION := "tests/fixtures/human_trace_serialization_contract.json"
const RESULT_PREFIX := "P1A_HUMAN_RESULT "
const ROUTES := ["A1", "A2", "X0"]
const PROHIBITED_ACTIONS := ["hop", "reset", "pause", "debug_overlay", "diagnostic_menu", "diagnostic_prev", "diagnostic_next", "diagnostic_spawn"]

var mode := ""
var route_id := ""
var output_dir := ""
var session_id := ""
var attempt_index := 0
var replay_index := 0
var input_trace_path := ""
var vector: Dictionary = {}
var gate: P1AWorldGate
var craft: CraftController
var telemetry: P1ATelemetry
var data: P1AWorldData
var overlay_label: Label
var observed_events: Array = []
var input_records: Array = []
var telemetry_records: Array = []
var state_records: Array = []
var replay_input: Dictionary = {}
var fast_distance_m := 0.0
var peak_speed_mps := 0.0
var maximum_lateral_m := 0.0
var genuine_distance_m := 0.0
var entered := false
var traversed := false
var hard_collision_count := 0
var fall_reset_count := 0
var prohibited_input_count := 0
var previous_point := Vector2.ZERO
var previous_point_valid := false
var last_event_index := 0
var termination_reason := ""
var manual_abort := false
var smoke_mode := false
var smoke_started_usec := 0
var smoke_movement_input_s := 0.0
var smoke_steer_left_s := 0.0
var smoke_steer_right_s := 0.0
var smoke_pause_timestamps_s: Array[float] = []
var smoke_resume_timestamps_s: Array[float] = []
var smoke_focus_out_timestamps_s: Array[float] = []
var smoke_focus_in_timestamps_s: Array[float] = []
var _smoke_previous_paused := false


func _notification(what: int) -> void:
	if not smoke_mode or smoke_started_usec <= 0:
		return
	var elapsed := float(Time.get_ticks_usec() - smoke_started_usec) / 1000000.0
	if what == NOTIFICATION_APPLICATION_FOCUS_OUT:
		smoke_focus_out_timestamps_s.append(elapsed)
	elif what == NOTIFICATION_APPLICATION_FOCUS_IN:
		smoke_focus_in_timestamps_s.append(elapsed)


func _initialize() -> void:
	call_deferred("_run")


func _run() -> void:
	var errors := _parse_arguments()
	if not errors.is_empty():
		_blocked("; ".join(errors))
		return
	var parsed = JSON.parse_string(FileAccess.get_file_as_string(VECTOR_PATH))
	if not parsed is Dictionary:
		_blocked("runtime vector fixture is unreadable")
		return
	for value in parsed.get("vectors", []):
		if String(value.get("id", "")) == "RT_ROUTE_%s" % route_id:
			vector = value
			break
	if vector.is_empty():
		_blocked("requested route vector is absent")
		return
	if _engine_identity() != EXACT_ENGINE:
		_blocked("exact Godot identity mismatch: %s" % _engine_identity())
		return
	if mode == "replay":
		var parsed_trace = JSON.parse_string(FileAccess.get_file_as_string(input_trace_path))
		if not parsed_trace is Dictionary:
			_blocked("replay input trace is absent or invalid")
			return
		replay_input = parsed_trace
		if String(replay_input.get("route_id", "")) != route_id or replay_input.get("records", []).is_empty():
			_blocked("replay input trace route/records mismatch")
			return
	gate = MAIN_SCENE.instantiate() as P1AWorldGate
	get_root().add_child(gate)
	await process_frame
	craft = gate.craft
	telemetry = gate.telemetry
	data = gate.data
	telemetry.event_emitted.connect(_on_event)
	_configure_capture_ui()
	_apply_canonical_state()
	if mode == "familiarization":
		await _run_familiarization()
		return
	if mode == "capture":
		await _ready_countdown()
	else:
		_begin_physics()
	await _run_evidentiary_attempt()


func _parse_arguments() -> Array[String]:
	mode = _argument_value("--mode")
	route_id = _argument_value("--route")
	output_dir = _argument_value("--output-dir")
	session_id = _argument_value("--session-id")
	input_trace_path = _argument_value("--input-trace")
	attempt_index = int(_argument_value("--attempt-index"))
	replay_index = int(_argument_value("--replay-index"))
	smoke_mode = "--v1-2-6-smoke" in OS.get_cmdline_user_args()
	var errors: Array[String] = []
	if not mode in ["familiarization", "capture", "replay"]:
		errors.append("--mode must be familiarization, capture, or replay")
	if not route_id in ROUTES:
		errors.append("--route must be A1, A2, or X0")
	if output_dir.is_empty() or session_id.is_empty():
		errors.append("--output-dir and --session-id are required")
	if mode == "capture" and (attempt_index < 1 or attempt_index > 5):
		errors.append("capture --attempt-index must be 1..5")
	if mode == "replay" and (replay_index < 1 or replay_index > 3 or input_trace_path.is_empty()):
		errors.append("replay requires --input-trace and --replay-index 1..3")
	return errors


func _configure_capture_ui() -> void:
	gate.menu_panel.visible = false
	gate.debug_label.visible = false
	gate.status_label.get_parent().visible = false
	gate.diagnostic_identity_panel.visible = false
	var layer := CanvasLayer.new()
	var panel := PanelContainer.new()
	panel.position = Vector2(24.0, 24.0)
	panel.custom_minimum_size = Vector2(560.0, 126.0)
	overlay_label = Label.new()
	overlay_label.add_theme_font_size_override("font_size", 20)
	panel.add_child(overlay_label)
	layer.add_child(panel)
	gate.add_child(layer)
	_update_overlay("SETUP", 0.0, "")


func _apply_canonical_state() -> void:
	_release_actions()
	craft.set_physics_process(false)
	telemetry.set_physics_process(false)
	telemetry.segment_boundary()
	telemetry.physics_tick = 0
	telemetry.events.clear()
	var spawn: Dictionary = vector.get("spawn_transform", {})
	var p: Array = spawn.get("position_xyz_m", [0.0, 0.0, 0.0])
	var transform := Transform3D(Basis.IDENTITY.rotated(Vector3.UP, float(spawn.get("yaw_rad", 0.0))), Vector3(float(p[0]), float(p[1]), float(p[2])))
	craft.set_spawn_transform(transform)
	craft.global_transform = transform
	craft.velocity = Vector3.ZERO
	craft.fold_amount = 1.0
	craft.set("_input_locked_until_release", false)
	craft.clear_pending_hop()
	craft.hop_cooldown_remaining = 0.0
	craft.hop_count = 0
	craft.reset_physics_interpolation()
	gate.active_tour_id = ""
	gate.camera_rig.snap_to_target()
	previous_point = Vector2(craft.global_position.x, craft.global_position.z)
	previous_point_valid = true


func _ready_countdown() -> void:
	var remaining := 3.0
	while remaining > 0.0:
		_update_overlay("READY", 3.0 - remaining, "Physics held · hold SHIFT before GO")
		var started := Time.get_ticks_usec()
		await process_frame
		remaining -= float(Time.get_ticks_usec() - started) / 1000000.0
	_begin_physics()


func _begin_physics() -> void:
	telemetry.segment_boundary()
	telemetry.physics_tick = 0
	telemetry.events.clear()
	observed_events.clear()
	last_event_index = 0
	craft.set_physics_process(true)
	telemetry.set_physics_process(true)


func _run_familiarization() -> void:
	_begin_physics()
	var started := Time.get_ticks_usec()
	smoke_started_usec = started
	var previous_sample_usec := started
	_smoke_previous_paused = paused
	while float(Time.get_ticks_usec() - started) / 1000000.0 < 300.0:
		var now := Time.get_ticks_usec()
		var elapsed := float(now - started) / 1000000.0
		var sample_delta := float(now - previous_sample_usec) / 1000000.0
		previous_sample_usec = now
		if smoke_mode:
			_record_smoke_inputs(sample_delta, elapsed)
		_update_overlay("FAMILIARIZATION", elapsed, "F10 when ready · no evidence recorded")
		if Input.is_physical_key_pressed(KEY_F10):
			break
		await process_frame
	_release_actions()
	var result := {"schema": "district_zero.p1a.human_familiarization_result.v1", "authority_version": AUTHORITY, "route_id": route_id, "session_id": session_id, "status": "COMPLETE", "evidence_class": "NON_EVIDENTIARY_FAMILIARIZATION", "elapsed_s": float(Time.get_ticks_usec() - started) / 1000000.0}
	if smoke_mode:
		result["v1_2_6_smoke_observation"] = {
			"movement_input_s": smoke_movement_input_s,
			"steer_left_s": smoke_steer_left_s,
			"steer_right_s": smoke_steer_right_s,
			"pause_timestamps_s": smoke_pause_timestamps_s,
			"resume_timestamps_s": smoke_resume_timestamps_s,
			"focus_out_timestamps_s": smoke_focus_out_timestamps_s,
			"focus_in_timestamps_s": smoke_focus_in_timestamps_s,
		}
	_write_json(output_dir.path_join("familiarization_result.json"), result)
	print(RESULT_PREFIX + JSON.stringify(result))
	quit(0)


func _record_smoke_inputs(delta: float, elapsed: float) -> void:
	if Input.get_action_strength("throttle") > 0.05 or Input.get_action_strength("brake") > 0.05:
		smoke_movement_input_s += delta
	if Input.get_action_strength("steer_left") > 0.05:
		smoke_steer_left_s += delta
	if Input.get_action_strength("steer_right") > 0.05:
		smoke_steer_right_s += delta
	var paused_now := paused
	if paused_now != _smoke_previous_paused:
		if paused_now:
			smoke_pause_timestamps_s.append(elapsed)
		else:
			smoke_resume_timestamps_s.append(elapsed)
		_smoke_previous_paused = paused_now


func _run_evidentiary_attempt() -> void:
	var source_records: Array = replay_input.get("records", []) if mode == "replay" else []
	var maximum_ticks := source_records.size() if mode == "replay" else int(ceil(float(vector.get("termination", {}).get("maximum_duration_s", 1.0)) * 60.0))
	for tick in maximum_ticks:
		var input_record := _replay_input_record(source_records[tick]) if mode == "replay" else _capture_input_record(tick)
		if mode == "replay":
			_apply_replay_input(input_record)
		input_records.append(input_record)
		if mode == "capture":
			var invalid := _prohibited_input_name()
			if not invalid.is_empty():
				prohibited_input_count += 1
				termination_reason = "PROHIBITED_INPUT:%s" % invalid
				break
			if not bool(input_record.transform_pressed):
				prohibited_input_count += 1
				termination_reason = "DRIVE_TRANSFORM_NOT_HELD"
				break
			if Input.is_physical_key_pressed(KEY_F10):
				manual_abort = true
				termination_reason = "MANUAL_ABORT"
				break
		await physics_frame
		await process_frame
		_record_post_physics(tick, input_record)
		_update_overlay("REPLAY" if mode == "replay" else "RECORDING", float(tick + 1) / 60.0, "Input replay %d/3" % replay_index if mode == "replay" else "Attempt %d/5 · F10 abort" % attempt_index)
		var terminal := _terminal_after_tick()
		if not terminal.is_empty():
			termination_reason = terminal
			break
	if termination_reason.is_empty():
		termination_reason = "INPUT_TRACE_EXHAUSTED" if mode == "replay" else "TIMEOUT"
	_release_actions()
	craft.set_physics_process(false)
	telemetry.set_physics_process(false)
	_finalize_files()


func _capture_input_record(tick: int) -> Dictionary:
	var throttle := clampf(Input.get_action_strength("throttle"), 0.0, 1.0)
	var brake := clampf(Input.get_action_strength("brake"), 0.0, 1.0)
	var steer := clampf(Input.get_axis("steer_left", "steer_right"), -1.0, 1.0)
	return {"brake_u16": int(round(brake * 65535.0)), "hop_pressed": Input.is_action_pressed("hop"), "physics_tick": tick + 1, "steer_i16": int(round(steer * 32767.0)), "throttle_u16": int(round(throttle * 65535.0)), "transform_pressed": Input.is_action_pressed("transform"), "vector_tick": tick}


func _replay_input_record(value) -> Dictionary:
	var raw: Dictionary = value
	return {"brake_u16": int(raw.get("brake_u16", 0)), "hop_pressed": bool(raw.get("hop_pressed", false)), "physics_tick": int(raw.get("physics_tick", 0)), "steer_i16": int(raw.get("steer_i16", 0)), "throttle_u16": int(raw.get("throttle_u16", 0)), "transform_pressed": bool(raw.get("transform_pressed", false)), "vector_tick": int(raw.get("vector_tick", 0))}


func _apply_replay_input(record: Dictionary) -> void:
	_release_actions()
	var throttle := float(int(record.throttle_u16)) / 65535.0
	var brake := float(int(record.brake_u16)) / 65535.0
	var steer := float(int(record.steer_i16)) / 32767.0
	if throttle > 0.0: Input.action_press("throttle", throttle)
	if brake > 0.0: Input.action_press("brake", brake)
	if steer > 0.0: Input.action_press("steer_right", steer)
	elif steer < 0.0: Input.action_press("steer_left", -steer)
	if bool(record.transform_pressed): Input.action_press("transform", 1.0)


func _record_post_physics(tick: int, input_record: Dictionary) -> void:
	var point := Vector2(craft.global_position.x, craft.global_position.z)
	var nearest: Dictionary = data.nearest_route_sample(route_id, point)
	var chainage := float(nearest.get("chainage_m", 0.0))
	var lateral := float(nearest.get("distance_m", INF))
	var speed := Vector2(craft.velocity.x, craft.velocity.z).length()
	if speed + 0.000001 >= float(vector.thresholds.fast_route_speed_floor_mps) and previous_point_valid:
		fast_distance_m += previous_point.distance_to(point)
	previous_point = point
	previous_point_valid = true
	peak_speed_mps = maxf(peak_speed_mps, speed)
	maximum_lateral_m = maxf(maximum_lateral_m, lateral)
	var surface_class := int(telemetry.previous_surface_class)
	var record := {"fast_distance_m": fast_distance_m, "fold": craft.fold_amount, "horizontal_speed_mps": speed, "input": input_record.duplicate(true), "physics_tick": telemetry.physics_tick, "position_xyz_m": [craft.global_position.x, craft.global_position.y, craft.global_position.z], "route_chainage_m": chainage, "route_lateral_distance_m": lateral, "surface_class": surface_class, "vector_tick": tick, "velocity_xyz_mps": [craft.velocity.x, craft.velocity.y, craft.velocity.z], "yaw_rad": craft.rotation.y}
	telemetry_records.append(record)
	state_records.append({"chainage_mm": int(round(chainage * 1000.0)), "fast_distance_mm": int(round(fast_distance_m * 1000.0)), "fold_u6": int(round(craft.fold_amount * 1000000.0)), "lateral_mm": int(round(lateral * 1000.0)), "physics_tick": telemetry.physics_tick, "position_mm": [int(round(craft.global_position.x * 1000.0)), int(round(craft.global_position.y * 1000.0)), int(round(craft.global_position.z * 1000.0))], "surface_class": surface_class, "vector_tick": tick, "velocity_mmps": [int(round(craft.velocity.x * 1000.0)), int(round(craft.velocity.y * 1000.0)), int(round(craft.velocity.z * 1000.0))], "yaw_urad": int(round(craft.rotation.y * 1000000.0))})
	for event in observed_events:
		if int(event.get("serial", 0)) <= last_event_index:
			continue
		last_event_index = maxi(last_event_index, int(event.get("serial", 0)))
		if String(event.get("event", "")) == "ROUTE_STATE" and String(event.get("route_id", "")) == route_id:
			if String(event.get("state", "")) == "ENTERED": entered = true
			if String(event.get("state", "")) == "TRAVERSED":
				traversed = true
				genuine_distance_m = maxf(genuine_distance_m, float(event.get("distance_since_genuine_entry_m", 0.0)))
		if String(event.get("event", "")) == "COLLISION_SAMPLE" and String(event.get("collision_class", "")) != "HARD_HOP": hard_collision_count += 1
		if String(event.get("event", "")) == "RESET" and String(event.get("reason", "")) == "FALL": fall_reset_count += 1


func _terminal_after_tick() -> String:
	if maximum_lateral_m > float(vector.thresholds.maximum_test_driver_path_deviation_m) + 0.000001: return "LATERAL_LIMIT_CROSSED"
	if hard_collision_count > 0: return "NON_HOP_HARD_COLLISION"
	if fall_reset_count > 0: return "FALL_OR_RESET"
	if traversed: return "ROUTE_TRAVERSED"
	return ""


func _route_failures() -> Array[String]:
	var failures: Array[String] = []
	if not entered: failures.append("genuine requested-route ENTERED event absent")
	if not traversed: failures.append("genuine requested-route TRAVERSED event absent")
	if genuine_distance_m + 0.000001 < float(vector.thresholds.minimum_genuine_classified_distance_m): failures.append("genuine traversal distance minimum not met")
	if fast_distance_m + 0.000001 < float(vector.thresholds.minimum_distance_at_or_above_fast_route_speed_m): failures.append("fast-distance minimum not met")
	if maximum_lateral_m > float(vector.thresholds.maximum_test_driver_path_deviation_m) + 0.000001: failures.append("lateral maximum exceeded")
	if hard_collision_count > 0: failures.append("non-Hop hard collision observed")
	if fall_reset_count > 0: failures.append("fall/reset observed")
	if prohibited_input_count > 0: failures.append("prohibited or ineligible input observed")
	if manual_abort: failures.append("manual capture abort")
	if input_records.is_empty() or input_records.size() != telemetry_records.size(): failures.append("input/telemetry records absent or noncontiguous")
	return failures


func _finalize_files() -> void:
	DirAccess.make_dir_recursive_absolute(output_dir)
	var failures := _route_failures()
	var status := "PASS" if failures.is_empty() else ("ABORTED" if manual_abort else "FAIL")
	var trace_id := String(replay_input.get("trace_id", "%s-%s-attempt-%02d" % [session_id, route_id, attempt_index]))
	var project_identity := _project_identity()
	var initial_state := {"fold": 1.0, "linear_velocity_xyz_mps": [0.0, 0.0, 0.0], "spawn_transform": vector.spawn_transform}
	if mode == "capture":
		var input_trace := {"attempt_index": attempt_index, "authority_version": AUTHORITY, "engine_identity": _engine_identity(), "initial_state": initial_state, "physics_timestep_s": 1.0 / 60.0, "project_identity": project_identity, "records": input_records, "route_id": route_id, "schema": "district_zero.p1a.human_input_trace.v1", "serialization_contract": SERIALIZATION, "terminal": {"record_count": input_records.size(), "status": status, "termination_reason": termination_reason}, "trace_id": trace_id}
		_write_json(output_dir.path_join("input_trace.json"), input_trace)
	elif not input_trace_path.is_empty():
		_copy_file(input_trace_path, output_dir.path_join("input_trace.json"))
	var state_trace := {"authority_version": AUTHORITY, "records": state_records, "route_id": route_id, "schema": "district_zero.p1a.human_state_trace.v1", "serialization_contract": SERIALIZATION, "trace_id": trace_id}
	var telemetry_doc := {"attempt_index": int(replay_input.get("attempt_index", attempt_index)), "engine_identity": _engine_identity(), "events": observed_events, "project_identity": project_identity, "records": telemetry_records, "route_id": route_id, "schema": "district_zero.p1a.human_capture_telemetry.v1", "summary": _metrics(), "trace_id": trace_id}
	_write_json(output_dir.path_join("state_trace.json"), state_trace)
	_write_json(output_dir.path_join("telemetry.json"), telemetry_doc)
	var result: Dictionary
	if mode == "capture":
		result = {"attempt_index": attempt_index, "authority_version": AUTHORITY, "evidence_hashes": {}, "failures": failures, "metrics": _metrics(), "route_id": route_id, "schema": "district_zero.p1a.human_capture_attempt_result.v1", "status": status, "trace_id": trace_id}
		_write_json(output_dir.path_join("attempt_result.json"), result)
	else:
		result = {"authority_version": AUTHORITY, "determinism": {}, "evidence_hashes": {}, "replay_index": replay_index, "route_id": route_id, "route_metrics_pass": failures.is_empty(), "schema": "district_zero.p1a.human_replay_result.v1", "status": "PASS" if failures.is_empty() else "FAIL", "trace_id": trace_id}
		_write_json(output_dir.path_join("replay_result.json"), result)
	_update_overlay("COMPLETE", float(input_records.size()) / 60.0, status)
	print(RESULT_PREFIX + JSON.stringify(result))
	quit(0 if failures.is_empty() else 1)


func _metrics() -> Dictionary:
	return {"contiguous_tick_count": telemetry_records.size(), "entered": entered, "fall_reset_count": fall_reset_count, "fast_distance_m": fast_distance_m, "genuine_distance_m": genuine_distance_m, "hard_collision_count": hard_collision_count, "maximum_lateral_distance_m": maximum_lateral_m, "peak_speed_mps": peak_speed_mps, "post_result_event_count": 0, "prohibited_input_count": prohibited_input_count, "termination_tick": telemetry.physics_tick, "traversed": traversed}


func _project_identity() -> Dictionary:
	return {"capture_runner_sha256": FileAccess.get_sha256("res://tests/p1a_human_feasibility_runner.gd"), "project_godot_sha256": FileAccess.get_sha256("res://project.godot"), "runtime_runner_sha256": FileAccess.get_sha256("res://tests/p1a_runtime_runner.gd")}


func _engine_identity() -> String:
	var info := Engine.get_version_info()
	return "%d.%d.%d.%s.%s.%s" % [int(info.get("major", 0)), int(info.get("minor", 0)), int(info.get("patch", 0)), String(info.get("status", "")), String(info.get("build", "")), String(info.get("hash", "")).substr(0, 9)]


func _prohibited_input_name() -> String:
	for action in PROHIBITED_ACTIONS:
		if Input.is_action_pressed(action): return action
	return ""


func _on_event(event: Dictionary) -> void:
	observed_events.append(event.duplicate(true))


func _update_overlay(phase: String, elapsed: float, detail: String) -> void:
	if overlay_label == null: return
	overlay_label.text = "DISTRICT ZERO · P1A FEASIBILITY CAPTURE · v1.2.5\nRoute %s · %s · %s\nElapsed %.1f s · %s" % [route_id, phase, "Attempt %d/5" % attempt_index if mode == "capture" else ("Replay %d/3" % replay_index if mode == "replay" else "Non-evidentiary"), elapsed, detail]


func _write_json(path: String, value) -> void:
	var file := FileAccess.open(path, FileAccess.WRITE)
	file.store_string(JSON.stringify(value, "", true, true) + "\n")
	file.close()


func _copy_file(source: String, destination: String) -> void:
	var source_file := FileAccess.open(source, FileAccess.READ)
	var bytes := source_file.get_buffer(source_file.get_length())
	source_file.close()
	var destination_file := FileAccess.open(destination, FileAccess.WRITE)
	destination_file.store_buffer(bytes)
	destination_file.close()


func _release_actions() -> void:
	for action in ["throttle", "brake", "steer_left", "steer_right", "transform", "hop"]:
		Input.action_release(action)


func _blocked(reason: String) -> void:
	var result := {"schema": "district_zero.p1a.human_runner_blocked.v1", "status": "BLOCKED/NOT TESTABLE", "reason": reason, "route_id": route_id, "mode": mode}
	if not output_dir.is_empty():
		DirAccess.make_dir_recursive_absolute(output_dir)
		_write_json(output_dir.path_join("blocked_result.json"), result)
	printerr(RESULT_PREFIX + JSON.stringify(result))
	quit(2)


func _argument_value(flag: String) -> String:
	var args := OS.get_cmdline_user_args()
	for index in args.size() - 1:
		if args[index] == flag: return args[index + 1]
	return ""
