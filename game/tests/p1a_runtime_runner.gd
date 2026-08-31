extends SceneTree

const VECTOR_PATH := "res://tests/fixtures/runtime_vectors.json"
const V5_CANDIDATE_PATH := "res://tests/fixtures/fast_route_driver_v5_candidates.json"
const V6_CANDIDATE_PATH := "res://tests/fixtures/fast_route_driver_v6_candidates.json"
const V7_CANDIDATE_PATH := "res://tests/fixtures/fast_route_driver_v7_candidates.json"
const HUMAN_REPLAY_CONTROLLER := "NORMALIZED_INPUT_TRACE_REPLAY_V1"
const MAIN_SCENE := preload("res://scenes/district_zero_p1a.tscn")
const ACTIONS := ["throttle", "brake", "steer_left", "steer_right", "transform", "hop"]
const IMPLEMENTED_COMMANDS := ["ASSERT_SELECTION","END","HOP_PRESS","HOP_RELEASE","MANUAL_RESET_WITH_R","OPEN_DIAGNOSTIC_MENU","PREVIOUS_SELECTION","SET_POSITION_Y_FOR_FALL_TEST","SPAWN_SELECTED_WITH_ENTER","THROTTLE"]
const IMPLEMENTED_THRESHOLD_KEYS := ["default_diagnostic_selection","default_spawn_id","exact_allowed_input_actions","exact_gate_crossing_count","exact_hop_started_count","expected_test_driver_liveness_sample_count","fast_route_speed_floor_mps","hop_started_before_bar_contact_plane","legacy_selector_action_count","maximum_core_plinth_collision_count","maximum_craft_center_samples_inside_hard_obstacle","maximum_crossings_to_opposite_side_of_target_face","maximum_fall_reset_count","maximum_hard_collision_count","maximum_hard_obstacle_penetration_samples","maximum_hop_bar_collision_count","maximum_hop_bar_hje_clear_crossing_count","maximum_hop_bar_span_crossing_count","maximum_hop_command_to_start_ticks","maximum_hop_end_bypass_crossing_count","maximum_non_hop_hard_collision_count","maximum_route_entered_event_count","maximum_route_entered_or_traversed_events_caused_by_spawn_or_reset","maximum_route_traversed_event_count","maximum_test_driver_path_deviation_m","minimum_HOP_BAR_HJE_CLEAR_crossing_count","minimum_bar_overlap_vertical_clearance_m","minimum_distance_at_or_above_fast_route_speed_m","minimum_first_liveness_horizontal_speed_mps","minimum_genuine_classified_distance_m","minimum_hop_bar_collision_count","minimum_hop_started_count","minimum_peak_horizontal_speed_mps","minimum_positive_throttle_fraction","minimum_support_ready_consecutive_ticks","movement_tuning_digest_algorithm_id","movement_tuning_digest_before_equals_after","required_event_order","required_first_hard_geometry_id","required_liveness_every_tick","required_movement_tuning_digest_after","required_movement_tuning_digest_before","required_neutral_spawn_selection_id","required_surface_class_sequence","support_ready_before_hop_command","target_face_plane_id","visible_build_label_exact"]
const EXPECTED_CUSTOM_INPUT_ACTIONS := ["brake","debug_overlay","diagnostic_menu","diagnostic_next","diagnostic_prev","diagnostic_spawn","hop","pause","reset","steer_left","steer_right","throttle","transform"]
const TUNING_DIGEST_ALGORITHM_ID := "DZP1A_TUNING_SHA256_V1"

var gate_root: P1AWorldGate
var craft: CraftController
var telemetry: P1ATelemetry
var data: P1AWorldData
var fixture: Dictionary
var vector: Dictionary
var vector_tick := 0
var observed: Array[Dictionary] = []
var route_cache := {}
var crossing_states := {}
var obstacle_inside_samples := 0
var maximum_chainage := 0.0
var hop_press_sent := false
var multi_segment := 0
var scripted_throttle := 0.0
var scripted_hop := false
var collision_window_start_tick := 0
var collision_window_end_tick := 0
var previous_observation_point := Vector2.ZERO
var maximum_lateral_error_m := 0.0
var peak_horizontal_speed_mps := 0.0
var distance_at_or_above_fast_speed_m := 0.0
var previous_metric_point := Vector2.ZERO
var command_assertion_failures: Array[String] = []
var preflight_failures: Array[String] = []
var movement_tuning_digest_before := ""
var movement_tuning_digest_after := ""
var powered_waypoint_index := 0
var active_controller_throttle := 0.0
var liveness_records: Array[Dictionary] = []
var maximum_test_driver_path_deviation_m := 0.0
var maximum_liveness_path_deviation_m := 0.0
var route_driver_plans := {}
var route_projection_records: Array[Dictionary] = []
var last_v4_control: Dictionary = {}
var last_v5_control: Dictionary = {}
var v5_candidate_registry: Dictionary = {}
var v5_candidate_id := ""
var v5_candidate: Dictionary = {}
var first_hard_limit_violation: Dictionary = {}
var last_v6_control: Dictionary = {}
var v6_candidate_registry: Dictionary = {}
var v6_candidate_id := ""
var v6_candidate: Dictionary = {}
var v6_slowdown_window_ticks := 0
var v6_slowdown_window_cumulative_speed_change_mps := 0.0
var v6_slowdown_health_violation: Dictionary = {}
var last_v7_control: Dictionary = {}
var v7_candidate_registry: Dictionary = {}
var v7_candidate_id := ""
var v7_candidate: Dictionary = {}
var v7_phase := "ACCELERATE"
var v7_phase_enter_vector_tick := 0
var v7_brake_health_window_ticks := 0
var v7_brake_health_cumulative_speed_change_mps := 0.0
var v7_brake_health_violation: Dictionary = {}
var human_input_trace_path := ""
var human_input_trace: Dictionary = {}
var human_input_records: Array = []
var last_human_control: Dictionary = {}
var terminal_evidence_sealed := false
var terminal_result_emitted := false
var post_result_event_count := 0
var minimum_required_window_distance_m := INF
var powered_required_window_closest_sample: Dictionary = {}
var support_ready_consecutive := 0
var maximum_support_ready_consecutive := 0
var support_ready_tick := -1
var hop_command_tick := -1
var hop_command_x_m := INF
var hop_trigger_x_m := INF
var hop_timing_offset_m := INF
var minimum_bar_overlap_vertical_clearance_m := INF
var bar_overlap_clearance_sample_count := 0
var first_hop_started_x_m := INF
var first_hard_geometry_id := ""
var first_hard_collision_tick := -1
var first_hop_bar_contact_tick := -1
var termination_completed := false
var termination_reason := ""
var termination_physics_tick := -1
var termination_vector_tick := -1
var termination_window_id := ""


func _initialize() -> void:
	call_deferred("_run")


func _run() -> void:
	var requested := _argument_value("--vector")
	if requested.is_empty():
		printerr("P1A_RUNTIME_RESULT " + JSON.stringify({"status": "BLOCKED/NOT TESTABLE", "reason": "--vector is required", "physics_ticks": 0, "runtime_phase": "PRE_PHYSICS"}))
		quit(2)
		return
	var parsed = JSON.parse_string(FileAccess.get_file_as_string(VECTOR_PATH))
	if not parsed is Dictionary:
		printerr("P1A_RUNTIME_RESULT " + JSON.stringify({"status": "BLOCKED/NOT TESTABLE", "reason": "runtime vector fixture parse failed", "physics_ticks": 0, "runtime_phase": "PRE_PHYSICS"}))
		quit(2)
		return
	fixture = parsed
	for value in fixture.vectors:
		if String(value.id) == requested:
			vector = value
			break
	if vector.is_empty():
		printerr("P1A_RUNTIME_RESULT " + JSON.stringify({"status": "BLOCKED/NOT TESTABLE", "reason": "unknown vector", "id": requested, "physics_ticks": 0, "runtime_phase": "PRE_PHYSICS"}))
		quit(2)
		return
	var controller_type := String(vector.get("controller_commands", {}).get("type", ""))
	if controller_type == HUMAN_REPLAY_CONTROLLER:
		human_input_trace_path = _argument_value("--input-trace")
		var human_parsed = JSON.parse_string(FileAccess.get_file_as_string(human_input_trace_path)) if not human_input_trace_path.is_empty() else null
		if not human_parsed is Dictionary:
			printerr("P1A_RUNTIME_RESULT " + JSON.stringify({"status": "BLOCKED/NOT TESTABLE", "reason": "normalized human input trace is absent or invalid", "id": requested, "physics_ticks": 0, "runtime_phase": "PRE_PHYSICS"}))
			quit(2)
			return
		human_input_trace = human_parsed
		human_input_records = human_input_trace.get("records", [])
	if controller_type == "ROUTE_FOLLOWER_INPUT_CONTROLLER_V5_INERTIAL_THRUST_VECTOR_CONTAINED":
		v5_candidate_id = _argument_value("--v5-candidate-id")
		var candidate_parsed = JSON.parse_string(FileAccess.get_file_as_string(V5_CANDIDATE_PATH))
		if not candidate_parsed is Dictionary or v5_candidate_id.is_empty():
			printerr("P1A_RUNTIME_RESULT " + JSON.stringify({"status": "BLOCKED/NOT TESTABLE", "reason": "V5 candidate registry or --v5-candidate-id is absent", "id": requested, "physics_ticks": 0, "runtime_phase": "PRE_PHYSICS"}))
			quit(2)
			return
		v5_candidate_registry = candidate_parsed
		for candidate_value in v5_candidate_registry.get("candidates", []):
			var candidate_record: Dictionary = candidate_value
			if String(candidate_record.get("id", "")) == v5_candidate_id:
				v5_candidate = candidate_record
				break
		if v5_candidate.is_empty():
			printerr("P1A_RUNTIME_RESULT " + JSON.stringify({"status": "BLOCKED/NOT TESTABLE", "reason": "unknown V5 candidate", "candidate_id": v5_candidate_id, "id": requested, "physics_ticks": 0, "runtime_phase": "PRE_PHYSICS"}))
			quit(2)
			return
	if controller_type == "ROUTE_FOLLOWER_INPUT_CONTROLLER_V6_DECEL_CONSTRAINED_THRUST_VECTOR_CONTAINED":
		v6_candidate_id = _argument_value("--v6-candidate-id")
		var v6_parsed = JSON.parse_string(FileAccess.get_file_as_string(V6_CANDIDATE_PATH))
		if not v6_parsed is Dictionary or v6_candidate_id.is_empty():
			printerr("P1A_RUNTIME_RESULT " + JSON.stringify({"status": "BLOCKED/NOT TESTABLE", "reason": "V6 candidate registry or --v6-candidate-id is absent", "id": requested, "physics_ticks": 0, "runtime_phase": "PRE_PHYSICS"}))
			quit(2)
			return
		v6_candidate_registry = v6_parsed
		for candidate_value in v6_candidate_registry.get("candidates", []):
			var candidate_record: Dictionary = candidate_value
			if String(candidate_record.get("id", "")) == v6_candidate_id:
				v6_candidate = candidate_record
				break
		if v6_candidate.is_empty():
			printerr("P1A_RUNTIME_RESULT " + JSON.stringify({"status": "BLOCKED/NOT TESTABLE", "reason": "unknown V6 candidate", "candidate_id": v6_candidate_id, "id": requested, "physics_ticks": 0, "runtime_phase": "PRE_PHYSICS"}))
			quit(2)
			return
	if controller_type == "ROUTE_FOLLOWER_INPUT_CONTROLLER_V7_PHASE_SEPARATED_BRAKE_CAPTURE_CONTAINED":
		v7_candidate_id = _argument_value("--v7-candidate-id")
		var v7_parsed = JSON.parse_string(FileAccess.get_file_as_string(V7_CANDIDATE_PATH))
		if not v7_parsed is Dictionary or v7_candidate_id.is_empty():
			printerr("P1A_RUNTIME_RESULT " + JSON.stringify({"status": "BLOCKED/NOT TESTABLE", "reason": "V7 candidate registry or --v7-candidate-id is absent", "id": requested, "physics_ticks": 0, "runtime_phase": "PRE_PHYSICS"}))
			quit(2)
			return
		v7_candidate_registry = v7_parsed
		for candidate_value in v7_candidate_registry.get("candidates", []):
			var candidate_record: Dictionary = candidate_value
			if String(candidate_record.get("id", "")) == v7_candidate_id:
				v7_candidate = candidate_record
				break
		if v7_candidate.is_empty():
			printerr("P1A_RUNTIME_RESULT " + JSON.stringify({"status": "BLOCKED/NOT TESTABLE", "reason": "unknown V7 candidate", "candidate_id": v7_candidate_id, "id": requested, "physics_ticks": 0, "runtime_phase": "PRE_PHYSICS"}))
			quit(2)
			return
	gate_root = MAIN_SCENE.instantiate() as P1AWorldGate
	get_root().add_child(gate_root)
	await process_frame
	craft = gate_root.craft
	telemetry = gate_root.telemetry
	data = gate_root.data
	telemetry.event_emitted.connect(_on_event)
	_prepare_route_cache()
	preflight_failures = _validate_vector_contract()
	if not preflight_failures.is_empty():
		_release_actions()
		printerr("P1A_RUNTIME_RESULT " + JSON.stringify({
			"status": "BLOCKED/NOT TESTABLE",
			"runtime_phase": "PRE_PHYSICS",
			"process_exit_contract_id": "DZP1A_RUNTIME_RESULT_EXIT_V1",
			"id": requested,
			"physics_ticks": 0,
			"event_count": 0,
			"failures": preflight_failures,
			"reason": "runtime vector contract/preflight validation failed",
		}))
		quit(2)
		return
	_release_actions()
	_apply_initial_state()
	_initialize_crossing_states()
	collision_window_start_tick = telemetry.physics_tick + 1
	if vector.get("thresholds", {}).has("movement_tuning_digest_algorithm_id"):
		movement_tuning_digest_before = _movement_tuning_digest()
	var max_ticks := _maximum_ticks()
	for tick in max_ticks + 1:
		vector_tick = tick
		_apply_commands(tick)
		_observe_thresholds_before_tick()
		await physics_frame
		_observe_thresholds_after_tick()
		if _termination_reached():
			break
	collision_window_end_tick = telemetry.physics_tick
	var termination_contract: Dictionary = vector.get("termination", {})
	if String(termination_contract.get("type", "")) == "FIRST_VALID_HOP_CLEARANCE" and not termination_completed:
		termination_reason = "TIMEOUT_NO_VALID_HOP_CLEARANCE"
		termination_physics_tick = telemetry.physics_tick
		termination_vector_tick = vector_tick
		termination_window_id = String(termination_contract.get("window_id", ""))
	if vector.get("thresholds", {}).has("movement_tuning_digest_algorithm_id"):
		movement_tuning_digest_after = _movement_tuning_digest()
	_release_actions()
	var failures := _evaluate()
	var genuine_distance := _genuine_distance_evidence()
	var result := {
		"status": "PASS" if failures.is_empty() else "FAIL",
		"runtime_phase": "GAMEPLAY_COMPLETE",
		"process_exit_contract_id": "DZP1A_RUNTIME_RESULT_EXIT_V1",
		"id": String(vector.id),
		"physics_ticks": vector_tick,
		"event_count": observed.size(),
		"failures": failures,
		"route_states": _event_summary("ROUTE_STATE"),
		"gate_crossings": _event_summary("GATE_CROSSED"),
		"hard_collisions": _hard_collision_count(false),
		"fall_resets": _reset_count("FALL"),
		"hop_starts": _event_count("HOP_STARTED"),
		"crossing_windows": _crossing_results(),
		"plane_crossings": _all_window_crossing_count(),
		"plane_crossing_points": _all_window_crossing_points(),
		"maximum_plane_distance": _maximum_window_signed_distance(),
		"obstacle_inside_samples": obstacle_inside_samples,
		"maximum_chainage_m": maximum_chainage,
		"genuine_classified_distance": genuine_distance,
		"movement_tuning_digest": {
			"algorithm_id": TUNING_DIGEST_ALGORITHM_ID,
			"before": movement_tuning_digest_before,
			"after": movement_tuning_digest_after,
			"field_count": int(fixture.global_rules.movement_tuning_digest.field_count),
		},
		"collision_window": {"start_physics_tick": collision_window_start_tick, "end_physics_tick": collision_window_end_tick, "inclusive": true},
		"termination_evidence": {"contract_type": String(vector.get("termination", {}).get("type", "FIXED_OR_ROUTE")), "completed": termination_completed, "reason": termination_reason, "physics_tick": termination_physics_tick, "vector_tick": termination_vector_tick, "window_id": termination_window_id, "completion_tick_inclusive": bool(vector.get("termination", {}).get("completion_tick_inclusive", true)), "timeout_tick": vector.get("termination", {}).get("timeout_tick", null)},
		"final_position_xyz_m": [craft.global_position.x, craft.global_position.y, craft.global_position.z],
		"final_velocity_xyz_mps": [craft.velocity.x, craft.velocity.y, craft.velocity.z],
		"final_effective_thrust": craft.effective_thrust,
		"final_input_throttle": Input.get_action_strength("throttle"),
		"collision_sources": _collision_sources(),
		"maximum_lateral_error_m": maximum_lateral_error_m,
		"peak_horizontal_speed_mps": peak_horizontal_speed_mps,
		"distance_at_or_above_fast_speed_m": distance_at_or_above_fast_speed_m,
		"test_driver_liveness": _liveness_summary(),
		"test_driver_route_projection": _fast_route_projection_summary(),
		"first_unauthorized_hard_collision": _first_unauthorized_hard_collision(),
		"first_hard_lateral_limit_violation": first_hard_limit_violation.duplicate(true),
		"v5_candidate_id": v5_candidate_id if not v5_candidate_id.is_empty() else null,
		"v6_candidate_id": v6_candidate_id if not v6_candidate_id.is_empty() else null,
		"v6_slowdown_health_violation": v6_slowdown_health_violation.duplicate(true),
		"v7_candidate_id": v7_candidate_id if not v7_candidate_id.is_empty() else null,
		"v7_brake_health_violation": v7_brake_health_violation.duplicate(true),
		"human_input_trace_sha256": FileAccess.get_sha256(human_input_trace_path) if not human_input_trace_path.is_empty() else null,
		"human_trace_id": String(human_input_trace.get("trace_id", "")) if not human_input_trace.is_empty() else null,
		"first_hop_started_physics_tick": _first_event_physics_tick("HOP_STARTED"),
		"hop_gate_evidence": {
			"support_ready_tick": support_ready_tick,
			"maximum_support_ready_consecutive_ticks": maximum_support_ready_consecutive,
			"hop_command_tick": hop_command_tick,
			"hop_command_x_m": hop_command_x_m if hop_command_x_m < INF else null,
			"hop_trigger_x_m": hop_trigger_x_m if hop_trigger_x_m < INF else null,
			"timing_offset_m": hop_timing_offset_m if hop_timing_offset_m < INF else null,
			"first_hop_started_x_m": first_hop_started_x_m if first_hop_started_x_m < INF else null,
			"minimum_bar_overlap_vertical_clearance_m": minimum_bar_overlap_vertical_clearance_m if minimum_bar_overlap_vertical_clearance_m < INF else null,
			"bar_overlap_clearance_sample_count": bar_overlap_clearance_sample_count,
			"first_hard_geometry_id": first_hard_geometry_id,
			"first_hard_collision_tick": first_hard_collision_tick,
			"first_hop_bar_contact_tick": first_hop_bar_contact_tick,
		},
	}
	_seal_terminal_evidence()
	result["terminal_evidence"] = {"sealed_before_result": terminal_evidence_sealed, "post_result_event_count": post_result_event_count, "result_count": 1, "collision_window_completion_tick_inclusive": true}
	terminal_result_emitted = true
	print("P1A_RUNTIME_RESULT " + JSON.stringify(result))
	quit(0 if failures.is_empty() else 1)
	return


