extends RefCounted

const V_FLOOR := 20.0


# Seed metric. Farming is expected. Rewrite freely.
static func step(
	velocity: Vector3,
	forward: Vector3,
	drive: bool,
	delta: float,
	current_brrr: float,
	current_streak_s: float
) -> Dictionary:
	var horizontal_velocity := Vector2(velocity.x, velocity.z)
	var speed := horizontal_velocity.length()
	var flat_forward := Vector2(forward.x, forward.z)
	var split_degrees := 0.0
	if speed > 0.000001 and flat_forward.length_squared() > 0.000001:
		var heading := flat_forward.normalized()
		var course := horizontal_velocity / speed
		split_degrees = clampf(
			rad_to_deg(acos(clampf(heading.dot(course), -1.0, 1.0))),
			0.0,
			90.0
		)
	var qualifying := drive and speed >= V_FLOOR
	var streak_s := current_streak_s
	var brrr := current_brrr
	var rate := 0.0
	if qualifying:
		streak_s += delta
		rate = (
			(speed - V_FLOOR)
			* (1.0 + split_degrees / 30.0)
			* (1.0 + minf(streak_s, 10.0) / 10.0)
		)
		brrr += rate * delta * 10.0
	else:
		streak_s = 0.0
	return {
		"brrr": brrr,
		"streak_s": streak_s,
		"rate": rate,
		"speed": speed,
		"split_degrees": split_degrees,
		"qualifying": qualifying,
	}
