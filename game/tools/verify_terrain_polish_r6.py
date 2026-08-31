#!/usr/bin/env python3
"""Verify that Terrain Polish R6 changes only its declared presentation surface."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import sys


MODIFIED = {
    "AGENTS.md",
    "STATUS.md",
    "project.godot",
    "scenes/district_zero_p1a.tscn",
    "scripts/p1a_world_builder.gd",
    "scripts/p1a_world_gate.gd",
}
REMOVED = {"PLAY_DISTRICT_ZERO_POLISH_R5.command", "POLISH_R5_SHA256SUMS.txt"}
ADDED = {
    "P1A_POST_V1_2_8_TERRAIN_POLISH_R6_AUTHORITY.md",
    "PLAY_DISTRICT_ZERO_TERRAIN_POLISH_R6.command",
    "R5_BASELINE_SHA256SUMS.txt",
    "README_TERRAIN_POLISH_R6.md",
    "TERRAIN_POLISH_R6_EXECUTION_REPORT.md",
    "tests/p1a_polish_r6_runner.gd",
    "tests/p1a_polish_r6_runner.gd.uid",
    "tests/p1a_polish_r6_ui_probe.gd",
    "tests/p1a_polish_r6_ui_probe.gd.uid",
    "tests/p1a_terrain_polish_r6_runner.gd",
    "tests/p1a_terrain_polish_r6_runner.gd.uid",
    "tools/compare_terrain_polish_r6_c1.py",
    "tools/verify_terrain_polish_r6.py",
}
FORBIDDEN_PARTS = {".godot", "__pycache__", "__MACOSX"}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def substantive(root: Path) -> set[str]:
    result = set()
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(root)
        if any(part in FORBIDDEN_PARTS for part in rel.parts):
            continue
        if path.name == ".DS_Store" or path.name.startswith("._"):
            continue
        result.add(rel.as_posix())
    return result


def inventory(root: Path) -> tuple[int, list[str]]:
    failures = []
    rows = (root / "POLISH_R5_SHA256SUMS.txt").read_text(encoding="utf-8").splitlines()
    for row in rows:
        expected, relative = row.split("  ", 1)
        path = root / relative
        if not path.is_file() or digest(path) != expected:
            failures.append(relative)
    return len(rows), failures


def normalize_identity(relative: str, text: str) -> str:
    replacements = {
        "project.godot": [
            ("District Zero P1A — Terrain Polish R6 Owner Review", "District Zero P1A — Polish R5 Development Review"),
        ],
        "scenes/district_zero_p1a.tscn": [
            ("P1A TERRAIN POLISH R6 · OWNER REVIEW", "P1A POLISH R5 · DEVELOPMENT REVIEW"),
            ("DISTRICT ZERO · P1A TERRAIN POLISH R6 · WORLD v1.2.3", "DISTRICT ZERO · P1A POLISH R5 · WORLD v1.2.3"),
        ],
        "scripts/p1a_world_gate.gd": [
            ("DISTRICT ZERO · P1A TERRAIN POLISH R6 · WORLD v1.2.3", "DISTRICT ZERO · P1A POLISH R5 · WORLD v1.2.3"),
            ("P1A TERRAIN POLISH R6 · OWNER REVIEW", "P1A POLISH R5 · DEVELOPMENT REVIEW"),
        ],
    }
    for current, baseline in replacements.get(relative, []):
        if text.count(current) != 1:
            raise ValueError(f"identity anchor count mismatch: {relative}: {current}")
        text = text.replace(current, baseline)
    return text


def normalize_builder(text: str) -> str:
    constants = (
        "const TERRAIN_RENDER_BOUNDARY_BLEND := 0.22\n"
        "const TERRAIN_RENDER_SMOOTHABLE_CLASS_MAX := 9\n"
    )
    if text.count(constants) != 1:
        raise ValueError("terrain smoothing constant block mismatch")
    text = text.replace(constants, "")
    call = "\t\t\tcolors[index] = _terrain_render_color(ix, iz, width, depth)"
    original = "\t\t\tcolors[index] = SURFACE_COLORS.get(int(data.surface_bytes[index]), Color.MAGENTA)"
    if text.count(call) != 1:
        raise ValueError("terrain color call anchor mismatch")
    text = text.replace(call, original)
    pattern = re.compile(r"\n\nfunc _terrain_render_color\(.*?\n\nfunc _build_solids\(\) -> void:", re.DOTALL)
    text, count = pattern.subn("\n\nfunc _build_solids() -> void:", text)
    if count != 1:
        raise ValueError("terrain helper block mismatch")
    return text


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print("usage: verify_terrain_polish_r6.py R5_BASELINE R6_SOURCE", file=sys.stderr)
        return 2
    baseline, source = map(lambda value: Path(value).resolve(), argv[1:])
    failures: list[str] = []
    try:
        count, inventory_failures = inventory(baseline)
        if count != 208 or inventory_failures:
            failures.append(f"R5 inventory: count={count}, failures={inventory_failures}")
        base_files, source_files = substantive(baseline), substantive(source)
        expected_source = (base_files - REMOVED) | ADDED
        missing = sorted(expected_source - source_files)
        unexpected = sorted(source_files - expected_source)
        if missing:
            failures.append(f"missing paths: {missing}")
        if unexpected:
            failures.append(f"unexpected paths: {unexpected}")
        for relative in sorted(base_files - MODIFIED - REMOVED):
            if digest(baseline / relative) != digest(source / relative):
                failures.append(f"undeclared byte delta: {relative}")
        for relative in ("project.godot", "scenes/district_zero_p1a.tscn", "scripts/p1a_world_gate.gd"):
            current = normalize_identity(relative, (source / relative).read_text(encoding="utf-8"))
            if current.encode() != (baseline / relative).read_bytes():
                failures.append(f"non-identity delta in {relative}")
        builder = normalize_builder((source / "scripts/p1a_world_builder.gd").read_text(encoding="utf-8"))
        if builder.encode() != (baseline / "scripts/p1a_world_builder.gd").read_bytes():
            failures.append("world builder contains a delta outside the declared terrain-color helper")
        height_sha = digest(source / "world/generated/heightfield_i16le.bin")
        surface_sha = digest(source / "world/generated/surface_classes_u8.bin")
        if height_sha != "f377a1034406ee2f35232c01f6cb80be8dd43d13267e3821d1edcab9a9735b88":
            failures.append("heightfield identity mismatch")
        if surface_sha != "3d7466384a52bb8033e5fad5acd014a2daedec76475d5ad21ff13a94cee73949":
            failures.append("surface-class identity mismatch")
        result = {
            "baseline_inventory_records": count,
            "declared_added_paths": len(ADDED),
            "heightfield_sha256": height_sha,
            "schema": "district_zero.p1a.terrain_polish_r6.preservation.v1",
            "status": "PASS" if not failures else "FAIL",
            "surface_classes_sha256": surface_sha,
            "unchanged_baseline_paths": len(base_files - MODIFIED - REMOVED),
            "violations": failures,
        }
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0 if not failures else 1
    except (OSError, ValueError) as error:
        print(json.dumps({"error": str(error), "status": "FAIL"}, sort_keys=True), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
