extends SceneTree

const RUN_SCENE := preload("res://scenes/district_zero_run.tscn")
const BrrrSeed := preload("res://scripts/run/brrr_seed.gd")
const EXACT_ENGINE := "4.7.1.stable.official.a13da4feb"
const POSITION_TOLERANCE_M := 0.0001


class PhysicsFence:
	extends Node

	signal physics_tail

	var armed := false


	func _ready() -> void:
		process_mode = Node.PROCESS_MODE_ALWAYS
		process_physics_priority = 1000


	func _physics_process(_delta: float) -> void:
		if not armed:
			return
		armed = false
		physics_tail.emit()


var checks: Array[Dictionary] = []
var failures: Array[String] = []
var reset_reasons: Array[String] = []
var _fence: PhysicsFence
var _scene: Node
var _gate: P1AWorldGate
var _run: Node
var _craft: CraftController


func _initialize() -> void:
	_run_probe.call_deferred()


func _run_probe() -> void:
	_record("EXACT_ENGINE", _engine_identity() == EXACT_ENGINE, _engine_identity())
	_scene = RUN_SCENE.instantiate()
	root.add_child(_scene)
	_fence = PhysicsFence.new()
	root.add_child(_fence)
	await process_frame
	await process_frame

	_gate = _scene.get_node_or_null("DistrictZeroP1A") as P1AWorldGate
	_run = _scene.get_node_or_null("RunLayer")
	if _gate == null or _run == null:
		_record("RUN_SCENE_NODES", false, {"gate": _gate != null, "run": _run != null})
		_finish()
		return
	_craft = _gate.craft
	_craft.reset_performed.connect(_collect_reset_reason)

	_validate_initial_geometry_and_order()
	_validate_segment_disc()
	_validate_brrr_formula()
	await _validate_free_roam_and_retry_ownership()
	await _validate_held_lock_and_post_move()
	_validate_longest_streak()
	await _validate_pause_and_live_fall()
	_validate_integrated_tunneling_finish()
	_finish()


func _validate_initial_geometry_and_order() -> void:
	var qry: Dictionary = _gate.data.manifest.destination_pads.QRY
	var qry_xz := P1AWorldData.xz(qry.center_xz_m)
	var expected_position := Vector3(
		qry_xz.x,
		_gate.data.terrain_height_at(qry_xz.x, qry_xz.y) + 1.65,
		qry_xz.y
	)
	var a0_points: Array = _gate.data.routes.A0.points_xz_m
	var tangent := (P1AWorldData.xz(a0_points[1]) - P1AWorldData.xz(a0_points[0])).normalized()
	var actual_forward_3d: Vector3 = -_craft.global_basis.z
	var actual_forward := Vector2(actual_forward_3d.x, actual_forward_3d.z).normalized()
	var observed_yaw := atan2(-actual_forward.x, -actual_forward.y)
	_record("PROCESS_PRIORITY_CRAFT_0", _craft.process_physics_priority == 0, _craft.process_physics_priority)
	_record("PROCESS_PRIORITY_TELEMETRY_100", _gate.telemetry.process_physics_priority == 100, _gate.telemetry.process_physics_priority)
	_record("PROCESS_PRIORITY_RUN_200", _run.process_physics_priority == 200, _run.process_physics_priority)
	_record(
		"PAUSE_GUARD_INITIAL_CLOCK",
		_run.process_mode == Node.PROCESS_MODE_ALWAYS,
		{"mode": _run.process_mode, "contract": "ALWAYS with explicit paused guard"}
	)
	_record("BOOT_STATE_COUNTDOWN", _run.state_name() == "COUNTDOWN", _run.state_name())
	_record("BOOT_QRY_POSITION", _craft.global_position.distance_to(expected_position) <= POSITION_TOLERANCE_M, {
		"expected": expected_position,
		"observed": _craft.global_position,
	})
	_record("BOOT_SPAWN_QRY", _run.run_start_transform.origin.distance_to(expected_position) <= POSITION_TOLERANCE_M, {
		"expected": expected_position,
		"observed": _run.run_start_transform.origin,
	})
	_record("BOOT_A0_TANGENT", actual_forward.distance_to(tangent) <= 0.00001, {
		"expected": tangent,
		"observed": actual_forward,
		"yaw": observed_yaw,
	})
	_record("BOOT_A0_YAW", absf(observed_yaw - (-1.740573356)) <= 0.00001, observed_yaw)
	_record("BOOT_SPREAD_ZEROED", _craft.regime_name() == "SPREAD" and _craft.fold_amount == 0.0 and _craft.velocity.is_zero_approx(), {
		"regime": _craft.regime_name(),
		"fold": _craft.fold_amount,
		"velocity": _craft.velocity,
	})
	_record("BOOT_RUN_OWNS_TOUR", _gate.active_tour_id.is_empty(), _gate.active_tour_id)
	_record("BOOT_ROUTES_CLEAR", _gate.map.highlighted_route_ids.is_empty(), _gate.map.highlighted_route_ids)
	var rly: Dictionary = _gate.data.manifest.destination_pads.RLY
	_record("FINISH_FROM_RLY_MANIFEST", _run.finish_center_xz == P1AWorldData.xz(rly.center_xz_m) and is_equal_approx(_run.finish_radius_m, float(rly.outer_blend_radius_m)), {
		"center": _run.finish_center_xz,
		"radius": _run.finish_radius_m,
	})