func _apply_initial_state() -> void:
	telemetry.segment_boundary()
	observed.clear()
	var spawn: Dictionary = vector.get("spawn_transform", gate_root.data.diagnostic.initial_craft_spawn.transform)
	var position: Array = spawn.position_xyz_m
	var transform := Transform3D(Basis.IDENTITY.rotated(Vector3.UP, float(spawn.yaw_rad)), Vector3(float(position[0]), float(position[1]), float(position[2])))
	craft.set_spawn_transform(transform)
	craft.global_transform = transform
	craft.velocity = _initial_velocity(transform)
	craft.fold_amount = 1.0 if String(vector.get("initial_mode", "SPREAD")) == "DRIVE" else 0.0
	craft.set("_input_locked_until_release", false)
	craft.clear_pending_hop()
	craft.hop_cooldown_remaining = 0.0
	craft.hop_count = 0
	craft.reset_physics_interpolation()
	if String(vector.get("initial_mode", "SPREAD")) == "DRIVE":
		Input.action_press("transform", 1.0)
	previous_observation_point = Vector2(craft.global_position.x, craft.global_position.z)
	previous_metric_point = previous_observation_point
	powered_waypoint_index = 0
	liveness_records.clear()
	route_projection_records.clear()
	last_v4_control.clear()
	last_v5_control.clear()
	last_v6_control.clear()
	v6_slowdown_window_ticks = 0
	v6_slowdown_window_cumulative_speed_change_mps = 0.0
	v6_slowdown_health_violation.clear()
	last_v7_control.clear()
	last_human_control.clear()
	v7_phase = "ACCELERATE"
	v7_phase_enter_vector_tick = 0
	v7_brake_health_window_ticks = 0
	v7_brake_health_cumulative_speed_change_mps = 0.0
	v7_brake_health_violation.clear()
	first_hard_limit_violation.clear()
	terminal_evidence_sealed = false
	terminal_result_emitted = false
	post_result_event_count = 0
	maximum_test_driver_path_deviation_m = 0.0
	minimum_required_window_distance_m = INF
	powered_required_window_closest_sample.clear()
	support_ready_consecutive = 0
	maximum_support_ready_consecutive = 0
	support_ready_tick = -1
	hop_command_tick = -1
	hop_command_x_m = INF
	hop_trigger_x_m = INF
	minimum_bar_overlap_vertical_clearance_m = INF
	bar_overlap_clearance_sample_count = 0
	first_hop_started_x_m = INF
	first_hard_geometry_id = ""
	first_hard_collision_tick = -1
	first_hop_bar_contact_tick = -1
	termination_completed = false
	termination_reason = ""
	termination_physics_tick = -1
	termination_vector_tick = -1
	termination_window_id = ""
	hop_timing_offset_m = _resolved_hop_timing_offset(vector.get("controller_commands", {})) if String(vector.get("controller_commands", {}).get("type", "")) == "SUPPORTED_HOP_BRACKET_CONTROLLER" else INF


func _initial_velocity(transform: Transform3D) -> Vector3:
	if vector.has("initial_linear_velocity_xyz_mps"):
		var raw: Array = vector.initial_linear_velocity_xyz_mps
		return Vector3(float(raw[0]), float(raw[1]), float(raw[2]))
	if vector.has("initial_linear_velocity_route_tangent_mps"):
		var source: Dictionary = vector.spawn_transform.source
		var route_id := String(source.route)
		var cache: Dictionary = route_cache[route_id]
		var sample := _route_sample(route_id, float(source.chainage_m))
		var tangent: Vector2 = sample.tangent
		if String(source.get("direction", "FORWARD")) == "REVERSE":
			tangent = -tangent
		return Vector3(tangent.x, 0.0, tangent.y) * float(vector.initial_linear_velocity_route_tangent_mps)
	return Vector3.ZERO


func _apply_commands(tick: int) -> void:
	Input.action_release("throttle")
	Input.action_release("brake")
	Input.action_release("steer_left")
	Input.action_release("steer_right")
	if String(vector.get("initial_mode", "SPREAD")) == "DRIVE":
		Input.action_press("transform", 1.0)
	else:
		Input.action_release("transform")
	active_controller_throttle = 0.0
	var controller: Dictionary = vector.get("controller_commands", {})
	var type := String(controller.get("type", ""))
	if type == "ROUTE_FOLLOWER_INPUT_CONTROLLER_V2":
		_route_controller(controller)
	elif type == "ROUTE_FOLLOWER_INPUT_CONTROLLER_V3_FAST_CONTAINED":
		_route_controller_v3_fast_contained(controller)
	elif type == "ROUTE_FOLLOWER_INPUT_CONTROLLER_V4_FORWARD_BRAKING_CONTAINED":
		_route_controller_v4_forward_braking_contained(controller)
	elif type == "ROUTE_FOLLOWER_INPUT_CONTROLLER_V5_INERTIAL_THRUST_VECTOR_CONTAINED":
		_route_controller_v5_inertial_thrust_vector_contained(controller)
	elif type == "ROUTE_FOLLOWER_INPUT_CONTROLLER_V6_DECEL_CONSTRAINED_THRUST_VECTOR_CONTAINED":
		_route_controller_v6_decel_constrained_thrust_vector_contained(controller)
	elif type == "ROUTE_FOLLOWER_INPUT_CONTROLLER_V7_PHASE_SEPARATED_BRAKE_CAPTURE_CONTAINED":
		_route_controller_v7_phase_separated_brake_capture_contained(controller)
	elif type == HUMAN_REPLAY_CONTROLLER:
		_normalized_input_trace_replay(tick)
	elif type == "POWERED_WAYPOINT_INPUT_CONTROLLER":
		_powered_waypoint_controller(controller)
	elif type == "MULTI_ROUTE_FOLLOWER_INPUT_CONTROLLER":
		_multi_route_controller(controller)
	elif type == "POINT_TARGET_INPUT_CONTROLLER":
		_point_target_controller(controller)
	elif type == "SUPPORTED_HOP_BRACKET_CONTROLLER":
		_supported_hop_bracket_controller(controller)
	for command_value in vector.get("tick_commands", []):
		var command: Dictionary = command_value
		if int(command.tick) != tick:
			continue
		var command_name := String(command.command)
		match command_name:
			"THROTTLE": scripted_throttle = float(command.value)
			"HOP_PRESS": scripted_hop = true
			"HOP_RELEASE": scripted_hop = false
			"OPEN_DIAGNOSTIC_MENU": gate_root.menu_panel.visible = true
			"ASSERT_SELECTION": _assert_selection(String(command.value), tick)
			"PREVIOUS_SELECTION": gate_root._change_selection(-1)
			"SPAWN_SELECTED_WITH_ENTER": gate_root.spawn_selected_tour()
			"MANUAL_RESET_WITH_R": gate_root.reset_active_segment("MANUAL")
			"SET_POSITION_Y_FOR_FALL_TEST": craft.global_position.y = float(command.value)
			"END": pass
			_:
				command_assertion_failures.append("unhandled fixture command %s at tick %d" % [command_name, tick])
	if type.is_empty() and scripted_throttle > 0.0:
		active_controller_throttle = scripted_throttle
		Input.action_press("throttle", scripted_throttle)
	if type.is_empty() and scripted_hop:
		Input.action_press("hop", 1.0)
	elif type.is_empty():
		Input.action_release("hop")


func _normalized_input_trace_replay(tick: int) -> void:
	Input.action_release("hop")
	if tick < 0 or tick >= human_input_records.size():
		last_human_control = {"commanded_throttle": 0.0, "commanded_brake": 0.0, "commanded_steer": 0.0}
		return
	var record: Dictionary = human_input_records[tick]
	var throttle := clampf(float(int(record.get("throttle_u16", 0))) / 65535.0, 0.0, 1.0)
	var brake := clampf(float(int(record.get("brake_u16", 0))) / 65535.0, 0.0, 1.0)
	var steer := clampf(float(int(record.get("steer_i16", 0))) / 32767.0, -1.0, 1.0)
	active_controller_throttle = throttle
	if throttle > 0.0:
		Input.action_press("throttle", throttle)
	if brake > 0.0:
		Input.action_press("brake", brake)
	if steer > 0.0:
		Input.action_press("steer_right", steer)
	elif steer < 0.0:
		Input.action_press("steer_left", -steer)
	if bool(record.get("transform_pressed", false)):
		Input.action_press("transform", 1.0)
	else:
		Input.action_release("transform")
	last_human_control = {
		"commanded_throttle": throttle,
		"commanded_brake": brake,
		"commanded_steer": steer,
	}


func _assert_selection(expected: String, tick: int) -> void:
	var order: Array = data.diagnostic.selection_order
	var actual := String(order[gate_root.selection_index])
	var passed := actual == expected
	telemetry.emit_event({"event": "TEST_ASSERTION", "assertion": "DIAGNOSTIC_SELECTION", "expected": expected, "actual": actual, "passed": passed, "vector_tick": tick})
	if not passed:
		command_assertion_failures.append("ASSERT_SELECTION expected %s, found %s at tick %d" % [expected, actual, tick])


func _route_controller(controller: Dictionary) -> void:
	var route_id := String(controller.route_id)
	var point := Vector2(craft.global_position.x, craft.global_position.z)
	var nearest := _nearest_global(route_id, point)
	maximum_chainage = maxf(maximum_chainage, float(nearest.chainage))
	maximum_lateral_error_m = maxf(maximum_lateral_error_m, float(nearest.distance))
	var forward := String(controller.get("direction", "FORWARD")) != "REVERSE"
	var speed := Vector2(craft.velocity.x, craft.velocity.z).length()
	var lookahead := clampf(float(controller.get("lookahead_min_m", 8.0)) + speed * float(controller.get("lookahead_speed_gain_s", 0.4)), float(controller.get("lookahead_min_m", 8.0)), float(controller.get("lookahead_max_m", 24.0)))
	var target_chainage := float(nearest.chainage) + (lookahead if forward else -lookahead)
	_steer_toward(_route_sample(route_id, target_chainage).point, float(controller.get("steer_gain", 1.75)))
	var remaining := float(nearest.length) - float(nearest.chainage) if forward else float(nearest.chainage)
	var drive := String(vector.get("initial_mode", "SPREAD")) == "DRIVE"
	var cap := float(controller.get("drive_speed_cap_mps", 27.0) if drive else controller.get("spread_speed_cap_mps", 11.5))
	var brake_decel := float(controller.get("drive_brake_decel_mps2", 4.5) if drive else controller.get("spread_brake_decel_mps2", 19.0))
	var yaw_rate := float(controller.get("drive_yaw_rate_rad_s", 0.44) if drive else controller.get("spread_yaw_rate_rad_s", 1.9))
	var span := float(controller.get("curvature_span_m", 8.0))
	var t0: Vector2 = _route_sample(route_id, float(nearest.chainage) - span).tangent
	var t1: Vector2 = _route_sample(route_id, float(nearest.chainage) + span).tangent
	var turn_angle := absf(atan2(t0.x * t1.y - t0.y * t1.x, t0.dot(t1)))
	var radius := 1000000.0 if turn_angle < 0.000001 else (2.0 * span / turn_angle)
	var turn_cap := yaw_rate * radius * float(controller.get("turn_rate_margin", 0.72))
	var stop_cap := sqrt(maxf(0.0, 2.0 * brake_decel * maxf(0.0, remaining - float(controller.get("endpoint_margin_m", 3.0)))))
	var desired := minf(cap, minf(turn_cap, stop_cap))
	var deadband := float(controller.get("speed_deadband_mps", 0.6))
	var scale := float(controller.get("speed_error_full_scale_mps", 5.0))
	if speed < desired - deadband:
		Input.action_press("throttle", clampf((desired - speed) / scale, 0.15, 1.0))
	elif speed > desired + deadband:
		Input.action_press("brake", clampf((speed - desired) / scale, 0.15, 1.0))
	if route_id == "HOP" and float(nearest.chainage) >= 36.0 and not hop_press_sent:
		Input.action_press("hop", 1.0)
		hop_press_sent = true
	elif hop_press_sent:
		Input.action_release("hop")


func _route_controller_v3_fast_contained(controller: Dictionary) -> void:
	var route_id := String(controller.route_id)
	var point := Vector2(craft.global_position.x, craft.global_position.z)
	var nearest := _nearest_global(route_id, point)
	var chainage := float(nearest.chainage)
	var forward := String(controller.get("direction", "FORWARD")) != "REVERSE"
	maximum_chainage = maxf(maximum_chainage, chainage)
	maximum_lateral_error_m = maxf(maximum_lateral_error_m, float(nearest.distance))
	var center_sample := _route_sample(route_id, chainage)
	var center: Vector2 = center_sample.point
	var tangent: Vector2 = center_sample.tangent if forward else -center_sample.tangent
	var normal := Vector2(-tangent.y, tangent.x)
	var signed_error := (point - center).dot(normal)
	var speed := Vector2(craft.velocity.x, craft.velocity.z).length()
	var lookahead := clampf(float(controller.lookahead_min_m) + speed * float(controller.lookahead_speed_gain_s), float(controller.lookahead_min_m), float(controller.lookahead_max_m))
	var soft := float(controller.lateral_soft_limit_m)
	var hard := float(controller.lateral_hard_limit_m)
	if float(nearest.distance) > soft:
		lookahead = float(controller.lookahead_min_m)
	var target_chainage := chainage + (lookahead if forward else -lookahead)
	var target_sample := _route_sample(route_id, target_chainage)
	var target: Vector2 = target_sample.point
	var correction := clampf(-signed_error * float(controller.lateral_target_gain), -float(controller.lateral_target_max_m), float(controller.lateral_target_max_m))
	target += normal * correction
	_steer_toward(target, float(controller.steer_gain))
	var remaining := float(nearest.length) - chainage if forward else chainage
	var desired := float(controller.drive_speed_cap_mps)
	var preview: Array = controller.preview_distances_m
	for distance_value in preview:
		var distance := float(distance_value)
		var before: Vector2 = _route_sample(route_id, chainage - distance).tangent
		var after: Vector2 = _route_sample(route_id, chainage + distance).tangent
		var angle := absf(atan2(before.x * after.y - before.y * after.x, before.dot(after)))
		if angle > 0.000001:
			var radius := 2.0 * distance / angle
			desired = minf(desired, float(controller.drive_yaw_rate_rad_s) * radius * float(controller.turn_rate_margin))
	var stop_cap := sqrt(maxf(0.0, 2.0 * float(controller.drive_brake_decel_mps2) * maxf(0.0, remaining - float(controller.endpoint_margin_m))))
	desired = minf(desired, stop_cap)
	if float(nearest.distance) > soft:
		desired = minf(desired, float(controller.recovery_speed_cap_mps))
	if float(nearest.distance) > hard:
		Input.action_press("brake", 1.0)
		return
	var deadband := float(controller.speed_deadband_mps)
	var scale := float(controller.speed_error_full_scale_mps)
	if speed < desired - deadband:
		active_controller_throttle = clampf((desired - speed) / scale, 0.15, 1.0)
		Input.action_press("throttle", active_controller_throttle)
	elif speed > desired + deadband:
		Input.action_press("brake", clampf((speed - desired) / scale, 0.15, 1.0))


func _route_controller_v4_forward_braking_contained(controller: Dictionary) -> void:
	var route_id := String(controller.route_id)
	var point := Vector2(craft.global_position.x, craft.global_position.z)
	var nearest := _nearest_global(route_id, point)
	var chainage := float(nearest.chainage)
	var forward := String(controller.get("direction", "FORWARD")) != "REVERSE"
	if not forward:
		preflight_failures.append("V4 fast-route driver authorizes FORWARD only")
		return
	maximum_chainage = maxf(maximum_chainage, chainage)
	maximum_lateral_error_m = maxf(maximum_lateral_error_m, float(nearest.distance))
	var center_sample := _route_sample(route_id, chainage)
	var center: Vector2 = center_sample.point
	var tangent: Vector2 = center_sample.tangent
	var normal := Vector2(-tangent.y, tangent.x)
	var signed_error := (point - center).dot(normal)
	var horizontal_velocity := Vector2(craft.velocity.x, craft.velocity.z)
	var speed := horizontal_velocity.length()
	var lateral_speed := horizontal_velocity.dot(normal)
	var predicted_error := signed_error + lateral_speed * float(controller.recovery_prediction_horizon_s)
	var soft := float(controller.lateral_soft_limit_m)
	var hard := float(controller.lateral_hard_limit_m)
	var recovery_metric := maxf(absf(signed_error), absf(predicted_error))
	var recovery_active := recovery_metric >= soft
	var emergency_brake_active := recovery_metric >= hard - float(controller.recovery_emergency_margin_m)
	var lookahead := clampf(float(controller.steering_lookahead_min_m) + speed * float(controller.steering_lookahead_speed_gain_s), float(controller.steering_lookahead_min_m), float(controller.steering_lookahead_max_m))
	if recovery_active:
		lookahead = float(controller.recovery_lookahead_m)
	var target_sample := _route_sample(route_id, chainage + lookahead)
	var target: Vector2 = target_sample.point
	var correction_gain := float(controller.recovery_lateral_target_gain) if recovery_active else float(controller.lateral_target_gain)
	var velocity_gain := float(controller.recovery_lateral_velocity_gain_s) if recovery_active else 0.0
	var correction := clampf(-signed_error * correction_gain - lateral_speed * velocity_gain, -float(controller.lateral_target_max_m), float(controller.lateral_target_max_m))
	target += normal * correction
	var desired_direction := (target - point).normalized()
	var craft_forward := Vector2(-craft.global_basis.z.x, -craft.global_basis.z.z).normalized()
	var heading_error := atan2(craft_forward.x * desired_direction.y - craft_forward.y * desired_direction.x, craft_forward.dot(desired_direction))
	var steer_command := clampf(float(controller.steer_gain) * heading_error, -1.0, 1.0)
	if steer_command >= 0.0:
		Input.action_press("steer_right", steer_command)
	else:
		Input.action_press("steer_left", -steer_command)
	var plan := _v4_speed_plan(controller)
	var lead := clampf(speed * float(controller.plan_query_lead_time_s), float(controller.plan_query_lead_min_m), float(controller.plan_query_lead_max_m))
	var desired_speed := minf(_v4_plan_speed_at(plan, chainage), _v4_plan_speed_at(plan, chainage + lead))
	if recovery_active:
		desired_speed = minf(desired_speed, float(controller.recovery_speed_cap_mps))
	var commanded_brake := 0.0
	if emergency_brake_active:
		commanded_brake = 1.0
		Input.action_press("brake", commanded_brake)
	else:
		var deadband := float(controller.speed_deadband_mps)
		var scale := float(controller.speed_error_full_scale_mps)
		if speed < desired_speed - deadband:
			active_controller_throttle = clampf((desired_speed - speed) / scale, 0.15, 1.0)
			Input.action_press("throttle", active_controller_throttle)
		elif speed > desired_speed + deadband:
			commanded_brake = clampf((speed - desired_speed) / scale, 0.15, 1.0)
			Input.action_press("brake", commanded_brake)
	last_v4_control = {
		"route_id": route_id,
		"planned_speed_cap_mps": desired_speed,
		"recovery_active": recovery_active,
		"emergency_brake_active": emergency_brake_active,
		"commanded_throttle": active_controller_throttle,
		"commanded_brake": commanded_brake,
		"commanded_steer": steer_command,
		"predicted_lateral_error_m": predicted_error,
	}


func _v4_speed_plan(controller: Dictionary) -> Dictionary:
	var route_id := String(controller.route_id)
	if route_driver_plans.has(route_id):
		return route_driver_plans[route_id]
	var cache: Dictionary = route_cache[route_id]
	var points: PackedVector2Array = cache.points
	var cumulative: PackedFloat64Array = cache.cumulative
	var raw_caps := PackedFloat64Array()
	var planned_caps := PackedFloat64Array()
	raw_caps.resize(points.size())
	planned_caps.resize(points.size())
	for index in points.size():
		var chainage := float(cumulative[index])
		var remaining := float(cache.length) - chainage
		var span := minf(float(controller.forward_curvature_window_m), maxf(0.0, remaining))
		var local_cap := float(controller.drive_speed_cap_mps)
		if span > 0.000001:
			var tangent_now: Vector2 = _route_sample(route_id, chainage).tangent
			var tangent_forward: Vector2 = _route_sample(route_id, chainage + span).tangent
			var angle := absf(atan2(tangent_now.x * tangent_forward.y - tangent_now.y * tangent_forward.x, tangent_now.dot(tangent_forward)))
			if angle > 0.000001:
				var radius := span / angle
				local_cap = minf(local_cap, float(controller.drive_yaw_rate_rad_s) * radius * float(controller.turn_rate_margin))
		if remaining <= float(controller.endpoint_margin_m) + 0.000001:
			local_cap = minf(local_cap, float(controller.endpoint_speed_cap_mps))
		raw_caps[index] = local_cap
		planned_caps[index] = local_cap
	for index in range(points.size() - 2, -1, -1):
		var ds := float(cumulative[index + 1] - cumulative[index])
		var feasible := sqrt(maxf(0.0, planned_caps[index + 1] * planned_caps[index + 1] + 2.0 * float(controller.braking_envelope_decel_mps2) * ds))
		planned_caps[index] = minf(planned_caps[index], feasible)
	var plan := {
		"route_id": route_id,
		"cumulative": cumulative,
		"raw_caps": raw_caps,
		"planned_caps": planned_caps,
		"length": float(cache.length),
		"algorithm_id": String(controller.curve_plan_algorithm_id),
	}
	route_driver_plans[route_id] = plan
	return plan


