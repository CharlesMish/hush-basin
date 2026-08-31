class_name CraftController
extends CharacterBody3D

signal reset_performed(count: int, reason: String)

@export var tuning: CraftTuning

@onready var _probes: Array[RayCast3D] = [
	$ProbeLeft as RayCast3D,
	$ProbeRight as RayCast3D,
	$ProbeRear as RayCast3D,
]
@onready var _hazard_preview: ShapeCast3D = get_node_or_null("HazardPreview") as ShapeCast3D
@onready var _visual_root: Node3D = $VisualRoot
@onready var _visual_rig: VehicleVisualRig = $VisualRoot as VehicleVisualRig

var fold_amount: float = 0.0
var support_reacquire_blend: float = 1.0
var probe_hit_count: int = 0
var measured_height: float = -1.0
var support_normal: Vector3 = Vector3.UP
var support_normal_angle: float = 0.0
var reset_count: int = 0
var last_reset_reason: String = "spawn"
var last_physics_delta: float = 0.0

var active_target_height: float = 1.25
var active_vertical_limit: float = 42.0
var powered_speed_target: float = 17.0
var powered_surface_speed: float = 0.0
var effective_thrust: float = 0.0
var thrust_taper: float = 1.0

var hop_cooldown_remaining: float = 0.0
var hop_buffer_remaining: float = 0.0
var support_grace_remaining: float = 0.0
var last_hop_speed_cost: float = 0.0
var hop_count: int = 0

var last_impact_severity: float = 0.0
var last_impact_closing_speed: float = 0.0
var last_impact_speed_lost: float = 0.0
var last_impact_retention: float = 1.0
var last_impact_in_drive: bool = false
var impact_count: int = 0

var preview_distance: float = 0.0
var preview_safe_fraction: float = 1.0
var clearance_state: String = "CLEAR"

var _spawn_transform: Transform3D
var _last_valid_support_normal: Vector3 = Vector3.UP
var _grace_support_normal: Vector3 = Vector3.UP
var _grace_support_height: float = -1.0
var _grace_support_hit_count: int = 0
var _support_grace_available: bool = false
var _input_locked_until_release: bool = false
var _visual_bank: float = 0.0
var _transform_was_held: bool = false
var _support_reacquiring: bool = false
var _strike_cue_remaining: float = 0.0


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	_spawn_transform = global_transform
	if _visual_rig != null:
		_visual_rig.set_form_amount(fold_amount)
	if tuning == null:
		push_error("CraftController requires a CraftTuning resource.")


func _notification(what: int) -> void:
	if what == NOTIFICATION_APPLICATION_FOCUS_OUT:
		_input_locked_until_release = true
		clear_pending_hop()


func _unhandled_input(event: InputEvent) -> void:
	if event.is_action_pressed("pause"):
		get_tree().paused = not get_tree().paused
		_input_locked_until_release = true
		clear_pending_hop()
		get_viewport().set_input_as_handled()
	elif event.is_action_pressed("reset"):
		reset_craft("manual")
		get_viewport().set_input_as_handled()


