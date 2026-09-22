extends "res://scripts/courier/alpha_hud.gd"
## Presentation adapter: three visible neighbors, with the selection in the middle.
## All ordinary contracts remain accessible. This node never settles a receipt.
signal reset_experiment
const Precision=preload("res://scripts/courier/challenge_display.gd")
var pool_size:=1
var reset_dialog: ConfirmationDialog
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
var purpose_panel: PanelContainer
var purpose_text: Label
var handoff_visual: Control
var accept_button: Button

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
	purpose_panel=PanelContainer.new()
	purpose_panel.position=Vector2(18,150)
	purpose_panel.custom_minimum_size=Vector2(380,62)
	purpose_panel.mouse_filter=Control.MOUSE_FILTER_IGNORE
	purpose_panel.add_theme_stylebox_override("panel",style())
	purpose_text=label(16)
	purpose_text.add_theme_color_override("font_color",Color("b1cbc5"))
	purpose_panel.add_child(purpose_text);add_child(purpose_panel)
	purpose_panel.hide()
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
	var previous := button("<",func():select_job.emit(posmod(selected_index-1,pool_size)))
	previous.custom_minimum_size.x = 44
	previous.custom_minimum_size.y = 28
	browse.add_child(previous)
	browse_position = label(14)
	browse_position.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	browse_position.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	browse.add_child(browse_position)
	var next := button(">",func():select_job.emit(posmod(selected_index+1,pool_size)))
	next.custom_minimum_size.x = 44
	next.custom_minimum_size.y = 28
	browse.add_child(next)
	var row := HBoxContainer.new()
	row.alignment=BoxContainer.ALIGNMENT_CENTER
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
	accept_button=accept
	accept.custom_minimum_size.x = 308
	actions.add_child(accept)
	buy = button("",func():purchase.emit())
	buy.custom_minimum_size.x = 432
	actions.add_child(buy)
	actions.add_child(button("Back · Esc",func():secondary.emit()))
	reward = button("Reset Project Experiment…",func():reset_dialog.popup_centered())
	reward.custom_minimum_size.y = 30
	reward.add_theme_font_size_override("font_size",14)
	content.add_child(reward)
	reset_dialog=ConfirmationDialog.new()
	reset_dialog.title="Reset Project Experiment"
	reset_dialog.dialog_text="Forget both Relay needs and deactivate the annex?\nCredits, cargo liner and session mastery are unchanged."
	reset_dialog.confirmed.connect(func():reset_experiment.emit())
	add_child(reset_dialog)
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
	handoff_visual=preload("res://scripts/courier/receiver_handoff_visual.gd").new()
	result_stack.add_child(handoff_visual)
	handoff_visual.hide()
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
	handoff_visual.hide()
	card.offset_top=-246;card.offset_bottom=246
	purpose_panel.visible=not job.neutral_control and job.state=="ACTIVE" and job.contract.id in ["relay_stock","relay_receiver"]
	if purpose_panel.visible:
		purpose_text.text="Finished receiver → Ren, Relay\nOpens local dispatch" if job.contract.id=="relay_receiver" else "Receiver kit → Ivo, Works\nIvo builds Ren's receiver"
	board.visible = job.state=="DISPATCH"
	card.visible = job.state in ["RESULTS","PAUSED","WAIT_NEUTRAL"]
	readout.get_parent().visible = not board.visible and not card.visible
	action.visible = job.state!="WAIT_NEUTRAL"
	mastery_result.visible = job.state=="RESULTS"
	hint.text = "W/S thrust/brake · A/D steer · Shift form · Space Hop · R reset · Esc pause\nRELAY EXPERIMENT · F2 cargo receipts · F3 bookmark · project saved locally"
	hint.visible = not board.visible
	if board.visible:_refresh_board(job)
	match job.state:
		"FREE_ROAM":
			var id: String=job.guidance_id()
			var place: String={"MRK":"Market", "WRK":"Works pickup", "RLY":"Relay Dispatch"}[id]
			var distance: float=job._xz().distance_to(job.hub_position(id))
			readout.text="%s · %d Credits%s\n%s" % [place.to_upper(),job.session.balance," · Liner" if job.session.liner_owned else "","E / Enter / B · Open Dispatch" if job.can_dispatch() else "%s %.0f m" % [place,distance]]
			if job.project.stage()==1:readout.text+="\n"+("Relay shipment ready at Works" if job.neutral_control else "Ivo has the finished receiver · pickup at Works")
			elif job.project.stage()==2 and job.nearby_hub()=="RLY" and not job.neutral_control:readout.text+="\nRen offers a Market return pouch · accept when ready"
			if not job.project_error.is_empty():readout.text+="\nPROJECT NOT SAVED · open Dispatch for details"
		"ACTIVE":
			var c: Dictionary = job.contract
			var distance: float = job._xz().distance_to(job.destination)
			readout.text = "%s > %s · %.0f m\nCargo %.1f%% · %s · %d Credits%s\n%s" % [c.name.to_upper(),String(c.place).to_upper(),distance,job.cargo.condition_units/10.0,OldHud.time_text(job.elapsed),job.session.balance," · Liner" if job.cargo.protected else "",objective_progress(job)]
			if job.elapsed<4:readout.text += "\n"+String(c.dispatch)
			if distance<=job.destination_radius:readout.text += "\n"+("Receiving…" if job.settle>0 else "Settle below 6 m/s to deliver.")
			if purpose_panel.visible:
				readout.text="DELIVERY · %.0f m\nCargo %.1f%% · %s · %d Credits" % [distance,job.cargo.condition_units/10.0,OldHud.time_text(job.elapsed),job.session.balance]
				if distance<=job.destination_radius:readout.text+="\n"+("Receiving…" if job.settle>0 else "Settle below 6 m/s to deliver.")
		"RESULTS":
			if not _refresh_handoff(job):
				_refresh_results(job.last_result)
				_refresh_contribution(job)
		"PAUSED":
			title.text = "Paused"
			body.text = "Parcel and clock wait with you.\nSession balance: %d Credits.\n\nR resets the craft and returns any active parcel.\nIt cannot award a delivery." % job.session.balance
			action.text = "Resume · Esc / Enter / B"
		"WAIT_NEUTRAL":
			title.text = "Ready when you are"
			body.text = "Release the controls to return to the street."

