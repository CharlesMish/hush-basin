extends Node
## Hem Loop verification. Every scenario loads a fresh rink scene and drives it
## through ordinary input actions (tests/rink_bot.gd). The only non-input
## fixture is the "skipped checkpoint" scenario, which moves the craft across
## the Hem infield to imitate a cut the walls do not physically allow.
##
## Headless: godot --headless --fixed-fps 60 --path game --script res://tests/rink_suite.gd -- --result <file.json>
## Browser: the same node is the main scene of the rink Web smoke export
## (tools/export_rink_web.py --smoke); results go to the console and page title.

const Plans = preload("res://tests/rink_plans.gd")
const Bot = preload("res://tests/rink_bot.gd")
const SCENE := "res://rink/rink.tscn"

var checks: Dictionary = {}
var scenarios: Dictionary = {}
var game: Node3D
var bot
var result_path := ""
var only := ""
var root: Node
var finished := false
var status := "RUNNING"


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	root = get_tree().root
	var args := OS.get_cmdline_user_args()
	for i in args.size():
		if args[i] == "--result" and i + 1 < args.size():
			result_path = args[i + 1]
		if args[i] == "--only" and i + 1 < args.size():
			only = args[i + 1]
	if OS.has_feature("web"):
		var search := String(JavaScriptBridge.eval("window.location.search", true))
		var draw := true
		for entry in search.trim_prefix("?").split("&"):
			if entry.begins_with("only="):
				only = entry.trim_prefix("only=")
			if entry == "draw=0":
				draw = false
		if not draw:
			# Logic-only browser run: same physics ticks, no 3D drawing, catch up fast.
			get_tree().root.disable_3d = true
			Engine.max_physics_steps_per_frame = 240
		JavaScriptBridge.eval("document.title='Hem Loop checks RUNNING'", true)
	_main.call_deferred()


func check(id: String, ok: bool, detail: Variant = null) -> void:
	checks[id] = ok
	if not ok:
		print("CHECK_FAIL ", id, " ", detail)
	if detail != null:
		scenarios.get_or_add("_details", {})[id] = detail


func _fresh(mode: String) -> void:
	if game != null:
		game.queue_free()
		bot.queue_free()
		get_tree().paused = false
		await get_tree().process_frame
	Bot.release()
	game = (load(SCENE) as PackedScene).instantiate()
	root.add_child(game)
	bot = Bot.new()
	root.add_child(bot)
	await get_tree().physics_frame
	bot.setup(game)
	if mode != "ENTRY":
		game.start_mode(mode)
	await get_tree().physics_frame


func _ticks(n: int) -> void:
	for i in n:
		await get_tree().physics_frame


func _until(cond: Callable, max_ticks: int) -> bool:
	for i in max_ticks:
		if cond.call():
			return true
		await get_tree().physics_frame
	return cond.call()


## Synthetic events are delivered once per rendered frame (in the browser
## several physics ticks can run per frame), so wait for frames, not ticks.
func _delivered() -> void:
	await get_tree().process_frame
	await get_tree().process_frame
	await get_tree().physics_frame


func _press(action: String) -> void:
	var e := InputEventAction.new()
	e.action = action
	e.pressed = true
	Input.parse_input_event(e)
	await _delivered()
	var r := InputEventAction.new()
	r.action = action
	r.pressed = false
	Input.parse_input_event(r)
	await _delivered()


func _key(code: Key) -> void:
	var e := InputEventKey.new()
	e.physical_keycode = code
	e.keycode = code
	e.pressed = true
	Input.parse_input_event(e)
	await _delivered()
	var r := e.duplicate()
	r.pressed = false
	Input.parse_input_event(r)
	await _delivered()


