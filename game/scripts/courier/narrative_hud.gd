extends "res://scripts/courier/relay_hud.gd"
signal review_conversation
var review_button: Button

func _ready() -> void:
	super._ready()
	reward.text="Reset Narrative Experiment…";reset_dialog.title="Reset Narrative Experiment"
	review_button=button("Review conversation",func():review_conversation.emit())
	review_button.custom_minimum_size.y=30;review_button.add_theme_font_size_override("font_size",14)
	board.get_child(0).add_child(review_button)

func refresh(job: Node) -> void:
	if job.state=="NARRATIVE":
		board.hide();card.hide();readout.get_parent().hide();purpose_panel.hide();hint.hide();return
	super.refresh(job)
	if job.story_store==null:return
	hint.text="W/S thrust/brake · A/D steer · Hold Shift Drive · Space Hop · R reset · Esc pause\nE / Enter interact · F2 cargo receipts · F3 bookmark"
	if job.state=="FREE_ROAM":
		# Keep location/interaction feedback; replace the inherited return-pouch hint.
		var rows:=readout.text.split("\n")
		readout.text=rows[0]+"\n"+rows[1]+"\n"+job.resume_sentence()
		if not job.project_error.is_empty():readout.text+="\nNOT SAVED · open Dispatch for details"
	if job.state=="RESULTS" and job.last_result.get("job_id","")=="relay_quarry" and job.last_result.get("delivered",false):
		card.offset_top=-160;card.offset_bottom=160
		title.text="QUARRY STORES";mastery_result.text="Dry socks received · Payment +100 received"
		body.text=preload("res://scripts/courier/narrative_text.gd").RECEIPT+"\n\nCargo %.1f%% · Session %d Credits" % [job.last_result.condition_units/10.0,job.last_result.session_balance]
	if job.state=="ACTIVE" and String(job.contract.id).begins_with("relay_"):
		purpose_panel.show();purpose_text.text=job.contract.purpose
		readout.text="DELIVERY · %.0f m\nCargo %.1f%% · %d Credits" % [job._xz().distance_to(job.destination),job.cargo.condition_units/10.0,job.session.balance]
		if job._xz().distance_to(job.destination)<=job.destination_radius:readout.text+="\n"+("Receiving…" if job.settle>0 else "Settle below 6 m/s to deliver.")
	if board.visible:
		reset_dialog.dialog_text="Reset the Ren/Ivo conversations, receiver project and Quarry request?\nSession rewards stay unchanged. The older Relay experiment save is preserved."
		notice.text=job.resume_sentence() if job.project_error.is_empty() else "NOT SAVED · "+job.project_error
		var id: String={"MRK":"market","WRK":"works","RLY":"relay"}[job.board_hub]
		review_button.disabled=not id in job.story_store.record.seen
		var c: Dictionary=job.board_jobs[job.selected]
		if String(c.id).begins_with("relay_"):accept_button.text="Talk / view offer · Enter / B"
