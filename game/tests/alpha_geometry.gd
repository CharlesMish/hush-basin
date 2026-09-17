extends SceneTree
func _initialize() -> void:call_deferred("run")
func snapshot(gate: P1AWorldGate) -> Dictionary:
	var rows: Array=[]
	for n in gate.world.find_children("*","CollisionShape3D",true,false):
		var shape: Shape3D=n.shape
		var properties: Dictionary={}
		for key in ["size","radius","height","points","data","map_width","map_depth","map_data","margin"]:
			if key in shape:properties[key]=var_to_bytes(shape.get(key)).hex_encode().sha256_text()
		# Godot's auto-generated child names use process-global instance counters.
		# Parent source identity + stable child index avoids mistaking these for geometry.
		rows.append({"parent":String(gate.world.get_path_to(n.get_parent())),"child_index":n.get_index(),"transform":var_to_bytes(n.transform).hex_encode(),"class":shape.get_class(),"properties":properties,"disabled":n.disabled,"layer":n.get_parent().collision_layer,"mask":n.get_parent().collision_mask})
	var terrain: MeshInstance3D=gate.world.get_node("FrozenHeightfieldVisual")
	var arrays:=terrain.mesh.surface_get_arrays(0)
	var hashes: Dictionary={}
	for slot in [Mesh.ARRAY_VERTEX,Mesh.ARRAY_NORMAL,Mesh.ARRAY_INDEX]:hashes[str(slot)]=var_to_bytes(arrays[slot]).hex_encode().sha256_text()
	return {"collision_sha256":JSON.stringify(rows).sha256_text(),"collision_count":rows.size(),"terrain":hashes}
func run() -> void:
	var args:=OS.get_cmdline_user_args();var out:=args[args.find("--result")+1]
	var baseline=load("res://scenes/district_zero_p1a.tscn").instantiate();root.add_child(baseline)
	await process_frame;await physics_frame
	var before:=snapshot(baseline)
	baseline.queue_free();await process_frame
	var game=load("res://scenes/district_zero_alpha.tscn").instantiate();root.add_child(game)
	for i in 4:await process_frame
	var gate: P1AWorldGate=game.get_node("DistrictZeroP1A")
	var after:=snapshot(gate)
	var lantern:=gate.world.get_node("MarketHomeLantern")
	var checks:={"collision_identical":before.collision_sha256==after.collision_sha256,"terrain_identical":before.terrain==after.terrain,"landmark_no_collision":lantern.find_children("*","CollisionObject3D",true,false).is_empty(),"three_material_batches":lantern.get_child_count()==3}
	var finite:=true;var materials:=true;var mask:=true;var count:=0;var contained:=true
	for n in lantern.get_children():
		materials=materials and n.material_override is StandardMaterial3D
		mask=mask and n.layers==3
		count+=n.multimesh.instance_count
		# Headless Dummy rendering returns identity for GPU-backed transform reads.
		# Inspect the authored CPU definitions there; native lane also checks GPU data.
		var authored: Array=lantern._batches[n.material_override]
		for i in n.multimesh.instance_count:
			var t: Transform3D=authored[i] if DisplayServer.get_name()=="headless" else n.multimesh.get_instance_transform(i)
			finite=finite and t.is_finite() and t.basis.determinant()>0
			contained=contained and absf(t.origin.x)<=3 and absf(t.origin.z-67)<=3 and t.origin.y>=19.5
	checks.merge({"finite_positive_transforms":finite,"native_materials":materials,"rain_mask":mask,"roof_contained":contained,"bounded_instances":count<=40})
	var good:=true
	for v in checks.values():good=good and v
	FileAccess.open(out,FileAccess.WRITE).store_string(JSON.stringify({"status":"PASS" if good else "FAIL","checks":checks,"before":before,"after":after,"instances":count},"  "))
	quit(0 if good else 1)
