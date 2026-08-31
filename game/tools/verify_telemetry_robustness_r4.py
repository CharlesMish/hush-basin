#!/usr/bin/env python3
"""Verify the behavior-neutral R4 telemetry/output robustness successor."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
from typing import Any


EXACT_ENGINE = "4.7.1.stable.official.a13da4feb"
RESULT_PREFIX = "P1A_TELEMETRY_POLICY_RESULT "
RUNTIME_PREFIX = "P1A_RUNTIME_RESULT "
IGNORED_PARTS = {".godot", "__pycache__", ".pytest_cache", ".mypy_cache"}
ALLOWED_MODIFIED = {
    "AGENTS.md",
    "PACKET_SHA256SUMS.txt",
    "STATUS.md",
    "scripts/p1a_telemetry.gd",
}
ALLOWED_ADDED = {
    "P1A_POST_V1_2_8_ROBUSTNESS_R4_AUTHORITY.md",
    "PLAY_DISTRICT_ZERO_R4.command",
    "README_ROBUSTNESS_R4.md",
    "tests/p1a_telemetry_output_policy_test.gd",
    "tools/package_telemetry_robustness_r4.py",
    "tools/verify_telemetry_robustness_r4.py",
}
ERROR_PATTERNS = tuple(re.compile(value, re.IGNORECASE) for value in (
    r"SCRIPT ERROR",
    r"Parse Error",
    r"Failed to load script",
    r"Could not find type",
    r"not declared in the current scope",
    r"ERROR:\s+Failed",
))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value, encoding="utf-8", newline="\n")


def dump(path: Path, value: Any) -> None:
    write(path, json.dumps(value, indent=2, sort_keys=True) + "\n")


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
        path.relative_to(root).as_posix(): sha256(path)
        for path in sorted(root.rglob("*"))
        if path.is_file() and not ignored(path, root)
    }


def verify_inventory(root: Path, name: str) -> list[str]:
    inventory = root / name
    if not inventory.is_file():
        return [f"missing {name}"]
    errors: list[str] = []
    represented: set[str] = set()
    for line_number, line in enumerate(inventory.read_text(encoding="utf-8").splitlines(), 1):
        match = re.fullmatch(r"([0-9a-f]{64})  (.+)", line)
        if not match:
            errors.append(f"malformed inventory line {line_number}")
            continue
        digest, relative = match.groups()
        represented.add(relative)
        target = root / relative
        if not target.is_file() or sha256(target) != digest:
            errors.append(f"inventory mismatch: {relative}")
    actual = set(tree(root)) - {name}
    if represented != actual:
        errors.append(f"inventory coverage mismatch missing={sorted(actual-represented)[:3]} extra={sorted(represented-actual)[:3]}")
    return errors


def run_stage(directory: Path, command: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    directory.mkdir(parents=True, exist_ok=True)
    dump(directory / "argv.json", {"argv": command, "cwd": str(cwd)})
    process = subprocess.run(command, cwd=cwd, capture_output=True, text=True, check=False)
    write(directory / "stdout.txt", process.stdout)
    write(directory / "stderr.txt", process.stderr)
    dump(directory / "process_result.json", {"returncode": process.returncode})
    return process


def recognized_errors(*texts: str) -> list[str]:
    found: list[str] = []
    for text in texts:
        for line in text.splitlines():
            normalized = line.strip()
            if normalized and any(pattern.search(normalized) for pattern in ERROR_PATTERNS) and normalized not in found:
                found.append(normalized)
    return found


def json_records(stdout: str) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for line in stdout.splitlines():
        if not line.startswith("{"):
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict):
            records.append(value)
    return records


def prefixed_records(stdout: str, prefix: str) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for line in stdout.splitlines():
        if not line.startswith(prefix):
            continue
        try:
            value = json.loads(line[len(prefix):])
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict):
            records.append(value)
    return records


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True)
    parser.add_argument("--r3-baseline", required=True)
    parser.add_argument("--player-project", required=True)
    parser.add_argument("--godot", required=True)
    parser.add_argument("--p0-root", required=True)
    parser.add_argument("--evidence", required=True)
    parser.add_argument("--c1-work", required=True)
    args = parser.parse_args()

    source = Path(args.source).resolve()
    baseline = Path(args.r3_baseline).resolve()
    player = Path(args.player_project).resolve()
    godot = str(Path(args.godot).resolve())
    evidence = Path(args.evidence).resolve()
    c1_work = Path(args.c1_work).resolve()
    errors: list[str] = []

    if evidence.exists() and any(evidence.iterdir()):
        print(json.dumps({"status": "BLOCKED", "error": "evidence root is not new/empty"}, sort_keys=True))
        return 2
    evidence.mkdir(parents=True, exist_ok=True)

    baseline_inventory_errors = verify_inventory(baseline, "PACKET_SHA256SUMS.txt")
    if baseline_inventory_errors:
        errors.append(f"R3 baseline inventory failed: {baseline_inventory_errors[:3]}")
    baseline_tree = tree(baseline)
    source_tree = tree(source)
    modified = sorted(path for path in baseline_tree.keys() & source_tree.keys() if baseline_tree[path] != source_tree[path])
    added = sorted(source_tree.keys() - baseline_tree.keys())
    removed = sorted(baseline_tree.keys() - source_tree.keys())
    unexpected_modified = sorted(set(modified) - ALLOWED_MODIFIED)
    unexpected_added = sorted(set(added) - ALLOWED_ADDED)
    if unexpected_modified:
        errors.append(f"unexpected modified paths: {unexpected_modified}")
    if unexpected_added:
        errors.append(f"unexpected added paths: {unexpected_added}")
    if removed:
        errors.append(f"removed R3 paths: {removed}")

    fixture = player / "tests/fixtures/v1_2_7_v1_2_6_world_builder.gd"
    production_builder = player / "scripts/p1a_world_builder.gd"
    if fixture.exists():
        errors.append("runnable player copy retained the duplicate-class builder fixture")
    if not production_builder.is_file():
        errors.append("runnable player copy lacks production builder")

    engine = run_stage(evidence / "ENGINE_IDENTITY", [godot, "--version"], source)
    observed_engine = engine.stdout.strip()
    if engine.returncode != 0 or observed_engine != EXACT_ENGINE:
        errors.append(f"exact engine mismatch: {observed_engine!r}")

    import_log = evidence / "PLAYER_IMPORT" / "import-engine.txt"
    imported = run_stage(evidence / "PLAYER_IMPORT" / "IMPORT", [godot, "--headless", "--path", str(player), "--import", "--log-file", str(import_log)], player)
    parse_log = evidence / "PLAYER_IMPORT" / "parse-engine.txt"
    parsed = run_stage(evidence / "PLAYER_IMPORT" / "PARSE", [godot, "--headless", "--editor", "--quit", "--path", str(player), "--log-file", str(parse_log)], player)
    import_errors = recognized_errors(
        imported.stdout,
        imported.stderr,
        parsed.stdout,
        parsed.stderr,
        import_log.read_text(encoding="utf-8", errors="replace") if import_log.is_file() else "",
        parse_log.read_text(encoding="utf-8", errors="replace") if parse_log.is_file() else "",
    )
    if imported.returncode != 0 or parsed.returncode != 0 or import_errors:
        errors.append(f"player import/parse failed: {import_errors[:3]}")

    test_script = "res://tests/p1a_telemetry_output_policy_test.gd"
    normal_log = evidence / "TELEMETRY_POLICY" / "NORMAL" / "engine.txt"
    normal = run_stage(evidence / "TELEMETRY_POLICY" / "NORMAL", [godot, "--headless", "--path", str(player), "--script", test_script, "--log-file", str(normal_log)], player)
    normal_events = json_records(normal.stdout)
    normal_results = prefixed_records(normal.stdout, RESULT_PREFIX)
    if not (
        normal.returncode == 0
        and len(normal_events) == 0
        and len(normal_results) == 1
        and normal_results[0].get("status") == "PASS"
        and normal_results[0].get("console_jsonl_enabled") is False
        and normal_results[0].get("event_queue_count") == 1
        and normal_results[0].get("signal_count") == 1
    ):
        errors.append("ordinary-play telemetry policy probe failed")

    vector_log = evidence / "TELEMETRY_POLICY" / "VECTOR" / "engine.txt"
    vector = run_stage(evidence / "TELEMETRY_POLICY" / "VECTOR", [godot, "--headless", "--path", str(player), "--script", test_script, "--log-file", str(vector_log), "--", "--vector", "ROBUSTNESS_PROBE"], player)
    vector_events = json_records(vector.stdout)
    vector_results = prefixed_records(vector.stdout, RESULT_PREFIX)
    if not (
        vector.returncode == 0
        and len(vector_events) == 1
        and vector_events[0].get("event") == "ROBUSTNESS_POLICY_PROBE"
        and len(vector_results) == 1
        and vector_results[0].get("status") == "PASS"
        and vector_results[0].get("console_jsonl_enabled") is True
    ):
        errors.append("runtime-vector telemetry policy probe failed")

    smoke_log = evidence / "STANDALONE_SMOKE" / "engine.txt"
    smoke = run_stage(evidence / "STANDALONE_SMOKE", [godot, "--headless", "--path", str(player), "--fixed-fps", "60", "--quit-after", "180", "--log-file", str(smoke_log)], player)
    if smoke.returncode != 0 or json_records(smoke.stdout) or smoke.stdout.count("P1A_RUNTIME_READY") != 1:
        errors.append("ordinary standalone smoke emitted telemetry JSONL or failed readiness")

    wall_log = evidence / "RUNTIME_VECTOR_WALL_CONTACT" / "engine.txt"
    wall = run_stage(evidence / "RUNTIME_VECTOR_WALL_CONTACT", [godot, "--headless", "--path", str(player), "--fixed-fps", "60", "--script", "res://tests/p1a_runtime_runner.gd", "--log-file", str(wall_log), "--", "--vector", "RT_BOUNDARY_CORE_WALL_LOW_THRUST"], player)
    wall_events = json_records(wall.stdout)
    wall_results = prefixed_records(wall.stdout, RUNTIME_PREFIX)
    collision_count = sum(record.get("event") == "COLLISION_SAMPLE" for record in wall_events)
    if not (
        wall.returncode == 0
        and len(wall_results) == 1
        and wall_results[0].get("status") == "PASS"
        and collision_count > 0
        and wall_results[0].get("terminal_evidence", {}).get("post_result_event_count") == 0
    ):
        errors.append("authoritative wall-contact runtime vector did not preserve JSONL evidence")

    launcher = run_stage(evidence / "LAUNCHER_SYNTAX", ["/bin/zsh", "-n", str(player / "PLAY_DISTRICT_ZERO_R4.command")], player)
    if launcher.returncode != 0:
        errors.append("standalone launcher syntax failed")

    semantic_results: dict[str, Any] = {}
    for name, relative in (
        ("v1_2_7r1", "tools/test_v1_2_7r1_repairs.py"),
        ("v1_2_8", "tools/test_v1_2_8_semantics.py"),
    ):
        process = run_stage(evidence / "INHERITED_SEMANTICS" / name, [sys.executable, "-B", str(source / relative)], source)
        semantic_results[name] = {"returncode": process.returncode, "status": "PASS" if process.returncode == 0 else "FAIL"}
        if process.returncode != 0:
            errors.append(f"inherited semantic suite failed: {name}")

    c1_command = [
        sys.executable,
        "-B",
        str(source / "tools/run_v1_2_7r1_c1.py"),
        "--root",
        str(source),
        "--godot",
        godot,
        "--evidence-dir",
        str(evidence / "C1"),
        "--work-root",
        str(c1_work),
    ]
    c1 = run_stage(evidence / "C1_WRAPPER", c1_command, source)
    try:
        inherited_c1_result = json.loads((evidence / "C1" / "C1_result.json").read_text(encoding="utf-8"))
    except Exception:
        inherited_c1_result = {}
    visibility_c1_command = [
        sys.executable,
        "-B",
        str(source / "tools/compare_visibility_repair_c1.py"),
        str(evidence / "C1" / "v1_2_6_runtime_baseline" / "trace.jsonl"),
        str(evidence / "C1" / "v1_2_7r1_selected" / "trace.jsonl"),
        str(source / "tests/fixtures/baseline_flat_support.json"),
    ]
    visibility_c1 = run_stage(evidence / "C1_VISIBILITY_COMPARATOR", visibility_c1_command, source)
    try:
        c1_result = json.loads(visibility_c1.stdout.strip().splitlines()[-1])
    except Exception:
        c1_result = {}
    if not (
        visibility_c1.returncode == 0
        and c1_result.get("status") == "PASS"
        and c1_result.get("ticks_compared") == 1260
        and float(c1_result.get("maximum_absolute_difference", 1.0)) == 0.0
        and c1_result.get("raw_trace_bytes_equal") is True
    ):
        errors.append("C1 did not remain 1,260 ticks at zero delta")

    all_process_text = "\n".join(
        path.read_text(encoding="utf-8", errors="replace")
        for path in evidence.rglob("*.txt")
        if path.is_file()
    )
    process_errors = recognized_errors(all_process_text)
    if process_errors:
        errors.append(f"recognized engine/script errors in R4 verification: {process_errors[:3]}")

    report = {
        "schema": "district_zero.p1a.telemetry_robustness_r4_verification.v1",
        "status": "PASS" if not errors else "FAIL",
        "exact_engine": observed_engine,
        "errors": errors,
        "r3_baseline_inventory": "PASS" if not baseline_inventory_errors else "FAIL",
        "source_delta": {
            "modified": modified,
            "added": added,
            "removed": removed,
            "unexpected_modified": unexpected_modified,
            "unexpected_added": unexpected_added,
            "frozen_byte_identical_file_count": len(baseline_tree) - len(modified),
        },
        "player_import_parse": "PASS" if not import_errors and imported.returncode == 0 and parsed.returncode == 0 else "FAIL",
        "ordinary_policy": {"status": normal_results[0].get("status") if normal_results else "MISSING", "json_event_lines": len(normal_events)},
        "runtime_policy": {"status": vector_results[0].get("status") if vector_results else "MISSING", "json_event_lines": len(vector_events)},
        "standalone_smoke": {"returncode": smoke.returncode, "json_event_lines": len(json_records(smoke.stdout))},
        "wall_contact_vector": {"returncode": wall.returncode, "status": wall_results[0].get("status") if wall_results else "MISSING", "event_count": len(wall_events), "collision_sample_count": collision_count},
        "semantic_results": semantic_results,
        "c1": {
            "inherited_comparator_status": inherited_c1_result.get("status"),
            "inherited_comparator_error": inherited_c1_result.get("error"),
            "visibility_successor": c1_result,
            "raw_traces_preserved_after_inherited_wrapper": c1.returncode in (0, 1),
        },
        "human_attempts": 0,
        "human_world_gate": "NOT PERFORMED",
        "P1B": "FROZEN",
    }
    dump(evidence / "VERIFICATION_REPORT.json", report)
    print(json.dumps(report, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
