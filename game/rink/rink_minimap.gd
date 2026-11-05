extends Control
## Small top-down map of the Hem Loop: lap outline, gates, craft and story marks.

var outline: PackedVector2Array = PackedVector2Array()
var gate_points: Array = []
var craft_point := Vector2.ZERO
var craft_heading := Vector2.UP
var marks: Array = []  # [world Vector2, Color]
var _min := Vector2.ZERO
var _scale := 1.0
var _offset := Vector2.ZERO


func _ready() -> void:
	mouse_filter = Control.MOUSE_FILTER_IGNORE


func configure(course) -> void:
	var lo := Vector2(INF, INF)
	var hi := Vector2(-INF, -INF)
	outline.clear()
	for i in range(0, course.samples.size(), 4):
		var p: Vector2 = course.samples[i].p
		outline.append(p)
		lo = Vector2(minf(lo.x, p.x), minf(lo.y, p.y))
		hi = Vector2(maxf(hi.x, p.x), maxf(hi.y, p.y))
	outline.append(course.samples[0].p)
	var pad := Vector2(14, 14)
	var span := hi - lo
	_scale = minf((size.x - pad.x * 2.0) / span.x, (size.y - pad.y * 2.0) / span.y)
	_min = lo
	_offset = pad + ((size - pad * 2.0) - span * _scale) * 0.5
	gate_points.clear()
	for g in course.gates:
		gate_points.append([g.a, g.b])
	queue_redraw()


func to_map(p: Vector2) -> Vector2:
	return _offset + (p - _min) * _scale


func set_craft(p: Vector2, heading: Vector2) -> void:
	craft_point = p
	craft_heading = heading
	queue_redraw()


func _draw() -> void:
	draw_rect(Rect2(Vector2.ZERO, size), Color(0.012, 0.024, 0.034, 0.78))
	draw_rect(Rect2(Vector2.ZERO, size), Color(0.13, 0.7, 0.66, 0.7), false, 1.0)
	if outline.size() < 2:
		return
	var pts := PackedVector2Array()
	for p in outline:
		pts.append(to_map(p))
	draw_polyline(pts, Color(0.55, 0.6, 0.58, 0.9), 5.0, true)
	draw_polyline(pts, Color(0.16, 0.2, 0.21, 1.0), 3.0, true)
	for i in gate_points.size():
		var g: Array = gate_points[i]
		var tint := Color(0.96, 0.96, 0.92) if i == 0 else Color(0.13, 0.74, 0.69, 0.9)
		draw_line(to_map(g[0]), to_map(g[1]), tint, 2.0 if i == 0 else 1.0)
	for m in marks:
		draw_circle(to_map(m[0]), 6.5, Color(0.0, 0.0, 0.0, 0.6))
		draw_circle(to_map(m[0]), 5.0, m[1])
		draw_arc(to_map(m[0]), 8.5, 0.0, TAU, 20, m[1], 1.5, true)
	var c := to_map(craft_point)
	draw_circle(c, 4.5, Color(0.96, 0.96, 0.92))
	draw_line(c, c + craft_heading.normalized() * 10.0, Color(0.96, 0.96, 0.92), 2.0)
