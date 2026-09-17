extends Node
## One observer-owned job. The craft owns every movement decision.
const Rules = preload("res://scripts/courier/courier_rules.gd")
const Cargo = preload("res://scripts/courier/cargo_observer.gd")
const Brrr = preload("res://scripts/run/brrr_seed.gd")
const Hud = preload("res://scripts/courier/courier_hud.gd")
const MapCue = preload("res://scripts/run/run_map_overlay.gd")

var gate: P1AWorldGate
var craft: CraftController
var hud: CanvasLayer
var cue: Control
var cargo = Cargo.new()
var state := "FREE_ROAM"
var origin := Vector2.ZERO
var destination := Vector2.ZERO
var origin_radius := 0.0
var destination_radius := 0.0
var elapsed := 0.0
var brrr := 0.0
var streak := 0.0
var longest_streak := 0.0
var peak_speed := 0.0
var settle := 0.0
var last_result: Dictionary = {}
var initialized := false
var _last_hop := 0
var _resume_state := "FREE_ROAM"
var _neutral_frames := 0

func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	process_priority = 200
	process_physics_priority = 200
	_initialize()

func _initialize() -> void:
	await get_tree().process_frame
	gate = get_node("../DistrictZeroP1A") as P1AWorldGate
	craft = gate.craft
	var pads: Dictionary = gate.data.manifest.destination_pads
	origin = P1AWorldData.xz(pads[Rules.ORIGIN].center_xz_m)
	destination = P1AWorldData.xz(pads[Rules.DESTINATION].center_xz_m)
	origin_radius = float(pads[Rules.ORIGIN].inner_flat_radius_m)
	destination_radius = float(pads[Rules.DESTINATION].inner_flat_radius_m)
	hud = Hud.new()
	add_child(hud)
	hud.primary.connect(primary_action)
	hud.secondary.connect(close_dispatch)
	cue = MapCue.new()
	gate.map.add_child(cue)
	gate.status_label.get_parent().hide()
	gate.diagnostic_identity_panel.hide()
	gate.menu_panel.hide()
	gate.active_tour_id = ""
	var no_routes: Array[String] = []
	gate.map.set_highlighted_routes(no_routes)
	var direction := (destination-origin).normalized()
	var pose := Transform3D(Basis(Vector3.UP,atan2(-direction.x,-direction.y)),Vector3(origin.x,gate.data.terrain_height_at(origin.x,origin.y)+1.65,origin.y))
	craft.set_spawn_transform(pose)
	craft.reset_craft("courier_spawn")
	gate.camera_rig.snap_to_target()
	craft.reset_performed.connect(_on_reset)
	initialized = true
	print("COURIER_READY Market → Depot; geometry from destination_pads")

func _process(_delta: float) -> void:
	if not initialized:
		return
	gate.pause_panel.hide()
	if state == "WAIT_NEUTRAL":
		_neutral_frames = _neutral_frames+1 if inputs_neutral() else 0
		if _neutral_frames >= 2:
			state = _resume_state
			get_tree().paused = false
	var target := destination if state == "ACTIVE" or (state == "PAUSED" and _resume_state == "ACTIVE") else origin
	cue.configure(target,"DEP" if target == destination else "MRK")
	cue.visible = state != "RESULTS"
	hud.refresh(self)

func _input(event: InputEvent) -> void:
	if not initialized:
		return
	var fresh: bool = (event is InputEventKey and event.pressed and not event.echo) or (event is InputEventJoypadButton and event.pressed)
	var interact: bool = fresh and ((event is InputEventKey and (event.physical_keycode in [KEY_E,KEY_ENTER] or event.keycode in [KEY_E,KEY_ENTER])) or (event is InputEventJoypadButton and event.button_index == JOY_BUTTON_B))
	if interact:
		# Keep the historical diagnostic Enter binding while its menu is open.
		if gate.menu_panel.visible and state in ["FREE_ROAM","ACTIVE"]:
			return
		primary_action()
		get_viewport().set_input_as_handled()
		return
	if event.is_action_pressed("pause") and not (event is InputEventKey and event.echo):
		if state == "DISPATCH":
			close_dispatch()
		elif state == "PAUSED":
			_wait_for_neutral(_resume_state)
		elif state in ["FREE_ROAM","ACTIVE"]:
			_resume_state = state
			state = "PAUSED"
			craft.clear_pending_hop()
			get_tree().paused = true
		get_viewport().set_input_as_handled()
		return
	if state in ["DISPATCH","RESULTS","WAIT_NEUTRAL","PAUSED"]:
		# Reset remains available during a pause, but never leaks from Results.
		if state == "PAUSED" and event.is_action_pressed("reset"):
			craft.reset_craft("manual")
		get_viewport().set_input_as_handled()

