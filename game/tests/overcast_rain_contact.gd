extends SceneTree
## Native sensitivity test. A camera sees only rain, while the separate static
## heightfield still sees actual world geometry. No diagnostic enters product.

var out := ""
var checks: Array = []

func _initialize() -> void:
	call_deferred("run")

func pixels_changed(a: Image, b: Image) -> int:
	var changed := 0
	for y in a.get_height():
		for x in a.get_width():
			if a.get_pixel(x,y) != b.get_pixel(x,y):
				changed += 1
	return changed

func frame() -> Image:
	for i in 45:
		await process_frame
	await RenderingServer.frame_post_draw
	return root.get_texture().get_image()

func run() -> void:
	var args := OS.get_cmdline_user_args()
	out = args[args.find("--result") + 1]
	var gate = load("res://scenes/district_zero_p1a.tscn").instantiate()
	root.add_child(gate)
	for i in 120:
		await process_frame
	gate.get_node("UI").visible = false
	var weather: Node3D = gate.get_node("WarmOvercastWeather")
	weather.set_process(false)
	var rain: GPUParticles3D = weather.rain
	rain.layers = 4
	rain.amount = 64
	rain.lifetime = 1.0
	rain.process_material = rain.process_material.duplicate()
	rain.process_material.emission_box_extents = Vector3(0.6, 0.05, 0.6)
	rain.process_material.initial_velocity_min = 0.0
	rain.process_material.initial_velocity_max = 0.0
	var material: StandardMaterial3D = rain.draw_pass_1.material
	material.albedo_color = Color.WHITE
	var camera := Camera3D.new()
	camera.cull_mask = 4
	camera.projection = Camera3D.PROJECTION_ORTHOGONAL
	camera.size = 3.0
	gate.add_child(camera)
	camera.make_current()
	var ground := Vector3(-200, gate.data.terrain_height_at(-200,-10) - 0.3, -10)
	# B01 roof, QRY_STEP_A top, and exposed yard support are frozen source data.
	for item in [["ground", ground], ["roof", Vector3(-80,15.2,-5)], ["quarry_retaining_top", Vector3(-302,11.7,12)]]:
		var id := String(item[0])
		var position: Vector3 = item[1]
		rain.global_position = position
		camera.global_position = position + Vector3(0,2,2)
		camera.look_at(position)
		rain.visible = false
		var empty := await frame()
		rain.visible = true
		rain.process_material.collision_mode = ParticleProcessMaterial.COLLISION_HIDE_ON_CONTACT
		rain.restart(true)
		var contact := await frame()
		contact.save_png(out.get_base_dir().path_join(id + "_contact.png"))
		rain.process_material.collision_mode = ParticleProcessMaterial.COLLISION_DISABLED
		rain.restart(true)
		var control := await frame()
		control.save_png(out.get_base_dir().path_join(id + "_disabled_control.png"))
		var killed := pixels_changed(empty,contact)
		var visible := pixels_changed(empty,control)
		checks.append({"id":id,"pass":visible > 20 and killed < visible * 0.05,"contact_pixels":killed,"disabled_control_pixels":visible})
	var good := true
	for item in checks:
		good = good and item.pass
	FileAccess.open(out, FileAccess.WRITE).store_string(JSON.stringify({"status":"PASS" if good else "FAIL","checks":checks,"note":"Native particle-only camera and controlled emission below real surfaces. White oversized diagnostic drizzle material is test-only."}, "  "))
	print("RAIN_CONTACT ", JSON.stringify(checks))
	gate.queue_free()
	await process_frame
	quit(0 if good else 1)
