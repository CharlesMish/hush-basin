#!/usr/bin/env python3
"""Verify the narrow Polish R5 delta against the checksum-clean R4 player."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys


ALLOWED_EXACT = {
    "AGENTS.md",
    "P1A_POST_V1_2_8_POLISH_R5_AUTHORITY.md",
    "POLISH_R5_EXECUTION_REPORT.md",
    "POLISH_R5_SHA256SUMS.txt",
    "PLAY_DISTRICT_ZERO_R4.command",
    "PLAY_DISTRICT_ZERO_POLISH_R5.command",
    "PLAY_PROJECT_SHA256SUMS.txt",
    "R4_BASELINE_PLAY_PROJECT_SHA256SUMS.txt",
    "README_POLISH_R5.md",
    "STATUS.md",
    "project.godot",
    "scenes/district_zero_p1a.tscn",
    "scripts/p1a_map.gd",
    "scripts/p1a_world_builder.gd",
    "scripts/p1a_world_gate.gd",
}
ALLOWED_PREFIXES = (
    "tests/p1a_polish_",
    "tools/compare_polish_r5_c1.py",
    "tools/verify_polish_r5.py",
)
EXCLUDED_PARTS = {".godot", "__pycache__", ".pytest_cache", ".mypy_cache"}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def substantive_tree(root: Path) -> dict[str, str]:
    records: dict[str, str] = {}
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        relative = path.relative_to(root)
        if any(part in EXCLUDED_PARTS for part in relative.parts):
            continue
        if path.name == ".DS_Store" or path.name.startswith("._") or path.suffix in {".pyc", ".pyo"}:
            continue
        records[relative.as_posix()] = sha256(path)
    return records


def load_inventory(path: Path) -> dict[str, str]:
    records: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        digest, relative = line.split("  ", 1)
        records[relative] = digest
    return records


def node_block(text: str, name: str) -> str:
    pattern = re.compile(rf'^\[node name="{re.escape(name)}"(?:.|\n)*?(?=^\[node |\Z)', re.MULTILINE)
    match = pattern.search(text)
    if match is None:
        raise ValueError(f"scene node absent: {name}")
    return match.group(0)


def json_file(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def extract_prefixed_json(path: Path, prefix: str) -> dict:
    for line in reversed(path.read_text(encoding="utf-8").splitlines()):
        if line.startswith(prefix):
            return json.loads(line[len(prefix):])
    raise ValueError(f"result prefix absent: {prefix}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True)
    parser.add_argument("--baseline", required=True)
    parser.add_argument("--evidence", required=True)
    args = parser.parse_args()
    root = Path(args.root).resolve()
    baseline = Path(args.baseline).resolve()
    evidence = Path(args.evidence).resolve()
    errors: list[str] = []

    inventory_path = baseline / "PLAY_PROJECT_SHA256SUMS.txt"
    inventory = load_inventory(inventory_path)
    inventory_failures = [relative for relative, digest in inventory.items() if not (baseline / relative).is_file() or sha256(baseline / relative) != digest]
    if len(inventory) != 2247 or inventory_failures:
        errors.append(f"R4 inventory mismatch: records={len(inventory)} failures={inventory_failures[:5]}")

    base_tree = substantive_tree(baseline)
    root_tree = substantive_tree(root)
    changed = sorted(path for path in set(base_tree) | set(root_tree) if base_tree.get(path) != root_tree.get(path))
    unauthorized = [path for path in changed if path not in ALLOWED_EXACT and not path.startswith(ALLOWED_PREFIXES)]
    if unauthorized:
        errors.append(f"unauthorized substantive paths changed: {unauthorized}")

    baseline_builder = (baseline / "scripts/p1a_world_builder.gd").read_text(encoding="utf-8")
    current_builder = (root / "scripts/p1a_world_builder.gd").read_text(encoding="utf-8")
    marker_anchor = "func _build_node_markers"
    after_anchor = "func _solid_color"
    if baseline_builder.split(marker_anchor, 1)[0] != current_builder.split(marker_anchor, 1)[0]:
        errors.append("world-builder bytes before node-marker function changed")
    if baseline_builder.split(after_anchor, 1)[1] != current_builder.split(after_anchor, 1)[1]:
        errors.append("world-builder bytes after node-marker region changed")

    baseline_scene = (baseline / "scenes/district_zero_p1a.tscn").read_text(encoding="utf-8")
    current_scene = (root / "scenes/district_zero_p1a.tscn").read_text(encoding="utf-8")
    for node_name in ("Sun", "Craft", "SurfaceFeedback", "Telemetry", "CameraRig", "Camera"):
        try:
            if node_block(baseline_scene, node_name) != node_block(current_scene, node_name):
                errors.append(f"protected scene node changed: {node_name}")
        except ValueError as error:
            errors.append(str(error))

    try:
        metric = json_file(evidence / "POST_POLISH/NATIVE_VISUALS/metric_result.json")
        if metric.get("status") != "PASS" or len(metric.get("checks", [])) != 21 or not all(check.get("pass") for check in metric.get("checks", [])):
            errors.append("native visual metrics are not 21/21 PASS")
        probe = json_file(evidence / "POST_POLISH/NATIVE_VISUALS/probe_result.json")
        rays = probe.get("ray_result", {})
        if probe.get("status") != "PASS" or rays.get("sample_count") != 14 or rays.get("mismatch_count") != 0:
            errors.append("frozen ray classification is not 14/14 PASS")
        sweep = json_file(evidence / "POST_POLISH/NATIVE_SWEEP/probe_result.json")
        records = sweep.get("records", [])
        if sweep.get("status") != "PASS" or len(records) != 14 or any(float(record.get("camera_pull_in_m", 1.0)) != 0.0 for record in records):
            errors.append("registered-start sweep is not 14/14 with zero pull-in")
        ui = json_file(evidence / "POST_POLISH/UI/ui_probe_result.json")
        if ui.get("status") != "PASS" or len(ui.get("captures", {})) != 3:
            errors.append("UI capture contract did not pass")
        behavior = extract_prefixed_json(evidence / "POST_POLISH/R5_BEHAVIOR.stdout.txt", "P1A_POLISH_R5_RESULT ")
        if behavior.get("status") != "PASS" or behavior.get("failure_count") != 0 or len(behavior.get("checks", [])) != 19:
            errors.append("R5 behavior suite is not 19/19 PASS")
        c1 = json.loads((evidence / "POST_POLISH/C1/POLISH_R5_COMPARE.stdout.txt").read_text(encoding="utf-8"))
        if c1.get("status") != "PASS" or c1.get("ticks_compared") != 1260 or c1.get("maximum_absolute_difference") != 0.0 or c1.get("raw_trace_bytes_equal") is not True:
            errors.append("R5 C1 is not exact zero-delta PASS")
    except (OSError, KeyError, ValueError, json.JSONDecodeError) as error:
        errors.append(f"evidence parse failure: {error}")

    result = {
        "schema": "district_zero.p1a.polish_r5.preservation_result.v1",
        "status": "PASS" if not errors else "FAIL",
        "baseline_inventory": {"records": len(inventory), "failures": len(inventory_failures)},
        "changed_substantive_paths": changed,
        "changed_substantive_path_count": len(changed),
        "unauthorized_path_count": len(unauthorized),
        "protected_scene_nodes": 6,
        "builder_non_marker_regions_byte_identical": not any("world-builder" in error for error in errors),
        "errors": errors,
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