func _main() -> void:
	var started := Time.get_ticks_msec()
	var list := ["entry", "consecutive_laps", "doubling_back", "skipped_checkpoint", "retry", "story_hit", "story_miss_then_hit", "story_scuff", "lines"]
	var chosen := only.split(",", false)
	for name in list:
		if not chosen.is_empty() and not chosen.has(name):
			continue
		print("SCENARIO ", name)
		await call("_scenario_" + name)
		Bot.release()
	var failed := checks.keys().filter(func(k): return not checks[k])
	var out := {
		"schema": "hush_basin.hem_loop_suite.v1",
		"engine": Engine.get_version_info().string,
		"status": "PASS" if failed.is_empty() and not checks.is_empty() else "FAIL",
		"check_count": checks.size(), "failed": failed, "checks": checks,
		"scenarios": scenarios, "wall_ms": Time.get_ticks_msec() - started,
	}
	if result_path != "":
		var f := FileAccess.open(result_path, FileAccess.WRITE)
		f.store_string(JSON.stringify(out, "  ") + "\n")
	status = out.status
	finished = true
	print("RINK_SUITE ", out.status, " checks=", checks.size(), " failed=", failed)
	print("RINK_SUITE_JSON ", JSON.stringify({"status": out.status, "check_count": out.check_count, "failed": failed, "engine": out.engine, "scenarios": scenarios}))
	if OS.has_feature("web"):
		JavaScriptBridge.eval("document.title='Hem Loop checks %s'" % out.status, true)
	else:
		get_tree().quit(0 if out.status == "PASS" else 1)


# --- scenarios ------------------------------------------------------------------

func _scenario_entry() -> void:
	await _fresh("ENTRY")
	check("entry.card_visible_at_launch", game.hud.entry.visible and game.mode == "ENTRY")
	check("entry.story_props_hidden", not game.story.tess.visible and not game.story.crew.visible)
	Input.action_press("throttle")
	await _ticks(3)
	check("entry.throttle_starts_time_trial", game.mode == "RACE" and not game.hud.entry.visible, game.mode)
	await _ticks(30)
	Input.action_release("throttle")
	check("entry.craft_moving_within_half_second", game.craft.velocity.length() > 4.0, game.craft.velocity.length())
	await _press("pause")
	check("entry.pause_toggles", get_tree().paused)
	await _key(KEY_C)
	await _ticks(2)
	check("entry.pause_C_starts_crew_run", game.mode == "CREW" and not get_tree().paused and game.story.state == "WAITING")
	check("entry.crew_run_shows_tess_and_crew", game.story.tess.visible and game.story.held_jacket.visible and game.story.crew.visible)
	await _press("pause")
	await _key(KEY_T)
	await _ticks(2)
	check("entry.pause_T_returns_to_time_trial", game.mode == "RACE" and game.story.state == "OFF" and not game.story.tess.visible)
	await _fresh("ENTRY")
	await _key(KEY_C)
	await _ticks(2)
	check("entry.C_on_card_starts_crew_run", game.mode == "CREW" and game.story.state == "WAITING")
	scenarios["entry"] = {"ok": true}


func _laps(n: int, max_ticks: int = 60 * 60 * 4) -> bool:
	return await _until(func(): return game.timing.laps.size() >= n, max_ticks)


func _scenario_consecutive_laps() -> void:
	await _fresh("RACE")
	bot.set_plan(Plans.FLICK)
	bot.active = true
	var ok := await _laps(3)
	bot.active = false
	var laps: Array = game.timing.laps
	check("laps.three_consecutive_valid", ok and laps.size() == 3 and game.timing.refused.is_empty(), laps.size())
	var times := laps.map(func(l): return float(l.time))
	check("laps.times_plausible", times.all(func(t): return t > 25.0 and t < 60.0), times)
	check("laps.session_best_is_min", is_equal_approx(game.timing.best_time, times.min()), [game.timing.best_time, times])
	var gate_ids: Array = game.events.filter(func(e): return e.event == "gate").map(func(e): return e.gate)
	check("laps.every_checkpoint_in_order", gate_ids.slice(0, 9) == ["HEM", "SIDING", "DOCK", "HEM", "SIDING", "DOCK", "HEM", "SIDING", "DOCK"], gate_ids)
	var board: String = game.builder.chalkboard_label.text
	check("laps.chalkboard_shows_best", board.contains(game.Timing.format_time(game.timing.best_time)), board)
	check("laps.no_resets", game.craft.reset_count == 0)
	check("laps.sectors_sum_to_lap", laps.all(func(l): return absf((l.sectors as Array).reduce(func(a, b): return a + b, 0.0) - float(l.time)) < 0.002))
	scenarios["consecutive_laps"] = {"times": times, "sectors": laps.map(func(l): return l.sectors), "impacts": game.craft.impact_count}


