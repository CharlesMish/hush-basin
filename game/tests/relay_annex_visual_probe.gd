extends SceneTree
const Annex = preload("res://scripts/courier/relay_annex.gd")
var checks: Dictionary = {}
func _initialize() -> void: call_deferred("run")
func check(key: String, value: bool) -> void: checks[key] = value
func run() -> void:
	var data := P1AWorldData.new()
	check("authoritative_world_load", data.load_all())
	var annex := Annex.new()
	root.add_child(annex)
	annex.configure(data)
	check("derived_mast_anchor", annex.position == Vector3(0,8,-285))
	check("stage_zero_untouched", annex.stage == 0 and annex.visible_instance_count() == 0)
	var bound := annex.equipment_bounds
	check("finite_bounds", bound.position.is_finite() and bound.size.is_finite())
	var bounds_world := AABB(bound.position+annex.position, bound.size)
	check("elevated_equipment", bounds_world.position.y > 12.0)
	var within := true
	for i in 8:
		var point := bounds_world.get_endpoint(i)
		within = within and Geometry2D.is_point_in_polygon(Vector2(point.x,point.z),annex.occupied_plot)
	check("all_bounds_inside_existing_occupied_plot", within)
	check("no_physics", annex.find_children("*","CollisionObject3D",true,false).is_empty() and annex.find_children("*","CollisionShape3D",true,false).is_empty())
	check("no_lights_or_particles", annex.find_children("*","Light3D",true,false).is_empty() and annex.find_children("*","GPUParticles3D",true,false).is_empty())
	var finite := true
	var materials := true
	var masks := true
	var batches := 0
	for child in annex.get_children():
		if not child is MultiMeshInstance3D: continue
		batches += 1
		materials = materials and child.material_override is StandardMaterial3D
		masks = masks and (child.layers & 2) != 0
		for i in child.multimesh.instance_count:
			var t: Transform3D = child.multimesh.get_instance_transform(i)
			finite = finite and t.origin.is_finite() and t.basis.is_finite() and t.basis.determinant() > 0.0
	check("finite_positive_transforms",finite)
	check("native_standard_materials",materials)
	check("particle_heightfield_layer",masks)
	check("three_batches_maximum",batches <= 3)
	for stage in [1,2,1,0,2,0]:
		annex.set_stage(stage)
		check("stage_%s_count_%s" % [checks.size(),stage], annex.visible_instance_count() == [0,10,24][stage])
		check("stage_metadata_%s" % checks.size(), annex.get_meta("project_stage") == stage)
		check("header_stage_%s" % checks.size(), annex.get_node("DispatchHeader").visible == (stage == 2))
	annex.set_stage(2)
	annex.configure(data)
	check("reconfigure_bounded",annex.get_child_count() == 4 and annex.visible_instance_count() == 24)
	await process_frame
	var ok := not checks.values().has(false)
	var result := {"status":"PASS" if ok else "FAIL","checks":checks,"count":checks.size(),"instances":annex.visible_instance_count(),"batches":batches,"world_bounds":{"position":[bounds_world.position.x,bounds_world.position.y,bounds_world.position.z],"size":[bounds_world.size.x,bounds_world.size.y,bounds_world.size.z]},"geometry_identity":annex.get_meta("presentation_identity")}
	var args := OS.get_cmdline_user_args()
	if "--result" in args: FileAccess.open(args[args.find("--result")+1],FileAccess.WRITE).store_string(JSON.stringify(result,"  "))
	print("RELAY_VISUAL_RESULT ",JSON.stringify(result))
	quit(0 if ok else 1)
