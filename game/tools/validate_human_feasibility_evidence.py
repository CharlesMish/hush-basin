#!/usr/bin/env python3
"""Validate and finalize District Zero P1A v1.2.5 human capture evidence."""
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import re
import sys
from typing import Any

ROOT = pathlib.Path(__file__).resolve().parents[1]
EXACT = "4.7.1.stable.official.a13da4feb"
ROUTES = ("A1", "A2", "X0")
ATTEMPT_FILES = {
    "argv.json", "engine_identity.json", "project_identity.json", "input_trace.json",
    "telemetry.json", "state_trace.json", "attempt_result.json", "stdout.txt",
    "stderr.txt", "engine.txt", "SHA256SUMS.txt",
}
REPLAY_FILES = (ATTEMPT_FILES - {"attempt_result.json"}) | {"replay_result.json"}
EVENT_NAMES = {"ROUTE_STATE", "COLLISION_SAMPLE", "RESET", "SURFACE_CLASS_CHANGED"}


def load(path: pathlib.Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} is not a JSON object")
    return value


def dump(path: pathlib.Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")


def canonical_bytes(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True) + "\n").encode("utf-8")


def sha(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def checksum_inventory(directory: pathlib.Path) -> int:
    paths = sorted(
        (p for p in directory.rglob("*") if p.is_file() and p.name != "SHA256SUMS.txt"),
        key=lambda p: p.relative_to(directory).as_posix().encode("utf-8"),
    )
    rows = [f"{sha(path)}  {path.relative_to(directory).as_posix()}\n" for path in paths]
    (directory / "SHA256SUMS.txt").write_text("".join(rows), encoding="utf-8", newline="\n")
    return len(paths)


def verify_inventory(directory: pathlib.Path) -> list[str]:
    errors: list[str] = []
    inventory = directory / "SHA256SUMS.txt"
    if not inventory.is_file():
        return ["SHA256SUMS.txt absent"]
    expected: set[str] = set()
    for line in inventory.read_text(encoding="utf-8").splitlines():
        match = re.fullmatch(r"([0-9a-f]{64})  (.+)", line)
        if not match:
            errors.append(f"malformed checksum row: {line}")
            continue
        digest, relative = match.groups()
        if relative in expected:
            errors.append(f"duplicate checksum path: {relative}")
            continue
        expected.add(relative)
        target = directory / relative
        if not target.is_file():
            errors.append(f"missing checksummed file: {relative}")
        elif sha(target) != digest:
            errors.append(f"checksum mismatch: {relative}")
    actual = {p.relative_to(directory).as_posix() for p in directory.rglob("*") if p.is_file() and p.name != "SHA256SUMS.txt"}
    if expected != actual:
        errors.append("checksum inventory path set mismatch")
    return errors


def protocol() -> dict[str, Any]:
    return load(ROOT / "tests/fixtures/human_feasibility_protocol.json")


def validate_canonical_trace(path: pathlib.Path, *, state: bool) -> tuple[dict[str, Any], list[str]]:
    errors: list[str] = []
    try:
        value = load(path)
    except Exception as exc:
        return {}, [str(exc)]
    if path.read_bytes() != canonical_bytes(value):
        errors.append(f"{path.name} is not canonical compact sorted UTF-8 JSON with LF")
    expected_schema = "district_zero.p1a.human_state_trace.v1" if state else "district_zero.p1a.human_input_trace.v1"
    if value.get("schema") != expected_schema or value.get("authority_version") != "v1.2.5":
        errors.append(f"{path.name} schema/authority mismatch")
    if value.get("route_id") not in ROUTES or not isinstance(value.get("records"), list) or not value.get("records"):
        errors.append(f"{path.name} route/records invalid")
        return value, errors
    for index, record in enumerate(value["records"]):
        if not isinstance(record, dict) or record.get("vector_tick") != index or record.get("physics_tick") != index + 1:
            errors.append(f"{path.name} tick sequence is not contiguous at index {index}")
            break
        if not state:
            for key, low, high in (("throttle_u16", 0, 65535), ("brake_u16", 0, 65535), ("steer_i16", -32767, 32767)):
                raw = record.get(key)
                if isinstance(raw, bool) or not isinstance(raw, int) or not low <= raw <= high:
                    errors.append(f"{path.name} invalid {key} at index {index}")
    return value, errors


def route_metric_errors(route: str, result: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    spec = protocol()["route_specs"][route]
    metrics = result.get("metrics", {})
    if metrics.get("entered") is not True:
        errors.append("genuine ENTERED absent")
    if metrics.get("traversed") is not True:
        errors.append("genuine TRAVERSED absent")
    if float(metrics.get("genuine_distance_m", 0.0)) + 1e-6 < float(spec["genuine_distance_m"]):
        errors.append("genuine distance minimum not met")
    if float(metrics.get("fast_distance_m", 0.0)) + 1e-6 < float(spec["fast_distance_m"]):
        errors.append("fast distance minimum not met")
    if float(metrics.get("maximum_lateral_distance_m", float("inf"))) > float(spec["lateral_limit_m"]) + 1e-6:
        errors.append("lateral maximum exceeded")
    if int(metrics.get("hard_collision_count", -1)) != 0:
        errors.append("non-Hop hard collision count is not zero")
    if int(metrics.get("fall_reset_count", -1)) != 0:
        errors.append("fall/reset count is not zero")
    if int(metrics.get("prohibited_input_count", -1)) != 0:
        errors.append("prohibited input count is not zero")
    if int(metrics.get("post_result_event_count", -1)) != 0:
        errors.append("post-result event count is not zero")
    return errors


def _identity_errors(directory: pathlib.Path) -> list[str]:
    errors: list[str] = []
    engine = load(directory / "engine_identity.json")
    if engine.get("observed") != EXACT or engine.get("required") != EXACT or engine.get("match") is not True:
        errors.append("engine identity mismatch")
    project = load(directory / "project_identity.json")
    telemetry = load(directory / "telemetry.json")
    if telemetry.get("engine_identity") != EXACT or telemetry.get("project_identity") != project:
        errors.append("telemetry identity mismatch")
    return errors


def finalize_attempt(directory: pathlib.Path) -> dict[str, Any]:
    input_trace, input_errors = validate_canonical_trace(directory / "input_trace.json", state=False)
    state_trace, state_errors = validate_canonical_trace(directory / "state_trace.json", state=True)
    provisional = load(directory / "attempt_result.json")
    route = str(provisional.get("route_id", ""))
    errors = input_errors + state_errors + _identity_errors(directory)
    records = input_trace.get("records", [])
    if provisional.get("status") == "PASS":
        errors += route_metric_errors(route, provisional)
        if any(record.get("hop_pressed") is not False or record.get("transform_pressed") is not True for record in records):
            errors.append("passing trace contains ineligible Hop/transform state")
    if state_trace.get("route_id") != route or input_trace.get("route_id") != route:
        errors.append("attempt route identity mismatch")
    telemetry = load(directory / "telemetry.json")
    if len(records) != len(telemetry.get("records", [])) or len(records) != len(state_trace.get("records", [])):
        errors.append("attempt trace lengths differ")
    hashes = {
        "engine_log_sha256": sha(directory / "engine.txt"),
        "input_trace_sha256": sha(directory / "input_trace.json"),
        "state_trace_sha256": sha(directory / "state_trace.json"),
        "stderr_sha256": sha(directory / "stderr.txt"),
        "stdout_sha256": sha(directory / "stdout.txt"),
        "telemetry_sha256": sha(directory / "telemetry.json"),
    }
    status = str(provisional.get("status", "BLOCKED/NOT TESTABLE"))
    failures = list(provisional.get("failures", []))
    if errors:
        failures.extend(errors)
        if status == "PASS":
            status = "BLOCKED/NOT TESTABLE"
    result = {
        "schema": "district_zero.p1a.human_capture_attempt_result.v1",
        "authority_version": "v1.2.5",
        "trace_id": str(provisional.get("trace_id", "")),
        "route_id": route,
        "attempt_index": int(provisional.get("attempt_index", 0)),
        "status": status,
        "metrics": provisional.get("metrics", {}),
        "failures": failures,
        "evidence_hashes": hashes,
    }
    dump(directory / "attempt_result.json", result)
    checksum_inventory(directory)
    result["inventory_errors"] = verify_inventory(directory)
    result["evidence_valid"] = not errors and not result["inventory_errors"]
    return result


def _event_sequence(telemetry: dict[str, Any]) -> list[dict[str, Any]]:
    sequence: list[dict[str, Any]] = []
    for event in telemetry.get("events", []):
        if isinstance(event, dict) and event.get("event") in EVENT_NAMES:
            sequence.append({key: value for key, value in event.items() if key not in {"serial", "physics_tick"}})
    return sequence


def _raw_deltas(capture: dict[str, Any], replay: dict[str, Any]) -> dict[str, float]:
    names = {"position_m": 0.0, "velocity_mps": 0.0, "yaw_rad": 0.0, "fold": 0.0, "chainage_m": 0.0, "lateral_m": 0.0, "fast_distance_m": 0.0}
    cap_records = capture.get("records", [])
    rep_records = replay.get("records", [])
    if len(cap_records) != len(rep_records):
        # Keep terminal evidence strict JSON even on a structurally invalid replay.
        return {key: 1.0e99 for key in names}
    for a, b in zip(cap_records, rep_records):
        names["position_m"] = max(names["position_m"], *(abs(float(x) - float(y)) for x, y in zip(a["position_xyz_m"], b["position_xyz_m"])))
        names["velocity_mps"] = max(names["velocity_mps"], *(abs(float(x) - float(y)) for x, y in zip(a["velocity_xyz_mps"], b["velocity_xyz_mps"])))
        names["yaw_rad"] = max(names["yaw_rad"], abs(float(a["yaw_rad"]) - float(b["yaw_rad"])))
        names["fold"] = max(names["fold"], abs(float(a["fold"]) - float(b["fold"])))
        names["chainage_m"] = max(names["chainage_m"], abs(float(a["route_chainage_m"]) - float(b["route_chainage_m"])))
        names["lateral_m"] = max(names["lateral_m"], abs(float(a["route_lateral_distance_m"]) - float(b["route_lateral_distance_m"])))
        names["fast_distance_m"] = max(names["fast_distance_m"], abs(float(a["fast_distance_m"]) - float(b["fast_distance_m"])))
    return names


def finalize_replay(directory: pathlib.Path, capture_directory: pathlib.Path) -> dict[str, Any]:
    provisional = load(directory / "replay_result.json")
    capture_result = load(capture_directory / "attempt_result.json")
    replay_state, state_errors = validate_canonical_trace(directory / "state_trace.json", state=True)
    replay_input, input_errors = validate_canonical_trace(directory / "input_trace.json", state=False)
    errors = state_errors + input_errors + _identity_errors(directory)
    capture_telemetry = load(capture_directory / "telemetry.json")
    replay_telemetry = load(directory / "telemetry.json")
    deltas = _raw_deltas(capture_telemetry, replay_telemetry)
    limits = protocol()["replay"]["raw_delta_limits"]
    limit_map = {"position_m": "position_m", "velocity_mps": "velocity_mps", "yaw_rad": "yaw_rad", "fold": "fold", "chainage_m": "chainage_m", "lateral_m": "lateral_m", "fast_distance_m": "fast_distance_m"}
    all_limits = all(deltas[key] <= float(limits[value]) for key, value in limit_map.items())
    input_match = (directory / "input_trace.json").read_bytes() == (capture_directory / "input_trace.json").read_bytes()
    state_match = sha(directory / "state_trace.json") == sha(capture_directory / "state_trace.json")
    termination_match = provisional.get("route_metrics_pass") is True and int(replay_telemetry.get("summary", {}).get("termination_tick", -1)) == int(capture_result.get("metrics", {}).get("termination_tick", -2))
    event_match = _event_sequence(capture_telemetry) == _event_sequence(replay_telemetry)
    metrics_errors = route_metric_errors(str(provisional.get("route_id", "")), {"metrics": replay_telemetry.get("summary", {})})
    route_pass = not metrics_errors and provisional.get("route_metrics_pass") is True
    determinism = {
        "input_trace_sha256_match": input_match,
        "canonical_state_trace_sha256_match": state_match,
        "termination_tick_match": termination_match,
        "event_sequence_match": event_match,
        "maximum_raw_deltas": deltas,
        "all_limits_pass": all_limits,
    }
    if not input_match: errors.append("input trace raw bytes differ from capture")
    if not state_match: errors.append("canonical state trace SHA differs from capture")
    if not termination_match: errors.append("termination tick differs from capture")
    if not event_match: errors.append("route/collision/reset/surface event sequence differs")
    if not all_limits: errors.append("raw replay delta limit exceeded")
    errors += metrics_errors
    result = {
        "schema": "district_zero.p1a.human_replay_result.v1",
        "authority_version": "v1.2.5",
        "trace_id": str(provisional.get("trace_id", "")),
        "route_id": str(provisional.get("route_id", "")),
        "replay_index": int(provisional.get("replay_index", 0)),
        "status": "PASS" if route_pass and not errors else ("FAIL" if provisional.get("status") != "BLOCKED/NOT TESTABLE" else "BLOCKED/NOT TESTABLE"),
        "route_metrics_pass": route_pass,
        "determinism": determinism,
        "evidence_hashes": {
            "input_trace_sha256": sha(directory / "input_trace.json"),
            "telemetry_sha256": sha(directory / "telemetry.json"),
            "state_trace_sha256": sha(directory / "state_trace.json"),
        },
    }
    dump(directory / "replay_result.json", result)
    checksum_inventory(directory)
    result["validation_errors"] = errors + verify_inventory(directory)
    return result


def validate_session(session_root: pathlib.Path) -> dict[str, Any]:
    errors: list[str] = []
    for route in ROUTES:
        selected = session_root / "routes" / route / "selected_trace.json"
        if selected.exists():
            record = load(selected)
            capture = session_root / str(record.get("capture_directory", ""))
            if not capture.is_dir() or load(capture / "attempt_result.json").get("status") != "PASS":
                errors.append(f"{route} selected capture invalid")
    return {"schema": "district_zero.p1a.human_session_validation.v1", "status": "PASS" if not errors else "FAIL", "errors": errors}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--kind", choices=("attempt", "replay", "session"), required=True)
    parser.add_argument("--evidence-dir")
    parser.add_argument("--capture-dir")
    parser.add_argument("--session-root")
    args = parser.parse_args()
    try:
        if args.kind == "attempt":
            result = finalize_attempt(pathlib.Path(args.evidence_dir).resolve())
        elif args.kind == "replay":
            result = finalize_replay(pathlib.Path(args.evidence_dir).resolve(), pathlib.Path(args.capture_dir).resolve())
        else:
            result = validate_session(pathlib.Path(args.session_root).resolve())
    except Exception as exc:
        result = {"status": "BLOCKED/NOT TESTABLE", "error": str(exc)}
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result.get("status") == "PASS" or result.get("evidence_valid") is True else (1 if result.get("status") in {"FAIL", "ABORTED"} else 2)


if __name__ == "__main__":
    raise SystemExit(main())
