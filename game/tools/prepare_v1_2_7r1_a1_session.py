#!/usr/bin/env python3
"""Create an exact-imported, zero-attempt v1.2.7R1 prepared A1 session."""
from __future__ import annotations

import argparse
import datetime as dt
import json
import pathlib
import shutil
import sys
import uuid

ROOT_DEFAULT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DEFAULT / "tools"))

from p1a_v1_2_7r1_harness import (
    EXACT_ENGINE,
    dump,
    import_and_parse_project,
    sha256,
    verify_inventory,
    write,
    write_inventory,
)

TARGET = "res://tests/p1a_human_feasibility_runner.gd"


def copy_clean(source: pathlib.Path, destination: pathlib.Path) -> None:
    def ignore(_directory: str, names: list[str]) -> set[str]:
        return {
            name for name in names
            if name in {".godot", "__pycache__", "director_inputs", ".pytest_cache", ".mypy_cache"}
            or name == "v1_2_7_v1_2_6_world_builder.gd"
            or name == ".DS_Store"
            or name.startswith("._")
            or name.endswith((".pyc", ".pyo", ".zip"))
        }

    shutil.copytree(source, destination, ignore=ignore)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True)
    parser.add_argument("--godot", required=True)
    parser.add_argument("--session-root", required=True)
    parser.add_argument("--evidence-dir", required=True)
    args = parser.parse_args()
    root = pathlib.Path(args.root).resolve()
    godot = str(pathlib.Path(args.godot).resolve())
    session = pathlib.Path(args.session_root).resolve()
    evidence = pathlib.Path(args.evidence_dir).resolve()
    evidence.mkdir(parents=True, exist_ok=True)
    if session.exists() and any(session.iterdir()):
        result = {
            "status": "BLOCKED/NOT TESTABLE — HARNESS",
            "blocker": "session root is nonempty",
            "human_attempts_consumed": 0,
        }
        dump(evidence / "result.json", result)
        print(json.dumps(result, sort_keys=True))
        return 2
    session.mkdir(parents=True, exist_ok=True)
    project = session / "project"
    copy_clean(root, project)
    write_inventory(project, "PACKET_SHA256SUMS.txt")
    contract = json.loads((root / "tests/fixtures/disposable_import_preflight.json").read_text(encoding="utf-8"))
    required_classes = dict(contract["required_registered_classes"])
    imported = import_and_parse_project(
        godot,
        project,
        evidence / "IMPORT_PREFLIGHT",
        target_script=TARGET,
        required_classes=required_classes,
        expected_builder_sha256=sha256(project / "scripts/p1a_world_builder.gd"),
    )
    if imported.get("status") != "PASS":
        result = {
            "status": "BLOCKED/NOT TESTABLE — HARNESS",
            "blocker": "prepared project import/parse/class resolution failed",
            "import_preflight": imported,
            "human_attempts_consumed": 0,
            "human_world_gate": "NOT PERFORMED",
            "P1B": "FROZEN",
        }
        dump(evidence / "result.json", result)
        write_inventory(evidence, "SHA256SUMS.txt")
        print(json.dumps(result, sort_keys=True))
        return 2

    # Generated editor state is deliberately not packaged. The session-bound
    # launcher repeats this same exact import against the fresh extraction.
    shutil.rmtree(project / ".godot", ignore_errors=True)
    session_id = str(uuid.uuid4())
    import_copy = {
        **imported,
        "prepared_project_root": str(project),
        "prepared_project_builder_sha256": sha256(project / "scripts/p1a_world_builder.gd"),
        "external_evidence_result_sha256": sha256(evidence / "IMPORT_PREFLIGHT/result.json"),
    }
    dump(session / "PREPARE_IMPORT_RESULT.json", import_copy)
    state = {
        "schema": "district_zero.p1a.v1_2_7r1.session_state.v1",
        "authority_version": "v1.2.5",
        "presentation_version": "v1.2.7R1",
        "prepared": True,
        "prepared_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "human_attempts_consumed": 0,
        "routes": {
            route: {"capture": "NOT PERFORMED", "replay": "NOT PERFORMED"}
            for route in ("A1", "A2", "X0")
        },
        "human_world_gate": "NOT PERFORMED",
        "P1B": "FROZEN",
    }
    dump(session / "session_state.json", state)
    manifest = {
        "schema": "district_zero.p1a.v1_2_7r1.prepared_a1_session_manifest.v1",
        "session_uuid": session_id,
        "route_binding": "A1",
        "godot_path": godot,
        "engine_identity": EXACT_ENGINE,
        "capture_semantics_version": "v1.2.5",
        "presentation_version": "v1.2.7R1",
        "project_relative_path": "project",
        "prepared_project_root": str(project),
        "prepared_project_builder_sha256": sha256(project / "scripts/p1a_world_builder.gd"),
        "prepare_import_result_sha256": sha256(session / "PREPARE_IMPORT_RESULT.json"),
        "fresh_extraction_requires_launcher_reimport": True,
        "human_attempts_consumed": 0,
        "human_world_gate": "NOT PERFORMED",
        "P1B": "FROZEN",
    }
    dump(session / "SESSION_MANIFEST.json", manifest)
    launcher = session / "START_A1_CAPTURE.command"
    write(
        launcher,
        "#!/bin/zsh\n"
        "set -euo pipefail\n"
        "SESSION_ROOT=\"${0:A:h}\"\n"
        "exec /usr/bin/env python3 -B \"$SESSION_ROOT/project/tools/launch_a1_capture_v1_2_7r1.py\" --session-root \"$SESSION_ROOT\" \"$@\"\n",
    )
    launcher.chmod(0o755)
    result = {
        "schema": "district_zero.p1a.v1_2_7r1.prepared_a1_session_result.v1",
        "status": "READY FOR A1 HUMAN FEASIBILITY CAPTURE",
        "session_uuid": session_id,
        "engine_identity": EXACT_ENGINE,
        "prepared_project_root": str(project),
        "prepared_project_builder_sha256": sha256(project / "scripts/p1a_world_builder.gd"),
        "import_preflight": import_copy,
        "checksum_records": 0,
        "human_attempts_consumed": 0,
        "human_world_gate": "NOT PERFORMED",
        "P1B": "FROZEN",
    }
    # The result must exist before the inventory. Its later count update does
    # not change the path set, so the prospective count is stable.
    dump(session / "PREPARED_RESULT.json", result)
    prospective_count = len([
        path for path in session.rglob("*")
        if path.is_file()
        and path.name != "SESSION_SHA256SUMS.txt"
        and ".godot" not in path.parts
        and "__pycache__" not in path.parts
    ])
    result["checksum_records"] = prospective_count
    dump(session / "PREPARED_RESULT.json", result)
    count = write_inventory(session, "SESSION_SHA256SUMS.txt")
    inventory_errors = verify_inventory(session, "SESSION_SHA256SUMS.txt")
    if count != prospective_count or inventory_errors or not any(
        line.endswith("  PREPARED_RESULT.json")
        for line in (session / "SESSION_SHA256SUMS.txt").read_text(encoding="utf-8").splitlines()
    ):
        blocked = {
            "status": "BLOCKED/NOT TESTABLE — HARNESS",
            "blocker": "prepared-session final inventory is incomplete",
            "count": count,
            "prospective_count": prospective_count,
            "inventory_errors": inventory_errors,
            "human_attempts_consumed": 0,
        }
        dump(evidence / "result.json", blocked)
        print(json.dumps(blocked, sort_keys=True))
        return 2
    dump(evidence / "result.json", result)
    write_inventory(evidence, "SHA256SUMS.txt")
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