func _stop_and_turn(degrees: float) -> void:
	## Spread, brake to a stop, then rotate in place with full steer.
	bot.active = false
	Bot.release()
	Input.action_press("brake")
	await _until(func(): return game.craft.velocity.length() < 0.6, 600)
	Input.action_release("brake")
	var start_yaw: float = game.craft.rotation.y
	Input.action_press("steer_left")
	await _until(func(): return absf(rad_to_deg(wrapf(game.craft.rotation.y - start_yaw, -PI, PI))) >= degrees - 4.0, 600)
	Input.action_release("steer_left")


func _scenario_doubling_back() -> void:
	await _fresh("RACE")
	var line_s: float = game.course.gates[0].s
	# Spread straight over the line, then double back across it twice.
	bot.set_plan(Plans.CENTRE_SPREAD)
	bot.active = true
	await _until(func(): return game.progress_s > line_s + 18.0, 900)
	check("double.first_crossing_started_clock", game.timing.lap_active)
	var first_start: float = game.timing.lap_start
	await _stop_and_turn(180.0)
	Input.action_press("throttle")
	await _until(func(): return game.progress_s < line_s - 15.0, 900)
	Input.action_release("throttle")
	check("double.backward_crossing_keeps_lap_unvalidated", game.timing.laps.is_empty() and game.timing.lap_start == first_start)
	await _stop_and_turn(180.0)
	bot.set_plan(Plans.CENTRE_SPREAD)
	bot.active = true
	await _until(func(): return game.progress_s > line_s + 10.0 and game.progress_s < line_s + 60.0, 900)
	bot.active = false
	check("double.no_lap_awarded", game.timing.laps.is_empty(), game.timing.laps.size())
	check("double.refusal_has_no_checkpoints", game.timing.refused.size() == 1 and not bool(game.timing.refused[0].passed_any), game.timing.refused)
	check("double.clock_restarted_on_forward_crossing", game.timing.lap_active and game.timing.lap_start > first_start)
	# The run continues: the next full lap from here is a valid lap.
	bot.set_plan(Plans.FLICK)
	bot.active = true
	var ok := await _laps(1)
	check("double.next_full_lap_valid", ok and game.timing.laps.size() == 1)
	scenarios["doubling_back"] = {"refused": game.timing.refused, "valid_after": game.timing.laps.map(func(l): return l.time)}


func _scenario_skipped_checkpoint() -> void:
	await _fresh("RACE")
	bot.set_plan(Plans.FLICK)
	bot.active = true
	var hem: Vector2 = game.course.piece_ranges["HEM"]
	await _until(func(): return game.progress_s > hem.x - 30.0 and game.timing.lap_active, 1200)
	# Test-only cut: jump across the infield from the Hem entry to its exit.
	var exit_pose: Dictionary = game.course.pose_at(hem.y + 8.0)
	var c: CraftController = game.craft
	var yaw := atan2(-exit_pose.f.x, -exit_pose.f.y)
	c.global_transform = Transform3D(Basis(Vector3.UP, yaw), Vector3(exit_pose.p.x, c.global_position.y, exit_pose.p.y))
	c.velocity = Vector3(exit_pose.f.x, 0, exit_pose.f.y) * 20.0
	c.reset_physics_interpolation()
	await _until(func(): return not game.timing.refused.is_empty(), 60 * 40)
	var refused: Array = game.timing.refused
	check("skip.lap_refused", refused.size() == 1 and game.timing.laps.is_empty(), refused)
	check("skip.names_missed_hem", refused.size() == 1 and (refused[0].missed as Array) == [1], refused)
	check("skip.reported_on_hud", String(game.hud.result_line.text).contains("missed the Hem"), game.hud.result_line.text)
	var ok := await _laps(1)
	check("skip.following_lap_valid", ok and game.timing.laps.size() == 1)
	scenarios["skipped_checkpoint"] = {"refused": refused, "hud": game.hud.result_line.text}


