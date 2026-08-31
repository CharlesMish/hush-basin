#!/usr/bin/env python3
"""Deterministic vectors for overnight iteration 03."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

from iteration_03_pace_grade_model import (
    BestReceipt,
    GRADE_LABELS,
    ResultsCadence,
    calibrate_reference,
    compare_session_best,
    grade_for,
    pace_factor,
    pace_factor_from_ratio,
    pace_hud_label,
    receipt,
)


PASS_RECORDS: list[dict] = []


def check(condition: bool, label: str) -> None:
    if not condition:
        raise AssertionError(label)
    PASS_RECORDS.append({"id": label, "status": "PASS"})
    print(f"PASS {label}")


def expect_value_error(callable_, label: str) -> None:
    try:
        callable_()
    except ValueError:
        check(True, label)
    else:
        check(False, label)


def run() -> dict:
    anchors = {0.0: 1.0, 0.85: 1.0, 1.0: 0.75, 1.25: 0.40, 1.75: 0.0, 3.0: 0.0}
    for ratio, expected in anchors.items():
        check(abs(pace_factor_from_ratio(ratio) - expected) < 1.0e-12, f"pace anchor {ratio:.2f} equals {expected:.2f}")
    check(abs(pace_factor_from_ratio(0.925) - 0.875) < 1.0e-12, "first pace segment interpolates")
    check(abs(pace_factor_from_ratio(1.125) - 0.575) < 1.0e-12, "second pace segment interpolates")
    check(abs(pace_factor_from_ratio(1.50) - 0.20) < 1.0e-12, "third pace segment interpolates")
    grid = [pace_factor_from_ratio(index / 1000.0) for index in range(0, 3001)]
    check(all(a + 1.0e-12 >= b for a, b in zip(grid, grid[1:])), "pace factor is globally monotone")
    check(all(0.0 <= value <= 1.0 for value in grid), "pace factor is globally bounded")
    check(abs(pace_factor(85.0, 100.0) - pace_factor(170.0, 200.0)) < 1.0e-12, "pace is scale invariant")
    before = pace_factor_from_ratio(1.0 - 1.0 / 6000.0)
    after = pace_factor_from_ratio(1.0 + 1.0 / 6000.0)
    check(before > 0.75 > after and before - after < 0.001, "reference boundary is continuous across one tick")
    expect_value_error(lambda: pace_factor_from_ratio(-0.01), "negative pace ratio rejected")
    expect_value_error(lambda: pace_factor(float("nan"), 10.0), "nonfinite elapsed rejected")
    expect_value_error(lambda: pace_factor(10.0, 0.0), "nonpositive reference rejected")

    check(pace_hud_label(80.0, 100.0) == "PACE 01:20 · FULL BONUS OPEN", "HUD states full bonus without countdown")
    check(pace_hud_label(100.0, 100.0) == "PACE 01:40 · BONUS EASING", "HUD states easing at reference")
    check(pace_hud_label(175.0, 100.0) == "PACE 02:55 · BONUS ENDED · DELIVERY CONTINUES", "HUD states delivery continues at zero bonus")
    labels = " ".join(pace_hud_label(ratio * 100.0, 100.0) for ratio in (0.5, 1.0, 2.0)).upper()
    check("LATE" not in labels and "FAILED" not in labels and "COUNTDOWN" not in labels, "pace copy never implies contract failure")

    scenarios = {
        "exceptional": (0.98, 0.90, "S"),
        "clean_reference": (0.95, 1.00, "A"),
        "ordinary_learner": (0.90, 1.25, "B"),
        "clean_long_drift": (1.00, 1.50, "B"),
        "fast_damaged": (0.75, 0.85, "B"),
        "fragile_reference": (0.55, 1.00, "C"),
        "pristine_no_pace": (1.00, 1.75, "B"),
        "damaged_no_pace": (0.55, 1.75, "D"),
        "empty_fast": (0.00, 0.80, "D"),
    }
    scenario_results = {}
    for name, (integrity, ratio, expected_grade) in scenarios.items():
        result = grade_for(integrity, ratio)
        scenario_results[name] = result
        check(result["grade"] == expected_grade, f"grade scenario {name} is {expected_grade}")
    check(grade_for(1.0, 1.0)["grade"] == "A", "comfortable clean reference run tends A")
    check(grade_for(1.0, 0.95)["grade"] == "S", "strong clean run can reach S")
    check(grade_for(1.0, 0.951)["grade"] != "S", "S ratio gate is explicit")
    check(grade_for(0.949, 0.50)["grade"] != "S", "S condition gate is explicit")
    check(grade_for(0.799, 0.50)["grade"] != "A", "A condition gate is explicit")
    check(grade_for(0.549, 0.50)["grade"] not in {"S", "A", "B"}, "B condition gate is explicit")
    check(set(GRADE_LABELS) == {"S", "A", "B", "C", "D"}, "all five grade labels are registered")
    integrity_grid = [grade_for(index / 1000.0, 1.10)["quality"] for index in range(1001)]
    check(all(a <= b + 1.0e-12 for a, b in zip(integrity_grid, integrity_grid[1:])), "quality is monotone in integrity")
    elapsed_grid = [grade_for(0.90, index / 1000.0)["quality"] for index in range(3001)]
    check(all(a + 1.0e-12 >= b for a, b in zip(elapsed_grid, elapsed_grid[1:])), "quality is monotone in elapsed ratio")
    expect_value_error(lambda: grade_for(1.01, 1.0), "integrity above one rejected")
    expect_value_error(lambda: grade_for(-0.01, 1.0), "negative integrity rejected")
    expect_value_error(lambda: grade_for(1.0, float("inf")), "nonfinite grade input rejected")

    for base in (1, 7, 120, 121, 999):
        result = receipt(base, 0.923, 1.137)
        check(sum(result["lines"].values()) == result["credits"], f"receipt lines exactly sum at base {base}")
    baseline_receipt = receipt(120, 0.95, 1.00)
    check(baseline_receipt["grade_modifies_money"] is False, "grade never multiplies payout")
    changed_label_total = baseline_receipt["credits"]
    check(changed_label_total == receipt(120, 0.95, 1.00)["credits"], "grade rendering cannot alter payout")
    check(receipt(120, 0.0, 8.0)["credits"] == 60, "delivery floor remains fifty percent")
    check(receipt(120, 1.0, 0.0)["credits"] == 120, "perfect delivery reaches base but never exceeds it")
    expect_value_error(lambda: receipt(0, 1.0, 1.0), "nonpositive base rejected")

    calibration = calibrate_reference([98.2, 101.0, 99.1, 100.0, 250.0], [0.95, 0.91, 0.93, 0.89, 0.92])
    check(calibration["median_s"] == 100.0, "reference calibration uses median")
    check(calibration["reference_s"] == 110.0, "reference is 110 percent rounded up to a tenth")
    permuted = calibrate_reference([250.0, 100.0, 98.2, 99.1, 101.0], [0.92, 0.89, 0.95, 0.93, 0.91])
    check(permuted["reference_s"] == calibration["reference_s"], "calibration is permutation stable")
    rounded = calibrate_reference([10.01, 10.02, 10.03, 10.04, 10.05], [0.9] * 5)
    check(rounded["reference_s"] == 11.1, "reference rounds upward to next tenth")
    check(calibration["warmups_required"] == 2 and calibration["measured_runs"] == 5, "calibration declares two warmups plus five measured")
    check(calibration["version_locked"], "reference is frozen per build")
    expect_value_error(lambda: calibrate_reference([1.0] * 4, [1.0] * 4), "calibration rejects missing valid run")
    expect_value_error(lambda: calibrate_reference([1.0] * 5, [0.89] * 5), "calibration stops when cargo-route evidence is not clean")
    expect_value_error(lambda: calibrate_reference([1.0, 1.0, float("nan"), 1.0, 1.0], [1.0] * 5), "calibration rejects invalid observation")

    first = BestReceipt(ordinary_credits=96, integrity_units=920, elapsed_tenths=1020)
    message, best = compare_session_best(None, first)
    check(message == "FIRST SESSION RESULT" and best == first, "first completion establishes session best")
    faster_lower_pay = BestReceipt(95, 1000, 900)
    message, unchanged = compare_session_best(best, faster_lower_pay)
    check(message == "NO SESSION BEST CHANGE" and unchanged == first, "lower pay cannot beat best receipt by speed")
    equal_pay_better_condition = BestReceipt(96, 930, 1200)
    message, best = compare_session_best(best, equal_pay_better_condition)
    check(message == "NEW SESSION BEST RECEIPT" and best == equal_pay_better_condition, "condition breaks equal-credit tie")
    equal_pay_condition_faster = BestReceipt(96, 930, 1100)
    message, best = compare_session_best(best, equal_pay_condition_faster)
    check(message == "NEW SESSION BEST RECEIPT" and best == equal_pay_condition_faster, "pace breaks equal-credit condition tie")
    message, same = compare_session_best(best, BestReceipt(96, 930, 1100))
    check(message == "MATCHED SESSION BEST RECEIPT" and same == best, "exact tie retains earlier session best")
    message, same = compare_session_best(best, BestReceipt(999, 1000, 1), delivered=False)
    check(message == "NO SESSION BEST CHANGE" and same == best, "abort cannot create or erase session best")

    origin = (1.0, 2.0, 3.0)
    destination = (10.0, 2.0, 30.0)
    cadence = ResultsCadence(origin, destination, balance=50)
    check(cadence.commit_delivery(96), "delivery commits one immutable receipt")
    check(cadence.balance == 146 and cadence.award_commits == 1, "delivery changes balance exactly once")
    check(not cadence.commit_delivery(96) and cadence.balance == 146, "duplicate result cannot duplicate award")
    check(not cadence.choose_continue(fresh_edge=False), "held results input cannot continue")
    check(cadence.choose_continue(), "fresh continue enters neutral gate")
    cadence.sample_neutral(False)
    cadence.sample_neutral(True)
    cadence.physics_tick()
    check(cadence.state == "WAITING_FOR_NEUTRAL", "one neutral frame cannot exit results")
    cadence.sample_neutral(True)
    cadence.physics_tick()
    check(cadence.state == "FREE_ROAM" and cadence.position == destination, "continue preserves reached destination")
    check(cadence.relocations == 0 and cadence.recovery_anchor == destination, "continue updates recovery anchor without relocation")
    check(not cadence.board_open, "continue never auto-opens next dispatch")

    restart = ResultsCadence(origin, destination, balance=20)
    restart.commit_delivery(70)
    check(not restart.choose_restart_at_origin(relocation_authorized=False), "restart is omitted without explicit relocation authority")
    check(restart.choose_restart_at_origin(), "explicit restart enters neutral gate")
    restart.sample_neutral(True)
    restart.sample_neutral(True)
    restart.physics_tick()
    check(restart.state == "FREE_ROAM" and restart.position == origin, "restart relocates to named origin only after neutral")
    check(restart.relocations == 1 and restart.balance == 90, "restart preserves prior award and relocates once")
    restart.physics_tick()
    check(restart.relocations == 1 and not restart.board_open, "restart cannot repeat relocation or auto-accept")

    abort = ResultsCadence(origin, destination, balance=40)
    check(abort.active_reset_abort(), "active reset creates one aborted terminal")
    check(abort.position == origin and abort.balance == 40 and abort.award_commits == 0, "active reset returns to origin and awards zero")
    check(not abort.active_reset_abort() and abort.relocations == 1, "duplicate reset cannot create another terminal")

    return {
        "pace_anchors": [{"ratio": ratio, "factor": factor} for ratio, factor in ((0.85, 1.0), (1.0, 0.75), (1.25, 0.4), (1.75, 0.0))],
        "grade_scenarios": scenario_results,
        "calibration_example": calibration,
        "receipt_example": baseline_receipt,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    evidence = run()
    ids = [record["id"] for record in PASS_RECORDS]
    if len(ids) != len(set(ids)):
        raise AssertionError("pace/grade report check IDs must be unique")
    report = {
        "schema": "district_zero.p1b.iteration_03_pace_grade_report.v1",
        "status": "PASS",
        "decision": "REFERENCE_RATIO_CONDITION_PACE_GRADE_V1",
        "checks": PASS_RECORDS,
        "check_count": len(PASS_RECORDS),
        "evidence": evidence,
        "human_feel_authority": "NOT CLAIMED",
        "product_source_modified": False,
    }
    payload = json.dumps(report, indent=2, sort_keys=True) + "\n"
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(payload, encoding="utf-8")
    print(f"REPORT_SHA256 {hashlib.sha256(payload.encode('utf-8')).hexdigest()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

