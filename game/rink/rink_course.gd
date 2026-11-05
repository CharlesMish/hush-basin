extends RefCounted
## Hem Loop centreline, widths and timing gates. Pure geometry; owns no nodes.
## Coordinates are metres on the yard floor: Vector2(x east, z south).

const DATA_PATH := "res://rink/hem_loop_course.json"
const STEP_M := 0.5

var data: Dictionary = {}
var samples: Array[Dictionary] = []
var length := 0.0
var piece_ranges: Dictionary = {}
var gates: Array[Dictionary] = []


static func forward(yaw: float) -> Vector2:
	return Vector2(-sin(yaw), -cos(yaw))


static func left_of(f: Vector2) -> Vector2:
	return Vector2(f.y, -f.x)


func load_course(path: String = DATA_PATH) -> bool:
	var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(path))
	if typeof(parsed) != TYPE_DICTIONARY:
		push_error("Hem Loop course data could not be read: " + path)
		return false
	data = parsed
	_sample()
	_build_gates()
	return true


func _sample() -> void:
	samples.clear()
	piece_ranges.clear()
	var pos := Vector2.ZERO
	var yaw := deg_to_rad(float(data.start_yaw_degrees))
	var s := 0.0
	var prev_wl := float(data.pieces[-1].wl)
	var prev_wr := float(data.pieces[-1].wr)
	var blend := float(data.width_blend_m)
	for piece in data.pieces:
		var start_s := s
		var wl := float(piece.wl)
		var wr := float(piece.wr)
		var arc := String(piece.kind) == "arc"
		var turn := deg_to_rad(float(piece.get("deg", 0.0)))
		var radius := float(piece.get("r", 0.0))
		var piece_len := absf(turn) * radius if arc else float(piece.len)
		var piece_blend := float(piece.get("blend_m", blend))
		var steps := maxi(1, int(ceil(piece_len / STEP_M)))
		var centre := Vector2.ZERO
		var side := signf(turn)
		if arc:
			centre = pos + left_of(forward(yaw)) * radius * side
		for i in steps:
			var t := float(i) / float(steps)
			var local_s := t * piece_len
			var p := pos
			var y := yaw
			if arc:
				y = yaw + turn * t
				p = centre - left_of(forward(y)) * radius * side
			else:
				p = pos + forward(yaw) * local_s
			var w := smoothstep(0.0, 1.0, clampf(local_s / piece_blend, 0.0, 1.0))
			samples.append({
				"p": p, "f": forward(y), "yaw": y, "s": start_s + local_s,
				"wl": lerpf(prev_wl, wl, w), "wr": lerpf(prev_wr, wr, w),
				"id": String(piece.id), "k": (side / radius) if arc else 0.0,
			})
		if arc:
			yaw += turn
			pos = centre - left_of(forward(yaw)) * radius * side
		else:
			pos += forward(yaw) * piece_len
		s += piece_len
		piece_ranges[String(piece.id)] = Vector2(start_s, s)
		prev_wl = wl
		prev_wr = wr
	length = s
	if pos.length() > 0.05:
		push_warning("Hem Loop centreline closes %.3f m from its start." % pos.length())


func piece_s(piece_id: String, at_m: float = -1.0, fraction: float = -1.0) -> float:
	var r: Vector2 = piece_ranges[piece_id]
	if fraction >= 0.0:
		return lerpf(r.x, r.y, fraction)
	return r.x + at_m


func gate_s(spec: Dictionary) -> float:
	if spec.has("at_fraction"):
		return piece_s(String(spec.piece), -1.0, float(spec.at_fraction))
	return piece_s(String(spec.piece), float(spec.at))


func _build_gates() -> void:
	gates.clear()
	var overhang := float(data.gate_overhang_m)
	for spec in data.gates:
		var s := gate_s(spec)
		var pose := pose_at(s)
		var lf := left_of(pose.f)
		gates.append({
			"id": String(spec.id), "name": String(spec.name), "s": s,
			"a": pose.p + lf * (pose.wl + overhang),
			"b": pose.p - lf * (pose.wr + overhang),
			"f": pose.f,
		})


