#!/usr/bin/env python3
"""C1 comparator for the owner-authorized presentation-only vehicle R7."""
from __future__ import annotations

import json
import math
from pathlib import Path
import sys

from compare_p1a_baseline import (
    ComparisonFailure,
    EXPECTED_FIXTURE_SHA256,
    EXPECTED_TICKS,
    compare_value,
    load_jsonl,
    sha256,
)


EXPECTED_FILES = {
    "P1A_POST_V1_2_8_VEHICLE_INTEGRATION_R7_AUTHORITY.md": "aa6ff80400cd54906d085b5ed297eee08bf054264e03c014bd9f77e578a7157d",
    "project.godot": "2d09d7f399dce2c13f66299494e2066ef9ca622d32a2beb59925eb918c60d370",
    "resources/default_tuning.tres": "a6d7a6ef66f28a480bc28096c91124e5c93f9b8e7dd32c68296030ce21800459",
    "scenes/craft.tscn": "f6380bddd74692b1658bc77313231cf1ff49ea6e0400f9dbfe4d45c0dbd68877",
    "scenes/district_zero_p1a.tscn": "d98701322aaca814e14d561c71bb31cf1bffc84c706f831fa54f511ce579f12b",
    "scenes/vehicle_visual.tscn": "21efabf4d66a33b446687dbcd485f764b38897fb8cf44f72a7c7db4591b3bdc9",
    "scripts/camera_rig.gd": "8d4ae9565d868f1d531e3c8e22d0e6214f52ea738fb724e2116ba263cd21eebb",
    "scripts/craft_controller.gd": "c87d7fefa2c5c8489ab31508992293a81e31fa7a7efd8e1fc17aac2f74d41e6b",
    "scripts/craft_tuning.gd": "c6b82758d7d985d0a16d16a7265a52e2ba2b5a4ec2e608a08ef1d2fa7650acfd",
    "scripts/motion_math.gd": "c2ceb0ab0f5bcff7d6a4cf7c2b6e3c7fa1c70b96edee206d00b529d3329ed575",
    "scripts/p1a_map.gd": "04962dedc18f5df47a8fac90465004fdc18668e93fbf2e2715011a398f1b9ff4",
    "scripts/p1a_world_builder.gd": "ee0b33608a033443e6674779cc0bf4c8469a6f083605b6850b707c4652f5cd2b",
    "scripts/p1a_world_gate.gd": "500b4a7ee6c527c12fa3eadae8e52fb4d3232389427069c748102abfd24d593a",
    "scripts/surface_feedback_3d.gd": "8db47e1ba550efc3c0bfa871edae2a74ab103d7720ed8284add75057eaa4bda6",
    "scripts/vehicle_visual_rig.gd": "7f798341f24cd103bd8b58f6baee58f6612dd532c4bf7f24ddf751d47d7016c3",
}


def main(argv: list[str]) -> int:
    if len(argv) != 4:
        print("usage: compare_vehicle_r7_c1.py BASE_TRACE R7_TRACE FIXTURE", file=sys.stderr)
        return 2
    baseline_path, selected_path, fixture_path = map(Path, argv[1:])
    try:
        if sha256(fixture_path) != EXPECTED_FIXTURE_SHA256:
            raise ComparisonFailure("baseline fixture raw SHA-256 mismatch")
        fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
        required_fields = set(fixture["trace_fields_every_physics_tick"])
        tolerance = float(fixture["comparison"]["tolerances"]["all_scalar_and_vector_components_absolute"])
        if not math.isfinite(tolerance) or tolerance < 0.0:
            raise ComparisonFailure("invalid comparison tolerance")
        project_root = Path(__file__).resolve().parents[1]
        for relative, expected in EXPECTED_FILES.items():
            candidate = project_root / relative
            if not candidate.is_file() or sha256(candidate) != expected:
                raise ComparisonFailure(f"frozen/authorized file mismatch: {relative}")
        baseline_records, selected_records = load_jsonl(baseline_path), load_jsonl(selected_path)
        if len(baseline_records) != EXPECTED_TICKS or len(selected_records) != EXPECTED_TICKS:
            raise ComparisonFailure(
                f"line count mismatch: baseline={len(baseline_records)}, selected={len(selected_records)}, expected={EXPECTED_TICKS}"
            )
        maximum_difference = 0.0
        for tick, (baseline_record, selected_record) in enumerate(zip(baseline_records, selected_records)):
            if set(baseline_record) != required_fields or set(selected_record) != required_fields:
                raise ComparisonFailure(f"tick {tick}: exact trace field set mismatch")
            if baseline_record.get("physics_tick") != tick or selected_record.get("physics_tick") != tick:
                raise ComparisonFailure(f"tick {tick}: physics_tick alignment mismatch")
            for field in sorted(required_fields):
                maximum_difference = max(
                    maximum_difference,
                    compare_value(baseline_record[field], selected_record[field], f"tick {tick}.{field}", tolerance),
                )
        result = {
            "authorized_file_count": len(EXPECTED_FILES),
            "maximum_absolute_difference": maximum_difference,
            "raw_trace_bytes_equal": baseline_path.read_bytes() == selected_path.read_bytes(),
            "schema": "district_zero.p1a.vehicle_r7.c1_result.v1",
            "status": "PASS",
            "ticks_compared": EXPECTED_TICKS,
            "tolerance": tolerance,
        }
        print(json.dumps(result, sort_keys=True))
        return 0
    except (ComparisonFailure, OSError, KeyError, ValueError, json.JSONDecodeError) as error:
        print(json.dumps({"error": str(error), "status": "FAIL"}, sort_keys=True), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
