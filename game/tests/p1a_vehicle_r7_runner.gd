extends SceneTree

const MAIN_SCENE := preload("res://scenes/district_zero_p1a.tscn")
const EXACT_ENGINE := "4.7.1.stable.official.a13da4feb"

var checks: Array[Dictionary] = []
var failures: Array[String] = []


func _initialize() -> void:
	call_deferred("_run")


func _run() -> void:
	_record("EXACT_ENGINE", _engine_identity() == EXACT_ENGINE, _engine_identity())
	var gate := MAIN_SCENE.instantiate() as P1AWorldGate
	root.add_child(gate)
	await process_frame
	gate.craft.set_physics_process(false)
	gate.telemetry.set_physics_process(false)

	_record("MENU_DEFAULT_CLOSED", not gate.menu_panel.visible)
	_record("DEBUG_DEFAULT_CLOSED", not gate.debug_panel.visible)
	var debug_event := InputEventAction.new()
	debug_event.action = "debug_overlay"
	debug_event.pressed = true
	gate._unhandled_input(debug_event)
	_record("DEBUG_ACTION_OPENS_PANEL", gate.debug_panel.visible and gate.debug_label.visible)
	gate._unhandled_input(debug_event)
	_record("DEBUG_ACTION_CLOSES_PANEL", not gate.debug_panel.visible)
	_record("PAUSE_DEFAULT_CLOSED", not gate.pause_panel.visible)
	_record("R7_STATUS_IDENTITY", gate.status_label.text.contains("P1A VEHICLE R7") and gate.status_label.text.contains("WORLD v1.2.3"), gate.status_label.text)
	var identity := gate.get_node("UI/DiagnosticIdentityPanel/Label") as Label
	_record("R7_FOOTER_IDENTITY", identity.text == "P1A VEHICLE INTEGRATION R7 · OWNER REVIEW", identity.text)
	_record("DEFAULT_ROUTE_HIGHLIGHT", gate.map.highlighted_route_ids == ["A0"], gate.map.highlighted_route_ids)

	var menu_event := InputEventAction.new()
	menu_event.action = "diagnostic_menu"
	menu_event.pressed = true
	gate._unhandled_input(menu_event)
	_record("MENU_ACTION_OPENS", gate.menu_panel.visible)
	gate._unhandled_input(menu_event)
	_record("MENU_ACTION_CLOSES", not gate.menu_panel.visible)

	paused = true
	await process_frame
	_record("PAUSE_PANEL_VISIBLE_WHEN_PAUSED", gate.pause_panel.visible)
	paused = false
	await process_frame
	_record("PAUSE_PANEL_HIDDEN_AFTER_RESUME", not gate.pause_panel.visible)

	var environment := (gate.get_node("WorldEnvironment") as WorldEnvironment).environment
	_record("PROCEDURAL_SKY_ACTIVE", environment.background_mode == Environment.BG_SKY and environment.sky != null)
	_record("FOG_REMAINS_DISABLED", not environment.fog_enabled)
	var sun := gate.get_node("Sun") as DirectionalLight3D
	_record("SUN_PRESENTATION_FROZEN", sun.rotation_degrees.is_equal_approx(Vector3(-48.0, -32.0, 0.0)) and is_equal_approx(sun.light_energy, 1.1) and sun.shadow_enabled)

	var marker_count := 0
	var marker_positions_match := true
	var marker_meshes_are_bounded := true
	for node_id_value in gate.data.manifest.nodes:
		var node_id := String(node_id_value)
		var marker := gate.world.get_node_or_null("%s_Marker" % node_id) as MeshInstance3D
		if marker == null:
			marker_positions_match = false
			continue
		marker_count += 1
		var record: Dictionary = gate.data.manifest.nodes[node_id]
		var expected := Vector3(float(record.xz_m[0]), float(record.elevation_m) + 0.12, float(record.xz_m[1]))
		marker_positions_match = marker_positions_match and marker.position.is_equal_approx(expected)
		marker_meshes_are_bounded = marker_meshes_are_bounded and marker.mesh is ArrayMesh and marker.mesh.get_faces().size() == 360
		var material := marker.mesh.surface_get_material(0) as StandardMaterial3D
		marker_meshes_are_bounded = marker_meshes_are_bounded and material != null and material.cull_mode == BaseMaterial3D.CULL_DISABLED
	_record("NODE_MARKER_COUNT_FROZEN", marker_count == gate.data.manifest.nodes.size(), {"observed": marker_count, "expected": gate.data.manifest.nodes.size()})
	_record("NODE_MARKER_POSITIONS_FROZEN", marker_positions_match)
	_record("NODE_MARKER_RING_CENTER_MESH", marker_meshes_are_bounded)

	var result := {
		"schema": "district_zero.p1a.vehicle_r7_behavior.v1",
		"status": "PASS" if failures.is_empty() else "FAIL",
		"engine_identity": _engine_identity(),
		"checks": checks,
		"failure_count": failures.size(),
		"failures": failures,
	}
	print("P1A_VEHICLE_R7_RESULT " + JSON.stringify(result))
	gate.queue_free()
	await process_frame
	quit(0 if failures.is_empty() else 1)


func _record(id: String, passed: bool, detail = null) -> void:
	checks.append({"id": id, "status": "PASS" if passed else "FAIL", "detail": detail})
	if not passed:
		failures.append(id)


func _engine_identity() -> String:
	var info := Engine.get_version_info()
	return "%d.%d.%d.%s.%s.%s" % [
		int(info.get("major", 0)), int(info.get("minor", 0)), int(info.get("patch", 0)),
		String(info.get("status", "")), String(info.get("build", "")),
		String(info.get("hash", "")).substr(0, 9),
	]
