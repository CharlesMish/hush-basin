#!/usr/bin/env python3
"""Verify the bounded post-v1.2.8 Visibility R3 successor and evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from typing import Any


EXACT_ENGINE = "4.7.1.stable.official.a13da4feb"
IGNORED_PARTS = {".godot", "__pycache__", ".pytest_cache", ".mypy_cache"}
ALLOWED_MODIFIED = {
    "AGENTS.md",
    "PACKET_SHA256SUMS.txt",
    "README_VISIBILITY_REPAIR.md",
    "STATUS.md",
    "scenes/district_zero_p1a.tscn",
    "scripts/p1a_world_builder.gd",
    "scripts/p1a_world_gate.gd",
    "tests/p1a_visibility_repair_runner.gd",
    "tools/compare_visibility_repair_c1.py",
    "tools/package_visibility_repair.py",
    "tools/verify_visibility_repair.py",
}
ALLOWED_ADDED = {
    "P1A_POST_V1_2_8_VISIBILITY_REPAIR_R3_AUTHORITY.md",
    "tests/p1a_visibility_r3_ui_probe.gd",
}
BOUND_HASHES = {
    "P1A_POST_V1_2_8_VISIBILITY_REPAIR_R3_AUTHORITY.md": "ae9fb90740654419b4da65389670a7245486cb872e0ee0dbd2c515051dc75936",
    "scenes/district_zero_p1a.tscn": "b35f802f15b3f3a7e310d6ab0d753ddeca565e83cd95937d40dc1d6d7e83cbb8",
    "scripts/p1a_world_builder.gd": "a45815d865182eb4f69ddc54e8a510d84906b714ed8e64f6c8fcbba960d1c671",
    "scripts/p1a_world_gate.gd": "9ea6475292b7de7a2a6908933230bcc6736ce8e5dc5b6de4eb5dd66fb23756c7",
    "tests/p1a_visibility_repair_runner.gd": "afd7399831f0ba8987f43b31fbdab82e02467c0f0cf463a556c177211488495f",
    "tests/p1a_visibility_r3_ui_probe.gd": "f1ed1e8d63c875aac744b210c10288b5b84e30b6960e23cd8fc17662c3687fe5",
    "tools/compare_visibility_repair_c1.py": "9ab7a623a97517d847f74a0d302a99180245263e2e042897938f3ed600e0306d",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ignored(path: Path, root: Path) -> bool:
    relative = path.relative_to(root)
    return (
        any(part in IGNORED_PARTS for part in relative.parts)
        or path.name == ".DS_Store"
        or path.name.startswith("._")
        or path.name.endswith((".pyc", ".pyo"))
    )


def tree(root: Path) -> dict[str, str]:
    return {
        path.relative_to(root).as_posix(): sha(path)
        for path in sorted(root.rglob("*"))
        if path.is_file() and not ignored(path, root)
    }


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")


def run_semantics(root: Path, evidence: Path, script: str) -> dict[str, Any]:
    target = evidence / "SEMANTICS" / Path(script).stem
    target.mkdir(parents=True, exist_ok=True)
    argv = [sys.executable, "-B", str(root / script)]
    process = subprocess.run(argv, cwd=root, text=True, capture_output=True, check=False)
    write(target / "argv.json", {"argv": argv, "cwd": str(root)})
    (target / "stdout.txt").write_text(process.stdout, encoding="utf-8", newline="\n")
    (target / "stderr.txt").write_text(process.stderr, encoding="utf-8", newline="\n")
    result = {"returncode": process.returncode, "status": "PASS" if process.returncode == 0 else "FAIL"}
    write(target / "process_result.json", result)
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True)
    parser.add_argument("--base", required=True)
    parser.add_argument("--evidence", required=True)
    parser.add_argument("--godot", required=True)
    args = parser.parse_args()
    root = Path(args.root).resolve()
    base = Path(args.base).resolve()
    evidence = Path(args.evidence).resolve()
    errors: list[str] = []

    base_tree = tree(base)
    current_tree = tree(root)
    modified = sorted(path for path in base_tree.keys() & current_tree.keys() if base_tree[path] != current_tree[path])
    added = sorted(current_tree.keys() - base_tree.keys())
    removed = sorted(base_tree.keys() - current_tree.keys())
    unexpected_modified = sorted(set(modified) - ALLOWED_MODIFIED)
    unexpected_added = sorted(set(added) - ALLOWED_ADDED)
    if unexpected_modified:
        errors.append(f"unexpected modified files: {unexpected_modified}")
    if unexpected_added:
        errors.append(f"unexpected added files: {unexpected_added}")
    if removed:
        errors.append(f"removed baseline files: {removed}")
    for relative, digest in BOUND_HASHES.items():
        target = root / relative
        if not target.is_file() or sha(target) != digest:
            errors.append(f"authorized source hash mismatch: {relative}")

    version = subprocess.run([str(Path(args.godot).resolve()), "--version"], cwd=root, text=True, capture_output=True, check=False)
    engine = {
        "argv": [str(Path(args.godot).resolve()), "--version"],
        "observed": version.stdout.strip(),
        "required": EXACT_ENGINE,
        "returncode": version.returncode,
        "status": "PASS" if version.returncode == 0 and version.stdout.strip() == EXACT_ENGINE else "FAIL",
    }
    if engine["status"] != "PASS":
        errors.append("exact engine identity mismatch")

    semantic_results = {
        "v1_2_7r1": run_semantics(root, evidence, "tools/test_v1_2_7r1_repairs.py"),
        "v1_2_8": run_semantics(root, evidence, "tools/test_v1_2_8_semantics.py"),
    }
    if any(result["status"] != "PASS" for result in semantic_results.values()):
        errors.append("inherited semantic suite failure")

    c1 = load(evidence / "C1" / "adjudication.json")
    if not (
        c1.get("status") == "PASS"
        and c1.get("exact_engine") == EXACT_ENGINE
        and c1.get("trace_comparison", {}).get("ticks_compared") == 1260
        and c1.get("trace_comparison", {}).get("maximum_absolute_difference") == 0.0
        and c1.get("trace_comparison", {}).get("raw_trace_bytes_equal") is True
    ):
        errors.append("visibility C1 evidence is not exact zero-delta PASS")

    native = load(evidence / "POST_FIX" / "NATIVE_VISUALS" / "probe_result.json")
    metrics = load(evidence / "POST_FIX" / "NATIVE_VISUALS" / "metric_result.json")
    sweep = load(evidence / "POST_FIX" / "NATIVE_SWEEP_METAL" / "probe_result.json")
    ui = load(evidence / "POST_FIX" / "UI_PROBE" / "ui_probe_result.json")
    rays = native.get("ray_result", {})
    checks = metrics.get("checks", [])
    if not (
        native.get("status") == "PASS"
        and native.get("engine_identity") == EXACT_ENGINE
        and rays.get("status") == "PASS"
        and rays.get("sample_count") == 14
        and rays.get("mismatch_count") == 0
    ):
        errors.append("native visual/ray evidence is not 14/14 PASS")
    if not (
        metrics.get("status") == "PASS"
        and len(checks) == 21
        and all(isinstance(check, dict) and check.get("pass") is True for check in checks)
    ):
        errors.append("native metric evidence is not 21/21 PASS")
    left_separation = next((check.get("observed") for check in checks if check.get("id") == "A1:left_obstacle_separation"), None)
    if not isinstance(left_separation, (int, float)) or float(left_separation) < 0.12:
        errors.append("newly visible left wall does not meet unchanged 0.12 separation gate")
    sweep_records = sweep.get("records", [])
    if not (
        sweep.get("status") == "PASS"
        and sweep.get("engine_identity") == EXACT_ENGINE
        and len(sweep_records) == 14
        and all(float(record.get("camera_pull_in_m", -1.0)) == 0.0 for record in sweep_records)
    ):
        errors.append("registered visibility sweep is incomplete or altered an unobstructed camera start")

    if not (
        ui.get("status") == "PASS"
        and ui.get("engine_identity") == EXACT_ENGINE
        and "v1.2.8 VISIBILITY R3" in str(ui.get("status_text", ""))
        and "WORLD v1.2.3" in str(ui.get("status_text", ""))
        and "VISIBILITY R3" in str(ui.get("identity_text", ""))
        and len(str(ui.get("image_sha256", ""))) == 64
    ):
        errors.append("R3 user-facing executable identity/capture is not PASS")

    behavior_log = (evidence / "POST_FIX" / "visibility-test-engine.log").read_text(encoding="utf-8")
    behavior_lines = [line for line in behavior_log.splitlines() if line.startswith("P1A_VISIBILITY_REPAIR_RESULT ")]
    behavior = json.loads(behavior_lines[-1].split("P1A_VISIBILITY_REPAIR_RESULT ", 1)[1]) if behavior_lines else {}
    behavior_checks = behavior.get("checks", [])
    parity_checks = [check for check in behavior_checks if str(check.get("id", "")).endswith("_COLLISION_RENDER_TWO_SIDED")]
    if not (
        behavior.get("status") == "PASS"
        and behavior.get("failure_count") == 0
        and len(behavior_checks) == 39
        and len(parity_checks) == 19
        and all(check.get("status") == "PASS" for check in behavior_checks)
    ):
        errors.append("visibility behavior suite is not PASS")

    pre_fix_log = (evidence / "PRE_FIX" / "visibility-test-engine.log").read_text(encoding="utf-8")
    if not all(token in pre_fix_log for token in (
        '"id":"MESH_B01_COLLISION_RENDER_TWO_SIDED","status":"FAIL"',
        '"id":"MESH_B14_COLLISION_RENDER_TWO_SIDED","status":"FAIL"',
        '"id":"MESH_CORE_PLINTH_COLLISION_RENDER_TWO_SIDED","status":"FAIL"',
        '"id":"MESH_HOP_BAR_01_COLLISION_RENDER_TWO_SIDED","status":"FAIL"',
        '"id":"REVIEW_BUILD_IDENTITY_UNAMBIGUOUS","status":"FAIL"',
        '"failure_count":17',
    )):
        errors.append("pre-fix all-solid culling/identity reproduction is incomplete")

    report = {
        "added_files": added,
        "base_file_count": len(base_tree),
        "bound_source_hashes": BOUND_HASHES,
        "engine": engine,
        "errors": errors,
        "frozen_byte_identical_file_count": len(base_tree) - len(modified),
        "modified_files": modified,
        "native_metrics": {"passed": sum(check.get("pass") is True for check in checks), "total": len(checks)},
        "native_rays": {"mismatches": rays.get("mismatch_count"), "total": rays.get("sample_count")},
        "registered_sweep_count": len(sweep_records),
        "removed_files": removed,
        "schema": "district_zero.p1a.visibility_repair_r3_verification.v1",
        "semantic_results": semantic_results,
        "source_file_count": len(current_tree),
        "status": "PASS" if not errors else "FAIL",
        "unexpected_added": unexpected_added,
        "unexpected_modified": unexpected_modified,
        "two_sided_solid_families": len(parity_checks),
        "user_facing_identity": {"image_sha256": ui.get("image_sha256"), "status": ui.get("status")},
        "visibility_behavior_checks": {"passed": len(behavior_checks), "total": len(behavior_checks)},
        "visibility_c1": c1.get("trace_comparison"),
        "visible_left_wall_separation": {"observed": left_separation, "required_minimum": 0.12},
    }
    write(evidence / "STATIC_VERIFICATION" / "report.json", report)
    print(json.dumps(report, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