func _v4_plan_speed_at(plan: Dictionary, chainage: float) -> float:
	var cumulative: PackedFloat64Array = plan.cumulative
	var planned: PackedFloat64Array = plan.planned_caps
	var target := clampf(chainage, 0.0, float(plan.length))
	var low := 0
	var high := cumulative.size() - 1
	while low + 1 < high:
		var middle := (low + high) / 2
		if cumulative[middle] <= target:
			low = middle
		else:
			high = middle
	var ds := cumulative[low + 1] - cumulative[low]
	var t := (target - cumulative[low]) / ds if ds > 0.0 else 0.0
	return lerpf(planned[low], planned[low + 1], t)


func _route_controller_v5_inertial_thrust_vector_contained(controller: Dictionary) -> void:
	var route_id := String(controller.route_id)
	var point := Vector2(craft.global_position.x, craft.global_position.z)
	var nearest: Dictionary = _nearest_global(route_id, point)
	var chainage := float(nearest.chainage)
	if String(controller.get("direction", "FORWARD")) != "FORWARD":
		preflight_failures.append("V5 fast-route driver authorizes FORWARD only")
		return
	maximum_chainage = maxf(maximum_chainage, chainage)
	maximum_lateral_error_m = maxf(maximum_lateral_error_m, float(nearest.distance))
	var center_sample: Dictionary = _route_sample(route_id, chainage)
	var center: Vector2 = center_sample.point
	var tangent: Vector2 = center_sample.tangent
	var normal: Vector2 = Vector2(-tangent.y, tangent.x)
	var signed_error: float = (point - center).dot(normal)
	var horizontal_velocity: Vector2 = Vector2(craft.velocity.x, craft.velocity.z)
	var speed: float = horizontal_velocity.length()
	var velocity_direction: Vector2 = horizontal_velocity.normalized() if speed > 0.05 else tangent
	var lateral_speed: float = horizontal_velocity.dot(normal)
	var predicted_error: float = signed_error + lateral_speed * float(v5_candidate.recovery_prediction_horizon_s)
	var soft := float(controller.lateral_soft_limit_m)
	var hard := float(controller.lateral_hard_limit_m)
	var recovery_trigger := soft * float(v5_candidate.recovery_activation_fraction_of_soft_limit)
	var recovery_active := maxf(absf(signed_error), absf(predicted_error)) >= recovery_trigger
	var course_preview := clampf(speed * float(v5_candidate.desired_course_preview_time_s), float(v5_candidate.desired_course_preview_min_m), float(v5_candidate.desired_course_preview_max_m))
	var desired_tangent: Vector2 = _route_sample(route_id, chainage + course_preview).tangent
	var course_correction := clampf(
		-signed_error * float(v5_candidate.course_lateral_error_gain_rad_per_m)
		-lateral_speed * float(v5_candidate.course_lateral_velocity_gain_rad_per_mps),
		-float(v5_candidate.maximum_course_correction_rad),
		float(v5_candidate.maximum_course_correction_rad)
	)
	var desired_course: Vector2 = desired_tangent.rotated(course_correction).normalized()
	var course_error: float = _signed_angle_2d(velocity_direction, desired_course)
	var signed_curvature: float = _v5_signed_curvature(route_id, chainage, float(v5_candidate.curvature_plan_window_m))
	var requested_lateral_accel: float = (
		speed * speed * signed_curvature * float(v5_candidate.curvature_feedforward_gain)
		+ course_error * float(v5_candidate.course_error_accel_gain_mps2_per_rad)
		- signed_error * float(v5_candidate.lateral_error_accel_gain_s2)
		- lateral_speed * float(v5_candidate.lateral_velocity_accel_gain_s)
	)
	requested_lateral_accel = clampf(requested_lateral_accel, -float(v5_candidate.maximum_requested_lateral_accel_mps2), float(v5_candidate.maximum_requested_lateral_accel_mps2))
	var turn_required := absf(requested_lateral_accel) >= float(v5_candidate.turning_accel_threshold_mps2)
	var turning_throttle_floor := 0.0
	if turn_required:
		turning_throttle_floor = float(v5_candidate.recovery_turning_throttle if recovery_active else v5_candidate.minimum_turning_throttle)

	# Longitudinal speed control is solved before body lead so the commanded
	# thrust magnitude, not merely the minimum floor, determines the lead angle.
	var plan: Dictionary = _v5_speed_plan(controller)
	var lead := clampf(speed * float(v5_candidate.plan_query_lead_time_s), float(v5_candidate.plan_query_lead_min_m), float(v5_candidate.plan_query_lead_max_m))
	var desired_speed := minf(_v5_plan_speed_at(plan, chainage), _v5_plan_speed_at(plan, chainage + lead))
	if recovery_active:
		desired_speed = minf(desired_speed, float(v5_candidate.recovery_speed_cap_mps))
	var commanded_throttle := turning_throttle_floor
	var commanded_brake := 0.0
	var deadband := float(v5_candidate.speed_deadband_mps)
	var scale := float(v5_candidate.speed_error_full_scale_mps)
	if speed < desired_speed - deadband:
		commanded_throttle = maxf(commanded_throttle, clampf((desired_speed - speed) / scale, 0.15, 1.0))
	elif speed > desired_speed + deadband:
		commanded_brake = clampf((speed - desired_speed) / scale, 0.15, 1.0)
	if recovery_active and speed > float(v5_candidate.recovery_speed_cap_mps):
		commanded_brake = maxf(commanded_brake, clampf((speed - float(v5_candidate.recovery_speed_cap_mps)) / scale, 0.25, 1.0))

	var available_thrust := _v5_available_thrust(speed)
	var denominator := maxf(available_thrust * maxf(commanded_throttle, 0.001), 0.001)
	var maximum_lead := float(v5_candidate.maximum_body_lead_rad)
	var lead_ratio := clampf(requested_lateral_accel / denominator, -sin(maximum_lead), sin(maximum_lead))
	var body_lead: float = asin(lead_ratio)
	var desired_body: Vector2 = velocity_direction.rotated(body_lead).normalized()
	if speed <= 0.05:
		desired_body = desired_course
	var craft_forward: Vector2 = Vector2(-craft.global_basis.z.x, -craft.global_basis.z.z).normalized()
	var body_error: float = _signed_angle_2d(craft_forward, desired_body)
	var steer_command: float = clampf(float(v5_candidate.steer_gain) * body_error, -1.0, 1.0)
	if steer_command >= 0.0:
		Input.action_press("steer_right", steer_command)
	else:
		Input.action_press("steer_left", -steer_command)
	active_controller_throttle = commanded_throttle
	if commanded_throttle > 0.0:
		Input.action_press("throttle", commanded_throttle)
	if commanded_brake > 0.0:
		Input.action_press("brake", commanded_brake)
	last_v5_control = {
		"candidate_id": v5_candidate_id,
		"route_id": route_id,
		"planned_speed_cap_mps": desired_speed,
		"recovery_active": recovery_active,
		"commanded_throttle": commanded_throttle,
		"commanded_brake": commanded_brake,
		"commanded_steer": steer_command,
		"velocity_course_angle_rad": atan2(velocity_direction.y, velocity_direction.x),
		"desired_route_course_angle_rad": atan2(desired_course.y, desired_course.x),
		"course_error_rad": course_error,
		"signed_curvature_per_m": signed_curvature,
		"requested_lateral_accel_mps2": requested_lateral_accel,
		"body_lead_angle_rad": body_lead,
		"turning_throttle_floor": turning_throttle_floor,
		"predicted_lateral_error_m": predicted_error,
		"lateral_hard_limit_m": hard,
	}


func _route_controller_v6_decel_constrained_thrust_vector_contained(controller: Dictionary) -> void:
	var route_id := String(controller.route_id)
	var point := Vector2(craft.global_position.x, craft.global_position.z)
	var nearest: Dictionary = _nearest_global(route_id, point)
	var chainage := float(nearest.chainage)
	if String(controller.get("direction", "FORWARD")) != "FORWARD":
		preflight_failures.append("V6 fast-route driver authorizes FORWARD only")
		return
	maximum_chainage = maxf(maximum_chainage, chainage)
	maximum_lateral_error_m = maxf(maximum_lateral_error_m, float(nearest.distance))
	var center_sample: Dictionary = _route_sample(route_id, chainage)
	var center: Vector2 = center_sample.point
	var tangent: Vector2 = center_sample.tangent
	var normal: Vector2 = Vector2(-tangent.y, tangent.x)
	var signed_error: float = (point - center).dot(normal)
	var horizontal_velocity := Vector2(craft.velocity.x, craft.velocity.z)
	var speed := horizontal_velocity.length()
	var velocity_direction: Vector2 = horizontal_velocity.normalized() if speed > 0.05 else tangent
	var lateral_speed := horizontal_velocity.dot(normal)
	var predicted_error := signed_error + lateral_speed * float(v6_candidate.recovery_prediction_horizon_s)
	var soft := float(controller.lateral_soft_limit_m)
	var hard := float(controller.lateral_hard_limit_m)
	var recovery_trigger := soft * float(v6_candidate.recovery_activation_fraction_of_soft_limit)
	var recovery_active := maxf(absf(signed_error), absf(predicted_error)) >= recovery_trigger
	var course_preview := clampf(speed * float(v6_candidate.desired_course_preview_time_s), float(v6_candidate.desired_course_preview_min_m), float(v6_candidate.desired_course_preview_max_m))
	var desired_tangent: Vector2 = _route_sample(route_id, chainage + course_preview).tangent
	var course_correction := clampf(-signed_error * float(v6_candidate.course_lateral_error_gain_rad_per_m) - lateral_speed * float(v6_candidate.course_lateral_velocity_gain_rad_per_mps), -float(v6_candidate.maximum_course_correction_rad), float(v6_candidate.maximum_course_correction_rad))
	var desired_course := desired_tangent.rotated(course_correction).normalized()
	var course_error := _signed_angle_2d(velocity_direction, desired_course)
	var signed_curvature := _v6_signed_curvature(route_id, chainage, float(v6_candidate.curvature_plan_window_m))
	var requested_lateral_accel := speed * speed * signed_curvature * float(v6_candidate.curvature_feedforward_gain) + course_error * float(v6_candidate.course_error_accel_gain_mps2_per_rad) - signed_error * float(v6_candidate.lateral_error_accel_gain_s2) - lateral_speed * float(v6_candidate.lateral_velocity_accel_gain_s)
	requested_lateral_accel = clampf(requested_lateral_accel, -float(v6_candidate.maximum_requested_lateral_accel_mps2), float(v6_candidate.maximum_requested_lateral_accel_mps2))

	var plan := _v6_speed_plan(controller)
	var lead := clampf(speed * float(v6_candidate.plan_query_lead_time_s), float(v6_candidate.plan_query_lead_min_m), float(v6_candidate.plan_query_lead_max_m))
	var desired_speed := minf(_v6_plan_speed_at(plan, chainage), _v6_plan_speed_at(plan, chainage + lead))
	if recovery_active:
		desired_speed = minf(desired_speed, float(v6_candidate.recovery_speed_cap_mps))
	var deadband := float(v6_candidate.speed_deadband_mps)
	var slowdown_active := speed > desired_speed + deadband
	var required_net_decel := float(v6_candidate.minimum_required_net_deceleration_mps2) if slowdown_active else 0.0
	var commanded_brake := 1.0 if slowdown_active else 0.0
	var available_thrust := _v6_available_thrust(speed)
	var maximum_lead := float(v6_candidate.maximum_body_lead_rad)
	var lead_ratio := clampf(requested_lateral_accel / maxf(available_thrust, 0.001), -sin(maximum_lead), sin(maximum_lead))
	var body_lead := asin(lead_ratio)
	var desired_body := velocity_direction.rotated(body_lead).normalized()
	if speed <= 0.05:
		desired_body = desired_course
	var craft_forward := Vector2(-craft.global_basis.z.x, -craft.global_basis.z.z).normalized()
	var body_error := _signed_angle_2d(craft_forward, desired_body)
	var steer_command := clampf(float(v6_candidate.steer_gain) * body_error, -1.0, 1.0)

	var lateral_throttle_need := clampf(absf(requested_lateral_accel) / maxf(available_thrust * maxf(absf(sin(body_lead)), 0.12), 0.001), 0.0, 1.0)
	var commanded_throttle := lateral_throttle_need
	if not slowdown_active and speed < desired_speed - deadband:
		commanded_throttle = maxf(commanded_throttle, clampf((desired_speed - speed) / float(v6_candidate.speed_error_full_scale_mps), 0.15, 1.0))
	var forward_projection := craft_forward.dot(velocity_direction)
	var maximum_authorized_longitudinal_thrust := 0.0
	var recovery_phase := "CRUISE"
	if slowdown_active:
		recovery_phase = "BRAKE_THRUST_VECTOR"
		maximum_authorized_longitudinal_thrust = maxf(0.0, float(v6_candidate.frozen_full_brake_decel_mps2) - required_net_decel)
		if forward_projection > 0.0001:
			var throttle_cap := maximum_authorized_longitudinal_thrust / maxf(available_thrust * forward_projection, 0.001)
			commanded_throttle = minf(commanded_throttle, clampf(throttle_cap, 0.0, 1.0))
		if absf(body_error) > float(v6_candidate.brake_yaw_alignment_error_rad):
			recovery_phase = "BRAKE_YAW"
			commanded_throttle = minf(commanded_throttle, float(v6_candidate.brake_yaw_throttle_cap))
	elif recovery_active:
		recovery_phase = "RECOVERY_THRUST_VECTOR"

	var predicted_longitudinal_accel := commanded_throttle * available_thrust * maxf(0.0, forward_projection) - commanded_brake * float(v6_candidate.frozen_full_brake_decel_mps2)
	var predicted_speed_delta := predicted_longitudinal_accel / 60.0
	if steer_command >= 0.0:
		Input.action_press("steer_right", steer_command)
	else:
		Input.action_press("steer_left", -steer_command)
	active_controller_throttle = commanded_throttle
	if commanded_throttle > 0.0:
		Input.action_press("throttle", commanded_throttle)
	if commanded_brake > 0.0:
		Input.action_press("brake", commanded_brake)
	last_v6_control = {
		"candidate_id": v6_candidate_id, "algorithm_id": "DZP1A_DECEL_CONSTRAINED_THRUST_VECTOR_V1", "route_id": route_id,
		"planned_speed_cap_mps": desired_speed, "desired_speed_mps": desired_speed, "observed_speed_mps": speed, "pre_command_speed_mps": speed,
		"recovery_active": recovery_active, "recovery_phase": recovery_phase, "slowdown_command_active": slowdown_active,
		"required_net_decel_mps2": required_net_decel, "maximum_authorized_longitudinal_thrust_mps2": maximum_authorized_longitudinal_thrust,
		"actual_body_forward_longitudinal_component": forward_projection, "predicted_longitudinal_accel_mps2": predicted_longitudinal_accel, "predicted_speed_delta_mps": predicted_speed_delta,
		"commanded_throttle": commanded_throttle, "commanded_brake": commanded_brake, "commanded_steer": steer_command,
		"velocity_course_angle_rad": atan2(velocity_direction.y, velocity_direction.x), "desired_route_course_angle_rad": atan2(desired_course.y, desired_course.x), "course_error_rad": course_error,
		"signed_curvature_per_m": signed_curvature, "requested_lateral_accel_mps2": requested_lateral_accel, "body_lead_angle_rad": body_lead,
		"predicted_lateral_error_m": predicted_error, "lateral_velocity_mps": lateral_speed, "lateral_hard_limit_m": hard,
	}


