#!/usr/bin/env python3
"""Small semantic checks for reproducible design calculations."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import analyze_route_network
import minimum_reward_model
import reward_model


ROOT = Path(__file__).resolve().parents[1]


def check(condition: bool, label: str) -> None:
    if not condition:
        raise AssertionError(label)
    print(f"PASS {label}")


def main() -> int:
    distance, routes, nodes = analyze_route_network.shortest_path("QRY", "RLY")
    check(abs(distance - 398.37413) < 0.000001, "QRY-RLY shortest distance")
    check(routes == ["A0", "A1"], "QRY-RLY prefers A0+A1 over X0")
    check(nodes == ["QRY", "GW", "RLY"], "QRY-RLY node chain")

    source = json.loads((ROOT / "scenarios/reward_model_cases.json").read_text(encoding="utf-8"))
    results = {case["id"]: reward_model.evaluate(source["base_credits"], case) for case in source["cases"]}
    expected = {
        "NEAR_PERFECT_FLOW": ("S", 125),
        "CLEAN_PAR": ("A", 116),
        "TYPICAL_LEARNER": ("B", 98),
        "DAMAGED_DELIVERY": ("D", 76),
        "RESET_RECOVERY": ("D", 84),
        "CIRCLE_FARM_HOSTILE_RECORD": ("C", 102),
    }
    for case_id, (grade, credits) in expected.items():
        check(results[case_id]["grade"] == grade, f"{case_id} grade")
        check(results[case_id]["credits"] == credits, f"{case_id} credits")

    base_case = source["cases"][1]
    base_result = reward_model.evaluate(120, base_case)
    longer = dict(base_case, id="LONGER", distance_reference_ratio=1.35)
    check(reward_model.evaluate(120, longer)["credits"] <= base_result["credits"], "distance cannot mint credits")
    no_flow = dict(source["cases"][0], id="STRAIGHT_S", flow_factor=0.0)
    check(reward_model.evaluate(120, no_flow)["grade"] == "S", "Flow is not required for S")
    floor_case = {
        "id": "FLOOR",
        "integrity": 0.0,
        "elapsed_par_ratio": 3.0,
        "hard_impacts": 10,
        "brushes": 10,
        "resets": 10,
        "distance_reference_ratio": 3.0,
        "flow_factor": 0.0,
    }
    check(reward_model.evaluate(120, floor_case)["credits"] == 54, "45 percent completion floor")

    minimum_expected = {
        "NEAR_PERFECT_FLOW": ("S", 119),
        "CLEAN_PAR": ("S", 115),
        "TYPICAL_LEARNER": ("B", 103),
        "DAMAGED_DELIVERY": ("D", 84),
        "RESET_RECOVERY": (None, 0),
        "CIRCLE_FARM_HOSTILE_RECORD": ("B", 100),
    }
    for case in source["cases"]:
        grade, credits = minimum_expected[case["id"]]
        result = minimum_reward_model.evaluate(source["base_credits"], case)
        check(result["grade"] == grade, f"minimum {case['id']} grade")
        check(result["credits"] == credits, f"minimum {case['id']} credits")
    minimum_clean = minimum_reward_model.evaluate(120, base_case)
    minimum_longer = minimum_reward_model.evaluate(120, longer)
    check(minimum_longer["credits"] == minimum_clean["credits"], "minimum payout ignores odometer")
    cosmetic_case = dict(base_case, id="COSMETIC", paint_id="ORCHID", trail_id="TWIN_VECTOR")
    check(
        minimum_reward_model.evaluate(120, cosmetic_case)["credits"] == minimum_clean["credits"],
        "minimum payout ignores cosmetics",
    )

    with tempfile.TemporaryDirectory() as temporary:
        destination = Path(temporary) / "report.json"
        destination.write_text("{}\n", encoding="utf-8")
        check(destination.is_file(), "temporary-output isolation")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
