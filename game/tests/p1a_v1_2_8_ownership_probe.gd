extends SceneTree

## Disposable, exact-engine raster-owner probe.  This script never writes to
## the source project: every artifact is written beneath --output-dir.

const MAIN_SCENE := preload("res://scenes/district_zero_p1a.tscn")
const EXACT_ENGINE := "4.7.1.stable.official.a13da4feb"
const VIEWPORT := Vector2i(1280, 720)
const DECODE_MIN := Vector2i(218, 206)
const DECODE_MAX := Vector2i(294, 282)
const LOW := Color(0.03125, 0.03125, 0.03125, 1.0)
const HIGH := Color(0.96875, 0.96875, 0.96875, 1.0)

var output_dir := ""


func _initialize() -> void:
	call_deferred("_run")


func _run() -> void:
	output_dir = _arg("--output-dir")
	if output_dir.is_empty():
		_finish({"status":"BLOCKED/NOT TESTABLE — HARNESS", "blocker":"--output-dir required"}, 2)
		return
	DirAccess.make_dir_recursive_absolute(output_dir)
	var engine := _engine_identity()
	if engine != EXACT_ENGINE:
		_finish({"status":"BLOCKED/NOT TESTABLE — EXACT ENGINE", "required":EXACT_ENGINE, "observed":engine}, 2)
		return

	var gate := MAIN_SCENE.instantiate() as P1AWorldGate
	get_root().add_child(gate)
	await process_frame
	gate.craft.set_physics_process(false)
	gate.telemetry.set_physics_process(false)
	gate.get_node("UI").visible = false
	gate.craft.velocity = Vector3.ZERO
	gate.craft.clear_pending_hop()
	gate.craft.global_transform = Transform3D(Basis.IDENTITY.rotated(Vector3.UP, -0.045422), Vector3(-170.0, 1.55, 35.0))
	gate.craft.fold_amount = 1.0
	gate.craft.reset_physics_interpolation()
	gate.camera_rig.snap_to_target()
	await process_frame
	await process_frame

	var camera := gate.get_node("CameraRig/Camera") as Camera3D
	var instances: Array[MeshInstance3D] = []
	_collect_meshes(gate.world, instances)
	instances.sort_custom(func(a: MeshInstance3D, b: MeshInstance3D) -> bool: return String(a.get_path()) < String(b.get_path()))
	var owners: Array = []
	var overrides: Array[BaseMaterial3D] = []
	for index in instances.size():
		var instance := instances[index]
		var active := instance.get_active_material(0)
		var material: BaseMaterial3D
		if active is BaseMaterial3D:
			material = (active as BaseMaterial3D).duplicate(true) as BaseMaterial3D
		else:
			material = StandardMaterial3D.new()
		material.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
		material.albedo_color = LOW
		instance.material_override = material
		overrides.append(material)
		owners.append({
			"owner_index": index,
			"render_node": String(instance.get_path()),
			"source_geometry_id": _source_id(gate.world, instance),
			"mesh_surface_count": instance.mesh.get_surface_count() if instance.mesh != null else 0,
			"visible": instance.visible,
		})

	await process_frame
	await process_frame
	var low_name := "a1-owner-low-reference.png"
	_save_viewport(low_name)
	for index in instances.size():
		overrides[index].albedo_color = HIGH
		await process_frame
		await process_frame
		_save_viewport("a1-owner-high-%03d.png" % index)
		overrides[index].albedo_color = LOW
	await process_frame
	await process_frame

	var ray_grid := {}
	for y in range(DECODE_MIN.y, DECODE_MAX.y + 1):
		for x in range(DECODE_MIN.x, DECODE_MAX.x + 1):
			var key := "%d,%d" % [x, y]
			ray_grid[key] = _physics_ray(gate, camera, Vector2(float(x) + 0.5, float(y) + 0.5))
	var supplemental := {}
	for point in [Vector2(256.5,244.5), Vector2(252.5,240.5), Vector2(260.5,240.5), Vector2(252.5,248.5), Vector2(260.5,248.5), Vector2(256.0,244.8)]:
		supplemental["%.3f,%.3f" % [point.x, point.y]] = _physics_ray(gate, camera, point)

	var cp := camera.global_position
	var camera_record := {
		"global_position_xyz_m":[cp.x,cp.y,cp.z],
		"global_transform":_transform(camera.global_transform),
		"projection":"PERSPECTIVE" if camera.projection == Camera3D.PROJECTION_PERSPECTIVE else str(camera.projection),
		"fov_degrees":camera.fov,
		"near_m":camera.near,
		"far_m":camera.far,
		"viewport_px":[VIEWPORT.x,VIEWPORT.y],
	}
	var result := {
		"schema":"district_zero.p1a.v1_2_8.ownership_probe_result.v1",
		"status":"PASS",
		"engine_identity":engine,
		"renderer":RenderingServer.get_current_rendering_method(),
		"camera":camera_record,
		"decode_bounds_inclusive":{"x":[DECODE_MIN.x,DECODE_MAX.x],"y":[DECODE_MIN.y,DECODE_MAX.y]},
		"low_reference":low_name,
		"owners":owners,
		"owner_count":owners.size(),
		"high_pass_pattern":"a1-owner-high-%03d.png",
		"ray_grid":ray_grid,
		"supplemental_rays":supplemental,
		"frame_waits_per_capture":2,
		"human_attempts_consumed":0,
	}
	_finish(result, 0)


