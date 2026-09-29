extends "res://scripts/courier/relay_hud.gd"
const Chapter=preload("res://scripts/courier/chapter_text.gd")
signal review_conversation
signal return_line
var review_button: Button
var return_button: Button
func _ready() -> void:
	super._ready()
	reward.text="Reset Opening Chapter…";reset_dialog.title="Reset Opening Chapter"
	var row:=HBoxContainer.new();board.get_child(0).add_child(row)
	review_button=button("Review local exchange",func():review_conversation.emit());row.add_child(review_button)
	return_button=button("Talk",func():return_line.emit());row.add_child(return_button)
	for b in [review_button,return_button]:b.custom_minimum_size.y=28;b.add_theme_font_size_override("font_size",14)
func _refresh_handoff(_job: Node) -> bool:return false
func _refresh_contribution(_job: Node) -> void:pass
func refresh(job: Node) -> void:
	if job.story_store==null:return
	if job.state=="NARRATIVE":
		board.hide();card.hide();readout.get_parent().hide();purpose_panel.hide();hint.hide();return
	refresh_base(job)
	hint.text="W/S thrust/brake · A/D steer · Hold Shift Drive · Space Hop · R reset · Esc pause\nE / Enter interact · F2 cargo receipts · F3 bookmark"
	if job.state=="FREE_ROAM":
		var rows:=readout.text.split("\n");readout.text=rows[0]+"\n"+rows[1]+"\n"+job.resume_sentence()
	if job.state=="ACTIVE" and job.contract.id in Chapter.ORDER:
		purpose_panel.show();purpose_text.text=Chapter.pickup_label(job.contract)+"\n"+job.contract.purpose
		readout.text="DELIVERY · %.0f m\nCargo %.1f%% · %d Credits" % [job._xz().distance_to(job.destination),job.cargo.condition_units/10.0,job.session.balance]
		if job._xz().distance_to(job.destination)<=job.destination_radius:readout.text+="\n"+("Receiving…" if job.settle>0 else "Settle below 6 m/s to deliver.")
	if job.state=="RESULTS" and job.last_result.get("job_id","") in Chapter.ORDER:
		card.offset_top=-165;card.offset_bottom=165;title.text=String(job.last_result.place).to_upper()
		mastery_result.text="Payment +%d received" % job.last_result.total_credits if job.last_result.delivered else "Parcel returned"
		body.text=String(job.last_result.reaction) if job.last_result.delivered else "Recollect at the pickup. Earlier deliveries remain complete."
		if not job.project_error.is_empty():body.text+="\nNOT SAVED · "+job.project_error
	if board.visible:
		reset_dialog.dialog_text="Reset this entire Opening Chapter, including conversations, parcels and Tess’s patch?\nEarlier lab saves and session rewards are preserved."
		notice.text=job.resume_sentence() if job.project_error.is_empty() else "NOT SAVED · "+job.project_error
		review_button.disabled=job.local_review().is_empty();return_button.visible=not job.return_id().is_empty()
		return_button.text="Talk to "+("Ren" if job.board_hub=="RLY" else "Ivo")
		var c: Dictionary=job.board_jobs[job.selected]
		accept_button.disabled=not job.project_error.is_empty() or c.id=="chapter_closed"
		accept_button.text="Talk / view offer · Enter / B" if c.id in Chapter.ORDER else "View request · Enter / B" if c.id=="chapter_ticket" else "Accept selected · Enter / B"
		browse_position.text="< LEFT / RIGHT >   %d / %d selected" % [job.selected+1,job.board_jobs.size()]
		for slot in 3:
			var entry: Dictionary=job.board_jobs[visible_indices[slot]]
			if entry.id in Chapter.ORDER or String(entry.id).begins_with("chapter_"):
				card_labels[slot].kind.text="DELIVERY" if entry.id in Chapter.ORDER else "NOTICE"
				card_labels[slot].stamp.text="Accept when ready" if entry.id in Chapter.ORDER else "No cargo accepted"
		objective_detail.text=c.get("purpose",c.objective_text)+"\n"+Chapter.pickup_label(c)
		if c.id=="chapter_closed":objective_detail.text=c.purpose

func refresh_base(job: Node) -> void:
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
			var place: String=Chapter.PLACES[id]
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
	board_heading.text=Chapter.PLACES[job.board_hub].to_upper()
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