func _physics_process(delta: float) -> void:
	last_physics_delta = delta
	if tuning == null or get_tree().paused:
		return
	if global_position.y < tuning.fall_reset_y:
		reset_craft("fell below %.1f m" % tuning.fall_reset_y)
		return

	_update_input_lock()
	_sample_support()
	advance_hop_timing(delta)
	hop_cooldown_remaining = maxf(0.0, hop_cooldown_remaining - delta)
	_strike_cue_remaining = maxf(0.0, _strike_cue_remaining - delta)

	var throttle_input := 0.0
	var brake_input := 0.0
	var steer_input := 0.0
	if not _input_locked_until_release:
		throttle_input = Input.get_action_strength("throttle")
		brake_input = Input.get_action_strength("brake")
		steer_input = Input.get_axis("steer_left", "steer_right")
	var transform_held := not _input_locked_until_release and Input.is_action_pressed("transform")
	update_transform_state(transform_held, delta)
	_update_support_reacquisition(delta)
	if not _input_locked_until_release and Input.is_action_just_pressed("hop"):
		arm_hop_buffer()
	attempt_buffered_hop()

	active_target_height = lerpf(tuning.spread_target_height, tuning.drive_target_height, fold_amount)
	var hover_omega := lerpf(tuning.spread_hover_omega, tuning.drive_hover_omega, fold_amount)
	var hover_zeta := lerpf(tuning.spread_hover_zeta, tuning.drive_hover_zeta, fold_amount)
	var hover_up_limit := lerpf(tuning.spread_hover_accel_up_max, tuning.drive_hover_accel_up_max, fold_amount)
	var hover_down_limit := lerpf(tuning.spread_hover_accel_down_max, tuning.drive_hover_accel_down_max, fold_amount)
	var gravity_compensation_ratio := lerpf(
		tuning.spread_gravity_compensation_ratio,
		tuning.drive_gravity_compensation_ratio,
		fold_amount
	)
	active_vertical_limit = hover_up_limit

	var base_thrust := lerpf(tuning.spread_thrust_accel, tuning.drive_thrust_accel, fold_amount)
	var soft_speed := lerpf(tuning.spread_powered_speed_soft, tuning.drive_powered_speed_soft, fold_amount)
	powered_speed_target = lerpf(tuning.spread_powered_speed_cap, tuning.drive_powered_speed_cap, fold_amount)
	var steer_rate := lerpf(tuning.spread_steer_rate, tuning.drive_steer_rate, fold_amount)
	var drag := lerpf(tuning.spread_drag, tuning.drive_drag, fold_amount)
	var brake_decel := lerpf(tuning.spread_brake_decel, tuning.drive_brake_decel, fold_amount)

	rotate_y(-steer_input * steer_rate * delta)

	var movement_normal := support_normal if probe_hit_count > 0 else Vector3.UP
	var forward := MotionMath.tangent_component(-global_transform.basis.z, movement_normal)
	forward = MotionMath.safe_normalize(forward, -global_transform.basis.z)
	powered_surface_speed = MotionMath.powered_speed_budget(
		velocity,
		movement_normal
	)
	effective_thrust = MotionMath.powered_thrust(
		base_thrust,
		powered_surface_speed,
		soft_speed,
		powered_speed_target
	)
	thrust_taper = effective_thrust / maxf(base_thrust, 0.001)

	velocity += Vector3.DOWN * tuning.gravity * delta
	if probe_hit_count > 0 and support_reacquire_blend > 0.0:
		var normal_speed := velocity.dot(support_normal)
		var height_error := active_target_height - measured_height
		var gravity_compensation := (
			tuning.gravity
			* gravity_compensation_ratio
			* support_normal.dot(Vector3.UP)
		)
		var hover_accel := MotionMath.hover_acceleration(
			height_error,
			normal_speed,
			hover_omega,
			hover_zeta,
			gravity_compensation,
			hover_down_limit,
			hover_up_limit
		)
		velocity += support_normal * hover_accel * support_reacquire_blend * delta

	var normal_component := movement_normal * velocity.dot(movement_normal)
	var tangential_velocity := velocity - normal_component
	tangential_velocity = MotionMath.step_linear_drag(
		tangential_velocity,
		forward * throttle_input * effective_thrust,
		drag,
		delta
	)
	if brake_input > 0.0:
		tangential_velocity = tangential_velocity.move_toward(
			Vector3.ZERO,
			brake_decel * brake_input * delta
		)
	velocity = tangential_velocity + normal_component

	var pre_move_velocity := velocity
	move_and_slide()
	_apply_strongest_impact(pre_move_velocity)
	_update_hazard_preview()
	_update_clearance_state()
	_update_visuals(steer_input, delta)


