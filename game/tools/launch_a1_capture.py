#!/usr/bin/env python3
"""Single-use, session-bound District Zero v1.2.6 A1 launcher."""
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
import time
import zipfile
from typing import Any

EXACT = "4.7.1.stable.official.a13da4feb"
INCIDENT_SHA = "9ecddef5a6f38d590fc97666b9e55c27e6c389b4ee1ba82a39eaa4f86a96c231"
FORBIDDEN_PARTS = {"__MACOSX", "__pycache__", ".pytest_cache", ".mypy_cache"}
ERRORS = tuple(re.compile(value, re.I) for value in (
    r"SCRIPT ERROR", r"Parse Error", r"Failed to load script", r"ERROR:\s+Failed",
    r"not declared in the current scope", r"Could not find type", r"Cannot infer the type",
))


def dump(path: pathlib.Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write(path: pathlib.Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value, encoding="utf-8")


def load(path: pathlib.Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} is not a JSON object")
    return value


def sha(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_inventory(root: pathlib.Path, inventory: pathlib.Path) -> list[str]:
    errors: list[str] = []
    seen: set[str] = set()
    if not inventory.is_file():
        return [f"missing inventory: {inventory.name}"]
    for line in inventory.read_text(encoding="utf-8").splitlines():
        match = re.fullmatch(r"([0-9a-f]{64})  (.+)", line)
        if not match:
            errors.append(f"malformed inventory row: {line}")
            continue
        digest, relative = match.groups()
        if relative in seen:
            errors.append(f"duplicate inventory path: {relative}")
        seen.add(relative)
        target = root / relative
        if not target.is_file() or sha(target) != digest:
            errors.append(f"checksum mismatch: {relative}")
    return errors


def inventory(directory: pathlib.Path) -> int:
    files = sorted((path for path in directory.rglob("*") if path.is_file() and path.name not in {"SHA256SUMS.txt", "A1_LAUNCHER_EVIDENCE.zip"}), key=lambda path: path.relative_to(directory).as_posix().encode())
    write(directory / "SHA256SUMS.txt", "".join(f"{sha(path)}  {path.relative_to(directory).as_posix()}\n" for path in files))
    return len(files)


def deterministic_zip(source: pathlib.Path, output: pathlib.Path) -> None:
    if output.exists():
        output.unlink()
    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in sorted((p for p in source.rglob("*") if p.is_file() and p != output), key=lambda p: p.relative_to(source).as_posix().encode()):
            info = zipfile.ZipInfo(path.relative_to(source).as_posix(), (1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = (0o100755 if path.suffix == ".command" else 0o100644) << 16
            archive.writestr(info, path.read_bytes())


def parse_last_json(text: str) -> dict[str, Any]:
    for line in reversed(text.splitlines()):
        try:
            value = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict):
            return value
    return {}


def finalise(evidence: pathlib.Path, session: pathlib.Path, status: str) -> dict[str, Any]:
    count = inventory(evidence)
    output = session / "A1_LAUNCHER_EVIDENCE.zip"
    deterministic_zip(evidence, output)
    with zipfile.ZipFile(output) as archive:
        bad = archive.testzip()
        names = archive.namelist()
    if bad is not None or len(names) != len(set(names)):
        raise RuntimeError("launcher evidence ZIP integrity failure")
    result = {"status": status, "checksum_record_count": count, "zip_path": str(output), "zip_byte_size": output.stat().st_size, "zip_sha256": sha(output)}
    print(json.dumps(result, sort_keys=True))
    return result


def preflight(session: pathlib.Path, evidence: pathlib.Path) -> tuple[list[str], dict[str, Any]]:
    errors: list[str] = []
    project = session / "project"
    engine = session / "engine/Godot"
    manifest_path = session / "SESSION_MANIFEST.json"
    state_path = session / "session_state.json"
    manifest = load(manifest_path) if manifest_path.is_file() else {}
    state = load(state_path) if state_path.is_file() else {}
    if manifest.get("schema") != "district_zero.p1a.v1_2_6.prepared_session_manifest.v1": errors.append("session manifest schema mismatch")
    if manifest.get("presentation_launch_overlay_authority_version") != "v1.2.6": errors.append("session authority mismatch")
    if manifest.get("route_binding") != "A1": errors.append("session is not bound to A1")
    if manifest.get("supersedes_incident_transport_sha256") != INCIDENT_SHA: errors.append("incident supersession identity mismatch")
    if manifest.get("original_session_reuse_forbidden") is not True: errors.append("blocked original reuse prohibition absent")
    if not manifest.get("session_uuid") or manifest.get("session_uuid") == manifest.get("blocked_original_session_uuid"): errors.append("session UUID is absent or reused")
    if state.get("prepared") is not True or state.get("authority_version") != "v1.2.5": errors.append("session state is not prepared under v1.2.5 capture semantics")
    routes = state.get("routes", {})
    for route in ("A1", "A2", "X0"):
        record = routes.get(route, {})
        if record.get("capture") != "NOT PERFORMED" or record.get("replay") != "NOT PERFORMED": errors.append(f"{route} is not pristine")
    if state.get("human_attempts_consumed", 0) != 0: errors.append("session reports a consumed attempt")
    for relative in ("routes/A1/captures", "selected_human_traces.json", "FINALIZED.json", "LAUNCH_USED.json"):
        if (session / relative).exists(): errors.append(f"single-use/pristine path already exists: {relative}")
    errors.extend(verify_inventory(session, session / "PROJECT_SHA256SUMS.txt"))
    errors.extend(verify_inventory(session, session / "SESSION_INPUT_SHA256SUMS.txt"))
    try:
        version = subprocess.run([str(engine.resolve()), "--version"], cwd=project, capture_output=True, text=True, check=False)
        observed = version.stdout.strip()
    except OSError as exc:
        observed = str(exc)
        version = None
    if version is None or version.returncode != 0 or observed != EXACT: errors.append(f"exact engine identity mismatch: {observed}")
    identity = {"required": EXACT, "observed": observed, "match": not any("engine identity" in error for error in errors), "engine_path": str(engine)}
    dump(evidence / "launcher_engine_identity.json", identity)
    dump(evidence / "prelaunch_checks.json", {"status": "PASS" if not errors else "FAIL", "errors": errors, "session_uuid": manifest.get("session_uuid"), "route": "A1"})
    return errors, {"project": project, "engine": engine, "manifest": manifest, "state": state}


def import_preflight(engine: pathlib.Path, project: pathlib.Path, evidence: pathlib.Path) -> list[str]:
    errors: list[str] = []
    import_dir = evidence / "import_preflight"
    import_dir.mkdir(parents=True, exist_ok=True)
    for name, command in (
        ("import", [str(engine.resolve()), "--headless", "--path", str(project), "--import", "--log-file", str(import_dir / "import-engine.txt")]),
        ("parse", [str(engine.resolve()), "--headless", "--editor", "--quit", "--path", str(project), "--log-file", str(import_dir / "parse-engine.txt")]),
    ):
        process = subprocess.run(command, cwd=project, capture_output=True, text=True, check=False)
        dump(import_dir / f"{name}-argv.json", {"argv": command, "cwd": str(project)})
        write(import_dir / f"{name}-stdout.txt", process.stdout)
        write(import_dir / f"{name}-stderr.txt", process.stderr)
        dump(import_dir / f"{name}-result.json", {"returncode": process.returncode})
        log = (import_dir / f"{name}-engine.txt").read_text(encoding="utf-8", errors="replace") if (import_dir / f"{name}-engine.txt").is_file() else ""
        combined = "\n".join((process.stdout, process.stderr, log))
        if process.returncode != 0: errors.append(f"{name} process returned {process.returncode}")
        errors.extend(line.strip() for line in combined.splitlines() if any(pattern.search(line) for pattern in ERRORS))
    cache = project / ".godot/global_script_class_cache.cfg"
    if not cache.is_file() or cache.stat().st_size == 0: errors.append("global script class cache absent after import")
    dump(import_dir / "result.json", {"status": "PASS" if not errors else "FAIL", "errors": sorted(set(errors)), "project_root": str(project), "class_cache_generated": cache.is_file()})
    return sorted(set(errors))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--session-root", required=True)
    parser.add_argument("--smoke", action="store_true")
    args = parser.parse_args()
    session = pathlib.Path(args.session_root).resolve()
    expected = pathlib.Path(__file__).resolve().parents[1]
    evidence = session / "launcher_evidence"
    evidence.mkdir(parents=True, exist_ok=True)
    write(evidence / "launcher_cwd.txt", str(session / "project") + "\n")
    dump(evidence / "launcher_argv.json", {"argv": sys.argv, "resolved_session_root": str(session), "launcher_project_root": str(expected)})
    started = time.time()
    started_utc = dt.datetime.now(dt.timezone.utc).isoformat()
    errors, context = preflight(session, evidence)
    if expected != session / "project": errors.append("launcher is not executing from the bound session project")
    if errors:
        dump(evidence / "launcher_process.json", {"child_launched": False, "normal_exit": False, "attempt_consumed": False})
        dump(evidence / "launcher_timestamps.json", {"started_utc": started_utc, "ended_utc": dt.datetime.now(dt.timezone.utc).isoformat(), "wall_duration_s": time.time() - started})
        dump(evidence / "terminal_result.json", {"status": "BLOCKED/NOT TESTABLE", "errors": errors, "attempts_consumed": 0})
        finalise(evidence, session, "BLOCKED/NOT TESTABLE")
        return 2
    import_errors = import_preflight(context["engine"], context["project"], evidence)
    if import_errors:
        dump(evidence / "launcher_process.json", {"child_launched": False, "normal_exit": False, "attempt_consumed": False})
        dump(evidence / "launcher_timestamps.json", {"started_utc": started_utc, "ended_utc": dt.datetime.now(dt.timezone.utc).isoformat(), "wall_duration_s": time.time() - started})
        dump(evidence / "terminal_result.json", {"status": "BLOCKED/NOT TESTABLE", "errors": import_errors, "attempts_consumed": 0})
        finalise(evidence, session, "BLOCKED/NOT TESTABLE")
        return 2
    marker = {"schema": "district_zero.p1a.v1_2_6.launch_used.v1", "session_uuid": context["manifest"]["session_uuid"], "route": "A1", "smoke": args.smoke, "created_utc": dt.datetime.now(dt.timezone.utc).isoformat()}
    dump(session / "LAUNCH_USED.json", marker)
    child_zip = evidence / ("A1_SMOKE_EVIDENCE.zip" if args.smoke else "A1_CAPTURE_EVIDENCE.zip")
    if args.smoke:
        command = [sys.executable, "-B", str(context["project"] / "tools/run_v1_2_6_launcher_smoke.py"), "--godot", str(context["engine"]), "--project-root", str(context["project"]), "--session-root", str(session), "--output-dir", str(evidence / "native_smoke"), "--session-id", str(context["manifest"]["session_uuid"]), "--minimum-wall-duration-s", "75"]
    else:
        command = [sys.executable, "-B", str(context["project"] / "tools/run_human_feasibility_session.py"), "--stage", "capture", "--route", "A1", "--godot", str(context["engine"]), "--baseline-root", str(session / "inputs/v1_2_5_baseline"), "--p0-root", str(session / "inputs/p0"), "--session-root", str(session), "--standalone-evidence-zip", str(child_zip)]
    dump(evidence / "child_argv.json", {"argv": command, "cwd": str(context["project"])})
    process = subprocess.Popen(command, cwd=context["project"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    stdout, stderr = process.communicate()
    ended_utc = dt.datetime.now(dt.timezone.utc).isoformat()
    write(evidence / "launcher_stdout.txt", stdout)
    write(evidence / "launcher_stderr.txt", stderr)
    child_result = parse_last_json(stdout)
    if child_zip.is_file():
        dump(evidence / "child_evidence_zip_identity.json", {"path": str(child_zip), "byte_size": child_zip.stat().st_size, "sha256": sha(child_zip)})
    else:
        dump(evidence / "child_evidence_zip_identity.json", {"path": str(child_zip), "present": False})
    normal_exit = process.returncode in (0, 1) and bool(child_result)
    status = child_result.get("status", "")
    blocked = process.returncode == 2 or not child_result or "BLOCKED/NOT TESTABLE" in status
    terminal = "BLOCKED/NOT TESTABLE — MACOS GODOT RUNTIME" if blocked else status or ("PASS" if process.returncode == 0 else "FAIL")
    dump(evidence / "launcher_process.json", {"pid": process.pid, "started_utc": started_utc, "ended_utc": ended_utc, "wall_duration_s": time.time() - started, "returncode": process.returncode, "signal_if_any": -process.returncode if process.returncode < 0 else None, "normal_exit": normal_exit, "child_result_present": bool(child_result), "child_result_status": status, "attempt_consumed": False if args.smoke or blocked else None})
    dump(evidence / "launcher_timestamps.json", {"started_utc": started_utc, "ended_utc": ended_utc, "wall_duration_s": time.time() - started})
    dump(evidence / "terminal_result.json", {"status": terminal, "child_result": child_result, "attempts_consumed": 0 if args.smoke or blocked else "DETERMINED_BY_CAPTURE_RESULT", "human_world_gate": "NOT PERFORMED", "P1B": "FROZEN"})
    finalise(evidence, session, terminal)
    return 2 if blocked else process.returncode


if __name__ == "__main__":
    raise SystemExit(main())
