extends RefCounted
## Session-only receipt book; each accepted parcel can settle exactly once.
const Catalog = preload("res://scripts/courier/alpha_contracts.gd")
var balance := 0
var liner_owned := false
var deliveries := 0
var _next_id := 0
var _open: Dictionary={}
var _receipts: Dictionary={}

func accept(contract: Dictionary) -> int:
	_next_id+=1
	_open[_next_id]=contract
	return _next_id

func settle(id: int, evidence: Dictionary) -> Dictionary:
	if _receipts.has(id): return _receipts[id]
	if not _open.has(id): return {}
	var contract: Dictionary=_open[id]
	var delivered: bool=evidence.delivered
	var objective: bool=delivered and Catalog.objective_met(contract,evidence)
	var base: int=int(contract.base) if delivered else 0
	var bonus: int=int(contract.bonus) if objective else 0
	balance+=base+bonus
	if delivered:deliveries+=1
	var result:=evidence.duplicate(true)
	result.merge({"attempt_id":id,"job_id":contract.id,"job_name":contract.name,"destination_id":contract.destination,"place":contract.place,"objective":contract.objective,"objective_text":contract.objective_text,"objective_met":objective,"base_credits":base,"bonus_credits":bonus,"total_credits":base+bonus,"session_balance":balance,"liner_owned":liner_owned})
	result.make_read_only()
	_receipts[id]=result
	_open.erase(id)
	return result

func buy_liner() -> bool:
	if liner_owned or balance<Catalog.LINER_PRICE:return false
	balance-=Catalog.LINER_PRICE
	liner_owned=true
	return true
