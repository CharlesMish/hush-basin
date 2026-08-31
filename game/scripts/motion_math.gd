class_name MotionMath
extends RefCounted


static func step_linear_drag(
		velocity_value: Vector3,
		acceleration: Vector3,
		drag_coefficient: float,
		delta: float) -> Vector3:
	if delta <= 0.0:
		return velocity_value
	if drag_coefficient <= 0.000001:
		return velocity_value + acceleration * delta
	var decay := exp(-drag_coefficient * delta)
	return velocity_value * decay + acceleration * ((1.0 - decay) / drag_coefficient)


static func powered_thrust(
		base_thrust: float,
		forward_speed: float,
		soft_speed: float,
		powered_speed: float) -> float:
	if base_thrust <= 0.0:
		return 0.0
	if powered_speed <= soft_speed:
		return base_thrust if forward_speed < powered_speed else 0.0
	var t := clampf((maxf(0.0, forward_speed) - soft_speed) / (powered_speed - soft_speed), 0.0, 1.0)
	var smooth_t := t * t * (3.0 - 2.0 * t)
	return base_thrust * (1.0 - smooth_t)


static func powered_speed_budget(
		world_velocity: Vector3,
		movement_normal: Vector3) -> float:
	return tangent_component(world_velocity, movement_normal).length()


static func hover_acceleration(
		height_error: float,
		normal_speed: float,
		omega: float,
		zeta: float,
		gravity_compensation: float,
		accel_down_max: float,
		accel_up_max: float) -> float:
	var raw := omega * omega * height_error
	raw -= 2.0 * zeta * omega * normal_speed
	raw += gravity_compensation
	return clampf(raw, -accel_down_max, accel_up_max)


static func support_reacquire_is_valid(
		hit_count: int,
		distance: float,
		max_distance: float,
		support_normal: Vector3,
		world_velocity: Vector3,
		max_departure_speed: float,
		max_slope_degrees: float) -> bool:
	if hit_count <= 0 or distance < 0.0 or distance > max_distance:
		return false
	var normal := safe_normalize(support_normal, Vector3.UP)
	var slope_degrees := rad_to_deg(acos(clampf(normal.dot(Vector3.UP), -1.0, 1.0)))
	if slope_degrees > max_slope_degrees:
		return false
	return world_velocity.dot(normal) <= max_departure_speed


static func hop_can_start(
		fold_amount: float,
		max_fold_amount: float,
		hit_count: int,
		support_distance: float,
		max_support_distance: float,
		cooldown_remaining: float) -> bool:
	return (
		fold_amount <= max_fold_amount
		and hit_count > 0
		and support_distance >= 0.0
		and support_distance <= max_support_distance
		and cooldown_remaining <= 0.0
	)


static func hop_exchange(
		world_velocity: Vector3,
		support_normal: Vector3,
		target_normal_speed: float,
		tangential_retention: float) -> Vector3:
	var normal := safe_normalize(support_normal, Vector3.UP)
	var tangent := tangent_component(world_velocity, normal)
	var retained_tangent := tangent * clampf(tangential_retention, 0.0, 1.0)
	var normal_speed := maxf(world_velocity.dot(normal), target_normal_speed)
	return retained_tangent + normal * normal_speed


static func impact_response(
		post_move_velocity: Vector3,
		pre_move_velocity: Vector3,
		collision_normal: Vector3,
		min_closing_speed: float,
		full_closing_speed: float,
		max_speed_loss_fraction: float) -> Dictionary:
	var normal := safe_normalize(collision_normal, Vector3.UP)
	var closing_speed := maxf(0.0, -pre_move_velocity.dot(normal))
	var denominator := maxf(full_closing_speed - min_closing_speed, 0.001)
	var closing_severity := clampf((closing_speed - min_closing_speed) / denominator, 0.0, 1.0)
	var opposition := clampf(closing_speed / maxf(pre_move_velocity.length(), 0.001), 0.0, 1.0)
	var severity := closing_severity * lerpf(0.25, 1.0, opposition)
	var retention := 1.0 - clampf(max_speed_loss_fraction, 0.0, 0.95) * severity
	var result_velocity := post_move_velocity * retention
	return {
		"velocity": result_velocity,
		"closing_speed": closing_speed,
		"severity": severity,
		"retention": retention,
		"speed_lost": maxf(0.0, post_move_velocity.length() - result_velocity.length()),
	}


static func safe_normalize(value: Vector3, fallback: Vector3 = Vector3.UP) -> Vector3:
	if not is_finite_vector(value) or value.length_squared() <= 0.00000001:
		return fallback.normalized()
	return value.normalized()


static func is_finite_vector(value: Vector3) -> bool:
	return is_finite(value.x) and is_finite(value.y) and is_finite(value.z)


static func tangent_component(value: Vector3, normal: Vector3) -> Vector3:
	var safe_normal := safe_normalize(normal, Vector3.UP)
	return value - safe_normal * value.dot(safe_normal)
