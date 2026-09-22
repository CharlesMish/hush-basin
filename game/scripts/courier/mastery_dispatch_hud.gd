extends "res://scripts/courier/alpha_hud.gd"
## Presentation adapter: three visible neighbors, with the selection in the middle.
## All ordinary contracts remain accessible. This node never settles a receipt.
signal cosmetic
var mastery_state: RefCounted
var mastery_receipt: Dictionary = {}
var visible_indices: Array[int] = []
var card_labels: Array[Dictionary] = []
var collection: Label
var browse_position: Label
var objective_detail: Label
var mastery_result: Label
var reward: Button
var selected_index := 0

func _ready() -> void:
	layer = 45
	var strip := PanelContainer.new()
	strip.position = Vector2(18,18)
	strip.custom_minimum_size = Vector2(474,100)
	strip.mouse_filter = Control.MOUSE_FILTER_IGNORE
	strip.add_theme_stylebox_override("panel",style())
	readout = label(16)
	strip.add_child(readout)
	add_child(strip)
	board = panel(Vector2(1032,492))
	var content := VBoxContainer.new()
	content.add_theme_constant_override("separation",10)
	board.add_child(content)
	var heading_row := HBoxContainer.new()
	content.add_child(heading_row)
	board_heading = label(25)
	board_heading.text = "MARKET DISPATCH"
	board_heading.add_theme_color_override("font_color",Color("efc07f"))
	board_heading.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	heading_row.add_child(board_heading)
	collection = label(15)
	collection.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
	heading_row.add_child(collection)
	var browse := HBoxContainer.new()
	browse.add_theme_constant_override("separation",12)
	content.add_child(browse)
	var previous := button("<",func():select_job.emit(posmod(selected_index-1,Catalog.JOBS.size())))
	previous.custom_minimum_size.x = 44
	previous.custom_minimum_size.y = 28
	browse.add_child(previous)
	browse_position = label(14)
	browse_position.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	browse_position.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	browse.add_child(browse_position)
	var next := button(">",func():select_job.emit(posmod(selected_index+1,Catalog.JOBS.size())))
	next.custom_minimum_size.x = 44
	next.custom_minimum_size.y = 28
	browse.add_child(next)
	var row := HBoxContainer.new()
	row.add_theme_constant_override("separation",12)
	content.add_child(row)
	for slot in 3:
		var b := Button.new()
		b.custom_minimum_size = Vector2(320,148)
		b.focus_mode = Control.FOCUS_NONE
		b.pressed.connect(func():select_job.emit(visible_indices[slot]))
		row.add_child(b)
		cards.append(b)
		var margin := MarginContainer.new()
		margin.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
		for side in ["left","right"]:margin.add_theme_constant_override("margin_"+side,14)
		for side in ["top","bottom"]:margin.add_theme_constant_override("margin_"+side,10)
		margin.mouse_filter = Control.MOUSE_FILTER_IGNORE
		b.add_child(margin)
		var stack := VBoxContainer.new()
		stack.add_theme_constant_override("separation",4)
		stack.mouse_filter = Control.MOUSE_FILTER_IGNORE
		margin.add_child(stack)
		var fields := {}
		for field in ["place","name","kind","reward","stamp"]:
			var l := label(20 if field=="place" else 16 if field=="name" else 14)
			l.mouse_filter = Control.MOUSE_FILTER_IGNORE
			l.clip_text = true
			if field=="kind":l.add_theme_color_override("font_color",Color("b1cbc5"))
			if field=="stamp":l.add_theme_color_override("font_color",Color("efc07f"))
			stack.add_child(l)
			fields[field] = l
		card_labels.append(fields)
	objective_detail = label(16)
	objective_detail.custom_minimum_size = Vector2(984,44)
	objective_detail.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	content.add_child(objective_detail)
	var actions := HBoxContainer.new()
	actions.add_theme_constant_override("separation",10)
	content.add_child(actions)
	var accept := button("Accept selected · Enter / B",func():primary.emit())
	accept.custom_minimum_size.x = 308
	actions.add_child(accept)
	buy = button("",func():purchase.emit())
	buy.custom_minimum_size.x = 432
	actions.add_child(buy)
	actions.add_child(button("Back · Esc",func():secondary.emit()))
	reward = button("",func():cosmetic.emit())
	reward.custom_minimum_size.y = 30
	reward.add_theme_font_size_override("font_size",14)
	content.add_child(reward)
	notice = label(13)
	notice.custom_minimum_size = Vector2(984,34)
	notice.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	content.add_child(notice)
	card = panel(Vector2(672,492))
	var result_stack := VBoxContainer.new()
	result_stack.add_theme_constant_override("separation",12)
	card.add_child(result_stack)
	title = label(26)
	title.add_theme_color_override("font_color",Color("efc07f"))
	result_stack.add_child(title)
	mastery_result = label(16)
	mastery_result.add_theme_color_override("font_color",Color("efc07f"))
	mastery_result.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	mastery_result.custom_minimum_size.x = 620
	result_stack.add_child(mastery_result)
	body = label(16)
	body.custom_minimum_size.x = 620
	body.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	result_stack.add_child(body)
	action = button("",func():primary.emit())
	result_stack.add_child(action)
	hint = label(13)
	hint.position = Vector2(18,662)
	add_child(hint)

