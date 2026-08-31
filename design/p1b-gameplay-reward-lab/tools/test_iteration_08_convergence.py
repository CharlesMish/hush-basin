#!/usr/bin/env python3
"""Deterministic final-convergence vectors for overnight iteration 08."""

from __future__ import annotations

import argparse
from dataclasses import replace
from decimal import Decimal
import json
from pathlib import Path

from iteration_04_payout_model import SCORING_VERSION, ScoringSnapshot, derive_contract_terms, evaluate_receipt, snapshot_from_terms
from iteration_08_convergence_model import (
    AUTHORITY,
    DECISION_ID,
    DEFERRED,
    DESK_PAINTS,
    DESK_PAINT_RESERVES,
    DESK_TRAILS,
    DESK_TRAIL_RESERVES,
    EXACT_ENGINE,
    FINAL_STATUS,
    GATE_B_COSMETIC_SCOPE,
    HARD_INVARIANTS,
    INHERITED_CHECK_COUNTS,
    NO_SHOP_LABEL,
    ORCHID_STATIC_R1,
    PROOF_CONTRACT_IDS,
    PROVISIONAL_SEEDS,
    REJECTED_FOR_GATE_B,
    SESSION_WARNING,
    TWIN_VECTOR_R1,
    PaintRefinement,
    TechnicalEvidence,
    TrailRefinement,
    economy_stress_report,
    exact_grade,
    grade_float_boundary_audit,
    implementation_gate_status,
    illustrative_terms,
    proof_contract_snapshot,
    report_summary,
)


D = Decimal
PASS_RECORDS: list[dict] = []


def check(condition: bool, label: str) -> None:
    if not condition:
        raise AssertionError(label)
    PASS_RECORDS.append({"id": label, "status": "PASS"})
    print(f"PASS {label}")


def expect_error(callable_, label: str, error_type: type[Exception] = ValueError) -> None:
    try:
        callable_()
    except error_type:
        check(True, label)
    else:
        check(False, label)


