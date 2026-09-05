extends SceneTree

const Resources = preload("res://scripts/overcast_resources.gd")
const Presentation = preload("res://scripts/world_polish_presentation.gd")
var checks: Array = []
var out := ""

func _initialize() -> void:
	call_deferred("run")

func check(id: String, passed: bool, detail: Variant = null) -> void:
	checks.append({"id": id, "pass": passed, "detail": detail})

func run() -> void:
	var args := OS.get_cmdline_user_args()
	out = args[args.find("--result") + 1]
	var scene = load("res://scenes/district_zero_run.tscn").instantiate()
	root.add_child(scene)
	for i in 10:
		await process_frame
	var gate: P1AWorldGate = scene.get_node("DistrictZeroP1A")
	var run_layer: Node = scene.get_node("RunLayer")
	var weather: Node3D = gate.get_node("WarmOvercastWeather")
	var rain: GPUParticles3D = weather.rain
	var a: Image = Resources.sky_image
	var b := Resources.cloud_image()
	check("SKY_REPEATABLE", a.get_data() == b.get_data())
	check("SKY_REUSED", Resources.sky() == Resources.sky())
	check("SKY_SIZE", a.get_size() == Vector2i(1024, 512))
	var seam := true
	for y in a.get_height():
		seam = seam and a.get_pixel(0, y) == a.get_pixel(1023, y)
	check("SKY_LONGITUDE_SEAM", seam)
	check("SKY_CLOUD_CONTRAST", a.get_pixel(150, 190) != a.get_pixel(400, 190))
	check("SKY_HORIZON_LIGHTER", a.get_pixel(0, 254).get_luminance() > a.get_pixel(0, 150).get_luminance())
	a.save_png(out.get_base_dir().path_join("cloud_panorama.png"))
	check("NATIVE_SKY", Resources.sky().sky_material is PanoramaSkyMaterial)
	check("BOUNDED_RAIN", rain.amount == 384 and is_equal_approx(rain.lifetime, 1.7))
	check("WORLD_SPACE_RAIN", not rain.local_coords and rain.use_fixed_seed)
	check("RAIN_NATIVE_MATERIALS", rain.process_material is ParticleProcessMaterial and rain.draw_pass_1.material is StandardMaterial3D)
	check("RAIN_HIDE_ON_CONTACT", rain.process_material.collision_mode == ParticleProcessMaterial.COLLISION_HIDE_ON_CONTACT)
	check("RAIN_STATIC_HEIGHTFIELD", not weather.rain_collision.follow_camera_enabled and weather.rain_collision.update_mode == GPUParticlesCollisionHeightField3D.UPDATE_MODE_WHEN_MOVED)
	check("RAIN_NO_BODY_COLLISION", weather.find_children("*", "CollisionObject3D", true, false).is_empty())
	check("STATIC_CAPTURE_MASK", weather.rain_collision.heightfield_mask == 2)
	var static_only := true
	for visual in gate.craft.find_children("*", "GeometryInstance3D", true, false):
		static_only = static_only and (visual.layers & 2) == 0
	check("CRAFT_EXCLUDED_FROM_RAIN_HEIGHTFIELD", static_only)
	var marker: Vector2 = run_layer._map_overlay.marker_position()
	var relay := gate.map._world_to_map(Vector2(0, -210))
	check("RUN_MARKER_ALIGNS_RELAY", marker.distance_to(relay) < 0.01, [marker.x, marker.y, relay.x, relay.y])
	check("RUN_MARKER_NORTHERN", marker.y < gate.map.size.y * 0.5)
	check("EDGE_RULE_ZERO", not Presentation.drawable_edge(["test", [0,0], [0,0], 5]))
	check("EDGE_RULE_SHORT", not Presentation.drawable_edge(["test", [0,0], [0.00001,0], 5]))
	check("EDGE_RULE_AT_THRESHOLD", Presentation.drawable_edge(["test", [0,0], [0.0001,0], 5]))
	var omitted := 0
	for edge in gate.data.polish.wall_edges:
		if not Presentation.drawable_edge(edge):
			omitted += 1
	check("SIX_MICROSCOPIC_EDGES_ACCOUNTED", omitted == 6, omitted)
	var terrain: MeshInstance3D = gate.world.get_node("FrozenHeightfieldVisual")
	var material: StandardMaterial3D = terrain.mesh.surface_get_material(0)
	var mask: Image = material.roughness_texture.get_image()
	check("SURFACE_SUCCESSOR_ROUGHNESS_ATLAS", mask.get_size() == Vector2i(2048,2048) and mask.has_mipmaps())
	check("MINERAL_ALBEDO_PRESERVED", Resources.terrain_color(Color(0.4,0.3,0.2), 12) == Color(0.4,0.3,0.2))
	# Pause is tested explicitly because the parent gate processes while paused.
	paused = true
	await process_frame
	var age: float = weather.active_time
	for i in 20:
		await process_frame
	check("WEATHER_PAUSE", weather.active_time == age and not rain.can_process())
	var prior_restarts: int = weather.restart_count
	run_layer.start_attempt()
	for i in 5:
		await process_frame
	check("PAUSED_RETRY_PENDING", weather.reset_pending and weather.restart_count == prior_restarts)
	paused = false
	for i in 5:
		await process_frame
	check("PAUSED_RETRY_CLEAN_RESTART", weather.restart_count == prior_restarts + 1 and rain.emitting and not weather.reset_pending)
	check("FOLLOW_CAMERA", rain.global_position.distance_to(gate.camera_rig.get_node("Camera").global_position + Vector3.UP * 10.0) < 0.01)
	prior_restarts = weather.restart_count
	gate.craft.reset_craft("fell below reset plane")
	for i in 5:
		await process_frame
	check("FALL_WEATHER_RESTART", weather.restart_count > prior_restarts)
	prior_restarts = weather.restart_count
	gate.spawn_selected_tour()
	for i in 5:
		await process_frame
	check("DIAGNOSTIC_WEATHER_RESTART", weather.restart_count == prior_restarts + 1)
	run_layer.enter_free_roam()
	check("FREE_ROAM_WEATHER", rain.emitting and run_layer.state_name() == "FREE_ROAM")
	if DisplayServer.get_name() != "headless":
		gate.craft.set_physics_process(false)
		gate.camera_rig.set_physics_process(false)
		gate.craft.process_mode = Node.PROCESS_MODE_DISABLED
		gate.get_node("SurfaceFeedback").process_mode = Node.PROCESS_MODE_DISABLED
		gate.get_node("UI").visible = false
		for i in 120:
			await process_frame
		await RenderingServer.frame_post_draw
		var wet := root.get_texture().get_image()
		wet.save_png(out.get_base_dir().path_join("drizzle_visible.png"))
		rain.visible = false
		for i in 3:
			await process_frame
		await RenderingServer.frame_post_draw
		var dry := root.get_texture().get_image()
		dry.save_png(out.get_base_dir().path_join("drizzle_hidden_control.png"))
		var changed := 0
		for y in wet.get_height():
			for x in wet.get_width():
				if wet.get_pixel(x,y) != dry.get_pixel(x,y):
					changed += 1
		check("NATIVE_DRIZZLE_HAS_PIXELS", changed > 0 and changed < 100000, changed)
		rain.visible = true
	var failures: Array = []
	for item in checks:
		if not item.pass:
			failures.append(item.id)
	FileAccess.open(out, FileAccess.WRITE).store_string(JSON.stringify({"status":"PASS" if failures.is_empty() else "FAIL","check_count":checks.size(),"checks":checks,"failures":failures}, "  "))
	print("OVERCAST_RUNTIME ", JSON.stringify(failures))
	scene.queue_free()
	await process_frame
	quit(0 if failures.is_empty() else 1)
