extends Node
## Diagnostic export only: instantiate the unchanged game and exercise Run APIs.
## Synthetic placement checks the finish predicate, not a driven route completion.
var checks: Dictionary = {}

func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	var game: Node = load("res://scenes/district_zero_run.tscn").instantiate()
	add_child(game)
	await get_tree().process_frame
	await get_tree().process_frame
	var run: Node = game.get_node("RunLayer")
	var gate: Node = game.get_node("DistrictZeroP1A")
	checks["world_loaded"] = gate.data != null and not gate.data.manifest.is_empty()
	checks["run_initialized"] = run._initialized
	await get_tree().create_timer(2.1).timeout
	checks["countdown_reaches_live"] = run.state_name() == "LIVE"
	var craft: CharacterBody3D = gate.craft
	var visual: Node3D = craft.get_node("VisualRoot")
	craft.set_physics_process(false)
	visual.set_form_amount(1.0)
	checks["quarto_drive"] = is_equal_approx(visual.form_amount, 1.0)
	visual.set_form_amount(0.0)
	checks["quarto_spread"] = is_equal_approx(visual.form_amount, 0.0)
	checks["minimap_present"] = gate.map != null and gate.map.visible
	get_tree().paused = true
	var prior_time: float = run.run_time_s
	await get_tree().create_timer(0.3, true).timeout
	checks["pause_stops_run_clock"] = run.run_time_s == prior_time
	var retry := InputEventKey.new()
	retry.physical_keycode = KEY_R
	retry.pressed = true
	get_viewport().push_input(retry)
	checks["paused_retry_owned_by_run"] = run.state_name() == "COUNTDOWN" and run.run_time_s == 0.0
	retry.pressed = false
	get_viewport().push_input(retry)
	get_tree().paused = false
	await get_tree().create_timer(2.1).timeout
	checks["retry_reaches_live"] = run.state_name() == "LIVE"
	craft.set_physics_process(false)
	# Cross the unchanged RLY disc in one synthetic post-move segment.
	var center: Vector2 = run.finish_center_xz
	var radius: float = run.finish_radius_m
	run.previous_craft_xz = center + Vector2(-radius - 2.0, 0.0)
	craft.global_position = Vector3(center.x + radius + 2.0, 10.0, center.y)
	run._tick_live(1.0 / 60.0)
	checks["segment_finish_results"] = run.state_name() == "RESULTS" and not run.last_result.is_empty()
	checks["results_freeze_craft"] = not craft.is_physics_processing()
	await get_tree().create_timer(1.0).timeout
	run.enter_free_roam()
	checks["results_to_free_roam"] = run.state_name() == "FREE_ROAM" and craft.is_physics_processing()
	run.start_attempt()
	checks["retry_clears_metrics"] = run.brrr == 0.0 and run.run_time_s == 0.0 and run.last_result.is_empty()
	var passed := true
	for value in checks.values():
		passed = passed and bool(value)
	var result := {"status": "PASS" if passed else "FAIL", "checks": checks,
		"scope": "Diagnostic export, unchanged game APIs; synthetic finish crossing; no physical gamepad or human route completion claim."}
	print("WEB_SMOKE_RESULT " + JSON.stringify(result))