func _scenario_retry() -> void:
	await _fresh("RACE")
	bot.set_plan(Plans.FLICK)
	bot.active = true
	await _until(func(): return game.piece == "SIDING" and game.timing.lap_active, 60 * 40)
	bot.active = false
	Bot.release()
	var grid: Transform3D = game.course.grid_transform(1.3)
	await _press("reset")
	await _ticks(2)
	var c: CraftController = game.craft
	check("retry.back_on_grid", Vector2(c.global_position.x, c.global_position.z).distance_to(Vector2(grid.origin.x, grid.origin.z)) < 1.0)
	check("retry.lap_discarded_without_refusal", not game.timing.lap_active and game.timing.refused.is_empty() and game.timing.laps.is_empty())
	check("retry.clock_shows_zero", game.hud.lap_clock.text == "0:00.00", game.hud.lap_clock.text)
	bot.active = true
	var ok := await _laps(1)
	check("retry.next_attempt_is_valid_lap", ok and game.timing.laps.size() == 1)
	scenarios["retry"] = {"lap": game.timing.laps.map(func(l): return l.time), "resets": c.reset_count}


func _story_lines() -> Array:
	return game.events.filter(func(e): return e.event == "story_line").map(func(e): return e.line)


func _scenario_story_hit() -> void:
	await _fresh("CREW")
	var story = game.story
	check("hit.brief_line_spoken", game.hud.story_visible() and String(game.hud.story_text.text).contains("jacket"))
	bot.set_plan(Plans.INSIDE_HEM)
	bot.active = true
	await _until(func(): return story.state != "WAITING", 60 * 40)
	check("hit.caught_first_pass", story.state == "CARRYING" and story.misses == 0, story.catch_record)
	check("hit.caught_in_spread_moving", String(story.catch_record.get("form", "")) == "SPREAD" and float(story.catch_record.get("speed", 0)) > 7.0, story.catch_record)
	check("hit.jacket_visible_on_craft", story.craft_jacket.visible and story.craft_jacket.is_visible_in_tree())
	check("hit.tess_hand_empty", not story.held_jacket.visible)
	await _until(func(): return story.state == "DELIVERED", 60 * 40)
	check("hit.delivered_at_line", story.state == "DELIVERED")
	check("hit.crew_driver_now_wearing_it", story.crew_driver_jacket.visible and not story.craft_jacket.visible)
	await _ticks(60 * 20)
	var lines := _story_lines()
	var verdict: String = game.Story.Text.DELIVER_FIRST if story.scuffs == 0 else (game.Story.Text.DELIVER_SCUFF if story.scuffs == 1 else game.Story.Text.DELIVER_WALL)
	check("hit.crew_answer_matches_run", lines.has(verdict), [story.scuffs, lines])
	check("hit.reveal_names_the_hem", lines.has(game.Story.Text.REVEAL[2][1]), lines)
	check("hit.lines_short", lines.all(func(l): return String(l).length() <= 64), lines)
	scenarios["story_hit"] = {"delivered": story.delivered_record, "lines": lines}


