class_name P1ATelemetry
extends Node

signal event_emitted(event: Dictionary)

const QUEUE_LIMIT := 256
const CONSOLE_JSONL_ARGUMENT := "--p1a-telemetry-jsonl"
const HARD_IDS := {
	"CORE_PLINTH_MASK": true,
	"CORE_WALL": true,
	"HOP_BAR_01": true,
	"OUTER_CLOSURE_MASK": true,
	"OUTER_WALL": true,
}

var data: P1AWorldData
var craft: CraftController
var physics_tick: int = 0
var serial: int = 0
var dropped_count: int = 0
var events: Array[Dictionary] = []
var current_route_id := ""
var current_route_entry_tick: int = -1
var current_route_entry_point := Vector2.ZERO
var current_route_distance := 0.0
var current_route_origin_node := ""
var route_outside_ticks := 0
var candidate_route_id := ""
var candidate_tick: int = -1
var candidate_point := Vector2.ZERO
var candidate_elapsed := 0.0
var candidate_distance := 0.0
var previous_position := Vector2.ZERO
var previous_position_valid := false
var previous_inside_core := false
var previous_core_valid := false
var previous_junction_id := ""
var previous_hop_count := 0
var previous_surface_class := -1
var console_jsonl_enabled := false


func configure(source_data: P1AWorldData, source_craft: CraftController) -> void:
	data = source_data
	craft = source_craft
	console_jsonl_enabled = console_output_requested(OS.get_cmdline_user_args())
	process_physics_priority = 100
	set_physics_process(true)


static func console_output_requested(user_args: PackedStringArray) -> bool:
	# Runtime-vector evidence is parsed from stdout. Ordinary play and human
	# capture consume the same events through the queue/signal and must not flood
	# the editor's remote-debug console during sustained collision contact.
	return "--vector" in user_args or CONSOLE_JSONL_ARGUMENT in user_args


func _physics_process(delta: float) -> void:
	if data == null or craft == null:
		return
	physics_tick += 1
	var point := Vector2(craft.global_position.x, craft.global_position.z)
	_observe_collisions()
	_observe_hop()
	_observe_surface(point)
	_observe_gate(point)
	_observe_route(point, delta)
	previous_position = point
	previous_position_valid = true


func segment_boundary() -> void:
	current_route_id = ""
	current_route_entry_tick = -1
	current_route_distance = 0.0
	current_route_origin_node = ""
	route_outside_ticks = 0
	candidate_route_id = ""
	candidate_tick = -1
	candidate_elapsed = 0.0
	candidate_distance = 0.0
	previous_position_valid = false
	previous_core_valid = false
	previous_junction_id = ""
	previous_hop_count = craft.hop_count if craft != null else 0


func emit_reset(reason: String, from_transform: Transform3D, to_transform: Transform3D) -> void:
	segment_boundary()
	emit_event({
		"event": "RESET",
		"reason": reason.to_upper(),
		"from_transform": _transform_record(from_transform),
		"to_transform": _transform_record(to_transform),
	})


func emit_selection(selected_tour_id: String, prior_tour_id: String) -> void:
	emit_event({
		"event": "DIAGNOSTIC_SELECTION",
		"selected_tour_id": selected_tour_id,
		"prior_tour_id": prior_tour_id,
	})


func emit_spawn(tour_id: String, spawn_id: String, spawn_transform: Transform3D) -> void:
	segment_boundary()
	var point := Vector2(spawn_transform.origin.x, spawn_transform.origin.z)
	var classification := classify(point)
	emit_event({
		"event": "DIAGNOSTIC_SPAWN",
		"tour_id": tour_id,
		"spawn_id": spawn_id,
		"spawn_transform": _transform_record(spawn_transform),
		"classification_at_spawn": classification,
	})
	if classification.begins_with("ROUTE_"):
		emit_event({
			"event": "ROUTE_STATE",
			"route_id": classification.trim_prefix("ROUTE_"),
			"state": "SPAWNED",
			"entry_tick": -1,
			"entry_crossing_xz_m": [point.x, point.y],
			"distance_since_genuine_entry_m": 0.0,
		})


func emit_event(payload: Dictionary) -> void:
	serial += 1
	var event := payload.duplicate(true)
	event["serial"] = serial
	event["physics_tick"] = physics_tick
	if events.size() >= QUEUE_LIMIT:
		events.pop_front()
		dropped_count += 1
	events.append(event)
	event_emitted.emit(event)
	if console_jsonl_enabled:
		print(JSON.stringify(event))


func drain_events() -> Dictionary:
	var copy := events.duplicate(true)
	events.clear()
	return {"events": copy, "dropped_count": dropped_count}


func classify(point: Vector2) -> String:
	var junction := _junction_at(point)
	if not junction.is_empty():
		return "JUNCTION_%s" % junction
	var route := _winning_route(point, 0.0, false)
	if not route.is_empty():
		return "ROUTE_%s" % route
	var yard := data.yard_at(point)
	if not yard.is_empty():
		return "YARD_%s" % yard
	return "BASE"


