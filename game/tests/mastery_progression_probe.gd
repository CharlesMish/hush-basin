extends SceneTree
const State = preload("res://scripts/courier/mastery_state.gd")
const Session = preload("res://scripts/courier/mastery_session.gd")
const OldSession = preload("res://scripts/courier/alpha_session.gd")
const Catalog = preload("res://scripts/courier/alpha_contracts.gd")
const Palette = preload("res://scripts/courier/mastery_trail_palette.gd")
var checks: Dictionary = {}

func _initialize() -> void:
	call_deferred("run")

func evidence(delivered: bool = true, objective: bool = true, condition: int = 1000) -> Dictionary:
	return {"delivered": delivered, "condition_units": condition,
		"best_drift_s": 4.0 if objective else 0.0,
		"best_drive_m": 200.0 if objective else 0.0,
		"thread_complete": objective, "haul_phase": 3 if objective else 0,
		"route_complete": objective, "route_phase": 2 if objective else 0,
		"best_sweep_s": 10.0 if objective else 11.0}

func finish(session: RefCounted, index: int, delivered: bool = true, objective: bool = true, condition: int = 1000) -> Dictionary:
	var id: int = session.accept(Catalog.job(index))
	return session.settle(id, evidence(delivered, objective, condition))

func luminance(value: Color) -> float:
	var linear := value.srgb_to_linear()
	return linear.r * .2126 + linear.g * .7152 + linear.b * .0722

