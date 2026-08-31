#!/usr/bin/env python3
"""Verify the R7 vehicle transplant against immutable R6 and transfer roots."""
from __future__ import annotations

import difflib
import hashlib
import json
from pathlib import Path
import re
import sys


MODIFIED = {
    "AGENTS.md",
    "STATUS.md",
    "project.godot",
    "scenes/craft.tscn",
    "scenes/district_zero_p1a.tscn",
    "scripts/craft_controller.gd",
    "scripts/p1a_world_gate.gd",
}
REMOVED = {"PLAY_DISTRICT_ZERO_TERRAIN_POLISH_R6.command", "TERRAIN_POLISH_R6_SHA256SUMS.txt"}
ADDED = {
    "P1A_POST_V1_2_8_VEHICLE_INTEGRATION_R7_AUTHORITY.md",
    "PLAY_DISTRICT_ZERO_VEHICLE_R7.command",
    "R6_BASELINE_SHA256SUMS.txt",
    "README_VEHICLE_INTEGRATION_R7.md",
    "VEHICLE_INTEGRATION_R7_EXECUTION_REPORT.md",
    "scenes/vehicle_visual.tscn",
    "scripts/vehicle_visual_rig.gd",
    "scripts/vehicle_visual_rig.gd.uid",
    "tests/p1a_vehicle_r7_runner.gd",
    "tests/p1a_vehicle_r7_pose_probe.gd",
    "tests/p1a_vehicle_r7_ui_probe.gd",
    "tools/compare_vehicle_r7_c1.py",
    "tools/validate_vehicle_r7.gd",
    "tools/validate_vehicle_r7.gd.uid",
    "tools/verify_vehicle_r7.py",
}
FORBIDDEN_PARTS = {".godot", "__pycache__", "__MACOSX"}
EXPECTED_TRANSFER_HASHES = {
    "scenes/craft.tscn": "f6380bddd74692b1658bc77313231cf1ff49ea6e0400f9dbfe4d45c0dbd68877",
    "scenes/vehicle_visual.tscn": "21efabf4d66a33b446687dbcd485f764b38897fb8cf44f72a7c7db4591b3bdc9",
    "scripts/craft_controller.gd": "c87d7fefa2c5c8489ab31508992293a81e31fa7a7efd8e1fc17aac2f74d41e6b",
    "scripts/vehicle_visual_rig.gd": "7f798341f24cd103bd8b58f6baee58f6612dd532c4bf7f24ddf751d47d7016c3",
}
EXPECTED_DIFF_HASHES = {
    "scenes/craft.tscn": "2c6c6d2ffe5b949fd77dfea3479a8c3fdb6caddc55937d6837d67de8feb84bd8",
    "scripts/craft_controller.gd": "c9c2f45d93687352c54a7e914891975f8553f897db46307a9a6d895a6f745f38",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def files(root: Path, inventory_name: str | None = None) -> set[str]:
    result = set()
    for path in root.rglob("*"):
        if not path.is_file() or (inventory_name is not None and path == root / inventory_name):
            continue
        relative = path.relative_to(root)
        if any(part in FORBIDDEN_PARTS for part in relative.parts):
            continue
        if path.name == ".DS_Store" or path.name.startswith("._") or path.suffix in {".pyc", ".pyo"}:
            continue
        result.add(relative.as_posix())
    return result


def verify_inventory(root: Path, name: str, prefix: str = "") -> tuple[int, list[str]]:
    errors = []
    rows = (root / name).read_text(encoding="utf-8").splitlines()
    for row in rows:
        match = re.fullmatch(r"([0-9a-f]{64})  (?:\./)?(.+)", row)
        if not match:
            errors.append(f"{prefix}malformed row")
            continue
        expected, relative = match.groups()
        target = root / relative
        if not target.is_file() or sha(target) != expected:
            errors.append(f"{prefix}checksum mismatch: {relative}")
    return len(rows), errors


def diff_hash(baseline: Path, current: Path, relative: str) -> str:
    left = (baseline / relative).read_text(encoding="utf-8").splitlines(keepends=True)
    right = (current / relative).read_text(encoding="utf-8").splitlines(keepends=True)
    delta = "".join(difflib.unified_diff(left, right, fromfile=relative, tofile=relative))
    return hashlib.sha256(delta.encode()).hexdigest()


def normalized_identity(relative: str, text: str) -> str:
    replacements = {
        "project.godot": [("District Zero P1A — Vehicle Integration R7 Owner Review", "District Zero P1A — Terrain Polish R6 Owner Review")],
        "scenes/district_zero_p1a.tscn": [
            ("P1A VEHICLE INTEGRATION R7 · OWNER REVIEW", "P1A TERRAIN POLISH R6 · OWNER REVIEW"),
            ("DISTRICT ZERO · P1A VEHICLE R7 · WORLD v1.2.3", "DISTRICT ZERO · P1A TERRAIN POLISH R6 · WORLD v1.2.3"),
        ],
        "scripts/p1a_world_gate.gd": [
            ("DISTRICT ZERO · P1A VEHICLE R7 · WORLD v1.2.3", "DISTRICT ZERO · P1A TERRAIN POLISH R6 · WORLD v1.2.3"),
            ("P1A VEHICLE INTEGRATION R7 · OWNER REVIEW", "P1A TERRAIN POLISH R6 · OWNER REVIEW"),
        ],
    }
    for current, baseline in replacements.get(relative, []):
        if text.count(current) != 1:
            raise ValueError(f"identity anchor mismatch: {relative}: {current}")
        text = text.replace(current, baseline)
    return text


def main(argv: list[str]) -> int:
    if len(argv) != 4:
        print("usage: verify_vehicle_r7.py R6_ROOT TRANSFER_ROOT R7_ROOT", file=sys.stderr)
        return 2
    r6, transfer, r7 = (Path(value).resolve() for value in argv[1:])
    errors: list[str] = []
    try:
        r6_count, r6_errors = verify_inventory(r6, "TERRAIN_POLISH_R6_SHA256SUMS.txt", "R6 ")
        transfer_count, transfer_errors = verify_inventory(transfer, "TRANSFER_SHA256SUMS.txt", "transfer ")
        errors.extend(r6_errors + transfer_errors)
        if r6_count != 220:
            errors.append(f"R6 inventory count {r6_count} != 220")
        if transfer_count != 33:
            errors.append(f"transfer inventory count {transfer_count} != 33")
        r6_files, r7_files = files(r6), files(r7)
        expected_r7 = (r6_files - REMOVED) | ADDED
        missing, unexpected = sorted(expected_r7 - r7_files), sorted(r7_files - expected_r7)
        if missing:
            errors.append(f"missing paths: {missing}")
        if unexpected:
            errors.append(f"unexpected paths: {unexpected}")
        for relative in sorted(r6_files - MODIFIED - REMOVED):
            if sha(r6 / relative) != sha(r7 / relative):
                errors.append(f"undeclared R6 byte delta: {relative}")
        if (r7 / "R6_BASELINE_SHA256SUMS.txt").read_bytes() != (r6 / "TERRAIN_POLISH_R6_SHA256SUMS.txt").read_bytes():
            errors.append("renamed R6 baseline inventory bytes differ")
        for relative, expected in EXPECTED_TRANSFER_HASHES.items():
            if sha(r7 / relative) != expected or (r7 / relative).read_bytes() != (transfer / relative).read_bytes():
                errors.append(f"transfer byte identity mismatch: {relative}")
        for relative, expected in EXPECTED_DIFF_HASHES.items():
            if diff_hash(r6, r7, relative) != expected:
                errors.append(f"authorized R6 delta mismatch: {relative}")
        for relative in ("project.godot", "scenes/district_zero_p1a.tscn", "scripts/p1a_world_gate.gd"):
            normalized = normalized_identity(relative, (r7 / relative).read_text(encoding="utf-8"))
            if normalized.encode() != (r6 / relative).read_bytes():
                errors.append(f"non-identity delta in {relative}")
        result = {
            "authorized_controller_diff_sha256": diff_hash(r6, r7, "scripts/craft_controller.gd"),
            "authorized_craft_scene_diff_sha256": diff_hash(r6, r7, "scenes/craft.tscn"),
            "r6_inventory_records": r6_count,
            "schema": "district_zero.p1a.vehicle_integration_r7.preservation.v1",
            "status": "PASS" if not errors else "FAIL",
            "transfer_inventory_records": transfer_count,
            "unchanged_r6_paths": len(r6_files - MODIFIED - REMOVED),
            "violations": errors,
        }
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0 if not errors else 1
    except (OSError, ValueError) as error:
        print(json.dumps({"error": str(error), "status": "FAIL"}, sort_keys=True), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
