extends RefCounted
## Session-only observation of settled receipts. Never samples or controls craft.
## Five ordinary contracts stay open; only the optional appearance is gated.
const REWARD_NAME := "Lantern amber trail"
const REWARD_PRICE := 200
const STANDARD := "standard"
const LANTERN_AMBER := "lantern_amber"
const JOB_FAMILIES := {
	"freight_seals": "line",
	"relay_window": "line",
	"works_instruments": "route_care",
	"clinic_thread": "route_care",
	"quarry_haul": "route_care",
}
var reward_owned := false
var trail_style := STANDARD
var _seen: Dictionary = {}
var _delivered: Dictionary = {}
var _stamps: Dictionary = {}

func status(job_id: String) -> Dictionary:
	return {"available": JOB_FAMILIES.has(job_id), "lock_reason": "",
		"delivered": int(_delivered.get(job_id, 0)) > 0,
		"mastered": _stamps.has(job_id), "deliveries": int(_delivered.get(job_id, 0))}

func mastery_count() -> int:
	return _stamps.size()

func reward_unlocked() -> bool:
	var line := false
	var route_care := false
	for job_id in _stamps:
		line = line or JOB_FAMILIES[job_id] == "line"
		route_care = route_care or JOB_FAMILIES[job_id] == "route_care"
	return line and route_care

func reward_progress() -> String:
	if reward_owned: return "Lantern amber owned · appearance only"
	if reward_unlocked(): return "Lantern amber available · %d Credits" % REWARD_PRICE
	return "Unlock amber: master Depot or Relay, and Works, Thread or Haul"

func observe_receipt(receipt: Dictionary) -> Dictionary:
	var event := {"accepted": false, "first_mastery": false,
		"mastery_count": mastery_count(), "unlocks": []}
	if not _valid_receipt(receipt): return event
	var id: int = receipt.attempt_id
	if _seen.has(id): return event
	_seen[id] = true
	event.accepted = true
	var was_unlocked := reward_unlocked()
	var job_id: String = receipt.job_id
	if receipt.delivered:
		_delivered[job_id] = int(_delivered.get(job_id, 0)) + 1
		if receipt.objective_met and not _stamps.has(job_id):
			_stamps[job_id] = {"attempt_id": id}
			event.first_mastery = true
	event.mastery_count = mastery_count()
	if not was_unlocked and reward_unlocked(): event.unlocks.append(REWARD_NAME)
	return event

func snapshot() -> Dictionary:
	return {"mastered_jobs": _stamps.keys(), "deliveries": _delivered.duplicate(),
		"mastery_count": mastery_count(), "reward_unlocked": reward_unlocked(),
		"reward_owned": reward_owned, "trail_style": trail_style}

func _valid_receipt(receipt: Dictionary) -> bool:
	return typeof(receipt.get("attempt_id")) == TYPE_INT and int(receipt.attempt_id) > 0 \
		and JOB_FAMILIES.has(receipt.get("job_id", "")) \
		and typeof(receipt.get("delivered")) == TYPE_BOOL \
		and typeof(receipt.get("objective_met")) == TYPE_BOOL