func refresh(job: Node) -> void:
	board.visible = job.state=="DISPATCH"
	card.visible = job.state in ["RESULTS","PAUSED","WAIT_NEUTRAL"]
	readout.get_parent().visible = not board.visible and not card.visible
	action.visible = job.state!="WAIT_NEUTRAL"
	mastery_result.visible = job.state=="RESULTS"
	hint.text = "W/S thrust/brake · A/D steer · Shift form · Space Hop · R reset · Esc pause\nMASTERY ALPHA · F2 cargo receipts · F3 bookmark contact · session only"
	hint.visible = not board.visible
	if board.visible:_refresh_board(job)
	match job.state:
		"FREE_ROAM":
			var distance: float = job._xz().distance_to(job.origin)
			readout.text = "MARKET HOME · %d Credits%s\n%s" % [job.session.balance," · Liner fitted" if job.session.liner_owned else "","E / Enter / B · Open Dispatch" if job.can_dispatch() else "Market %.0f m · look for the warm rooftop crown" % distance]
		"ACTIVE":
			var c: Dictionary = job.contract
			var distance: float = job._xz().distance_to(job.destination)
			readout.text = "%s > %s · %.0f m\nCargo %.1f%% · %s · %d Credits%s\n%s" % [c.name.to_upper(),String(c.place).to_upper(),distance,job.cargo.condition_units/10.0,OldHud.time_text(job.elapsed),job.session.balance," · Liner" if job.cargo.protected else "",objective_progress(job)]
			if job.elapsed<4:readout.text += "\n"+String(c.dispatch)
			if distance<=job.destination_radius:readout.text += "\n"+("Receiving…" if job.settle>0 else "Settle below 6 m/s to deliver.")
		"RESULTS":_refresh_results(job.last_result)
		"PAUSED":
			title.text = "Paused"
			body.text = "Parcel and clock wait with you.\nSession balance: %d Credits.\n\nR resets the craft and returns any active parcel.\nIt cannot award a delivery." % job.session.balance
			action.text = "Resume · Esc / Enter / B"
		"WAIT_NEUTRAL":
			title.text = "Ready when you are"
			body.text = "Release the controls to return to the street."

func _refresh_board(job: Node) -> void:
	selected_index = job.selected
	collection.text = "%d Credits   ·   %d / %d mastered" % [job.session.balance,_mastery_count(),Catalog.JOBS.size()]
	browse_position.text = "<  LEFT / RIGHT  >     %d / %d selected     ·     1–5 quick select     ·     All jobs replayable" % [selected_index+1,Catalog.JOBS.size()]
	visible_indices.clear()
	for slot in 3:
		var index: int = posmod(selected_index+slot-1,Catalog.JOBS.size())
		visible_indices.append(index)
		var c: Dictionary = Catalog.JOBS[index]
		var fields: Dictionary = card_labels[slot]
		fields.place.text = "%d  %s" % [index+1,String(c.place).to_upper()]
		fields.name.text = c.name
		fields.kind.text = _archetype(c)+" · "+_route_character(c)
		fields.reward.text = "Delivery +%d   /   optional +%d" % [c.base,c.bonus]
		var status := _status(String(c.id))
		fields.stamp.text = "[SEAL] Mastered · replay welcome" if status.get("mastered",false) else "Delivered · mastery to earn" if status.get("delivered",false) else "Mastery to earn"
		cards[slot].add_theme_stylebox_override("normal",style(slot==1))
		cards[slot].add_theme_stylebox_override("hover",style(true))
	var selected: Dictionary = Catalog.JOBS[selected_index]
	objective_detail.text = "OPTIONAL · "+String(selected.objective_text)+"\n"+String(selected.character)
	buy.text = "Cargo liner installed · 25% protection" if job.session.liner_owned else "Cargo liner · %d Credits · C" % Catalog.LINER_PRICE
	buy.disabled = job.session.liner_owned or job.session.balance<Catalog.LINER_PRICE
	_refresh_reward(job)
	notice.text = "Any legal route pays delivery. Master an optional challenge once to earn its seal. Session resets on exit."
	if not String(job.board_notice).is_empty() and not String(job.board_notice).begins_with("Wall contact") and not String(job.board_notice).begins_with("Five repeatable"):
		notice.text = String(job.board_notice)+" Session resets on exit."

