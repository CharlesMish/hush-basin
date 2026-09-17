extends Node
## Shared native/Web integration lane. Driven completion uses input actions only;
## separate synthetic placements deliberately isolate terminal/reset predicates.
signal finished(result: Dictionary)
signal tail
var checks: Dictionary = {}
var job: Node
var craft: CraftController
var gate: P1AWorldGate
var frames: Array = []
var capture_dir := ""
var clip_frames := false
var game: Node

func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	process_physics_priority = 1000
	call_deferred("run")

func _physics_process(_delta: float) -> void:
	tail.emit()

func ticks(count: int) -> void:
	for i in count:
		await tail

func key(code: Key) -> void:
	var event := InputEventKey.new()
	event.physical_keycode = code
	event.keycode = code
	event.pressed = true
	get_viewport().push_input(event)
	event = event.duplicate()
	event.pressed = false
	get_viewport().push_input(event)

func capture(id: String) -> void:
	if capture_dir.is_empty() or DisplayServer.get_name()=="headless":
		return
	await get_tree().process_frame
	await RenderingServer.frame_post_draw
	get_viewport().get_texture().get_image().save_png(capture_dir.path_join(id+".png"))

func run() -> void:
	game = load("res://scenes/district_zero_courier.tscn").instantiate()
	add_child(game)
	await get_tree().process_frame
	await get_tree().process_frame
	job = game.get_node("CourierLayer")
	gate = game.get_node("DistrictZeroP1A")
	craft = gate.craft
	await ticks(90)
	checks["starts_free_at_authoritative_market"] = job.initialized and job.state=="FREE_ROAM" and job.can_dispatch() and job._xz().distance_to(P1AWorldData.xz(gate.data.manifest.destination_pads.MRK.center_xz_m))<0.1
	await capture("01_free_roam")
	key(KEY_E)
	checks["dispatch_fresh_edge"] = job.state=="DISPATCH" and get_tree().paused
	await capture("02_dispatch")
	var before := craft.global_transform
	await ticks(30)
	checks["dispatch_freezes_craft"] = craft.global_transform==before and job.elapsed==0
	Input.action_press("throttle")
	key(KEY_ENTER)
	await ticks(10)
	checks["accept_waits_for_neutral"] = job.state=="WAIT_NEUTRAL" and craft.global_transform==before
	Input.action_release("throttle")
	await ticks(10)
	checks["accept_active_no_teleport"] = job.state=="ACTIVE" and craft.global_position.distance_to(before.origin)<0.1
	var weather: Node = gate.get_node("WarmOvercastWeather")
	key(KEY_ESCAPE)
	var clock: float = job.elapsed
	print("PAUSE_DIAGNOSTIC start state=",job.state," paused=",get_tree().paused," clock=",clock)
	# Finish the process batch already in flight when the test injects Escape.
	await get_tree().process_frame
	var age: float = weather.active_time
	await ticks(30)
	print("PAUSE_DIAGNOSTIC end state=",job.state," paused=",get_tree().paused," clock=",job.elapsed," weather=",age," → ",weather.active_time)
	checks["pause_stops_clock"] = job.state=="PAUSED" and job.elapsed==clock
	checks["pause_stops_weather"] = weather.active_time==age and not weather.rain.can_process()
	key(KEY_ESCAPE)
	await ticks(10)
	checks["resume_retains_parcel"] = job.state=="ACTIVE" and job.cargo.condition_units==1000
	# Normal-input direct open-yard route. No position/velocity writes from
	# acceptance through completion. Spread handles alignment; Drive mid-route.
	var starting_resets := craft.reset_count
	for tick in 2400:
		if job.state!="ACTIVE":
			break
		var displacement: Vector2 = job.destination-job._xz()
		var target_yaw := atan2(-displacement.x,-displacement.y)
		var error := wrapf(target_yaw-craft.rotation.y,-PI,PI)
		var speed := craft.velocity.length()
		var distance := displacement.length()
		var drive := distance>55 and distance<105 and absf(error)<0.10
		var desired := 22.0 if drive else 10.0
		if distance<24:
			desired = maxf(0,(distance-2)*0.40)
		Input.action_press("steer_right",clampf(-error*2,-0.0,1))
		Input.action_press("steer_left",clampf(error*2,0,1))
		if drive: Input.action_press("transform")
		else: Input.action_release("transform")
		if speed<desired and absf(error)<0.8:
			Input.action_press("throttle")
			Input.action_release("brake")
		else:
			Input.action_release("throttle")
			Input.action_press("brake")
		await tail
		if tick%30==0:
			frames.append({"tick":tick,"p":[craft.global_position.x,craft.global_position.y,craft.global_position.z],"speed":speed,"condition":job.cargo.condition_units,"state":job.state,"distance":distance})
		if tick==120: await capture("03_active")
		if clip_frames and tick%4==0: await capture("drive_%04d" % (tick/4))
	release()
	checks["normal_input_market_depot_delivery"] = job.state=="RESULTS" and job.last_result.get("delivered",false) and craft.reset_count==starting_resets
	checks["clean_route_no_cargo_loss"] = job.cargo.condition_units==1000
	if job.state!="RESULTS":
		job._finish(false,"Diagnostic route did not complete")
	await capture("04_results")
	var frozen := JSON.stringify(job.last_result)
	before = craft.global_transform
	var velocity := craft.velocity
	await ticks(45)
	checks["terminal_evidence_immutable"] = job.last_result.is_read_only() and JSON.stringify(job.last_result)==frozen and craft.global_transform==before
	key(KEY_ENTER)
	checks["continue_does_not_write_pose_or_velocity"] = craft.global_transform==before and craft.velocity==velocity
	await ticks(5)
	checks["continue_free_roam_at_depot"] = job.state=="FREE_ROAM" and job._xz().distance_to(job.destination)<job.destination_radius
	await capture("05_depot_free_roam")
	# Synthetic initial placements below test guards, not route completion.
	await reset_at(job.origin)
	key(KEY_E)
	key(KEY_ENTER)
	await ticks(6)
	job.cargo.condition_units = 0
	job.elapsed = 3600
	place_without_reset(job.destination)
	craft.velocity = Vector3(12,0,0)
	await ticks(1)
	checks["fast_crossing_not_delivery"] = job.state=="ACTIVE" and job.settle==0
	place_without_reset(job.destination)
	await ticks(10)
	checks["arrival_requires_settle"] = job.state=="ACTIVE"
	await ticks(70)
	checks["zero_condition_and_slow_still_deliver"] = job.state=="RESULTS" and job.last_result.get("delivered",false) and job.last_result.condition_units==0 and job.last_result.elapsed>=3600
	key(KEY_ENTER)
	await ticks(6)
	await reset_at(job.origin)
	key(KEY_E)
	key(KEY_ENTER)
	await ticks(6)
	key(KEY_ESCAPE)
	var resets := craft.reset_count
	key(KEY_R)
	checks["paused_reset_cancels_once"] = craft.reset_count==resets+1 and job.state=="RESULTS" and not job.last_result.delivered
	key(KEY_ENTER)
	await ticks(10)
	checks["weather_restarts_after_paused_reset"] = weather.rain.emitting and not weather.reset_pending
	await reset_at(job.origin)
	key(KEY_E)
	key(KEY_ENTER)
	await ticks(6)
	craft.global_position.y = craft.tuning.fall_reset_y-10
	await ticks(3)
	checks["fall_reset_cancels_no_delivery"] = job.state=="RESULTS" and not job.last_result.delivered
	key(KEY_ENTER)
	await ticks(8)
	await reset_at(job.origin)
	key(KEY_E)
	key(KEY_ENTER)
	await ticks(6)
	gate.spawn_selected_tour()
	checks["diagnostic_relocation_cancels"] = job.state=="RESULTS" and not job.last_result.delivered
	var ok := true
	for value in checks.values(): ok = ok and value
	var result := {"status":"PASS" if ok else "FAIL","checks":checks,"driven_trace":frames,"scope":"One normal-input Market–Depot route plus explicit synthetic terminal/reset guards. No owner-feel or physical gamepad claim."}
	print("COURIER_SMOKE_RESULT "+JSON.stringify(result))
	finished.emit(result)

func release() -> void:
	for action in ["throttle","brake","steer_left","steer_right","transform","hop"]:
		Input.action_release(action)

func place_without_reset(point: Vector2) -> void:
	craft.global_position = Vector3(point.x,gate.data.terrain_height_at(point.x,point.y)+1.65,point.y)
	craft.velocity = Vector3.ZERO
	craft.reset_physics_interpolation()

func reset_at(point: Vector2) -> void:
	release()
	get_tree().paused = false
	craft.set_spawn_transform(Transform3D(Basis.IDENTITY,Vector3(point.x,gate.data.terrain_height_at(point.x,point.y)+1.65,point.y)))
	craft.reset_craft("test_initial_condition")
	await ticks(90)
