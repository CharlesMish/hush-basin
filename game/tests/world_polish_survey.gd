extends SceneTree

var records: Array = []
var out := ""

func _initialize() -> void:
	call_deferred("run")

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
	gate.get_node("UI").visible = false
	for tour in gate.data.diagnostic.tours:
		var s: Dictionary = tour.spawn_transform
		var p: Array = s.position_xyz_m
		await player_view(gate, String(tour.id), Vector3(p[0], p[1], p[2]), float(s.yaw_rad))
	for id in ["QRY", "DEP", "MRK", "RLY", "WRK", "CLN"]:
		var p: Array = gate.data.manifest.nodes[id].xz_m
		await player_view(gate, "destination_" + id, Vector3(p[0], gate.data.terrain_height_at(p[0], p[1]) + 1.65, p[1]), 0.0)
	for item in [["yard_west", -210.0, 20.0, -1.25], ["yard_north", 35.0, -165.0, -2.7], ["yard_market", -65.0, 60.0, -1.57]]:
		await player_view(gate, item[0], Vector3(item[1], gate.data.terrain_height_at(item[1], item[2]) + 1.65, item[2]), item[3])
	var camera := Camera3D.new()
	gate.add_child(camera)
	camera.far = 1500.0
	camera.make_current()
	camera.projection = Camera3D.PROJECTION_ORTHOGONAL
	camera.size = 690.0
	camera.position = Vector3(0, 610, -15)
	camera.look_at(Vector3(0, 8, -15), Vector3.FORWARD)
	await capture("overview", camera)
	camera.projection = Camera3D.PROJECTION_PERSPECTIVE
	camera.fov = 52.0
	camera.position = Vector3(-485, 355, 430)
	camera.look_at(Vector3(0, 8, -15))
	await capture("oblique", camera)
	var result := {"engine": Engine.get_version_info(), "renderer": RenderingServer.get_current_rendering_method(), "size": [root.size.x, root.size.y], "records": records, "note": "Static registered/player and evidence overview cameras; not human traversal. Uncapped matched static-view wall-clock frame timings."}
	var f := FileAccess.open(out.path_join("survey.json"), FileAccess.WRITE)
	f.store_string(JSON.stringify(result, "  "))
	gate.queue_free()
	await process_frame
	print("SURVEY PASS ", records.size())
	quit()

func player_view(gate, id: String, p: Vector3, yaw: float) -> void:
	gate.craft.global_transform = Transform3D(Basis(Vector3.UP, yaw), p)
	gate.craft.velocity = Vector3.ZERO
	gate.craft.fold_amount = 0.0
	gate.craft.reset_physics_interpolation()
	gate.camera_rig.snap_to_target()
	await capture(id, gate.camera_rig.get_node("Camera"))

func capture(id: String, camera: Camera3D) -> void:
	for i in 20:
		await process_frame
	await RenderingServer.frame_post_draw
	var path := out.path_join(id + ".png")
	root.get_texture().get_image().save_png(path)
	var frames: Array = []
	var prior := Time.get_ticks_usec()
	for i in 120:
		await process_frame
		var now := Time.get_ticks_usec()
		frames.append(float(now - prior) / 1000.0)
		prior = now
	frames.sort()
	records.append({"id": id, "image": id + ".png", "sha256": FileAccess.get_sha256(path), "camera": [camera.global_position.x, camera.global_position.y, camera.global_position.z], "p50_ms": frames[60], "p95_ms": frames[114], "draw_calls": Performance.get_monitor(Performance.RENDER_TOTAL_DRAW_CALLS_IN_FRAME), "primitives": Performance.get_monitor(Performance.RENDER_TOTAL_PRIMITIVES_IN_FRAME)})