def delivered(integrity_units: int, elapsed_ms: int, reference_ms: int = 100_000):
    terms = derive_contract_terms(contract_id="GRADE_TEST", learned_median_ms=reference_ms * 10 // 11)
    # Grade tests need an exact chosen reference. Rebuild through the public
    # evaluator with the derived reference and scale the supplied ratio.
    actual_elapsed = elapsed_ms * terms.reference_ms // reference_ms
    return evaluate_receipt(
        snapshot_from_terms(
            terms,
            terminal="DELIVERED",
            integrity_units=integrity_units,
            elapsed_ms=actual_elapsed,
        )
    )


def run() -> dict:
    # Keep the pure runner repeatable when imported by a larger verifier.
    PASS_RECORDS.clear()
    check(DECISION_ID == "THREE_JOB_MOMENTUM_COURIER_VERTICAL_SLICE_V1", "final decision identity is exact")
    check(FINAL_STATUS == "DESIGN LAB COMPLETE — AWAITING EXPLICIT P1B IMPLEMENTATION AUTHORITY", "final status does not claim implementation")
    check("NOT GODOT" in AUTHORITY and "HUMAN" in AUTHORITY, "authority names missing evidence classes")
    check(sum(INHERITED_CHECK_COUNTS) == 734, "all eight inherited suite counts sum to 734")
    check(len(INHERITED_CHECK_COUNTS) == 8, "exactly eight pre-convergence suite counts are bound")
    check(SESSION_WARNING == "SESSION PROTOTYPE — CREDITS AND FINISHES RESET WHEN THE APP CLOSES", "session warning is exact")
    check(NO_SHOP_LABEL == "SESSION CREDITS · NO SHOP IN THIS PROOF", "Gate-B no-shop label is exact")

    contracts = proof_contract_snapshot()
    check(tuple(row["contract_id"] for row in contracts) == PROOF_CONTRACT_IDS, "proof catalog is exactly C01 C02 C03")
    check(tuple(row["title"] for row in contracts) == ("Market Parcel", "Relay Window", "Clinic Glass"), "proof titles are stable")
    check(tuple((row["origin"], row["destination"]) for row in contracts) == (("MRK", "DEP"), ("DEP", "RLY"), ("RLY", "CLN")), "proof chain is spatially continuous")
    check(len({row["family"] for row in contracts}) == 1, "all proof contracts share one mechanical family")
    check(len({row["cargo_profile"] for row in contracts}) == 1, "all proof contracts share one cargo profile")
    check(all(row["complexity_class"] == 0 and row["complexity_reason"] == "NONE" for row in contracts), "all proof contracts are K0 NONE")
    check(all(option["advisory_only"] for row in contracts for option in row["route_options"]), "every route option is advisory only")
    lengths = {
        (row["contract_id"], option["option_id"]): option["suggested_distance_m"]
        for row in contracts for option in row["route_options"]
    }
    check(lengths[("C01", "MARKET_DIRECT")] == D("129.429845"), "C01 route length is exact")
    check(lengths[("C02", "LONG_WEST_SWEEP")] == D("394.186048"), "C02 suggested route length is exact")
    check(lengths[("C03", "INNER_CLINIC")] == D("377.225159"), "C03 inner route length is exact")
    check(lengths[("C03", "OUTER_EASTLINE")] == D("514.603795"), "C03 legal outer route length is exact")
    check(len(contracts[0]["route_options"]) == 1 and len(contracts[1]["route_options"]) == 1 and len(contracts[2]["route_options"]) == 2, "route-option cardinality is exact")

    check(len(HARD_INVARIANTS) == len(set(HARD_INVARIANTS)) == 14, "fourteen final invariants are unique")
    for required in (
        "R7_MOVEMENT_WORLD_CAMERA_VEHICLE_BYTES_UNCHANGED",
        "CLEAN_DRIFT_HOP_LANDING_ROUGH_TRAVEL_ZERO_CARGO_LOSS",
        "ROUTE_DISTANCE_FLOW_GRADE_COSMETICS_REPEATS_NEVER_PAY",
        "NO_SHOP_TRAIL_SAVE_REPUTATION_OR_MECHANICAL_UPGRADE",
    ):
        check(required in HARD_INVARIANTS, f"hard invariant retained: {required}")
    check(PROVISIONAL_SEEDS["cargo_dead_zone"] == "0.20", "cargo dead-zone seed is retained")
    check(PROVISIONAL_SEEDS["cargo_max_episode_loss"] == "0.24", "cargo episode-loss seed is retained")
    check(PROVISIONAL_SEEDS["cargo_exponent"] == "1.50", "cargo exponent seed is retained")
    check(PROVISIONAL_SEEDS["cargo_quiet_window_s"] == "0.25", "cargo quiet-window seed is retained")
    check(PROVISIONAL_SEEDS["pickup_speed_ceiling_mps"] == "4.0", "pickup speed seed is retained")
    check(PROVISIONAL_SEEDS["delivery_speed_ceiling_mps"] == "6.0", "delivery speed seed is retained")
    check(PROVISIONAL_SEEDS["delivery_settle_s"] == "0.50", "settle-time seed is retained")
    check(PROVISIONAL_SEEDS["pace_anchors"] == (("0.85", "1.00"), ("1.00", "0.75"), ("1.25", "0.40"), ("1.75", "0.00")), "pace anchors are exact")

    terms = illustrative_terms()
    check(tuple(terms) == PROOF_CONTRACT_IDS, "illustrative term order follows proof chain")
    check(tuple(item.valuation_ms for item in terms.values()) == (30_000, 60_000, 90_000), "illustrative valuation durations are exact")
    check(tuple(item.reference_ms for item in terms.values()) == (33_000, 66_000, 99_000), "illustrative references are 1.10x")
    check(tuple(item.base_credits for item in terms.values()) == (70, 120, 170), "illustrative K0 bases are exact")
    check(all(item.complexity_class == 0 and item.complexity_reason == "NONE" for item in terms.values()), "illustrative terms cannot smuggle complexity")

    economy = economy_stress_report()
    check(economy["scenarios"]["COMPLETION_FLOOR"]["chain_total"] == 180, "completion-floor chain pays 180 illustrative Credits")
    check(economy["scenarios"]["TYPICAL_LEARNER"]["chain_total"] == 315, "typical learner chain pays 315 illustrative Credits")
    check(economy["scenarios"]["LEARNED_CLEAN"]["chain_total"] == 349, "learned-clean chain pays 349 illustrative Credits")
    check(economy["scenarios"]["CLEAN_REFERENCE"]["chain_total"] == 340, "clean-reference chain pays 340 illustrative Credits")
    check(economy["scenarios"]["WALL_PRESSURE_SYNTHETIC"]["chain_total"] == 330, "synthetic wall-pressure chain pays 330 illustrative Credits")
    check(tuple(row["actual_overhead_s"] for row in economy["cadence_sensitivity"]) == (4, 8, 12, 16, 20), "cadence stress uses five preregistered overheads")
    expected_spreads = (D("13.939"), D("6.284"), D("0.493"), D("5.300"), D("10.294"))
    check(tuple(row["learned_clean_rate_spread_percent"] for row in economy["cadence_sensitivity"]) == expected_spreads, "cadence sensitivity reproduces exact spreads")
    check(economy["cadence_sensitivity"][0]["learned_clean_rate_spread_percent"] > D("5"), "four-second overhead fails preferred rate spread")
    check(economy["cadence_sensitivity"][2]["learned_clean_rate_spread_percent"] < D("5"), "matched twelve-second overhead meets preferred rate spread")
    check(any(row["wall_pressure_dominates"] for row in economy["cadence_sensitivity"]), "synthetic wall pressure exposes at least one rate dominance")
    check(economy["wall_pressure_status"].startswith("OPEN NATIVE FALSIFIER"), "wall-pressure risk remains open")
    check("measure overhead" in economy["required_action"], "economy requires measured cadence before freezing")
    price = economy["conditional_price_sensitivity"]
    check((price["typical_chain_original"], price["typical_chain_reduced"]) == (315, 284), "minus-ten-percent base perturbation changes typical chain 315 to 284")
    check((price["floor_chain_original"], price["floor_chain_reduced"]) == (180, 163), "minus-ten-percent base perturbation changes floor chain 180 to 163")
    check((price["floor_plus_typical_c01_after_240_original"], price["floor_plus_typical_c01_after_240_reduced"]) == (1, -22), "conditional shelf margin changes from plus one to minus twenty-two")

    grade_audit = grade_float_boundary_audit()
    check((grade_audit["points_scanned"], grade_audit["mismatch_count"]) == (3_004_001, 55), "full 0.001 legacy-float grid reproduces fifty-five grade mismatches")
    check(
        tuple((item["integrity_units"], item["ratio_milli"], item["legacy_grade"], item["exact_grade"]) for item in grade_audit["examples"])
        == ((215, 851, "D", "C"), (575, 955, "C", "B"), (835, 979, "B", "A")),
        "three exact float-boundary regression examples are preserved",
    )

    # Exact grade evaluator: derive labels from canonical integer receipt data,
    # never from a UI-provided label or binary-float threshold.
    check(exact_grade(delivered(1000, 95_000)) == "S", "exact S ratio boundary is inclusive when quality clears")
    check(exact_grade(delivered(1000, 95_100)) != "S", "S ratio gate rejects one tenth beyond boundary")
    check(exact_grade(delivered(800, 85_000)) == "A", "A integrity floor may pass at strong pace")
    check(exact_grade(delivered(799, 85_000)) != "A", "A integrity floor rejects one unit below")
    check(exact_grade(delivered(550, 100_000)) == "C", "condition-floor gate can hold quality below B")
    check(exact_grade(delivered(549, 100_000)) == "C", "one unit below B integrity stays C")
    check(exact_grade(delivered(0, 80_000)) == "D", "zero-integrity fast completion remains D")
    boundary_terms = derive_contract_terms(contract_id="BOUNDARY", learned_median_ms=100_000)
    for integrity_units, elapsed_ms, expected, label in (
        (215, 93_610, "C", "exact Q45 binary-float seam resolves C"),
        (575, 105_050, "B", "exact Q65 binary-float seam resolves B"),
        (835, 107_690, "A", "exact Q82 binary-float seam resolves A"),
    ):
        receipt = evaluate_receipt(snapshot_from_terms(boundary_terms, terminal="DELIVERED", integrity_units=integrity_units, elapsed_ms=elapsed_ms))
        check(exact_grade(receipt) == expected, label)
    aborted = evaluate_receipt(snapshot_from_terms(boundary_terms, terminal="ABORTED", integrity_units=1000, elapsed_ms=0))
    check(exact_grade(aborted) == "ABORTED", "grade projection preserves non-delivery terminal")
    forged = replace(delivered(950, 95_000), credits=999)
    expect_error(lambda: exact_grade(forged), "grade projection rejects a noncanonical receipt")
    visible_example = evaluate_receipt(ScoringSnapshot("DELIVERED", "VISIBLE_EXAMPLE", "0" * 64, 100, 920, 102_000, 95_000, SCORING_VERSION))
    check((visible_example.credits, visible_example.delivery_line, visible_example.condition_line, visible_example.pace_line, exact_grade(visible_example)) == (92, 50, 32, 10, "A"), "final visible Results example is canonically reconciled")

    check(DESK_PAINTS == ("ORCHID_STATIC", "SALTGLASS", "EMBER_RELAY"), "strongest desk paint 3-set is exact")
    check(DESK_TRAILS == ("TWIN_VECTOR", "COURIER_PULSE", "COMET_LEDGER"), "strongest desk trail 3-set is exact")
    check(DESK_PAINT_RESERVES == ("VESPER_CERAMIC", "MOSS_CIRCUIT"), "paint reserves are exact")
    check(DESK_TRAIL_RESERVES == ("ONE_WAKE", "TIDE_SCRIPT"), "trail reserves are exact")
    check(len(set(DESK_PAINTS + DESK_PAINT_RESERVES)) == 5, "paint finalists and reserves are unique")
    check(len(set(DESK_TRAILS + DESK_TRAIL_RESERVES)) == 5, "trail finalists and reserves are unique")
    check(GATE_B_COSMETIC_SCOPE == ("DISTRICT_STANDARD", "TWO_NATIVE_APPROVED_PROOF_PAINTS", "TRAIL_OFF"), "Gate-B cosmetic scope excludes a trail")
    ORCHID_STATIC_R1.validate()
    check(ORCHID_STATIC_R1.candidate_id == DESK_PAINTS[0], "iteration refines one existing lead paint")
    check(ORCHID_STATIC_R1.emission_ceilings["trim"] == D("0.52"), "Orchid trim ceiling is exact")
    check(max(ORCHID_STATIC_R1.emission_ceilings.values()) <= D("0.75"), "Orchid cannot exceed global cosmetic ceiling")
    check("DESK REFINEMENT" in ORCHID_STATIC_R1.status, "Orchid refinement does not claim native selection")
    bad_paint = PaintRefinement(ORCHID_STATIC_R1.candidate_id, {**ORCHID_STATIC_R1.colors, "trim": "nothex"}, ORCHID_STATIC_R1.emission_ceilings, ORCHID_STATIC_R1.copy)
    expect_error(lambda: bad_paint.validate(), "malformed paint color fails closed")
    bright_paint = PaintRefinement(ORCHID_STATIC_R1.candidate_id, ORCHID_STATIC_R1.colors, {**ORCHID_STATIC_R1.emission_ceilings, "trim": D("0.76")}, ORCHID_STATIC_R1.copy)
    expect_error(lambda: bright_paint.validate(), "paint above global ceiling fails closed")

    TWIN_VECTOR_R1.validate()
    check(TWIN_VECTOR_R1.candidate_id == DESK_TRAILS[0], "iteration refines one existing lead trail")
    check(TWIN_VECTOR_R1.port_anchor[0] == -TWIN_VECTOR_R1.starboard_anchor[0], "Twin Vector anchors are mirrored")
    check(TWIN_VECTOR_R1.samples_per_rail == 32 and TWIN_VECTOR_R1.total_vertices == 128, "Twin Vector history geometry cap is exact")
    check(TWIN_VECTOR_R1.history_s == D("0.58") and TWIN_VECTOR_R1.history_m == D("18"), "Twin Vector history bounds are exact")
    check(TWIN_VECTOR_R1.reduced_samples_per_rail == 12 and TWIN_VECTOR_R1.reduced_history_s == D("0.24"), "Twin Vector reduced-motion bounds are exact")
    check("OUTSIDE GATE B" in TWIN_VECTOR_R1.status, "trail refinement stays outside Gate B")
    bad_trail = replace(TWIN_VECTOR_R1, total_vertices=130)
    expect_error(lambda: bad_trail.validate(), "oversize trail geometry fails closed")
    forward_trail = replace(TWIN_VECTOR_R1, port_anchor=(D("0.24"), D("-0.04"), D("1.16")))
    expect_error(lambda: forward_trail.validate(), "forward-side trail anchor fails closed")
    nonfinite_trail = replace(TWIN_VECTOR_R1, history_s=D("NaN"))
    expect_error(lambda: nonfinite_trail.validate(), "nonfinite trail profile fails closed")

    empty = TechnicalEvidence()
    check(implementation_gate_status(empty) == "NOT AUTHORIZED — DESIGN LAB ONLY", "current gate stops without implementation authority")
    authority_only = replace(empty, implementation_authority=True)
    check(implementation_gate_status(authority_only) == "BLOCKED — EXACT ENGINE", "authority cannot waive exact engine")
    engine = replace(authority_only, engine_identity=EXACT_ENGINE)
    check(implementation_gate_status(engine) == "BLOCKED — R7 PRESERVATION OR REGRESSION", "engine alone cannot waive R7 proof")
    r7 = replace(engine, r7_byte_identity=True, r7_regression_and_c1_zero=True)
    check(implementation_gate_status(r7) == "BLOCKED — INPUT OR TERMINAL SEAM", "R7 proof cannot waive input seam")
    seam = replace(r7, input_and_terminal_seam=True)
    check(implementation_gate_status(seam) == "BLOCKED — CARGO OBSERVER", "input proof cannot waive cargo observer")
    cargo = replace(seam, cargo_observer_separation=True)
    check(implementation_gate_status(cargo) == "READY FOR OWNER GATE A — NOT PERFORMED", "C01 technical evidence stops before owner Gate A")
    gate_a = replace(cargo, owner_gate_a=True)
    check(implementation_gate_status(gate_a) == "BLOCKED — RECOVERY ANCHOR; STOP AFTER C01", "Gate A cannot unlock breadth without recovery anchor")
    anchor = replace(gate_a, recovery_anchor=True)
    check(implementation_gate_status(anchor) == "BLOCKED — NATIVE PAINT QUALIFICATION", "recovery proof cannot invent paint qualification")
    paint = replace(anchor, two_native_paints=True)
    check(implementation_gate_status(paint) == "READY FOR OWNER GATE B — NOT PERFORMED", "reward qualification stops before owner Gate B")
    gate_b = replace(paint, owner_gate_b=True)
    check(implementation_gate_status(gate_b) == "GATE B OWNER REVIEW COMPLETE — RETURN FOR A NEW DIRECTOR DECISION", "Gate B returns without self-authorizing expansion")

    check("PAID_SHOP" in DEFERRED and "ANY_TRAIL_STOCK" in DEFERRED and "DURABLE_SAVE" in DEFERRED, "shop trail and save are deferred")
    check("RESULTS_RESTART_RELOCATION" in DEFERRED, "results relocation remains separately authorized")
    check("RAW_SPEED_BRAKE_INTEGRITY_OR_HANDLING_UPGRADES" in REJECTED_FOR_GATE_B, "mechanical upgrades are rejected")
    check("FOURTH_GATE_B_CONTRACT" in REJECTED_FOR_GATE_B, "fourth proof contract is rejected")
    check(len(DEFERRED) == len(set(DEFERRED)), "deferred list is unique")
    check(len(REJECTED_FOR_GATE_B) == len(set(REJECTED_FOR_GATE_B)), "rejected list is unique")

    summary = report_summary()
    check(summary["implementation_gate_now"] == "NOT AUTHORIZED — DESIGN LAB ONLY", "report preserves current authority stop")
    check(summary["product_source_modified"] is False and summary["R7_source_modified"] is False, "report records no product or R7 modification")
    check(summary["godot_runtime"] == "NOT PERFORMED IN ITERATION 08", "report does not claim Godot execution")
    check(summary["human_world_gate"] == "NOT PERFORMED", "report does not claim Human World Gate")
    check(summary["P1B_product_implementation"] == "NOT STARTED" and summary["P1B_pass"] is False, "report does not claim P1B implementation or pass")

    summary["checks"] = {
        "passed": len(PASS_RECORDS),
        "failed": 0,
        "total": len(PASS_RECORDS),
        "status": "PASS WITH EXPLICIT NATIVE, ECONOMY, COSMETIC, AND OWNER GATES REMAINING",
        "records": list(PASS_RECORDS),
    }
    summary["aggregate_pure_checks"] = sum(INHERITED_CHECK_COUNTS) + len(PASS_RECORDS)
    return summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = run()
    encoded = json.dumps(report, indent=2, sort_keys=True, default=str) + "\n"
    if args.output is not None:
        args.output.write_text(encoded, encoding="utf-8")
    print(json.dumps({"status": report["checks"]["status"], "checks": report["checks"]["total"], "aggregate": report["aggregate_pure_checks"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