func _validate_segment_disc() -> void:
	var center := Vector2(4.0, -7.0)
	var radius := 13.0
	var tunnel_a := center + Vector2(-20.0, 0.0)
	var tunnel_b := center + Vector2(20.0, 0.0)
	_record("SEGMENT_TUNNEL_CROSSES", _run.segment_intersects_disc(tunnel_a, tunnel_b, center, radius))
	_record("SEGMENT_TUNNEL_REVERSED", _run.segment_intersects_disc(tunnel_b, tunnel_a, center, radius))
	_record("SEGMENT_TANGENT_INCLUSIVE", _run.segment_intersects_disc(center + Vector2(-20.0, 13.0), center + Vector2(20.0, 13.0), center, radius))
	_record("SEGMENT_NEAR_MISS", not _run.segment_intersects_disc(center + Vector2(-20.0, 13.001), center + Vector2(20.0, 13.001), center, radius))
	_record("SEGMENT_ZERO_LENGTH_INSIDE", _run.segment_intersects_disc(center + Vector2(1.0, 1.0), center + Vector2(1.0, 1.0), center, radius))
	_record("SEGMENT_ZERO_LENGTH_OUTSIDE", not _run.segment_intersects_disc(center + Vector2(14.0, 0.0), center + Vector2(14.0, 0.0), center, radius))


