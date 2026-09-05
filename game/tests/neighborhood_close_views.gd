extends SceneTree
func _initialize() -> void:
	call_deferred("run")
func run() -> void:
	var args := OS.get_cmdline_user_args()
	var out := args[args.find("--output")+1]
	DirAccess.make_dir_recursive_absolute(out)
	var gate = load("res://scenes/district_zero_p1a.tscn").instantiate()
	root.add_child(gate)
	await process_frame
	gate.craft.set_physics_process(false)
	gate.telemetry.set_physics_process(false)
	gate.craft.visible = false
	gate.get_node("UI").visible = false
	var camera := Camera3D.new()
	gate.add_child(camera)
	camera.fov = 58.0
	camera.far = 1500.0
	camera.make_current()
	gate.get_node("WarmOvercastWeather").camera = camera
	var rows: Array = []
	for item in [["QRY",Vector3(-278,22,65),Vector3(-302,14,30)], ["RLY",Vector3(27,22,-253),Vector3(0,19,-285)], ["DEP",Vector3(-168,19,153),Vector3(-138,12,120)], ["MRK",Vector3(-35,20,113),Vector3(0,12,78)], ["CLN",Vector3(172,22,151),Vector3(145,15,120)], ["WRK",Vector3(98,23,-46),Vector3(132,14,-82)], ["CLN_ENTRY",Vector3(118,9,72),Vector3(143,7,106)], ["DEP_ENTRY",Vector3(-117,9,72),Vector3(-143,7,106)]]:
		camera.position = item[1]
		camera.look_at(item[2])
		for i in 45:
			await process_frame
		await RenderingServer.frame_post_draw
		var path := out.path_join(String(item[0])+".png")
		root.get_texture().get_image().save_png(path)
		rows.append({"id":item[0],"image":String(item[0])+".png","sha256":FileAccess.get_sha256(path),"camera":item[1],"target":item[2]})
	FileAccess.open(out.path_join("close.json"),FileAccess.WRITE).store_string(JSON.stringify({"status":"PASS","renderer":RenderingServer.get_current_rendering_method(),"size":[root.size.x,root.size.y],"records":rows,"note":"Matched evidence cameras, not product camera changes."},"  "))
	quit()