func _sample_support() -> void:
	var normal_sum := Vector3.ZERO
	var height_sum := 0.0
	probe_hit_count = 0
	for probe in _probes:
		probe.force_raycast_update()
		if not probe.is_colliding():
			continue
		var hit_point := probe.get_collision_point()
		var hit_normal := probe.get_collision_normal()
		if not MotionMath.is_finite_vector(hit_point) or not MotionMath.is_finite_vector(hit_normal):
			continue
		probe_hit_count += 1
		normal_sum += hit_normal
		height_sum += global_position.y - hit_point.y
	if probe_hit_count > 0:
		support_normal = MotionMath.safe_normalize(normal_sum, _last_valid_support_normal)
		_last_valid_support_normal = support_normal
		measured_height = height_sum / float(probe_hit_count)
		support_normal_angle = rad_to_deg(acos(clampf(support_normal.dot(Vector3.UP), -1.0, 1.0)))
	else:
		support_normal = _last_valid_support_normal
		measured_height = -1.0
		support_normal_angle = rad_to_deg(acos(clampf(support_normal.dot(Vector3.UP), -1.0, 1.0)))


func update_transform_state(transform_held: bool, delta: float) -> void:
	# Button edges alter form state only; motion and location remain untouched.
	_transform_was_held = transform_held
	var duration := tuning.fold_duration if transform_held else tuning.deploy_duration
	var target := 1.0 if transform_held else 0.0
	fold_amount = move_toward(fold_amount, target, delta / maxf(duration, 0.001))


func _update_support_reacquisition(delta: float) -> void:
	if _transform_was_held or fold_amount >= 0.65:
		_support_reacquiring = false
		support_reacquire_blend = 1.0
		return
	if probe_hit_count <= 0:
		_support_reacquiring = true
		support_reacquire_blend = 0.0
		return
	if not _support_reacquiring:
		support_reacquire_blend = 1.0
		return
	if MotionMath.support_reacquire_is_valid(
		probe_hit_count,
		measured_height,
		tuning.support_reacquire_max_distance,
		support_normal,
		velocity,
		tuning.support_reacquire_max_departure_speed,
		tuning.support_reacquire_max_slope_degrees
	):
		support_reacquire_blend = move_toward(
			support_reacquire_blend,
			1.0,
			delta / maxf(tuning.support_reacquire_duration, 0.001)
		)
		if support_reacquire_blend >= 0.999:
			support_reacquire_blend = 1.0
			_support_reacquiring = false


func try_hop() -> bool:
	return _try_hop_from_support(support_normal, probe_hit_count, measured_height)


func arm_hop_buffer() -> void:
	if tuning == null or _input_locked_until_release or get_tree().paused:
		return
	hop_buffer_remaining = tuning.hop_input_buffer_seconds


func advance_hop_timing(delta: float) -> void:
	if tuning == null:
		return
	hop_buffer_remaining = maxf(0.0, hop_buffer_remaining - delta)
	support_grace_remaining = maxf(0.0, support_grace_remaining - delta)
	if _input_locked_until_release:
		clear_pending_hop()
		return
	var support_is_hop_eligible := (
		probe_hit_count > 0
		and measured_height >= 0.0
		and measured_height <= tuning.hop_max_support_distance
		and MotionMath.is_finite_vector(support_normal)
		and hop_cooldown_remaining <= 0.0
		and velocity.dot(support_normal) <= tuning.support_reacquire_max_departure_speed
	)
	if support_is_hop_eligible:
		_grace_support_normal = support_normal
		_grace_support_height = measured_height
		_grace_support_hit_count = probe_hit_count
		_support_grace_available = true
		support_grace_remaining = tuning.hop_support_grace_seconds
	elif support_grace_remaining <= 0.0:
		_support_grace_available = false


