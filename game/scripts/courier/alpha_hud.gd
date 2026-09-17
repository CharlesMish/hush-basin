extends CanvasLayer
signal primary
signal secondary
signal select_job(index: int)
signal purchase
const Catalog=preload("res://scripts/courier/alpha_contracts.gd")
const OldHud=preload("res://scripts/courier/courier_hud.gd")
var readout: Label
var board: PanelContainer
var board_heading: Label
var cards: Array[Button]=[]
var notice: Label
var buy: Button
var card: PanelContainer
var title: Label
var body: Label
var action: Button
var hint: Label
func _ready() -> void:
	layer=45
	var strip:=PanelContainer.new()
	strip.position=Vector2(18,18);strip.custom_minimum_size=Vector2(474,100)
	strip.mouse_filter=Control.MOUSE_FILTER_IGNORE
	strip.add_theme_stylebox_override("panel",style())
	readout=label(16);strip.add_child(readout);add_child(strip)
	board=panel(Vector2(1030,414))
	var content:=VBoxContainer.new();content.add_theme_constant_override("separation",14);board.add_child(content)
	board_heading=label(25);board_heading.add_theme_color_override("font_color",Color("efc07f"));content.add_child(board_heading)
	var sub:=label(14);sub.text="CHOOSE 1 / 2 / 3  ·  then Enter / B to accept  ·  Any legal route  ·  Bonuses are optional";content.add_child(sub)
	var row:=HBoxContainer.new();row.add_theme_constant_override("separation",12);content.add_child(row)
	for i in 3:
		var contract: Dictionary=Catalog.JOBS[i]
		var button:=Button.new()
		button.custom_minimum_size=Vector2(322,176)
		button.add_theme_font_size_override("font_size",16)
		button.text="%d   MARKET > %s\n%s\n%s\n\nDelivery  +%d Credits\n%s  +%d\n%s" % [i+1,String(contract.place).to_upper(),contract.name,contract.character,contract.base,contract.objective,contract.bonus,contract.objective_text]
		button.focus_mode=Control.FOCUS_NONE
		button.pressed.connect(func():select_job.emit(i))
		row.add_child(button);cards.append(button)
	notice=label(14);content.add_child(notice)
	var actions:=HBoxContainer.new();actions.add_theme_constant_override("separation",12);content.add_child(actions)
	var accept:=button("Accept selected · Enter / B",func():primary.emit());accept.custom_minimum_size.x=310;actions.add_child(accept)
	buy=button("",func():purchase.emit());buy.custom_minimum_size.x=424;actions.add_child(buy)
	actions.add_child(button("Back · Esc",func():secondary.emit()))
	var foot:=label(13);foot.text="Liner: 25% less cargo loss only. No handling changes. Credits and liner reset when you close the app.";content.add_child(foot)
	card=panel(Vector2(610,458))
	var stack:=VBoxContainer.new();stack.add_theme_constant_override("separation",14);card.add_child(stack)
	title=label(26);title.add_theme_color_override("font_color",Color("efc07f"));stack.add_child(title)
	body=label(17);body.custom_minimum_size.x=562;body.autowrap_mode=TextServer.AUTOWRAP_WORD_SMART;stack.add_child(body)
	action=button("",func():primary.emit());stack.add_child(action)
	hint=label(13);hint.position=Vector2(18,662);add_child(hint)

