extends SceneTree
## Runs unchanged with baseline and successor project roots.
func _initialize() -> void:
	call_deferred("run")

func run() -> void:
	var args := OS.get_cmdline_user_args()
	var output := args[args.find("--result")+1]
	var gate = load("res://scenes/district_zero_p1a.tscn").instantiate()
	root.add_child(gate)
	await process_frame
	await physics_frame
	var rows: Array = []
	for n in gate.world.find_children("*","CollisionShape3D",true,false):
		var shape: Shape3D = n.shape
		var properties: Dictionary = {}
		for key in ["size","radius","height","points","data","map_width","map_depth","map_data","margin"]:
			if key in shape:
				properties[key] = var_to_bytes(shape.get(key)).hex_encode().sha256_text()
		rows.append({"path":String(gate.world.get_path_to(n)),"transform":var_to_bytes(n.transform).hex_encode(),"class":shape.get_class(),"properties":properties,"disabled":n.disabled,"layer":n.get_parent().collision_layer,"mask":n.get_parent().collision_mask})
	var terrain: MeshInstance3D = gate.world.get_node("FrozenHeightfieldVisual")
	var terrain_arrays := terrain.mesh.surface_get_arrays(0)
	var terrain_hashes: Dictionary = {}
	for slot in [Mesh.ARRAY_VERTEX,Mesh.ARRAY_NORMAL,Mesh.ARRAY_INDEX]:
		terrain_hashes[str(slot)] = var_to_bytes(terrain_arrays[slot]).hex_encode().sha256_text()
	var detail: Node3D = gate.world.get_node_or_null("WorldIdentityDetailV2")
	var checks: Dictionary = {"terrain_finite":terrain.get_aabb().size.is_finite(),"collision_count_nonzero":rows.size()>0}
	var detail_instances := 0
	var detail_batches := 0
	if detail != null:
		checks["detail_no_physics"] = detail.find_children("*","CollisionObject3D",true,false).is_empty() and detail.find_children("*","CollisionShape3D",true,false).is_empty()
		checks["presentation_identity"] = detail.get_meta("presentation_identity") == "world-identity-detail-v2"
		var finite := true
		var native_materials := true
		var rain_mask := true
		for n in detail.find_children("*","MultiMeshInstance3D",true,false):
			detail_batches += 1
			detail_instances += n.multimesh.instance_count
			native_materials = native_materials and n.material_override is StandardMaterial3D
			rain_mask = rain_mask and (n.layers & 2) != 0
			for i in n.multimesh.instance_count:
				var t: Transform3D = n.multimesh.get_instance_transform(i)
				finite = finite and t.origin.is_finite() and t.basis.is_finite() and t.basis.determinant()>0
		checks["finite_positive_transforms"] = finite
		checks["native_materials"] = native_materials
		checks["roof_rain_mask"] = rain_mask
		checks["bounded_batches"] = detail_batches<=12
	var success := true
	for value in checks.values():
		success = success and value
	var result := {"status":"PASS" if success else "FAIL","checks":checks,"collision_count":rows.size(),"collision_sha256":JSON.stringify(rows).sha256_text(),"terrain_geometry_hashes":terrain_hashes,"detail_instances":detail_instances,"detail_batches":detail_batches,"renderer":RenderingServer.get_current_rendering_method()}
	FileAccess.open(output,FileAccess.WRITE).store_string(JSON.stringify(result,"  "))
	print("IDENTITY_RUNTIME ",JSON.stringify(result))
	quit(0 if success else 1)
