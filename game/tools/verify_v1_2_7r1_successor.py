#!/usr/bin/env python3
"""Strengthened static/preservation verifier for the v1.2.7R1 harness repair."""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
import pathlib
import re
import subprocess
import sys
from typing import Any

from p1a_v1_2_7r1_harness import (
    EXACT_ENGINE,
    expected_builder_from_selected,
    sha256,
    verify_inventory,
)

INPUT_INVENTORY_SHA256 = "b943b4c6c6b3a0a5166a3c8431582628e71b1b2421619220dd8b9b94bbd5d8fe"
SOURCE_TRANSPORT_SHA256 = "e59647e98f119405614718c5c20193dec25565ca2b186c25e083edbfd282bac8"
EVIDENCE_TRANSPORT_SHA256 = "13b024c56932e0b83b858ca6453b66dbd84b28b556ebcb38611ddc8d30277437"

MUTABLE_INPUT_PATHS = {
    "AGENTS.md",
    "README.md",
    "README_FIRST.md",
    "STATUS.md",
    "P1A_ACTIVE_AUTHORITY_CHAIN.json",
    "P1A_CODEX_SENDOFF.md",
    "PACKET_SHA256SUMS.txt",
    "scripts/p1a_world_builder.gd",
    "tests/fixtures/v1_2_7_candidate_evidence.schema.json",
    "tests/fixtures/v1_2_7_final_evidence_contract.json",
}

ADDED_PATHS = {
    "P1A_V1_2_7R1_HARNESS_REPAIR_AUTHORITY.md",
    "V1_2_7_INPUT_SHA256SUMS.txt",
    "evidence/v1_2_7r1_harness_repair_manifest.json",
    "presentation/p1a_v1_2_7r1_selected_presentation.json",
    "tests/fixtures/v1_2_7r1_harness_repair_contract.json",
    "tools/launch_a1_capture_v1_2_7r1.py",
    "tools/p1a_v1_2_7r1_harness.py",
    "tools/prepare_v1_2_7r1_a1_session.py",
    "tools/run_v1_2_7r1_calibration.py",
    "tools/run_v1_2_7r1_c1.py",
    "tools/test_v1_2_7r1_repairs.py",
    "tools/verify_v1_2_7r1_successor.py",
}


