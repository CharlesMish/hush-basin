extends "res://scripts/courier/alpha_session.gd"
## Optional adapter: unchanged Credit/cargo ledger plus a first-time stamp book.
const Mastery = preload("res://scripts/courier/mastery_state.gd")
var mastery = Mastery.new()
var _mastery_events: Dictionary = {}

func settle(id: int, evidence: Dictionary) -> Dictionary:
	var receipt: Dictionary = super.settle(id, evidence)
	if not receipt.is_empty() and not _mastery_events.has(id):
		var event: Dictionary = mastery.observe_receipt(receipt)
		event.make_read_only()
		_mastery_events[id] = event
	return receipt

func mastery_receipt(id: int) -> Dictionary:
	return _mastery_events.get(id, {"accepted": false, "first_mastery": false,
		"mastery_count": mastery.mastery_count(), "unlocks": []}).duplicate(true)

func buy_trail() -> bool:
	if mastery.reward_owned or not mastery.reward_unlocked() or balance < Mastery.REWARD_PRICE:
		return false
	balance -= Mastery.REWARD_PRICE
	mastery.reward_owned = true
	mastery.trail_style = Mastery.LANTERN_AMBER
	return true

func set_trail_style(value: String) -> bool:
	if value != Mastery.STANDARD and value != Mastery.LANTERN_AMBER: return false
	if value == Mastery.LANTERN_AMBER and not mastery.reward_owned: return false
	mastery.trail_style = value
	return true
