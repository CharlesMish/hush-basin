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
	board=panel(Vector2(1120,610))
	var content:=VBoxContainer.new();content.add_theme_constant_override("separation",8);board.add_child(content)
	board_heading=label(25);board_heading.add_theme_color_override("font_color",Color("efc07f"));content.add_child(board_heading)
	var sub:=label(14);sub.text="CHOOSE 1–5  ·  then Enter / B to accept  ·  Any legal route  ·  Bonuses are optional";content.add_child(sub)
	var row:=GridContainer.new();row.columns=2;row.add_theme_constant_override("h_separation",12);row.add_theme_constant_override("v_separation",8);content.add_child(row)
	for i in Catalog.JOBS.size():
		var contract: Dictionary=Catalog.JOBS[i]
		var button:=Button.new()
		button.custom_minimum_size=Vector2(528,94)
		button.add_theme_font_size_override("font_size",15)
		button.text="%d   %s · %s\n%s\nDelivery +%d   /   %s bonus +%d" % [i+1,String(contract.place).to_upper(),contract.name,contract.character,contract.base,contract.objective,contract.bonus]
		button.focus_mode=Control.FOCUS_NONE
		button.pressed.connect(func():select_job.emit(i))
		row.add_child(button);cards.append(button)
	notice=label(14);notice.custom_minimum_size=Vector2(1056,42);notice.autowrap_mode=TextServer.AUTOWRAP_WORD_SMART;content.add_child(notice)
	var actions:=HBoxContainer.new();actions.add_theme_constant_override("separation",12);content.add_child(actions)
	var accept:=button("Accept selected · Enter / B",func():primary.emit());accept.custom_minimum_size.x=310;actions.add_child(accept)
	buy=button("",func():purchase.emit());buy.custom_minimum_size.x=424;actions.add_child(buy)
	actions.add_child(button("Back · Esc",func():secondary.emit()))
	var foot:=label(13);foot.text="Liner: 25% less cargo loss only. No handling changes. Credits and liner reset when you close the app.";content.add_child(foot)
	card=panel(Vector2(650,492))
	var stack:=VBoxContainer.new();stack.add_theme_constant_override("separation",14);card.add_child(stack)
	title=label(26);title.add_theme_color_override("font_color",Color("efc07f"));stack.add_child(title)
	body=label(16);body.custom_minimum_size.x=562;body.autowrap_mode=TextServer.AUTOWRAP_WORD_SMART;stack.add_child(body)
	action=button("",func():primary.emit());stack.add_child(action)
	hint=label(13);hint.position=Vector2(18,662);add_child(hint)

func refresh(job: Node) -> void:
	board.visible=job.state=="DISPATCH"
	card.visible=job.state in ["RESULTS","PAUSED","WAIT_NEUTRAL"]
	readout.get_parent().visible=not board.visible and not card.visible
	action.visible=job.state!="WAIT_NEUTRAL"
	hint.text="W/S thrust/brake · A/D steer · Shift form · Space Hop · R reset · Esc pause\nMECHANICS RANGE V1.1 · F2 cargo receipts · F3 bookmark contact · session only"
	hint.visible=not board.visible
	if board.visible:
		board_heading.text="MARKET DISPATCH                       %d Credits" % job.session.balance
		for i in Catalog.JOBS.size():
			cards[i].add_theme_stylebox_override("normal",style(i==job.selected))
			cards[i].add_theme_stylebox_override("hover",style(true))
		notice.text=String(Catalog.JOBS[job.selected].objective_text)+"\n"+job.board_notice
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
			if job.elapsed<4:readout.text+="\n"+String(c.dispatch)
			if distance<=job.destination_radius:readout.text+="\n"+("Receiving…" if job.settle>0 else "Settle below 6 m/s to deliver.")
		"RESULTS":
			var r: Dictionary=job.last_result
			title.text="Delivered · "+r.place if r.delivered else "Parcel returned"
			body.text="%s\nCargo  %.1f%%  ·  Active time  %s\n\n%s  ·  %s\nDELIVERY  +%d\nOPTIONAL OBJECTIVE  +%d\nTOTAL  +%d    /    SESSION  %d Credits\n\nBRRR  %.0f  ·  Longest BRRR streak  %.1f s\nDrift combo  %.2f s  ·  Clean Drive  %.0f m\nPeak  %.1f m/s  ·  Impact episodes  %d\n%s\n\n%s" % [r.job_name,r.condition_units/10.0,OldHud.time_text(r.elapsed),r.objective,"Achieved" if r.objective_met else "Not achieved · delivery still counts" if r.delivered else "No delivery",r.base_credits,r.bonus_credits,r.total_credits,r.session_balance,r.brrr,r.longest_streak,r.get("best_drift_s",0),r.get("best_drive_m",0),r.peak_speed,r.episodes,"Liner saved %.1f condition points" % (r.protection_saved_units/10.0) if r.liner_owned else "Slip BRRR %.0f · no extra payout terms." % r.get("slip_brrr",0),String(r.get("reaction",""))+" Drive home when ready." if r.delivered else "No Credits charged or awarded. Collect again at Market."]
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
		"STYLE":return "STYLE +%d · drift %.2f / %.1f s · %s" % [c.bonus,job.lines.best_drift_s,c.target,job.lines.reason]
		"COMMIT":return "COMMIT +%d · clean Drive %.0f / %.0f m" % [c.bonus,job.lines.best_drive_m,c.target]
		"CARE":return "CARE +%d · arrive with at least %d%%" % [c.bonus,c.target/10]
		"THREAD":return "THREAD +%d · %s" % [c.bonus,"South crossing met" if job.lines.thread_complete else "Crossing · keep Spread clean" if job.lines.thread_active else "South Cut · Spread, Hop or dogleg"]
		"HAUL":
			var phase: int=job.lines.haul_phase
			return "HAUL +%d · %s" % [c.bonus,"Both Drive legs met" if phase==3 else "Drive leg 2 · %.0f / 90 m" % job.lines.second_leg_m if phase==2 else "Spread transfer · %.0f / 40 m" % job.lines.transfer_m if phase==1 else "Drive leg 1 · %.0f / 160 m" % job.lines.clean_drive_m]
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
