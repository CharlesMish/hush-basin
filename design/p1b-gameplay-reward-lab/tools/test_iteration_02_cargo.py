#!/usr/bin/env python3
"""Deterministic cargo-integrity vectors for overnight iteration 02."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

from iteration_02_cargo_model import (
    CargoIntegrityTracker,
    CargoProfile,
    ObserverDiscontinuity,
    episode_loss_units,
    quantize_severity_milli,
    simulate_pressure_stream,
)


PASS_RECORDS: list[dict] = []


def check(condition: bool, label: str) -> None:
    if not condition:
        raise AssertionError(label)
    PASS_RECORDS.append({"id": label, "status": "PASS"})
    print(f"PASS {label}")


def expect_invalid(callable_value, label: str) -> None:
    try:
        callable_value()
    except ObserverDiscontinuity:
        check(True, label)
        return
    raise AssertionError(label)


def tracker_at_zero() -> CargoIntegrityTracker:
    tracker = CargoIntegrityTracker()
    tracker.start(impact_count=0, hop_count=0, reset_count=0)
    return tracker


def one_impact(severity: float) -> CargoIntegrityTracker:
    tracker = tracker_at_zero()
    tracker.sample(
        sequence=1,
        delta_s=1.0 / 60.0,
        impact_count=1,
        hop_count=0,
        reset_count=0,
        impact_severity=severity,
    )
    return tracker


def two_episode_glances() -> CargoIntegrityTracker:
    tracker = tracker_at_zero()
    tracker.sample(
        sequence=1,
        delta_s=0.01,
        impact_count=1,
        hop_count=0,
        reset_count=0,
        impact_severity=0.50,
    )
    tracker.sample(
        sequence=2,
        delta_s=0.250001,
        impact_count=2,
        hop_count=0,
        reset_count=0,
        impact_severity=0.50,
    )
    return tracker


def run() -> dict:
    profile = CargoProfile()
    profile.validate()
    check(profile.id == "FORGIVING_PEAK_EPISODE_V1", "single shared proof profile has stable identity")
    check(profile.dead_zone_milli == 200, "dead-zone seed is exactly 0.200 severity")
    check(profile.maximum_episode_loss_units == 240, "full-severity episode is capped at 24.0 percent")
    check(profile.response_exponent == 1.50, "response exponent seed is exactly 1.50")
    check(profile.quiet_window_s == 0.250, "quiet window is exactly 0.250 active seconds")

    expected_curve = {
        0.00: 0,
        0.20: 0,
        0.25: 4,
        0.35: 19,
        0.40: 30,
        0.50: 55,
        0.60: 85,
        0.75: 137,
        0.80: 156,
        1.00: 240,
    }
    for severity, units in expected_curve.items():
        check(episode_loss_units(severity) == units, f"golden curve severity {severity:.2f} is {units} units")
    curve_values = [episode_loss_units(index / 1000.0) for index in range(1001)]
    check(curve_values == sorted(curve_values), "damage curve is monotone across every severity milli")
    check(max(curve_values) == 240, "damage curve never exceeds one-episode cap")

    baseline = CargoIntegrityTracker()
    baseline.start(impact_count=7, hop_count=3, reset_count=4)
    check(baseline.integrity_units == 1000, "acceptance snapshots nonzero counters without retroactive loss")
    baseline_result = baseline.sample(
        sequence=1,
        delta_s=1.0 / 60.0,
        impact_count=7,
        hop_count=3,
        reset_count=4,
        impact_severity=0.99,
    )
    check(not baseline_result.impact_observed, "unchanged counter ignores sticky severity")
    check(baseline.integrity_units == 1000, "sticky severity on a quiet tick cannot damage cargo")

    expressive = tracker_at_zero()
    for sequence in range(1, 121):
        expressive.sample(
            sequence=sequence,
            delta_s=1.0 / 120.0,
            impact_count=0,
            hop_count=0,
            reset_count=0,
            impact_severity=float("nan"),
        )
    check(expressive.integrity_units == 1000, "no impact increment means zero loss at any driving state")
    check(not expressive.episode_open, "clean expressive driving never opens an impact episode")

    sub_dead = tracker_at_zero()
    for sequence, severity in enumerate((0.05, 0.12, 0.19, 0.20), start=1):
        result = sub_dead.sample(
            sequence=sequence,
            delta_s=0.02,
            impact_count=sequence,
            hop_count=0,
            reset_count=0,
            impact_severity=severity,
        )
        check(result.damage_units == 0, f"sub-dead-zone impact {severity:.2f} has zero loss")
    check(sub_dead.integrity_units == 1000, "repeated sub-dead-zone contact preserves full integrity")

    rising = tracker_at_zero()
    rising_damage = 0
    for sequence, severity in enumerate((0.25, 0.50, 0.75), start=1):
        result = rising.sample(
            sequence=sequence,
            delta_s=0.05,
            impact_count=sequence,
            hop_count=0,
            reset_count=0,
            impact_severity=severity,
        )
        rising_damage += result.damage_units
    check(rising_damage == 137, "rising episode charges only the incremental peak")
    check(rising.integrity_units == 863, "rising 0.25 to 0.75 episode leaves 86.3 percent")
    direct = one_impact(0.75)
    check(direct.integrity_units == rising.integrity_units, "rising peak equals one direct terminal peak")

    descending = tracker_at_zero()
    descending_deltas = []
    for sequence, severity in enumerate((0.75, 0.50, 0.75, 0.20), start=1):
        descending_deltas.append(
            descending.sample(
                sequence=sequence,
                delta_s=0.04,
                impact_count=sequence,
                hop_count=0,
                reset_count=0,
                impact_severity=severity,
            ).damage_units
        )
    check(descending_deltas == [137, 0, 0, 0], "falling and repeated peaks cannot double-charge")

    rate_trackers = {rate: simulate_pressure_stream(rate) for rate in (30, 60, 120)}
    rate_integrities = {rate: tracker.integrity_units for rate, tracker in rate_trackers.items()}
    check(len(set(rate_integrities.values())) == 1, "30 60 and 120 Hz pressure streams have identical integrity")
    check(set(rate_integrities.values()) == {863}, "rate-invariant pressure stream resolves to 86.3 percent")

    exact_gap = tracker_at_zero()
    first = exact_gap.sample(
        sequence=1,
        delta_s=0.01,
        impact_count=1,
        hop_count=0,
        reset_count=0,
        impact_severity=0.50,
    )
    second = exact_gap.sample(
        sequence=2,
        delta_s=0.25,
        impact_count=2,
        hop_count=0,
        reset_count=0,
        impact_severity=0.50,
    )
    check(first.damage_units == 55 and second.damage_units == 0, "exact 0.250-second gap remains one episode")
    check(exact_gap.episode_id == 1, "equal quiet-window boundary retains episode identity")

    separated = two_episode_glances()
    check(separated.integrity_units == 890, "two glances beyond quiet window each charge once")
    check(separated.episode_id == 2, "strictly beyond quiet window opens a second episode")

    zero_then_glance = tracker_at_zero()
    zero_result = zero_then_glance.sample(
        sequence=1,
        delta_s=0.01,
        impact_count=1,
        hop_count=0,
        reset_count=0,
        impact_severity=0.20,
    )
    glance_result = zero_then_glance.sample(
        sequence=2,
        delta_s=0.10,
        impact_count=2,
        hop_count=0,
        reset_count=0,
        impact_severity=0.50,
    )
    check(not zero_result.settle_interrupt, "observed zero-loss contact does not interrupt unloading")
    check(glance_result.damage_units == 55 and glance_result.settle_interrupt, "positive cargo loss interrupts unloading")

    clean_hop = tracker_at_zero()
    hop_result = clean_hop.sample(
        sequence=1,
        delta_s=1.0 / 60.0,
        impact_count=0,
        hop_count=1,
        reset_count=0,
    )
    check(hop_result.hop_started and hop_result.damage_units == 0, "Hop start is condition-neutral")
    check(hop_result.settle_interrupt, "Hop start invalidates same-tick unloading support")
    clean_landing = clean_hop.sample(
        sequence=2,
        delta_s=0.20,
        impact_count=1,
        hop_count=1,
        reset_count=0,
        impact_severity=0.20,
    )
    check(clean_landing.damage_units == 0 and clean_hop.integrity_units == 1000, "ordinary landing at dead zone loses zero")

    poor_landing = one_impact(0.60)
    wall_strike = one_impact(0.60)
    check(poor_landing.integrity_units == 915, "poor landing seed loses 8.5 percent once")
    check(poor_landing.integrity_units == wall_strike.integrity_units, "landing and wall strike share one impact curve")

    paused = tracker_at_zero()
    paused.sample(
        sequence=1,
        delta_s=0.01,
        impact_count=1,
        hop_count=0,
        reset_count=0,
        impact_severity=0.40,
    )
    paused_before = (paused.active_time_s, paused.integrity_units, paused.episode_id)
    for _ in range(600):
        paused.pause_frame(impact_count=1, hop_count=0, reset_count=0)
    check(paused_before == (paused.active_time_s, paused.integrity_units, paused.episode_id), "pause freezes episode age and integrity")
    pause_resume = paused.sample(
        sequence=2,
        delta_s=0.05,
        impact_count=2,
        hop_count=0,
        reset_count=0,
        impact_severity=0.60,
    )
    check(pause_resume.damage_units == 55 and paused.integrity_units == 915, "resume continues one preserved peak episode")

    reset = tracker_at_zero()
    reset.sample(
        sequence=1,
        delta_s=0.01,
        impact_count=1,
        hop_count=0,
        reset_count=0,
        impact_severity=0.50,
    )
    before_abort = reset.integrity_units
    reset_result = reset.sample(
        sequence=2,
        delta_s=1.0 / 60.0,
        impact_count=0,
        hop_count=0,
        reset_count=1,
        impact_severity=1.0,
    )
    check(reset_result.status == "ABORTED", "reset epoch change aborts before cleared counters are inspected")
    check(reset.integrity_units == before_abort, "same-tick reset cannot add cargo loss")
    reset.sample(
        sequence=99,
        delta_s=99.0,
        impact_count=99,
        hop_count=99,
        reset_count=99,
        impact_severity=1.0,
    )
    check(reset.integrity_units == before_abort, "post-abort samples cannot mutate integrity")

    sealed = one_impact(0.50)
    sealed.seal_delivered()
    sealed_before = sealed.integrity_units
    sealed.sample(
        sequence=2,
        delta_s=1.0,
        impact_count=2,
        hop_count=0,
        reset_count=0,
        impact_severity=1.0,
    )
    check(sealed.integrity_units == sealed_before, "post-delivery samples cannot mutate frozen integrity")

    invalid_gap = tracker_at_zero()
    expect_invalid(
        lambda: invalid_gap.sample(
            sequence=1,
            delta_s=1.0 / 60.0,
            impact_count=2,
            hop_count=0,
            reset_count=0,
            impact_severity=0.50,
        ),
        "impact counter jump fails closed",
    )
    check(invalid_gap.status == "OBSERVER_INVALID", "impact counter jump invalidates attempt observer")

    invalid_rewind = CargoIntegrityTracker()
    invalid_rewind.start(impact_count=4, hop_count=2, reset_count=0)
    expect_invalid(
        lambda: invalid_rewind.sample(
            sequence=1,
            delta_s=1.0 / 60.0,
            impact_count=3,
            hop_count=2,
            reset_count=0,
        ),
        "counter rewind without reset fails closed",
    )
    expect_invalid(
        lambda: tracker_at_zero().sample(
            sequence=2,
            delta_s=1.0 / 60.0,
            impact_count=0,
            hop_count=0,
            reset_count=0,
        ),
        "missing active sample sequence fails closed",
    )
    expect_invalid(
        lambda: tracker_at_zero().sample(
            sequence=1,
            delta_s=0.0,
            impact_count=0,
            hop_count=0,
            reset_count=0,
        ),
        "nonpositive active delta fails closed",
    )
    expect_invalid(
        lambda: tracker_at_zero().sample(
            sequence=1,
            delta_s=float("nan"),
            impact_count=0,
            hop_count=0,
            reset_count=0,
        ),
        "nonfinite active delta fails closed",
    )
    for severity in (float("nan"), -0.01, 1.01):
        expect_invalid(
            lambda severity_value=severity: tracker_at_zero().sample(
                sequence=1,
                delta_s=1.0 / 60.0,
                impact_count=1,
                hop_count=0,
                reset_count=0,
                impact_severity=severity_value,
            ),
            f"invalid impact severity {severity} fails closed",
        )
    expect_invalid(
        lambda: tracker_at_zero().sample(
            sequence=1,
            delta_s=1.0 / 60.0,
            impact_count=1,
            hop_count=0,
            reset_count=0,
        ),
        "missing severity on new impact fails closed",
    )
    expect_invalid(
        lambda: tracker_at_zero().pause_frame(impact_count=1, hop_count=0, reset_count=0),
        "controller counter change during pause fails closed",
    )

    clamp = tracker_at_zero()
    for index in range(1, 6):
        clamp.sample(
            sequence=index,
            delta_s=0.251,
            impact_count=index,
            hop_count=0,
            reset_count=0,
            impact_severity=1.0,
        )
    check(clamp.integrity_units == 0, "repeated severe episodes clamp integrity at zero")
    check(clamp.integrity_units >= 0, "integrity never underflows")
    check(clamp.status == "ACTIVE", "zero integrity remains deliverable in forgiving proof")

    scenarios = {
        "EXPRESSIVE_DRIFT": {
            "integrity_units": expressive.integrity_units,
            "integrity_percent": expressive.integrity_units / 10.0,
            "episode_count": expressive.episode_id,
        },
        "CLEAN_HOP_AND_LANDING": {
            "integrity_units": clean_hop.integrity_units,
            "integrity_percent": clean_hop.integrity_units / 10.0,
            "episode_count": clean_hop.episode_id,
        },
        "LIGHT_BRUSH_035": {
            "integrity_units": one_impact(0.35).integrity_units,
            "integrity_percent": one_impact(0.35).integrity_units / 10.0,
        },
        "GLANCING_STRIKE_050": {
            "integrity_units": one_impact(0.50).integrity_units,
            "integrity_percent": one_impact(0.50).integrity_units / 10.0,
        },
        "POOR_LANDING_060": {
            "integrity_units": poor_landing.integrity_units,
            "integrity_percent": poor_landing.integrity_units / 10.0,
        },
        "SUSTAINED_PRESSURE_075": {
            "integrity_units": rate_trackers[120].integrity_units,
            "integrity_percent": rate_trackers[120].integrity_units / 10.0,
        },
        "SEVERE_STRIKE_100": {
            "integrity_units": one_impact(1.0).integrity_units,
            "integrity_percent": one_impact(1.0).integrity_units / 10.0,
        },
        "TWO_SEPARATE_GLANCES": {
            "integrity_units": separated.integrity_units,
            "integrity_percent": separated.integrity_units / 10.0,
            "episode_count": separated.episode_id,
        },
    }
    return scenarios


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    scenarios = run()
    ids = [record["id"] for record in PASS_RECORDS]
    if len(ids) != len(set(ids)):
        raise AssertionError("cargo report check IDs must be unique")
    report = {
        "schema": "district_zero.p1b.iteration_02_cargo_report.v1",
        "status": "PASS",
        "decision": "R7_COUNTER_EPOCH_FORGIVING_PEAK_EPISODE_V1",
        "parameters": {
            "dead_zone_severity": 0.200,
            "maximum_episode_loss_percent": 24.0,
            "response_exponent": 1.50,
            "quiet_window_active_seconds": 0.250,
            "severity_precision": 0.001,
            "integrity_precision_percent": 0.1,
            "shared_by_initial_contracts": 3,
        },
        "bounded_calibration_ranges": {
            "dead_zone_severity": [0.18, 0.23],
            "maximum_episode_loss_percent": [20.0, 28.0],
            "response_exponent": [1.35, 1.70],
            "quiet_window_active_seconds": [0.20, 0.30],
        },
        "checks": PASS_RECORDS,
        "check_count": len(PASS_RECORDS),
        "scenario_results": scenarios,
        "damage_inputs": ["fresh_impact_count_increment", "matching_last_impact_severity"],
        "explicit_non_inputs": [
            "speed",
            "sideslip",
            "Drive duty",
            "steering",
            "transform",
            "Hop count",
            "support loss or reacquisition",
            "braking",
            "elapsed time",
            "paint id",
            "trail id",
            "COLLISION_SAMPLE count",
        ],
        "product_source_modified": False,
    }
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
