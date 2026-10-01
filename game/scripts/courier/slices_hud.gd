extends "res://scripts/courier/chapter_hud.gd"
const Slice=preload("res://scripts/courier/slices_text.gd")
func _ready() -> void:
	super._ready();reward.text="Reset Story…";reset_dialog.title="Reset Story"
func refresh(job: Node) -> void:
	super.refresh(job)
	if job.story_store==null or job.state=="NARRATIVE":return
	reset_dialog.dialog_text="Reset all three chapters, conversations, parcels and their physical changes?\nEarlier review saves and session rewards are preserved."
	if job.state=="ACTIVE" and job.contract.id in Slice.JOBS:
		purpose_panel.show();purpose_text.text=Chapter.pickup_label(job.contract)+"\n"+job.contract.purpose
		readout.text="DELIVERY · %.0f m\nCargo %.1f%% · %d Credits" % [job._xz().distance_to(job.destination),job.cargo.condition_units/10.0,job.session.balance]
		if job._xz().distance_to(job.destination)<=job.destination_radius:readout.text+="\n"+("Receiving…" if job.settle>0 else "Settle below 6 m/s to deliver.")
	if job.state=="RESULTS" and (job.last_result.get("job_id","") in Slice.JOBS or not job.appended_receipt.is_empty()):
		card.offset_top=-190;card.offset_bottom=190;title.text=String(job.last_result.place).to_upper()
		mastery_result.text="Payment +%d received" % job.last_result.total_credits if job.last_result.delivered else "Parcel returned"
		body.text=String(job.last_result.reaction) if job.last_result.delivered else "Recollect at the pickup. Earlier deliveries remain complete."
		if job.last_result.delivered and job.contract.get("docket","")!="":body.text+="\n\nCargo docket\n"+job.contract.docket
		if not job.project_error.is_empty():body.text+="\nNOT SAVED · "+job.project_error
	if board.visible:
		var c: Dictionary=job.board_jobs[job.selected]
		if c.id in Slice.JOBS:
			accept_button.text="View ticket / offer · Enter / B"
			objective_detail.text=c.sender+"\n"+c.ticket+"\n"+Chapter.pickup_label(c)
		for slot in 3:
			if job.board_jobs[visible_indices[slot]].id in Slice.JOBS:
				card_labels[slot].kind.text="DELIVERY";card_labels[slot].stamp.text="Accept when ready"
		var id: String=job.return_id()
		if id in Slice.SCENES:return_button.text="Talk to "+Slice.HEADINGS[Slice.SCENES[id].speaker].get_slice(" ·",0).capitalize()