func primary_action() -> void:
	match state:
		"FREE_ROAM":
			if can_dispatch():
				state = "DISPATCH"
				craft.clear_pending_hop()
				get_tree().paused = true
		"DISPATCH":
			elapsed = 0
			brrr = 0
			streak = 0
			longest_streak = 0
			peak_speed = 0
			settle = 0
			last_result = {}
			cargo.begin(craft)
			_last_hop = craft.hop_count
			_wait_for_neutral("ACTIVE")
		"RESULTS":
			# A future recovery anchor; this never writes the current transform.
			if last_result.get("delivered",false):
				craft.set_spawn_transform(craft.global_transform)
			_wait_for_neutral("FREE_ROAM")
		"PAUSED":
			_wait_for_neutral(_resume_state)

func close_dispatch() -> void:
	if state == "DISPATCH":
		_wait_for_neutral("FREE_ROAM")

func _wait_for_neutral(next_state: String) -> void:
	_resume_state = next_state
	state = "WAIT_NEUTRAL"
	craft.clear_pending_hop()
	_neutral_frames = 0
	get_tree().paused = true

func inputs_neutral() -> bool:
	for action in ["throttle","brake","steer_left","steer_right","transform","hop","reset","pause"]:
		if Input.get_action_strength(action)>0.01:
			return false
	if Input.is_physical_key_pressed(KEY_E) or Input.is_physical_key_pressed(KEY_ENTER) or Input.is_mouse_button_pressed(MOUSE_BUTTON_LEFT):
		return false
	for device in Input.get_connected_joypads():
		if Input.is_joy_button_pressed(device,JOY_BUTTON_B):
			return false
	return true

func can_dispatch() -> bool:
	return _xz().distance_to(origin)<=origin_radius and _supported() and craft.velocity.length()<=Rules.DISPATCH_SPEED

func _supported() -> bool:
	# Probes precede move_and_slide, so also reject upward/downward flight and
	# require current height within the existing support reacquisition range.
	var ground := gate.data.terrain_height_at(craft.global_position.x,craft.global_position.z)
	var height := craft.global_position.y-ground
	return craft.probe_hit_count>=2 and height>0 and height<=craft.tuning.support_reacquire_max_distance and absf(craft.velocity.dot(craft.support_normal))<=Rules.ARRIVAL_NORMAL_SPEED

func _physics_process(delta: float) -> void:
	if not initialized or get_tree().paused or state != "ACTIVE":
		return
	if craft.global_position.y < craft.tuning.fall_reset_y:
		return # Controller reset owns the next tick; cannot deliver in the interim.
	var observed: Dictionary = cargo.sample(craft,delta)
	if not observed.valid:
		_finish(false,"Parcel returned · observation interrupted")
		push_warning("Courier stopped: "+String(observed.reason))
		return
	elapsed += delta
	var expression: Dictionary = Brrr.step(craft.velocity,-craft.global_basis.z,craft.regime_name()=="DRIVE",delta,brrr,streak)
	brrr = expression.brrr
	streak = expression.streak_s
	longest_streak = maxf(longest_streak,streak)
	peak_speed = maxf(peak_speed,expression.speed)
	var arrived: bool = _xz().distance_to(destination)<=destination_radius and _supported() and craft.velocity.length()<=Rules.ARRIVAL_SPEED and craft.hop_count==_last_hop and observed.loss==0
	_last_hop = craft.hop_count
	settle = settle+delta if arrived else 0.0
	if settle+0.000000001>=Rules.SETTLE_SECONDS:
		_finish(true,"Delivered to Depot")

func _finish(delivered: bool, message: String) -> void:
	last_result = {"delivered":delivered,"message":message,"condition_units":cargo.condition_units,"elapsed":elapsed,"impact_samples":cargo.impact_samples,"episodes":cargo.episodes,"ignored_samples":cargo.ignored_samples,"brrr":brrr,"longest_streak":longest_streak,"peak_speed":peak_speed}
	last_result.make_read_only()
	state = "RESULTS"
	get_tree().paused = true

func _on_reset(_count: int, reason: String) -> void:
	if state == "ACTIVE" or (state in ["PAUSED","WAIT_NEUTRAL"] and _resume_state == "ACTIVE"):
		_finish(false,"Parcel returned · "+reason)
		gate.camera_rig.snap_to_target()

func _xz() -> Vector2:
	return Vector2(craft.global_position.x,craft.global_position.z)
