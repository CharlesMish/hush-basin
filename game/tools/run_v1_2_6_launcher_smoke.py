#!/usr/bin/env python3
"""Run the one authorized non-evidentiary v1.2.6 native launcher smoke."""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import pathlib
import re
import shutil
import subprocess
import time
from typing import Any

EXACT = "4.7.1.stable.official.a13da4feb"
ERRORS = tuple(re.compile(value, re.I) for value in (
    r"SCRIPT ERROR", r"Parse Error", r"Failed to load script", r"ERROR:\s+Failed",
    r"not declared in the current scope", r"Could not find type", r"Cannot infer the type",
))


def dump(path: pathlib.Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def sha(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def crash_reports() -> dict[str, float]:
    root = pathlib.Path.home() / "Library/Logs/DiagnosticReports"
    if not root.is_dir():
        return {}
    return {str(path): path.stat().st_mtime for path in root.glob("Godot-*.ips") if path.is_file()}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--godot", required=True)
    parser.add_argument("--project-root", required=True)
    parser.add_argument("--session-root", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--session-id", required=True)
    parser.add_argument("--minimum-wall-duration-s", type=float, default=75.0)
    args = parser.parse_args()
    godot = pathlib.Path(args.godot).resolve()
    project = pathlib.Path(args.project_root).resolve()
    session = pathlib.Path(args.session_root).resolve()
    output = pathlib.Path(args.output_dir).resolve()
    output.mkdir(parents=True, exist_ok=True)
    state_path = session / "session_state.json"
    state_before = state_path.read_bytes() if state_path.is_file() else b""
    captures_before = sorted(str(path.relative_to(session)) for path in session.glob("routes/*/captures/*/attempt_result.json"))
    reports_before = crash_reports()
    engine_log = output / "engine.txt"
    command = [
        str(godot), "--log-file", str(engine_log), "--path", str(project), "--fixed-fps", "60",
        "--script", "res://tests/p1a_human_feasibility_runner.gd", "--",
        "--mode", "familiarization", "--route", "A1", "--output-dir", str(output),
        "--session-id", args.session_id, "--v1-2-6-smoke",
    ]
    dump(output / "argv.json", {"argv": command, "cwd": str(project)})
    started_wall = time.time()
    started_utc = dt.datetime.now(dt.timezone.utc).isoformat()
    process = subprocess.Popen(command, cwd=project, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    dump(output / "process_started.json", {"pid": process.pid, "started_utc": started_utc})
    stdout, stderr = process.communicate()
    ended_wall = time.time()
    ended_utc = dt.datetime.now(dt.timezone.utc).isoformat()
    (output / "stdout.txt").write_text(stdout, encoding="utf-8")
    (output / "stderr.txt").write_text(stderr, encoding="utf-8")
    if not engine_log.is_file():
        engine_log.write_text("", encoding="utf-8")
    familiarization_path = output / "familiarization_result.json"
    familiarization = json.loads(familiarization_path.read_text(encoding="utf-8")) if familiarization_path.is_file() else {}
    observation = familiarization.get("v1_2_6_smoke_observation", {}) if isinstance(familiarization, dict) else {}
    reports_after = crash_reports()
    new_reports = sorted(path for path, stamp in reports_after.items() if path not in reports_before or stamp > reports_before[path])
    for report in new_reports:
        (output / "crash_reports").mkdir(parents=True, exist_ok=True)
        shutil.copy2(report, output / "crash_reports" / pathlib.Path(report).name)
    combined = "\n".join((stdout, stderr, engine_log.read_text(encoding="utf-8", errors="replace")))
    script_errors = sorted({line.strip() for line in combined.splitlines() if any(pattern.search(line) for pattern in ERRORS)})
    wall_duration = ended_wall - started_wall
    state_after = state_path.read_bytes() if state_path.is_file() else b""
    captures_after = sorted(str(path.relative_to(session)) for path in session.glob("routes/*/captures/*/attempt_result.json"))
    checks = {
        "duration_at_least_75_s": wall_duration >= args.minimum_wall_duration_s,
        "clean_process_exit": process.returncode == 0,
        "runtime_result_present": familiarization.get("status") == "COMPLETE",
        "movement_input_at_least_10_s": float(observation.get("movement_input_s", 0.0)) >= 10.0,
        "steer_left_at_least_2_s": float(observation.get("steer_left_s", 0.0)) >= 2.0,
        "steer_right_at_least_2_s": float(observation.get("steer_right_s", 0.0)) >= 2.0,
        "pause_and_resume_observed": bool(observation.get("pause_timestamps_s")) and bool(observation.get("resume_timestamps_s")),
        "focus_out_and_in_observed": bool(observation.get("focus_out_timestamps_s")) and bool(observation.get("focus_in_timestamps_s")),
        "no_new_crash_report": not new_reports,
        "no_script_or_parse_error": not script_errors,
        "session_state_unchanged": state_before == state_after,
        "zero_attempt_results": captures_before == captures_after == [],
    }
    passed = all(checks.values())
    result = {
        "schema": "district_zero.p1a.v1_2_6.native_launcher_smoke_result.v1",
        "status": "PASS" if passed else "BLOCKED/NOT TESTABLE — MACOS GODOT RUNTIME",
        "engine_identity": EXACT,
        "process": {"pid": process.pid, "started_utc": started_utc, "ended_utc": ended_utc, "wall_duration_s": wall_duration, "returncode": process.returncode},
        "checks": checks,
        "observation": observation,
        "new_crash_reports": new_reports,
        "script_errors": script_errors,
        "session_state_sha256_before": hashlib.sha256(state_before).hexdigest(),
        "session_state_sha256_after": hashlib.sha256(state_after).hexdigest(),
        "attempts_consumed": 0,
        "human_world_gate": "NOT PERFORMED",
        "P1B": "FROZEN",
    }
    dump(output / "smoke_result.json", result)
    print(json.dumps(result, sort_keys=True))
    return 0 if passed else 2


if __name__ == "__main__":
    raise SystemExit(main())