func _route_controller_v7_phase_separated_brake_capture_contained(controller: Dictionary) -> void:
	var route_id := String(controller.route_id)
	var point := Vector2(craft.global_position.x, craft.global_position.z)
	var nearest: Dictionary = _nearest_global(route_id, point)
	var chainage := float(nearest.chainage)
	if String(controller.get("direction", "FORWARD")) != "FORWARD":
		preflight_failures.append("V7 fast-route driver authorizes FORWARD only")
		return
	maximum_chainage = maxf(maximum_chainage, chainage)
	maximum_lateral_error_m = maxf(maximum_lateral_error_m, float(nearest.distance))
	var center_sample: Dictionary = _route_sample(route_id, chainage)
	var center: Vector2 = center_sample.point
	var tangent: Vector2 = center_sample.tangent
	var normal := Vector2(-tangent.y, tangent.x)
	var signed_error: float = (point - center).dot(normal)
	var horizontal_velocity := Vector2(craft.velocity.x, craft.velocity.z)
	var speed := horizontal_velocity.length()
	var velocity_direction: Vector2 = horizontal_velocity.normalized() if speed > 0.05 else tangent
	var lateral_speed := horizontal_velocity.dot(normal)
	var predicted_error := signed_error + lateral_speed * float(v7_candidate.recovery_prediction_horizon_s)
	var soft := float(controller.lateral_soft_limit_m)
	var hard := float(controller.lateral_hard_limit_m)
	var course_preview := clampf(speed * float(v7_candidate.desired_course_preview_time_s), float(v7_candidate.desired_course_preview_min_m), float(v7_candidate.desired_course_preview_max_m))
	var desired_tangent: Vector2 = _route_sample(route_id, chainage + course_preview).tangent
	var course_correction := clampf(-signed_error * float(v7_candidate.course_lateral_error_gain_rad_per_m) - lateral_speed * float(v7_candidate.course_lateral_velocity_gain_rad_per_mps), -float(v7_candidate.maximum_course_correction_rad), float(v7_candidate.maximum_course_correction_rad))
	var desired_course := desired_tangent.rotated(course_correction).normalized()
	var course_error := _signed_angle_2d(velocity_direction, desired_course)
	var signed_curvature := _v7_effective_signed_curvature(route_id, chainage, float(v7_candidate.turn_plan_preview_m), float(v7_candidate.curvature_local_window_m))
	var requested_lateral_accel := speed * speed * signed_curvature * float(v7_candidate.curvature_feedforward_gain) + course_error * float(v7_candidate.course_error_accel_gain_mps2_per_rad) - signed_error * float(v7_candidate.lateral_error_accel_gain_s2) - lateral_speed * float(v7_candidate.lateral_velocity_accel_gain_s)
	requested_lateral_accel = clampf(requested_lateral_accel, -float(v7_candidate.maximum_requested_lateral_accel_mps2), float(v7_candidate.maximum_requested_lateral_accel_mps2))

	var plan := _v7_speed_plan(controller)
	var lead := clampf(speed * float(v7_candidate.plan_query_lead_time_s), float(v7_candidate.plan_query_lead_min_m), float(v7_candidate.plan_query_lead_max_m))
	var desired_speed := minf(_v7_plan_speed_at(plan, chainage), _v7_plan_speed_at(plan, chainage + lead))
	var capture_active := maxf(absf(signed_error), absf(predicted_error)) >= soft * float(v7_candidate.capture_activation_fraction_of_soft_limit) or absf(course_error) >= float(v7_candidate.capture_course_error_activation_rad) or absf(signed_curvature) >= float(v7_candidate.capture_curvature_activation_per_m)
	var deadband := float(v7_candidate.speed_deadband_mps)
	var ticks_in_phase := vector_tick - v7_phase_enter_vector_tick
	var next_phase := v7_phase
	if v7_phase == "BRAKE_COMMIT":
		if ticks_in_phase >= int(v7_candidate.brake_minimum_commit_ticks) and speed <= desired_speed - float(v7_candidate.brake_release_hysteresis_mps):
			next_phase = "CAPTURE_THRUST" if capture_active else "CRUISE"
	elif speed > desired_speed + float(v7_candidate.brake_reentry_margin_mps):
		next_phase = "BRAKE_COMMIT"
	elif capture_active:
		next_phase = "CAPTURE_THRUST"
	elif speed < desired_speed - deadband:
		next_phase = "ACCELERATE"
	else:
		next_phase = "CRUISE"
	if next_phase != v7_phase:
		v7_phase = next_phase
		v7_phase_enter_vector_tick = vector_tick
		ticks_in_phase = 0

	var available_thrust := _v6_available_thrust(speed)
	var maximum_lead := float(v7_candidate.maximum_body_lead_rad)
	var lead_ratio := clampf(requested_lateral_accel / maxf(available_thrust, 0.001), -sin(maximum_lead), sin(maximum_lead))
	var body_lead := asin(lead_ratio)
	var desired_body := desired_course
	if v7_phase == "CAPTURE_THRUST":
		desired_body = velocity_direction.rotated(body_lead).normalized()
	if speed <= 0.05:
		desired_body = desired_course
	var craft_forward := Vector2(-craft.global_basis.z.x, -craft.global_basis.z.z).normalized()
	var body_error := _signed_angle_2d(craft_forward, desired_body)
	var steer_command := clampf(float(v7_candidate.steer_gain) * body_error, -1.0, 1.0)
	var commanded_throttle := 0.0
	var commanded_brake := 0.0
	if v7_phase == "BRAKE_COMMIT":
		commanded_brake = 1.0
	elif v7_phase == "CAPTURE_THRUST":
		var lateral_need := clampf(absf(requested_lateral_accel) / maxf(available_thrust * maxf(absf(sin(body_lead)), 0.12), 0.001), 0.0, 1.0)
		commanded_throttle = maxf(float(v7_candidate.capture_throttle_floor), lateral_need)
	elif v7_phase == "ACCELERATE":
		commanded_throttle = clampf((desired_speed - speed) / float(v7_candidate.speed_error_full_scale_mps), 0.15, 1.0)
	elif speed < desired_speed - deadband:
		commanded_throttle = clampf((desired_speed - speed) / float(v7_candidate.speed_error_full_scale_mps), 0.0, 0.35)

	if commanded_throttle > 0.0 and commanded_brake > 0.0:
		preflight_failures.append("V7 phase separation violated: throttle and brake active together")
		commanded_throttle = 0.0
	if steer_command >= 0.0:
		Input.action_press("steer_right", steer_command)
	else:
		Input.action_press("steer_left", -steer_command)
	active_controller_throttle = commanded_throttle
	if commanded_throttle > 0.0:
		Input.action_press("throttle", commanded_throttle)
	if commanded_brake > 0.0:
		Input.action_press("brake", commanded_brake)
	var forward_projection := craft_forward.dot(velocity_direction)
	var predicted_longitudinal_accel := commanded_throttle * available_thrust * maxf(0.0, forward_projection) - commanded_brake * float(v7_candidate.frozen_full_brake_decel_mps2)
	last_v7_control = {
		"candidate_id": v7_candidate_id, "algorithm_id": "DZP1A_PHASE_SEPARATED_BRAKE_CAPTURE_V1", "route_id": route_id,
		"desired_speed_mps": desired_speed, "planned_speed_cap_mps": desired_speed, "observed_speed_mps": speed, "pre_command_speed_mps": speed,
		"predicted_speed_delta_mps": predicted_longitudinal_accel / 60.0, "predicted_longitudinal_accel_mps2": predicted_longitudinal_accel,
		"commanded_throttle": commanded_throttle, "commanded_brake": commanded_brake, "commanded_steer": steer_command,
		"recovery_phase": v7_phase, "phase_ticks": vector_tick - v7_phase_enter_vector_tick, "capture_active": capture_active,
		"velocity_course_angle_rad": atan2(velocity_direction.y, velocity_direction.x), "desired_route_course_angle_rad": atan2(desired_course.y, desired_course.x), "course_error_rad": course_error,
		"signed_curvature_per_m": signed_curvature, "requested_lateral_accel_mps2": requested_lateral_accel, "body_lead_angle_rad": body_lead,
		"predicted_lateral_error_m": predicted_error, "lateral_velocity_mps": lateral_speed, "lateral_hard_limit_m": hard,
		"turn_plan_preview_m": float(v7_candidate.turn_plan_preview_m), "plan_lateral_accel_budget_mps2": float(v7_candidate.plan_lateral_accel_budget_mps2), "brake_release_hysteresis_mps": float(v7_candidate.brake_release_hysteresis_mps),
	}


func _v7_speed_plan(controller: Dictionary) -> Dictionary:
	var route_id := String(controller.route_id)
	var cache_key := "V7|%s|%s" % [route_id, v7_candidate_id]
	if route_driver_plans.has(cache_key):
		return route_driver_plans[cache_key]
	var cache: Dictionary = route_cache[route_id]
	var points: PackedVector2Array = cache.points
	var cumulative: PackedFloat64Array = cache.cumulative
	var raw_caps := PackedFloat64Array()
	var planned_caps := PackedFloat64Array()
	raw_caps.resize(points.size())
	planned_caps.resize(points.size())
	for index in points.size():
		var chainage := float(cumulative[index])
		var remaining := float(cache.length) - chainage
		var curvature := _v7_effective_signed_curvature(route_id, chainage, minf(float(v7_candidate.turn_plan_preview_m), maxf(0.0, remaining)), minf(float(v7_candidate.curvature_local_window_m), maxf(0.0, remaining)))
		var local_cap := float(v7_candidate.drive_speed_cap_mps)
		if absf(curvature) > 0.000000001:
			local_cap = minf(local_cap, sqrt(float(v7_candidate.plan_lateral_accel_budget_mps2) / absf(curvature)) * float(v7_candidate.curve_speed_margin))
		if remaining <= float(v7_candidate.endpoint_margin_m) + 0.000001:
			local_cap = minf(local_cap, float(v7_candidate.endpoint_speed_cap_mps))
		raw_caps[index] = local_cap
		planned_caps[index] = local_cap
	for index in range(points.size() - 2, -1, -1):
		var ds := float(cumulative[index + 1] - cumulative[index])
		var feasible := sqrt(maxf(0.0, planned_caps[index + 1] * planned_caps[index + 1] + 2.0 * float(v7_candidate.braking_envelope_decel_mps2) * ds))
		planned_caps[index] = minf(planned_caps[index], feasible)
	var plan := {"route_id": route_id, "candidate_id": v7_candidate_id, "cumulative": cumulative, "raw_caps": raw_caps, "planned_caps": planned_caps, "length": float(cache.length), "algorithm_id": String(v7_candidate.algorithm_id)}
	route_driver_plans[cache_key] = plan
	return plan


func _v7_plan_speed_at(plan: Dictionary, chainage: float) -> float:
	var cumulative: PackedFloat64Array = plan.cumulative
	var planned: PackedFloat64Array = plan.planned_caps
	var target := clampf(chainage, 0.0, float(plan.length))
	var low := 0
	var high := cumulative.size() - 1
	while low + 1 < high:
		var middle := (low + high) / 2
		if cumulative[middle] <= target:
			low = middle
		else:
			high = middle
	var ds := cumulative[low + 1] - cumulative[low]
	var interpolation := (target - cumulative[low]) / ds if ds > 0.0 else 0.0
	return lerpf(planned[low], planned[low + 1], interpolation)


func _v7_effective_signed_curvature(route_id: String, chainage: float, preview_span: float, local_span: float) -> float:
	var local_curvature := _v6_signed_curvature(route_id, chainage, local_span)
	var preview_curvature := _v6_signed_curvature(route_id, chainage, preview_span)
	return preview_curvature if absf(preview_curvature) > absf(local_curvature) else local_curvature


func _v6_speed_plan(controller: Dictionary) -> Dictionary:
	var route_id := String(controller.route_id)
	var cache_key := "V6|%s|%s" % [route_id, v6_candidate_id]
	if route_driver_plans.has(cache_key):
		return route_driver_plans[cache_key]
	var cache: Dictionary = route_cache[route_id]
	var points: PackedVector2Array = cache.points
	var cumulative: PackedFloat64Array = cache.cumulative
	var raw_caps := PackedFloat64Array(); var planned_caps := PackedFloat64Array()
	raw_caps.resize(points.size()); planned_caps.resize(points.size())
	for index in points.size():
		var chainage := float(cumulative[index]); var remaining := float(cache.length) - chainage
		var curvature := _v6_signed_curvature(route_id, chainage, minf(float(v6_candidate.curvature_plan_window_m), maxf(0.0, remaining)))
		var local_cap := float(v6_candidate.drive_speed_cap_mps)
		if absf(curvature) > 0.000000001:
			local_cap = minf(local_cap, sqrt(float(v6_candidate.plan_lateral_accel_budget_mps2) / absf(curvature)) * float(v6_candidate.curve_speed_margin))
		if remaining <= float(v6_candidate.endpoint_margin_m) + 0.000001:
			local_cap = minf(local_cap, float(v6_candidate.endpoint_speed_cap_mps))
		raw_caps[index] = local_cap; planned_caps[index] = local_cap
	for index in range(points.size() - 2, -1, -1):
		var ds := float(cumulative[index + 1] - cumulative[index])
		var feasible := sqrt(maxf(0.0, planned_caps[index + 1] * planned_caps[index + 1] + 2.0 * float(v6_candidate.braking_envelope_decel_mps2) * ds))
		planned_caps[index] = minf(planned_caps[index], feasible)
	var plan := {"route_id": route_id, "candidate_id": v6_candidate_id, "cumulative": cumulative, "raw_caps": raw_caps, "planned_caps": planned_caps, "length": float(cache.length), "algorithm_id": String(v6_candidate.algorithm_id)}
	route_driver_plans[cache_key] = plan
	return plan


func _v6_plan_speed_at(plan: Dictionary, chainage: float) -> float:
	var cumulative: PackedFloat64Array = plan.cumulative; var planned: PackedFloat64Array = plan.planned_caps
	var target := clampf(chainage, 0.0, float(plan.length)); var low := 0; var high := cumulative.size() - 1
	while low + 1 < high:
		var middle := (low + high) / 2
		if cumulative[middle] <= target: low = middle
		else: high = middle
	var ds := cumulative[low + 1] - cumulative[low]; var t := (target - cumulative[low]) / ds if ds > 0.0 else 0.0
	return lerpf(planned[low], planned[low + 1], t)


func _v6_signed_curvature(route_id: String, chainage: float, span: float) -> float:
	if span <= 0.000001: return 0.0
	var tangent_now: Vector2 = _route_sample(route_id, chainage).tangent
	var tangent_forward: Vector2 = _route_sample(route_id, chainage + span).tangent
	return _signed_angle_2d(tangent_now, tangent_forward) / span


func _v6_available_thrust(speed: float) -> float:
	return MotionMath.powered_thrust(craft.tuning.drive_thrust_accel, speed, craft.tuning.drive_powered_speed_soft, craft.tuning.drive_powered_speed_cap)


func _v5_speed_plan(controller: Dictionary) -> Dictionary:
	var route_id := String(controller.route_id)
	var cache_key := "%s|%s" % [route_id, v5_candidate_id]
	if route_driver_plans.has(cache_key):
		return route_driver_plans[cache_key]
	var cache: Dictionary = route_cache[route_id]
	var points: PackedVector2Array = cache.points
	var cumulative: PackedFloat64Array = cache.cumulative
	var raw_caps := PackedFloat64Array()
	var planned_caps := PackedFloat64Array()
	raw_caps.resize(points.size())
	planned_caps.resize(points.size())
	for index in points.size():
		var chainage := float(cumulative[index])
		var remaining := float(cache.length) - chainage
		var curvature := _v5_signed_curvature(route_id, chainage, minf(float(v5_candidate.curvature_plan_window_m), maxf(0.0, remaining)))
		var local_cap := float(v5_candidate.drive_speed_cap_mps)
		if absf(curvature) > 0.000000001:
			local_cap = minf(local_cap, sqrt(float(v5_candidate.plan_lateral_accel_budget_mps2) / absf(curvature)) * float(v5_candidate.curve_speed_margin))
		if remaining <= float(v5_candidate.endpoint_margin_m) + 0.000001:
			local_cap = minf(local_cap, float(v5_candidate.endpoint_speed_cap_mps))
		raw_caps[index] = local_cap
		planned_caps[index] = local_cap
	for index in range(points.size() - 2, -1, -1):
		var ds := float(cumulative[index + 1] - cumulative[index])
		var feasible := sqrt(maxf(0.0, planned_caps[index + 1] * planned_caps[index + 1] + 2.0 * float(v5_candidate.braking_envelope_decel_mps2) * ds))
		planned_caps[index] = minf(planned_caps[index], feasible)
	var plan := {"route_id": route_id, "candidate_id": v5_candidate_id, "cumulative": cumulative, "raw_caps": raw_caps, "planned_caps": planned_caps, "length": float(cache.length), "algorithm_id": String(v5_candidate.algorithm_id)}
	route_driver_plans[cache_key] = plan
	return plan


func _v5_plan_speed_at(plan: Dictionary, chainage: float) -> float:
	var cumulative: PackedFloat64Array = plan.cumulative
	var planned: PackedFloat64Array = plan.planned_caps
	var target := clampf(chainage, 0.0, float(plan.length))
	var low := 0
	var high := cumulative.size() - 1
	while low + 1 < high:
		var middle := (low + high) / 2
		if cumulative[middle] <= target:
			low = middle
		else:
			high = middle
	var ds := cumulative[low + 1] - cumulative[low]
	var t := (target - cumulative[low]) / ds if ds > 0.0 else 0.0
	return lerpf(planned[low], planned[low + 1], t)


func _v5_signed_curvature(route_id: String, chainage: float, span: float) -> float:
	if span <= 0.000001:
		return 0.0
	var tangent_now: Vector2 = _route_sample(route_id, chainage).tangent
	var tangent_forward: Vector2 = _route_sample(route_id, chainage + span).tangent
	return _signed_angle_2d(tangent_now, tangent_forward) / span


func _v5_available_thrust(speed: float) -> float:
	return MotionMath.powered_thrust(craft.tuning.drive_thrust_accel, speed, craft.tuning.drive_powered_speed_soft, craft.tuning.drive_powered_speed_cap)


func _signed_angle_2d(from_direction: Vector2, to_direction: Vector2) -> float:
	return atan2(from_direction.x * to_direction.y - from_direction.y * to_direction.x, clampf(from_direction.dot(to_direction), -1.0, 1.0))


func _powered_waypoint_controller(controller: Dictionary) -> void:
	var waypoints: Array = controller.waypoints_xz_m
	powered_waypoint_index = clampi(powered_waypoint_index, 0, waypoints.size() - 1)
	var point := Vector2(craft.global_position.x, craft.global_position.z)
	while powered_waypoint_index < waypoints.size() - 1 and point.distance_to(P1AWorldData.xz(waypoints[powered_waypoint_index])) <= float(controller.waypoint_radius_m):
		powered_waypoint_index += 1
	_steer_toward(P1AWorldData.xz(waypoints[powered_waypoint_index]), float(controller.steer_gain))
	active_controller_throttle = float(controller.throttle)
	Input.action_press("throttle", active_controller_throttle)


func _multi_route_controller(controller: Dictionary) -> void:
	var path: Array = controller.path
	multi_segment = clampi(multi_segment, 0, path.size() - 1)
	var segment: Dictionary = path[multi_segment]
	var route_id := String(segment.route)
	var nearest := _nearest_global(route_id, Vector2(craft.global_position.x, craft.global_position.z))
	var direction := String(segment.direction)
	var forward := direction == "FORWARD"
	var end_chainage := float(segment.end_chainage_m)
	var progress_reached := float(nearest.chainage) >= end_chainage - 1.0 if forward else float(nearest.chainage) <= end_chainage + 1.0
	if progress_reached and multi_segment < path.size() - 1:
		multi_segment += 1
		segment = path[multi_segment]
		route_id = String(segment.route)
		nearest = _nearest_global(route_id, Vector2(craft.global_position.x, craft.global_position.z))
		direction = String(segment.direction)
		forward = direction == "FORWARD"
	var target_chainage := float(nearest.chainage) + (float(controller.lookahead_m) if forward else -float(controller.lookahead_m))
	_steer_toward(_route_sample(route_id, target_chainage).point, 1.6)
	active_controller_throttle = float(controller.throttle_command)
	Input.action_press("throttle", active_controller_throttle)
	maximum_chainage = maxf(maximum_chainage, float(nearest.chainage))


func _supported_hop_bracket_controller(controller: Dictionary) -> void:
	Input.action_release("hop")
	if support_ready_tick < 0:
		return
	var runup: Dictionary = controller.runup
	var point := Vector2(craft.global_position.x, craft.global_position.z)
	_steer_toward(Vector2(8.0, float(runup.centerline_z_m)), float(runup.steer_gain))
	var speed := Vector2(craft.velocity.x, craft.velocity.z).length()
	var minimum_speed := float(runup.minimum_trigger_speed_mps)
	var maximum_speed := float(runup.maximum_trigger_speed_mps)
	if speed < minimum_speed:
		active_controller_throttle = float(runup.throttle_below_band)
		Input.action_press("throttle", active_controller_throttle)
	elif speed > maximum_speed:
		Input.action_press("brake", float(runup.brake_above_band))
	else:
		active_controller_throttle = float(runup.hold_throttle_in_band)
		Input.action_press("throttle", active_controller_throttle)
	if hop_command_tick >= 0 or hop_timing_offset_m == INF:
		return
	var timing: Dictionary = controller.timing_model
	var apex_time := float(timing.apex_time_s)
	hop_trigger_x_m = float(timing.bar_center_x_m) - speed * float(timing.hop_tangential_retention) * apex_time + hop_timing_offset_m
	if point.x + 0.000001 >= hop_trigger_x_m and speed + 0.000001 >= minimum_speed and speed <= maximum_speed + 0.000001:
		Input.action_press("hop", 1.0)
		hop_command_tick = telemetry.physics_tick
		hop_command_x_m = craft.global_position.x
		telemetry.emit_event({
			"event": "HOP_COMMAND",
			"timing_offset_m": hop_timing_offset_m,
			"trigger_x_m": hop_trigger_x_m,
			"craft_center_x_m": hop_command_x_m,
			"horizontal_speed_mps": speed,
		})


func _resolved_hop_timing_offset(controller: Dictionary) -> float:
	var command_line := _argument_value("--hop-offset-m")
	if not command_line.is_empty():
		return float(command_line)
	var selected = controller.get("selected_timing_offset_m", null)
	if selected == null:
		return INF
	return float(selected)


func _observe_support_readiness() -> void:
	var controller: Dictionary = vector.get("controller_commands", {})
	if String(controller.get("type", "")) != "SUPPORTED_HOP_BRACKET_CONTROLLER" or support_ready_tick >= 0:
		return
	var contract: Dictionary = controller.support_readiness
	var bad_event := false
	for event in observed:
		if int(event.get("physics_tick", -1)) != telemetry.physics_tick:
			continue
		if String(event.get("event", "")) in ["COLLISION_SAMPLE", "RESET", "DIAGNOSTIC_SPAWN"]:
			bad_event = true
			break
	var normal_speed := craft.velocity.dot(craft.support_normal)
	var ready := (
		craft.probe_hit_count >= int(contract.minimum_probe_hit_count)
		and craft.measured_height + 0.000001 >= float(contract.minimum_measured_height_m)
		and craft.measured_height <= float(contract.maximum_measured_height_m) + 0.000001
		and craft.support_reacquire_blend + 0.000001 >= float(contract.minimum_support_reacquire_blend)
		and absf(normal_speed) <= float(contract.maximum_abs_support_normal_speed_mps) + 0.000001
		and craft.fold_amount <= float(contract.maximum_fold_amount) + 0.000001
		and craft.hop_cooldown_remaining <= float(contract.maximum_hop_cooldown_s) + 0.000001
		and (not bool(contract.no_collision_or_reset_during_readiness) or not bad_event)
	)
	if ready:
		support_ready_consecutive += 1
		maximum_support_ready_consecutive = maxi(maximum_support_ready_consecutive, support_ready_consecutive)
	else:
		support_ready_consecutive = 0
	if support_ready_consecutive >= int(contract.minimum_consecutive_physics_ticks):
		support_ready_tick = telemetry.physics_tick
		telemetry.emit_event({
			"event": "SUPPORT_READY",
			"consecutive_ticks": support_ready_consecutive,
			"probe_hit_count": craft.probe_hit_count,
			"measured_height_m": craft.measured_height,
			"support_reacquire_blend": craft.support_reacquire_blend,
			"support_normal_speed_mps": normal_speed,
			"fold_amount": craft.fold_amount,
			"hop_cooldown_s": craft.hop_cooldown_remaining,
		})


