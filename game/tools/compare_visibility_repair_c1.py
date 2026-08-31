#!/usr/bin/env python3
"""Compare visibility-repair C1 traces without weakening movement freezes.

The inherited comparator intentionally rejects any camera-rig byte change before
reading traces.  The owner-authorized visibility repair changes that script, so
this successor comparator binds the exact replacement camera, builder, and
authority hashes while retaining every inherited movement/tuning freeze and the
unchanged 1,260-tick fixture contract.
"""

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


AUTHORIZED_REPLACEMENTS = {
    "P1A_POST_V1_2_8_VISIBILITY_REPAIR_AUTHORITY.md": "c65accd8dff700ab1aace9b1c4266c5847c561c9294a6c51f35ee46da8c162b8",
    "P1A_POST_V1_2_8_VISIBILITY_REPAIR_R2_AUTHORITY.md": "305dd38ea1c89596218b609c7db4465267d10c0484d4637c2e3b618f39c45c3e",
    "P1A_POST_V1_2_8_VISIBILITY_REPAIR_R3_AUTHORITY.md": "ae9fb90740654419b4da65389670a7245486cb872e0ee0dbd2c515051dc75936",
    "scenes/district_zero_p1a.tscn": "b35f802f15b3f3a7e310d6ab0d753ddeca565e83cd95937d40dc1d6d7e83cbb8",
    "scripts/camera_rig.gd": "8d4ae9565d868f1d531e3c8e22d0e6214f52ea738fb724e2116ba263cd21eebb",
    "scripts/p1a_world_builder.gd": "a45815d865182eb4f69ddc54e8a510d84906b714ed8e64f6c8fcbba960d1c671",
    "scripts/p1a_world_gate.gd": "9ea6475292b7de7a2a6908933230bcc6736ce8e5dc5b6de4eb5dd66fb23756c7",
}


def main(argv: list[str]) -> int:
    if len(argv) != 4:
        print("usage: compare_visibility_repair_c1.py BASE_TRACE SELECTED_TRACE FIXTURE", file=sys.stderr)
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
        frozen.update(AUTHORIZED_REPLACEMENTS)
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
        print(json.dumps({
            "authorized_replacement_count": len(AUTHORIZED_REPLACEMENTS),
            "frozen_file_count": len(frozen),
            "maximum_absolute_difference": maximum_difference,
            "raw_trace_bytes_equal": baseline_path.read_bytes() == selected_path.read_bytes(),
            "schema": "district_zero.p1a.visibility_repair_r3_c1_result.v1",
            "status": "PASS",
            "ticks_compared": EXPECTED_TICKS,
            "tolerance": tolerance,
        }, sort_keys=True))
        return 0
    except (ComparisonFailure, OSError, KeyError, ValueError, json.JSONDecodeError) as error:
        print(json.dumps({"error": str(error), "status": "FAIL"}, sort_keys=True), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
