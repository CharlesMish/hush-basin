extends SceneTree
var checks: Array = []
func _initialize() -> void:
	call_deferred("run")
func check(id: String, ok: bool, detail: Variant = null) -> void:
	checks.append({"id":id,"pass":ok,"detail":detail})
func run() -> void:
	var gate: P1AWorldGate = load("res://scenes/district_zero_p1a.tscn").instantiate()
	root.add_child(gate)
	for i in 10:
		await physics_frame
	gate.craft.set_physics_process(false)
	var architecture := gate.world.get_node("WorkingNeighborhood")
	var d: Dictionary = architecture.get_meta("definition")
	var shapes := architecture.find_children("*", "CollisionShape3D", true, false)
	var solid_count := 0
	for p in d.parts:
		if p.solid:
			solid_count += 1
	check("EVERY_STRUCTURAL_PART_HAS_COLLISION", shapes.size() == solid_count, solid_count)
	var matching := true
	for shape in shapes:
		var p: Dictionary = d.parts[int(shape.get_meta("definition_index"))]
		var size := Vector3(p.size[0],p.size[1],p.size[2])
		matching = matching and shape.position.distance_to(Vector3(p.p[0],p.p[1],p.p[2])) < 0.0001
		if shape.shape is BoxShape3D:
			matching = matching and shape.shape.size.is_equal_approx(size)
		else:
			matching = matching and is_equal_approx(shape.shape.radius, size.x * 0.5) and is_equal_approx(shape.shape.height, size.y)
	check("COLLIDER_DEFINITIONS_MATCH_RENDER_SOURCE", matching)
	var mask_ok := true
	var instances := 0
	var render_match := true
	var max_render_delta := 0.0
	for node in architecture.find_children("*", "MultiMeshInstance3D", true, false):
		mask_ok = mask_ok and (node.layers & 2) != 0
		instances += node.multimesh.instance_count
		var index := 0
		for row in d.parts:
			var key := "Architecture_%s_%s_%s" % [row.kind,row.emission,row.solid]
			if String(node.name) != key:
				continue
			var expected := Transform3D(Basis(Vector3.UP,float(row.yaw))*Basis.from_scale(Vector3(row.size[0],row.size[1],row.size[2])),Vector3(row.p[0],row.p[1],row.p[2]))
			var actual: Transform3D = node.multimesh.get_instance_transform(index)
			var delta := actual.origin.distance_to(expected.origin)
			for axis in 3:
				delta = maxf(delta,actual.basis[axis].distance_to(expected.basis[axis]))
			max_render_delta = maxf(max_render_delta,delta)
			render_match = render_match and delta<0.0001
			index += 1
	check("ALL_PARTS_RENDERED", instances == d.parts.size(), instances)
	# Dummy headless rendering returns identity for MultiMesh GPU readback.
	# Require this check in native verification; do not call it a headless pass.
	if DisplayServer.get_name()!="headless":
		check("RENDER_TRANSFORMS_MATCH_SHARED_SOURCE",render_match,{"max_native_float_delta_m":max_render_delta,"limit_m":0.0001})
	check("BATCHES_JOIN_STATIC_RAIN_MASK", mask_ok)
	check("NO_ADDED_LIGHTS", architecture.find_children("*", "Light3D", true, false).is_empty())
	var state: PhysicsDirectSpaceState3D = gate.world.get_world_3d().direct_space_state
	for f in d.compound_frontages:
		var pad: Array = gate.data.manifest.nodes[f.node].xz_m
		var basis := Basis(Vector3.UP,float(f.yaw))
		var visible := true
		var blockers: Array = []
		for y in [2.0,4.65]:
			for u in [-float(f.width)*0.4,0.0,float(f.width)*0.4]:
				var target := Vector3(f.p[0],y,f.p[2])+basis*Vector3(u,0,0.22)
				var query := PhysicsRayQueryParameters3D.create(Vector3(pad[0],y,pad[1]),target,1,[gate.craft.get_rid()])
				var blocker := state.intersect_ray(query)
				if not blocker.is_empty():
					blockers.append({"position":blocker.position,"normal":blocker.normal,"body":String(blocker.collider.name)})
				visible = visible and blocker.is_empty()
		check("COMPOUND_FRONT_VISIBLE_FROM_PAD:"+String(f.node)+":"+String(f.title),visible,blockers)
	for owner in d.owners:
		var p := Vector3.ZERO
		for row in d.parts:
			if row.owner == owner.id and row.role in ["upper_mass","landmark_mass"]:
				p = Vector3(row.p[0],float(owner.principal_top),row.p[2])
		var query := PhysicsRayQueryParameters3D.create(p+Vector3.UP*5,p-Vector3.UP,1,[gate.craft.get_rid()])
		var hit := state.intersect_ray(query)
		# The retained Market fin overlaps B10. Validate the visible union top,
		# rather than pretending each overlapping mass has an exposed roof.
		var expected_top := -INF
		for row in d.parts:
			if not row.solid:
				continue
			var local := Basis(Vector3.UP,-float(row.yaw))*(p-Vector3(row.p[0],row.p[1],row.p[2]))
			var inside := absf(local.x)<=float(row.size[0])*0.5 and absf(local.z)<=float(row.size[2])*0.5
			if row.kind=="cylinder":
				inside = Vector2(local.x,local.z).length()<=float(row.size[0])*0.5
			var top := float(row.p[1])+float(row.size[1])*0.5
			if inside and top<=p.y+5.0:
				expected_top = maxf(expected_top,top)
		check("SUPPORTED_STRUCTURAL_TOP:"+String(owner.id),not hit.is_empty() and absf(hit.position.y-expected_top)<0.02,hit.get("position",null))
	# Exercise actual shipped normal inputs against the B01 service-side wall,
	# then brake/turn out to ensure architecture is a recoverable solid boundary.
	gate.craft.set_physics_process(true)
	gate.craft.set_spawn_transform(Transform3D(Basis.IDENTITY,Vector3(-80,7.15,9)))
	gate.craft.reset_craft("architecture-contact")
	gate.camera_rig.snap_to_target()
	for i in 90:
		await physics_frame
	Input.action_press("throttle")
	for i in 120:
		await physics_frame
	Input.action_release("throttle")
	Input.action_press("brake")
	for i in 60:
		await physics_frame
	Input.action_release("brake")
	var contact := gate.craft.global_position
	check("STRUCTURE_CONTACT",gate.craft.velocity.is_finite() and gate.craft.impact_count>0 and contact.z>=7.0,{"position":contact,"impacts":gate.craft.impact_count})
	Input.action_press("steer_right")
	for i in 120:
		await physics_frame
	Input.action_release("steer_right")
	Input.action_press("throttle")
	for i in 120:
		await physics_frame
	Input.action_release("throttle")
	check("STRUCTURE_RECOVERY",gate.craft.velocity.is_finite() and gate.craft.reset_count==1 and gate.craft.global_position.distance_to(contact)>2.0)
	var args := OS.get_cmdline_user_args()
	var out := args[args.find("--result")+1]
	var ok := true
	for c in checks:
		ok = ok and c.pass
	FileAccess.open(out,FileAccess.WRITE).store_string(JSON.stringify({"status":"PASS" if ok else "FAIL","checks":checks,"check_count":checks.size()},"  "))
	print("NEIGHBORHOOD_RUNTIME ",ok," ",checks.size())
	quit(0 if ok else 1)
