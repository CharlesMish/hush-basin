extends SceneTree

class Fence:
	extends Node
	signal tail
	func _ready() -> void:
		process_physics_priority = 1000
	func _physics_process(_delta: float) -> void:
		tail.emit()

var gate: P1AWorldGate
var craft: CraftController
var fence: Fence
var checks: Array = []
var traces: Array = []
var failures: Array = []
var result_path := ""

func _initialize() -> void:
	call_deferred("run")

func check(id: String, value: bool, detail: Variant = null) -> void:
	checks.append({"id": id, "pass": value, "detail": detail})
	if not value:
		failures.append(id)

func release() -> void:
	for a in ["throttle", "brake", "steer_left", "steer_right", "transform", "hop"]:
		Input.action_release(a)

func settle(at: Vector2, toward: Vector2) -> void:
	release()
	var direction := (toward - at).normalized()
	var yaw := atan2(-direction.x, -direction.y)
	var position := Vector3(at.x, gate.data.terrain_height_at(at.x, at.y) + 1.65, at.y)
	craft.set_spawn_transform(Transform3D(Basis(Vector3.UP, yaw), position))
	craft.reset_craft("world-polish-test")
	gate.camera_rig.snap_to_target()
	for i in 45:
		await fence.tail

func run() -> void:
	var args := OS.get_cmdline_user_args()
	result_path = args[args.find("--result") + 1]
	gate = load("res://scenes/district_zero_p1a.tscn").instantiate()
	root.add_child(gate)
	fence = Fence.new()
	root.add_child(fence)
	await process_frame
	craft = gate.craft
	check("WORLD_IDENTITY", gate.data.AUTHORITY_VERSION == "world-polish-v1")
	check("VISIBLE_SUCCESSOR_IDENTITY", String((gate.diagnostic_identity_panel.get_node("Label") as Label).text) == "QUIET SURFACES · LIGHT DRIZZLE · OWNER REVIEW")
	check("YARDS", gate.data.polish.yards.size() == 3)
	for id in ["QRY", "RLY", "DEP", "MRK", "CLN", "WRK"]:
		var p := P1AWorldData.xz(gate.data.manifest.nodes[id].xz_m)
		await settle(p, p + Vector2(0, -10))
		check("SPAWN_SUPPORT:" + id, craft.probe_hit_count == 3 and craft.impact_count == 0)
	for yard in gate.data.polish.yards:
		var center := P1AWorldData.xz(yard.clear_square_center)
		var clear := true
		var max_error := 0.0
		for dx in range(-20, 21, 4):
			for dz in range(-20, 21, 4):
				var p := center + Vector2(dx, dz)
				var h := gate.data.terrain_height_at(p.x, p.y)
				var query := PhysicsRayQueryParameters3D.create(Vector3(p.x, 15, p.y), Vector3(p.x, -5, p.y), 1, [craft.get_rid()])
				var hit := gate.get_world_3d().direct_space_state.intersect_ray(query)
				if hit.is_empty() or hit.collider.get_meta("source_geometry_id", "") != "HEIGHTFIELD_SUPPORT":
					clear = false
				else:
					max_error = maxf(max_error, absf(hit.position.y - h))
		check("SQUARE_PHYSICS:" + yard.id, clear and max_error < 0.02, max_error)
		for entrance_index in yard.entrances.size():
			var entrance: Array = yard.entrances[entrance_index]
			for drive in [false, true]:
				await drive_connection(yard.id, entrance_index, entrance, drive)
	await wall_and_controls()
	# Native map mapping is north-up: Relay must appear above Market.
	check("MAP_NORTH_UP", gate.map._world_to_map(Vector2(0, -210)).y < gate.map._world_to_map(Vector2(0, 20)).y)
	var visual := gate.world.get_node("WorldPolishArchitecture")
	check("DETAILS_NO_COLLISION", visual.find_children("*", "CollisionObject3D", true, false).is_empty())
	var bands := visual.get_node("RetainingWallBands") as MeshInstance3D
	var band_points: PackedVector3Array = bands.mesh.surface_get_arrays(0)[Mesh.ARRAY_VERTEX]
	var finite_bands := not band_points.is_empty()
	for point in band_points:
		finite_bands = finite_bands and point.is_finite()
	var eligible := 0
	for edge in gate.data.polish.wall_edges:
		if preload("res://scripts/world_polish_presentation.gd").drawable_edge(edge):
			eligible += 1
	check("CONTINUOUS_WALL_BANDS", finite_bands and band_points.size() == eligible * 12, {"vertices": band_points.size(), "eligible_edges": eligible, "omitted_edges": gate.data.polish.wall_edges.size() - eligible})
	release()
	gate.queue_free()
	await process_frame
	await shortcut_finish()
	var f := FileAccess.open(result_path, FileAccess.WRITE)
	var result := {"status": "PASS" if failures.is_empty() else "FAIL", "checks": checks, "traces": traces, "failures": failures, "engine": Engine.get_version_info()}
	f.store_string(JSON.stringify(result, "  "))
	print("WORLD_POLISH_RUNTIME ", JSON.stringify({"checks": checks.size(), "failures": failures}))
	fence.queue_free()
	await process_frame
	quit(0 if failures.is_empty() else 1)

