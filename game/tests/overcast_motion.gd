extends SceneTree

class Fence:
	extends Node
	signal tail
	func _ready() -> void:
		process_physics_priority = 1000
	func _physics_process(_delta: float) -> void:
		tail.emit()

var out := ""
var capture_frames := false
var gate: P1AWorldGate
var fence: Fence
var records: Array = []
var measuring := false
var frame_times: Array = []
var prior := 0

func _initialize() -> void:
	call_deferred("run")

func _process(_delta: float) -> bool:
	var now := Time.get_ticks_usec()
	if measuring and prior > 0:
		frame_times.append(float(now - prior) / 1000.0)
	prior = now
	return false

func release() -> void:
	for a in ["throttle", "brake", "transform", "steer_right", "steer_left"]:
		Input.action_release(a)

func run() -> void:
	var args := OS.get_cmdline_user_args()
	out = args[args.find("--output") + 1]
	capture_frames = args.has("--capture")
	DirAccess.make_dir_recursive_absolute(out)
	gate = load("res://scenes/district_zero_p1a.tscn").instantiate()
	root.add_child(gate)
	fence = Fence.new()
	root.add_child(fence)
	await process_frame
	gate.get_node("UI").visible = false
	# Test-only A/B control: keep all resources and collider allocation equal,
	# then stop only weather processing/rendering in the disabled arm.
	if args.has("--weather-disabled"):
		var weather := gate.get_node("WarmOvercastWeather")
		weather.process_mode = Node.PROCESS_MODE_DISABLED
		weather.visible = false
	for yard in gate.data.polish.yards:
		var entrance: Array = yard.entrances[1]
		var a := P1AWorldData.xz(entrance[0])
		var b := P1AWorldData.xz(entrance[1])
		var direction := (b - a).normalized()
		await clip(String(yard.id), Vector3(a.x, gate.data.terrain_height_at(a.x, a.y) + 1.65, a.y), atan2(-direction.x, -direction.y), 0.0)
	for id in ["T02_WEST_SWEEP", "T03_EAST_SWEEP"]:
		for tour in gate.data.diagnostic.tours:
			if tour.id == id:
				var p: Array = tour.spawn_transform.position_xyz_m
				await clip(id, Vector3(p[0], p[1], p[2]), float(tour.spawn_transform.yaw_rad), 0.15 if id == "T02_WEST_SWEEP" else -0.15)
	var f := FileAccess.open(out.path_join("motion.json"), FileAccess.WRITE)
	f.store_string(JSON.stringify({"status": "PASS", "capture": capture_frames, "renderer": RenderingServer.get_current_rendering_method(), "size": [root.size.x, root.size.y], "records": records, "note": "Scripted normal inputs from controlled starts. Frame time measurements exclude image capture runs; not human play."}, "  "))
	release()
	gate.queue_free()
	fence.queue_free()
	await process_frame
	quit()

func clip(id: String, position: Vector3, yaw: float, steering: float) -> void:
	release()
	gate.craft.set_spawn_transform(Transform3D(Basis(Vector3.UP, yaw), position))
	gate.craft.reset_craft("weather-motion")
	gate.camera_rig.snap_to_target()
	for i in 90:
		await fence.tail
	var directory := out.path_join(id)
	if capture_frames:
		DirAccess.make_dir_recursive_absolute(directory)
	frame_times.clear()
	var frames := 0
	measuring = not capture_frames
	Input.action_press("throttle")
	Input.action_press("transform")
	if steering > 0:
		Input.action_press("steer_right", steering)
	elif steering < 0:
		Input.action_press("steer_left", -steering)
	var trace: Array = []
	for tick in 300:
		if tick == 150:
			release()
			Input.action_press("brake")
		await fence.tail
		var p := gate.craft.global_position
		var v := gate.craft.velocity
		trace.append([p.x, p.y, p.z, v.x, v.y, v.z, gate.craft.fold_amount])
		if capture_frames and tick % 4 == 0:
			await RenderingServer.frame_post_draw
			root.get_texture().get_image().save_jpg(directory.path_join("%04d.jpg" % frames), 0.92)
			frames += 1
	measuring = false
	frame_times.sort()
	records.append({"id": id, "frames": frames, "p95_ms": frame_times[int(frame_times.size() * 0.95)] if not frame_times.is_empty() else 0.0, "frame_times_ms": frame_times.duplicate(), "trace": trace, "impacts": gate.craft.impact_count, "reset_count": gate.craft.reset_count})
	release()
