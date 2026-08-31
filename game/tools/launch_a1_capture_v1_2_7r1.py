#!/usr/bin/env python3
"""Session-bound v1.2.7R1 launcher with fresh-extraction import preflight."""
from __future__ import annotations

import argparse
import datetime as dt
import json
import pathlib
import subprocess
import sys

ROOT_DEFAULT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DEFAULT / "tools"))

from p1a_v1_2_7r1_harness import (
    EXACT_ENGINE,
    dump,
    import_and_parse_project,
    package_tree,
    sha256,
    verify_inventory,
    write,
    write_inventory,
)

TARGET = "res://tests/p1a_human_feasibility_runner.gd"


def load(path: pathlib.Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    return value if isinstance(value, dict) else {}


def finalize(evidence: pathlib.Path, session: pathlib.Path, status: str, *, preflight_only: bool) -> dict:
    dump(evidence / "terminal_result.json", {
        "schema": "district_zero.p1a.v1_2_7r1.launcher_terminal_result.v1",
        "status": status,
        "preflight_only": preflight_only,
        "attempts_consumed": 0 if preflight_only or status.startswith("BLOCKED") else "DETERMINED_BY_CAPTURE_RESULT",
        "human_world_gate": "NOT PERFORMED",
        "P1B": "FROZEN",
    })
    write_inventory(evidence, "SHA256SUMS.txt")
    output = session / (
        "A1_LAUNCHER_PREFLIGHT_EVIDENCE.zip" if preflight_only else "A1_LAUNCHER_EVIDENCE.zip"
    )
    report = package_tree(
        evidence,
        output,
        inventory_name="SHA256SUMS.txt",
        scratch_parent=session / ".launcher-fresh-extraction",
    )
    # The scratch directory is generated state and is absent after verification.
    try:
        (session / ".launcher-fresh-extraction").rmdir()
    except OSError:
        pass
    print(json.dumps({"status": status, "package": report}, sort_keys=True))
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--session-root", required=True)
    parser.add_argument("--preflight-only", action="store_true")
    args = parser.parse_args()
    session = pathlib.Path(args.session_root).resolve()
    project = session / "project"
    manifest_path = session / "SESSION_MANIFEST.json"
    state_path = session / "session_state.json"
    errors: list[str] = []
    if not manifest_path.is_file() or not state_path.is_file():
        errors.append("session manifest/state absent")
        manifest: dict = {}
        state: dict = {}
    else:
        manifest = load(manifest_path)
        state = load(state_path)
    inventory_errors = verify_inventory(session, "SESSION_SHA256SUMS.txt")
    errors.extend(inventory_errors)
    if manifest.get("schema") != "district_zero.p1a.v1_2_7r1.prepared_a1_session_manifest.v1":
        errors.append("manifest schema mismatch")
    if manifest.get("route_binding") != "A1" or manifest.get("project_relative_path") != "project":
        errors.append("session route/project binding mismatch")
    if manifest.get("engine_identity") != EXACT_ENGINE or manifest.get("presentation_version") != "v1.2.7R1":
        errors.append("session authority/engine binding mismatch")
    if not state.get("prepared") or state.get("human_attempts_consumed") != 0:
        errors.append("session is not pristine and prepared")
    if (session / "LAUNCH_USED.json").exists():
        errors.append("single-use launcher already consumed")
    godot = pathlib.Path(str(manifest.get("godot_path", "")))
    try:
        version = subprocess.run([str(godot), "--version"], cwd=project, capture_output=True, text=True, check=False)
        observed = version.stdout.strip()
    except OSError as exc:
        observed = str(exc)
    if observed != EXACT_ENGINE:
        errors.append(f"exact engine mismatch: {observed}")
    if not project.is_dir() or not (project / "scripts/p1a_world_builder.gd").is_file():
        errors.append("session project absent")
    elif manifest.get("prepared_project_builder_sha256") != sha256(project / "scripts/p1a_world_builder.gd"):
        errors.append("prepared project builder identity mismatch")

    evidence = session / "launcher_evidence"
    evidence.mkdir(parents=True, exist_ok=True)
    dump(evidence / "session_preflight.json", {
        "status": "PASS" if not errors else "BLOCKED/NOT TESTABLE — HARNESS",
        "errors": errors,
        "inventory_errors": inventory_errors,
        "observed_engine": observed,
        "attempts_consumed": 0,
    })
    if errors:
        finalize(evidence, session, "BLOCKED/NOT TESTABLE — HARNESS", preflight_only=args.preflight_only)
        return 2

    contract = load(project / "tests/fixtures/disposable_import_preflight.json")
    imported = import_and_parse_project(
        str(godot),
        project,
        evidence / "IMPORT_PREFLIGHT",
        target_script=TARGET,
        required_classes=dict(contract["required_registered_classes"]),
        expected_builder_sha256=sha256(project / "scripts/p1a_world_builder.gd"),
    )
    if imported.get("status") != "PASS":
        dump(evidence / "preflight_result.json", {
            "status": "BLOCKED/NOT TESTABLE — HARNESS",
            "import_preflight": imported,
            "attempts_consumed": 0,
            "launch_used_created": False,
        })
        finalize(evidence, session, "BLOCKED/NOT TESTABLE — HARNESS", preflight_only=args.preflight_only)
        return 2
    if args.preflight_only:
        dump(evidence / "preflight_result.json", {
            "status": "PASS",
            "import_preflight": imported,
            "attempts_consumed": 0,
            "launch_used_created": False,
        })
        finalize(evidence, session, "PASS", preflight_only=True)
        return 0

    dump(session / "LAUNCH_USED.json", {
        "schema": "district_zero.p1a.v1_2_7r1.launch_used.v1",
        "created_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "route": "A1",
    })
    child_zip = session / "A1_CAPTURE_EVIDENCE.zip"
    command = [
        sys.executable,
        "-B",
        str(project / "tools/run_human_feasibility_session.py"),
        "--stage",
        "capture",
        "--route",
        "A1",
        "--godot",
        str(godot),
        "--baseline-root",
        str(project),
        "--p0-root",
        str(project),
        "--session-root",
        str(session),
        "--standalone-evidence-zip",
        str(child_zip),
    ]
    dump(evidence / "child_argv.json", {"argv": command, "cwd": str(project)})
    process = subprocess.run(command, cwd=project, capture_output=True, text=True, check=False)
    write(evidence / "child_stdout.txt", process.stdout)
    write(evidence / "child_stderr.txt", process.stderr)
    dump(evidence / "child_result.json", {
        "returncode": process.returncode,
        "capture_evidence_present": child_zip.is_file(),
        "capture_evidence_sha256": sha256(child_zip) if child_zip.is_file() else None,
    })
    status = "PASS" if process.returncode == 0 else "FAIL" if process.returncode == 1 else "BLOCKED/NOT TESTABLE — HARNESS"
    finalize(evidence, session, status, preflight_only=False)
    return process.returncode if process.returncode in (0, 1) else 2


if __name__ == "__main__":
    raise SystemExit(main())