func _validate_brrr_formula() -> void:
	var forward := Vector3(0.0, 0.0, -1.0)
	var spread: Dictionary = BrrrSeed.step(Vector3(0.0, 0.0, -30.0), forward, false, 0.5, 7.0, 2.0)
	_record("BRRR_SPREAD_CANNOT_SCORE", is_equal_approx(float(spread.brrr), 7.0) and is_zero_approx(float(spread.streak_s)) and not bool(spread.qualifying), spread)
	var below: Dictionary = BrrrSeed.step(Vector3(0.0, 0.0, -19.999), forward, true, 0.5, 7.0, 2.0)
	_record("BRRR_BELOW_FLOOR_RESETS", is_equal_approx(float(below.brrr), 7.0) and is_zero_approx(float(below.streak_s)) and not bool(below.qualifying), below)
	var floor_sample: Dictionary = BrrrSeed.step(Vector3(0.0, 0.0, -20.0), forward, true, 0.5, 0.0, 0.0)
	_record("BRRR_FLOOR_INCLUSIVE_ZERO_RATE", bool(floor_sample.qualifying) and is_equal_approx(float(floor_sample.streak_s), 0.5) and is_zero_approx(float(floor_sample.brrr)), floor_sample)
	var aligned: Dictionary = BrrrSeed.step(Vector3(0.0, 0.0, -30.0), forward, true, 0.5, 0.0, 0.0)
	_record("BRRR_ALIGNED_EXACT", absf(float(aligned.brrr) - 52.5) <= 0.00001 and is_zero_approx(float(aligned.split_degrees)), aligned)
	var sideways: Dictionary = BrrrSeed.step(Vector3(30.0, 0.0, 0.0), forward, true, 0.5, 0.0, 0.0)
	_record("BRRR_SIDEWAYS_EXACT", absf(float(sideways.brrr) - 210.0) <= 0.00001 and is_equal_approx(float(sideways.split_degrees), 90.0), sideways)
	var backwards: Dictionary = BrrrSeed.step(Vector3(0.0, 0.0, 30.0), forward, true, 0.5, 0.0, 0.0)
	_record("BRRR_BACKWARD_CLAMPS_90", absf(float(backwards.brrr) - 210.0) <= 0.00001 and is_equal_approx(float(backwards.split_degrees), 90.0), backwards)
	var capped: Dictionary = BrrrSeed.step(Vector3(0.0, 0.0, -30.0), forward, true, 1.0, 0.0, 9.5)
	_record("BRRR_MULTIPLIER_CAP", absf(float(capped.brrr) - 200.0) <= 0.00001 and is_equal_approx(float(capped.streak_s), 10.5), capped)
	var vertical: Dictionary = BrrrSeed.step(Vector3(0.0, 100.0, -30.0), forward, true, 0.5, 0.0, 0.0)
	_record("BRRR_IGNORES_VERTICAL_SPEED", absf(float(vertical.brrr) - 52.5) <= 0.00001 and is_equal_approx(float(vertical.speed), 30.0), vertical)


func _validate_free_roam_and_retry_ownership() -> void:
	var selection_order: Array = _gate.data.diagnostic.selection_order
	var tour_index := selection_order.find("T04_QUARRY_SHELF")
	_gate.selection_index = tour_index
	_gate.spawn_selected_tour()
	await process_frame
	_record("DIAGNOSTIC_ENTERS_FREE_ROAM", _run.state_name() == "FREE_ROAM", _run.state_name())
	_record("DIAGNOSTIC_OWNS_TOUR", _gate.active_tour_id == "T04_QUARRY_SHELF" and not _gate.map.highlighted_route_ids.is_empty(), {
		"tour": _gate.active_tour_id,
		"routes": _gate.map.highlighted_route_ids,
	})
	_record("DIAGNOSTIC_DRIVE_FORM", _craft.regime_name() == "DRIVE", {"regime": _craft.regime_name(), "fold": _craft.fold_amount})

	var free_reset_before := _craft.reset_count
	var free_reason_index := reset_reasons.size()
	_craft.global_position.y = _craft.tuning.fall_reset_y - 0.5
	await _physics_tail()
	var free_new_reasons := reset_reasons.slice(free_reason_index)
	_record("FREE_ROAM_FALL_ONE_R7_RESET", _craft.reset_count == free_reset_before + 1 and free_new_reasons.size() == 1 and String(free_new_reasons[0]).begins_with("fell below"), {
		"count_delta": _craft.reset_count - free_reset_before,
		"reasons": free_new_reasons,
	})
	_record("FREE_ROAM_FALL_STAYS_FREE", _run.state_name() == "FREE_ROAM" and _gate.active_tour_id == "T04_QUARRY_SHELF" and _craft.is_physics_processing(), {
		"state": _run.state_name(),
		"tour": _gate.active_tour_id,
		"physics": _craft.is_physics_processing(),
	})
	_record("FREE_ROAM_FALL_RETAINS_R7_FORM_AND_ROUTES", _craft.regime_name() == "DRIVE" and not _gate.map.highlighted_route_ids.is_empty(), {
		"regime": _craft.regime_name(),
		"routes": _gate.map.highlighted_route_ids,
	})

	Input.action_press("throttle", 1.0)
	var retry_reset_before := _craft.reset_count
	var retry_reason_index := reset_reasons.size()
	var retry_count_before: int = _run.manual_retry_count
	_push_physical_key(KEY_R, true)
	_push_physical_key(KEY_R, false)
	var retry_reasons := reset_reasons.slice(retry_reason_index)
	_record("ONE_R_ONE_RUN_RETRY", _craft.reset_count == retry_reset_before + 1 and retry_reasons == ["run_retry"] and _run.manual_retry_count == retry_count_before + 1, {
		"count_delta": _craft.reset_count - retry_reset_before,
		"reasons": retry_reasons,
		"manual_retry_delta": _run.manual_retry_count - retry_count_before,
	})
	_record("RETRY_RECLAIMS_TOUR", _gate.active_tour_id.is_empty() and _gate.map.highlighted_route_ids.is_empty(), {
		"tour": _gate.active_tour_id,
		"routes": _gate.map.highlighted_route_ids,
	})
	_record("RETRY_QRY_SPREAD_COUNTDOWN", _run.state_name() == "COUNTDOWN" and _craft.regime_name() == "SPREAD" and not _craft.is_physics_processing(), {
		"state": _run.state_name(),
		"regime": _craft.regime_name(),
		"physics": _craft.is_physics_processing(),
	})