func _refresh_board(job: Node) -> void:
	reset_dialog.dialog_text="Forget both shipment completions and close Relay outbound Dispatch?\nSession rewards are unchanged." if job.neutral_control else "Forget both Relay needs and deactivate the annex?\nCredits, cargo liner and session mastery are unchanged."
	selected_index=job.selected;pool_size=job.board_jobs.size()
	board_heading.text={"MRK":"MARKET DISPATCH", "WRK":"WORKS PICKUP", "RLY":"RELAY DISPATCH"}[job.board_hub]
	if not job.neutral_control:
		if job.board_hub=="WRK":board_heading.text="IVO · WORKS PICKUP"
		if job.board_hub=="RLY":board_heading.text="REN · RELAY DISPATCH"
	accept_button.text="Accept selected · Enter / B"
	if not job.neutral_control and job.board_hub=="WRK":accept_button.text="Collect finished receiver · Enter / B"
	if not job.neutral_control and job.board_hub=="RLY":accept_button.text="Accept return pouch · Enter / B"
	collection.text="%d Credits · %d / 4 mastered" % [job.session.balance,_mastery_count()]
	browse_position.text="< LEFT / RIGHT >   %d / %d selected · All listed work replayable" % [selected_index+1,pool_size]
	visible_indices.clear()
	for slot in 3:
		var index: int=posmod(selected_index+slot-1,pool_size)
		visible_indices.append(index)
		cards[slot].visible=pool_size>=3 or slot==1
		var c: Dictionary=job.board_jobs[index]
		var fields: Dictionary=card_labels[slot]
		fields.place.text=String(c.place).to_upper();fields.name.text=c.name
		fields.kind.text=("SHIPMENT" if job.neutral_control else "RELAY ANNEX") if String(c.id).begins_with("relay_") and c.id!="relay_return" else "BASIC" if c.objective=="NONE" else _archetype(c)
		fields.reward.text="Delivery +%d" % c.base if c.objective=="NONE" else "Delivery +%d / optional +%d" % [c.base,c.bonus]
		var status:=_status(String(c.id))
		fields.stamp.text="No mastery slot" if c.objective=="NONE" else "[SEAL] Mastered · replay welcome" if status.get("mastered",false) else "Mastery to earn"
		if c.id=="relay_stock":fields.stamp.text="Completed · ordinary paid replay" if job.project.stage()>=1 else "First shipment" if job.neutral_control else "Ivo fabricates Ren's receiver"
		if c.id=="relay_receiver":fields.stamp.text="Completed · ordinary paid replay" if job.project.stage()>=2 else "Next shipment" if job.neutral_control else "Ren installs it · opens dispatch"
		cards[slot].add_theme_stylebox_override("normal",style(slot==1));cards[slot].add_theme_stylebox_override("hover",style(true))
	var c: Dictionary=job.board_jobs[selected_index]
	objective_detail.text=String(c.get("purpose",c.objective_text))+"\n"+String(c.character)
	if (c.id=="relay_stock" and job.project.stage()>=1) or (c.id=="relay_receiver" and job.project.stage()>=2):objective_detail.text="Already received. Replay pays ordinary Credits; availability remains unchanged.\n"+String(c.character)
	buy.text="Cargo liner fitted · 25% protection" if job.session.liner_owned else "Cargo liner · 400 Credits · C"
	buy.disabled=job.session.liner_owned or job.session.balance<400
	reward.disabled=false
	notice.text="Project is saved locally. Credits, liner and four challenge seals reset on exit. Default trail is always available."
	if job.neutral_control:notice.text="Review control · delivery availability saved locally; session rewards reset on exit."
	if not job.board_notice.is_empty():notice.text=job.board_notice
	if not job.project_error.is_empty():notice.text="PROJECT NOT SAVED: "+job.project_error+". Fix storage or Reset Project Experiment; delivery Credits still paid."