func _observe_hop() -> void:
	if craft.hop_count > previous_hop_count:
		emit_event({"event": "HOP_STARTED", "hop_count": craft.hop_count})
	previous_hop_count = craft.hop_count


func _observe_surface(point: Vector2) -> void:
	var grid: Dictionary = data.terrain_meta.grid
	var origin := P1AWorldData.xz(grid.origin_xz_m)
	var spacing := float(grid.spacing_m)
	var width := int(grid.vertex_count_x)
	var depth := int(grid.vertex_count_z)
	var ix := clampi(int(round((point.x - origin.x) / spacing)), 0, width - 1)
	var iz := clampi(int(round((point.y - origin.y) / spacing)), 0, depth - 1)
	var surface_class := int(data.surface_bytes[iz * width + ix])
	if surface_class != previous_surface_class:
		emit_event({"event": "SURFACE_CLASS_CHANGED", "surface_class": surface_class})
		previous_surface_class = surface_class


func _observe_collisions() -> void:
	var seen := {}
	for index in craft.get_slide_collision_count():
		var collision := craft.get_slide_collision(index)
		var collider := collision.get_collider() as CollisionObject3D
		if collider == null:
			continue
		var source_id := String(collider.get_meta("source_geometry_id", ""))
		if not HARD_IDS.has(source_id) or seen.has(source_id):
			continue
		seen[source_id] = true
		var route_id := current_route_id
		var chainage := -1.0
		var lateral := -1.0
		if not route_id.is_empty():
			var nearest := data.nearest_route_sample(route_id, Vector2(craft.global_position.x, craft.global_position.z))
			chainage = float(nearest.chainage_m)
			lateral = float(nearest.distance_m)
		var contact := collision.get_position()
		var normal := collision.get_normal()
		var horizontal_speed := Vector2(craft.velocity.x, craft.velocity.z).length()
		emit_event({
			"event": "COLLISION_SAMPLE",
			"source_geometry_id": source_id,
			"collision_class": "HARD_HOP" if source_id == "HOP_BAR_01" else "HARD_NON_HOP",
			"contact_position_xyz_m": [contact.x, contact.y, contact.z],
			"craft_position_xyz_m": [craft.global_position.x, craft.global_position.y, craft.global_position.z],
			"craft_velocity_xyz_mps": [craft.velocity.x, craft.velocity.y, craft.velocity.z],
			"horizontal_speed_mps": horizontal_speed,
			"normal_xyz": [normal.x, normal.y, normal.z],
			"route_id": route_id,
			"route_chainage_m": chainage,
			"route_lateral_distance_m": lateral,
		})


func _observe_gate(point: Vector2) -> void:
	var inside_core := data.geometry_contains("CORE_REGION", point)
	if previous_core_valid and inside_core != previous_inside_core and previous_position_valid:
		var crossing := _core_crossing(previous_position, point, previous_inside_core)
		var matches: Array[String] = []
		for gate_id_value in ["GE", "GN", "GW"]:
			var gate_id := String(gate_id_value)
			if data.geometry_contains("GATE_%s_APERTURE" % gate_id, crossing):
				matches.append(gate_id)
		if matches.size() == 1:
			emit_event({
				"event": "GATE_CROSSED",
				"gate_id": matches[0],
				"direction": "OUTSKIRTS_TO_CORE" if inside_core else "CORE_TO_OUTSKIRTS",
				"crossing_xz_m": [crossing.x, crossing.y],
			})
	previous_inside_core = inside_core
	previous_core_valid = true


