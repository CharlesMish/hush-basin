extends SceneTree

const MAIN_SCENE := preload("res://scenes/district_zero_p1a.tscn")


func _initialize() -> void:
	call_deferred("_run")


func _run() -> void:
	var gate := MAIN_SCENE.instantiate() as P1AWorldGate
	root.add_child(gate)
	await process_frame
	gate.craft.set_physics_process(false)
	gate.telemetry.set_physics_process(false)
	var cases := [
		{"id": "A1_GW", "craft_position": Vector3(-170.0, 1.55, 35.0), "yaw": -0.045422, "screen": Vector2(0.47 * 1280.0, 0.83 * 720.0), "marker": "GW_Marker"},
		{"id": "FREE_MRK", "craft_position": Vector3(0.0, 1.5713321685791, 20.0), "yaw": -1.989022, "screen": Vector2(0.5 * 1280.0, 0.71 * 720.0), "marker": "MRK_Marker"},
	]
	var records := []
	for case in cases:
		gate.craft.global_transform = Transform3D(Basis.IDENTITY.rotated(Vector3.UP, float(case.yaw)), case.craft_position)
		gate.craft.fold_amount = 1.0 if String(case.id).begins_with("A1") else 0.0
		gate.camera_rig.snap_to_target()
		await process_frame
		var camera := gate.get_node("CameraRig/Camera") as Camera3D
		var marker := gate.world.get_node(String(case.marker)) as MeshInstance3D
		var origin := camera.project_ray_origin(case.screen)
		var direction := camera.project_ray_normal(case.screen).normalized()
		var distance_along := (marker.global_position.y - origin.y) / direction.y
		var point := origin + direction * distance_along
		records.append({"id": case.id, "marker": case.marker, "point": [point.x, point.y, point.z], "marker_position": [marker.global_position.x, marker.global_position.y, marker.global_position.z], "radial_distance_m": Vector2(point.x - marker.global_position.x, point.z - marker.global_position.z).length()})
	print("P1A_POLISH_MARKER_RAY_RESULT " + JSON.stringify({"records": records}))
	gate.queue_free()
	await process_frame
	quit(0)
