extends SceneTree
## Chase-camera captures at listed progress marks during a bot lap (needs a
## rendering driver, e.g. xvfb-run ... --rendering-driver opengl3). Env vars:
## PLAN (rink_plans.gd constant), MODE (RACE/CREW), LAP (laps before capturing),
## MARKS (comma-separated progress metres), OUT (existing output directory).
var game: Node3D
var bot
func _initialize() -> void:
	game = (load("res://rink/rink.tscn") as PackedScene).instantiate()
	root.add_child(game)
	bot = load("res://tests/rink_bot.gd").new()
	root.add_child(bot)
	_run.call_deferred()
func _run() -> void:
	await physics_frame
	bot.setup(game)
	bot.set_plan(load("res://tests/rink_plans.gd").get(OS.get_environment("PLAN")))
	game.start_mode(OS.get_environment("MODE") if OS.get_environment("MODE") != "" else "RACE")
	await physics_frame
	bot.active = true
	var marks := []
	for m in OS.get_environment("MARKS").split(","): marks.append(float(m))
	var out := OS.get_environment("OUT")
	var lap_target := int(OS.get_environment("LAP")) if OS.get_environment("LAP") != "" else 0
	var i := 0
	var last_s: float = game.progress_s
	for tick in 9000:
		await physics_frame
		var s: float = game.progress_s
		var laps_done: int = game.timing.laps.size()
		if laps_done >= lap_target and i < marks.size() and last_s < marks[i] and s >= marks[i] and s - last_s < 30.0:
			await process_frame
			await process_frame
			root.get_viewport().get_texture().get_image().save_png("%s/%02d_s%04d.png" % [out, i, int(marks[i])])
			i += 1
		last_s = s
		if i >= marks.size(): break
	print("FILM_DONE ", i)
	quit()
