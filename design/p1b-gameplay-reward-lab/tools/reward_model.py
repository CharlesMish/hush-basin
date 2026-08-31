#!/usr/bin/env python3
"""Pure exploratory scoring model; this is not District Zero product code."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path


TIME_ANCHORS = (
    (0.85, 1.00),
    (1.00, 0.85),
    (1.25, 0.55),
    (1.75, 0.20),
    (2.50, 0.00),
)


def clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return min(high, max(low, value))


def interpolate_time_factor(ratio: float) -> float:
    if ratio <= TIME_ANCHORS[0][0]:
        return TIME_ANCHORS[0][1]
    if ratio >= TIME_ANCHORS[-1][0]:
        return TIME_ANCHORS[-1][1]
    for (left_x, left_y), (right_x, right_y) in zip(TIME_ANCHORS, TIME_ANCHORS[1:]):
        if ratio <= right_x:
            alpha = (ratio - left_x) / (right_x - left_x)
            return left_y + (right_y - left_y) * alpha
    raise AssertionError("unreachable")


def round_half_up(value: float) -> int:
    if value < 0:
        raise ValueError("reward amounts must be nonnegative")
    return math.floor(value + 0.5)


def evaluate(base_credits: int, case: dict) -> dict:
    integrity = clamp(float(case["integrity"]))
    time_factor = clamp(interpolate_time_factor(max(0.0, float(case["elapsed_par_ratio"]))))
    clean_factor = clamp(
        1.0
        - 0.18 * max(0, int(case["hard_impacts"]))
        - 0.05 * max(0, int(case["brushes"]))
        - 0.35 * max(0, int(case["resets"]))
    )
    distance_ratio = max(1.0, float(case["distance_reference_ratio"]))
    efficiency_factor = clamp((1.40 - distance_ratio) / 0.40)
    flow_factor = clamp(float(case["flow_factor"]))

    condition_term = 0.30 * integrity**1.40
    time_term = 0.15 * time_factor
    clean_term = 0.06 * clean_factor
    efficiency_term = 0.04 * efficiency_factor
    ordinary_multiplier = 0.45 + condition_term + time_term + clean_term + efficiency_term
    ordinary_credits = round_half_up(base_credits * ordinary_multiplier)
    flow_credits = round_half_up(base_credits * 0.06 * flow_factor * (0.50 + 0.50 * integrity))
    quality = 100.0 * (condition_term + time_term + clean_term + efficiency_term) / 0.55

    if quality >= 92.0 and integrity >= 0.92 and int(case["resets"]) == 0:
        grade = "S"
    elif quality >= 80.0 and integrity >= 0.78:
        grade = "A"
    elif quality >= 64.0 and integrity >= 0.55:
        grade = "B"
    elif quality >= 48.0:
        grade = "C"
    else:
        grade = "D"
    if int(case["resets"]) > 0 and grade in {"S", "A"}:
        grade = "B"

    return {
        "id": case["id"],
        "factors": {
            "integrity": integrity,
            "time": time_factor,
            "clean": clean_factor,
            "efficiency": efficiency_factor,
            "flow": flow_factor,
        },
        "ordinary_multiplier": ordinary_multiplier,
        "quality_score": quality,
        "grade": grade,
        "ordinary_credits": ordinary_credits,
        "flow_credits": flow_credits,
        "credits": ordinary_credits + flow_credits,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cases", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    source = json.loads(args.cases.read_text(encoding="utf-8"))
    base = int(source["base_credits"])
    report = {
        "schema": "district_zero.p1b.reward_model_report.v1",
        "base_credits": base,
        "status": "EXPLORATORY_NOT_PRODUCT_AUTHORITY",
        "results": [evaluate(base, case) for case in source["cases"]],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
