extends "res://tests/world_polish_survey.gd"
func run() -> void:
	var args := OS.get_cmdline_user_args()
	out = args[args.find("--output") + 1]
	DirAccess.make_dir_recursive_absolute(out)
	assert(RenderingServer.get_current_rendering_method() == "forward_plus")
	assert(root.size == Vector2i(1280, 720))
	var gate = load("res://scenes/district_zero_p1a.tscn").instantiate()
	root.add_child(gate)
	await process_frame
	gate.craft.set_physics_process(false)
	gate.telemetry.set_physics_process(false)
	gate.get_node("UI").hide()
	for tour in gate.data.diagnostic.tours:
		if tour.id not in ["T02_WEST_SWEEP", "T03_EAST_SWEEP", "T04_QUARRY_SHELF"]:
			continue
		var s: Dictionary = tour.spawn_transform
		var p: Array = s.position_xyz_m
		await player_view(gate, tour.id, Vector3(p[0],p[1],p[2]), s.yaw_rad)
	await player_view(gate,"yard_market",Vector3(-65,gate.data.terrain_height_at(-65,60)+1.65,60),-1.57)
	var f := FileAccess.open(out.path_join("survey.json"), FileAccess.WRITE)
	f.store_string(JSON.stringify({"records":records,"stage":"edge-only"},"  "))
	quit()
