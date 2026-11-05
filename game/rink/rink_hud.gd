extends CanvasLayer
## Hem Loop heads-up display. Everything here is presentation: it reads the
## director's state and never touches craft simulation.

const Timing = preload("res://rink/rink_timing.gd")
const TEAL := Color(0.13, 0.74, 0.69)
const AMBER := Color(0.98, 0.72, 0.3)
const GOOD := Color(0.42, 0.93, 0.55)
const BAD := Color(1.0, 0.5, 0.42)
const PALE := Color(0.9, 0.92, 0.9)

var lap_title: Label
var lap_clock: Label
var lap_lines: Label
var message: Label
var result_line: Label
var story_panel: PanelContainer
var story_portrait: TextureRect
var story_speaker: Label
var story_text: Label
var form_label: Label
var hint: Label
var entry: PanelContainer
var entry_body: Label
var pause_panel: PanelContainer
var pause_body: Label
var map: Control
var _message_until := 0.0
var _result_until := 0.0
var _story_until := 0.0
var _now := 0.0


func _ready() -> void:
	layer = 10
	process_mode = Node.PROCESS_MODE_ALWAYS
	var root := Control.new()
	root.set_anchors_preset(Control.PRESET_FULL_RECT)
	root.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(root)

	var lap_panel := _panel(root, Vector2(22, 18), Vector2(300, 0))
	var lap_box := VBoxContainer.new()
	lap_box.add_theme_constant_override("separation", 0)
	lap_panel.add_child(lap_box)
	lap_title = _text(lap_box, "HEM LOOP · TIME TRIAL", 15, TEAL)
	lap_clock = _text(lap_box, "-:--.--", 44, PALE)
	lap_lines = _text(lap_box, "", 17, PALE)

	message = _text(root, "", 26, PALE)
	message.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	message.position = Vector2(340, 26)
	message.size = Vector2(600, 40)
	_shadow(message)

	result_line = _text(root, "", 20, PALE)
	result_line.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	result_line.position = Vector2(290, 66)
	result_line.size = Vector2(700, 60)
	_shadow(result_line)

	story_panel = _panel(root, Vector2(330, 120), Vector2(620, 0))
	var story_row := HBoxContainer.new()
	story_row.add_theme_constant_override("separation", 12)
	story_panel.add_child(story_row)
	story_portrait = TextureRect.new()
	story_portrait.custom_minimum_size = Vector2(64, 64)
	story_portrait.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	story_portrait.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_COVERED
	story_row.add_child(story_portrait)
	var story_col := VBoxContainer.new()
	story_col.add_theme_constant_override("separation", 2)
	story_col.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	story_row.add_child(story_col)
	story_speaker = _text(story_col, "", 14, TEAL)
	story_text = _text(story_col, "", 22, PALE)
	story_text.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	story_text.custom_minimum_size = Vector2(520, 0)
	story_panel.visible = false

	form_label = _text(root, "", 22, PALE)
	form_label.position = Vector2(26, 660)
	_shadow(form_label)

	hint = _text(root, "", 16, Color(0.85, 0.88, 0.85, 0.9))
	hint.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	hint.position = Vector2(240, 686)
	hint.size = Vector2(800, 24)
	_shadow(hint)

	map = preload("res://rink/rink_minimap.gd").new()
	map.position = Vector2(1032, 18)
	map.size = Vector2(228, 164)
	root.add_child(map)

	entry = _panel(root, Vector2(22, 200), Vector2(430, 0))
	entry_body = _text(entry, "", 17, PALE)
	entry_body.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	entry_body.custom_minimum_size = Vector2(400, 0)

	pause_panel = _panel(root, Vector2(440, 230), Vector2(400, 0))
	pause_body = _text(pause_panel, "", 20, PALE)
	pause_body.custom_minimum_size = Vector2(360, 0)
	pause_panel.visible = false


func _panel(parent: Control, at: Vector2, min_size: Vector2) -> PanelContainer:
	var panel := PanelContainer.new()
	var style := StyleBoxFlat.new()
	style.bg_color = Color(0.018, 0.028, 0.038, 0.82)
	style.border_width_left = 3
	style.border_color = Color(TEAL, 0.85)
	style.set_corner_radius_all(5)
	style.content_margin_left = 14
	style.content_margin_right = 14
	style.content_margin_top = 9
	style.content_margin_bottom = 9
	panel.add_theme_stylebox_override("panel", style)
	panel.position = at
	panel.custom_minimum_size = min_size
	panel.mouse_filter = Control.MOUSE_FILTER_IGNORE
	parent.add_child(panel)
	return panel


func _text(parent: Control, text: String, font_size: int, tint: Color) -> Label:
	var label := Label.new()
	label.text = text
	label.add_theme_font_size_override("font_size", font_size)
	label.add_theme_color_override("font_color", tint)
	label.mouse_filter = Control.MOUSE_FILTER_IGNORE
	parent.add_child(label)
	return label


func _shadow(label: Label) -> void:
	label.add_theme_color_override("font_shadow_color", Color(0, 0, 0, 0.75))
	label.add_theme_constant_override("shadow_offset_x", 2)
	label.add_theme_constant_override("shadow_offset_y", 2)


func tick(now: float) -> void:
	_now = now
	if message.text != "" and now > _message_until:
		message.text = ""
	if result_line.text != "" and now > _result_until:
		result_line.text = ""
	if story_panel.visible and now > _story_until:
		story_panel.visible = false


func flash(text: String, tint: Color = PALE, seconds: float = 2.2) -> void:
	message.text = text
	message.add_theme_color_override("font_color", tint)
	_message_until = _now + seconds


func show_result(text: String, tint: Color, seconds: float = 4.0) -> void:
	result_line.text = text
	result_line.add_theme_color_override("font_color", tint)
	_result_until = _now + seconds


func say(speaker: String, line: String, portrait: Texture2D, seconds: float) -> void:
	story_speaker.text = speaker
	story_text.text = line
	story_portrait.texture = portrait
	story_portrait.visible = portrait != null
	story_panel.visible = true
	_story_until = _now + seconds


func story_visible() -> bool:
	return story_panel.visible


func set_lap(title: String, clock_text: String, lines: String) -> void:
	lap_title.text = title
	lap_clock.text = clock_text
	lap_lines.text = lines


func set_form(text: String) -> void:
	form_label.text = text