func _refresh_contribution(job: Node) -> void:
	var r: Dictionary=job.last_result
	if r.objective=="NONE":
		mastery_result.text="Ordinary delivery · no mastery slot" if r.delivered else "No delivery recorded"
		if r.delivered and r.job_id in ["relay_stock","relay_receiver"]:
			if not job.project_receipt.get("ok",false):
				mastery_result.text="Delivery paid · project NOT SAVED"
				body.text=body.text.replace(String(r.reaction),"Project state could not be recorded. No installation or new pickup has been committed.")+"\n"+String(job.project_error)
			elif job.project_receipt.get("changed",false):
				mastery_result.text=("Shipment received · next pickup at Works" if r.job_id=="relay_stock" else "Shipment received · Relay Dispatch available") if job.neutral_control else ("CONTRIBUTED · Receiver mounting stock" if r.job_id=="relay_stock" else "INSTALLED · Assembled receiver · Relay annex operational")
			else:
				mastery_result.text="Already received · ordinary replay paid"
				body.text=body.text.replace(String(r.reaction),"Repeat shipment received. The completed need remains unchanged.")
		if r.delivered and r.job_id=="relay_stock" and job.project.stage()==1:action.text="Continue here · collect at Works · Enter / B"
		if r.delivered and r.job_id=="relay_receiver" and job.project.stage()==2:action.text="Continue here · Relay Dispatch · Enter / B"

