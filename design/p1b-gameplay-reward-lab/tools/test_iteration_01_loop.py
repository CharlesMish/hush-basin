#!/usr/bin/env python3
"""Deterministic transition vectors for overnight iteration 01."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from iteration_01_loop_model import LoopModel, delivery_feedback, dispatch_eligible


PASS_RECORDS: list[dict] = []


def check(condition: bool, label: str) -> None:
    if not condition:
        raise AssertionError(label)
    PASS_RECORDS.append({"id": label, "status": "PASS"})
    print(f"PASS {label}")


def active_model() -> LoopModel:
    model = LoopModel()
    assert model.open_board(eligible=True)
    assert model.accept()
    model.sample_neutral({})
    assert model.paused
    model.sample_neutral({})
    assert not model.paused
    model.physics_tick(1.0 / 60.0)
    assert model.state == "ACTIVE"
    return model


def run() -> None:
    check(
        dispatch_eligible(
            distance_to_pad_m=8.0,
            support_probe_count=2,
            measured_height_m=1.65,
            tangential_speed_mps=4.0,
        ),
        "dispatch exact spatial and speed boundaries are inclusive",
    )
    check(
        not dispatch_eligible(
            distance_to_pad_m=8.001,
            support_probe_count=2,
            measured_height_m=1.65,
            tangential_speed_mps=0.0,
        ),
        "dispatch rejects outer pad blend",
    )
    check(
        not dispatch_eligible(
            distance_to_pad_m=0.0,
            support_probe_count=2,
            measured_height_m=1.65,
            tangential_speed_mps=4.01,
        ),
        "dispatch press revalidation rejects excess speed",
    )
    check(
        not dispatch_eligible(
            distance_to_pad_m=0.0,
            support_probe_count=1,
            measured_height_m=1.65,
            tangential_speed_mps=0.0,
        ),
        "dispatch rejects insufficient support",
    )
    check(
        not dispatch_eligible(
            distance_to_pad_m=float("nan"),
            support_probe_count=3,
            measured_height_m=1.65,
            tangential_speed_mps=0.0,
        ),
        "dispatch rejects nonfinite observation",
    )
    feedback_base = {
        "destination_label": "DEP",
        "distance_to_pad_m": 4.0,
        "support_probe_count": 3,
        "measured_height_m": 1.65,
        "tangential_speed_mps": 2.0,
        "cargo_loss_increment": 0.0,
        "settle_fraction": 0.42,
    }
    check(
        delivery_feedback(**dict(feedback_base, distance_to_pad_m=8.001)) == "REACH DEP",
        "delivery feedback prioritizes outside zone",
    )
    check(
        delivery_feedback(**dict(feedback_base, support_probe_count=1)) == "TOUCH DOWN",
        "delivery feedback prioritizes support after zone",
    )
    check(
        delivery_feedback(**dict(feedback_base, cargo_loss_increment=0.01)) == "CARGO MOVING — STABILIZE",
        "delivery feedback exposes cargo-loss impact",
    )
    check(
        delivery_feedback(**dict(feedback_base, tangential_speed_mps=8.1)) == "SLOW · 8.1 / 6.0 m/s",
        "delivery feedback exposes exact speed failure",
    )
    check(delivery_feedback(**feedback_base) == "UNLOADING 42%", "delivery feedback exposes settle progress")

    model = LoopModel()
    check(not model.open_board(eligible=False), "ineligible dispatch rejected")
    check(model.state == "FREE_ROAM", "ineligible dispatch preserves free roam")
    check(model.open_board(eligible=True), "fresh dispatch opens board")
    check(model.paused, "board owns pause")
    check(not model.accept(fresh_edge=False), "opener hold cannot accept")
    check(model.accept(fresh_edge=True), "new accept edge enters neutral latch")
    model.sample_neutral({"interact": 1.0})
    model.sample_neutral({})
    check(model.paused, "held-or-single-neutral frame cannot cross modal")
    model.sample_neutral({})
    check(not model.paused, "two consecutive neutral frames release modal")
    check(model.elapsed_s == 0.0, "modal and neutral time are free")
    model.physics_tick(1.0 / 60.0)
    check(model.state == "ACTIVE", "first resumed physics activates contract")
    check(abs(model.elapsed_s - 1.0 / 60.0) < 1.0e-12, "first resumed physics charges one delta")

    paused = active_model()
    paused.physics_tick(0.20, delivery_valid=True)
    before_time = paused.elapsed_s
    before_settle = paused.settle_s
    check(paused.open_pause(), "fresh pause opens overlay")
    paused.physics_tick(0.5, delivery_valid=True)
    check(paused.elapsed_s == before_time and paused.settle_s == before_settle, "pause freezes clock and settle")
    check(paused.close_pause(), "fresh pause close enters neutral latch")
    paused.sample_neutral({})
    paused.sample_neutral({})
    paused.physics_tick(1.0 / 60.0, delivery_valid=False)
    check(abs(paused.elapsed_s - before_time - 1.0 / 60.0) < 1.0e-12, "resume has no delta catch-up")
    check(paused.settle_s == 0.0, "invalid resumed sample resets preserved settle")

    settle = active_model()
    settle.physics_tick(1.0 / 60.0, delivery_valid=True)
    check(settle.state == "DELIVERY_SETTLE", "valid arrival begins automatic settle")
    check(settle.settle_s > 0.0, "first valid tick counts toward settle")
    settle.physics_tick(1.0 / 60.0, delivery_valid=True, cargo_loss_impact=False)
    check(settle.state == "DELIVERY_SETTLE" and settle.settle_s > 1.0 / 60.0, "zero-loss contact preserves settle")
    settle.physics_tick(1.0 / 60.0, delivery_valid=True, cargo_loss_impact=True)
    check(settle.state == "ACTIVE" and settle.settle_s == 0.0, "cargo-loss impact resets settle before terminal")
    for _ in range(29):
        settle.physics_tick(1.0 / 60.0, delivery_valid=True)
    check(settle.state != "RESULTS", "twenty-nine valid ticks cannot complete half-second settle")
    settle.physics_tick(1.0 / 60.0, delivery_valid=True)
    check(settle.state == "RESULTS" and settle.terminal == "DELIVERED", "thirty valid ticks commit delivery")
    check(settle.result_commits == 1 and settle.award_commits == 1, "delivery commits result and award once")
    settle.physics_tick(1.0 / 60.0, delivery_valid=True)
    check(settle.result_commits == 1 and settle.award_commits == 1, "post-result samples cannot double award")

    race = active_model()
    for _ in range(29):
        race.physics_tick(1.0 / 60.0, delivery_valid=True)
    race.physics_tick(1.0 / 60.0, delivery_valid=True, reset=True)
    check(race.terminal == "ABORTED" and race.state == "ABORTED", "reset wins delivery terminal race")
    check(race.result_commits == 0 and race.award_commits == 0, "aborted attempt awards zero")

    modal = LoopModel()
    modal.open_board(eligible=True)
    check(modal.consume_modal_reset(), "board consumes reset without R7 teleport")
    check(modal.state == "BOARD_OPEN", "modal reset preserves board and creates no terminal")

    results = active_model()
    for _ in range(30):
        results.physics_tick(1.0 / 60.0, delivery_valid=True)
    check(results.continue_results(), "fresh continue enters neutral latch")
    results.sample_neutral({"accept": 1.0})
    results.sample_neutral({})
    check(results.paused, "held result input cannot resume world")
    results.sample_neutral({})
    results.physics_tick(1.0 / 60.0)
    check(results.state == "FREE_ROAM", "neutral result exit returns to free roam")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    run()
    ids = [record["id"] for record in PASS_RECORDS]
    if len(ids) != len(set(ids)):
        raise AssertionError("transition report check IDs must be unique")
    report = {
        "schema": "district_zero.p1b.iteration_01_transition_report.v1",
        "status": "PASS",
        "checks": PASS_RECORDS,
        "check_count": len(PASS_RECORDS),
        "product_source_modified": False,
    }
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