func _validate_held_lock_and_post_move() -> void:
	var start_xz := _craft_xz()
	var reached_live := await _wait_for_state("LIVE", 240)
	_record("COUNTDOWN_REACHES_LIVE", reached_live, _run.state_name())
	if not reached_live:
		Input.action_release("throttle")
		return
	for _index in 4:
		await _physics_tail()
	var held_displacement := _craft_xz().distance_to(start_xz)
	var held_speed := Vector2(_craft.velocity.x, _craft.velocity.z).length()
	_record("HELD_INPUT_LOCK_THROUGH_GO", bool(_craft.get("_input_locked_until_release")) and held_displacement <= POSITION_TOLERANCE_M and held_speed <= POSITION_TOLERANCE_M, {
		"locked": _craft.get("_input_locked_until_release"),
		"displacement": held_displacement,
		"speed": held_speed,
	})
	Input.action_release("throttle")
	await _physics_tail()
	_record("INPUT_LOCK_CLEARS_AFTER_RELEASE", not bool(_craft.get("_input_locked_until_release")), _craft.get("_input_locked_until_release"))
	var movement_start := _craft_xz()
	Input.action_press("throttle", 1.0)
	for _index in 5:
		await _physics_tail()
	Input.action_release("throttle")
	var movement_end := _craft_xz()
	_record("FIRST_POST_GO_PRESS_MOVES", movement_end.distance_to(movement_start) > POSITION_TOLERANCE_M, {
		"start": movement_start,
		"end": movement_end,
		"distance": movement_end.distance_to(movement_start),
	})
	_record("RUN_SAMPLES_POST_MOVE_POSITION", _run.previous_craft_xz.distance_to(movement_end) <= POSITION_TOLERANCE_M and _run.last_post_move_craft_xz.distance_to(movement_end) <= POSITION_TOLERANCE_M, {
		"craft": movement_end,
		"previous": _run.previous_craft_xz,
		"last_post_move": _run.last_post_move_craft_xz,
	})


