class_name P1AMap
extends Control

const WORLD_MIN := Vector2(-330.0, -315.0)
const WORLD_MAX := Vector2(330.0, 285.0)

var data: P1AWorldData
var craft: CraftController
var highlighted_route_ids: Array[String] = []


func configure(source_data: P1AWorldData, source_craft: CraftController) -> void:
	data = source_data
	craft = source_craft
	custom_minimum_size = Vector2(258.0, 232.0)
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	queue_redraw()


func set_highlighted_routes(route_ids: Array[String]) -> void:
	highlighted_route_ids = route_ids.duplicate()
	queue_redraw()


func _process(_delta: float) -> void:
	if craft != null:
		queue_redraw()


func _draw() -> void:
	draw_rect(Rect2(Vector2.ZERO, size), Color(0.025, 0.04, 0.055, 0.90), true)
	draw_rect(Rect2(Vector2.ZERO, size), Color(0.20, 0.48, 0.46, 0.75), false, 1.5)
	if data == null:
		return
	var route_ids: Array = data.routes.keys()
	route_ids.sort()
	for route_id_value in route_ids:
		var route_id := String(route_id_value)
		var raw_points: Array = data.routes[route_id].points_xz_m
		var points := PackedVector2Array()
		points.resize(raw_points.size())
		for index in raw_points.size():
			points[index] = _world_to_map(P1AWorldData.xz(raw_points[index]))
		var highlighted := route_id in highlighted_route_ids
		var route_color := Color(0.18, 0.9, 0.8, 0.98) if highlighted else Color(0.42, 0.51, 0.51, 0.56)
		var route_width := 3.0 if highlighted else 1.1
		draw_polyline(points, route_color, route_width, true)
	for node_id_value in data.manifest.nodes:
		var record: Dictionary = data.manifest.nodes[node_id_value]
		var map_point := _world_to_map(P1AWorldData.xz(record.xz_m))
		var color := Color(0.95, 0.58, 0.18) if String(record.kind) == "GATE" else Color(0.18, 0.82, 0.72)
		draw_circle(map_point, 3.0, color)
	if craft != null:
		var p := _world_to_map(Vector2(craft.global_position.x, craft.global_position.z))
		var forward := Vector2(-craft.global_basis.z.x, -craft.global_basis.z.z).normalized()
		var tip := p + Vector2(forward.x, -forward.y) * 9.0
		draw_circle(p, 4.5, Color.WHITE)
		draw_line(p, tip, Color.WHITE, 2.0)
	# North-up orientation marker.
	draw_string(ThemeDB.fallback_font, Vector2(12.0, 20.0), "N ↑", HORIZONTAL_ALIGNMENT_LEFT, -1.0, 14, Color(0.88, 0.92, 0.90))
	draw_string(ThemeDB.fallback_font, Vector2(12.0, size.y - 10.0), "active route", HORIZONTAL_ALIGNMENT_LEFT, -1.0, 12, Color(0.18, 0.9, 0.8, 0.9))


func _world_to_map(world: Vector2) -> Vector2:
	var margin := 12.0
	var usable := size - Vector2.ONE * margin * 2.0
	var normalized := (world - WORLD_MIN) / (WORLD_MAX - WORLD_MIN)
	return Vector2(margin + normalized.x * usable.x, margin + (1.0 - normalized.y) * usable.y)
