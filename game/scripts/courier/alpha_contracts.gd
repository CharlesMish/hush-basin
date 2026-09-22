extends RefCounted
## Provisional alpha catalog. Routes are advisory; THREAD asks for one optional
## feature crossing. Endpoint delivery always remains open-route.
const VERSION := "mastery-alpha-v1"
const LINER_PRICE := 400
const LINER_PERCENT := 25
const JOBS := [
 {"id":"freight_seals","destination":"DEP","place":"Depot","name":"Freight seals","character":"Open yard · drift, then settle","base":80,"bonus":60,"objective":"STYLE","target":3.5,"objective_text":"3.5 s drift combo: Drive, 22+ m/s, 15-75 deg slip","routes":["L1"],"dispatch":"Fresh seals for the freight office.","reaction":"Seals counted. The next load can leave."},
 {"id":"relay_window","destination":"RLY","place":"Relay","name":"Longline coil","character":"West Sweep · shape a fast bend","base":100,"bonus":200,"objective":"SWEEP","target":10.0,"objective_text":"West Sweep Express: GW-to-Relay road section in 10 s","routes":["L1","L0","A1"],"dispatch":"One matched coil. West Sweep is the optional express line.","reaction":"The mast crew has what it needs."},
 {"id":"works_instruments","destination":"WRK","place":"Works","name":"Bench instruments","character":"Service crossing · Spread/Hop or bypass","base":120,"bonus":35,"objective":"CARE","target":850,"objective_text":"Deliver with at least 85% condition","routes":["L6"],"dispatch":"Keep the Works gauge needles steady.","reaction":"Bench instruments received."},
 {"id":"clinic_thread","destination":"CLN","place":"Clinic","name":"South desk kit","character":"THREAD · South Cut · technical / longer","base":100,"bonus":300,"objective":"THREAD","target":1,"objective_text":"Clean South Cut crossing in Spread (Hop or dogleg)","routes":["L1","S0","DOG","HOP","S1"],"dispatch":"The south desk needs its replacement kit.","reaction":"Kit received. The south desk stays open."},
 {"id":"quarry_haul","destination":"QRY","place":"Quarry","name":"Shelf survey pack","character":"East Sweep then Quarry Shelf · long / technical","base":140,"bonus":420,"objective":"HAUL","target":2,"objective_text":"East Sweep northbound, then Quarry Shelf without wall contact","routes":["L2","L3","A2","X0"],"dispatch":"Survey pack. The optional long round ends on Quarry Shelf.","reaction":"The shelf crew can start its round."}
]

static func objective_met(contract: Dictionary, evidence: Dictionary) -> bool:
	match contract.objective:
		"STYLE": return float(evidence.get("best_drift_s",0.0))+0.000000001>=float(contract.target)
		"SWEEP": return bool(evidence.get("route_complete",false)) and float(evidence.get("best_sweep_s",-1.0))>=0 and float(evidence.get("best_sweep_s",-1.0))<=float(contract.target)+0.000000001
		"CARE": return int(evidence.condition_units)>=int(contract.target)
		"THREAD": return bool(evidence.get("thread_complete",false))
		"HAUL": return bool(evidence.get("route_complete",false)) and int(evidence.get("route_phase",0))>=2
	return false

static func job(index: int) -> Dictionary:
	var result: Dictionary=JOBS[clampi(index,0,JOBS.size()-1)].duplicate(true)
	result.routes.make_read_only()
	result.make_read_only()
	return result
