#!/usr/bin/env python3
"""Run District Zero P1A runtime vectors under execution overlay v1.2.5.

This runner preserves the raw Godot result separately from suite classification.
A completed gameplay vector is PASS/0 or FAIL/1. Exit 2, an absent/invalid result,
zero pre-result telemetry, launch errors, or post-result telemetry is
BLOCKED/NOT TESTABLE.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import pathlib
import re
import shutil
import subprocess
import sys
import zipfile
from dataclasses import dataclass
from typing import Any, Iterable

ROOT = pathlib.Path(__file__).resolve().parents[1]
FIXTURE_PATH = ROOT / "tests" / "fixtures" / "runtime_vectors.json"
CANDIDATE_PATH = ROOT / "tests" / "fixtures" / "fast_route_driver_v7_candidates.json"
PREFIX = "P1A_RUNTIME_RESULT "
FAST_IDS = ("RT_ROUTE_A1", "RT_ROUTE_A2", "RT_ROUTE_X0")
EXACT_VERSION = "4.7.1.stable.official.a13da4feb"
EXECUTION_OVERLAY = "1.2.5"
FIXTURE_AUTHORITY = "1.2.5"
V7_ALGORITHM_AUTHORITY = "RETIRED"
WORLD_AUTHORITY = "1.2.3"
RESULT_CONTRACT_ID = "DZP1A_RUNTIME_RESULT_EXIT_V1"
V7_CONTROLLER = "ROUTE_FOLLOWER_INPUT_CONTROLLER_V7_PHASE_SEPARATED_BRAKE_CAPTURE_CONTAINED"
HUMAN_CONTROLLER = "NORMALIZED_INPUT_TRACE_REPLAY_V1"
PER_VECTOR_FILES = (
    "argv.json",
    "stdout.txt",
    "stderr.txt",
    "engine.txt",
    "runtime_result_line.txt",
    "runtime_result.json",
    "suite_classification.json",
    "events.jsonl",
    "post_result_events.jsonl",
    "result.json",
)
REQUIRED_CLASSES = sorted(
    (
        "CraftController",
        "CraftTuning",
        "MotionMath",
        "P1AMap",
        "P1ATelemetry",
        "P1AWorldBuilder",
        "P1AWorldData",
        "P1AWorldGate",
        "StableCameraRig",
        "SurfaceFeedback3D",
    )
)
LAUNCH_ERROR_PATTERNS = (
    re.compile(r"SCRIPT ERROR", re.IGNORECASE),
    re.compile(r"Parse Error", re.IGNORECASE),
    re.compile(r"Cannot infer the type", re.IGNORECASE),
    re.compile(r"Could not find type", re.IGNORECASE),
    re.compile(r"not declared in the current scope", re.IGNORECASE),
    re.compile(r"Failed to load script", re.IGNORECASE),
    re.compile(r"unresolved registered class", re.IGNORECASE),
    re.compile(r"ERROR:\s+Failed", re.IGNORECASE),
)


def dump(path: pathlib.Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def write_text(path: pathlib.Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value, encoding="utf-8", newline="\n")


def sha256(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def checksum_inventory(root: pathlib.Path) -> int:
    rows: list[str] = []
    for path in sorted(
        (p for p in root.rglob("*") if p.is_file() and p.name != "SHA256SUMS.txt"),
        key=lambda p: p.relative_to(root).as_posix().encode("utf-8"),
    ):
        rows.append(f"{sha256(path)}  {path.relative_to(root).as_posix()}\n")
    write_text(root / "SHA256SUMS.txt", "".join(rows))
    return len(rows)


def deterministic_zip(source: pathlib.Path, output: pathlib.Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists():
        output.unlink()
    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in sorted(
            (p for p in source.rglob("*") if p.is_file()),
            key=lambda p: p.relative_to(source).as_posix().encode("utf-8"),
        ):
            rel = path.relative_to(source).as_posix()
            info = zipfile.ZipInfo(rel, (1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, path.read_bytes())


def load_json(path: pathlib.Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} is not a JSON object")
    return value


def scan_launch_errors(texts: Iterable[str]) -> list[str]:
    found: list[str] = []
    seen: set[str] = set()
    for text in texts:
        for line in text.splitlines():
            normalized = line.strip()
            if normalized and any(pattern.search(normalized) for pattern in LAUNCH_ERROR_PATTERNS):
                if normalized not in seen:
                    found.append(normalized)
                    seen.add(normalized)
    return found


@dataclass(frozen=True)
class ParsedOutput:
    raw_result_lines: list[str]
    raw_results: list[dict[str, Any]]
    pre_result_events: list[dict[str, Any]]
    post_result_events: list[dict[str, Any]]
    malformed_result_lines: list[str]


def parse_runner_stdout(stdout: str) -> ParsedOutput:
    raw_lines: list[str] = []
    raw_results: list[dict[str, Any]] = []
    pre_events: list[dict[str, Any]] = []
    post_events: list[dict[str, Any]] = []
    malformed: list[str] = []
    result_seen = False
    for line in stdout.splitlines():
        if line.startswith(PREFIX):
            raw_lines.append(line)
            result_seen = True
            try:
                value = json.loads(line[len(PREFIX) :])
            except json.JSONDecodeError:
                malformed.append(line)
                continue
            if isinstance(value, dict):
                raw_results.append(value)
            else:
                malformed.append(line)
            continue
        if not line.startswith("{"):
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(value, dict) or "event" not in value:
            continue
        (post_events if result_seen else pre_events).append(value)
    return ParsedOutput(raw_lines, raw_results, pre_events, post_events, malformed)


def classify_runtime_attempt(
    *,
    requested_vector_id: str,
    process_returncode: int,
    parsed: ParsedOutput,
    launch_error_lines: list[str],
    import_preflight_passed: bool,
) -> dict[str, Any]:
    """Classify one process without mutating the raw result payload."""
    blockers: list[str] = []
    raw: dict[str, Any] | None = parsed.raw_results[0] if len(parsed.raw_results) == 1 else None
    if not import_preflight_passed:
        blockers.append("composite import/runner-parse preflight was not PASS")
    if parsed.malformed_result_lines:
        blockers.append("malformed P1A_RUNTIME_RESULT line")
    if len(parsed.raw_result_lines) != 1 or len(parsed.raw_results) != 1:
        blockers.append(
            f"expected exactly one valid runtime result, observed {len(parsed.raw_result_lines)} line(s) and {len(parsed.raw_results)} valid payload(s)"
        )
    if launch_error_lines:
        blockers.append("launch/parse/load error emitted")
    if raw is not None:
        status = raw.get("status")
        if raw.get("id") != requested_vector_id:
            blockers.append("runtime result vector ID mismatch")
        if status in ("PASS", "FAIL"):
            expected_code = 0 if status == "PASS" else 1
            if process_returncode != expected_code:
                blockers.append(
                    f"runtime result/exit mismatch: status={status!r}, returncode={process_returncode}, expected={expected_code}"
                )
            if raw.get("runtime_phase") != "GAMEPLAY_COMPLETE":
                blockers.append("runtime result does not identify completed gameplay phase")
        elif status == "BLOCKED/NOT TESTABLE":
            if process_returncode != 2:
                blockers.append(
                    f"blocked result/exit mismatch: returncode={process_returncode}, expected=2"
                )
            blockers.append("runner reported a pre-physics or internal blocked result")
        else:
            blockers.append("runtime result status is not PASS, FAIL, or BLOCKED/NOT TESTABLE")
        if raw.get("process_exit_contract_id") != RESULT_CONTRACT_ID:
            blockers.append("runtime result exit-contract ID mismatch")
        if int(raw.get("physics_ticks", 0)) <= 0:
            blockers.append("runtime result reports no positive gameplay physics tick count")
        if not isinstance(raw.get("failures"), list):
            blockers.append("runtime result lacks a failures array")
        terminal = raw.get("terminal_evidence")
        if not isinstance(terminal, dict):
            blockers.append("runtime result lacks terminal-evidence structure")
        else:
            if terminal.get("sealed_before_result") is not True:
                blockers.append("runtime result was not emitted after terminal evidence sealing")
            if int(terminal.get("post_result_event_count", -1)) != 0:
                blockers.append("runtime result reports post-result telemetry")
            if int(terminal.get("result_count", -1)) != 1:
                blockers.append("runtime result count is not exactly one")
    else:
        status = None
    if len(parsed.pre_result_events) <= 0:
        blockers.append("zero telemetry/event records before runtime result")
    if parsed.post_result_events:
        blockers.append(f"{len(parsed.post_result_events)} telemetry/event record(s) appeared after runtime result")
    executed = not blockers
    if executed:
        classification_status = str(raw["status"])
        return {
            "schema": "district_zero.p1a.v1_2_5.suite_classification.v1",
            "id": requested_vector_id,
            "status": classification_status,
            "gameplay_physics_executed": True,
            "runtime_result_record_present": True,
            "process_returncode": process_returncode,
            "expected_process_returncode": 0 if classification_status == "PASS" else 1,
            "event_record_count_before_result": len(parsed.pre_result_events),
            "post_result_event_count": 0,
            "raw_runtime_result_status": classification_status,
            "raw_runtime_result_preserved_unmodified": True,
            "failure_list": list(raw.get("failures", [])),
            "classification_basis": "Valid gameplay result using PASS/0 or FAIL/1 contract.",
            "blockers": [],
        }
    return {
        "schema": "district_zero.p1a.v1_2_5.suite_classification.v1",
        "id": requested_vector_id,
        "status": "BLOCKED/NOT TESTABLE",
        "gameplay_physics_executed": False,
        "runtime_result_record_present": raw is not None,
        "process_returncode": process_returncode,
        "expected_process_returncode": None,
        "event_record_count_before_result": len(parsed.pre_result_events),
        "post_result_event_count": len(parsed.post_result_events),
        "raw_runtime_result_status": raw.get("status") if raw else None,
        "raw_runtime_result_preserved_unmodified": raw is not None,
        "failure_list": [],
        "classification_basis": "Gameplay execution is not creditable because one or more launch/result/evidence invariants failed.",
        "blockers": blockers,
        "launch_error_lines": launch_error_lines,
    }


def validate_import_preflight_record(path: pathlib.Path) -> tuple[bool, list[str], dict[str, Any] | None]:
    errors: list[str] = []
    if not path.is_file():
        return False, ["composite preflight record is absent"], None
    try:
        record = load_json(path)
    except Exception as exc:
        return False, [f"composite preflight record unreadable: {exc}"], None
    if record.get("schema") != "district_zero.p1a.v1_2_4j.disposable_import_result.v1":
        errors.append("preflight schema mismatch")
    if record.get("status") != "PASS" or record.get("explicit_import_result") != "PASS":
        errors.append("preflight status is not PASS")
    if pathlib.Path(str(record.get("project_root", ""))).resolve() != ROOT.resolve():
        errors.append("preflight project root differs from runtime suite root")
    if record.get("required_godot_version") != EXACT_VERSION or record.get("observed_godot_version") != EXACT_VERSION:
        errors.append("preflight exact-engine identity mismatch")
    if record.get("class_cache_generated") is not True:
        errors.append("registered-class cache was not generated")
    if sorted(record.get("required_classes_verified", [])) != REQUIRED_CLASSES:
        errors.append("required registered-class set mismatch")
    if record.get("registered_project_scripts_parse_confirmed") is not True:
        errors.append("registered scripts were not parse-confirmed")
    if record.get("runtime_runner_parse_confirmed") is not True:
        errors.append("actual runtime runner was not parse-confirmed")
    if record.get("required_project_scripts_parse_confirmed") is not True:
        errors.append("complete required script set was not parse-confirmed")
    if int(record.get("parse_or_import_error_count", -1)) != 0:
        errors.append("preflight reports parse/import errors")
    expected_runner = ROOT / "tests" / "p1a_runtime_runner.gd"
    if record.get("runtime_runner_target_resource_path") != "res://tests/p1a_runtime_runner.gd":
        errors.append("runtime-runner target mismatch")
    if record.get("runtime_runner_sha256") != sha256(expected_runner):
        errors.append("runtime-runner hash mismatch")
    if int(record.get("runtime_runner_parse_process_returncode", -1)) != 0:
        errors.append("runtime-runner parse process did not return zero")
    if int(record.get("runtime_runner_parse_error_count", -1)) != 0:
        errors.append("runtime-runner parse preflight reports errors")
    return not errors, errors, record


def select_vector_ids(fixture: dict[str, Any], only: list[str], fast_gate: bool) -> list[str]:
    all_ids = [str(v["id"]) for v in fixture["vectors"]]
    if only:
        missing = [v for v in only if v not in all_ids]
        if missing:
            raise ValueError(f"unknown vector ID(s): {missing}")
        return only
    if fast_gate:
        return list(FAST_IDS)
    return all_ids


def resolve_selected_human_traces(path_value: str | None) -> tuple[dict[str, pathlib.Path], list[str]]:
    errors: list[str] = []
    if not path_value:
        return {}, ["--selected-trace-manifest is required for A1/A2/X0"]
    path = pathlib.Path(path_value).resolve()
    try:
        manifest = load_json(path)
    except Exception as exc:
        return {}, [f"selected trace manifest unreadable: {exc}"]
    if manifest.get("schema") != "district_zero.p1a.selected_human_trace_manifest.v1" or manifest.get("authority_version") != "v1.2.5" or manifest.get("selection_complete") is not True:
        errors.append("selected trace manifest schema/authority/completion mismatch")
    if manifest.get("engine_identity") != EXACT_VERSION:
        errors.append("selected trace manifest engine mismatch")
    routes = manifest.get("routes", {})
    resolved: dict[str, pathlib.Path] = {}
    for route in ("A1", "A2", "X0"):
        record = routes.get(route, {}) if isinstance(routes, dict) else {}
        trace = pathlib.Path(str(record.get("input_trace_path", ""))).resolve()
        if record.get("status") != "PASS" or not trace.is_file():
            errors.append(f"{route} selected input trace absent/not PASS")
            continue
        if sha256(trace) != record.get("input_trace_sha256"):
            errors.append(f"{route} selected input trace hash mismatch")
            continue
        try:
            trace_value = load_json(trace)
        except Exception as exc:
            errors.append(f"{route} selected input trace unreadable: {exc}")
            continue
        if trace_value.get("route_id") != route or trace_value.get("schema") != "district_zero.p1a.human_input_trace.v1":
            errors.append(f"{route} selected input trace identity mismatch")
            continue
        resolved[route] = trace
    return resolved, errors


def vector_by_id(fixture: dict[str, Any], vector_id: str) -> dict[str, Any]:
    for vector in fixture["vectors"]:
        if vector.get("id") == vector_id:
            return vector
    raise KeyError(vector_id)


def candidate_ids() -> list[str]:
    registry = load_json(CANDIDATE_PATH)
    return [str(v["id"]) for v in registry.get("candidates", [])]


def write_jsonl(path: pathlib.Path, records: list[dict[str, Any]]) -> None:
    write_text(path, "".join(json.dumps(v, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n" for v in records))


def blocked_report(
    fixture: dict[str, Any], output: pathlib.Path, evidence: pathlib.Path, selected: list[str], blocker: str
) -> int:
    report = {
        "schema": "district_zero.p1a.runtime_suite_result.v1_2_5",
        "execution_overlay_authority_version": EXECUTION_OVERLAY,
        "fixture_authority_version": FIXTURE_AUTHORITY,
        "v7_algorithm_authority_version": V7_ALGORITHM_AUTHORITY,
        "world_data_authority_version": WORLD_AUTHORITY,
        "status": "BLOCKED/NOT TESTABLE",
        "required_godot_version": EXACT_VERSION,
        "selected_vector_ids": selected,
        "attempted_vector_count": 0,
        "executed_vector_count": 0,
        "pass_count": 0,
        "fail_count": 0,
        "blocked_count": len(selected),
        "results": [],
        "blocker": blocker,
        "human_world_gate": "NOT PERFORMED",
        "P1B": "FROZEN",
    }
    dump(output, report)
    dump(evidence / "runtime_vector_results.json", report)
    checksum_inventory(evidence)
    print(json.dumps(report, sort_keys=True))
    return 2


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--godot", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--evidence-dir", required=True)
    parser.add_argument("--only", action="append", default=[])
    parser.add_argument("--fast-route-gate", action="store_true")
    parser.add_argument("--fail-fast-on-vector-failure", action="store_true")
    parser.add_argument("--hop-offset-m", type=float)
    parser.add_argument("--v7-candidate-id")
    parser.add_argument("--selected-trace-manifest")
    parser.add_argument("--standalone-evidence-zip")
    parser.add_argument("--import-preflight-record", required=True)
    args = parser.parse_args()

    fixture = load_json(FIXTURE_PATH)
    output = pathlib.Path(args.output).resolve()
    evidence = pathlib.Path(args.evidence_dir).resolve()
    if evidence.exists():
        shutil.rmtree(evidence)
    evidence.mkdir(parents=True)
    try:
        selected = select_vector_ids(fixture, args.only, args.fast_route_gate)
    except ValueError as exc:
        return blocked_report(fixture, output, evidence, [], str(exc))

    preflight_path = pathlib.Path(args.import_preflight_record).resolve()
    preflight_ok, preflight_errors, _ = validate_import_preflight_record(preflight_path)
    if not preflight_ok:
        return blocked_report(fixture, output, evidence, selected, "composite import/runner-parse preflight rejected: " + "; ".join(preflight_errors))

    try:
        version_process = subprocess.run([args.godot, "--version"], capture_output=True, text=True, check=False)
    except OSError as exc:
        return blocked_report(fixture, output, evidence, selected, f"exact Godot unavailable: {exc}")
    observed_version = version_process.stdout.strip()
    if observed_version != EXACT_VERSION or observed_version != fixture.get("required_godot_version"):
        return blocked_report(fixture, output, evidence, selected, f"exact Godot version mismatch: {observed_version!r}")

    v7_ids = set(candidate_ids())
    selected_v7 = [v for v in selected if vector_by_id(fixture, v).get("controller_commands", {}).get("type") == V7_CONTROLLER]
    if selected_v7 and args.v7_candidate_id not in v7_ids:
        return blocked_report(fixture, output, evidence, selected, "V7 vector selected without a valid preregistered --v7-candidate-id")
    selected_human = [v for v in selected if vector_by_id(fixture, v).get("controller_commands", {}).get("type") == HUMAN_CONTROLLER]
    trace_paths: dict[str, pathlib.Path] = {}
    if selected_human:
        trace_paths, trace_errors = resolve_selected_human_traces(args.selected_trace_manifest)
        if trace_errors:
            return blocked_report(fixture, output, evidence, selected, "selected human trace manifest rejected: " + "; ".join(trace_errors))

    dump(
        evidence / "suite_argv.json",
        {
            "argv": sys.argv,
            "cwd": str(ROOT),
            "selected_vector_ids": selected,
            "v7_candidate_id": args.v7_candidate_id,
            "selected_trace_manifest": args.selected_trace_manifest,
            "fail_fast_on_vector_failure": args.fail_fast_on_vector_failure,
            "import_preflight_record": str(preflight_path),
            "import_preflight_record_sha256": sha256(preflight_path),
        },
    )
    dump(evidence / "engine_identity.json", {"required": EXACT_VERSION, "observed": observed_version, "match": True})

    results: list[dict[str, Any]] = []
    attempted = 0
    executed = 0
    for ordinal, vector_id in enumerate(selected, 1):
        attempted += 1
        directory = evidence / vector_id
        directory.mkdir(parents=True)
        engine_path = directory / "engine.txt"
        cmd = [
            args.godot,
            "--headless",
            "--log-file",
            str(engine_path),
            "--path",
            str(ROOT),
            "--fixed-fps",
            "60",
            "--script",
            "res://tests/p1a_runtime_runner.gd",
            "--",
            "--vector",
            vector_id,
        ]
        vector = vector_by_id(fixture, vector_id)
        if vector.get("controller_commands", {}).get("type") == V7_CONTROLLER:
            cmd += ["--v7-candidate-id", str(args.v7_candidate_id)]
        if vector.get("controller_commands", {}).get("type") == HUMAN_CONTROLLER:
            route_id = str(vector.get("controller_commands", {}).get("route_id", ""))
            cmd += ["--input-trace", str(trace_paths[route_id])]
        if vector_id == "RT_HOP_SUCCESS" and args.hop_offset_m is not None:
            cmd += ["--hop-offset-m", format(args.hop_offset_m, ".12g")]
        dump(
            directory / "argv.json",
            {
                "argv": cmd,
                "cwd": str(ROOT),
                "required_godot_version": EXACT_VERSION,
                "execution_overlay_authority_version": EXECUTION_OVERLAY,
                "fixture_authority_version": FIXTURE_AUTHORITY,
                "world_data_authority_version": WORLD_AUTHORITY,
                "import_preflight_record": str(preflight_path),
                "v7_candidate_id": args.v7_candidate_id if vector_id in selected_v7 else None,
                "selected_input_trace": str(trace_paths[str(vector.get("controller_commands", {}).get("route_id", ""))]) if vector_id in selected_human else None,
            },
        )
        completed = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, check=False)
        write_text(directory / "stdout.txt", completed.stdout)
        write_text(directory / "stderr.txt", completed.stderr)
        if not engine_path.exists():
            write_text(engine_path, "")
        parsed = parse_runner_stdout(completed.stdout)
        write_text(directory / "runtime_result_line.txt", (parsed.raw_result_lines[0] + "\n") if len(parsed.raw_result_lines) == 1 else "")
        raw_result = parsed.raw_results[0] if len(parsed.raw_results) == 1 else {
            "status": "ABSENT_OR_INVALID",
            "raw_result_line_count": len(parsed.raw_result_lines),
            "valid_raw_result_count": len(parsed.raw_results),
        }
        dump(directory / "runtime_result.json", raw_result)
        write_jsonl(directory / "events.jsonl", parsed.pre_result_events)
        write_jsonl(directory / "post_result_events.jsonl", parsed.post_result_events)
        launch_errors = scan_launch_errors((completed.stdout, completed.stderr, engine_path.read_text(encoding="utf-8", errors="replace")))
        classification = classify_runtime_attempt(
            requested_vector_id=vector_id,
            process_returncode=completed.returncode,
            parsed=parsed,
            launch_error_lines=launch_errors,
            import_preflight_passed=True,
        )
        classification.update(
            {
                "stdout_sha256": sha256(directory / "stdout.txt"),
                "stderr_sha256": sha256(directory / "stderr.txt"),
                "engine_log_sha256": sha256(engine_path),
                "runtime_result_line_sha256": sha256(directory / "runtime_result_line.txt"),
                "runtime_result_sha256": sha256(directory / "runtime_result.json"),
                "events_sha256": sha256(directory / "events.jsonl"),
                "post_result_events_sha256": sha256(directory / "post_result_events.jsonl"),
                "v7_candidate_id": args.v7_candidate_id if vector.get("controller_commands", {}).get("type") == V7_CONTROLLER else None,
                "human_trace_id": raw_result.get("human_trace_id") if vector.get("controller_commands", {}).get("type") == HUMAN_CONTROLLER else None,
            }
        )
        dump(directory / "suite_classification.json", classification)
        dump(directory / "result.json", classification)
        checksum_inventory(directory)
        results.append(classification)
        if classification["gameplay_physics_executed"]:
            executed += 1
        print(f"[{ordinal:02d}/{len(selected):02d}] {vector_id}: {classification['status']}", flush=True)
        if classification["status"] == "BLOCKED/NOT TESTABLE" or (
            args.fail_fast_on_vector_failure and classification["status"] == "FAIL"
        ):
            break

    pass_count = sum(r["status"] == "PASS" for r in results)
    fail_count = sum(r["status"] == "FAIL" for r in results)
    blocked_count = sum(r["status"] == "BLOCKED/NOT TESTABLE" for r in results)
    all_attempted = len(results) == len(selected)
    if blocked_count:
        status = "BLOCKED/NOT TESTABLE"
    elif all_attempted and fail_count == 0:
        status = "PASS" if len(selected) == len(fixture["vectors"]) else "ISOLATED_PASS"
    else:
        status = "FAIL" if len(selected) == len(fixture["vectors"]) else "ISOLATED_FAIL"
    report = {
        "schema": "district_zero.p1a.runtime_suite_result.v1_2_5",
        "execution_overlay_authority_version": EXECUTION_OVERLAY,
        "fixture_authority_version": FIXTURE_AUTHORITY,
        "v7_algorithm_authority_version": V7_ALGORITHM_AUTHORITY,
        "world_data_authority_version": WORLD_AUTHORITY,
        "status": status,
        "run_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "required_godot_version": EXACT_VERSION,
        "godot_version": observed_version,
        "required_vector_count": len(fixture["vectors"]),
        "selected_vector_ids": selected,
        "v7_candidate_id": args.v7_candidate_id,
        "selected_trace_manifest": args.selected_trace_manifest,
        "attempted_vector_count": attempted,
        "executed_vector_count": executed,
        "pass_count": pass_count,
        "fail_count": fail_count,
        "blocked_count": blocked_count,
        "results": results,
        "human_world_gate": "NOT PERFORMED",
        "P1B": "FROZEN",
    }
    dump(output, report)
    dump(evidence / "runtime_vector_results.json", report)
    checksum_inventory(evidence)
    if args.standalone_evidence_zip:
        zip_path = pathlib.Path(args.standalone_evidence_zip).resolve()
        deterministic_zip(evidence, zip_path)
        with zipfile.ZipFile(zip_path) as archive:
            if archive.testzip() is not None:
                raise RuntimeError("standalone evidence ZIP failed structural validation")
    print(json.dumps({"status": status, "pass": pass_count, "fail": fail_count, "blocked": blocked_count, "report": str(output), "evidence_root": str(evidence)}, sort_keys=True))
    if blocked_count:
        return 2
    return 0 if fail_count == 0 and all_attempted else 1


if __name__ == "__main__":
    raise SystemExit(main())
