extends "res://scripts/courier/alpha_session.gd"
## Existing exactly-once Credit ledger; four authored session mastery slots.
var mastery=preload("res://scripts/courier/relay_mastery.gd").new()
var events: Dictionary={}
func settle(id: int, evidence: Dictionary) -> Dictionary:
	var receipt: Dictionary=super.settle(id,evidence)
	if not receipt.is_empty() and not events.has(id):events[id]=mastery.observe_receipt(receipt)
	return receipt
func mastery_receipt(id: int) -> Dictionary:
	return events.get(id,{}).duplicate(true)
