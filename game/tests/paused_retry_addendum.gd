extends SceneTree

const RUN_SCENE := preload("res://scenes/district_zero_run.tscn")
const EXACT_ENGINE := "4.7.1.stable.official.a13da4feb"


class PhysicsFence:
	extends Node
	signal physics_tail
	var armed := false

	func _ready() -> void:
		process_mode = Node.PROCESS_MODE_ALWAYS
		process_physics_priority = 1000

	func _physics_process(_delta: float) -> void:
		if armed:
			armed = false
			physics_tail.emit()


var checks: Array[Dictionary] = []
var failures: Array[String] = []
var reasons: Array[String] = []
var fence: PhysicsFence
var run_scene: Node
var gate: P1AWorldGate
var run: Node
var craft: CraftController


func _initialize() -> void:
	_execute.call_deferred()


func _execute() -> void:
	_record("EXACT_ENGINE", _engine_identity() == EXACT_ENGINE, _engine_identity())
	run_scene = RUN_SCENE.instantiate()
	root.add_child(run_scene)
	fence = PhysicsFence.new()
	root.add_child(fence)
	await process_frame
	await process_frame
	gate = run_scene.get_node("DistrictZeroP1A") as P1AWorldGate
	run = run_scene.get_node("RunLayer")
	craft = gate.craft
	craft.reset_performed.connect(_on_reset)

	var reached_live := await _wait_for_state("LIVE", 240)
	_record("PRECONDITION_LIVE", reached_live, run.state_name())
	if not reached_live:
		_finish()
		return
	await _tail()
	var position_before := craft.global_position
	var reset_before := craft.reset_count
	var reason_before := reasons.size()
	var retry_before: int = run.manual_retry_count
	var signal_before: int = run.reset_signal_count
	paused = true
	_record("SCENE_TREE_PAUSED", paused, paused)

	_push_key(KEY_R, true)
	var handled_after_press := root.is_input_handled()
	_push_key(KEY_R, false)
	var new_reasons := reasons.slice(reason_before)
	_record("PAUSED_R_HANDLED_BY_RUN", handled_after_press, handled_after_press)
	_record("PAUSED_R_EXACTLY_ONE_RESET", craft.reset_count == reset_before + 1 and new_reasons.size() == 1, {
		"reset_delta": craft.reset_count - reset_before,
		"reasons": new_reasons,
	})
	_record("PAUSED_R_IS_RUN_RETRY_ONLY", new_reasons == ["run_retry"] and craft.last_reset_reason == "run_retry" and not ("manual" in new_reasons), {
		"reasons": new_reasons,
		"last_reset_reason": craft.last_reset_reason,
	})
	_record("PAUSED_R_ONE_MANUAL_RETRY", run.manual_retry_count == retry_before + 1 and run.reset_signal_count == signal_before + 1, {
		"manual_retry_delta": run.manual_retry_count - retry_before,
		"reset_signal_delta": run.reset_signal_count - signal_before,
	})
	_record("PAUSED_R_ENTERS_COUNTDOWN", run.state_name() == "COUNTDOWN" and not craft.is_physics_processing(), {
		"state": run.state_name(),
		"craft_physics": craft.is_physics_processing(),
	})
	_record("PAUSED_R_RESETS_QRY_AND_METRICS", craft.global_position.distance_to(run.run_start_transform.origin) <= 0.0001 and craft.velocity.is_zero_approx() and craft.regime_name() == "SPREAD" and is_zero_approx(run.run_time_s) and is_zero_approx(run.brrr), {
		"before": position_before,
		"after": craft.global_position,
		"expected": run.run_start_transform.origin,
		"regime": craft.regime_name(),
		"time": run.run_time_s,
		"brrr": run.brrr,
	})
	var countdown_at_pause: float = run.get("_countdown_remaining_s")
	_record("PAUSED_R_FULL_COUNTDOWN", absf(countdown_at_pause - 1.8) <= 0.00001, countdown_at_pause)
	for _index in 6:
		await _tail()
	_record("PAUSED_COUNTDOWN_REMAINS_FROZEN", run.state_name() == "COUNTDOWN" and is_equal_approx(float(run.get("_countdown_remaining_s")), countdown_at_pause) and not craft.is_physics_processing(), {
		"state": run.state_name(),
		"before": countdown_at_pause,
		"after": run.get("_countdown_remaining_s"),
		"craft_physics": craft.is_physics_processing(),
	})
	_record("PAUSED_WAIT_ADDS_NO_RESETS", craft.reset_count == reset_before + 1 and reasons.slice(reason_before) == ["run_retry"], {
		"reset_delta": craft.reset_count - reset_before,
		"reasons": reasons.slice(reason_before),
	})

	_push_key(KEY_ESCAPE, true)
	_push_key(KEY_ESCAPE, false)
	_record("ESC_RESUMES_TREE", not paused, paused)
	var resumed_live := await _wait_for_state("LIVE", 240)
	_record("COUNTDOWN_RESUMES_TO_LIVE", resumed_live and craft.is_physics_processing(), {
		"state": run.state_name(),
		"craft_physics": craft.is_physics_processing(),
	})
	_record("RESUME_ADDS_NO_RESET", craft.reset_count == reset_before + 1 and reasons.slice(reason_before) == ["run_retry"], {
		"reset_delta": craft.reset_count - reset_before,
		"reasons": reasons.slice(reason_before),
	})
	_finish()


func _wait_for_state(expected: String, maximum_ticks: int) -> bool:
	for _index in maximum_ticks:
		if run.state_name() == expected:
			return true
		await _tail()
	return run.state_name() == expected


func _tail() -> void:
	fence.armed = true
	await fence.physics_tail


func _push_key(key: Key, is_pressed: bool) -> void:
	var event := InputEventKey.new()
	event.physical_keycode = key
	event.keycode = key
	event.pressed = is_pressed
	event.echo = false
	root.push_input(event)


func _on_reset(_count: int, reason: String) -> void:
	reasons.append(reason)


func _record(id: String, passed: bool, detail = null) -> void:
	checks.append({"id": id, "status": "PASS" if passed else "FAIL", "detail": _safe(detail)})
	if not passed:
		failures.append(id)


func _safe(value):
	if value is Vector3:
		return [value.x, value.y, value.z]
	if value is Array:
		var converted: Array = []
		for item in value:
			converted.append(_safe(item))
		return converted
	if value is Dictionary:
		var converted := {}
		for key in value:
			converted[String(key)] = _safe(value[key])
		return converted
	return value


func _finish() -> void:
	paused = false
	var result := {
		"schema": "district_zero.run_v0.paused_retry_addendum.v1",
		"status": "PASS" if failures.is_empty() else "FAIL",
		"engine_identity": _engine_identity(),
		"check_count": checks.size(),
		"failure_count": failures.size(),
		"failures": failures,
		"checks": checks,
	}
	var result_path := _arg("--result")
	if not result_path.is_empty():
		var file := FileAccess.open(result_path, FileAccess.WRITE)
		file.store_string(JSON.stringify(result, "  ") + "\n")
		file.close()
	print("RUN_V0_PAUSED_RETRY_RESULT " + JSON.stringify(result))
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