func run() -> void:
	var success_fixture := evidence()
	var miss_fixture := evidence(true, false)
	checks["synthetic_success_supports_upcoming_Sweep_10s_boundary"] = success_fixture.route_complete and float(success_fixture.best_sweep_s) == 10.0
	checks["synthetic_miss_supports_upcoming_Sweep_over_reference"] = not miss_fixture.route_complete and float(miss_fixture.best_sweep_s) > 10.0
	checks["synthetic_Haul_fixtures_have_explicit_route_completion"] = success_fixture.route_complete and not miss_fixture.route_complete
	var session := Session.new()
	checks["fresh_no_mastery_credit_or_reward"] = session.balance == 0 and session.mastery.mastery_count() == 0 and not session.mastery.reward_unlocked() and not session.mastery.reward_owned
	for contract in Catalog.JOBS:
		checks["ordinary_" + contract.id + "_always_available"] = session.mastery.status(contract.id).available
	checks["unearned_amber_cannot_equip"] = not session.set_trail_style(State.LANTERN_AMBER)
	checks["unknown_appearance_rejected"] = not session.set_trail_style("handling_upgrade")
	checks["locked_reward_purchase_no_debt"] = not session.buy_trail() and session.balance == 0
	var base := finish(session, 0, true, false, 0)
	checks["base_delivery_is_separate_from_mastery"] = base.total_credits == 80 and session.mastery.status("freight_seals").delivered and not session.mastery.status("freight_seals").mastered
	var canceled := finish(session, 0, false, true)
	checks["cancellation_cannot_stamp"] = not session.mastery_receipt(canceled.attempt_id).first_mastery and session.mastery.mastery_count() == 0 and canceled.total_credits == 0
	var zero_cargo := finish(session, 0, true, true, 0)
	checks["zero_cargo_style_success_stamps"] = zero_cargo.objective_met and session.mastery_receipt(zero_cargo.attempt_id).first_mastery and session.mastery.mastery_count() == 1
	var before: int = session.balance
	var again := session.settle(zero_cargo.attempt_id, evidence(false, false))
	checks["repeat_settlement_keeps_frozen_receipt_and_money"] = again == zero_cargo and session.balance == before
	var replay := finish(session, 0)
	checks["legitimate_repeat_pays_but_never_re_stamps"] = replay.total_credits == 140 and not session.mastery_receipt(replay.attempt_id).first_mastery and session.mastery.mastery_count() == 1
	checks["one_family_never_unlocks_reward"] = not session.mastery.reward_unlocked()
	finish(session, 1)
	checks["two_line_jobs_do_not_replace_variety_requirement"] = session.mastery.mastery_count() == 2 and not session.mastery.reward_unlocked()
	var technical := finish(session, 3)
	checks["contrasting_mastery_unlocks_exactly_one_reward"] = session.mastery.reward_unlocked() and session.mastery_receipt(technical.attempt_id).unlocks == [State.REWARD_NAME]
	var technical_repeat := finish(session, 3)
	checks["replayed_mastery_does_not_repeat_unlock"] = session.mastery_receipt(technical_repeat.attempt_id).unlocks.is_empty()
	var event: Dictionary = session.mastery_receipt(technical.attempt_id)
	event.unlocks.append("forged")
	checks["returned_event_cannot_mutate_ledger"] = session.mastery_receipt(technical.attempt_id).unlocks == [State.REWARD_NAME]
	var snapshot: Dictionary = session.mastery.snapshot()
	snapshot.mastered_jobs.clear(); snapshot.deliveries.clear()
	checks["returned_snapshot_cannot_mutate_mastery"] = session.mastery.mastery_count() == 3 and session.mastery.status("clinic_thread").deliveries == 2
	before = session.balance
	checks["trail_purchase_exact_fixed_cost"] = session.buy_trail() and session.balance == before - 200 and session.mastery.reward_owned and session.mastery.trail_style == State.LANTERN_AMBER
	before = session.balance
	checks["trail_purchase_idempotent"] = not session.buy_trail() and session.balance == before
	checks["standard_can_always_equip"] = session.set_trail_style(State.STANDARD) and session.mastery.trail_style == State.STANDARD
	checks["owned_amber_re_equip_free"] = session.set_trail_style(State.LANTERN_AMBER) and session.balance == before
	checks["trail_does_not_buy_or_change_liner"] = not session.liner_owned
	checks["liner_purchase_remains_independent"] = session.buy_liner() and session.balance == before - 400 and session.liner_owned and session.mastery.reward_owned
	before = session.balance
	checks["liner_remains_once_only"] = not session.buy_liner() and session.balance == before

	var tight := Session.new()
	finish(tight, 0); finish(tight, 3)
	checks["authored_unlock_example_earns_540"] = tight.balance == 540 and tight.mastery.reward_unlocked()
	tight.buy_liner()
	checks["liner_then_reward_insufficient_funds_no_debt"] = tight.balance == 140 and not tight.buy_trail() and tight.balance == 140
	finish(tight, 0, true, false)
	checks["one_more_base_delivery_can_buy_reward_after_liner"] = tight.balance == 220 and tight.buy_trail() and tight.balance == 20
	var fresh := Session.new()
	checks["new_session_resets_all_progression"] = fresh.balance == 0 and not fresh.liner_owned and fresh.mastery.mastery_count() == 0 and not fresh.mastery.reward_owned

	var state := State.new()
	for bad in [{}, {"attempt_id": 1, "job_id": "unknown", "delivered": true, "objective_met": true}, {"attempt_id": -1, "job_id": "freight_seals", "delivered": true, "objective_met": true}, {"attempt_id": 1, "job_id": "freight_seals", "delivered": "true", "objective_met": true}]:
		checks["malformed_receipt_" + str(checks.size())] = not state.observe_receipt(bad).accepted
	var minimal := {"attempt_id": 1, "job_id": "freight_seals", "delivered": false, "objective_met": true}
	state.observe_receipt(minimal)
	minimal.delivered = true
	checks["same_attempt_cannot_change_cancellation_into_stamp"] = not state.observe_receipt(minimal).accepted and state.mastery_count() == 0
	minimal.attempt_id = 2
	var first := state.observe_receipt(minimal)
	checks["one_real_receipt_first_mastery"] = first.first_mastery and state.mastery_count() == 1
	checks["observer_duplicate_is_not_new_notification"] = not state.observe_receipt(minimal).first_mastery

	var old := OldSession.new()
	var candidate := Session.new()
	var receipts_match := true
	for index in Catalog.JOBS.size():
		for success in [false, true]:
			var a := finish(old, index, true, success, 1000 if success else 0)
			var b := finish(candidate, index, true, success, 1000 if success else 0)
			receipts_match = receipts_match and a == b and old.balance == candidate.balance and old.deliveries == candidate.deliveries
	checks["all_five_old_credit_receipts_byte_value_equal"] = receipts_match
	checks["all_five_stamps_once"] = candidate.mastery.mastery_count() == 5
	checks["all_five_stay_available_after_mastery"] = true
	for contract in Catalog.JOBS:
		checks.all_five_stay_available_after_mastery = checks.all_five_stay_available_after_mastery and candidate.mastery.status(contract.id).available
	var same_standard := true
	var comparable_luminance := true
	var alpha_unchanged := true
	var max_luminance_delta := 0.0
	for i in 101:
		var slip := i / 100.0
		var standard := Palette.color_for(State.STANDARD, slip)
		var amber := Palette.color_for(State.LANTERN_AMBER, slip)
		same_standard = same_standard and standard == Color("69c9b9").lerp(Color("d7c18d"), slip * .35)
		var difference := absf(luminance(amber) / luminance(standard) - 1.0)
		max_luminance_delta = maxf(max_luminance_delta, difference)
		comparable_luminance = comparable_luminance and difference < .02
		alpha_unchanged = alpha_unchanged and amber.a == standard.a
	checks["standard_rgb_exactly_preserved"] = same_standard
	checks["amber_linear_luminance_within_two_percent"] = comparable_luminance
	checks["palette_never_changes_alpha"] = alpha_unchanged
	var passed := true
	for value in checks.values(): passed = passed and value
	var result := {"status": "PASS" if passed else "FAIL", "checks": checks,
		"count": checks.size(), "maximum_palette_luminance_delta_percent": max_luminance_delta * 100.0,
		"scope": "Pure session/receipt and palette checks, not movement or native visual validation"}
	var args := OS.get_cmdline_user_args()
	if args.has("--result"):
		FileAccess.open(args[args.find("--result") + 1], FileAccess.WRITE).store_string(JSON.stringify(result, "  "))
	print("MASTERY_PROGRESSION_RESULT " + JSON.stringify(result))
	quit(0 if passed else 1)