func index_at(s: float) -> int:
	var wrapped := fposmod(s, length)
	return clampi(int(wrapped / STEP_M), 0, samples.size() - 1)


func pose_at(s: float) -> Dictionary:
	var wrapped := fposmod(s, length)
	var i := clampi(int(floor(wrapped / STEP_M)), 0, samples.size() - 1)
	var a: Dictionary = samples[i]
	var b: Dictionary = samples[(i + 1) % samples.size()]
	var span := float(b.s) - float(a.s)
	if span <= 0.0:
		span += length
	var t := clampf((wrapped - float(a.s)) / maxf(span, 0.0001), 0.0, 1.0)
	return {
		"p": (a.p as Vector2).lerp(b.p, t), "f": ((a.f as Vector2).lerp(b.f, t)).normalized(),
		"wl": lerpf(a.wl, b.wl, t), "wr": lerpf(a.wr, b.wr, t), "s": wrapped,
		"id": a.id, "k": a.k,
	}


func edge_point(s: float, lateral: float) -> Vector2:
	## lateral > 0 is left of the racing direction.
	var pose := pose_at(s)
	return pose.p + left_of(pose.f) * lateral


## Nearest centreline sample. With a hint it searches a local window, which keeps
## the answer on the right lap section where the centreline passes close to itself.
func project(point: Vector2, hint_s: float = -1.0) -> Dictionary:
	var best_i := 0
	var best_d := INF
	if hint_s < 0.0:
		for i in samples.size():
			var d := point.distance_squared_to(samples[i].p)
			if d < best_d:
				best_d = d
				best_i = i
	else:
		var centre := index_at(hint_s)
		for offset in range(-120, 121):
			var i := posmod(centre + offset, samples.size())
			var d := point.distance_squared_to(samples[i].p)
			if d < best_d:
				best_d = d
				best_i = i
	var sample: Dictionary = samples[best_i]
	var rel := point - (sample.p as Vector2)
	return {
		"s": float(sample.s) + rel.dot(sample.f), "lateral": rel.dot(left_of(sample.f)),
		"index": best_i, "id": sample.id, "distance": sqrt(best_d),
	}


## Height of the yard surface at (s, lateral): zero everywhere except the
## Hem's banked outer band. Lateral beyond the outer edge clamps to the edge.
func bank_height(s: float, lateral: float) -> float:
	if not data.has("bank"):
		return 0.0
	var b: Dictionary = data.bank
	var r: Vector2 = piece_ranges[String(b.piece)]
	var x := fposmod(s, length)
	var start := r.x - float(b.lead_m)
	var finish := r.y + float(b.trail_m)
	if x < start or x > finish:
		return 0.0
	var envelope := smoothstep(start, start + float(b.ramp_in_m), x) * (1.0 - smoothstep(finish - float(b.ramp_out_m), finish, x))
	if envelope <= 0.0:
		return 0.0
	var wr := float(pose_at(x).wr)
	var band := float(b.band_m)
	var u := clampf((-lateral - (wr - band)) / band, 0.0, 1.0)
	return float(b.height_m) * envelope * u * u


func bank_range() -> Vector2:
	if not data.has("bank"):
		return Vector2.ZERO
	var r: Vector2 = piece_ranges[String(data.bank.piece)]
	return Vector2(r.x - float(data.bank.lead_m), r.y + float(data.bank.trail_m))


func grid_transform(height: float) -> Transform3D:
	var pose := pose_at(float(data.grid_s))
	var yaw := atan2(-pose.f.x, -pose.f.y)
	return Transform3D(Basis(Vector3.UP, yaw), Vector3(pose.p.x, height, pose.p.y))


func piece_name(piece_id: String) -> String:
	for piece in data.pieces:
		if String(piece.id) == piece_id:
			return String(piece.name)
	return piece_id
