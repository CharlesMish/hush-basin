extends "res://review/cargo_v1_1/cargo_review.gd"
## Retained F2/F3 v1.1 evidence, plus explicit cargo-protection receipts.
var _shown_loss_frame := -1
var _last_line_transition := -1.0
func _init() -> void:
	game_scene_path="res://scenes/district_zero_alpha.tscn"
func _ready() -> void:
	await super._ready()
	panel.hide()
func _physics_process(delta: float) -> void:
	super._physics_process(delta)
	if is_instance_valid(job) and not job.lines.transitions.is_empty():
		var newest: Dictionary=job.lines.transitions[-1]
		if float(newest.time)!=_last_line_transition:
			_last_line_transition=float(newest.time)
			write({"event":"line_transition","attempt_id":job.attempt_id,"job_id":job.contract.id,"transition":newest.duplicate(true)})
	if last_loss.is_empty() or int(last_loss.physics_frame)==_shown_loss_frame:return
	_shown_loss_frame=last_loss.physics_frame
	if last_loss.has("protection_receipt"):
		var r: Dictionary=last_loss.protection_receipt
		label.text+="\nRaw %.1f%% - liner %.1f%% = charged %.1f%%" % [r.raw_capped_loss_units/10.0,r.protection_actual_reduction_units/10.0,r.committed_loss_units/10.0]
func write(row: Dictionary) -> void:
	row["build"]="mastery-alpha-v1"
	if row.get("event","")=="impact" and is_instance_valid(job):
		row["protection_receipt"]=job.cargo.loss_receipt.duplicate(true)
		row["protection_receipt_is_this_impact"]=row.incremental_loss_units>0
		row["liner_owned"]=job.session.liner_owned
		row["job_id"]=job.contract.id
		row["attempt_id"]=job.attempt_id
	if row.get("event","") in ["owner_bookmark","impact"] and is_instance_valid(job):
		row["line_evidence"]=job.lines.snapshot.duplicate(true)
		row["route_execution"]=job.execution.snapshot.duplicate(true)
	if row.get("event","")=="owner_bookmark" and is_instance_valid(job):
		row["line_transitions"]=job.lines.transitions.duplicate(true)
		row["mastery"]=job.session.mastery.snapshot()
	if row.get("event","")=="owner_bookmark":
		print("CARGO_BOOKMARK "+JSON.stringify(row))
	super.write(row)
