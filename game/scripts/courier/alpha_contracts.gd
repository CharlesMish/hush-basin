extends RefCounted
## Provisional authored alpha catalog. Routes are suggestions, never predicates.
const VERSION := "courier-alpha-loop-v1"
const LINER_PRICE := 400
const LINER_PERCENT := 25
const JOBS := [
	{"id":"freight_seals","destination":"DEP","place":"Depot","name":"Freight seals","character":"Short yard hop · room to play","base":100,"bonus":25,"objective":"STYLE","target":0.4,"objective_text":"Hold one BRRR streak for 0.4 s","routes":["L1"]},
	{"id":"relay_window","destination":"RLY","place":"Relay","name":"Signal spares","character":"Northern run · commit, then settle","base":150,"bonus":40,"objective":"EXPRESS","target":55.0,"objective_text":"Deliver within 0:55 active time","routes":["L5","L4"]},
	{"id":"works_instruments","destination":"WRK","place":"Works","name":"Bench instruments","character":"Industrial approach · choose your braking","base":120,"bonus":35,"objective":"CARE","target":750,"objective_text":"Deliver with at least 75% condition","routes":["L6"]}
]

static func objective_met(contract: Dictionary, evidence: Dictionary) -> bool:
	match contract.objective:
		"STYLE": return float(evidence.longest_streak)+0.000000001>=float(contract.target)
		"EXPRESS": return float(evidence.elapsed)<=float(contract.target)+0.000000001
		"CARE": return int(evidence.condition_units)>=int(contract.target)
	return false

static func job(index: int) -> Dictionary:
	var result: Dictionary=JOBS[clampi(index,0,JOBS.size()-1)].duplicate(true)
	result.routes.make_read_only()
	result.make_read_only()
	return result
