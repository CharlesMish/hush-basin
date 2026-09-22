extends RefCounted
## Pure visual geometry. Future tints share this functional width/fade response.
static func frames(history: Array, side: float, cfg: Dictionary) -> Array:
	var result: Array = []
	for i in range(history.size()):
		var point: Dictionary = history[i]
		var center: Vector3 = point.p + point.right * side * float(cfg.rail_offset_m)
		var before: Vector3 = center
		var after: Vector3 = center
		if i > 0 and not bool(point.get("break_before", false)):
			before = history[i - 1].p + history[i - 1].right * side * float(cfg.rail_offset_m)
		if i + 1 < history.size() and not bool(history[i + 1].get("break_before", false)):
			after = history[i + 1].p + history[i + 1].right * side * float(cfg.rail_offset_m)
		var tangent := after - before
		var right := tangent.cross(Vector3.UP).normalized()
		if right.length_squared() < 0.5:
			right = point.right.normalized()
		var remaining := clampf(1.0 - float(point.age) / float(cfg.history_seconds), 0.0, 1.0)
		# The old end finishes at a point even when bounded history drops a
		# sample. Width relaxes along the same continuously fading lifetime.
		var is_tail := i == 0 or bool(point.get("break_before", false))
		var taper := 0.0 if is_tail else smoothstep(0.0, float(cfg.tail_fraction), remaining)
		var width := lerpf(float(cfg.straight_half_width_m), float(cfg.drift_half_width_m), float(point.slip)) * taper
		var alpha := lerpf(float(cfg.straight_alpha), float(cfg.drift_alpha), float(point.slip))
		alpha *= remaining * remaining * (0.88 + 0.12 * float(point.streak)) * taper
		result.append({"center": center, "right": right, "width": width, "alpha": alpha,
			"slip": float(point.slip), "break_before": bool(point.get("break_before", false))})
	return result
