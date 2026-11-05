extends SceneTree
## Hem drift envelope with simple, human-style inputs (no feedback steering).
## Each variant: Drive + throttle from the grid; at a brake board, either brake
## (Drive) or flick (release Shift with full left) for a fixed time; then hold
## Drive + full left + throttle until the Hem ends. Reports what happened.
## godot --headless --fixed-fps 60 --path game --script res://tests/rink_hem_sweep.gd -- --result <file.json>

const VARIANTS := [
	# [name, board metres before the Hem, phase, phase seconds]
	["no_scrub_full_lock", 0.0, "none", 0.0],
	["brake_from_100_for_0.8s", 100.0, "brake", 0.8],
	["brake_from_100_for_1.2s", 100.0, "brake", 1.2],
	["brake_from_50_for_1.0s", 50.0, "brake", 1.0],
	["flick_at_50_for_0.25s", 50.0, "flick", 0.25],
	["flick_at_50_for_0.4s", 50.0, "flick", 0.4],
	["flick_at_30_for_0.35s", 30.0, "flick", 0.35],
]

var results := []


func _initialize() -> void:
	_main.call_deferred()


func _release() -> void:
	for a in ["throttle", "brake", "steer_left", "steer_right", "transform", "hop"]:
		Input.action_release(a)


func _main() -> void:
	for v in VARIANTS:
		var game: Node3D = (load("res://rink/rink.tscn") as PackedScene).instantiate()
		root.add_child(game)
		await physics_frame
		game.start_mode("RACE")
		await physics_frame
		results.append(await _run(game, v))
		_release()
		game.queue_free()
		await process_frame
	var out := {"schema": "hush_basin.hem_sweep.v1", "engine": Engine.get_version_info().string, "variants": results}
	var args := OS.get_cmdline_user_args()
	for i in args.size():
		if args[i] == "--result" and i + 1 < args.size():
			FileAccess.open(args[i + 1], FileAccess.WRITE).store_string(JSON.stringify(out, "  ") + "\n")
	for r in results:
		print("HEM_SWEEP ", JSON.stringify(r))
	quit()


func _run(game: Node3D, v: Array) -> Dictionary:
	var craft: CraftController = game.craft
	var hem: Vector2 = game.course.piece_ranges["HEM"]
	var board := hem.x - float(v[1])
	var phase := String(v[2])
	var phase_left := float(v[3])
	var stage := "approach"
	var entry_speed := -1.0
	var min_speed := 99.0
	var hard_hits := 0
	var clear_outer := 99.0
	var hem_start_t := -1.0
	var hem_time := -1.0
	var impacts := craft.impact_count
	var max_slip := 0.0
	for tick in 60 * 40:
		var s: float = game.progress_s
		_release()
		Input.action_press("transform")
		match stage:
			"approach":
				Input.action_press("throttle")
				if s >= board and phase != "none":
					stage = phase
				elif s >= hem.x - 25.0 and phase == "none":
					stage = "drift"
			"brake":
				Input.action_press("brake")
				phase_left -= 1.0 / 60.0
				if phase_left <= 0.0:
					stage = "drift"
			"flick":
				Input.action_release("transform")
				Input.action_press("steer_left")
				phase_left -= 1.0 / 60.0
				if phase_left <= 0.0:
					stage = "drift"
			"drift":
				Input.action_press("steer_left")
				Input.action_press("throttle")
		await physics_frame
		if game.piece == "HEM":
			if hem_start_t < 0.0:
				hem_start_t = game.sim_time
				entry_speed = craft.velocity.length()
			min_speed = minf(min_speed, craft.velocity.length())
			var pose: Dictionary = game.course.pose_at(game.progress_s)
			clear_outer = minf(clear_outer, float(pose.wr) + float(game.lateral))
			var vel := Vector2(craft.velocity.x, craft.velocity.z)
			var head := Vector2(-sin(craft.rotation.y), -cos(craft.rotation.y))
			if vel.length() > 2.0:
				max_slip = maxf(max_slip, absf(rad_to_deg(head.angle_to(vel))))
			if craft.impact_count != impacts:
				impacts = craft.impact_count
				if craft.last_impact_severity >= 0.3:
					hard_hits += 1
		elif hem_start_t >= 0.0:
			hem_time = game.sim_time - hem_start_t
			break
		if game.progress_s > hem.y + 5.0 or game.piece in ["HEMX", "POINTS"]:
			if hem_start_t >= 0.0 and hem_time < 0.0:
				hem_time = game.sim_time - hem_start_t
			break
	return {
		"variant": v[0], "entry_speed": snappedf(entry_speed, 0.1), "min_speed": snappedf(min_speed, 0.1),
		"exit_speed": snappedf(craft.velocity.length(), 0.1), "hard_hits": hard_hits,
		"outer_clearance_m": snappedf(clear_outer - 0.58, 0.1), "max_slip_deg": int(max_slip),
		"hem_seconds": snappedf(hem_time, 0.01), "tip_shown": game.events.any(func(e): return e.event == "tip"),
	}