func _scenario_story_miss_then_hit() -> void:
	await _fresh("CREW")
	var story = game.story
	bot.set_plan(Plans.FLICK)
	bot.active = true
	await _until(func(): return story.misses >= 1 or story.state != "WAITING", 60 * 40)
	check("miss.recorded_on_fast_wide_line", story.misses == 1 and story.state == "WAITING", [story.misses, story.state])
	check("miss.tess_still_holding", story.held_jacket.visible and not story.craft_jacket.visible)
	check("miss.marker_and_chalk_visible", story.miss_ring.visible and story.chalk_hints.visible)
	await _ticks(2)
	check("miss.hud_says_missed", String(game.hud.message.text).contains("missed"), game.hud.message.text)
	# Second attempt: unfold early and take the inside wall.
	bot.set_plan(Plans.INSIDE_HEM)
	await _until(func(): return story.state == "CARRYING", 60 * 60)
	check("miss.second_pass_caught", story.state == "CARRYING" and int(story.catch_record.get("attempt", 0)) == 2, story.catch_record)
	check("miss.marker_cleared_on_catch", not story.miss_ring.visible)
	await _until(func(): return story.state == "DELIVERED", 60 * 40)
	await _ticks(60 * 6)
	var lines := _story_lines()
	check("miss.delivered_with_attempt_count", story.state == "DELIVERED" and int(story.delivered_record.misses) == 1)
	var expected: String = game.Story.Text.DELIVER_AGAIN if story.scuffs == 0 else (game.Story.Text.DELIVER_SCUFF if story.scuffs == 1 else game.Story.Text.DELIVER_WALL)
	check("miss.crew_answer_acknowledges_retries", lines.has(expected), [story.scuffs, lines])
	check("miss.tess_miss_line_spoken", lines.has(game.Story.Text.MISS[0]), lines)
	scenarios["story_miss_then_hit"] = {"delivered": story.delivered_record, "lines": lines}


func _scenario_story_scuff() -> void:
	await _fresh("CREW")
	var story = game.story
	bot.set_plan(Plans.INSIDE_HEM)
	bot.active = true
	await _until(func(): return story.state == "CARRYING", 60 * 40)
	# Carrying the jacket, steer hard into the Hem exit's outside wall in Drive.
	bot.active = false
	Bot.release()
	Input.action_press("transform")
	Input.action_press("throttle")
	Input.action_press("steer_right")
	await _until(func(): return story.scuffs >= 1, 60 * 8)
	Bot.release()
	check("scuff.wall_hit_marks_jacket", story.scuffs >= 1 and story.craft_scuffs[0].visible, story.scuffs)
	bot.active = true
	await _until(func(): return story.state == "DELIVERED", 60 * 60)
	await _ticks(60 * 4)
	var lines := _story_lines()
	check("scuff.crew_notices_wall", story.state == "DELIVERED" and (lines.has(game.Story.Text.DELIVER_SCUFF) or lines.has(game.Story.Text.DELIVER_WALL)), [story.scuffs, lines])
	scenarios["story_scuff"] = {"delivered": story.delivered_record}


func _scenario_lines() -> void:
	## Reference lap times for the documented lines (bot driving, not a human).
	var results := {}
	for plan_name in ["FLICK", "DOCK_HOP", "INSIDE_HEM", "CENTRE_SPREAD"]:
		await _fresh("RACE")
		bot.set_plan((Plans as Script).get_script_constant_map()[plan_name])
		bot.active = true
		var ok := await _laps(2)
		bot.active = false
		results[plan_name] = {"ok": ok, "laps": game.timing.laps.map(func(l): return snappedf(float(l.time), 0.01)),
			"sectors": game.timing.laps.map(func(l): return (l.sectors as Array).map(func(x): return snappedf(x, 0.01))),
			"impacts": game.craft.impact_count, "hops": game.craft.hop_count}
		check("lines.%s_two_valid_laps" % plan_name, ok and game.timing.refused.is_empty())
	check("lines.dock_hop_used_hop", int(results.DOCK_HOP.hops) >= 2)
	var dock_sector: float = results.DOCK_HOP.sectors[-1][2]
	var lane_sector: float = results.FLICK.sectors[-1][2]
	check("lines.dock_hop_shortcut_faster_sector", dock_sector < lane_sector - 0.5, [dock_sector, lane_sector])
	var inside_hem: float = results.INSIDE_HEM.sectors[-1][0] + results.INSIDE_HEM.sectors[-1][1]
	var drift_hem: float = results.FLICK.sectors[-1][0] + results.FLICK.sectors[-1][1]
	check("lines.inside_story_line_costs_time", inside_hem > drift_hem + 0.8, [inside_hem, drift_hem])
	scenarios["lines"] = results