func _refresh_reward(job: Node) -> void:
	reward.visible = mastery_state!=null and mastery_state.has_method("reward_unlocked")
	if not reward.visible:return
	if not mastery_state.reward_unlocked():
		reward.text = "Lantern amber trail · earn one line seal (Depot / Relay) + one service seal (Works / Clinic / Quarry)"
		reward.disabled = true
	elif not mastery_state.reward_owned:
		reward.text = "Unlocked · Lantern amber trail · 200 Credits · T"
		reward.disabled = job.session.balance<200
	else:
		reward.text = "Trail · Lantern amber equipped · T: switch to Standard" if mastery_state.trail_style=="lantern_amber" else "Trail · Standard equipped · T: switch to Lantern amber"
		reward.disabled = false

func _refresh_results(r: Dictionary) -> void:
	title.text = "Delivered · "+String(r.place) if r.delivered else "Parcel returned"
	var status := _status(String(r.job_id))
	mastery_result.text = "NEW MASTERY SEAL · "+String(r.job_name) if mastery_receipt.get("first_mastery",false) else "Mastery already earned · repeat reward paid" if r.delivered and r.objective_met and status.get("mastered",false) else "Optional challenge missed · delivery still counts" if r.delivered else "No delivery or mastery recorded"
	var unlocked: Array = mastery_receipt.get("unlocks",[])
	if not unlocked.is_empty():mastery_result.text += "\nUnlocked · "+", ".join(unlocked)
	var outcome: String="Achieved" if r.objective_met else "Not achieved"
	if r.objective=="SWEEP":
		outcome += " · section %.2f / %.1f s" % [r.best_sweep_s,r.get("objective_target",10.0)] if float(r.get("best_sweep_s",-1.0))>=0 else " · section not recorded"
	elif r.objective=="HAUL" and not r.objective_met:
		outcome += " · clean Shelf pending" if int(r.get("route_phase",0))>=1 else " · East Sweep pending"
	body.text = "%s\nCargo %.1f%% · Active time %s\n%s · %s\n\nDELIVERY +%d   /   OPTIONAL +%d\nTOTAL +%d   /   SESSION %d Credits\n\nBRRR %.0f · Longest BRRR streak %.1f s\nDrift chain %.2f s · Peak %.1f m/s\nImpact episodes %d%s\n\n%s" % [r.job_name,r.condition_units/10.0,OldHud.time_text(r.elapsed),r.objective,outcome,r.base_credits,r.bonus_credits,r.total_credits,r.session_balance,r.brrr,r.longest_streak,r.get("best_drift_s",0),r.peak_speed,r.episodes," · Liner saved %.1f points" % (r.protection_saved_units/10.0) if r.liner_owned else "",String(r.get("reaction",""))+" Drive home when ready." if r.delivered else "Collect again at Market. No Credits charged or awarded."]
	action.text = "Continue here · Enter / B"

func objective_progress(job: Node) -> String:
	var c: Dictionary = job.contract
	if c.objective not in ["SWEEP","HAUL"]:return super.objective_progress(job)
	var evidence: Dictionary = job.execution.snapshot
	var complete: bool = evidence.get("route_complete",false)
	var active: bool = evidence.get("route_active",false)
	var reason: String = evidence.get("route_reason","ready")
	if c.objective=="SWEEP":
		var target: float = c.target
		var best: float = evidence.get("best_sweep_s",-1.0)
		if complete:return "SWEEP +%d · section %.2f / %.1f s · earned" % [c.bonus,best,target]
		if active:return "SWEEP +%d · section %.1f / %.1f s" % [c.bonus,evidence.get("route_elapsed_s",0.0),target]
		if reason=="over reference":return "SWEEP +%d · section %.2f / %.1f s · delivery still pays" % [c.bonus,best,target]
		if reason=="left road":return "SWEEP +%d · left section · retry from West Gate" % c.bonus
		return "SWEEP +%d · %.1f s section · starts after West Gate" % [c.bonus,target]
	var phase: int = evidence.get("route_phase",0)
	if complete:return "HAUL +%d · East Sweep + clean Shelf earned" % c.bonus
	if phase==0:return "HAUL +%d · East Sweep in progress" % c.bonus if active else "HAUL +%d · East Sweep, then clean Quarry Shelf" % c.bonus
	if active:return "HAUL +%d · Quarry Shelf · keep crossing clean" % c.bonus
	if reason=="Shelf contact":return "HAUL +%d · Shelf contact · retry from Relay end" % c.bonus
	if reason=="left road":return "HAUL +%d · left Shelf · retry from Relay end" % c.bonus
	return "HAUL +%d · East Sweep met · enter Shelf from Relay" % c.bonus

func _mastery_count() -> int:
	return int(mastery_state.mastery_count()) if mastery_state!=null else 0

func _status(job_id: String) -> Dictionary:
	return mastery_state.status(job_id) if mastery_state!=null else {}

func _archetype(c: Dictionary) -> String:
	return "DRIFT CHAIN" if c.objective=="STYLE" else String(c.objective)

func _route_character(c: Dictionary) -> String:
	match c.id:
		"freight_seals":return "yard / short"
		"relay_window":return "outer sweep"
		"works_instruments":return "service crossing"
		"clinic_thread":return "south / technical"
		"quarry_haul":return "shelf / long"
	return "open route"