func _collect_meshes(node: Node, out: Array[MeshInstance3D]) -> void:
	for child in node.get_children():
		if child is MeshInstance3D:
			var instance := child as MeshInstance3D
			if instance.visible and instance.mesh != null:
				out.append(instance)
		_collect_meshes(child, out)


func _source_id(world: Node3D, instance: MeshInstance3D):
	var name := String(instance.name)
	if name == "FrozenHeightfieldVisual":
		return "HEIGHTFIELD_SUPPORT"
	if name.ends_with("_Visual"):
		var collision_name := name.trim_suffix("_Visual") + "_Collision"
		var collision := world.get_node_or_null(collision_name)
		if collision != null and collision.has_meta("source_geometry_id"):
			return String(collision.get_meta("source_geometry_id"))
	return null


func _physics_ray(gate: P1AWorldGate, camera: Camera3D, screen: Vector2) -> Dictionary:
	var origin := camera.project_ray_origin(screen)
	var direction := camera.project_ray_normal(screen).normalized()
	var endpoint := origin + direction * camera.far
	var query := PhysicsRayQueryParameters3D.create(origin, endpoint)
	query.exclude = [gate.craft.get_rid()]
	query.hit_from_inside = true
	var hit := gate.get_world_3d().direct_space_state.intersect_ray(query)
	var collider_path = null
	var source_id = null
	var position = null
	var normal = null
	var distance = null
	if not hit.is_empty():
		var collider = hit.get("collider")
		if collider is Node:
			collider_path = String((collider as Node).get_path())
			if collider.has_meta("source_geometry_id"):
				source_id = String(collider.get_meta("source_geometry_id"))
		var p: Vector3 = hit.get("position", Vector3.ZERO)
		var n: Vector3 = hit.get("normal", Vector3.ZERO)
		position = [p.x,p.y,p.z]
		normal = [n.x,n.y,n.z]
		distance = origin.distance_to(p)
	return {
		"screen_px":[screen.x,screen.y],
		"origin":[origin.x,origin.y,origin.z],
		"direction":[direction.x,direction.y,direction.z],
		"physics_hit":not hit.is_empty(),
		"collision_node":collider_path,
		"source_geometry_id":source_id,
		"shape_index":int(hit.get("shape", -1)),
		"face_index":int(hit.get("face_index", -1)),
		"position":position,
		"normal":normal,
		"distance":distance,
	}


func _save_viewport(filename: String) -> void:
	var image := get_root().get_viewport().get_texture().get_image()
	image.save_png(output_dir.path_join(filename))


func _transform(value: Transform3D) -> Dictionary:
	return {
		"basis_x":[value.basis.x.x,value.basis.x.y,value.basis.x.z],
		"basis_y":[value.basis.y.x,value.basis.y.y,value.basis.y.z],
		"basis_z":[value.basis.z.x,value.basis.z.y,value.basis.z.z],
		"origin":[value.origin.x,value.origin.y,value.origin.z],
	}


func _engine_identity() -> String:
	var info := Engine.get_version_info()
	return "%d.%d.%d.%s.%s.%s" % [int(info.get("major",0)),int(info.get("minor",0)),int(info.get("patch",0)),String(info.get("status","")),String(info.get("build","")),String(info.get("hash","")).substr(0,9)]


func _arg(name: String) -> String:
	var args := OS.get_cmdline_user_args()
	for i in args.size():
		if args[i] == name and i + 1 < args.size():
			return args[i + 1]
	return ""


func _finish(value: Dictionary, code: int) -> void:
	if not output_dir.is_empty():
		var file := FileAccess.open(output_dir.path_join("ownership_probe_result.json"), FileAccess.WRITE)
		if file:
			file.store_string(JSON.stringify(value, "  ") + "\n")
			file.close()
	# The complete result is the checksummed file.  Keep stdout compact so a
	# 5,929-ray grid does not obscure process/evidence diagnostics.
	print(JSON.stringify({
		"schema":value.get("schema"),
		"status":value.get("status"),
		"engine_identity":value.get("engine_identity"),
		"owner_count":value.get("owner_count"),
		"human_attempts_consumed":value.get("human_attempts_consumed", 0),
	}))
	quit(code)
