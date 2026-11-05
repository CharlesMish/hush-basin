extends Node
## Test-only Hem Loop driver. It presses the same input actions a player does
## (throttle, brake, steer, transform, hop) and never writes craft pose or
## velocity. A plan is a list of keyframes along the lap:
##   [piece_id, fraction_or_metres, lateral_m, form "D"/"S", target_speed, hop]
## lateral > 0 is left of the racing direction; "W+" / "W-" mean "this far
## from the left / right wall".

var game: Node3D
var course
var active := false
var keys: Array = []
var hop_done: Dictionary = {}
var lap_hint := 0
var last: Dictionary = {}
var steer_gain := 2.2
var spread_k := 1.4
var drive_kp := 0.5
var drive_kd := 1.5
var drive_kv := 1.2
var drive_lon_floor := 10.0
var drive_max_lean := 1.0
var reverse := false


func setup(owner_game: Node3D) -> void:
	game = owner_game
	course = game.course
	process_physics_priority = -50
	process_mode = Node.PROCESS_MODE_PAUSABLE


func set_plan(plan: Array) -> void:
	keys.clear()
	for k in plan:
		var r: Vector2 = course.piece_ranges[String(k[0])]
		var at := float(k[1])
		var s := lerpf(r.x, r.y, at) if at >= 0.0 and at <= 1.0 else r.x + at
		keys.append({"s": s, "lat": k[2], "form": String(k[3]), "speed": float(k[4]), "hop": k.size() > 5 and bool(k[5])})
	keys.sort_custom(func(a, b): return a.s < b.s)
	hop_done.clear()


func _resolve_lat(value, s: float) -> float:
	if typeof(value) == TYPE_STRING:
		var text := String(value)
		var pose: Dictionary = course.pose_at(s)
		if text.begins_with("W+"):
			return float(pose.wl) - float(text.substr(2))
		if text.begins_with("W-"):
			return -float(pose.wr) + float(text.substr(2))
	return float(value)


func _key_at(s: float) -> Array:
	## Returns [previous key, next key, t] around s on the closed lap.
	var n := keys.size()
	var wrapped := fposmod(s, course.length)
	for i in n:
		var a: Dictionary = keys[i]
		var b: Dictionary = keys[(i + 1) % n]
		var a_s := float(a.s)
		var b_s: float = float(b.s) + (float(course.length) if i == n - 1 else 0.0)
		var x: float = wrapped if wrapped >= a_s else wrapped + float(course.length)
		if x >= a_s and x < b_s:
			return [a, b, (x - a_s) / maxf(b_s - a_s, 0.001)]
	return [keys[-1], keys[0], 0.0]


func lateral_at(s: float) -> float:
	var k := _key_at(s)
	return lerpf(_resolve_lat(k[0].lat, s), _resolve_lat(k[1].lat, s), smoothstep(0.0, 1.0, float(k[2])))


static func release() -> void:
	for a in ["throttle", "brake", "steer_left", "steer_right", "transform", "hop"]:
		Input.action_release(a)


func _physics_process(_delta: float) -> void:
	if not active or keys.is_empty() or get_tree().paused:
		return
	var craft: CraftController = game.craft
	if craft.get("_input_locked_until_release"):
		release()
		return
	var pos := Vector2(craft.global_position.x, craft.global_position.z)
	var vel := Vector2(craft.velocity.x, craft.velocity.z)
	var speed := vel.length()
	var s: float = game.progress_s
	var here := _key_at(s)
	var form: String = here[0].form
	var target_speed: float = here[0].speed
	var yaw := craft.rotation.y
	var heading := Vector2(-sin(yaw), -cos(yaw))
	var desired := yaw
	var throttle := 0.0
	var brake := 0.0
	if form == "D" and speed > 6.0:
		# Drive: thrust is the only lateral force, so point the nose along the
		# acceleration the path needs (centripetal feed-forward + lateral PD).
		var pose: Dictionary = course.pose_at(s)
		var t: Vector2 = pose.f
		var n: Vector2 = course.left_of(t)
		var v_t := vel.dot(t)
		var look_s := s + speed * 0.45
		var kappa := float(course.pose_at(look_s).k)
		var lat_err: float = float(game.lateral) - lateral_at(s + speed * 0.25)
		var lat_rate := vel.dot(n) - (lateral_at(s + 2.0) - lateral_at(s - 2.0)) / 4.0 * v_t
		var a_lat := kappa * v_t * v_t - drive_kp * lat_err - drive_kd * lat_rate
		var a_lon := maxf(drive_kv * (target_speed - v_t), drive_lon_floor)
		# Lean the nose off the track tangent by at most drive_max_lean.
		var lean := clampf(atan2(a_lat, a_lon), -drive_max_lean, drive_max_lean)
		var aim := t.rotated(-lean)
		desired = atan2(-aim.x, -aim.y)
		var a := t * a_lon + n * a_lat
		var align := aim.dot(heading)
		throttle = 1.0 if align > 0.75 and (target_speed > v_t or absf(a_lat) > 1.5) else (0.6 if align > 0.4 else 0.0)
		if v_t > target_speed + 0.8:
			brake = 1.0
			throttle = 0.0 if absf(a_lat) < 3.0 else throttle
	else:
		var look := clampf(7.0 + speed * 0.5, 8.0, 24.0)
		var ts := s + look
		# Spread velocity lags the nose; lean the aim point against drift-out.
		var drift_out: float = float(game.lateral) - lateral_at(s)
		var target: Vector2 = course.edge_point(ts, lateral_at(ts) - clampf(drift_out * spread_k, -6.0, 6.0))
		var want := (target - pos).normalized()
		desired = atan2(-want.x, -want.y)
		var err0 := wrapf(desired - yaw, -PI, PI)
		if speed < target_speed and absf(err0) < 1.3:
			throttle = 1.0
		elif speed > target_speed + 1.0:
			brake = 1.0
	var error := wrapf(desired - yaw, -PI, PI)
	Input.action_press("steer_left", clampf(error * steer_gain, 0.0, 1.0))
	Input.action_press("steer_right", clampf(-error * steer_gain, 0.0, 1.0))
	if form == "D":
		Input.action_press("transform")
	else:
		Input.action_release("transform")
	if throttle > 0.0:
		Input.action_press("throttle", throttle)
	else:
		Input.action_release("throttle")
	if brake > 0.0:
		Input.action_press("brake", brake)
	else:
		Input.action_release("brake")
	Input.action_release("hop")
	for k in keys:
		if bool(k.hop) and (not hop_done.has(k.s) or game.sim_time - float(hop_done[k.s]) > 8.0):
			var d := wrapf(s - float(k.s), -course.length * 0.5, course.length * 0.5)
			if d >= 0.0 and d < 6.0:
				hop_done[k.s] = game.sim_time
				Input.action_press("hop")
	last = {"s": s, "speed": speed, "form": craft.regime_name(), "error": error, "lat": game.lateral}
