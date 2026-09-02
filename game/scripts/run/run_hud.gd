extends CanvasLayer

var _live_panel: PanelContainer
var _live_label: Label
var _countdown_label: Label
var _results_panel: PanelContainer
var _results_label: Label


func _ready() -> void:
	layer = 40
	_build_live_panel()
	_build_countdown()
	_build_results_panel()
	hide_all()


func hide_all() -> void:
	_live_panel.visible = false
	_countdown_label.visible = false
	_results_panel.visible = false


func show_countdown(value: String) -> void:
	_live_panel.visible = false
	_results_panel.visible = false
	_countdown_label.text = value
	_countdown_label.visible = true


func show_live(run_time_s: float, brrr: float, streak_s: float) -> void:
	_countdown_label.visible = false
	_results_panel.visible = false
	_live_label.text = "→ RLY\n%s   BRRR %s\nSTREAK ×%.2f" % [
		_format_time(run_time_s),
		_format_integer(int(round(brrr))),
		1.0 + minf(streak_s, 10.0) / 10.0,
	]
	_live_panel.visible = true


func show_results(stats: Dictionary) -> void:
	_live_panel.visible = false
	_countdown_label.visible = false
	_results_label.text = (
		"QRY → RLY\n"
		+ "%s          BEST TIME %s\n" % [
			_format_time(float(stats.time_s)),
			_format_time(float(stats.best_time_s)),
		]
		+ "BRRR %s       BEST BRRR %s\n" % [
			_format_integer(int(round(float(stats.brrr)))),
			_format_integer(int(round(float(stats.best_brrr)))),
		]
		+ "Drive %.1f s · peak %.1f m/s · crab %.0f° · streak %.1f s · impacts %d\n\n" % [
			float(stats.drive_seconds),
			float(stats.peak_speed),
			float(stats.peak_split_degrees),
			float(stats.longest_streak_s),
			int(stats.impacts),
		]
		+ "[ R ] RETRY      [ F ] FREE ROAM"
	)
	_results_panel.visible = true


func _build_live_panel() -> void:
	_live_panel = PanelContainer.new()
	_live_panel.name = "LivePanel"
	_live_panel.set_anchors_preset(Control.PRESET_TOP_LEFT)
	_live_panel.offset_left = 610.0
	_live_panel.offset_top = 18.0
	_live_panel.offset_right = 970.0
	_live_panel.offset_bottom = 94.0
	_live_panel.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_live_panel.add_theme_stylebox_override("panel", _panel_style(Color(0.12, 0.78, 0.72, 0.88)))
	_live_label = Label.new()
	_live_label.name = "Readout"
	_live_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_live_label.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	_live_label.add_theme_font_size_override("font_size", 16)
	_live_label.add_theme_color_override("font_color", Color(0.9, 0.97, 0.98, 1.0))
	_live_panel.add_child(_live_label)
	add_child(_live_panel)


func _build_countdown() -> void:
	_countdown_label = Label.new()
	_countdown_label.name = "Countdown"
	_countdown_label.set_anchors_preset(Control.PRESET_CENTER)
	_countdown_label.offset_left = -120.0
	_countdown_label.offset_top = -72.0
	_countdown_label.offset_right = 120.0
	_countdown_label.offset_bottom = 72.0
	_countdown_label.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_countdown_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_countdown_label.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	_countdown_label.add_theme_font_size_override("font_size", 64)
	_countdown_label.add_theme_color_override("font_color", Color(1.0, 0.75, 0.24, 1.0))
	_countdown_label.add_theme_color_override("font_shadow_color", Color(0.0, 0.0, 0.0, 0.9))
	_countdown_label.add_theme_constant_override("shadow_offset_x", 3)
	_countdown_label.add_theme_constant_override("shadow_offset_y", 3)
	add_child(_countdown_label)


func _build_results_panel() -> void:
	_results_panel = PanelContainer.new()
	_results_panel.name = "ResultsPanel"
	_results_panel.set_anchors_preset(Control.PRESET_CENTER)
	_results_panel.offset_left = -340.0
	_results_panel.offset_top = -125.0
	_results_panel.offset_right = 340.0
	_results_panel.offset_bottom = 125.0
	_results_panel.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_results_panel.add_theme_stylebox_override("panel", _panel_style(Color(1.0, 0.65, 0.18, 0.92)))
	_results_label = Label.new()
	_results_label.name = "Results"
	_results_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_results_label.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	_results_label.add_theme_font_size_override("font_size", 20)
	_results_label.add_theme_color_override("font_color", Color(0.93, 0.97, 0.98, 1.0))
	_results_panel.add_child(_results_label)
	add_child(_results_panel)


func _panel_style(border_color: Color) -> StyleBoxFlat:
	var style := StyleBoxFlat.new()
	style.bg_color = Color(0.012, 0.022, 0.031, 0.92)
	style.border_color = border_color
	style.set_border_width_all(2)
	style.set_corner_radius_all(6)
	style.content_margin_left = 16.0
	style.content_margin_top = 10.0
	style.content_margin_right = 16.0
	style.content_margin_bottom = 10.0
	return style


func _format_time(seconds: float) -> String:
	var hundredths := maxi(0, int(floor(seconds * 100.0 + 0.5)))
	var minutes := hundredths / 6000
	var remainder := hundredths % 6000
	return "%d:%02d.%02d" % [minutes, remainder / 100, remainder % 100]


func _format_integer(value: int) -> String:
	var digits := str(maxi(0, value))
	var grouped := ""
	for index in digits.length():
		if index > 0 and (digits.length() - index) % 3 == 0:
			grouped += ","
		grouped += digits[index]
	return grouped