func attempt_buffered_hop() -> bool:
	if hop_buffer_remaining <= 0.0 or tuning == null or _input_locked_until_release:
		return false
	var hopped := false
	if probe_hit_count > 0:
		hopped = _try_hop_from_support(support_normal, probe_hit_count, measured_height)
	elif _support_grace_available and support_grace_remaining > 0.0:
		hopped = _try_hop_from_support(
			_grace_support_normal,
			_grace_support_hit_count,
			_grace_support_height
		)
	if hopped:
		clear_pending_hop()
	return hopped


func clear_pending_hop() -> void:
	hop_buffer_remaining = 0.0
	support_grace_remaining = 0.0
	_support_grace_available = false
	_grace_support_height = -1.0
	_grace_support_hit_count = 0


func _try_hop_from_support(
	hop_normal: Vector3,
	hit_count: int,
	hit_height: float
) -> bool:
	if not MotionMath.hop_can_start(
		fold_amount,
		tuning.hop_max_fold_amount,
		hit_count,
		hit_height,
		tuning.hop_max_support_distance,
		hop_cooldown_remaining
	):
		return false
	var before_tangent_speed := MotionMath.tangent_component(velocity, hop_normal).length()
	velocity = MotionMath.hop_exchange(
		velocity,
		hop_normal,
		tuning.hop_normal_speed,
		tuning.hop_tangential_retention
	)
	var after_tangent_speed := MotionMath.tangent_component(velocity, hop_normal).length()
	last_hop_speed_cost = maxf(0.0, before_tangent_speed - after_tangent_speed)
	hop_cooldown_remaining = tuning.hop_cooldown
	hop_count += 1
	_support_reacquiring = true
	support_reacquire_blend = 0.0
	return true


func _apply_strongest_impact(pre_move_velocity: Vector3) -> void:
	var strongest_closing := 0.0
	var strongest_normal := Vector3.ZERO
	for index in get_slide_collision_count():
		var collision := get_slide_collision(index)
		var normal := MotionMath.safe_normalize(collision.get_normal(), Vector3.UP)
		var closing := maxf(0.0, -pre_move_velocity.dot(normal))
		if closing > strongest_closing:
			strongest_closing = closing
			strongest_normal = normal
	if strongest_closing <= tuning.impact_min_closing_speed:
		return
	var max_loss := lerpf(
		tuning.spread_impact_max_speed_loss,
		tuning.drive_impact_max_speed_loss,
		fold_amount
	)
	var response := MotionMath.impact_response(
		velocity,
		pre_move_velocity,
		strongest_normal,
		tuning.impact_min_closing_speed,
		tuning.impact_full_closing_speed,
		max_loss
	)
	velocity = response.velocity
	last_impact_closing_speed = float(response.closing_speed)
	last_impact_severity = float(response.severity)
	last_impact_retention = float(response.retention)
	last_impact_speed_lost = float(response.speed_lost)
	last_impact_in_drive = fold_amount >= 0.65
	impact_count += 1
	_strike_cue_remaining = tuning.impact_strike_cue_duration


func _update_hazard_preview() -> void:
	if _hazard_preview == null:
		preview_distance = 0.0
		preview_safe_fraction = 1.0
		return
	preview_distance = clampf(
		tuning.preview_min_distance + velocity.length() * tuning.preview_seconds_ahead,
		tuning.preview_min_distance,
		tuning.preview_max_distance
	)
	_hazard_preview.target_position = Vector3(0.0, 0.0, -preview_distance)
	_hazard_preview.force_shapecast_update()
	preview_safe_fraction = _hazard_preview.get_closest_collision_safe_fraction()


func _update_clearance_state() -> void:
	if _strike_cue_remaining > 0.0:
		clearance_state = "STRIKE"
	elif _hazard_preview != null and _hazard_preview.is_colliding():
		clearance_state = "CAUTION"
	else:
		clearance_state = "CLEAR"


func _update_visuals(steer_input: float, delta: float) -> void:
	var target_bank := deg_to_rad(-steer_input * tuning.visual_bank_degrees)
	var response := 1.0 - exp(-tuning.visual_response * delta)
	_visual_bank = lerpf(_visual_bank, target_bank, response)
	_visual_root.rotation.z = _visual_bank
	if _visual_rig != null:
		_visual_rig.set_form_amount(fold_amount)
		_visual_rig.set_energy_state(clearance_state)


