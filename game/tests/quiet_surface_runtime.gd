extends SceneTree
var checks: Array = []
func _initialize() -> void:
	call_deferred("run")
func check(id: String, ok: bool, detail: Variant = null) -> void:
	checks.append({"id":id,"pass":ok,"detail":detail})
func digest(bytes: PackedByteArray) -> String:
	var h := HashingContext.new()
	h.start(HashingContext.HASH_SHA256)
	h.update(bytes)
	return h.finish().hex_encode()
func run() -> void:
	var args := OS.get_cmdline_user_args()
	var out := args[args.find("--result")+1]
	var baseline := args.has("--baseline")
	var gate: P1AWorldGate = load("res://scenes/district_zero_p1a.tscn").instantiate()
	root.add_child(gate)
	for i in 4:
		await process_frame
	await physics_frame
	var terrain: MeshInstance3D = gate.world.get_node("FrozenHeightfieldVisual")
	var arrays := terrain.mesh.surface_get_arrays(0)
	var vertices: PackedVector3Array = arrays[Mesh.ARRAY_VERTEX]
	var normals: PackedVector3Array = arrays[Mesh.ARRAY_NORMAL]
	var indices: PackedInt32Array = arrays[Mesh.ARRAY_INDEX]
	var shape: ConcavePolygonShape3D = gate.world.get_node("FrozenHeightfieldCollision").get_child(0).shape
	var identity := {"vertices":digest(vertices.to_byte_array()),"normals":digest(normals.to_byte_array()),"indices":digest(indices.to_byte_array()),"collision_faces":digest(shape.get_faces().to_byte_array()),"shapes":gate.world.find_children("*","CollisionShape3D",true,false).size(),"geometry_nodes":gate.world.find_children("*","GeometryInstance3D",true,false).size()}
	if not baseline:
		var reference: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(args[args.find("--reference")+1]))
		var same := true
		for key in identity:
			if key in ["shapes","geometry_nodes"]:
				same = same and int(identity[key]) == int(reference.identity[key])
			else:
				same = same and identity[key] == reference.identity[key]
		check("EXACT_TERRAIN_AND_COLLISION_HASHES",same,identity)
		check("ONE_EXISTING_TERRAIN_SURFACE",terrain.mesh.get_surface_count()==1)
		var uv: PackedVector2Array = arrays[Mesh.ARRAY_TEX_UV]
		check("WORLD_ALIGNED_UV_CORNERS",uv[0]==Vector2.ZERO and uv[440]==Vector2(1,0) and uv[-1]==Vector2.ONE)
		var finite := true
		for v in uv:
			finite = finite and is_finite(v.x) and is_finite(v.y) and v.x>=0 and v.x<=1 and v.y>=0 and v.y<=1
		check("FINITE_BOUNDED_UVS",finite)
		var material: StandardMaterial3D = terrain.mesh.surface_get_material(0)
		check("NATIVE_OPAQUE_MATERIAL",material.transparency==BaseMaterial3D.TRANSPARENCY_DISABLED and material.next_pass==null and not material.vertex_color_use_as_albedo)
		check("CLAMPED_MIP_FILTER",not material.texture_repeat and material.texture_filter==BaseMaterial3D.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS)
		var albedo: Image = material.albedo_texture.get_image()
		var rough: Image = material.roughness_texture.get_image()
		check("MATCHED_ATLAS_DIMENSIONS",albedo.get_size()==Vector2i(2048,2048) and rough.get_size()==albedo.get_size())
		check("OFFLINE_COMPLETE_MIPMAPS",albedo.has_mipmaps() and rough.has_mipmaps() and albedo.get_mipmap_count()==11 and rough.get_mipmap_count()==11)
		check("EXPLICIT_GPU_FORMATS",albedo.get_format()==Image.FORMAT_RGBA8 and rough.get_format()==Image.FORMAT_R8)
		check("TEXTURE_MEMORY_CAP",albedo.get_data_size()+rough.get_data_size()<=32*1024*1024,albedo.get_data_size()+rough.get_data_size())
		var index: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://presentation/generated/quiet_surfaces_index.json"))
		for d in index.details:
			var clear := true
			for v in d.polygon:
				var hit := gate.get_world_3d().direct_space_state.intersect_ray(PhysicsRayQueryParameters3D.create(Vector3(v[0],50,v[1]),Vector3(v[0],-5,v[1]),1))
				clear = clear and not hit.is_empty() and hit.collider.get_meta("source_geometry_id","")=="HEIGHTFIELD_SUPPORT"
			check("FLUSH_DETAIL_ON_EXPOSED_GROUND:"+str(checks.size()),clear,d)
	var result := {"status":"PASS","check_count":checks.size(),"checks":checks,"identity":identity}
	for c in checks:
		if not c.pass:result.status="FAIL"
	FileAccess.open(out,FileAccess.WRITE).store_string(JSON.stringify(result,"  "))
	print(result.status," surface checks ",checks.size())
	quit(0 if result.status=="PASS" else 1)