func _observe_bar_overlap_clearance(point: Vector2) -> void:
	var controller: Dictionary = vector.get("controller_commands", {})
	if String(controller.get("type", "")) != "SUPPORTED_HOP_BRACKET_CONTROLLER":
		return
	var contract: Dictionary = controller.bar_overlap_clearance
	if point.x < float(contract.plan_overlap_center_x_min_m) or point.x > float(contract.plan_overlap_center_x_max_m):
		return
	if point.y < float(contract.plan_overlap_center_z_min_m) or point.y > float(contract.plan_overlap_center_z_max_m):
		return
	var mesh: Dictionary = data.solids.get("MESH_HOP_BAR_01", {})
	var top_y := float(mesh.get("top_y_m", 0.0))
	var clearance := craft.global_position.y - float(contract.craft_vertical_radius_m) - top_y
	minimum_bar_overlap_vertical_clearance_m = minf(minimum_bar_overlap_vertical_clearance_m, clearance)
	bar_overlap_clearance_sample_count += 1
	telemetry.emit_event({
		"event": "HOP_BAR_CLEARANCE_SAMPLE",
		"craft_center_xyz_m": [craft.global_position.x, craft.global_position.y, craft.global_position.z],
		"bar_top_y_m": top_y,
		"clearance_m": clearance,
	})


func _point_target_controller(controller: Dictionary) -> void:
	_steer_toward(P1AWorldData.xz(controller.target_xz_m), float(controller.steer_gain))
	active_controller_throttle = float(controller.throttle)
	Input.action_press("throttle", active_controller_throttle)


func _steer_toward(target: Vector2, gain: float) -> void:
	var position := Vector2(craft.global_position.x, craft.global_position.z)
	var desired := (target - position).normalized()
	var forward := Vector2(-craft.global_basis.z.x, -craft.global_basis.z.z).normalized()
	var error := atan2(forward.x * desired.y - forward.y * desired.x, forward.dot(desired))
	var steer := clampf(gain * error, -1.0, 1.0)
	if steer >= 0.0:
		Input.action_press("steer_right", steer)
	else:
		Input.action_press("steer_left", -steer)


func _observe_thresholds_before_tick() -> void:
	pass


func _observe_thresholds_after_tick() -> void:
	var point := Vector2(craft.global_position.x, craft.global_position.z)
	var speed := Vector2(craft.velocity.x, craft.velocity.z).length()
	peak_horizontal_speed_mps = maxf(peak_horizontal_speed_mps, speed)
	var thresholds: Dictionary = vector.get("thresholds", {})
	if thresholds.has("fast_route_speed_floor_mps") and speed + 0.000001 >= float(thresholds.fast_route_speed_floor_mps):
		distance_at_or_above_fast_speed_m += previous_metric_point.distance_to(point)
	previous_metric_point = point
	_observe_crossing_windows(point)
	_observe_support_readiness()
	_observe_bar_overlap_clearance(point)
	var obstacle_id := _boundary_obstacle_id()
	if not obstacle_id.is_empty() and _inside_obstacle(obstacle_id, point):
		obstacle_inside_samples += 1
	if String(vector.id) == "RT_HOP_SUCCESS":
		maximum_chainage = maxf(maximum_chainage, float(_nearest_global("HOP", point).chainage))
	_observe_v4_route_projection(point, speed)
	_observe_v5_route_projection(point, speed)
	_observe_v6_route_projection(point, speed)
	_observe_v7_route_projection(point, speed)
	_observe_human_route_projection(point, speed)
	_observe_test_driver_liveness(point, speed)
	previous_observation_point = point


func _termination_reached() -> bool:
	var termination: Dictionary = vector.get("termination", {})
	var controller: Dictionary = vector.get("controller_commands", {})
	var controller_type := String(controller.get("type", ""))
	if controller_type in ["ROUTE_FOLLOWER_INPUT_CONTROLLER_V4_FORWARD_BRAKING_CONTAINED", "ROUTE_FOLLOWER_INPUT_CONTROLLER_V5_INERTIAL_THRUST_VECTOR_CONTAINED", "ROUTE_FOLLOWER_INPUT_CONTROLLER_V6_DECEL_CONSTRAINED_THRUST_VECTOR_CONTAINED", "ROUTE_FOLLOWER_INPUT_CONTROLLER_V7_PHASE_SEPARATED_BRAKE_CAPTURE_CONTAINED", HUMAN_REPLAY_CONTROLLER] and bool(controller.get("fail_fast_on_first_unauthorized_hard_collision", false)):
		var first_collision := _first_unauthorized_hard_collision()
		if not first_collision.is_empty():
			termination_completed = false
			termination_reason = "FIRST_UNAUTHORIZED_HARD_COLLISION"
			termination_physics_tick = int(first_collision.get("physics_tick", telemetry.physics_tick))
			termination_vector_tick = vector_tick
			return true
	if controller_type in ["ROUTE_FOLLOWER_INPUT_CONTROLLER_V5_INERTIAL_THRUST_VECTOR_CONTAINED", "ROUTE_FOLLOWER_INPUT_CONTROLLER_V6_DECEL_CONSTRAINED_THRUST_VECTOR_CONTAINED", "ROUTE_FOLLOWER_INPUT_CONTROLLER_V7_PHASE_SEPARATED_BRAKE_CAPTURE_CONTAINED", HUMAN_REPLAY_CONTROLLER] and bool(controller.get("fail_fast_on_first_hard_lateral_limit_violation", false)) and not route_projection_records.is_empty():
		var last_projection: Dictionary = route_projection_records[-1]
		if float(last_projection.get("route_lateral_distance_m", 0.0)) > float(controller.lateral_hard_limit_m) + 0.000001:
			first_hard_limit_violation = last_projection.duplicate(true)
			termination_completed = false
			termination_reason = "FIRST_HARD_LATERAL_LIMIT_VIOLATION"
			termination_physics_tick = int(last_projection.get("physics_tick", telemetry.physics_tick))
			termination_vector_tick = vector_tick
			return true
	if controller_type == "ROUTE_FOLLOWER_INPUT_CONTROLLER_V6_DECEL_CONSTRAINED_THRUST_VECTOR_CONTAINED" and not v6_slowdown_health_violation.is_empty():
		termination_completed = false
		termination_reason = "SUSTAINED_SLOWDOWN_SPEED_RISE"
		termination_physics_tick = int(v6_slowdown_health_violation.get("physics_tick", telemetry.physics_tick))
		termination_vector_tick = vector_tick
		return true
	if controller_type == "ROUTE_FOLLOWER_INPUT_CONTROLLER_V7_PHASE_SEPARATED_BRAKE_CAPTURE_CONTAINED" and not v7_brake_health_violation.is_empty():
		termination_completed = false
		termination_reason = "BRAKE_COMMIT_SPEED_RISE"
		termination_physics_tick = int(v7_brake_health_violation.get("physics_tick", telemetry.physics_tick))
		termination_vector_tick = vector_tick
		return true
	if String(termination.get("type", "")) == "FIRST_VALID_HOP_CLEARANCE":
		return _q1_hop_clearance_completion_satisfied(termination)
	if String(vector.id) == "RT_R0_SURFACE_NEUTRALITY":
		return maximum_chainage >= float(vector.controller_commands.terminate_chainage_m)
	if String(vector.id).begins_with("RT_ROUTE_") or String(vector.id) == "RT_DOG_PASSAGE":
		var requested_route := _requested_route_id()
		for event in observed:
			if String(event.get("event", "")) == "ROUTE_STATE" and String(event.get("state", "")) == "TRAVERSED" and String(event.get("route_id", "")) == requested_route:
				return true
	if controller_type == HUMAN_REPLAY_CONTROLLER and vector_tick >= human_input_records.size() - 1:
		termination_completed = false
		termination_reason = "INPUT_TRACE_EXHAUSTED"
		termination_physics_tick = telemetry.physics_tick
		termination_vector_tick = vector_tick
		return true
	if String(vector.id).begins_with("RT_GATE_"):
		return multi_segment >= int(vector.controller_commands.path.size()) - 1 and _multi_end_reached()
	return false


func _q1_hop_clearance_completion_satisfied(termination: Dictionary) -> bool:
	if String(vector.id) != "RT_HOP_SUCCESS":
		return false
	var window_id := String(termination.get("window_id", ""))
	if window_id != "HOP_BAR_HJE_CLEAR" or not crossing_states.has(window_id):
		return false
	var records: Array = crossing_states[window_id].records
	if records.is_empty():
		return false
	var crossing: Dictionary = records[-1]
	var completion_tick := int(crossing.get("physics_tick", -1))
	# Only the newly observed bounded crossing may complete Q1. A stale earlier crossing
	# cannot be promoted by later overlap, landing, or controller motion.
	if completion_tick != telemetry.physics_tick:
		return false
	var requires: Dictionary = termination.get("requires", {})
	var first_hop_tick := _first_event_physics_tick("HOP_STARTED")
	if support_ready_tick < 0 or hop_command_tick < 0 or first_hop_tick < 0:
		return false
	if not (support_ready_tick < hop_command_tick and hop_command_tick < first_hop_tick and first_hop_tick <= completion_tick):
		return false
	if maximum_support_ready_consecutive < int(requires.get("minimum_support_ready_consecutive_ticks", 0)):
		return false
	if _event_count("HOP_STARTED") != int(requires.get("exact_hop_started_count", 1)):
		return false
	if bar_overlap_clearance_sample_count < int(requires.get("minimum_bar_overlap_clearance_sample_count", 1)):
		return false
	if minimum_bar_overlap_vertical_clearance_m + 0.000001 < float(requires.get("minimum_bar_overlap_vertical_clearance_m", 0.0)):
		return false
	if _collision_count_through("HOP_BAR_01", completion_tick) > int(requires.get("maximum_hop_bar_collision_count", 0)):
		return false
	if _hard_collision_count_through(completion_tick, false) > int(requires.get("maximum_hard_collision_count", 0)):
		return false
	termination_completed = true
	termination_reason = "FIRST_VALID_HOP_CLEARANCE"
	termination_physics_tick = completion_tick
	termination_vector_tick = vector_tick
	termination_window_id = window_id
	return true


func _multi_end_reached() -> bool:
	var segment: Dictionary = vector.controller_commands.path[multi_segment]
	var nearest := _nearest_global(String(segment.route), Vector2(craft.global_position.x, craft.global_position.z))
	return float(nearest.chainage) >= float(segment.end_chainage_m) - 0.75 if String(segment.direction) == "FORWARD" else float(nearest.chainage) <= float(segment.end_chainage_m) + 0.75


func _evaluate() -> Array[String]:
	var failures: Array[String] = []
	failures.append_array(preflight_failures)
	failures.append_array(command_assertion_failures)
	for expected_value in vector.get("expected_events", []):
		var expected: Dictionary = expected_value
		if bool(expected.get("allowed", false)):
			continue
		if expected.has("ordered_values"):
			var actual := _ordered_event_values(String(expected.event), "surface_class")
			if not _contains_subsequence(actual, expected.ordered_values):
				failures.append("missing ordered %s sequence %s (actual %s)" % [expected.event, expected.ordered_values, actual])
			continue
		var matched := 0
		for event in observed:
			if _event_matches(event, expected):
				matched += 1
		if matched < int(expected.get("minimum_count", 1)):
			failures.append("missing expected event %s" % JSON.stringify(expected))
	var thresholds: Dictionary = vector.get("thresholds", {})
	var termination: Dictionary = vector.get("termination", {})
	if String(termination.get("type", "")) == "FIRST_VALID_HOP_CLEARANCE" and not termination_completed:
		failures.append("authorized Q1 completion event not reached before timeout")
	if _reset_count("FALL") > int(thresholds.get("maximum_fall_reset_count", 999999)):
		failures.append("fall reset maximum exceeded")
	if _hard_collision_count(true) > int(thresholds.get("maximum_non_hop_hard_collision_count", 999999)):
		failures.append("non-Hop hard collision maximum exceeded")
	if _hard_collision_count(false) > int(thresholds.get("maximum_hard_collision_count", 999999)):
		failures.append("hard collision maximum exceeded")
	if _collision_count("HOP_BAR_01") > int(thresholds.get("maximum_hop_bar_collision_count", 999999)):
		failures.append("Hop-bar collision maximum exceeded")
	if _window_count_by_class("TARGET_FACE") > int(thresholds.get("maximum_crossings_to_opposite_side_of_target_face", 999999)):
		failures.append("bounded target-face crossing maximum exceeded")
	if _window_count_by_class("END_BYPASS") > int(thresholds.get("maximum_hop_end_bypass_crossing_count", 999999)):
		failures.append("Hop end-bypass crossing maximum exceeded")
	if _window_count_by_class("BAR_SPAN") > int(thresholds.get("maximum_hop_bar_span_crossing_count", 999999)):
		failures.append("Hop bar-span crossing maximum exceeded")
	if _window_count_by_id("HOP_BAR_HJE_CLEAR") < int(thresholds.get("minimum_HOP_BAR_HJE_CLEAR_crossing_count", 0)):
		failures.append("HOP_BAR_HJE_CLEAR crossing minimum not met")
	if obstacle_inside_samples > int(thresholds.get("maximum_craft_center_samples_inside_hard_obstacle", thresholds.get("maximum_hard_obstacle_penetration_samples", 999999))):
		failures.append("craft center entered hard obstacle")
	if _event_count("HOP_STARTED") < int(thresholds.get("minimum_hop_started_count", 0)):
		failures.append("Hop minimum not met")
	if _event_count("HOP_STARTED") != int(thresholds.get("exact_hop_started_count", _event_count("HOP_STARTED"))):
		failures.append("Hop exact count mismatch")
	if distance_at_or_above_fast_speed_m + 0.01 < float(thresholds.get("minimum_distance_at_or_above_fast_route_speed_m", 0.0)):
		failures.append("fast-route sustained-distance minimum not met")
	if maximum_chainage + 0.01 < float(thresholds.get("minimum_final_route_chainage_m", 0.0)):
		failures.append("minimum final chainage not met")
	if thresholds.has("minimum_genuine_classified_distance_m"):
		var evidence := _genuine_distance_evidence()
		if float(evidence.actual_m) + 0.000001 < float(evidence.required_m):
			failures.append("requested-route genuine TRAVERSED distance minimum not met: route=%s actual=%.6f required=%.6f" % [evidence.route_id, evidence.actual_m, evidence.required_m])
	if _route_state_count("ENTERED") > int(thresholds.get("maximum_route_entered_event_count", 999999)):
		failures.append("route ENTERED maximum exceeded")
	if _route_state_count("TRAVERSED") > int(thresholds.get("maximum_route_traversed_event_count", 999999)):
		failures.append("route TRAVERSED maximum exceeded")
	if thresholds.has("exact_gate_crossing_count") and _event_count("GATE_CROSSED") != int(thresholds.exact_gate_crossing_count):
		failures.append("gate crossing exact count mismatch")
	if thresholds.has("required_surface_class_sequence"):
		var classes := _ordered_event_values("SURFACE_CLASS_CHANGED", "surface_class")
		if not _contains_subsequence(classes, thresholds.required_surface_class_sequence):
			failures.append("required surface-class sequence not observed")
	if thresholds.has("target_face_plane_id") and not _has_window_id(String(thresholds.target_face_plane_id)):
		failures.append("target-face window ID is not active")
	if thresholds.has("maximum_hop_started_physics_tick"):
		var first_hop_tick := _first_event_physics_tick("HOP_STARTED")
		if first_hop_tick < 0 or first_hop_tick > int(thresholds.maximum_hop_started_physics_tick):
			failures.append("HOP_STARTED occurred too late or was absent")
	if _collision_count("HOP_BAR_01") < int(thresholds.get("minimum_hop_bar_collision_count", 0)):
		failures.append("Hop-bar collision minimum not met")
	if _window_count_by_id("HOP_BAR_HJE_CLEAR") > int(thresholds.get("maximum_hop_bar_hje_clear_crossing_count", 999999)):
		failures.append("HOP_BAR_HJE_CLEAR crossing maximum exceeded")
	if thresholds.has("expected_test_driver_liveness_sample_count"):
		var expected_liveness := int(thresholds.expected_test_driver_liveness_sample_count)
		if liveness_records.size() != expected_liveness:
			failures.append("test-driver liveness sample count mismatch")
	if bool(thresholds.get("required_liveness_every_tick", false)) and not _liveness_is_contiguous():
		failures.append("test-driver liveness is not every-tick contiguous")
	if _positive_throttle_fraction() + 0.000001 < float(thresholds.get("minimum_positive_throttle_fraction", 0.0)):
		failures.append("positive-throttle liveness fraction minimum not met")
	if not liveness_records.is_empty() and float(liveness_records[0].horizontal_speed_mps) + 0.000001 < float(thresholds.get("minimum_first_liveness_horizontal_speed_mps", 0.0)):
		failures.append("first liveness speed minimum not met")
	if peak_horizontal_speed_mps + 0.000001 < float(thresholds.get("minimum_peak_horizontal_speed_mps", 0.0)):
		failures.append("peak horizontal speed minimum not met")
	if maximum_test_driver_path_deviation_m > float(thresholds.get("maximum_test_driver_path_deviation_m", INF)) + 0.000001:
		failures.append("test-driver path deviation maximum exceeded")
	var active_controller_type := String(vector.get("controller_commands", {}).get("type", ""))
	if active_controller_type in ["ROUTE_FOLLOWER_INPUT_CONTROLLER_V4_FORWARD_BRAKING_CONTAINED", "ROUTE_FOLLOWER_INPUT_CONTROLLER_V5_INERTIAL_THRUST_VECTOR_CONTAINED", "ROUTE_FOLLOWER_INPUT_CONTROLLER_V6_DECEL_CONSTRAINED_THRUST_VECTOR_CONTAINED", "ROUTE_FOLLOWER_INPUT_CONTROLLER_V7_PHASE_SEPARATED_BRAKE_CAPTURE_CONTAINED", HUMAN_REPLAY_CONTROLLER]:
		if route_projection_records.is_empty():
			failures.append("fast-route projection evidence is absent")
		elif not _route_projection_is_contiguous():
			failures.append("fast-route projection evidence is not every-tick contiguous")
	if thresholds.has("maximum_powered_required_window_distance_m"):
		if powered_required_window_closest_sample.is_empty():
			failures.append("powered required-window approach has no qualifying sample")
		elif float(powered_required_window_closest_sample.distance_m) > float(thresholds.maximum_powered_required_window_distance_m) + 0.000001:
			failures.append("powered required-window closest approach maximum exceeded")
	if _collision_count("CORE_PLINTH_MASK") > int(thresholds.get("maximum_core_plinth_collision_count", 999999)):
		failures.append("CORE_PLINTH_MASK collision maximum exceeded")
	if thresholds.has("required_first_hard_geometry_id") and first_hard_geometry_id != String(thresholds.required_first_hard_geometry_id):
		failures.append("first hard geometry mismatch: actual=%s required=%s" % [first_hard_geometry_id, String(thresholds.required_first_hard_geometry_id)])
	if maximum_support_ready_consecutive < int(thresholds.get("minimum_support_ready_consecutive_ticks", 0)):
		failures.append("support-ready consecutive tick minimum not met")
	if bool(thresholds.get("support_ready_before_hop_command", false)) and (support_ready_tick < 0 or hop_command_tick < 0 or support_ready_tick >= hop_command_tick):
		failures.append("SUPPORT_READY did not precede HOP_COMMAND")
	if thresholds.has("maximum_hop_command_to_start_ticks"):
		var first_hop_tick := _first_event_physics_tick("HOP_STARTED")
		if hop_command_tick < 0 or first_hop_tick < 0 or first_hop_tick - hop_command_tick > int(thresholds.maximum_hop_command_to_start_ticks):
			failures.append("HOP_COMMAND to HOP_STARTED tick maximum exceeded")
	if bool(thresholds.get("hop_started_before_bar_contact_plane", false)):
		var required_x := float(vector.controller_commands.timing_model.required_hop_started_before_center_x_m)
		if first_hop_started_x_m == INF or first_hop_started_x_m >= required_x - 0.000001:
			failures.append("HOP_STARTED did not occur before the conservative bar-contact plane")
	if thresholds.has("minimum_bar_overlap_vertical_clearance_m"):
		if bar_overlap_clearance_sample_count <= 0 or minimum_bar_overlap_vertical_clearance_m + 0.000001 < float(thresholds.minimum_bar_overlap_vertical_clearance_m):
			failures.append("bar-overlap vertical clearance minimum not met")
	failures.append_array(_evaluate_tuning_digest(thresholds))
	if String(vector.id) == "RT_DIAGNOSTIC_PATHS":
		failures.append_array(_evaluate_diagnostic())
	if String(vector.id) == "RT_FRESH_OPEN_IDENTITY":
		failures.append_array(_evaluate_identity())
	return failures


