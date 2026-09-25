extends SceneTree
func _initialize() -> void:call_deferred("run")
func run() -> void:
	var args:=OS.get_cmdline_user_args();var out:=args[args.find("--output")+1]
	set_meta("relay_test_save",out+".legacy.json");set_meta("narrative_test_save",out+".story.json")
	var scene=load("res://review/narrative_presence/review.tscn").instantiate();root.add_child(scene)
	for i in 120:await physics_frame
	var job=scene.job;var craft=job.craft;var data=job.gate.data;var rows: Array=[]
	for z in [68,72,76,78,80,82,84,86,88]:
		for x in [32,36,40,44,48]:
			var q:=PhysicsRayQueryParameters3D.create(Vector3(x,25,z),Vector3(x,-5,z));q.exclude=[craft.get_rid()]
			var h: Dictionary=craft.get_world_3d().direct_space_state.intersect_ray(q)
			rows.append({"xz":[x,z],"terrain":data.terrain_height_at(x,z),"hit_y":h.position.y if not h.is_empty() else -999,"collider":String(h.collider.name) if not h.is_empty() else "none"})
	FileAccess.open(out,FileAccess.WRITE).store_string(JSON.stringify(rows,"  "))
	craft.set_spawn_transform(Transform3D(Basis(Vector3.UP,PI),Vector3(40,data.terrain_height_at(40,76)+1.65,76)));craft.reset_craft("site_fixture");job.gate.camera_rig.snap_to_target()
	for i in 120:await physics_frame
	if DisplayServer.get_name()!="headless":
		RenderingServer.force_draw(false);root.get_texture().get_image().save_png(out+".png")
	quit()