func refresh(job: Node) -> void:
	board.visible=job.state=="DISPATCH"
	card.visible=job.state in ["RESULTS","PAUSED","WAIT_NEUTRAL"]
	readout.get_parent().visible=not board.visible and not card.visible
	action.visible=job.state!="WAIT_NEUTRAL"
	hint.text="W/S thrust/brake · A/D steer · Shift form · Space Hop · R reset · Esc pause\nALPHA LOOP · F2 cargo receipts · F3 bookmark contact · session only"
	if board.visible:
		board_heading.text="MARKET DISPATCH                       %d Credits" % job.session.balance
		for i in 3:
			cards[i].add_theme_stylebox_override("normal",style(i==job.selected))
			cards[i].add_theme_stylebox_override("hover",style(true))
		notice.text=job.board_notice
		buy.text="Cargo liner installed · 25% protection" if job.session.liner_owned else "Buy cargo liner · %d Credits · C" % Catalog.LINER_PRICE
		buy.disabled=job.session.liner_owned or job.session.balance<Catalog.LINER_PRICE
	match job.state:
		"FREE_ROAM":
			var distance: float=job._xz().distance_to(job.origin)
			readout.text="MARKET HOME  ·  %d Credits%s\n%s" % [job.session.balance,"  ·  Liner fitted" if job.session.liner_owned else "","E / Enter / B  ·  Open Dispatch" if job.can_dispatch() else "Market  %.0f m · look for the warm rooftop crown" % distance]
		"ACTIVE":
			var c: Dictionary=job.contract
			var distance: float=job._xz().distance_to(job.destination)
			readout.text="%s > %s  ·  %.0f m\nCargo %.1f%% · %s · %d Credits%s\n%s" % [c.name.to_upper(),String(c.place).to_upper(),distance,job.cargo.condition_units/10.0,OldHud.time_text(job.elapsed),job.session.balance," · Liner" if job.cargo.protected else "",objective_progress(job)]
			if distance<=job.destination_radius:readout.text+="\n"+("Receiving…" if job.settle>0 else "Settle below 6 m/s to deliver.")
		"RESULTS":
			var r: Dictionary=job.last_result
			title.text="Delivered · "+r.place if r.delivered else "Parcel returned"
			body.text="%s\nCargo  %.1f%%  ·  Active time  %s\n\n%s  ·  %s\nDELIVERY  +%d\nOPTIONAL OBJECTIVE  +%d\nTOTAL  +%d    /    SESSION  %d Credits\n\nBRRR  %.0f  ·  Longest streak  %.1f s\nPeak  %.1f m/s  ·  Impact episodes  %d\n%s\n\n%s" % [r.job_name,r.condition_units/10.0,OldHud.time_text(r.elapsed),r.objective,"Achieved" if r.objective_met else "Not achieved · delivery still counts" if r.delivered else "No delivery",r.base_credits,r.bonus_credits,r.total_credits,r.session_balance,r.brrr,r.longest_streak,r.peak_speed,r.episodes,"Liner saved %.1f condition points" % (r.protection_saved_units/10.0) if r.liner_owned else "No extra payout terms.","Drive back to Market when you want another job." if r.delivered else "No Credits charged or awarded. Collect again at Market."]
			action.text="Continue here · Enter / B"
		"PAUSED":
			title.text="Paused"
			body.text="Parcel and clock wait with you.\nSession balance: %d Credits.\n\nR resets the craft and returns any active parcel.\nIt cannot award a delivery." % job.session.balance
			action.text="Resume · Esc / Enter / B"
		"WAIT_NEUTRAL":
			title.text="Ready when you are"
			body.text="Release the controls to return to the street."

func objective_progress(job: Node) -> String:
	var c: Dictionary=job.contract
	match c.objective:
		"STYLE":return "Optional STYLE +%d · streak %.1f / %.1f s%s" % [c.bonus,job.longest_streak,c.target," · met" if job.longest_streak+0.000000001>=c.target else ""]
		"EXPRESS":return "Optional EXPRESS +%d · target %s%s" % [c.bonus,OldHud.time_text(c.target)," · base delivery remains" if job.elapsed>c.target else ""]
		"CARE":return "Optional CARE +%d · arrive with at least %d%%" % [c.bonus,c.target/10]
	return ""
func label(size: int) -> Label:
	var l:=Label.new();l.add_theme_font_size_override("font_size",size);return l
func button(text: String, callback: Callable) -> Button:
	var b:=Button.new();b.text=text;b.custom_minimum_size.y=42;b.focus_mode=Control.FOCUS_NONE;b.pressed.connect(callback);return b
func panel(size: Vector2) -> PanelContainer:
	var p:=PanelContainer.new();p.set_anchors_preset(Control.PRESET_CENTER)
	p.offset_left=-size.x*.5;p.offset_top=-size.y*.5;p.offset_right=size.x*.5;p.offset_bottom=size.y*.5
	p.add_theme_stylebox_override("panel",style());add_child(p);return p
func style(selected: bool=false) -> StyleBoxFlat:
	var s:=StyleBoxFlat.new();s.bg_color=Color("234b45") if selected else Color(.035,.052,.055,.96);s.border_color=Color("efc07f") if selected else Color("698a86")
	s.set_border_width_all(2 if selected else 1);s.set_corner_radius_all(5)
	s.content_margin_left=16;s.content_margin_right=16;s.content_margin_top=12;s.content_margin_bottom=12
	return s
