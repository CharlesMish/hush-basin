extends Control

var _destination_xz := Vector2.ZERO
var _destination_label := "RLY"


func _ready() -> void:
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	resized.connect(queue_redraw)
	queue_redraw()


func configure(destination_xz: Vector2, destination_label: String) -> void:
	_destination_xz = destination_xz
	_destination_label = destination_label
	queue_redraw()


func _draw() -> void:
	if size.x <= 0.0 or size.y <= 0.0:
		return
	var margin := 12.0
	var usable := size - Vector2.ONE * margin * 2.0
	var normalized := (
		(_destination_xz - P1AMap.WORLD_MIN)
		/ (P1AMap.WORLD_MAX - P1AMap.WORLD_MIN)
	)
	var marker := Vector2(
		margin + normalized.x * usable.x,
		margin + (1.0 - normalized.y) * usable.y
	)
	draw_circle(marker, 8.0, Color(1.0, 0.68, 0.18, 0.18))
	draw_arc(marker, 8.0, 0.0, TAU, 32, Color(1.0, 0.68, 0.18, 0.98), 2.0, true)
	draw_circle(marker, 2.5, Color(1.0, 0.82, 0.38, 1.0))
	draw_string(
		ThemeDB.fallback_font,
		marker + Vector2(10.0, 4.0),
		_destination_label,
		HORIZONTAL_ALIGNMENT_LEFT,
		-1.0,
		12,
		Color(1.0, 0.86, 0.52, 1.0)
	)
