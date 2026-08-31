#!/usr/bin/env python3
"""C1 comparator for the owner-authorized presentation-only Polish R5 successor."""
from __future__ import annotations

import json
import math
from pathlib import Path
import sys

from compare_p1a_baseline import (
    ComparisonFailure,
    EXPECTED_FIXTURE_SHA256,
    EXPECTED_TICKS,
    FROZEN_FILES,
    compare_value,
    load_jsonl,
    sha256,
)


AUTHORIZED_PRESENTATION_FILES = {
    "P1A_POST_V1_2_8_POLISH_R5_AUTHORITY.md": "867ef0a6716a0a93ead196a671dedb96c9f06ab0cfef2b9a72219440b4c64766",
    "project.godot": "a1212fd727bb61589b5f39968a898ffb82fe96e6bcb097edc3891011fb04de88",
    "scenes/district_zero_p1a.tscn": "39d7454e22d24685f997869909616bc99789676f8ce5f59c1c9b136b902fde10",
    "scripts/camera_rig.gd": "8d4ae9565d868f1d531e3c8e22d0e6214f52ea738fb724e2116ba263cd21eebb",
    "scripts/p1a_map.gd": "04962dedc18f5df47a8fac90465004fdc18668e93fbf2e2715011a398f1b9ff4",
    "scripts/p1a_world_builder.gd": "117557ab310e5ca73c821c771915acf722d45905a3de4ac2343dff2e35aec34c",
    "scripts/p1a_world_gate.gd": "8da41cf26b5135f4550677d1e0b9b31ca9506764d5d025e1736ba5ffb3a5215a",
}


def main(argv: list[str]) -> int:
    if len(argv) != 4:
        print("usage: compare_polish_r5_c1.py BASE_TRACE SELECTED_TRACE FIXTURE", file=sys.stderr)
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
        frozen = dict(FROZEN_FILES)
        frozen.pop("scripts/camera_rig.gd")
        frozen.update(AUTHORIZED_PRESENTATION_FILES)
        for relative_path, expected_hash in frozen.items():
            candidate = project_root / relative_path
            if not candidate.is_file() or sha256(candidate) != expected_hash:
                raise ComparisonFailure(f"frozen/authorized file mismatch: {relative_path}")
        baseline_records = load_jsonl(baseline_path)
        selected_records = load_jsonl(selected_path)
        if len(baseline_records) != EXPECTED_TICKS or len(selected_records) != EXPECTED_TICKS:
            raise ComparisonFailure(
                f"line count mismatch: baseline={len(baseline_records)}, "
                f"selected={len(selected_records)}, expected={EXPECTED_TICKS}"
            )
        maximum_difference = 0.0
        for tick, (baseline_record, selected_record) in enumerate(zip(baseline_records, selected_records)):
            if set(baseline_record) != required_fields or set(selected_record) != required_fields:
                raise ComparisonFailure(f"tick {tick}: exact trace field set mismatch")
            if baseline_record.get("physics_tick") != tick or selected_record.get("physics_tick") != tick:
                raise ComparisonFailure(f"tick {tick}: physics_tick alignment mismatch")
            for field_name in sorted(required_fields):
                maximum_difference = max(
                    maximum_difference,
                    compare_value(
                        baseline_record[field_name],
                        selected_record[field_name],
                        f"tick {tick}.{field_name}",
                        tolerance,
                    ),
                )
        result = {
            "authorized_presentation_file_count": len(AUTHORIZED_PRESENTATION_FILES),
            "frozen_file_count": len(frozen),
            "maximum_absolute_difference": maximum_difference,
            "raw_trace_bytes_equal": baseline_path.read_bytes() == selected_path.read_bytes(),
            "schema": "district_zero.p1a.polish_r5.c1_result.v1",
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