func _observe_route(point: Vector2, delta: float) -> void:
	var junction := _junction_at(point)
	if not junction.is_empty():
		if not current_route_id.is_empty():
			var route_record: Dictionary = data.manifest.routes[current_route_id]
			var from_node := String(route_record.from_node)
			var to_node := String(route_record.to_node)
			if junction != current_route_origin_node and (junction == from_node or junction == to_node):
				emit_event({
					"event": "ROUTE_STATE",
					"route_id": current_route_id,
					"state": "TRAVERSED",
					"entry_tick": current_route_entry_tick,
					"entry_crossing_xz_m": [current_route_entry_point.x, current_route_entry_point.y],
					"distance_since_genuine_entry_m": current_route_distance,
				})
			current_route_id = ""
		_clear_candidate()
		previous_junction_id = junction
		return
	if not current_route_id.is_empty():
		if previous_position_valid:
			current_route_distance += previous_position.distance_to(point)
		var inside_operational := data.geometry_contains("ROUTE_%s_OPERATIONAL" % current_route_id, point)
		var boundary_distance := data.geometry_boundary_distance("ROUTE_%s_OPERATIONAL" % current_route_id, point)
		if inside_operational or boundary_distance <= 1.0:
			route_outside_ticks = 0
		else:
			route_outside_ticks += 1
			if route_outside_ticks >= 3:
				current_route_id = ""
				route_outside_ticks = 0
		return

	# A segment boundary/teleport invalidates continuity. The first later sample
	# establishes prior state only and can never begin a route candidate.
	if not previous_position_valid:
		_clear_candidate()
		return

	var winner := _winning_route(point, 0.5, true)
	if winner.is_empty():
		_clear_candidate()
		return

	# Candidate creation requires the exact continuous outside-to-inside crossing
	# of the winner's entry-inset envelope. Being already inside after a spawn or
	# reset is insufficient, including the mid-route RT_HOP_SUCCESS spawn.
	var previous_inside_winner := _route_entry_contains(winner, previous_position)
	if winner != candidate_route_id:
		_clear_candidate()
		if previous_inside_winner:
			return
		candidate_route_id = winner
		candidate_tick = physics_tick
		candidate_point = _entry_crossing(previous_position, point, winner)
		candidate_elapsed = 0.0
		candidate_distance = candidate_point.distance_to(point)
		return

	# A candidate survives only while the same total-order winner remains inside
	# its entry inset. Time commits prospectively; entry tick/point/distance remain
	# backdated to the original crossing pair.
	if not _route_entry_contains(candidate_route_id, point):
		_clear_candidate()
		return
	candidate_elapsed += delta
	candidate_distance += previous_position.distance_to(point)
	if candidate_elapsed + 0.000001 >= 0.25 and candidate_distance + 0.000001 >= 2.0:
		current_route_id = candidate_route_id
		current_route_entry_tick = candidate_tick
		current_route_entry_point = candidate_point
		current_route_distance = candidate_distance
		current_route_origin_node = previous_junction_id
		emit_event({
			"event": "ROUTE_STATE",
			"route_id": current_route_id,
			"state": "ENTERED",
			"entry_tick": current_route_entry_tick,
			"entry_crossing_xz_m": [current_route_entry_point.x, current_route_entry_point.y],
			"distance_since_genuine_entry_m": current_route_distance,
		})
		_clear_candidate()


func _route_entry_contains(route_id: String, point: Vector2) -> bool:
	if not _junction_at(point).is_empty():
		return false
	var geometry_id := "ROUTE_%s_OPERATIONAL" % route_id
	return data.geometry_contains(geometry_id, point) and data.geometry_boundary_distance(geometry_id, point) + 0.000001 >= 0.5


func _clear_candidate() -> void:
	candidate_route_id = ""
	candidate_tick = -1
	candidate_point = Vector2.ZERO
	candidate_elapsed = 0.0
	candidate_distance = 0.0


func _winning_route(point: Vector2, inset: float, require_inset: bool) -> String:
	var candidates: Array[Dictionary] = []
	for route_id_value in data.routes:
		var route_id := String(route_id_value)
		var geometry_id := "ROUTE_%s_OPERATIONAL" % route_id
		if not data.geometry_contains(geometry_id, point):
			continue
		if require_inset and data.geometry_boundary_distance(geometry_id, point) + 0.000001 < inset:
			continue
		var nearest := data.nearest_route_sample(route_id, point)
		var half_width := float(data.manifest.routes[route_id].operational_half_width_m)
		candidates.append({"id": route_id, "normalized": float(nearest.distance_m) / half_width})
	candidates.sort_custom(func(a: Dictionary, b: Dictionary) -> bool:
		if absf(float(a.normalized) - float(b.normalized)) > 0.000000000001:
			return float(a.normalized) < float(b.normalized)
		return String(a.id) < String(b.id)
	)
	return String(candidates[0].id) if not candidates.is_empty() else ""


func _junction_at(point: Vector2) -> String:
	var ids: Array = data.manifest.junctions.keys()
	ids.sort()
	for id_value in ids:
		var id := String(id_value)
		if data.geometry_contains("JUNCTION_%s" % id, point):
			return id
	return ""


func _entry_crossing(from: Vector2, to: Vector2, route_id: String) -> Vector2:
	var low := 0.0
	var high := 1.0
	var geometry_id := "ROUTE_%s_OPERATIONAL" % route_id
	for _step in 28:
		var mid := (low + high) * 0.5
		var sample := from.lerp(to, mid)
		var inside := _route_entry_contains(route_id, sample)
		if inside:
			high = mid
		else:
			low = mid
	return from.lerp(to, high)


func _core_crossing(from: Vector2, to: Vector2, from_inside: bool) -> Vector2:
	var low := 0.0
	var high := 1.0
	for _step in 30:
		var mid := (low + high) * 0.5
		if data.geometry_contains("CORE_REGION", from.lerp(to, mid)) == from_inside:
			low = mid
		else:
			high = mid
	return from.lerp(to, (low + high) * 0.5)


static func _transform_record(value: Transform3D) -> Dictionary:
	return {
		"position_xyz_m": [value.origin.x, value.origin.y, value.origin.z],
		"yaw_rad": value.basis.get_euler().y,
	}
