extends RefCounted
## Ordered-gate lap timing for the Hem Loop.
##
## Gate 0 is the start / finish line; gates 1..n are checkpoints. A lap counts
## only when the line is crossed forward after every checkpoint was crossed
## forward in order. Validation is forgiving rather than fussy:
## - each gate spans the full track plus an overhang beyond both walls;
## - backward crossings are ignored (they never cancel progress);
## - every forward line crossing starts a fresh clock, so doubling back over
##   the line can restart the clock but can never earn a lap;
## - a skipped checkpoint is reported by name when the lap is refused.
## Crossing times are interpolated inside the physics step.

signal lap_started(time: float)
signal gate_passed(index: int, split: float, delta: float, has_delta: bool)
signal lap_completed(record: Dictionary)
signal lap_refused(missed: Array, passed_any: bool)
signal lap_aborted(reason: String)

var gates: Array[Dictionary] = []
var clock := 0.0
var lap_active := false
var lap_start := 0.0
var next_gate := 1
var missed: Array[int] = []
var splits: Array[float] = []
var laps: Array[Dictionary] = []
var refused: Array[Dictionary] = []
var best_time := INF
var best_splits: Array[float] = []
var best_sectors: Array[float] = []


func configure(source_gates: Array[Dictionary]) -> void:
	gates = source_gates
	best_sectors.clear()
	for i in gates.size():
		best_sectors.append(INF)


func current_time() -> float:
	return clock - lap_start if lap_active else 0.0


func has_best() -> bool:
	return best_time < INF


## Advance the clock by one physics step in which the craft moved prev -> curr.
func step(prev: Vector2, curr: Vector2, delta: float) -> void:
	var t0 := clock
	clock += delta
	if prev.distance_squared_to(curr) < 0.0000001:
		return
	var hits: Array = []
	for i in gates.size():
		var hit := crossing(prev, curr, gates[i])
		if not hit.is_empty():
			hits.append([float(hit.fraction), i, bool(hit.forward)])
	hits.sort_custom(func(a, b): return a[0] < b[0])
	for h in hits:
		_on_cross(int(h[1]), t0 + float(h[0]) * delta, bool(h[2]))


static func crossing(p: Vector2, q: Vector2, gate: Dictionary) -> Dictionary:
	var a: Vector2 = gate.a
	var b: Vector2 = gate.b
	var r := q - p
	var s := b - a
	var denom := r.cross(s)
	if absf(denom) < 0.0000001:
		return {}
	var t := (a - p).cross(s) / denom
	var u := (a - p).cross(r) / denom
	if t < 0.0 or t >= 1.0 or u < 0.0 or u > 1.0:
		return {}
	return {"fraction": t, "forward": r.dot(gate.f) > 0.0}


func _on_cross(index: int, time: float, forward: bool) -> void:
	if not forward:
		return
	if index == 0:
		_on_line(time)
		return
	if not lap_active or index < next_gate:
		return
	for skipped in range(next_gate, index):
		missed.append(skipped)
	var split := time - lap_start
	while splits.size() < index - 1:
		splits.append(-1.0)
	splits.append(split)
	next_gate = index + 1
	var has_delta := has_best() and best_splits.size() >= index and missed.is_empty()
	gate_passed.emit(index, split, split - best_splits[index - 1] if has_delta else 0.0, has_delta)


func _on_line(time: float) -> void:
	if lap_active:
		var complete := next_gate == gates.size() and missed.is_empty()
		if complete:
			_complete(time)
		else:
			var not_passed: Array = missed.duplicate()
			for g in range(next_gate, gates.size()):
				not_passed.append(g)
			var passed_any := next_gate > 1
			refused.append({"time": time - lap_start, "missed": not_passed.duplicate(), "passed_any": passed_any})
			lap_refused.emit(not_passed, passed_any)
	lap_active = true
	lap_start = time
	next_gate = 1
	missed.clear()
	splits.clear()
	lap_started.emit(time)


func _complete(time: float) -> void:
	var lap_time := time - lap_start
	var sectors: Array[float] = []
	var previous := 0.0
	for s in splits:
		sectors.append(s - previous)
		previous = s
	sectors.append(lap_time - previous)
	var was_best := lap_time < best_time
	var delta := lap_time - best_time if has_best() else 0.0
	var record := {
		"lap": laps.size() + 1, "time": lap_time, "splits": splits.duplicate(),
		"sectors": sectors, "best": was_best, "delta": delta, "had_best": has_best(),
		"sector_best": [],
	}
	for i in sectors.size():
		var sector_best := sectors[i] < best_sectors[i]
		record.sector_best.append(sector_best)
		if sector_best:
			best_sectors[i] = sectors[i]
	if was_best:
		best_time = lap_time
		best_splits = splits.duplicate()
	laps.append(record)
	lap_completed.emit(record)


## Craft returned to the grid: the lap in progress is discarded without blame.
func abort(reason: String) -> void:
	var had := lap_active
	lap_active = false
	next_gate = 1
	missed.clear()
	splits.clear()
	if had:
		lap_aborted.emit(reason)


func clear_session() -> void:
	abort("session")
	laps.clear()
	refused.clear()
	best_time = INF
	best_splits.clear()
	configure(gates)


static func format_time(seconds: float) -> String:
	if seconds == INF or seconds < 0.0:
		return "-:--.--"
	var total := int(floor(seconds * 100.0 + 0.0001))
	return "%d:%02d.%02d" % [total / 6000, (total / 100) % 60, total % 100]


static func format_delta(seconds: float) -> String:
	return ("+" if seconds >= 0.0 else "−") + "%.2f" % absf(seconds)
