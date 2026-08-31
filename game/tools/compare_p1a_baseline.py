#!/usr/bin/env python3
"""Compare the exact District Zero P1A same-host baseline traces."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
import sys
from typing import Any


EXPECTED_FIXTURE_SHA256 = "0b5147dc5448f987a3e8d68b597501687347bd4f7049e676ad42e48849080770"
EXPECTED_TICKS = 1260
FROZEN_FILES = {
    "resources/default_tuning.tres": "a6d7a6ef66f28a480bc28096c91124e5c93f9b8e7dd32c68296030ce21800459",
    "scenes/craft.tscn": "2ccf2f2e9007eeb63a52091a771c840aabb5b1cf9a176f5f6e21d3c84cab8502",
    "scripts/camera_rig.gd": "91cf26e9510734580d0424533f1c3bb0b0104f2b490a337f6f57a0c14e9fb67e",
    "scripts/craft_controller.gd": "fd2e6e676bf828382fda4dee7eaf37fde0c00a326ef1d5ca56d1cfaaa15e1b5d",
    "scripts/craft_tuning.gd": "c6b82758d7d985d0a16d16a7265a52e2ba2b5a4ec2e608a08ef1d2fa7650acfd",
    "scripts/motion_math.gd": "c2ceb0ab0f5bcff7d6a4cf7c2b6e3c7fa1c70b96edee206d00b529d3329ed575",
    "scripts/surface_feedback_3d.gd": "8db47e1ba550efc3c0bfa871edae2a74ab103d7720ed8284add75057eaa4bda6",
}


class ComparisonFailure(Exception):
    pass


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8", newline="") as handle:
        for line_number, line in enumerate(handle, 1):
            if not line.endswith("\n"):
                raise ComparisonFailure(f"{path}: line {line_number} lacks LF terminator")
            value = json.loads(line)
            if not isinstance(value, dict):
                raise ComparisonFailure(f"{path}: line {line_number} is not an object")
            records.append(value)
    return records


def compare_value(expected: Any, actual: Any, location: str, tolerance: float) -> float:
    if isinstance(expected, bool) or isinstance(actual, bool):
        if type(expected) is not type(actual) or expected != actual:
            raise ComparisonFailure(f"{location}: boolean mismatch {expected!r} != {actual!r}")
        return 0.0
    if isinstance(expected, int) or isinstance(actual, int):
        if type(expected) is not int or type(actual) is not int or expected != actual:
            raise ComparisonFailure(f"{location}: integer mismatch {expected!r} != {actual!r}")
        return 0.0
    if isinstance(expected, float) or isinstance(actual, float):
        if not isinstance(expected, (int, float)) or not isinstance(actual, (int, float)):
            raise ComparisonFailure(f"{location}: numeric type mismatch")
        expected_float = float(expected)
        actual_float = float(actual)
        if not math.isfinite(expected_float) or not math.isfinite(actual_float):
            raise ComparisonFailure(f"{location}: non-finite numeric value")
        difference = abs(expected_float - actual_float)
        if difference > tolerance:
            raise ComparisonFailure(
                f"{location}: |{expected_float!r} - {actual_float!r}| = {difference!r} > {tolerance}"
            )
        return difference
    if isinstance(expected, list) or isinstance(actual, list):
        if not isinstance(expected, list) or not isinstance(actual, list) or len(expected) != len(actual):
            raise ComparisonFailure(f"{location}: array shape mismatch")
        maximum = 0.0
        for index, (expected_item, actual_item) in enumerate(zip(expected, actual)):
            maximum = max(maximum, compare_value(expected_item, actual_item, f"{location}[{index}]", tolerance))
        return maximum
    if expected != actual:
        raise ComparisonFailure(f"{location}: value mismatch {expected!r} != {actual!r}")
    return 0.0


def main(argv: list[str]) -> int:
    if len(argv) != 4:
        print("usage: compare_p1a_baseline.py P0_TRACE_JSONL P1A_TRACE_JSONL FIXTURE_JSON", file=sys.stderr)
        return 2
    p0_trace_path, p1a_trace_path, fixture_path = map(Path, argv[1:])
    try:
        if sha256(fixture_path) != EXPECTED_FIXTURE_SHA256:
            raise ComparisonFailure("baseline fixture raw SHA-256 mismatch")
        fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
        required_fields = set(fixture["trace_fields_every_physics_tick"])
        tolerance = float(fixture["comparison"]["tolerances"]["all_scalar_and_vector_components_absolute"])
        project_root = Path(__file__).resolve().parents[1]
        for relative_path, expected_hash in FROZEN_FILES.items():
            candidate = project_root / relative_path
            if not candidate.is_file() or sha256(candidate) != expected_hash:
                raise ComparisonFailure(f"frozen file mismatch: {relative_path}")
        p0_records = load_jsonl(p0_trace_path)
        p1a_records = load_jsonl(p1a_trace_path)
        if len(p0_records) != EXPECTED_TICKS or len(p1a_records) != EXPECTED_TICKS:
            raise ComparisonFailure(
                f"line count mismatch: P0={len(p0_records)}, P1A={len(p1a_records)}, expected={EXPECTED_TICKS}"
            )
        maximum_difference = 0.0
        for tick, (p0_record, p1a_record) in enumerate(zip(p0_records, p1a_records)):
            if set(p0_record) != required_fields or set(p1a_record) != required_fields:
                raise ComparisonFailure(f"tick {tick}: exact trace field set mismatch")
            if p0_record.get("physics_tick") != tick or p1a_record.get("physics_tick") != tick:
                raise ComparisonFailure(f"tick {tick}: physics_tick alignment mismatch")
            for field_name in sorted(required_fields):
                maximum_difference = max(
                    maximum_difference,
                    compare_value(p0_record[field_name], p1a_record[field_name], f"tick {tick}.{field_name}", tolerance),
                )
        print(
            json.dumps(
                {
                    "frozen_file_count": len(FROZEN_FILES),
                    "maximum_absolute_difference": maximum_difference,
                    "status": "PASS",
                    "ticks_compared": EXPECTED_TICKS,
                    "tolerance": tolerance,
                },
                sort_keys=True,
            )
        )
        return 0
    except (ComparisonFailure, OSError, KeyError, ValueError, json.JSONDecodeError) as error:
        print(json.dumps({"error": str(error), "status": "FAIL"}, sort_keys=True), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
