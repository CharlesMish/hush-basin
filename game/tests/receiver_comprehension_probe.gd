extends "res://tests/relay_probe.gd"
## UI assertions sit beside the retained normal-input integration route probe.
## They establish presentation/flow correctness, never human comprehension.
var purpose_checked:=false
var stock_receipt: Dictionary={}
func _physics_process(delta: float) -> void:
	super._physics_process(delta)
	if not neutral and is_instance_valid(job) and job.state=="ACTIVE" and job.contract.id=="relay_receiver" and job.elapsed>5 and not purpose_checked:
		purpose_checked=true
		call_deferred("purpose_check")
func purpose_check() -> void:
	checks["purpose_survives_initial_four_seconds"]=job.hud.purpose_panel.visible and job.hud.purpose_text.text=="Finished receiver → Ren, Relay\nOpens local dispatch"
	await capture("03b_receiver_purpose")
func capture(id: String) -> void:
	await ticks(2)
	if neutral:
		await super.capture(id)
		return
	if id=="02_stock_received":
		stock_receipt=job.last_result
		checks["Works_names_Ivo"]=job.hud.title.text=="Ivo · Works"
		checks["Works_transforms_cargo_identity"]=job.hud.mastery_result.text=="Receiver kit → Finished receiver" and job.hud.body.text.contains("assembled your kit")
		checks["Works_explains_Ren_and_dispatch"]=job.hud.body.text.contains("Ren at Relay") and job.hud.body.text.contains("open local dispatch")
		checks["handoff_only_one_next_action"]=job.hud.action.visible and job.hud.action.text=="Continue here · Enter / B"
		checks["stopped_handoff"]=get_tree().paused and job.state=="RESULTS"
	if id=="03_works_pickup":checks["finished_receiver_pickup_identity"]=job.hud.board_heading.text.begins_with("IVO") and job.board_jobs[0].name=="Finished receiver"
	if id=="04_receiver_installed":
		checks["Relay_names_Ren"]=job.hud.title.text=="Ren · Relay"
		checks["Relay_explains_installation_payoff"]=job.hud.body.text.contains("receiver is installed") and job.hud.body.text.contains("dispatch from Relay now")
		checks["schematic_matches_unchanged_world_definition"]=job.hud.handoff_visual.definition==job.annex.definition and job.hud.handoff_visual.installed
	if id=="05_relay_dispatch":
		var attempt: int=job.attempt_id
		var elapsed: float=job.elapsed
		await ticks(120)
		checks["outbound_offer_not_autoaccepted"]=job.state=="DISPATCH" and job.attempt_id==attempt and job.elapsed==elapsed and job.board_jobs[0].id=="relay_return"
		checks["Ren_offers_outbound"]=job.hud.board_heading.text.begins_with("REN") and job.hud.accept_button.text.begins_with("Accept return pouch")
	await super.capture(id)
func adversarial() -> void:
	await super.adversarial()
	if neutral:return
	# Presentation-only failure fixture: never claim fabrication when storage failed.
	var prior: Dictionary=job.last_result
	job.last_result=stock_receipt
	job.project_receipt={"ok":false,"changed":false}
	job.hud._refresh_results(stock_receipt)
	job.hud._refresh_contribution(job)
	job.hud._refresh_handoff(job)
	checks["save_failure_does_not_claim_fabrication"]=not job.hud.body.text.contains("assembled the kit") and job.hud.mastery_result.text.contains("NOT SAVED")
	job.last_result=prior