func _validate_longest_streak() -> void:
	_craft.set_physics_process(false)
	_run._clear_attempt_metrics()
	_craft.fold_amount = 1.0
	_craft.velocity = -_craft.global_basis.z * 30.0
	_run.previous_craft_xz = _craft_xz()
	_run._physics_process(0.4)
	_run._physics_process(0.4)
	_craft.fold_amount = 0.0
	_craft.velocity = Vector3.ZERO
	_run._physics_process(0.2)
	_record("LONGEST_STREAK_SURVIVES_BREAK", is_zero_approx(_run.streak_s) and absf(_run.longest_streak_s - 0.8) <= 0.00001, {
		"current": _run.streak_s,
		"longest": _run.longest_streak_s,
	})
	_run.start_attempt()


func _validate_pause_and_live_fall() -> void:
	var reached_live := await _wait_for_state("LIVE", 240)
	_record("SECOND_COUNTDOWN_REACHES_LIVE", reached_live, _run.state_name())
	if not reached_live:
		return
	await _physics_tail()
	var clock_before_pause: float = _run.run_time_s
	paused = true
	for _index in 3:
		await _physics_tail()
	_record("PAUSE_FREEZES_RUN_TIME", is_equal_approx(_run.run_time_s, clock_before_pause), {
		"before": clock_before_pause,
		"after": _run.run_time_s,
	})
	paused = false

	# Make every per-attempt metric nonzero so the fall must visibly clear it.
	_run.run_time_s = 5.0
	_run.brrr = 10.0
	_run.streak_s = 2.0
	_run.longest_streak_s = 3.0
	_run.drive_seconds = 1.0
	_run.peak_speed = 25.0
	_run.peak_split_degrees = 30.0
	var fall_reset_before := _craft.reset_count
	var reason_index := reset_reasons.size()
	var fall_restart_before: int = _run.fall_restart_count
	var attempt_before: int = _run.attempt_serial
	_craft.global_position.y = _craft.tuning.fall_reset_y - 0.5
	await _physics_tail()
	var fall_reasons := reset_reasons.slice(reason_index)
	_record("LIVE_FALL_ONE_R7_RESET", _craft.reset_count == fall_reset_before + 1 and fall_reasons.size() == 1 and String(fall_reasons[0]).begins_with("fell below"), {
		"count_delta": _craft.reset_count - fall_reset_before,
		"reasons": fall_reasons,
	})
	_record("LIVE_FALL_NO_SECOND_RUN_RESET", not ("run_retry" in fall_reasons) and _run.fall_restart_count == fall_restart_before + 1 and _run.attempt_serial == attempt_before + 1, {
		"reasons": fall_reasons,
		"fall_restart_delta": _run.fall_restart_count - fall_restart_before,
		"attempt_delta": _run.attempt_serial - attempt_before,
	})
	_record("LIVE_FALL_ENTERS_FROZEN_COUNTDOWN", _run.state_name() == "COUNTDOWN" and not _craft.is_physics_processing(), {
		"state": _run.state_name(),
		"physics": _craft.is_physics_processing(),
	})
	_record("LIVE_FALL_R7_COMPLETED_TELEPORT", _craft.global_position.distance_to(_run.run_start_transform.origin) <= POSITION_TOLERANCE_M and _craft.velocity.is_zero_approx() and _craft.regime_name() == "SPREAD", {
		"position": _craft.global_position,
		"expected": _run.run_start_transform.origin,
		"velocity": _craft.velocity,
		"regime": _craft.regime_name(),
	})
	_record("LIVE_FALL_CLEARS_ATTEMPT", is_zero_approx(_run.run_time_s) and is_zero_approx(_run.brrr) and is_zero_approx(_run.streak_s) and is_zero_approx(_run.longest_streak_s) and is_zero_approx(_run.drive_seconds) and is_zero_approx(_run.peak_speed) and is_zero_approx(_run.peak_split_degrees), {
		"time": _run.run_time_s,
		"brrr": _run.brrr,
		"streak": _run.streak_s,
		"longest": _run.longest_streak_s,
		"drive": _run.drive_seconds,
		"peak_speed": _run.peak_speed,
		"peak_split": _run.peak_split_degrees,
	})
	_record("LIVE_FALL_PRESERVES_INPUT_LOCK", bool(_craft.get("_input_locked_until_release")), _craft.get("_input_locked_until_release"))
	_record("LIVE_FALL_CAMERA_SNAPPED", int(_gate.camera_rig.get("_last_reset_count")) == _craft.reset_count, {
		"camera": _gate.camera_rig.get("_last_reset_count"),
		"craft": _craft.reset_count,
	})