func drive_connection(id: String, index: int, points: Array, drive: bool) -> void:
	var a := P1AWorldData.xz(points[0])
	var b := P1AWorldData.xz(points[1])
	await settle(a, b)
	var reset_count := craft.reset_count
	Input.action_press("throttle")
	if drive:
		Input.action_press("transform")
	var direction := (b - a).normalized()
	var peak := 0.0
	var progress := 0.0
	var lateral := 0.0
	var unsupported := 0
	var used_ticks := 0
	var contacts: Array = []
	for tick in 600:
		await fence.tail
		used_ticks = tick + 1
		var p := Vector2(craft.global_position.x, craft.global_position.z)
		progress = (p - a).dot(direction)
		lateral = maxf(lateral, absf((p - a).cross(direction)))
		peak = maxf(peak, craft.powered_surface_speed)
		if craft.get_slide_collision_count() > 0 and contacts.size() < 16:
			var contact := craft.get_slide_collision(0)
			contacts.append({"position": [p.x, craft.global_position.y, p.y], "source": contact.get_collider().get_meta("source_geometry_id", ""), "normal": [contact.get_normal().x, contact.get_normal().y, contact.get_normal().z]})
		if craft.probe_hit_count == 0:
			unsupported += 1
		if progress >= a.distance_to(b) or craft.reset_count != reset_count:
			break
	var record := {"id": id, "entrance": index, "drive": drive, "ticks": used_ticks, "progress_m": progress, "distance_m": a.distance_to(b), "peak_mps": peak, "max_lateral_m": lateral, "impacts": craft.impact_count, "unsupported_ticks": unsupported, "resets": craft.reset_count - reset_count, "contacts": contacts}
	traces.append(record)
	if DisplayServer.get_name() != "headless":
		await RenderingServer.frame_post_draw
		root.get_texture().get_image().save_png(result_path.get_base_dir().path_join("traverse_%s_%d_%s.png" % [id, index, drive]))
	check("INPUT_TRAVERSE:%s:%d:%s" % [id, index, drive], progress >= a.distance_to(b) and lateral < 3.0 and craft.impact_count == 0 and craft.reset_count == reset_count and unsupported == 0, record)
	release()

func wall_and_controls() -> void:
	await settle(Vector2(-245, 20), Vector2(-310, 20))
	Input.action_press("throttle")
	Input.action_press("transform")
	for i in 270:
		await fence.tail
	check("VISIBLE_OUTER_CONTACT", craft.impact_count > 0 and craft.global_position.x > -315.0, craft.global_position.x)
	var pivot := craft.global_position + Vector3.UP
	var blocked := gate.camera_rig._resolve_obstructed_position(pivot, Vector3(-325, pivot.y, pivot.z))
	check("CAMERA_OBSTRUCTION", blocked.x > -315.0, blocked.x)
	await settle(Vector2(-200, -10), Vector2(-150, -10))
	Input.action_press("throttle")
	Input.action_press("transform")
	for i in 100:
		await fence.tail
	Input.action_press("steer_right")
	for i in 45:
		await fence.tail
	check("STEERING_FINITE", craft.velocity.is_finite() and craft.powered_surface_speed < 38.5)
	release()
	var speed := craft.velocity.length()
	Input.action_press("brake")
	for i in 150:
		await fence.tail
	check("BRAKING", craft.velocity.length() < speed * 0.3)
	release()
	await settle(Vector2(-55, 50), Vector2(-55, 0))
	Input.action_press("hop")
	for i in 5:
		await fence.tail
	check("YARD_HOP", craft.hop_count == 1)
	release()
	for i in 180:
		await fence.tail
	check("HOP_LANDING", craft.probe_hit_count > 0 and craft.velocity.is_finite())

func shortcut_finish() -> void:
	var scene = load("res://scenes/district_zero_run.tscn").instantiate()
	root.add_child(scene)
	await process_frame
	await process_frame
	gate = scene.get_node("DistrictZeroP1A")
	craft = gate.craft
	var run_layer = scene.get_node("RunLayer")
	# Controlled initial condition for a new off-route finish approach. From GO
	# onward the shipped Run observer sees only normal input-driven movement.
	var a := Vector2(30, -175)
	var b := Vector2(0, -210)
	var direction := (b - a).normalized()
	var yaw := atan2(-direction.x, -direction.y)
	run_layer.run_start_transform = Transform3D(Basis(Vector3.UP, yaw), Vector3(a.x, gate.data.terrain_height_at(a.x, a.y) + 1.65, a.y))
	run_layer.start_attempt()
	for i in 150:
		await fence.tail
	check("SHORTCUT_READY", run_layer.state_name() == "LIVE")
	if DisplayServer.get_name() != "headless":
		await RenderingServer.frame_post_draw
		root.get_texture().get_image().save_png(result_path.get_base_dir().path_join("run_live.png"))
	Input.action_press("throttle")
	Input.action_press("transform")
	for i in 240:
		await fence.tail
		if run_layer.state_name() == "RESULTS":
			break
	check("INPUT_SHORTCUT_FINISH", run_layer.state_name() == "RESULTS" and craft.impact_count == 0, {"state": run_layer.state_name(), "impacts": craft.impact_count})
	release()
	if DisplayServer.get_name() != "headless":
		await RenderingServer.frame_post_draw
		root.get_texture().get_image().save_png(result_path.get_base_dir().path_join("run_results.png"))
	scene.queue_free()
	await process_frame
