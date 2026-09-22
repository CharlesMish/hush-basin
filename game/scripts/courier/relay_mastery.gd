extends "res://scripts/courier/mastery_state.gd"
## The basic Depot job has no mastery. The trail is baseline feedback, not a gate.
func _valid_receipt(receipt: Dictionary) -> bool:
	return super._valid_receipt(receipt) and receipt.get("job_id","")!="freight_seals"
func reward_unlocked() -> bool:
	return false
func status(job_id: String) -> Dictionary:
	var s:=super.status(job_id)
	if job_id=="freight_seals":s.available=true;s.mastered=false
	return s
