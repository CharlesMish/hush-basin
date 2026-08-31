extends SceneTree

const RESULT_PREFIX := "P1A_TELEMETRY_POLICY_RESULT "

var failures: Array[String] = []
var observed_signal_count := 0


func _initialize() -> void:
	call_deferred("_run")


func _run() -> void:
	_check(not P1ATelemetry.console_output_requested(PackedStringArray()), "ordinary play must not request JSONL console output")
	_check(P1ATelemetry.console_output_requested(PackedStringArray(["--vector", "RT_BOUNDARY_CORE_WALL_DRIVE"])), "runtime vector must request JSONL console output")
	_check(P1ATelemetry.console_output_requested(PackedStringArray([P1ATelemetry.CONSOLE_JSONL_ARGUMENT])), "explicit JSONL argument must request console output")
	_check(not P1ATelemetry.console_output_requested(PackedStringArray(["--mode", "capture"])), "human capture must not request JSONL console output")
	_check(not P1ATelemetry.console_output_requested(PackedStringArray(["--mode", "replay"])), "human replay must not request JSONL console output")

	var telemetry := P1ATelemetry.new()
	root.add_child(telemetry)
	telemetry.event_emitted.connect(_on_event)
	telemetry.configure(null, null)
	var expected_console := P1ATelemetry.console_output_requested(OS.get_cmdline_user_args())
	_check(telemetry.console_jsonl_enabled == expected_console, "configure must apply the callable console-output policy")
	telemetry.emit_event({"event": "ROBUSTNESS_POLICY_PROBE", "payload": "preserved"})
	_check(telemetry.events.size() == 1, "event must remain in the bounded queue")
	_check(observed_signal_count == 1, "event signal must remain intact")
	_check(int(telemetry.events[0].get("serial", -1)) == 1, "event serial must remain intact")
	_check(int(telemetry.events[0].get("physics_tick", -1)) == 0, "event physics tick must remain intact")

	var result := {
		"schema": "district_zero.p1a.telemetry_output_policy_test.v1",
		"status": "PASS" if failures.is_empty() else "FAIL",
		"console_jsonl_enabled": telemetry.console_jsonl_enabled,
		"event_queue_count": telemetry.events.size(),
		"signal_count": observed_signal_count,
		"failures": failures,
	}
	print(RESULT_PREFIX + JSON.stringify(result))
	quit(0 if failures.is_empty() else 1)


func _on_event(_event: Dictionary) -> void:
	observed_signal_count += 1


func _check(condition: bool, message: String) -> void:
	if not condition:
		failures.append(message)
