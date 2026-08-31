#!/usr/bin/env python3
"""Ruthless first-slice payout challenger; exploratory and product-neutral."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import reward_model


def evaluate(base_credits: int, case: dict) -> dict:
    if case.get("terminal", "DELIVERED") != "DELIVERED":
        return {
            "id": case["id"],
            "terminal": case["terminal"],
            "time_factor": None,
            "quality_score": None,
            "grade": None,
            "credits": 0,
        }
    integrity = reward_model.clamp(float(case["integrity"]))
    time_factor = reward_model.clamp(
        reward_model.interpolate_time_factor(max(0.0, float(case["elapsed_par_ratio"])))
    )
    multiplier = 0.50 + 0.35 * integrity + 0.15 * time_factor
    credits = reward_model.round_half_up(base_credits * multiplier)
    quality = 100.0 * (0.35 * integrity + 0.15 * time_factor) / 0.50
    if quality >= 92.0 and integrity >= 0.92:
        grade = "S"
    elif quality >= 80.0 and integrity >= 0.78:
        grade = "A"
    elif quality >= 64.0 and integrity >= 0.55:
        grade = "B"
    elif quality >= 48.0:
        grade = "C"
    else:
        grade = "D"
    return {
        "id": case["id"],
        "terminal": "DELIVERED",
        "time_factor": time_factor,
        "quality_score": quality,
        "grade": grade,
        "credits": credits,
        "receipt": {
            "completion": reward_model.round_half_up(base_credits * 0.50),
            "condition": reward_model.round_half_up(base_credits * 0.35 * integrity),
            "pace_unrounded": base_credits * 0.15 * time_factor,
            "note": "Total rounds once from the raw additive multiplier; display lines are explanatory.",
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cases", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    source = json.loads(args.cases.read_text(encoding="utf-8"))
    report = {
        "schema": "district_zero.p1b.minimum_reward_model_report.v1",
        "status": "SELECTED_FOR_FIRST_SLICE_PROOF_NOT_PRODUCT_AUTHORITY",
        "base_credits": int(source["base_credits"]),
        "results": [evaluate(int(source["base_credits"]), case) for case in source["cases"]],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
