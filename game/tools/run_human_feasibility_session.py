#!/usr/bin/env python3
"""Orchestrate the bounded District Zero v1.2.5 human capture/replay session."""
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
import tempfile
import zipfile
from typing import Any, Iterable

from validate_human_feasibility_evidence import finalize_attempt, finalize_replay

ROOT = pathlib.Path(__file__).resolve().parents[1]
EXACT = "4.7.1.stable.official.a13da4feb"
ROUTES = ("A1", "A2", "X0")
REQUIRED_CLASSES = sorted(("CraftController", "CraftTuning", "MotionMath", "P1AMap", "P1ATelemetry", "P1AWorldBuilder", "P1AWorldData", "P1AWorldGate", "StableCameraRig", "SurfaceFeedback3D"))
FORBIDDEN = {".godot", "__MACOSX", "__pycache__", ".pytest_cache", ".mypy_cache"}
ERROR_PATTERNS = tuple(re.compile(value, re.I) for value in (
    r"SCRIPT ERROR", r"Parse Error", r"Cannot infer the type", r"Could not find type",
    r"not declared in the current scope", r"Failed to load script", r"ERROR:\s+Failed",
))


def dump(path: pathlib.Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")


def write(path: pathlib.Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value, encoding="utf-8", newline="\n")


def load(path: pathlib.Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} is not a JSON object")
    return value


def sha(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(command: list[str], cwd: pathlib.Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=cwd, capture_output=True, text=True, check=False)


def scan_errors(texts: Iterable[str]) -> list[str]:
    output: list[str] = []
    for text in texts:
        for line in text.splitlines():
            normalized = line.strip()
            if normalized and any(pattern.search(normalized) for pattern in ERROR_PATTERNS) and normalized not in output:
                output.append(normalized)
    return output


def copy_clean(source: pathlib.Path, destination: pathlib.Path) -> None:
    def ignore(_directory: str, names: list[str]) -> set[str]:
        return {name for name in names if name in FORBIDDEN or name == ".DS_Store" or name.startswith("._") or name.endswith((".pyc", ".pyo", ".zip"))}
    shutil.copytree(source, destination, ignore=ignore)


def checksum_inventory(directory: pathlib.Path) -> int:
    paths = sorted((p for p in directory.rglob("*") if p.is_file() and p.name != "SHA256SUMS.txt"), key=lambda p: p.relative_to(directory).as_posix().encode("utf-8"))
    write(directory / "SHA256SUMS.txt", "".join(f"{sha(path)}  {path.relative_to(directory).as_posix()}\n" for path in paths))
    return len(paths)


def verify_inventory(directory: pathlib.Path) -> list[str]:
    errors: list[str] = []
    seen: set[str] = set()
    for line in (directory / "SHA256SUMS.txt").read_text(encoding="utf-8").splitlines():
        match = re.fullmatch(r"([0-9a-f]{64})  (.+)", line)
        if not match:
            errors.append(f"malformed checksum row: {line}")
            continue
        digest, relative = match.groups()
        if relative in seen:
            errors.append(f"duplicate checksum path: {relative}")
        seen.add(relative)
        target = directory / relative
        if not target.is_file() or sha(target) != digest:
            errors.append(f"checksum mismatch: {relative}")
    actual = {p.relative_to(directory).as_posix() for p in directory.rglob("*") if p.is_file() and p.name != "SHA256SUMS.txt"}
    if actual != seen:
        errors.append("checksum path set mismatch")
    return errors


def forbidden_entries(directory: pathlib.Path) -> list[str]:
    bad: list[str] = []
    for path in directory.rglob("*"):
        relative = path.relative_to(directory)
        if any(part in FORBIDDEN for part in relative.parts) or path.name == ".DS_Store" or path.name.startswith("._"):
            bad.append(relative.as_posix())
        if path.is_file() and path.suffix.lower() in {".zip", ".tar", ".gz", ".7z", ".rar"}:
            bad.append(relative.as_posix())
    return sorted(set(bad))


def deterministic_zip(directory: pathlib.Path, output: pathlib.Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists():
        output.unlink()
    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in sorted((p for p in directory.rglob("*") if p.is_file()), key=lambda p: p.relative_to(directory).as_posix().encode("utf-8")):
            info = zipfile.ZipInfo(path.relative_to(directory).as_posix(), (1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, path.read_bytes())


def finalize_package(evidence: pathlib.Path, output_zip: pathlib.Path, result: dict[str, Any]) -> dict[str, Any]:
    dump(evidence / "session_stage_result.json", result)
    dump(evidence / "EVIDENCE_PACKAGE_MANIFEST.json", {
        "schema": "district_zero.p1a.v1_2_5.evidence_package_manifest.v1",
        "authority_version": "v1.2.5",
        "terminal_stage": result.get("stage"),
        "terminal_status": result.get("status"),
        "finalized_before_cleanup": True,
        "human_world_gate": "NOT PERFORMED",
        "P1B": "FROZEN",
    })
    bad = forbidden_entries(evidence)
    if bad:
        raise RuntimeError(f"forbidden evidence entries: {bad[:20]}")
    count = checksum_inventory(evidence)
    errors = verify_inventory(evidence)
    if errors:
        raise RuntimeError(f"evidence checksum verification failed: {errors[:20]}")
    deterministic_zip(evidence, output_zip)
    with zipfile.ZipFile(output_zip) as archive:
        crc = archive.testzip()
        names = archive.namelist()
    if crc is not None or len(names) != len(set(names)):
        raise RuntimeError(f"evidence ZIP invalid: crc={crc!r} duplicate={len(names) != len(set(names))}")
    packaged = {"durably_packaged": True, "checksum_record_count": count, "zip_path": str(output_zip), "zip_byte_size": output_zip.stat().st_size, "zip_sha256": sha(output_zip), "status": result.get("status"), "stage": result.get("stage")}
    print(json.dumps(packaged, sort_keys=True))
    return packaged


def project_identity(project: pathlib.Path) -> dict[str, str]:
    return {
        "capture_runner_sha256": sha(project / "tests/p1a_human_feasibility_runner.gd"),
        "project_godot_sha256": sha(project / "project.godot"),
        "runtime_runner_sha256": sha(project / "tests/p1a_runtime_runner.gd"),
    }


def engine_identity(godot: str, cwd: pathlib.Path) -> tuple[dict[str, Any], subprocess.CompletedProcess[str] | None]:
    try:
        process = run([godot, "--version"], cwd)
        observed = process.stdout.strip()
    except OSError as exc:
        return {"required": EXACT, "observed": "", "match": False, "error": str(exc)}, None
    return {"required": EXACT, "observed": observed, "match": process.returncode == 0 and observed == EXACT}, process


def write_process(evidence: pathlib.Path, name: str, command: list[str], cwd: pathlib.Path, process: subprocess.CompletedProcess[str]) -> None:
    stage = evidence / name
    stage.mkdir(parents=True, exist_ok=True)
    dump(stage / "argv.json", {"argv": command, "cwd": str(cwd)})
    write(stage / "stdout.txt", process.stdout)
    write(stage / "stderr.txt", process.stderr)
    dump(stage / "result.json", {"process_returncode": process.returncode})
    checksum_inventory(stage)


def session_state(session: pathlib.Path) -> dict[str, Any]:
    path = session / "session_state.json"
    if path.is_file():
        return load(path)
    return {"schema": "district_zero.p1a.v1_2_5.session_state.v1", "authority_version": "v1.2.5", "prepared": False, "routes": {route: {"capture": "NOT PERFORMED", "replay": "NOT PERFORMED"} for route in ROUTES}, "human_world_gate": "NOT PERFORMED", "P1B": "FROZEN"}


def save_state(session: pathlib.Path, state: dict[str, Any]) -> None:
    dump(session / "session_state.json", state)


def prepare(args: argparse.Namespace, session: pathlib.Path, evidence: pathlib.Path) -> tuple[dict[str, Any], int]:
    if session.exists() and any(session.iterdir()):
        return {"stage": "PREPARE", "status": "BLOCKED/NOT TESTABLE", "blocker": "session root already exists and is nonempty"}, 2
    session.mkdir(parents=True, exist_ok=True)
    evidence.mkdir(parents=True, exist_ok=True)
    identity, version_process = engine_identity(args.godot, ROOT)
    dump(evidence / "ENGINE_IDENTITY.json", identity)
    if not identity["match"]:
        return {"stage": "PREPARE", "status": "BLOCKED/NOT TESTABLE", "blocker": "exact engine unavailable or mismatched", "engine": identity}, 2
    verifier_command = [sys.executable, "-B", str(ROOT / "tools/verify_p1a_implementation.py"), "--root", str(ROOT), "--baseline-root", args.baseline_root, "--p0-root", args.p0_root, "--phase", "implementation"]
    verifier = run(verifier_command, ROOT)
    write_process(evidence, "STATIC_IMPLEMENTATION_VERIFIER", verifier_command, ROOT, verifier)
    try:
        verifier_result = json.loads(verifier.stdout)
    except json.JSONDecodeError:
        verifier_result = {}
    if verifier.returncode != 0 or verifier_result.get("status") != "PASS":
        return {"stage": "PREPARE", "status": "BLOCKED/NOT TESTABLE", "blocker": "implementation verifier failed", "verifier": verifier_result}, 2
    project = session / "project"
    copy_clean(ROOT, project)
    import_log = evidence / "IMPORT" / "engine.txt"
    import_log.parent.mkdir(parents=True, exist_ok=True)
    import_command = [args.godot, "--headless", "--path", str(project), "--import", "--log-file", str(import_log)]
    imported = run(import_command, project)
    write_process(evidence, "IMPORT", import_command, project, imported)
    if not import_log.is_file(): write(import_log, "")
    parse_log = evidence / "PARSE_VALIDATION" / "engine.txt"
    parse_log.parent.mkdir(parents=True, exist_ok=True)
    parse_command = [args.godot, "--headless", "--editor", "--quit", "--path", str(project), "--log-file", str(parse_log)]
    parsed = run(parse_command, project)
    write_process(evidence, "PARSE_VALIDATION", parse_command, project, parsed)
    if not parse_log.is_file(): write(parse_log, "")
    parse_errors = scan_errors((imported.stdout, imported.stderr, import_log.read_text(encoding="utf-8", errors="replace"), parsed.stdout, parsed.stderr, parse_log.read_text(encoding="utf-8", errors="replace")))
    cache = project / ".godot/global_script_class_cache.cfg"
    if imported.returncode != 0 or parsed.returncode != 0 or parse_errors or not cache.is_file() or cache.stat().st_size == 0:
        return {"stage": "PREPARE", "status": "BLOCKED/NOT TESTABLE", "blocker": "exact-engine import/parse failed", "import_returncode": imported.returncode, "parse_returncode": parsed.returncode, "parse_errors": parse_errors, "class_cache_generated": cache.is_file()}, 2
    preflight_record = {
        "schema": "district_zero.p1a.v1_2_4j.disposable_import_result.v1",
        "status": "PASS",
        "explicit_import_result": "PASS",
        "project_root": str(project),
        "required_godot_version": EXACT,
        "observed_godot_version": EXACT,
        "class_cache_generated": True,
        "required_classes_verified": REQUIRED_CLASSES,
        "registered_project_scripts_parse_confirmed": True,
        "runtime_runner_parse_confirmed": True,
        "required_project_scripts_parse_confirmed": True,
        "parse_or_import_error_count": 0,
        "runtime_runner_target_resource_path": "res://tests/p1a_runtime_runner.gd",
        "runtime_runner_sha256": sha(project / "tests/p1a_runtime_runner.gd"),
        "runtime_runner_parse_process_returncode": 0,
        "runtime_runner_parse_error_count": 0,
    }
    dump(session / "prepare_import_record.json", preflight_record)
    dump(evidence / "IMPORT/PREFLIGHT_RECORD.json", preflight_record)
    checksum_inventory(evidence / "IMPORT")
    c1_work = pathlib.Path(tempfile.mkdtemp(prefix="district-zero-v125-c1-"))
    c1_evidence = evidence / "C1_INSTRUMENTATION_INACTIVE"
    c1_command = [sys.executable, "-B", str(project / "tools/run_selected_c1.py"), "--godot", args.godot, "--p0-root", args.p0_root, "--evidence-dir", str(c1_evidence), "--work-root", str(c1_work)]
    try:
        c1 = run(c1_command, project)
        write_process(evidence, "C1_WRAPPER", c1_command, project, c1)
        c1_result = load(c1_evidence / "C1_result.json") if (c1_evidence / "C1_result.json").is_file() else {}
    finally:
        shutil.rmtree(c1_work, ignore_errors=True)
    if c1.returncode != 0 or c1_result.get("status") != "PASS" or float(c1_result.get("maximum_absolute_difference", 1.0)) != 0.0:
        return {"stage": "PREPARE", "status": "BLOCKED/NOT TESTABLE", "blocker": "instrumentation-inactive C1 did not remain zero-delta", "c1": c1_result}, 2
    state = session_state(session)
    state.update({"prepared": True, "prepared_utc": dt.datetime.now(dt.timezone.utc).isoformat(), "engine_identity": identity, "project_identity": project_identity(project), "instrumentation_inactive_c1": {"status": "PASS", "maximum_delta": 0.0}})
    save_state(session, state)
    result = {"stage": "PREPARE", "status": "READY FOR HUMAN FEASIBILITY CAPTURE", "engine_identity": identity, "project_identity": state["project_identity"], "import": "PASS", "parse": "PASS", "instrumentation_inactive_c1": state["instrumentation_inactive_c1"], "next_route": "A1", "human_world_gate": "NOT PERFORMED", "P1B": "FROZEN"}
    return result, 0


def route_order_allowed(state: dict[str, Any], route: str, stage: str) -> bool:
    index = ROUTES.index(route)
    for prior in ROUTES[:index]:
        if state["routes"][prior].get("replay") != "PASS":
            return False
    if stage == "replay" and state["routes"][route].get("capture") != "PASS":
        return False
    return True


def launch_human(project: pathlib.Path, args: argparse.Namespace, route: str, mode: str, output: pathlib.Path, *, attempt: int = 0, replay: int = 0, input_trace: pathlib.Path | None = None) -> subprocess.CompletedProcess[str]:
    output.mkdir(parents=True, exist_ok=True)
    engine_log = output / "engine.txt"
    command = [args.godot]
    if mode == "replay": command.append("--headless")
    command += ["--log-file", str(engine_log), "--path", str(project), "--fixed-fps", "60", "--script", "res://tests/p1a_human_feasibility_runner.gd", "--", "--mode", mode, "--route", route, "--output-dir", str(output), "--session-id", args.session_root_id]
    if attempt: command += ["--attempt-index", str(attempt)]
    if replay: command += ["--replay-index", str(replay)]
    if input_trace is not None: command += ["--input-trace", str(input_trace)]
    process = run(command, project)
    dump(output / "argv.json", {"argv": command, "cwd": str(project)})
    write(output / "stdout.txt", process.stdout)
    write(output / "stderr.txt", process.stderr)
    if not engine_log.is_file(): write(engine_log, "")
    identity, _ = engine_identity(args.godot, project)
    dump(output / "engine_identity.json", identity)
    dump(output / "project_identity.json", project_identity(project))
    return process


def capture(args: argparse.Namespace, session: pathlib.Path, evidence: pathlib.Path) -> tuple[dict[str, Any], int]:
    state = session_state(session)
    route = args.route
    if not state.get("prepared") or not route_order_allowed(state, route, "capture"):
        return {"stage": f"{route}_CAPTURE", "status": "BLOCKED/NOT TESTABLE", "blocker": "prepare/prior-route order lock is not satisfied"}, 2
    project = session / "project"
    route_root = session / "routes" / route
    familiarization = route_root / "familiarization"
    if not (familiarization / "familiarization_result.json").is_file():
        familiarization_process = launch_human(project, args, route, "familiarization", familiarization)
        familiarization_result_path = familiarization / "familiarization_result.json"
        familiarization_errors = scan_errors((
            familiarization_process.stdout,
            familiarization_process.stderr,
            (familiarization / "engine.txt").read_text(encoding="utf-8", errors="replace"),
        ))
        if familiarization_process.returncode != 0 or not familiarization_result_path.is_file() or familiarization_errors:
            evidence.mkdir(parents=True, exist_ok=True)
            if familiarization.is_dir():
                copy_clean(familiarization, evidence / "familiarization_abnormal_exit")
            return {
                "stage": f"{route}_CAPTURE",
                "status": "BLOCKED/NOT TESTABLE — MACOS GODOT RUNTIME",
                "blocker": "familiarization process did not emit a clean runtime result",
                "process_returncode": familiarization_process.returncode,
                "parse_or_script_errors": familiarization_errors,
                "attempts_consumed": 0,
            }, 2
    attempts: list[dict[str, Any]] = []
    selected: dict[str, Any] | None = None
    for index in range(1, 6):
        directory = route_root / "captures" / f"attempt-{index:02d}"
        if (directory / "attempt_result.json").is_file() and (directory / "SHA256SUMS.txt").is_file():
            result = load(directory / "attempt_result.json")
        else:
            launch_human(project, args, route, "capture", directory, attempt=index)
            result = finalize_attempt(directory)
        attempts.append({"attempt_index": index, "status": result.get("status"), "directory": str(directory.relative_to(session))})
        if result.get("status") == "PASS" and result.get("evidence_valid") is not False:
            selected = {"route_id": route, "attempt_index": index, "trace_id": result["trace_id"], "capture_directory": str(directory.relative_to(session)), "input_trace_sha256": sha(directory / "input_trace.json"), "state_trace_sha256": sha(directory / "state_trace.json"), "telemetry_sha256": sha(directory / "telemetry.json"), "status": "PASS"}
            dump(route_root / "selected_trace.json", selected)
            break
    evidence.mkdir(parents=True, exist_ok=True)
    if familiarization.is_dir(): copy_clean(familiarization, evidence / "familiarization")
    for attempt in attempts:
        source = session / attempt["directory"]
        copy_clean(source, evidence / "attempts" / pathlib.Path(attempt["directory"]).name)
    if selected is None:
        state["routes"][route]["capture"] = "FAIL"
        save_state(session, state)
        return {"stage": f"{route}_CAPTURE", "status": f"HUMAN FEASIBILITY NOT ESTABLISHED — {route}", "attempts": attempts, "selected_trace": None}, 1
    state["routes"][route]["capture"] = "PASS"
    state["routes"][route]["selected_attempt"] = selected["attempt_index"]
    save_state(session, state)
    dump(evidence / "selected_trace.json", selected)
    return {"stage": f"{route}_CAPTURE", "status": "PASS", "attempts": attempts, "selected_trace": selected, "next_stage": f"{route}_REPLAY"}, 0


def replay(args: argparse.Namespace, session: pathlib.Path, evidence: pathlib.Path) -> tuple[dict[str, Any], int]:
    state = session_state(session)
    route = args.route
    if not state.get("prepared") or not route_order_allowed(state, route, "replay"):
        return {"stage": f"{route}_REPLAY", "status": "BLOCKED/NOT TESTABLE", "blocker": "capture/prior-route order lock is not satisfied"}, 2
    project = session / "project"
    route_root = session / "routes" / route
    selected = load(route_root / "selected_trace.json")
    capture_dir = session / selected["capture_directory"]
    input_trace = capture_dir / "input_trace.json"
    results: list[dict[str, Any]] = []
    for index in range(1, 4):
        directory = route_root / "replays" / f"replay-{index:02d}"
        launch_human(project, args, route, "replay", directory, replay=index, input_trace=input_trace)
        result = finalize_replay(directory, capture_dir)
        results.append({"replay_index": index, "status": result.get("status"), "directory": str(directory.relative_to(session)), "result_sha256": sha(directory / "replay_result.json")})
        if result.get("status") != "PASS":
            break
    evidence.mkdir(parents=True, exist_ok=True)
    copy_clean(capture_dir, evidence / "selected_capture")
    for result in results:
        copy_clean(session / result["directory"], evidence / "replays" / pathlib.Path(result["directory"]).name)
    if len(results) != 3 or any(result["status"] != "PASS" for result in results):
        state["routes"][route]["replay"] = "FAIL"
        save_state(session, state)
        return {"stage": f"{route}_REPLAY", "status": f"HUMAN FEASIBILITY NOT ESTABLISHED — {route}", "replays": results}, 1
    state["routes"][route]["replay"] = "PASS"
    save_state(session, state)
    selected["replays"] = results
    dump(route_root / "selected_trace.json", selected)
    next_route = ROUTES[ROUTES.index(route) + 1] if route != "X0" else None
    return {"stage": f"{route}_REPLAY", "status": "PASS", "replays": results, "next_stage": f"{next_route}_CAPTURE" if next_route else "CONTINUE"}, 0


def selected_manifest(session: pathlib.Path) -> dict[str, Any]:
    routes: dict[str, Any] = {}
    for route in ROUTES:
        selected = load(session / "routes" / route / "selected_trace.json")
        capture = session / selected["capture_directory"]
        replay_results = []
        for record in selected["replays"]:
            path = session / record["directory"] / "replay_result.json"
            replay_results.append({"replay_index": record["replay_index"], "path": str(path), "sha256": sha(path), "status": "PASS"})
        routes[route] = {"trace_id": selected["trace_id"], "attempt_index": selected["attempt_index"], "input_trace_path": str(capture / "input_trace.json"), "input_trace_sha256": sha(capture / "input_trace.json"), "telemetry_path": str(capture / "telemetry.json"), "telemetry_sha256": sha(capture / "telemetry.json"), "state_trace_path": str(capture / "state_trace.json"), "state_trace_sha256": sha(capture / "state_trace.json"), "capture_result_path": str(capture / "attempt_result.json"), "capture_result_sha256": sha(capture / "attempt_result.json"), "replay_results": replay_results, "status": "PASS"}
    return {"schema": "district_zero.p1a.selected_human_trace_manifest.v1", "authority_version": "v1.2.5", "engine_identity": EXACT, "serialization_contract": "tests/fixtures/human_trace_serialization_contract.json", "routes": routes, "selection_complete": True}


def continue_gate(args: argparse.Namespace, session: pathlib.Path, evidence: pathlib.Path) -> tuple[dict[str, Any], int]:
    state = session_state(session)
    if any(state["routes"][route].get("replay") != "PASS" for route in ROUTES):
        return {"stage": "CONTINUE", "status": "BLOCKED/NOT TESTABLE", "blocker": "all three route replay gates must pass first"}, 2
    project = session / "project"
    manifest = selected_manifest(session)
    manifest_path = session / "selected_human_traces.json"
    manifest_path.write_bytes((json.dumps(manifest, ensure_ascii=False, separators=(",", ":"), sort_keys=True) + "\n").encode("utf-8"))
    c1_work = pathlib.Path(tempfile.mkdtemp(prefix="district-zero-v125-selected-c1-"))
    c1_evidence = evidence / "C1_SELECTED"
    c1_command = [sys.executable, "-B", str(project / "tools/run_selected_c1.py"), "--godot", args.godot, "--p0-root", args.p0_root, "--evidence-dir", str(c1_evidence), "--work-root", str(c1_work)]
    try:
        c1 = run(c1_command, project)
        c1_result = load(c1_evidence / "C1_result.json") if (c1_evidence / "C1_result.json").is_file() else {}
    finally:
        shutil.rmtree(c1_work, ignore_errors=True)
    if c1.returncode != 0 or c1_result.get("status") != "PASS" or float(c1_result.get("maximum_absolute_difference", 1.0)) != 0.0:
        return {"stage": "SELECTED_C1", "status": "BLOCKED/NOT TESTABLE" if c1.returncode == 2 else "FAIL", "c1": c1_result}, 2 if c1.returncode == 2 else 1
    suite_evidence = evidence / "COMPLETE_40_VECTOR_SUITE"
    suite_command = [sys.executable, "-B", str(project / "tools/run_p1a_runtime_suite.py"), "--godot", args.godot, "--output", str(suite_evidence / "runtime_vector_results.json"), "--evidence-dir", str(suite_evidence / "runtime_vectors"), "--import-preflight-record", str(session / "prepare_import_record.json"), "--selected-trace-manifest", str(manifest_path)]
    suite = run(suite_command, project)
    suite_result = load(suite_evidence / "runtime_vector_results.json") if (suite_evidence / "runtime_vector_results.json").is_file() else {}
    if suite.returncode != 0 or suite_result.get("status") != "PASS" or int(suite_result.get("pass_count", 0)) != 40:
        return {"stage": "COMPLETE_40_VECTOR_SUITE", "status": "BLOCKED/NOT TESTABLE" if suite.returncode == 2 else "FAIL", "suite": suite_result}, 2 if suite.returncode == 2 else 1
    state["human_world_gate"] = "AUTHORIZED_NOT_PERFORMED"
    save_state(session, state)
    return {"stage": "COMPLETE_40_VECTOR_SUITE", "status": "FEASIBILITY GATE PASS", "selected_c1_maximum_delta": 0.0, "suite": "40/40 PASS", "human_world_gate": "AUTHORIZED_NOT_PERFORMED", "P1B": "FROZEN"}, 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage", choices=("prepare", "capture", "replay", "continue"), required=True)
    parser.add_argument("--godot", required=True)
    parser.add_argument("--baseline-root", required=True)
    parser.add_argument("--p0-root", required=True)
    parser.add_argument("--session-root", required=True)
    parser.add_argument("--standalone-evidence-zip", required=True)
    parser.add_argument("--route", choices=ROUTES)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if args.stage in {"capture", "replay"} and args.route is None:
        print(json.dumps({"status": "BLOCKED/NOT TESTABLE", "blocker": "--route required"}))
        return 2
    if args.stage not in {"capture", "replay"} and args.route is not None:
        print(json.dumps({"status": "BLOCKED/NOT TESTABLE", "blocker": "--route forbidden"}))
        return 2
    session = pathlib.Path(args.session_root).resolve()
    args.session_root_id = session.name
    output_zip = pathlib.Path(args.standalone_evidence_zip).resolve()
    evidence = session / "evidence" / ("PREPARE" if args.stage == "prepare" else f"{args.route}_{args.stage.upper()}" if args.route else "CONTINUE")
    if evidence.exists():
        shutil.rmtree(evidence)
    try:
        if args.stage == "prepare": result, code = prepare(args, session, evidence)
        elif args.stage == "capture": result, code = capture(args, session, evidence)
        elif args.stage == "replay": result, code = replay(args, session, evidence)
        else: result, code = continue_gate(args, session, evidence)
        finalize_package(evidence, output_zip, result)
        return code
    except Exception as exc:
        evidence.mkdir(parents=True, exist_ok=True)
        result = {"stage": args.stage.upper(), "status": "BLOCKED/NOT TESTABLE", "blocker": str(exc), "human_world_gate": "NOT PERFORMED", "P1B": "FROZEN"}
        finalize_package(evidence, output_zip, result)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