func _evaluate_tuning_digest(thresholds: Dictionary) -> Array[String]:
	var failures: Array[String] = []
	if not thresholds.has("movement_tuning_digest_algorithm_id"):
		return failures
	if String(thresholds.movement_tuning_digest_algorithm_id) != TUNING_DIGEST_ALGORITHM_ID:
		failures.append("movement tuning digest algorithm ID mismatch")
	if movement_tuning_digest_before != String(thresholds.required_movement_tuning_digest_before):
		failures.append("live movement tuning digest before mismatch")
	if movement_tuning_digest_after != String(thresholds.required_movement_tuning_digest_after):
		failures.append("live movement tuning digest after mismatch")
	if bool(thresholds.movement_tuning_digest_before_equals_after) and movement_tuning_digest_before != movement_tuning_digest_after:
		failures.append("live movement tuning digest changed during R0 sequence")
	return failures


func _evaluate_diagnostic() -> Array[String]:
	var failures: Array[String] = []
	if _reset_count("MANUAL") != 1:
		failures.append("manual reset exact count mismatch: expected=1 actual=%d" % _reset_count("MANUAL"))
	var expected: Array = vector.get("thresholds", {}).get("required_event_order", [])
	var actual: Array[String] = []
	for event in observed:
		match String(event.get("event", "")):
			"DIAGNOSTIC_SELECTION": actual.append("DIAGNOSTIC_SELECTION:%s" % event.selected_tour_id)
			"DIAGNOSTIC_SPAWN": actual.append("DIAGNOSTIC_SPAWN:%s" % event.get("spawn_id", ""))
			"RESET": actual.append("RESET:%s" % event.reason)
	if not _contains_subsequence(actual, expected):
		failures.append("diagnostic event order mismatch: %s" % actual)
	var route_credit_events := 0
	for event in observed:
		if String(event.get("event", "")) == "ROUTE_STATE" and String(event.get("state", "")) != "SPAWNED":
			route_credit_events += 1
	var maximum_route_credit := int(vector.get("thresholds", {}).get("maximum_route_entered_or_traversed_events_caused_by_spawn_or_reset", 0))
	if route_credit_events > maximum_route_credit:
		failures.append("spawn/reset route coverage credit maximum exceeded: actual=%d required<=%d" % [route_credit_events, maximum_route_credit])
	var required_selection := String(vector.thresholds.required_neutral_spawn_selection_id)
	if String(data.diagnostic.selection_order[gate_root.selection_index]) != required_selection:
		failures.append("neutral diagnostic selection mismatch at completion")
	return failures


func _evaluate_identity() -> Array[String]:
	var failures: Array[String] = []
	var thresholds: Dictionary = vector.thresholds
	if P1AWorldGate.BUILD_LABEL != String(thresholds.visible_build_label_exact):
		failures.append("build label mismatch")
	if String(data.diagnostic.default_menu_selection) != String(thresholds.default_diagnostic_selection):
		failures.append("default selection mismatch")
	if String(data.diagnostic.initial_craft_spawn.id) != String(thresholds.default_spawn_id):
		failures.append("default spawn mismatch")
	var actual_actions := _custom_input_actions()
	var expected_actions: Array = thresholds.exact_allowed_input_actions
	if actual_actions != expected_actions:
		failures.append("exact custom input-action set mismatch: %s" % actual_actions)
	var legacy_count := 0
	for action in actual_actions:
		if not (action in EXPECTED_CUSTOM_INPUT_ACTIONS):
			legacy_count += 1
	if legacy_count != int(thresholds.legacy_selector_action_count):
		failures.append("legacy selector action count mismatch")
	return failures


func _on_event(event: Dictionary) -> void:
	if terminal_result_emitted or terminal_evidence_sealed:
		post_result_event_count += 1
		return
	observed.append(event.duplicate(true))
	var name := String(event.get("event", ""))
	if name == "RESET" or name == "DIAGNOSTIC_SPAWN":
		_reset_crossing_history()
		previous_metric_point = Vector2(craft.global_position.x, craft.global_position.z)
	if name == "HOP_STARTED" and first_hop_started_x_m == INF:
		first_hop_started_x_m = craft.global_position.x
	if name == "COLLISION_SAMPLE" and int(event.get("physics_tick", -1)) >= collision_window_start_tick:
		var source_id := String(event.get("source_geometry_id", ""))
		if first_hard_geometry_id.is_empty():
			first_hard_geometry_id = source_id
			first_hard_collision_tick = int(event.get("physics_tick", -1))
		if source_id == "HOP_BAR_01" and first_hop_bar_contact_tick < 0:
			first_hop_bar_contact_tick = int(event.get("physics_tick", -1))


func _prepare_route_cache() -> void:
	for route_id_value in data.routes:
		var route_id := String(route_id_value)
		var raw: Array = data.routes[route_id].points_xz_m
		var points := PackedVector2Array()
		var cumulative := PackedFloat64Array()
		points.resize(raw.size())
		cumulative.resize(raw.size())
		var length := 0.0
		for index in raw.size():
			points[index] = P1AWorldData.xz(raw[index])
			if index > 0: length += points[index - 1].distance_to(points[index])
			cumulative[index] = length
		route_cache[route_id] = {"points": points, "cumulative": cumulative, "length": length, "cursor": 0}


func _nearest_cached(route_id: String, point: Vector2) -> Dictionary:
	var cache: Dictionary = route_cache[route_id]
	var points: PackedVector2Array = cache.points
	var cumulative: PackedFloat64Array = cache.cumulative
	var center := int(cache.cursor)
	var start := maxi(0, center - 120)
	var finish := mini(points.size() - 2, center + 240)
	var best_d2 := INF
	var best_index := center
	var best_t := 0.0
	for index in range(start, finish + 1):
		var segment := points[index + 1] - points[index]
		var t := clampf((point - points[index]).dot(segment) / segment.length_squared(), 0.0, 1.0)
		var d2 := point.distance_squared_to(points[index] + segment * t)
		if d2 < best_d2:
			best_d2 = d2; best_index = index; best_t = t
	cache.cursor = best_index
	route_cache[route_id] = cache
	var chainage := cumulative[best_index] + points[best_index].distance_to(points[best_index + 1]) * best_t
	return {"chainage": chainage, "length": float(cache.length), "distance": sqrt(best_d2)}


func _nearest_global(route_id: String, point: Vector2) -> Dictionary:
	var cache: Dictionary = route_cache[route_id]
	var points: PackedVector2Array = cache.points
	var cumulative: PackedFloat64Array = cache.cumulative
	var best_d2 := INF
	var best_index := 0
	var best_t := 0.0
	var best_chainage := 0.0
	for index in points.size() - 1:
		var segment := points[index + 1] - points[index]
		var length_squared := segment.length_squared()
		var t := clampf((point - points[index]).dot(segment) / length_squared, 0.0, 1.0) if length_squared > 0.0 else 0.0
		var d2 := point.distance_squared_to(points[index] + segment * t)
		var chainage := cumulative[index] + sqrt(length_squared) * t
		if d2 < best_d2 - 0.000000000001 or (absf(d2 - best_d2) <= 0.000000000001 and chainage < best_chainage):
			best_d2 = d2
			best_index = index
			best_t = t
			best_chainage = chainage
	return {"chainage": best_chainage, "length": float(cache.length), "distance": sqrt(best_d2), "segment_index": best_index, "segment_t": best_t}


func _route_sample(route_id: String, chainage: float) -> Dictionary:
	var cache: Dictionary = route_cache[route_id]
	var points: PackedVector2Array = cache.points
	var cumulative: PackedFloat64Array = cache.cumulative
	var target := clampf(chainage, 0.0, float(cache.length))
	var low := 0
	var high := cumulative.size() - 1
	while low + 1 < high:
		var middle := (low + high) / 2
		if cumulative[middle] <= target: low = middle
		else: high = middle
	var length := points[low].distance_to(points[low + 1])
	var t := (target - cumulative[low]) / length if length > 0.0 else 0.0
	return {"point": points[low].lerp(points[low + 1], t), "tangent": (points[low + 1] - points[low]).normalized()}


func _maximum_ticks() -> int:
	if String(vector.get("controller_commands", {}).get("type", "")) == HUMAN_REPLAY_CONTROLLER:
		return maxi(human_input_records.size() - 1, 0)
	if vector.has("duration_s"): return int(round(float(vector.duration_s) * 60.0))
	var termination: Dictionary = vector.get("termination", {})
	if termination.has("timeout_tick"): return int(termination.timeout_tick)
	if termination.has("tick"): return int(termination.tick)
	return int(ceil(float(termination.get("maximum_duration_s", 3.0)) * 60.0))


func _boundary_obstacle_id() -> String:
	var explicit := String(vector.get("obstacle_geometry_id", ""))
	if not explicit.is_empty():
		return explicit
	if not vector.has("spawn_transform"):
		return ""
	var source: Dictionary = vector.spawn_transform.get("source", {})
	var value := String(source.get("obstacle", source.get("boundary", "")))
	if value == "CORE_PLINTH": return "CORE_PLINTH_MASK"
	if value == "OUTER_CLOSURE": return "OUTER_CLOSURE_MASK"
	return value


func _inside_obstacle(id: String, point: Vector2) -> bool:
	return data.geometry_contains(id, point)


func _initialize_crossing_states() -> void:
	crossing_states.clear()
	for spec_value in _active_crossing_windows():
		var spec: Dictionary = spec_value
		var id := String(spec.id)
		crossing_states[id] = {
			"spec": spec,
			"sample_valid": false,
			"previous_distance": 0.0,
			"armed": false,
			"count": 0,
			"points": [],
			"records": [],
			"rejected": [],
			"maximum_signed_distance": -INF,
		}


func _reset_crossing_history() -> void:
	for id_value in crossing_states.keys():
		var id := String(id_value)
		var state: Dictionary = crossing_states[id]
		state.sample_valid = false
		state.previous_distance = 0.0
		state.armed = false
		crossing_states[id] = state


func _active_crossing_windows() -> Array[Dictionary]:
	var result: Array[Dictionary] = []
	if vector.has("crossing_windows"):
		for value in vector.crossing_windows:
			result.append(_normalized_window(value, "GENERIC"))
	elif vector.has("target_face_plane"):
		result.append(_normalized_window(vector.target_face_plane, "TARGET_FACE"))
	elif vector.has("crossing_plane"):
		result.append(_normalized_window(vector.crossing_plane, "HOP_CLEAR"))
	elif vector.has("crossing_plane_id"):
		result.append(_normalized_window(_named_plane_raw(String(vector.crossing_plane_id)), "GENERIC"))
	return result


func _normalized_window(raw_value, fallback_class: String) -> Dictionary:
	var raw: Dictionary = raw_value
	var result := raw.duplicate(true)
	result["id"] = String(result.get("id", "UNNAMED_WINDOW"))
	result["evidence_class"] = String(result.get("evidence_class", fallback_class))
	result["unit_tangent_xz"] = result.get("unit_tangent_xz", [-float(result.unit_normal_xz[1]), float(result.unit_normal_xz[0])])
	result["minimum_tangent_offset_m"] = float(result.get("minimum_tangent_offset_m", -INF))
	result["maximum_tangent_offset_m"] = float(result.get("maximum_tangent_offset_m", INF))
	result["required_source_geometry_id"] = String(result.get("required_source_geometry_id", ""))
	result["maximum_source_boundary_distance_m"] = float(result.get("maximum_source_boundary_distance_m", 0.0))
	return result


func _named_plane_raw(id: String) -> Dictionary:
	var named: Dictionary = fixture.global_rules.named_crossing_planes
	return named.get(id, {}).duplicate(true)


func _observe_crossing_windows(point: Vector2) -> void:
	var ids: Array = crossing_states.keys()
	ids.sort()
	for id_value in ids:
		var id := String(id_value)
		var state: Dictionary = crossing_states[id]
		var spec: Dictionary = state.spec
		var plane_point := P1AWorldData.xz(spec.point_xz_m)
		var normal := P1AWorldData.xz(spec.unit_normal_xz).normalized()
		var tangent := P1AWorldData.xz(spec.unit_tangent_xz).normalized()
		var distance := (point - plane_point).dot(normal)
		state.maximum_signed_distance = maxf(float(state.maximum_signed_distance), distance)
		if not bool(state.sample_valid):
			state.sample_valid = true
			state.previous_distance = distance
			state.armed = distance < 0.0
			crossing_states[id] = state
			continue
		var previous_distance := float(state.previous_distance)
		if bool(state.armed) and previous_distance < 0.0 and distance >= 0.0:
			var denominator := distance - previous_distance
			var fraction := clampf(-previous_distance / denominator, 0.0, 1.0) if absf(denominator) > 0.000000001 else 1.0
			var crossing := previous_observation_point.lerp(point, fraction)
			var tangent_offset := (crossing - plane_point).dot(tangent)
			var in_window := tangent_offset + 0.000001 >= float(spec.minimum_tangent_offset_m) and tangent_offset - 0.000001 <= float(spec.maximum_tangent_offset_m)
			var associated := _window_crossing_associated(spec, crossing)
			if in_window and associated:
				state.count = int(state.count) + 1
				state.points.append([crossing.x, crossing.y])
				state.records.append({"point_xz_m": [crossing.x, crossing.y], "physics_tick": telemetry.physics_tick, "horizontal_speed_mps": Vector2(craft.velocity.x, craft.velocity.z).length(), "commanded_throttle": active_controller_throttle})
			else:
				state.rejected.append({"point_xz_m": [crossing.x, crossing.y], "tangent_offset_m": tangent_offset, "in_window": in_window, "associated": associated})
			state.armed = false
		elif distance < 0.0:
			state.armed = true
		state.previous_distance = distance
		crossing_states[id] = state


func _window_crossing_associated(spec: Dictionary, crossing: Vector2) -> bool:
	var source_id := String(spec.required_source_geometry_id)
	if source_id.is_empty():
		return true
	return data.geometry_contains(source_id, crossing) or data.geometry_boundary_distance(source_id, crossing) <= float(spec.maximum_source_boundary_distance_m) + 0.000001


func _window_count_by_class(evidence_class: String) -> int:
	var count := 0
	for state_value in crossing_states.values():
		var state: Dictionary = state_value
		if String(state.spec.evidence_class) == evidence_class:
			count += int(state.count)
	return count


func _window_count_by_id(id: String) -> int:
	return int(crossing_states.get(id, {}).get("count", 0))


func _has_window_id(id: String) -> bool:
	return crossing_states.has(id)


func _all_window_crossing_count() -> int:
	var count := 0
	for state_value in crossing_states.values():
		count += int(state_value.count)
	return count


func _all_window_crossing_points() -> Array:
	var result := []
	for id_value in crossing_states.keys():
		var id := String(id_value)
		for point in crossing_states[id].points:
			result.append({"window_id": id, "point_xz_m": point})
	return result


func _maximum_window_signed_distance() -> float:
	var result := -INF
	for state_value in crossing_states.values():
		result = maxf(result, float(state_value.maximum_signed_distance))
	return result if result > -INF else 0.0


func _crossing_results() -> Dictionary:
	var result := {}
	var ids: Array = crossing_states.keys()
	ids.sort()
	for id_value in ids:
		var id := String(id_value)
		var state: Dictionary = crossing_states[id]
		result[id] = {
			"evidence_class": String(state.spec.evidence_class),
			"count": int(state.count),
			"points_xz_m": state.points,
			"crossing_records": state.records,
			"rejected_crossings": state.rejected,
			"maximum_signed_distance_m": float(state.maximum_signed_distance) if float(state.maximum_signed_distance) > -INF else 0.0,
		}
	return result


func _requested_route_id() -> String:
	return String(vector.get("controller_commands", {}).get("route_id", ""))


func _genuine_distance_evidence() -> Dictionary:
	var route_id := _requested_route_id()
	var actual := 0.0
	for event in observed:
		if String(event.get("event", "")) == "ROUTE_STATE" and String(event.get("state", "")) == "TRAVERSED" and String(event.get("route_id", "")) == route_id:
			actual = maxf(actual, float(event.get("distance_since_genuine_entry_m", 0.0)))
	return {"route_id": route_id, "actual_m": actual, "required_m": float(vector.get("thresholds", {}).get("minimum_genuine_classified_distance_m", 0.0)), "source": "requested route TRAVERSED event only"}


func _route_state_count(state_name: String) -> int:
	var count := 0
	for event in observed:
		if String(event.get("event", "")) == "ROUTE_STATE" and String(event.get("state", "")) == state_name:
			count += 1
	return count


func _observe_v4_route_projection(point: Vector2, speed: float) -> void:
	var controller: Dictionary = vector.get("controller_commands", {})
	if String(controller.get("type", "")) != "ROUTE_FOLLOWER_INPUT_CONTROLLER_V4_FORWARD_BRAKING_CONTAINED":
		return
	var route_id := String(controller.route_id)
	var nearest := _nearest_global(route_id, point)
	var sample := _route_sample(route_id, float(nearest.chainage))
	var tangent: Vector2 = sample.tangent
	var normal: Vector2 = Vector2(-tangent.y, tangent.x)
	var sample_point: Vector2 = sample.point
	var signed_error: float = (point - sample_point).dot(normal)
	var path_distance := float(nearest.distance)
	maximum_test_driver_path_deviation_m = maxf(maximum_test_driver_path_deviation_m, path_distance)
	maximum_lateral_error_m = maxf(maximum_lateral_error_m, path_distance)
	maximum_chainage = maxf(maximum_chainage, float(nearest.chainage))
	var record := {
		"event": "TEST_DRIVER_ROUTE_PROJECTION",
		"vector_id": String(vector.id),
		"vector_tick": vector_tick,
		"physics_tick": telemetry.physics_tick,
		"route_id": route_id,
		"chainage_m": float(nearest.chainage),
		"route_lateral_distance_m": path_distance,
		"signed_lateral_error_m": signed_error,
		"horizontal_speed_mps": speed,
		"planned_speed_cap_mps": float(last_v4_control.get("planned_speed_cap_mps", 0.0)),
		"recovery_active": bool(last_v4_control.get("recovery_active", false)),
		"emergency_brake_active": bool(last_v4_control.get("emergency_brake_active", false)),
		"commanded_throttle": float(last_v4_control.get("commanded_throttle", 0.0)),
		"commanded_brake": float(last_v4_control.get("commanded_brake", 0.0)),
		"commanded_steer": float(last_v4_control.get("commanded_steer", 0.0)),
	}
	route_projection_records.append(record)
	print(JSON.stringify(record))