func _refresh_results(r: Dictionary) -> void:
	title.text = "Delivered · "+String(r.place) if r.delivered else "Parcel returned"
	var status := _status(String(r.job_id))
	mastery_result.text = "NEW MASTERY SEAL · "+String(r.job_name) if mastery_receipt.get("first_mastery",false) else "Mastery already earned · repeat reward paid" if r.delivered and r.objective_met and status.get("mastered",false) else "Optional challenge missed · delivery still counts" if r.delivered else "No delivery or mastery recorded"
	var unlocked: Array = mastery_receipt.get("unlocks",[])
	if not unlocked.is_empty():mastery_result.text += "\nUnlocked · "+", ".join(unlocked)
	var outcome: String="No optional objective" if r.objective=="NONE" else "Achieved" if r.objective_met else "Not achieved"
	if r.objective=="SWEEP":
		outcome += " · section %s / %.2f s" % [Precision.maximum_time(r.best_sweep_s),r.get("objective_target",10.0)] if float(r.get("best_sweep_s",-1.0))>=0 else " · section not recorded"
	elif r.objective=="HAUL" and not r.objective_met:
		outcome += " · clean Shelf pending" if int(r.get("route_phase",0))>=1 else " · East Sweep pending"
	body.text = "%s\nCargo %.1f%% · Active time %s\n%s · %s\n\nDELIVERY +%d   /   OPTIONAL +%d\nTOTAL +%d   /   SESSION %d Credits\n\nBRRR %.0f · Longest BRRR streak %.1f s\nDrift chain %.2f s · Peak %.1f m/s\nImpact episodes %d%s\n\n%s" % [r.job_name,r.condition_units/10.0,OldHud.time_text(r.elapsed),r.objective,outcome,r.base_credits,r.bonus_credits,r.total_credits,r.session_balance,r.brrr,r.longest_streak,r.get("best_drift_s",0),r.peak_speed,r.episodes," · Liner saved %.1f points" % (r.protection_saved_units/10.0) if r.liner_owned else "",String(r.get("reaction","")) if r.delivered else "No Credits charged or awarded. Recollect at the pickup."]
	action.text = "Continue here · Enter / B"

func _refresh_handoff(job: Node) -> bool:
	var r: Dictionary=job.last_result
	if job.neutral_control or not r.delivered or not r.job_id in ["relay_stock","relay_receiver"] or not job.project_receipt.get("ok",false):return false
	var works: bool=r.job_id=="relay_stock"
	title.text="Ivo · Works" if works else "Ren · Relay"
	card.offset_top=-192;card.offset_bottom=192
	var changed: bool=job.project_receipt.get("changed",false)
	if changed:
		mastery_result.text="Receiver kit → Finished receiver" if works else "Finished receiver → Installed at Relay"
		handoff_visual.show_installation(not works);handoff_visual.show()
		body.text="I assembled your kit into Ren's finished receiver.\nTake it to Ren at Relay; they'll install it to open local dispatch." if works else "Your receiver is installed. We can dispatch from Relay now.\nI have a Market return pouch if you'd like the next delivery."
	else:
		mastery_result.text="Repeat kit received" if works else "Spare receiver received"
		body.text="Ren's finished receiver is already ready for pickup here." if works and job.project.stage()==1 else "Relay's receiver is already installed; local dispatch stays open."
	body.text+="\n\nDelivery +%d · Session %d Credits\nCargo %.1f%% · %s" % [r.base_credits,r.session_balance,r.condition_units/10.0,OldHud.time_text(r.elapsed)]
	action.text="Continue here · Enter / B"
	return true

func objective_progress(job: Node) -> String:
	var c: Dictionary = job.contract
	if c.objective=="NONE":return "Delivery +%d · any legal route · condition never prevents delivery" % c.base
	if c.objective not in ["SWEEP","HAUL"]:return super.objective_progress(job)
	var evidence: Dictionary = job.execution.snapshot
	var complete: bool = evidence.get("route_complete",false)
	var active: bool = evidence.get("route_active",false)
	var reason: String = evidence.get("route_reason","ready")
	if c.objective=="SWEEP":
		var target: float = c.target
		var best: float = evidence.get("best_sweep_s",-1.0)
		if complete:return "SWEEP +%d · section %s / %.2f s · earned" % [c.bonus,Precision.maximum_time(best),target]
		if active:return "SWEEP +%d · section %s / %.2f s" % [c.bonus,Precision.maximum_time(evidence.get("route_elapsed_s",0.0)),target]
		if reason=="over reference":return "SWEEP +%d · section %s / %.2f s · delivery still pays" % [c.bonus,Precision.maximum_time(best),target]
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
