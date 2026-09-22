extends SceneTree
const Catalog = preload("res://scripts/courier/relay_contracts.gd")
const Previous = preload("res://scripts/courier/alpha_contracts.gd")
const Session = preload("res://scripts/courier/relay_session.gd")
const Precision = preload("res://scripts/courier/challenge_display.gd")
var checks: Dictionary = {}

func _initialize() -> void:
	call_deferred("run")

func evidence(condition: int = 1000) -> Dictionary:
	return {"delivered": true, "condition_units": condition, "best_drift_s": 20.0,
		"route_complete": true, "best_sweep_s": 9.0, "thread_complete": true, "route_phase": 2}

func run() -> void:
	var basic := Catalog.ordinary(0)
	checks["Depot_basic_has_no_optional_mastery_slot"] = basic.id == "freight_seals" and basic.objective == "NONE" and basic.bonus == 0 and basic.base == 80
	for index in range(1, 5):
		checks["ordinary_challenge_%d_exact_definition_preserved" % index] = Catalog.ordinary(index) == Previous.job(index)
	var ordinary_copy := Catalog.ordinary(1)
	ordinary_copy.base = 99999
	checks["catalog_returns_detached_ordinary_data"] = Catalog.ordinary(1).base == 100
	var fields := ["id", "destination", "base", "bonus", "objective", "target", "routes"]
	for index in 2:
		var named := Catalog.project_job(index, false)
		var control := Catalog.project_job(index, true)
		for field in fields:
			checks["neutral_leg_%d_%s_exact_parity" % [index, field]] = named[field] == control[field]
		checks["neutral_leg_%d_has_distinct_context_only" % index] = named.dispatch != control.dispatch and named.reaction != control.reaction
	var outbound := Catalog.outbound()
	for field in fields:
		checks["neutral_outbound_%s_exact_parity" % field] = outbound[field] == Catalog.outbound(true)[field]
	checks["outbound_is_repeatable_basic_Market_endpoint"] = outbound.destination == "MRK" and outbound.objective == "NONE" and outbound.base == 100 and outbound.bonus == 0
	var session := Session.new()
	var basic_id: int = session.accept(basic)
	var basic_receipt: Dictionary = session.settle(basic_id, evidence())
	checks["basic_pays_base_even_with_high_style_evidence"] = basic_receipt.total_credits == 80 and not basic_receipt.objective_met
	checks["basic_never_stamps"] = session.mastery.mastery_count() == 0 and not session.mastery.status(basic.id).mastered and not session.mastery_receipt(basic_id).first_mastery
	for condition in [0, 100, 1000]:
		for index in 2:
			var job := Catalog.project_job(index)
			var id: int = session.accept(job)
			var receipt: Dictionary = session.settle(id, evidence(condition))
			checks["project_leg_%d_condition_%d_pays_fixed_base" % [index, condition]] = receipt.delivered and receipt.base_credits == job.base and receipt.bonus_credits == 0 and receipt.total_credits == job.base and not receipt.objective_met
			var balance: int = session.balance
			var changed_evidence := evidence(1000)
			changed_evidence.delivered = false
			checks["project_leg_%d_condition_%d_cannot_double_settle" % [index, condition]] = session.settle(id, changed_evidence) == receipt and session.balance == balance
	checks["project_receipts_do_not_stamp"] = session.mastery.mastery_count() == 0
	for index in range(1, 5):
		var id: int = session.accept(Catalog.ordinary(index))
		var receipt: Dictionary = session.settle(id, evidence())
		checks["authored_challenge_%d_still_stamps" % index] = receipt.objective_met and session.mastery_receipt(id).first_mastery
	checks["exactly_four_mastery_slots"] = session.mastery.mastery_count() == 4
	checks["mastery_does_not_withhold_default_trail"] = not session.mastery.reward_unlocked() and not session.mastery.reward_owned and session.mastery.trail_style == "standard"
	var all_time_display_consistent := true
	var all_duration_display_consistent := true
	for offset in range(-1000, 1001):
		var seconds: float = 10.0 + offset * 0.00001
		var met := Previous.objective_met(Catalog.ordinary(1), {"route_complete": true, "best_sweep_s": seconds})
		all_time_display_consistent = all_time_display_consistent and ((float(Precision.maximum_time(seconds)) <= 10.0) == met)
		var duration: float = 3.5 + offset * 0.00001
		var drift_met := Previous.objective_met(Previous.job(0), {"best_drift_s": duration})
		all_duration_display_consistent = all_duration_display_consistent and ((float(Precision.minimum_duration(duration)) >= 3.5) == drift_met)
	checks["2001_Sweep_boundary_displays_match_award_precision"] = all_time_display_consistent
	checks["2001_drift_boundary_displays_match_award_precision"] = all_duration_display_consistent
	for offset in [-0.000000002, -0.0000000005, 0.0, 0.0000000005, 0.000000002]:
		var seconds: float = 10.0 + offset
		checks["Sweep_epsilon_boundary_%s" % str(offset)] = ((float(Precision.maximum_time(seconds)) <= 10.0) == Previous.objective_met(Catalog.ordinary(1), {"route_complete": true, "best_sweep_s": seconds}))
	var passed := true
	for value in checks.values(): passed = passed and value
	var result := {"status": "PASS" if passed else "FAIL", "checks": checks, "count": checks.size(),
		"scope": "Catalog, ledger, mastery and numerical display predicates; not UI input/world/browser integration"}
	var args := OS.get_cmdline_user_args()
	if args.has("--result"):
		FileAccess.open(args[args.find("--result") + 1], FileAccess.WRITE).store_string(JSON.stringify(result, "  "))
	print("RELAY_CATALOG_RESULT " + JSON.stringify(result))
	quit(0 if passed else 1)
