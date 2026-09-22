extends CanvasLayer
signal primary
signal secondary
var readout: Label
var card: PanelContainer
var title: Label
var body: Label
var action: Button
var back: Button
var hint: Label

func _ready() -> void:
	layer = 45
	var strip := PanelContainer.new()
	strip.position = Vector2(18,18)
	strip.custom_minimum_size = Vector2(480,78)
	strip.mouse_filter = Control.MOUSE_FILTER_IGNORE
	strip.add_theme_stylebox_override("panel",_style())
	readout = Label.new()
	readout.add_theme_font_size_override("font_size",17)
	strip.add_child(readout)
	add_child(strip)
	card = PanelContainer.new()
	card.set_anchors_preset(Control.PRESET_CENTER)
	card.offset_left = -285
	card.offset_top = -200
	card.offset_right = 285
	card.offset_bottom = 200
	card.add_theme_stylebox_override("panel",_style())
	var content := VBoxContainer.new()
	content.add_theme_constant_override("separation",18)
	card.add_child(content)
	title = Label.new()
	title.add_theme_font_size_override("font_size",27)
	title.add_theme_color_override("font_color",Color("efc07f"))
	content.add_child(title)
	body = Label.new()
	body.add_theme_font_size_override("font_size",18)
	body.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	body.custom_minimum_size.x = 520
	content.add_child(body)
	action = Button.new()
	action.custom_minimum_size.y = 44
	action.focus_mode = Control.FOCUS_NONE
	action.pressed.connect(func(): primary.emit())
	content.add_child(action)
	back = Button.new()
	back.text = "Back to the street · Esc"
	back.focus_mode = Control.FOCUS_NONE
	back.pressed.connect(func(): secondary.emit())
	content.add_child(back)
	add_child(card)
	hint = Label.new()
	hint.position = Vector2(18,660)
	hint.add_theme_font_size_override("font_size",14)
	hint.add_theme_color_override("font_shadow_color",Color.BLACK)
	hint.add_theme_constant_override("shadow_offset_x",1)
	hint.add_theme_constant_override("shadow_offset_y",1)
	add_child(hint)

func refresh(job: Node) -> void:
	card.visible = job.state in ["DISPATCH","RESULTS","PAUSED","WAIT_NEUTRAL"]
	readout.get_parent().visible = not card.visible
	action.visible = job.state != "WAIT_NEUTRAL"
	back.visible = job.state == "DISPATCH"
	hint.text = "W/S drive/brake · A/D steer · Shift form · Space Hop · R reset · Esc pause\nCOURIER SLICE v1 · OWNER REVIEW"
	match job.state:
		"FREE_ROAM":
			readout.text = "FREE ROAM · MARKET DISPATCH\n"+("E / Enter / B  ·  Open Dispatch" if job.can_dispatch() else "Return to Market’s inner pad and slow to collect.")
		"ACTIVE":
			var distance: float = job._xz().distance_to(job.destination)
			readout.text = "PARCEL → DEPOT   ·   %.0f m\nCondition %.1f%%   ·   %s   ·   BRRR %.0f" % [distance,job.cargo.condition_units/10.0,time_text(job.elapsed),job.brrr]
			if distance<=job.destination_radius:
				readout.text += "\n"+("Receiving…" if job.settle>0 else "Settle on the pad below 6 m/s to deliver.")
		"DISPATCH":
			title.text = "Market → Depot"
			body.text = "One parcel: replacement seals for the freight office.\n\nChoose your own route. There is no time limit.\nSettle on Depot’s inner pad to hand it over.\n\nHeavy impacts affect the parcel. Even a damaged parcel can be delivered. BRRR stays separate."
			action.text = "Accept parcel · Enter / B"
		"RESULTS":
			var result: Dictionary = job.last_result
			title.text = result.message
			body.text = "Cargo condition   %.1f%%\nActive delivery time   %s\nObstacle episodes   %d   ·   impact samples   %d\n\nBRRR   %.0f\nLongest BRRR streak   %.1f s   ·   peak   %.1f m/s\n\n%s" % [result.condition_units/10.0,time_text(result.elapsed),result.episodes,result.impact_samples,result.brrr,result.longest_streak,result.peak_speed,"Thanks. The freight office will take it from here." if result.delivered else "No delivery recorded. You can collect again at Market."]
			action.text = "Continue in free roam · Enter / B"
		"PAUSED":
			title.text = "Paused"
			body.text = "The parcel and clock wait with you.\n\nR resets the craft and returns any active parcel."
			action.text = "Resume · Esc / Enter / B"
		"WAIT_NEUTRAL":
			title.text = "Ready when you are"
			body.text = "Release the controls to return to the street."

static func time_text(seconds: float) -> String:
	var whole := maxi(0,int(seconds))
	return "%d:%02d" % [whole/60,whole%60]

func _style() -> StyleBoxFlat:
	var style := StyleBoxFlat.new()
	style.bg_color = Color(0.035,0.052,0.055,0.96)
	style.border_color = Color("698a86")
	style.set_border_width_all(1)
	style.set_corner_radius_all(5)
	style.content_margin_left = 18
	style.content_margin_right = 18
	style.content_margin_top = 14
	style.content_margin_bottom = 14
	return style
