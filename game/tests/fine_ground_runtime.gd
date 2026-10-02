extends SceneTree
## Fine Ground v1 native probe. Reports terrain/collision identity for matched
## baseline comparison, successor material/environment checks and, with a
## display, gameplay-camera captures for human review. Not an acceptance gate.

const VIEWS := [
	["L4_ROAD_EDGE", Vector2(-4.0, -158.0), Vector2(30.0, -170.0)],
	["R0_ROUGH_CUE", Vector2(62.0, -128.0), Vector2(70.0, -100.0)],
	["A1_ARTERIAL", Vector2(-120.0, -104.0), Vector2(-150.0, -80.0)],
	["MARKET_FRONTAGE", Vector2(35.0, -82.0), Vector2(35.0, -100.0)],
]

var checks: Array = []


func _initialize() -> void:
	call_deferred("run")


func check(id: String, ok: bool, detail: Variant = null) -> void:
	checks.append({"id": id, "pass": ok, "detail": detail})


func digest(bytes: PackedByteArray) -> String:
	var h := HashingContext.new()
	h.start(HashingContext.HASH_SHA256)
	h.update(bytes)
	return h.finish().hex_encode()


func run() -> void:
	var args := OS.get_cmdline_user_args()
	var out := args[args.find("--result") + 1]
	var successor := not args.has("--baseline")
	var capture_dir := args[args.find("--capture-dir") + 1] if args.has("--capture-dir") else ""
	var gate: P1AWorldGate = load("res://scenes/district_zero_p1a.tscn").instantiate()
	root.add_child(gate)
	for i in 4:
		await process_frame
	await physics_frame
	var terrain: MeshInstance3D = gate.world.get_node("FrozenHeightfieldVisual")
	var arrays := terrain.mesh.surface_get_arrays(0)
	var shape: ConcavePolygonShape3D = gate.world.get_node("FrozenHeightfieldCollision").get_child(0).shape
	var identity := {
		"vertices": digest((arrays[Mesh.ARRAY_VERTEX] as PackedVector3Array).to_byte_array()),
		"normals": digest((arrays[Mesh.ARRAY_NORMAL] as PackedVector3Array).to_byte_array()),
		"indices": digest((arrays[Mesh.ARRAY_INDEX] as PackedInt32Array).to_byte_array()),
		"uvs": digest((arrays[Mesh.ARRAY_TEX_UV] as PackedVector2Array).to_byte_array()),
		"collision_faces": digest(shape.get_faces().to_byte_array()),
		"shapes": gate.world.find_children("*", "CollisionShape3D", true, false).size(),
		"geometry_nodes": gate.world.find_children("*", "GeometryInstance3D", true, false).size(),
		"gate_children": gate.get_child_count(),
	}
	if successor:
		var fine: GDScript = load("res://scripts/fine_ground.gd")
		var cfg: Dictionary = fine.config()
		check("ONE_TERRAIN_SURFACE", terrain.mesh.get_surface_count() == 1)
		var material := terrain.mesh.surface_get_material(0) as ShaderMaterial
		check("SHADER_MATERIAL", material != null and material.shader != null and material.next_pass == null)
		if material != null:
			var uniforms := {}
			for u in material.shader.get_shader_uniform_list():
				uniforms[String(u.name)] = true
			var bound := true
			for key in cfg.shader:
				bound = bound and uniforms.has(key) and material.get_shader_parameter(key) != null
			check("CONFIG_UNIFORMS_BOUND", bound)
			var detail := (material.get_shader_parameter("detail_map") as Texture2D).get_image()
			check("DETAIL_256_RGBA8_MIPMAPPED", detail.get_size() == Vector2i(256, 256) and detail.get_format() == Image.FORMAT_RGBA8 and detail.has_mipmaps())
			var albedo := (material.get_shader_parameter("macro_albedo") as Texture2D).get_image()
			var rough := (material.get_shader_parameter("macro_roughness") as Texture2D).get_image()
			check("MACRO_MAPS_UNCHANGED_FORMAT", albedo.get_size() == Vector2i(2048, 2048) and albedo.get_mipmap_count() == 11 and rough.get_format() == Image.FORMAT_R8)
			check("TEXTURE_MEMORY_CAP", albedo.get_data_size() + rough.get_data_size() + detail.get_data_size() <= 32 * 1024 * 1024, albedo.get_data_size() + rough.get_data_size() + detail.get_data_size())
		var env: Environment = (gate.get_node("WorldEnvironment") as WorldEnvironment).environment
		var atmosphere: Dictionary = cfg.atmosphere
		check("SSAO_CONFIGURED", env.ssao_enabled == bool(atmosphere.ssao.enabled) and is_equal_approx(env.ssao_radius, float(atmosphere.ssao.radius)))
		check("FOG_CONFIGURED", env.fog_enabled == bool(atmosphere.fog.enabled) and is_equal_approx(env.fog_density, float(atmosphere.fog.density)) and is_equal_approx(env.fog_sky_affect, float(atmosphere.fog.sky_affect)))
		check("VIEWPORT_MSAA_CONFIGURED", int(gate.get_viewport().msaa_3d) == int(cfg.display.msaa_3d))
		check("ANISOTROPIC_16X", int(ProjectSettings.get_setting("rendering/textures/default_filters/anisotropic_filtering_level")) == 4)
	if capture_dir != "" and DisplayServer.get_name() != "headless":
		DirAccess.make_dir_recursive_absolute(capture_dir)
		var craft: CraftController = gate.craft
		for view in VIEWS:
			var at: Vector2 = view[1]
			var direction: Vector2 = (view[2] - at).normalized()
			var yaw := atan2(-direction.x, -direction.y)
			craft.set_spawn_transform(Transform3D(Basis(Vector3.UP, yaw), Vector3(at.x, gate.data.terrain_height_at(at.x, at.y) + 1.65, at.y)))
			craft.reset_craft("fine-ground-capture")
			gate.camera_rig.snap_to_target()
			for i in 45:
				await process_frame
			await RenderingServer.frame_post_draw
			var image := root.get_texture().get_image()
			image.save_png(capture_dir.path_join(String(view[0]) + ".png"))
			# Lower third is ground in every view: reject black, blown or
			# shader-fallback output without judging appearance.
			var sum := Vector3.ZERO
			var count := 0
			for y in range(int(image.get_height() * 2.0 / 3.0), image.get_height(), 8):
				for x in range(0, image.get_width(), 8):
					var c := image.get_pixel(x, y)
					sum += Vector3(c.r, c.g, c.b)
					count += 1
			var mean := sum / maxf(1.0, float(count))
			check("GROUND_PIXELS_PLAUSIBLE:" + String(view[0]), mean.x > 0.04 and mean.x < 0.95 and mean.y > 0.04 and mean.z < 0.95 and not (mean.x > 0.7 and mean.z > 0.7 and mean.y < 0.35), [mean.x, mean.y, mean.z])
	var result := {"status": "PASS", "successor": successor, "check_count": checks.size(), "checks": checks, "identity": identity}
	for c in checks:
		if not c.pass:
			result.status = "FAIL"
	FileAccess.open(out, FileAccess.WRITE).store_string(JSON.stringify(result, "  "))
	print(result.status, " fine ground checks ", checks.size())
	quit(0 if result.status == "PASS" else 1)