func _observe_v5_route_projection(point: Vector2, speed: float) -> void:
	var controller: Dictionary = vector.get("controller_commands", {})
	if String(controller.get("type", "")) != "ROUTE_FOLLOWER_INPUT_CONTROLLER_V5_INERTIAL_THRUST_VECTOR_CONTAINED":
		return
	var route_id := String(controller.route_id)
	var nearest: Dictionary = _nearest_global(route_id, point)
	var sample: Dictionary = _route_sample(route_id, float(nearest.chainage))
	var tangent: Vector2 = sample.tangent
	var normal: Vector2 = Vector2(-tangent.y, tangent.x)
	var sample_point: Vector2 = sample.point
	var signed_error: float = (point - sample_point).dot(normal)
	var path_distance := float(nearest.distance)
	maximum_test_driver_path_deviation_m = maxf(maximum_test_driver_path_deviation_m, path_distance)
	maximum_lateral_error_m = maxf(maximum_lateral_error_m, path_distance)
	maximum_chainage = maxf(maximum_chainage, float(nearest.chainage))
	var record := {
		"event": "TEST_DRIVER_ROUTE_PROJECTION", "vector_id": String(vector.id), "vector_tick": vector_tick, "physics_tick": telemetry.physics_tick,
		"route_id": route_id, "chainage_m": float(nearest.chainage), "route_lateral_distance_m": path_distance, "signed_lateral_error_m": signed_error,
		"horizontal_speed_mps": speed, "candidate_id": v5_candidate_id,
		"velocity_course_angle_rad": float(last_v5_control.get("velocity_course_angle_rad", 0.0)),
		"desired_route_course_angle_rad": float(last_v5_control.get("desired_route_course_angle_rad", 0.0)),
		"course_error_rad": float(last_v5_control.get("course_error_rad", 0.0)),
		"signed_curvature_per_m": float(last_v5_control.get("signed_curvature_per_m", 0.0)),
		"requested_lateral_accel_mps2": float(last_v5_control.get("requested_lateral_accel_mps2", 0.0)),
		"body_lead_angle_rad": float(last_v5_control.get("body_lead_angle_rad", 0.0)),
		"turning_throttle_floor": float(last_v5_control.get("turning_throttle_floor", 0.0)),
		"commanded_throttle": float(last_v5_control.get("commanded_throttle", 0.0)),
		"commanded_brake": float(last_v5_control.get("commanded_brake", 0.0)),
		"commanded_steer": float(last_v5_control.get("commanded_steer", 0.0)),
		"planned_speed_cap_mps": float(last_v5_control.get("planned_speed_cap_mps", 0.0)),
		"recovery_active": bool(last_v5_control.get("recovery_active", false)),
	}
	route_projection_records.append(record)
	print(JSON.stringify(record))


func _observe_v6_route_projection(point: Vector2, speed: float) -> void:
	var controller: Dictionary = vector.get("controller_commands", {})
	if String(controller.get("type", "")) != "ROUTE_FOLLOWER_INPUT_CONTROLLER_V6_DECEL_CONSTRAINED_THRUST_VECTOR_CONTAINED":
		return
	var route_id := String(controller.route_id); var nearest: Dictionary = _nearest_global(route_id, point); var sample: Dictionary = _route_sample(route_id, float(nearest.chainage))
	var tangent: Vector2 = sample.tangent; var normal := Vector2(-tangent.y, tangent.x); var sample_point: Vector2 = sample.point
	var signed_error := (point - sample_point).dot(normal); var path_distance := float(nearest.distance)
	maximum_test_driver_path_deviation_m = maxf(maximum_test_driver_path_deviation_m, path_distance); maximum_lateral_error_m = maxf(maximum_lateral_error_m, path_distance); maximum_chainage = maxf(maximum_chainage, float(nearest.chainage))
	var observed_delta := speed - float(last_v6_control.get("pre_command_speed_mps", speed))
	var slowdown_active := bool(last_v6_control.get("slowdown_command_active", false))
	var desired_speed := float(last_v6_control.get("desired_speed_mps", speed))
	if slowdown_active and speed >= desired_speed + float(v6_candidate.slowdown_health_speed_excess_min_mps):
		v6_slowdown_window_ticks += 1; v6_slowdown_window_cumulative_speed_change_mps += observed_delta
	else:
		v6_slowdown_window_ticks = 0; v6_slowdown_window_cumulative_speed_change_mps = 0.0
	var slowdown_healthy := true
	if v6_slowdown_window_ticks >= int(v6_candidate.slowdown_health_window_ticks) and v6_slowdown_window_cumulative_speed_change_mps > float(v6_candidate.slowdown_health_max_cumulative_speed_rise_mps) + 0.000001:
		slowdown_healthy = false
		if v6_slowdown_health_violation.is_empty():
			v6_slowdown_health_violation = {"physics_tick": telemetry.physics_tick, "vector_tick": vector_tick, "route_id": route_id, "chainage_m": float(nearest.chainage), "observed_speed_mps": speed, "desired_speed_mps": desired_speed, "window_ticks": v6_slowdown_window_ticks, "cumulative_speed_change_mps": v6_slowdown_window_cumulative_speed_change_mps}
	var record := {
		"event":"TEST_DRIVER_ROUTE_PROJECTION", "vector_id":String(vector.id), "vector_tick":vector_tick, "physics_tick":telemetry.physics_tick, "route_id":route_id, "chainage_m":float(nearest.chainage),
		"route_lateral_distance_m":path_distance, "signed_lateral_error_m":signed_error, "lateral_velocity_mps":float(last_v6_control.get("lateral_velocity_mps",0.0)), "candidate_id":v6_candidate_id, "algorithm_id":"DZP1A_DECEL_CONSTRAINED_THRUST_VECTOR_V1",
		"desired_speed_mps":desired_speed, "observed_speed_mps":speed, "pre_command_speed_mps":float(last_v6_control.get("pre_command_speed_mps",speed)), "predicted_speed_delta_mps":float(last_v6_control.get("predicted_speed_delta_mps",0.0)), "observed_speed_delta_mps":observed_delta,
		"commanded_throttle":float(last_v6_control.get("commanded_throttle",0.0)), "commanded_brake":float(last_v6_control.get("commanded_brake",0.0)), "commanded_steer":float(last_v6_control.get("commanded_steer",0.0)), "recovery_phase":String(last_v6_control.get("recovery_phase","")),
		"velocity_course_angle_rad":float(last_v6_control.get("velocity_course_angle_rad",0.0)), "desired_route_course_angle_rad":float(last_v6_control.get("desired_route_course_angle_rad",0.0)), "course_error_rad":float(last_v6_control.get("course_error_rad",0.0)), "signed_curvature_per_m":float(last_v6_control.get("signed_curvature_per_m",0.0)),
		"requested_lateral_accel_mps2":float(last_v6_control.get("requested_lateral_accel_mps2",0.0)), "body_lead_angle_rad":float(last_v6_control.get("body_lead_angle_rad",0.0)), "predicted_lateral_error_m":float(last_v6_control.get("predicted_lateral_error_m",0.0)),
		"slowdown_command_active":slowdown_active, "required_net_decel_mps2":float(last_v6_control.get("required_net_decel_mps2",0.0)), "maximum_authorized_longitudinal_thrust_mps2":float(last_v6_control.get("maximum_authorized_longitudinal_thrust_mps2",0.0)),
		"actual_body_forward_longitudinal_component":float(last_v6_control.get("actual_body_forward_longitudinal_component",0.0)), "predicted_longitudinal_accel_mps2":float(last_v6_control.get("predicted_longitudinal_accel_mps2",0.0)),
		"slowdown_window_tick_count":v6_slowdown_window_ticks, "slowdown_window_cumulative_speed_change_mps":v6_slowdown_window_cumulative_speed_change_mps, "slowdown_healthy":slowdown_healthy,
		"planned_speed_cap_mps":float(last_v6_control.get("planned_speed_cap_mps",0.0)), "recovery_active":bool(last_v6_control.get("recovery_active",false)),
	}
	route_projection_records.append(record); print(JSON.stringify(record))


func _observe_v7_route_projection(point: Vector2, speed: float) -> void:
	var controller: Dictionary = vector.get("controller_commands", {})
	if String(controller.get("type", "")) != "ROUTE_FOLLOWER_INPUT_CONTROLLER_V7_PHASE_SEPARATED_BRAKE_CAPTURE_CONTAINED":
		return
	var route_id := String(controller.route_id)
	var nearest: Dictionary = _nearest_global(route_id, point)
	var sample: Dictionary = _route_sample(route_id, float(nearest.chainage))
	var tangent: Vector2 = sample.tangent
	var normal := Vector2(-tangent.y, tangent.x)
	var sample_point: Vector2 = sample.point
	var signed_error: float = (point - sample_point).dot(normal)
	var path_distance := float(nearest.distance)
	maximum_test_driver_path_deviation_m = maxf(maximum_test_driver_path_deviation_m, path_distance)
	maximum_lateral_error_m = maxf(maximum_lateral_error_m, path_distance)
	maximum_chainage = maxf(maximum_chainage, float(nearest.chainage))
	var observed_delta := speed - float(last_v7_control.get("pre_command_speed_mps", speed))
	var brake_commit := String(last_v7_control.get("recovery_phase", "")) == "BRAKE_COMMIT"
	var desired_speed := float(last_v7_control.get("desired_speed_mps", speed))
	if brake_commit and speed >= desired_speed + float(v7_candidate.slowdown_health_speed_excess_min_mps):
		v7_brake_health_window_ticks += 1
		v7_brake_health_cumulative_speed_change_mps += observed_delta
	else:
		v7_brake_health_window_ticks = 0
		v7_brake_health_cumulative_speed_change_mps = 0.0
	var slowdown_healthy := true
	if v7_brake_health_window_ticks >= int(v7_candidate.slowdown_health_window_ticks) and v7_brake_health_cumulative_speed_change_mps > float(v7_candidate.slowdown_health_max_cumulative_speed_rise_mps) + 0.000001:
		slowdown_healthy = false
		if v7_brake_health_violation.is_empty():
			v7_brake_health_violation = {"physics_tick": telemetry.physics_tick, "vector_tick": vector_tick, "route_id": route_id, "chainage_m": float(nearest.chainage), "observed_speed_mps": speed, "desired_speed_mps": desired_speed, "window_ticks": v7_brake_health_window_ticks, "cumulative_speed_change_mps": v7_brake_health_cumulative_speed_change_mps}
	var record := {
		"event": "TEST_DRIVER_ROUTE_PROJECTION", "vector_id": String(vector.id), "vector_tick": vector_tick, "physics_tick": telemetry.physics_tick, "route_id": route_id, "chainage_m": float(nearest.chainage),
		"route_lateral_distance_m": path_distance, "signed_lateral_error_m": signed_error, "lateral_velocity_mps": float(last_v7_control.get("lateral_velocity_mps", 0.0)), "candidate_id": v7_candidate_id, "algorithm_id": "DZP1A_PHASE_SEPARATED_BRAKE_CAPTURE_V1",
		"desired_speed_mps": desired_speed, "observed_speed_mps": speed, "pre_command_speed_mps": float(last_v7_control.get("pre_command_speed_mps", speed)), "predicted_speed_delta_mps": float(last_v7_control.get("predicted_speed_delta_mps", 0.0)), "observed_speed_delta_mps": observed_delta,
		"commanded_throttle": float(last_v7_control.get("commanded_throttle", 0.0)), "commanded_brake": float(last_v7_control.get("commanded_brake", 0.0)), "commanded_steer": float(last_v7_control.get("commanded_steer", 0.0)), "recovery_phase": String(last_v7_control.get("recovery_phase", "")), "phase_ticks": int(last_v7_control.get("phase_ticks", 0)),
		"velocity_course_angle_rad": float(last_v7_control.get("velocity_course_angle_rad", 0.0)), "desired_route_course_angle_rad": float(last_v7_control.get("desired_route_course_angle_rad", 0.0)), "course_error_rad": float(last_v7_control.get("course_error_rad", 0.0)), "signed_curvature_per_m": float(last_v7_control.get("signed_curvature_per_m", 0.0)),
		"requested_lateral_accel_mps2": float(last_v7_control.get("requested_lateral_accel_mps2", 0.0)), "body_lead_angle_rad": float(last_v7_control.get("body_lead_angle_rad", 0.0)), "predicted_lateral_error_m": float(last_v7_control.get("predicted_lateral_error_m", 0.0)),
		"capture_active": bool(last_v7_control.get("capture_active", false)), "planned_speed_cap_mps": float(last_v7_control.get("planned_speed_cap_mps", 0.0)),
		"turn_plan_preview_m": float(last_v7_control.get("turn_plan_preview_m", 0.0)), "plan_lateral_accel_budget_mps2": float(last_v7_control.get("plan_lateral_accel_budget_mps2", 0.0)), "brake_release_hysteresis_mps": float(last_v7_control.get("brake_release_hysteresis_mps", 0.0)),
		"slowdown_window_tick_count": v7_brake_health_window_ticks, "slowdown_window_cumulative_speed_change_mps": v7_brake_health_cumulative_speed_change_mps, "slowdown_healthy": slowdown_healthy,
	}
	route_projection_records.append(record)
	print(JSON.stringify(record))


func _observe_human_route_projection(point: Vector2, speed: float) -> void:
	var controller: Dictionary = vector.get("controller_commands", {})
	if String(controller.get("type", "")) != HUMAN_REPLAY_CONTROLLER:
		return
	var route_id := String(controller.get("route_id", ""))
	var nearest: Dictionary = _nearest_global(route_id, point)
	var sample: Dictionary = _route_sample(route_id, float(nearest.chainage))
	var tangent: Vector2 = sample.tangent
	var normal := Vector2(-tangent.y, tangent.x)
	var sample_point: Vector2 = sample.point
	var signed_error := (point - sample_point).dot(normal)
	var path_distance := float(nearest.distance)
	maximum_test_driver_path_deviation_m = maxf(maximum_test_driver_path_deviation_m, path_distance)
	maximum_lateral_error_m = maxf(maximum_lateral_error_m, path_distance)
	maximum_chainage = maxf(maximum_chainage, float(nearest.chainage))
	var record := {
		"event": "TEST_DRIVER_ROUTE_PROJECTION",
		"vector_id": String(vector.id),
		"vector_tick": vector_tick,
		"physics_tick": telemetry.physics_tick,
		"route_id": route_id,
		"chainage_m": float(nearest.chainage),
		"route_lateral_distance_m": path_distance,
		"signed_lateral_error_m": signed_error,
		"horizontal_speed_mps": speed,
		"commanded_throttle": float(last_human_control.get("commanded_throttle", 0.0)),
		"commanded_brake": float(last_human_control.get("commanded_brake", 0.0)),
		"commanded_steer": float(last_human_control.get("commanded_steer", 0.0)),
		"algorithm_id": "DZP1A_NORMALIZED_HUMAN_INPUT_REPLAY_V1",
		"trace_id": String(human_input_trace.get("trace_id", "")),
	}
	route_projection_records.append(record)
	print(JSON.stringify(record))


func _route_projection_is_contiguous() -> bool:
	for index in route_projection_records.size():
		if int(route_projection_records[index].vector_tick) != index:
			return false
		if index > 0 and int(route_projection_records[index].physics_tick) != int(route_projection_records[index - 1].physics_tick) + 1:
			return false
	return true


func _fast_route_projection_summary() -> Dictionary:
	if route_projection_records.is_empty():
		return {"sample_count": 0, "contiguous": true, "maximum_route_lateral_distance_m": 0.0, "evidence_source": "none"}
	var controller_type := String(vector.get("controller_commands", {}).get("type", ""))
	return {
		"sample_count": route_projection_records.size(), "contiguous": _route_projection_is_contiguous(),
		"maximum_route_lateral_distance_m": maximum_test_driver_path_deviation_m,
		"first_sample": route_projection_records[0], "last_sample": route_projection_records[-1],
		"evidence_source": "per-tick global baked-route projection",
		"algorithm_id": "DZP1A_NORMALIZED_HUMAN_INPUT_REPLAY_V1" if controller_type == HUMAN_REPLAY_CONTROLLER else (String(v7_candidate.get("algorithm_id", "DZP1A_PHASE_SEPARATED_BRAKE_CAPTURE_V1")) if controller_type == "ROUTE_FOLLOWER_INPUT_CONTROLLER_V7_PHASE_SEPARATED_BRAKE_CAPTURE_CONTAINED" else (String(v6_candidate.get("algorithm_id", "DZP1A_DECEL_CONSTRAINED_THRUST_VECTOR_V1")) if controller_type == "ROUTE_FOLLOWER_INPUT_CONTROLLER_V6_DECEL_CONSTRAINED_THRUST_VECTOR_CONTAINED" else (String(v5_candidate.get("algorithm_id", "DZP1A_FORWARD_CURVATURE_BACKWARD_BRAKE_V1")) if controller_type == "ROUTE_FOLLOWER_INPUT_CONTROLLER_V5_INERTIAL_THRUST_VECTOR_CONTAINED" else "DZP1A_FORWARD_CURVATURE_BACKWARD_BRAKE_V1"))),
		"candidate_id": v7_candidate_id if not v7_candidate_id.is_empty() else (v6_candidate_id if not v6_candidate_id.is_empty() else (v5_candidate_id if not v5_candidate_id.is_empty() else null)),
	}


func _v4_projection_is_contiguous() -> bool:
	return _route_projection_is_contiguous()


func _v4_projection_summary() -> Dictionary:
	return _fast_route_projection_summary()


func _first_unauthorized_hard_collision() -> Dictionary:
	var hard_ids: Array = fixture.global_rules.collision_counting.hard_geometry_ids
	for event in observed:
		if String(event.get("event", "")) != "COLLISION_SAMPLE":
			continue
		var tick := int(event.get("physics_tick", -1))
		if tick < collision_window_start_tick:
			continue
		if String(event.get("source_geometry_id", "")) in hard_ids:
			return event.duplicate(true)
	return {}


func _observe_test_driver_liveness(point: Vector2, speed: float) -> void:
	if not vector.has("test_driver_liveness"):
		return
	var contract: Dictionary = vector.test_driver_liveness
	var path: Array = contract.get("path_polyline_xz_m", [])
	var path_distance := _distance_to_polyline(point, path)
	maximum_liveness_path_deviation_m = maxf(maximum_liveness_path_deviation_m, path_distance)
	maximum_test_driver_path_deviation_m = maxf(maximum_test_driver_path_deviation_m, path_distance)
	var window_id := String(contract.get("required_window_id", ""))
	var window_distance := INF
	if not window_id.is_empty() and crossing_states.has(window_id):
		window_distance = _distance_to_finite_window(point, crossing_states[window_id].spec)
		minimum_required_window_distance_m = minf(minimum_required_window_distance_m, window_distance)
	var minimum_powered_speed := float(contract.get("minimum_powered_approach_horizontal_speed_mps", 5.0))
	var throttle_qualifies := active_controller_throttle > 0.0 if bool(contract.get("powered_approach_requires_positive_throttle", true)) else true
	if window_distance < INF and throttle_qualifies and speed + 0.000001 >= minimum_powered_speed:
		if powered_required_window_closest_sample.is_empty() or window_distance < float(powered_required_window_closest_sample.distance_m):
			powered_required_window_closest_sample = {"vector_tick": vector_tick, "physics_tick": telemetry.physics_tick, "craft_center_xz_m": [point.x, point.y], "distance_m": window_distance, "horizontal_speed_mps": speed, "commanded_throttle": active_controller_throttle, "required_window_id": window_id}
	var record := {"event": "TEST_DRIVER_LIVENESS", "vector_id": String(vector.id), "vector_tick": vector_tick, "physics_tick": telemetry.physics_tick, "craft_center_xz_m": [point.x, point.y], "horizontal_speed_mps": speed, "commanded_throttle": active_controller_throttle, "closest_path_distance_m": path_distance, "closest_required_window_distance_m": window_distance if window_distance < INF else null}
	liveness_records.append(record)
	print(JSON.stringify(record))


func _distance_to_polyline(point: Vector2, raw: Array) -> float:
	if raw.size() < 2:
		return 0.0
	var best := INF
	for index in raw.size() - 1:
		var a := P1AWorldData.xz(raw[index])
		var b := P1AWorldData.xz(raw[index + 1])
		var segment := b - a
		var t := clampf((point - a).dot(segment) / segment.length_squared(), 0.0, 1.0) if segment.length_squared() > 0.0 else 0.0
		best = minf(best, point.distance_to(a + segment * t))
	return best


func _distance_to_finite_window(point: Vector2, spec: Dictionary) -> float:
	var origin := P1AWorldData.xz(spec.point_xz_m)
	var tangent := P1AWorldData.xz(spec.unit_tangent_xz).normalized()
	var a := origin + tangent * float(spec.minimum_tangent_offset_m)
	var b := origin + tangent * float(spec.maximum_tangent_offset_m)
	var segment := b - a
	var t := clampf((point - a).dot(segment) / segment.length_squared(), 0.0, 1.0) if segment.length_squared() > 0.0 else 0.0
	return point.distance_to(a + segment * t)