func _validate_integrated_tunneling_finish() -> void:
	_run.set_physics_process(false)
	_craft.set_physics_process(false)
	_run._clear_attempt_metrics()
	_run.state = 2 # RunState.LIVE
	var p0: Vector2 = _run.finish_center_xz + Vector2(-20.0, 0.0)
	var p1: Vector2 = _run.finish_center_xz + Vector2(20.0, 0.0)
	_run.previous_craft_xz = p0
	_craft.global_position = Vector3(p1.x, 5.0, p1.y)
	_craft.velocity = Vector3.ZERO
	_craft.fold_amount = 0.0
	_run._physics_process(1.0 / 60.0)
	_record("FINISH_TUNNEL_INTEGRATED", _run.state_name() == "RESULTS" and not _craft.is_physics_processing() and not _run.last_result.is_empty(), {
		"state": _run.state_name(),
		"physics": _craft.is_physics_processing(),
		"result": _run.last_result,
		"endpoint_distances": [p0.distance_to(_run.finish_center_xz), p1.distance_to(_run.finish_center_xz)],
	})
	_record("FINISH_RECORDS_LONGEST_STREAK_FIELD", _run.last_result.has("longest_streak_s"), _run.last_result)


func _wait_for_state(expected: String, maximum_ticks: int) -> bool:
	for _index in maximum_ticks:
		if _run.state_name() == expected:
			return true
		await _physics_tail()
	return _run.state_name() == expected


func _physics_tail() -> void:
	_fence.armed = true
	await _fence.physics_tail


func _push_physical_key(key: Key, pressed: bool) -> void:
	var event := InputEventKey.new()
	event.physical_keycode = key
	event.keycode = key
	event.pressed = pressed
	event.echo = false
	root.push_input(event)


func _craft_xz() -> Vector2:
	return Vector2(_craft.global_position.x, _craft.global_position.z)


func _collect_reset_reason(_count: int, reason: String) -> void:
	reset_reasons.append(reason)


func _record(id: String, passed: bool, detail = null) -> void:
	checks.append({"id": id, "status": "PASS" if passed else "FAIL", "detail": _json_safe(detail)})
	if not passed:
		failures.append(id)


func _json_safe(value):
	if value is Vector2:
		return [value.x, value.y]
	if value is Vector3:
		return [value.x, value.y, value.z]
	if value is Transform3D:
		return {"origin": _json_safe(value.origin)}
	if value is Array:
		var converted: Array = []
		for item in value:
			converted.append(_json_safe(item))
		return converted
	if value is Dictionary:
		var converted := {}
		for key in value:
			converted[String(key)] = _json_safe(value[key])
		return converted
	return value


func _finish() -> void:
	Input.action_release("throttle")
	paused = false
	var result := {
		"schema": "district_zero.run_v0.disposable_behavior_probe.v1",
		"status": "PASS" if failures.is_empty() else "FAIL",
		"engine_identity": _engine_identity(),
		"check_count": checks.size(),
		"failure_count": failures.size(),
		"failures": failures,
		"checks": checks,
	}
	var result_path := _arg("--result")
	if not result_path.is_empty():
		var output := FileAccess.open(result_path, FileAccess.WRITE)
		if output != null:
			output.store_string(JSON.stringify(result, "  ") + "\n")
			output.close()
	print("RUN_V0_PROBE_RESULT " + JSON.stringify(result))
	if _scene != null:
		_scene.queue_free()
	quit(0 if failures.is_empty() else 1)


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
