extends SceneTree
## Controlled road starts, unchanged normal player camera, both visual forms.
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
	gate.get_node("UI").visible = false
	var rows: Array = []
	for item in [["QRY",Vector2(-260,32),Vector2(-303,30)],["DEP",Vector2(-110,75),Vector2(-142,120)],["RLY",Vector2(0,-225),Vector2(0,-285)],["WRK",Vector2(92,-40),Vector2(132,-82)],["MRK",Vector2(-32,50),Vector2(0,80)],["CLN",Vector2(110,75),Vector2(145,120)]]:
		var position: Vector2 = item[1]
		var direction: Vector2 = (item[2]-position).normalized()
		var yaw := atan2(-direction.x,-direction.y)
		for form in [0.0,1.0]:
			var craft_position := Vector3(position.x,gate.data.terrain_height_at(position.x,position.y)+1.65,position.y)
			gate.craft.set_spawn_transform(Transform3D(Basis(Vector3.UP,yaw),craft_position))
			gate.craft.reset_craft("identity-approach-evidence")
			gate.craft.fold_amount = form
			gate.craft.get_node("VisualRoot").set_form_amount(form)
			gate.camera_rig.snap_to_target()
			for i in 45:
				await process_frame
			await RenderingServer.frame_post_draw
			var id := String(item[0])+ ("_Drive" if form>0 else "_Spread")
			root.get_texture().get_image().save_png(out.path_join(id+".png"))
			rows.append({"id":id,"image":id+".png","craft":craft_position,"yaw":yaw,"camera":gate.camera_rig.get_node("Camera").global_position})
	FileAccess.open(out.path_join("approaches.json"),FileAccess.WRITE).store_string(JSON.stringify({"status":"PASS","records":rows,"note":"Registered stationary road starts using unchanged player camera; moving input routes recorded separately."},"  "))
	quit()