def load(path: pathlib.Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def input_records(path: pathlib.Path) -> tuple[dict[str, str], list[str]]:
    records: dict[str, str] = {}
    errors: list[str] = []
    if not path.is_file() or sha256(path) != INPUT_INVENTORY_SHA256:
        return {}, ["preserved v1.2.7 input inventory identity mismatch"]
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        match = re.fullmatch(r"([0-9a-f]{64})  (.+)", line)
        if not match:
            errors.append(f"malformed input inventory row {number}")
            continue
        digest, relative = match.groups()
        if relative in records:
            errors.append(f"duplicate input path {relative}")
        records[relative] = digest
    if len(records) != 2187:
        errors.append(f"input inventory record count {len(records)} != 2187")
    return records, errors


def substantive_paths(root: pathlib.Path) -> set[str]:
    output: set[str] = set()
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        relative = path.relative_to(root)
        if any(part in {".godot", "__pycache__", ".pytest_cache", ".mypy_cache"} for part in relative.parts):
            continue
        if path.name == ".DS_Store" or path.name.startswith("._") or path.name.endswith((".pyc", ".pyo")):
            continue
        output.add(relative.as_posix())
    return output


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True)
    parser.add_argument("--phase", choices=("repair", "final"), default="repair")
    args = parser.parse_args()
    root = pathlib.Path(args.root).resolve()
    errors: list[str] = []
    counts: dict[str, Any] = {}

    def check(condition: bool, message: str) -> None:
        if not condition:
            errors.append(message)

    records, record_errors = input_records(root / "V1_2_7_INPUT_SHA256SUMS.txt")
    errors.extend(record_errors)
    counts["v1_2_7_input_records"] = len(records)
    frozen = {path: digest for path, digest in records.items() if path not in MUTABLE_INPUT_PATHS}
    changed = [path for path, digest in frozen.items() if not (root / path).is_file() or sha256(root / path) != digest]
    check(not changed, f"frozen v1.2.7 input bytes changed: {changed[:10]}")
    counts["strict_frozen_v1_2_7_files"] = len(frozen)

    actual = substantive_paths(root)
    input_paths = set(records) | {"PACKET_SHA256SUMS.txt"}
    additions = actual - input_paths
    allowed_additions = set(ADDED_PATHS)
    if args.phase == "repair":
        allowed_additions.discard("presentation/p1a_v1_2_7r1_selected_presentation.json")
    check(additions <= allowed_additions, f"unauthorized added paths: {sorted(additions-allowed_additions)[:10]}")
    check((allowed_additions & actual) == allowed_additions, f"required R1 paths absent: {sorted(allowed_additions-actual)[:10]}")

    baseline_path = root / "tests/fixtures/v1_2_7_v1_2_6_world_builder.gd"
    builder_path = root / "scripts/p1a_world_builder.gd"
    baseline = baseline_path.read_text(encoding="utf-8")
    current = builder_path.read_text(encoding="utf-8")
    check(sha256(baseline_path) == "c016d5e2654919d6de5e1416ab21a40da81149ec11100dae8d95a89922b9dc38", "frozen builder fixture identity mismatch")
    registry = load(root / "tests/fixtures/v1_2_7_calibration_registry.json")
    if args.phase == "repair":
        check(current == baseline, "repair-phase source preselects presentation values")
    else:
        selected_path = root / "presentation/p1a_v1_2_7r1_selected_presentation.json"
        check(selected_path.is_file(), "selected presentation record absent")
        if selected_path.is_file():
            selected = load(selected_path)
            expected, selected_errors = expected_builder_from_selected(baseline, selected, registry)
            errors.extend(selected_errors)
            check(expected is not None and current == expected, "material source differs from exact selected canonical bytes")
            check(selected.get("source_material_file_sha256") == sha256(builder_path), "selected source hash differs from actual builder")

    chain = load(root / "P1A_ACTIVE_AUTHORITY_CHAIN.json")
    status = (root / "STATUS.md").read_text(encoding="utf-8")
    check(chain.get("active_director_authority") == "v1.2.7R1", "active authority is not v1.2.7R1")
    check(chain.get("repair_overlay_authority") == "P1A_V1_2_7R1_HARNESS_REPAIR_AUTHORITY.md", "repair authority binding absent")
    check(chain.get("operative_calibration_runner") == "tools/run_v1_2_7r1_calibration.py", "operative R1 runner binding wrong")
    check(chain.get("operative_c1_runner") == "tools/run_v1_2_7r1_c1.py", "operative R1 C1 runner binding wrong")
    check(chain.get("operative_verifier") == "tools/verify_v1_2_7r1_successor.py", "operative R1 verifier binding wrong")
    check(chain.get("world_data_authority") == "v1.2.3", "world authority changed")
    check(chain.get("presentation_baseline_authority") == "v1.2.6", "presentation baseline changed")
    check(chain.get("capture_replay_semantics_authority") == "v1.2.5", "capture semantics changed")
    check(chain.get("all_original_visual_thresholds") == "FROZEN", "visual thresholds not frozen")
    check(registry.get("absolute_candidate_engine_launch_cap") == 82, "candidate render cap changed")
    check(registry.get("exact_engine") == EXACT_ENGINE, "registry engine changed")
    if args.phase == "repair":
        check("**Outcome:** `READY FOR CODEX — v1.2.7R1 PREFLIGHT REQUIRED`" in status, "repair status wrong")

    evidence_zip = root / "director_inputs/District-Zero-P1A-v1.2.6-Run-1-Validation-Evidence.transport.zip"
    check(evidence_zip.is_file() and sha256(evidence_zip) == EVIDENCE_TRANSPORT_SHA256, "retained Run-1 evidence transport mismatch")
    retained = root / "director_inputs/v1_2_6_run1_validation_evidence"
    retained_errors = verify_inventory(retained, "SHA256SUMS.txt")
    check(not retained_errors, f"retained Run-1 evidence inventory failed: {retained_errors[:3]}")
    counts["run1_substantive_records"] = 72 if not retained_errors else None

    python_bad: list[str] = []
    for path in root.rglob("*.py"):
        if "__pycache__" in path.parts:
            continue
        try:
            ast.parse(path.read_text(encoding="utf-8"))
        except Exception as exc:
            python_bad.append(f"{path.relative_to(root)}:{exc}")
    check(not python_bad, f"Python parse errors: {python_bad[:5]}")
    counts["python_files"] = len([path for path in root.rglob("*.py") if "__pycache__" not in path.parts])
    json_bad: list[str] = []
    for path in root.rglob("*.json"):
        try:
            load(path)
        except Exception as exc:
            json_bad.append(f"{path.relative_to(root)}:{exc}")
    check(not json_bad, f"JSON parse errors: {json_bad[:5]}")
    counts["json_files"] = len(list(root.rglob("*.json")))

    semantic_command = [sys.executable, "-B", str(root / "tools/test_v1_2_7r1_repairs.py"), "--root", str(root), "--static-only"]
    semantic = subprocess.run(semantic_command, cwd=root, capture_output=True, text=True, check=False)
    try:
        semantic_result = json.loads(semantic.stdout)
    except Exception:
        semantic_result = {}
    check(semantic.returncode == 0 and semantic_result.get("status") == "PASS", "R1 semantic/static repairs failed")
    counts["r1_semantic_cases"] = semantic_result.get("case_count")

    packet_errors = verify_inventory(root, "PACKET_SHA256SUMS.txt")
    check(not packet_errors, f"R1 packet inventory failed: {packet_errors[:3]}")
    counts["packet_records"] = len((root / "PACKET_SHA256SUMS.txt").read_text(encoding="utf-8").splitlines()) if (root / "PACKET_SHA256SUMS.txt").is_file() else 0
    result = {
        "schema": "district_zero.p1a.v1_2_7r1.successor_static_verifier_result.v1",
        "status": "PASS" if not errors else "FAIL",
        "phase": args.phase,
        "error_count": len(errors),
        "errors": errors,
        "counts": counts,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