func _liveness_is_contiguous() -> bool:
	for index in liveness_records.size():
		if int(liveness_records[index].vector_tick) != index:
			return false
		if index > 0 and int(liveness_records[index].physics_tick) != int(liveness_records[index - 1].physics_tick) + 1:
			return false
	return true


func _positive_throttle_fraction() -> float:
	if liveness_records.is_empty():
		return 0.0
	var count := 0
	for record in liveness_records:
		if float(record.commanded_throttle) > 0.0:
			count += 1
	return float(count) / float(liveness_records.size())


func _liveness_summary() -> Dictionary:
	return {"sample_count": liveness_records.size(), "contiguous": _liveness_is_contiguous(), "positive_throttle_fraction": _positive_throttle_fraction(), "maximum_path_deviation_m": maximum_liveness_path_deviation_m, "minimum_required_window_distance_m": minimum_required_window_distance_m if minimum_required_window_distance_m < INF else null, "powered_required_window_closest_approach_sample": powered_required_window_closest_sample if not powered_required_window_closest_sample.is_empty() else null}


func _first_event_physics_tick(event_name: String) -> int:
	var first := 2147483647
	for event in observed:
		if String(event.get("event", "")) == event_name:
			first = mini(first, int(event.get("physics_tick", 2147483647)))
	return -1 if first == 2147483647 else first


func _ordered_event_values(event_name: String, field_name: String) -> Array:
	var actual := []
	for event in observed:
		if String(event.get("event", "")) == event_name:
			var value = event.get(field_name, null)
			if actual.is_empty() or actual[-1] != value:
				actual.append(value)
	return actual


func _movement_tuning_digest() -> String:
	var contract: Dictionary = fixture.global_rules.movement_tuning_digest
	if String(contract.algorithm_id) != TUNING_DIGEST_ALGORITHM_ID:
		return ""
	var bytes := PackedByteArray()
	bytes.append_array(String(contract.prefix_bytes_utf8_then_nul).to_utf8_buffer())
	bytes.append(0)
	for field_value in contract.field_order:
		var field_name := String(field_value)
		bytes.append_array(field_name.to_utf8_buffer())
		bytes.append(0)
		var stream := StreamPeerBuffer.new()
		stream.big_endian = true
		stream.put_double(float(craft.tuning.get(field_name)))
		bytes.append_array(stream.data_array)
	var context := HashingContext.new()
	if context.start(HashingContext.HASH_SHA256) != OK:
		return ""
	context.update(bytes)
	return context.finish().hex_encode()


func _custom_input_actions() -> Array[String]:
	var result: Array[String] = []
	for value in InputMap.get_actions():
		var action := String(value)
		if not action.begins_with("ui_"):
			result.append(action)
	result.sort()
	return result


func _validate_vector_contract() -> Array[String]:
	var failures: Array[String] = []
	var registry: Dictionary = fixture.global_rules.threshold_evaluator_registry
	for key_value in vector.get("thresholds", {}).keys():
		var key := String(key_value)
		if not registry.has(key) or not (key in IMPLEMENTED_THRESHOLD_KEYS):
			failures.append("threshold lacks implemented evaluator: %s" % key)
	for command_value in vector.get("tick_commands", []):
		var command_name := String(command_value.command)
		if not (command_name in IMPLEMENTED_COMMANDS):
			failures.append("unhandled fixture command: %s" % command_name)
	var controller: Dictionary = vector.get("controller_commands", {})
	var type := String(controller.get("type", ""))
	if type in ["ROUTE_FOLLOWER_INPUT_CONTROLLER_V2", "ROUTE_FOLLOWER_INPUT_CONTROLLER_V3_FAST_CONTAINED", "ROUTE_FOLLOWER_INPUT_CONTROLLER_V4_FORWARD_BRAKING_CONTAINED", "ROUTE_FOLLOWER_INPUT_CONTROLLER_V5_INERTIAL_THRUST_VECTOR_CONTAINED", "ROUTE_FOLLOWER_INPUT_CONTROLLER_V6_DECEL_CONSTRAINED_THRUST_VECTOR_CONTAINED", "ROUTE_FOLLOWER_INPUT_CONTROLLER_V7_PHASE_SEPARATED_BRAKE_CAPTURE_CONTAINED"]:
		for required_field in ["type", "route_id", "direction"]:
			if not controller.has(required_field):
				failures.append("route follower missing %s" % required_field)
		var route_id := String(controller.get("route_id", ""))
		if route_id.is_empty() or not route_cache.has(route_id):
			failures.append("empty or unknown route-follower route_id: %s" % route_id)
		if String(vector.id) == "RT_R0_SURFACE_NEUTRALITY" and not controller.has("terminate_chainage_m"):
			failures.append("R0 controller missing terminate_chainage_m")

		if type == "ROUTE_FOLLOWER_INPUT_CONTROLLER_V5_INERTIAL_THRUST_VECTOR_CONTAINED":
			for field in ["candidate_registry_path", "candidate_id_source", "lateral_soft_limit_m", "lateral_hard_limit_m", "route_projection_evidence_every_tick", "fail_fast_on_first_unauthorized_hard_collision", "fail_fast_on_first_hard_lateral_limit_violation", "input_actions_only", "position_or_velocity_writes"]:
				if not controller.has(field):
					failures.append("V5 fast-route controller missing %s" % field)
			if not (String(vector.id) in ["RT_ROUTE_A1", "RT_ROUTE_A2", "RT_ROUTE_X0"]):
				failures.append("V5 fast-route controller is authorized only for A1/A2/X0")
			if v5_candidate.is_empty() or String(v5_candidate.get("algorithm_id", "")) != "DZP1A_INERTIAL_THRUST_VECTOR_V1":
				failures.append("V5 preregistered candidate is absent or invalid")
			if not bool(controller.get("route_projection_evidence_every_tick", false)):
				failures.append("V5 route projection must be every-tick")
			if not bool(controller.get("fail_fast_on_first_unauthorized_hard_collision", false)) or not bool(controller.get("fail_fast_on_first_hard_lateral_limit_violation", false)):
				failures.append("V5 fail-fast contract mismatch")
			if controller.get("input_actions_only", []) != ["throttle", "brake", "steer_left", "steer_right"] or String(controller.get("position_or_velocity_writes", "")) != "FORBIDDEN":
				failures.append("V5 input-only contract mismatch")
		if type == "ROUTE_FOLLOWER_INPUT_CONTROLLER_V6_DECEL_CONSTRAINED_THRUST_VECTOR_CONTAINED":
			for field in ["candidate_registry_path", "candidate_id_source", "lateral_soft_limit_m", "lateral_hard_limit_m", "route_projection_evidence_every_tick", "fail_fast_on_first_unauthorized_hard_collision", "fail_fast_on_first_hard_lateral_limit_violation", "input_actions_only", "position_or_velocity_writes"]:
				if not controller.has(field):
					failures.append("V6 fast-route controller missing %s" % field)
			if not (String(vector.id) in ["RT_ROUTE_A1", "RT_ROUTE_A2", "RT_ROUTE_X0"]):
				failures.append("V6 fast-route controller is authorized only for A1/A2/X0")
			if v6_candidate.is_empty() or String(v6_candidate.get("algorithm_id", "")) != "DZP1A_DECEL_CONSTRAINED_THRUST_VECTOR_V1":
				failures.append("V6 preregistered candidate is absent or invalid")
			if not bool(controller.get("route_projection_evidence_every_tick", false)):
				failures.append("V6 route projection must be every-tick")
			if not bool(controller.get("fail_fast_on_first_unauthorized_hard_collision", false)) or not bool(controller.get("fail_fast_on_first_hard_lateral_limit_violation", false)):
				failures.append("V6 fail-fast contract mismatch")
			if controller.get("input_actions_only", []) != ["throttle", "brake", "steer_left", "steer_right"] or String(controller.get("position_or_velocity_writes", "")) != "FORBIDDEN":
				failures.append("V6 input-only contract mismatch")
		if type == "ROUTE_FOLLOWER_INPUT_CONTROLLER_V7_PHASE_SEPARATED_BRAKE_CAPTURE_CONTAINED":
			for field in ["candidate_registry_path", "candidate_id_source", "lateral_soft_limit_m", "lateral_hard_limit_m", "route_projection_evidence_every_tick", "fail_fast_on_first_unauthorized_hard_collision", "fail_fast_on_first_hard_lateral_limit_violation", "input_actions_only", "position_or_velocity_writes"]:
				if not controller.has(field):
					failures.append("V7 fast-route controller missing %s" % field)
			if not (String(vector.id) in ["RT_ROUTE_A1", "RT_ROUTE_A2", "RT_ROUTE_X0"]):
				failures.append("V7 fast-route controller is authorized only for A1/A2/X0")
			if v7_candidate.is_empty() or String(v7_candidate.get("algorithm_id", "")) != "DZP1A_PHASE_SEPARATED_BRAKE_CAPTURE_V1":
				failures.append("V7 preregistered candidate is absent or invalid")
			if bool(v7_candidate.get("simultaneous_throttle_and_brake", true)) or String(v7_candidate.get("position_or_velocity_writes", "")) != "FORBIDDEN":
				failures.append("V7 phase-separated input-only contract mismatch")
			if not bool(controller.get("route_projection_evidence_every_tick", false)):
				failures.append("V7 route projection must be every-tick")
			if not bool(controller.get("fail_fast_on_first_unauthorized_hard_collision", false)) or not bool(controller.get("fail_fast_on_first_hard_lateral_limit_violation", false)):
				failures.append("V7 fail-fast contract mismatch")
			if controller.get("input_actions_only", []) != ["throttle", "brake", "steer_left", "steer_right"] or String(controller.get("position_or_velocity_writes", "")) != "FORBIDDEN":
				failures.append("V7 input-only controller fixture mismatch")
		if type == "ROUTE_FOLLOWER_INPUT_CONTROLLER_V4_FORWARD_BRAKING_CONTAINED":
			var v4_fields := ["curve_plan_algorithm_id","forward_curvature_window_m","drive_speed_cap_mps","drive_yaw_rate_rad_s","turn_rate_margin","braking_envelope_decel_mps2","endpoint_margin_m","endpoint_speed_cap_mps","plan_query_lead_time_s","plan_query_lead_min_m","plan_query_lead_max_m","steering_lookahead_min_m","steering_lookahead_max_m","steering_lookahead_speed_gain_s","lateral_soft_limit_m","lateral_hard_limit_m","recovery_speed_cap_mps","recovery_prediction_horizon_s","recovery_emergency_margin_m","route_projection_evidence_every_tick","fail_fast_on_first_unauthorized_hard_collision"]
			for field in v4_fields:
				if not controller.has(field):
					failures.append("V4 fast-route controller missing %s" % field)
			if not (String(vector.id) in ["RT_ROUTE_A1", "RT_ROUTE_A2", "RT_ROUTE_X0"]):
				failures.append("V4 fast-route controller is authorized only for A1/A2/X0")
			if String(controller.get("curve_plan_algorithm_id", "")) != "DZP1A_FORWARD_CURVATURE_BACKWARD_BRAKE_V1":
				failures.append("V4 curve-plan algorithm ID mismatch")
			if not bool(controller.get("route_projection_evidence_every_tick", false)):
				failures.append("V4 route projection must be every-tick")
			if not bool(controller.get("fail_fast_on_first_unauthorized_hard_collision", false)):
				failures.append("V4 first unauthorized hard collision must fail fast")
	elif type == HUMAN_REPLAY_CONTROLLER:
		for field in ["type", "algorithm_id", "route_id", "direction", "selected_trace_manifest_flag", "trace_route_id_must_match", "input_actions_only", "prohibited_actions", "position_or_velocity_writes", "route_projection_evidence_every_tick", "fail_fast_on_first_unauthorized_hard_collision", "fail_fast_on_first_hard_lateral_limit_violation", "lateral_soft_limit_m", "lateral_hard_limit_m", "input_trace_schema", "selected_trace_manifest_schema"]:
			if not controller.has(field):
				failures.append("normalized-input replay controller missing %s" % field)
		if not (String(vector.id) in ["RT_ROUTE_A1", "RT_ROUTE_A2", "RT_ROUTE_X0"]):
			failures.append("normalized-input replay is authorized only for A1/A2/X0")
		if String(controller.get("algorithm_id", "")) != "DZP1A_NORMALIZED_HUMAN_INPUT_REPLAY_V1":
			failures.append("normalized-input replay algorithm ID mismatch")
		if controller.get("input_actions_only", []) != ["throttle", "brake", "steer_left", "steer_right", "transform"] or String(controller.get("position_or_velocity_writes", "")) != "FORBIDDEN":
			failures.append("normalized-input replay input-only contract mismatch")
		if String(human_input_trace.get("schema", "")) != "district_zero.p1a.human_input_trace.v1" or String(human_input_trace.get("route_id", "")) != String(controller.get("route_id", "")):
			failures.append("normalized human input trace schema/route mismatch")
		if human_input_records.is_empty():
			failures.append("normalized human input trace has no records")
		else:
			for index in human_input_records.size():
				var record: Dictionary = human_input_records[index]
				if int(record.get("vector_tick", -1)) != index or int(record.get("physics_tick", -1)) != index + 1:
					failures.append("normalized human input trace is not contiguous at index %d" % index)
					break
				if not bool(record.get("transform_pressed", false)) or bool(record.get("hop_pressed", true)):
					failures.append("normalized human input trace contains ineligible transform/Hop state")
					break
	elif type == "POWERED_WAYPOINT_INPUT_CONTROLLER":
		for field in ["waypoints_xz_m", "waypoint_radius_m", "steer_gain", "throttle"]:
			if not controller.has(field): failures.append("powered-waypoint controller missing %s" % field)
		if controller.get("waypoints_xz_m", []).size() < 2: failures.append("powered-waypoint controller requires at least two waypoints")
	elif type == "MULTI_ROUTE_FOLLOWER_INPUT_CONTROLLER":
		for required_field in ["type", "path", "lookahead_m", "throttle_command"]:
			if not controller.has(required_field):
				failures.append("multi-route controller missing %s" % required_field)
		if not controller.has("path") or controller.path.is_empty():
			failures.append("multi-route controller path missing")
		else:
			for segment_value in controller.path:
				var segment: Dictionary = segment_value
				if not segment.has("route") or not segment.has("direction") or not segment.has("start_chainage_m") or not segment.has("end_chainage_m"):
					failures.append("multi-route segment missing required field")
				elif not route_cache.has(String(segment.route)):
					failures.append("multi-route segment has unknown route %s" % segment.route)
	elif type == "POINT_TARGET_INPUT_CONTROLLER":
		for field in ["target_xz_m", "steer_gain", "throttle"]:
			if not controller.has(field):
				failures.append("point-target controller missing %s" % field)
	elif type == "SUPPORTED_HOP_BRACKET_CONTROLLER":
		for field in ["support_readiness", "runup", "timing_model", "timing_offsets_m", "bar_overlap_clearance"]:
			if not controller.has(field):
				failures.append("supported-Hop bracket controller missing %s" % field)
		if hop_timing_offset_m == INF:
			failures.append("supported-Hop bracket requires --hop-offset-m or a promoted selected_timing_offset_m")
		else:
			var allowed := false
			for value in controller.get("timing_offsets_m", []):
				if absf(float(value) - hop_timing_offset_m) <= 0.0000001:
					allowed = true
			if not allowed:
				failures.append("Hop timing offset is outside the preregistered scan")
	elif not type.is_empty():
		failures.append("unknown controller type %s" % type)
	var termination: Dictionary = vector.get("termination", {})
	if String(termination.get("type", "")) == "FIRST_VALID_HOP_CLEARANCE":
		for field in ["window_id", "timeout_tick", "completion_tick_inclusive", "timeout_is_failure", "requires"]:
			if not termination.has(field):
				failures.append("event termination missing %s" % field)
		if termination.has("tick"):
			failures.append("event-based Q1 termination must not contain a fixed success tick")
		if String(vector.id) != "RT_HOP_SUCCESS":
			failures.append("FIRST_VALID_HOP_CLEARANCE is authorized only for RT_HOP_SUCCESS")
		if String(termination.get("window_id", "")) != String(vector.get("crossing_plane", {}).get("id", "")):
			failures.append("Q1 termination window does not match the active bounded crossing plane")
	return failures


func _event_matches(event: Dictionary, expected: Dictionary) -> bool:
	for key in expected:
		if key in ["minimum_count", "allowed"]: continue
		if event.get(key, null) != expected[key]: return false
	return true


func _event_count(name: String) -> int:
	var count := 0
	for event in observed:
		if String(event.get("event", "")) == name: count += 1
	return count


func _reset_count(reason: String) -> int:
	var count := 0
	for event in observed:
		if String(event.get("event", "")) == "RESET" and String(event.get("reason", "")) == reason: count += 1
	return count


func _collision_count_through(source_id: String, end_tick_inclusive: int) -> int:
	var count := 0
	for event in observed:
		var tick := int(event.get("physics_tick", 0))
		if tick < collision_window_start_tick or tick > end_tick_inclusive:
			continue
		if String(event.get("event", "")) == "COLLISION_SAMPLE" and String(event.get("source_geometry_id", "")) == source_id:
			count += 1
	return count


func _hard_collision_count_through(end_tick_inclusive: int, exclude_hop: bool) -> int:
	var count := 0
	for event in observed:
		if String(event.get("event", "")) != "COLLISION_SAMPLE":
			continue
		var tick := int(event.get("physics_tick", 0))
		if tick < collision_window_start_tick or tick > end_tick_inclusive:
			continue
		if exclude_hop and String(event.get("collision_class", "")) == "HARD_HOP":
			continue
		count += 1
	return count


func _collision_count(source_id: String) -> int:
	var count := 0
	for event in observed:
		var tick := int(event.get("physics_tick", 0))
		if tick < collision_window_start_tick or tick > collision_window_end_tick: continue
		if String(event.get("event", "")) == "COLLISION_SAMPLE" and String(event.get("source_geometry_id", "")) == source_id: count += 1
	return count


func _hard_collision_count(exclude_hop: bool) -> int:
	var count := 0
	for event in observed:
		if String(event.get("event", "")) != "COLLISION_SAMPLE": continue
		var tick := int(event.get("physics_tick", 0))
		if tick < collision_window_start_tick or tick > collision_window_end_tick: continue
		if exclude_hop and String(event.get("collision_class", "")) == "HARD_HOP": continue
		count += 1
	return count


func _collision_sources() -> Dictionary:
	var result := {}
	for event in observed:
		if String(event.get("event", "")) != "COLLISION_SAMPLE": continue
		var tick := int(event.get("physics_tick", 0))
		if tick < collision_window_start_tick or tick > collision_window_end_tick: continue
		var source_id := String(event.get("source_geometry_id", ""))
		result[source_id] = int(result.get(source_id, 0)) + 1
	return result


func _event_summary(name: String) -> Array:
	var result := []
	for event in observed:
		if String(event.get("event", "")) == name: result.append(event)
	return result


static func _contains_subsequence(actual: Array, expected: Array) -> bool:
	var cursor := 0
	for value in actual:
		if cursor < expected.size() and value == expected[cursor]: cursor += 1
	return cursor == expected.size()


static func _command_number(value, fallback: float) -> float:
	if typeof(value) == TYPE_FLOAT or typeof(value) == TYPE_INT: return float(value)
	return fallback


func _seal_terminal_evidence() -> void:
	_release_actions()
	if craft != null:
		craft.set_physics_process(false)
		craft.set_process(false)
	if telemetry != null:
		telemetry.set_physics_process(false)
		telemetry.set_process(false)
		if telemetry.event_emitted.is_connected(_on_event):
			telemetry.event_emitted.disconnect(_on_event)
	if gate_root != null:
		gate_root.set_physics_process(false)
		gate_root.set_process(false)
	terminal_evidence_sealed = true


func _release_actions() -> void:
	for action in ACTIONS:
		Input.action_release(action)


func _argument_value(flag: String) -> String:
	var args := OS.get_cmdline_user_args()
	for index in args.size() - 1:
		if args[index] == flag: return args[index + 1]
	return ""