func _update_input_lock() -> void:
	if not _input_locked_until_release:
		return
	var movement_released := (
		Input.get_action_strength("throttle") < 0.01
		and Input.get_action_strength("brake") < 0.01
		and absf(Input.get_axis("steer_left", "steer_right")) < 0.01
		and not Input.is_action_pressed("transform")
		and not Input.is_action_pressed("hop")
	)
	if movement_released:
		_input_locked_until_release = false


func reset_craft(reason: String) -> void:
	# This is the only post-initialization gameplay transform write.
	global_transform = _spawn_transform
	velocity = Vector3.ZERO
	fold_amount = 0.0
	support_reacquire_blend = 1.0
	_transform_was_held = false
	_support_reacquiring = false
	hop_cooldown_remaining = 0.0
	clear_pending_hop()
	last_hop_speed_cost = 0.0
	hop_count = 0
	last_impact_severity = 0.0
	last_impact_closing_speed = 0.0
	last_impact_speed_lost = 0.0
	last_impact_retention = 1.0
	last_impact_in_drive = false
	impact_count = 0
	_strike_cue_remaining = 0.0
	clearance_state = "CLEAR"
	preview_safe_fraction = 1.0
	_input_locked_until_release = true
	_visual_bank = 0.0
	_visual_root.rotation = Vector3.ZERO
	if _visual_rig != null:
		_visual_rig.set_form_amount(0.0)
		_visual_rig.set_energy_state("CLEAR")
	reset_count += 1
	last_reset_reason = reason
	reset_physics_interpolation()
	reset_performed.emit(reset_count, reason)


func set_spawn_transform(new_spawn_transform: Transform3D) -> void:
	if not MotionMath.is_finite_vector(new_spawn_transform.origin):
		return
	_spawn_transform = new_spawn_transform


func regime_name() -> String:
	if _transform_was_held or fold_amount >= 0.55:
		return "DRIVE"
	return "SPREAD"


func telemetry() -> Dictionary:
	var normal := support_normal if probe_hit_count > 0 else _last_valid_support_normal
	var normal_speed := velocity.dot(normal)
	var tangential_speed := MotionMath.tangent_component(velocity, normal).length()
	return {
		"speed": velocity.length(),
		"tangential_speed": tangential_speed,
		"normal_speed": normal_speed,
		"target_height": active_target_height,
		"measured_height": measured_height,
		"height_error": active_target_height - measured_height if measured_height >= 0.0 else 0.0,
		"vertical_limit": active_vertical_limit,
		"probe_hits": probe_hit_count,
		"support_angle": support_normal_angle,
		"fold_amount": fold_amount,
		"regime": regime_name(),
		"powered_speed_target": powered_speed_target,
		"powered_surface_speed": powered_surface_speed,
		"effective_thrust": effective_thrust,
		"thrust_taper": thrust_taper,
		"support_reacquire_blend": support_reacquire_blend,
		"preview_distance": preview_distance,
		"preview_safe_fraction": preview_safe_fraction,
		"clearance_state": clearance_state,
		"hop_cooldown": hop_cooldown_remaining,
		"hop_buffer": hop_buffer_remaining,
		"support_grace": support_grace_remaining,
		"last_hop_speed_cost": last_hop_speed_cost,
		"hop_count": hop_count,
		"impact_severity": last_impact_severity,
		"impact_closing_speed": last_impact_closing_speed,
		"impact_speed_lost": last_impact_speed_lost,
		"impact_retention": last_impact_retention,
		"impact_count": impact_count,
		"impact_in_drive": last_impact_in_drive,
		"reset_count": reset_count,
		"reset_reason": last_reset_reason,
		"physics_delta": last_physics_delta,
	}
