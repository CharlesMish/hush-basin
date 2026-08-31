#!/usr/bin/env python3
"""District Zero P1A v1.2.4I exact-engine gated execution wrapper.

Sequence:
verify → copy selected project → import/validate → parse actual runtime runner →
A1 preregistered V6 candidates → freeze first A1 pass → A1 confirmation →
A2 → X0 → selected C1 → complete 40-vector suite → stop before human/P1B.
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
import tempfile
import zipfile
from typing import Any, Iterable

ROOT = pathlib.Path(__file__).resolve().parents[1]
EXACT = "4.7.1.stable.official.a13da4feb"
OVERLAY = "1.2.4I"
WORLD = "1.2.3"
HARNESS_REPAIR_REVISION = "v1.2.4I-R1"
V6_CONTROLLER = "ROUTE_FOLLOWER_INPUT_CONTROLLER_V6_DECEL_CONSTRAINED_THRUST_VECTOR_CONTAINED"
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
ERROR_PATTERNS = (
    re.compile(r"SCRIPT ERROR", re.IGNORECASE),
    re.compile(r"Parse Error", re.IGNORECASE),
    re.compile(r"Cannot infer the type", re.IGNORECASE),
    re.compile(r"Could not find type", re.IGNORECASE),
    re.compile(r"not declared in the current scope", re.IGNORECASE),
    re.compile(r"Failed to load script", re.IGNORECASE),
    re.compile(r"ERROR:\s+Failed", re.IGNORECASE),
)
FORBIDDEN_PARTS = {".godot", "__MACOSX", "__pycache__", ".pytest_cache", ".mypy_cache"}


def dump(path: pathlib.Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")


def write_text(path: pathlib.Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value, encoding="utf-8", newline="\n")


def sha256(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: pathlib.Path) -> dict[str, Any] | None:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None
    return value if isinstance(value, dict) else None


def parse_static_verifier_result(stdout: str, process_returncode: int) -> dict[str, Any]:
    """Parse one complete verifier JSON document and enforce the PASS contract.

    json.loads accepts surrounding whitespace and rejects empty input, malformed JSON,
    multiple documents, and non-whitespace trailing output.  A valid JSON value is
    still rejected unless it is an object with status PASS, integer error_count 0,
    and process return code 0.
    """
    result: dict[str, Any] = {
        "status": "BLOCKED/NOT TESTABLE",
        "verifier_result": None,
        "process_returncode": process_returncode,
        "parser_contract": "WHOLE_DOCUMENT_JSON_OBJECT_PASS_V1",
        "parser_errors": [],
        "harness_repair_revision": HARNESS_REPAIR_REVISION,
    }
    if process_returncode != 0:
        result["parser_errors"].append(f"static verifier process return code {process_returncode}, required 0")
        return result
    if not stdout.strip():
        result["parser_errors"].append("static verifier stdout is empty or whitespace-only")
        return result
    try:
        parsed = json.loads(stdout)
    except json.JSONDecodeError as exc:
        result["parser_errors"].append(
            f"static verifier stdout is not exactly one complete JSON document: {exc.msg} at line {exc.lineno} column {exc.colno}"
        )
        return result
    if not isinstance(parsed, dict):
        result["parser_errors"].append(f"static verifier JSON must be an object, observed {type(parsed).__name__}")
        return result
    if parsed.get("status") != "PASS":
        result["parser_errors"].append(f"static verifier status is {parsed.get('status')!r}, required 'PASS'")
        result["verifier_result"] = parsed
        return result
    error_count = parsed.get("error_count")
    if isinstance(error_count, bool) or not isinstance(error_count, int) or error_count != 0:
        result["parser_errors"].append(f"static verifier error_count is {error_count!r}, required integer 0")
        result["verifier_result"] = parsed
        return result
    result["status"] = "PASS"
    result["verifier_result"] = parsed
    return result


def run(command: list[str], cwd: pathlib.Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=cwd, capture_output=True, text=True, check=False)


def scan_errors(paths: Iterable[pathlib.Path]) -> list[str]:
    output: list[str] = []
    seen: set[str] = set()
    for path in paths:
        if not path.is_file():
            continue
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            normalized = line.strip()
            if normalized and any(pattern.search(normalized) for pattern in ERROR_PATTERNS) and normalized not in seen:
                output.append(normalized)
                seen.add(normalized)
    return output


def checksum_inventory(root: pathlib.Path) -> int:
    rows: list[str] = []
    for path in sorted(
        (p for p in root.rglob("*") if p.is_file() and p.name != "SHA256SUMS.txt"),
        key=lambda p: p.relative_to(root).as_posix().encode("utf-8"),
    ):
        rows.append(f"{sha256(path)}  {path.relative_to(root).as_posix()}\n")
    write_text(root / "SHA256SUMS.txt", "".join(rows))
    return len(rows)


def verify_checksum_inventory(root: pathlib.Path) -> tuple[bool, list[str]]:
    path = root / "SHA256SUMS.txt"
    if not path.is_file():
        return False, ["SHA256SUMS.txt absent"]
    errors: list[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line:
            continue
        try:
            digest, rel = line.split("  ", 1)
        except ValueError:
            errors.append(f"malformed row: {line}")
            continue
        target = root / rel
        if not target.is_file():
            errors.append(f"missing: {rel}")
        elif sha256(target) != digest:
            errors.append(f"hash mismatch: {rel}")
    return not errors, errors


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


def forbidden_evidence_entries(root: pathlib.Path) -> list[str]:
    bad: list[str] = []
    for path in root.rglob("*"):
        rel = path.relative_to(root)
        if any(part in FORBIDDEN_PARTS for part in rel.parts):
            bad.append(rel.as_posix())
        if path.name == ".DS_Store" or path.name.startswith("._"):
            bad.append(rel.as_posix())
        if path.is_file() and path.suffix.lower() in {".zip", ".tar", ".gz", ".7z", ".rar"}:
            bad.append(rel.as_posix())
    return sorted(set(bad))


def write_process_record(root: pathlib.Path, stage: str, command: list[str], cwd: pathlib.Path, completed: subprocess.CompletedProcess[str]) -> None:
    directory = root / stage
    directory.mkdir(parents=True, exist_ok=True)
    dump(directory / "argv.json", {"argv": command, "cwd": str(cwd)})
    write_text(directory / "stdout.txt", completed.stdout)
    write_text(directory / "stderr.txt", completed.stderr)
    dump(directory / "result.json", {"process_returncode": completed.returncode})
    checksum_inventory(directory)


def copy_without_generated(source: pathlib.Path, destination: pathlib.Path) -> None:
    def ignore(_directory: str, names: list[str]) -> set[str]:
        return {
            name
            for name in names
            if name in FORBIDDEN_PARTS
            or name == ".DS_Store"
            or name.startswith("._")
            or name.endswith((".pyc", ".pyo"))
        }
    shutil.copytree(source, destination, ignore=ignore)


def substantive_files(root: pathlib.Path) -> list[pathlib.Path]:
    return sorted(
        (
            p
            for p in root.rglob("*")
            if p.is_file()
            and not any(part in FORBIDDEN_PARTS for part in p.relative_to(root).parts)
            and p.name != ".DS_Store"
            and not p.name.startswith("._")
            and not p.name.endswith((".pyc", ".pyo"))
        ),
        key=lambda p: p.relative_to(root).as_posix().encode("utf-8"),
    )


def copy_selected_project(selected: pathlib.Path, evidence: pathlib.Path) -> dict[str, Any]:
    directory = evidence / "COPY_SELECTED_PROJECT"
    directory.mkdir(parents=True, exist_ok=True)
    copy_without_generated(ROOT, selected)
    source_map = {p.relative_to(ROOT).as_posix(): sha256(p) for p in substantive_files(ROOT)}
    copy_map = {p.relative_to(selected).as_posix(): sha256(p) for p in substantive_files(selected)}
    mismatches = [rel for rel in sorted(set(source_map) | set(copy_map)) if source_map.get(rel) != copy_map.get(rel)]
    result = {
        "schema": "district_zero.p1a.v1_2_4i.copy_selected_project_result.v1",
        "status": "PASS" if not mismatches else "BLOCKED/NOT TESTABLE",
        "source_root": str(ROOT),
        "selected_root": str(selected),
        "source_file_count": len(source_map),
        "selected_file_count": len(copy_map),
        "byte_identical_file_count": len(source_map) - len(mismatches),
        "mismatches": mismatches,
    }
    dump(directory / "result.json", result)
    checksum_inventory(directory)
    return result


def discover_classes(root: pathlib.Path) -> dict[str, str]:
    classes: dict[str, str] = {}
    for path in sorted((root / "scripts").glob("*.gd")):
        match = re.search(r"(?m)^class_name\s+([A-Za-z_][A-Za-z0-9_]*)\s*$", path.read_text(encoding="utf-8", errors="replace"))
        if match:
            classes[match.group(1)] = "res://" + path.relative_to(root).as_posix()
    return classes


def cache_resolution(cache: pathlib.Path, expected: dict[str, str]) -> tuple[list[str], dict[str, Any]]:
    text = cache.read_text(encoding="utf-8", errors="replace") if cache.is_file() else ""
    records: dict[str, Any] = {}
    missing: list[str] = []
    for name, resource_path in expected.items():
        class_ok = re.search(rf'"class"\s*:\s*&?"{re.escape(name)}"', text) is not None
        path_ok = resource_path in text
        records[name] = {"resource_path": resource_path, "class_present": class_ok, "path_present": path_ok, "resolved": class_ok and path_ok}
        if not class_ok or not path_ok:
            missing.append(name)
    return missing, {
        "cache_generated": cache.is_file() and cache.stat().st_size > 0,
        "cache_byte_size": cache.stat().st_size if cache.is_file() else 0,
        "cache_sha256": sha256(cache) if cache.is_file() else None,
        "classes": records,
    }


def import_and_parse_preflight(selected: pathlib.Path, evidence: pathlib.Path, godot: str, version: str) -> dict[str, Any]:
    directory = evidence / "DISPOSABLE_IMPORT"
    directory.mkdir(parents=True, exist_ok=True)

    import_engine = directory / "import_engine.txt"
    import_cmd = [godot, "--headless", "--path", str(selected), "--import", "--log-file", str(import_engine)]
    dump(directory / "import_argv.json", {"argv": import_cmd, "cwd": str(selected)})
    imported = run(import_cmd, cwd=selected)
    write_text(directory / "import_stdout.txt", imported.stdout)
    write_text(directory / "import_stderr.txt", imported.stderr)
    if not import_engine.exists():
        write_text(import_engine, "")

    validation_engine = directory / "validation_engine.txt"
    validation_cmd = [godot, "--headless", "--editor", "--quit", "--path", str(selected), "--log-file", str(validation_engine)]
    dump(directory / "validation_argv.json", {"argv": validation_cmd, "cwd": str(selected)})
    validated = run(validation_cmd, cwd=selected)
    write_text(directory / "validation_stdout.txt", validated.stdout)
    write_text(directory / "validation_stderr.txt", validated.stderr)
    if not validation_engine.exists():
        write_text(validation_engine, "")

    runner = selected / "tests" / "p1a_runtime_runner.gd"
    parse_engine = directory / "runner_parse_engine.txt"
    parse_cmd = [
        godot,
        "--headless",
        "--path",
        str(selected),
        "--check-only",
        "--script",
        "res://tests/p1a_runtime_runner.gd",
        "--log-file",
        str(parse_engine),
    ]
    dump(directory / "runner_parse_argv.json", {"argv": parse_cmd, "cwd": str(selected), "target_sha256": sha256(runner)})
    parsed = run(parse_cmd, cwd=selected)
    write_text(directory / "runner_parse_stdout.txt", parsed.stdout)
    write_text(directory / "runner_parse_stderr.txt", parsed.stderr)
    if not parse_engine.exists():
        write_text(parse_engine, "")

    expected = discover_classes(selected)
    missing, cache = cache_resolution(selected / ".godot" / "global_script_class_cache.cfg", expected)
    dump(directory / "class_cache_summary.json", cache)
    error_paths = [
        directory / "import_stdout.txt",
        directory / "import_stderr.txt",
        import_engine,
        directory / "validation_stdout.txt",
        directory / "validation_stderr.txt",
        validation_engine,
        directory / "runner_parse_stdout.txt",
        directory / "runner_parse_stderr.txt",
        parse_engine,
    ]
    errors = scan_errors(error_paths)
    blockers: list[str] = []
    if version != EXACT:
        blockers.append("exact engine mismatch")
    if imported.returncode != 0:
        blockers.append("import returned nonzero")
    if validated.returncode != 0:
        blockers.append("validation open returned nonzero")
    if parsed.returncode != 0:
        blockers.append("runtime-runner check-only returned nonzero")
    if not cache["cache_generated"]:
        blockers.append("global registered-class cache was not generated")
    if sorted(expected) != REQUIRED_CLASSES:
        blockers.append("discovered registered-class set differs from required authority")
    if missing:
        blockers.append(f"registered classes unresolved: {missing}")
    if errors:
        blockers.append("parse/import/load errors were emitted")
    parse_result = {
        "schema": "district_zero.p1a.v1_2_4i.runtime_runner_parse_result.v1",
        "status": "PASS" if not blockers else "BLOCKED/NOT TESTABLE",
        "explicit_parse_result": "PASS" if not blockers else "FAIL",
        "project_root": str(selected.resolve()),
        "required_godot_version": EXACT,
        "observed_godot_version": version,
        "target_script_resource_path": "res://tests/p1a_runtime_runner.gd",
        "selected_runner_sha256": sha256(runner),
        "process_returncode": parsed.returncode,
        "parse_error_count": len(errors),
        "parse_errors": errors,
    }
    dump(directory / "runner_parse_result.json", parse_result)
    result = {
        "schema": "district_zero.p1a.v1_2_4i.disposable_import_result.v1",
        "status": "PASS" if not blockers else "BLOCKED/NOT TESTABLE",
        "explicit_import_result": "PASS" if not blockers else "FAIL",
        "project_root": str(selected.resolve()),
        "required_godot_version": EXACT,
        "observed_godot_version": version,
        "import_process_returncode": imported.returncode,
        "validation_process_returncode": validated.returncode,
        "class_cache_generated": cache["cache_generated"],
        "class_cache_byte_size": cache["cache_byte_size"],
        "required_classes_verified": sorted(expected) if not missing else sorted(set(expected) - set(missing)),
        "registered_project_scripts_parse_confirmed": validated.returncode == 0 and not errors and not missing,
        "runtime_runner_parse_confirmed": parsed.returncode == 0 and not errors,
        "required_project_scripts_parse_confirmed": validated.returncode == 0 and parsed.returncode == 0 and not errors and not missing,
        "runtime_runner_target_resource_path": "res://tests/p1a_runtime_runner.gd",
        "runtime_runner_sha256": sha256(runner),
        "runtime_runner_parse_process_returncode": parsed.returncode,
        "runtime_runner_parse_error_count": len(errors),
        "runtime_runner_parse_result_path": str((directory / "runner_parse_result.json").resolve()),
        "runtime_runner_parse_result_sha256": sha256(directory / "runner_parse_result.json"),
        "parse_or_import_error_count": len(errors),
        "parse_or_import_errors": errors,
        "blockers": blockers,
    }
    dump(directory / "result.json", result)
    checksum_inventory(directory)
    return result


def run_static_verifier(args: argparse.Namespace, evidence: pathlib.Path) -> dict[str, Any]:
    command = [
        sys.executable,
        "-B",
        str(ROOT / "tools" / "verify_p1a_implementation.py"),
        "--root",
        str(ROOT),
        "--baseline-root",
        str(pathlib.Path(args.baseline_root).resolve()),
        "--p0-root",
        str(pathlib.Path(args.p0_root).resolve()),
        "--allow-blocked-runtime",
    ]
    completed = run(command, cwd=ROOT)
    write_process_record(evidence, "STATIC_VERIFIER", command, ROOT, completed)
    return parse_static_verifier_result(completed.stdout, completed.returncode)


def run_engine_identity(godot: str, evidence: pathlib.Path) -> dict[str, Any]:
    directory = evidence / "ENGINE_IDENTITY"
    directory.mkdir(parents=True, exist_ok=True)
    command = [godot, "--version"]
    try:
        completed = run(command, cwd=ROOT)
        observed = completed.stdout.strip()
    except OSError as exc:
        completed = subprocess.CompletedProcess(command, 127, "", str(exc))
        observed = ""
    dump(directory / "argv.json", {"argv": command, "cwd": str(ROOT)})
    write_text(directory / "stdout.txt", completed.stdout)
    write_text(directory / "stderr.txt", completed.stderr)
    result = {"status": "PASS" if completed.returncode == 0 and observed == EXACT else "BLOCKED/NOT TESTABLE", "required": EXACT, "observed": observed, "process_returncode": completed.returncode}
    dump(directory / "result.json", result)
    checksum_inventory(directory)
    return result


def run_suite_stage(
    selected: pathlib.Path,
    evidence: pathlib.Path,
    godot: str,
    preflight: pathlib.Path,
    stage: str,
    vector_ids: list[str] | None,
    candidate_id: str | None,
    *,
    fail_fast: bool,
) -> dict[str, Any]:
    stage_root = evidence / stage
    runtime_evidence = stage_root / "runtime_vectors"
    report_path = stage_root / "runtime_vector_results.json"
    command = [
        sys.executable,
        "-B",
        str(selected / "tools" / "run_p1a_runtime_suite.py"),
        "--godot",
        godot,
        "--import-preflight-record",
        str(preflight),
        "--output",
        str(report_path),
        "--evidence-dir",
        str(runtime_evidence),
    ]
    for vector_id in vector_ids or []:
        command += ["--only", vector_id]
    if candidate_id:
        command += ["--v6-candidate-id", candidate_id]
    if fail_fast:
        command.append("--fail-fast-on-vector-failure")
    completed = run(command, cwd=selected)
    write_process_record(evidence, stage + "_WRAPPER", command, selected, completed)
    report = load(report_path)
    if report is None:
        return {"status": "BLOCKED/NOT TESTABLE", "blocker": "runtime suite report absent/unreadable", "process_returncode": completed.returncode}
    if report.get("status") == "BLOCKED/NOT TESTABLE":
        return {"status": "BLOCKED/NOT TESTABLE", "report": report, "process_returncode": completed.returncode}
    failures = int(report.get("fail_count", 0))
    passes = int(report.get("pass_count", 0))
    expected = len(vector_ids) if vector_ids is not None else 40
    if int(report.get("executed_vector_count", -1)) != expected:
        return {"status": "BLOCKED/NOT TESTABLE", "blocker": "not all authorized vectors produced creditable gameplay results", "report": report}
    if failures:
        return {"status": "FAIL", "report": report, "process_returncode": completed.returncode}
    if passes != expected:
        return {"status": "BLOCKED/NOT TESTABLE", "blocker": "pass count does not equal expected executed count", "report": report}
    return {"status": "PASS", "report": report, "process_returncode": completed.returncode}


def run_v6_fast_route_gate(selected: pathlib.Path, evidence: pathlib.Path, godot: str, preflight: pathlib.Path) -> dict[str, Any]:
    registry = load(selected / "tests" / "fixtures" / "fast_route_driver_v6_candidates.json")
    if registry is None:
        return {"status": "BLOCKED/NOT TESTABLE", "blocker": "V6 candidate registry absent/unreadable"}
    order = [str(v) for v in registry.get("candidate_order", [])]
    candidates = {str(v.get("id")): v for v in registry.get("candidates", []) if isinstance(v, dict)}
    attempts: list[dict[str, Any]] = []
    selected_candidate: str | None = None
    for candidate_id in order:
        if candidate_id not in candidates:
            return {"status": "BLOCKED/NOT TESTABLE", "blocker": f"candidate order references unknown {candidate_id}"}
        result = run_suite_stage(selected, evidence, godot, preflight, f"V6_A1_DEVELOPMENT/{candidate_id}", ["RT_ROUTE_A1"], candidate_id, fail_fast=True)
        attempts.append({"candidate_id": candidate_id, "result": result})
        if result["status"] == "BLOCKED/NOT TESTABLE":
            return {"status": "BLOCKED/NOT TESTABLE", "stage": "A1_CANDIDATE_SELECTION", "attempts": attempts}
        if result["status"] == "PASS":
            selected_candidate = candidate_id
            break
    if selected_candidate is None:
        return {"status": "FAIL", "primary_failure_class": "TEST_DRIVER", "reason": "no preregistered V6 candidate passed unchanged A1 contract", "attempts": attempts}
    freeze = {
        "schema": "district_zero.p1a.v1_2_4i.v6_candidate_selection.v1",
        "status": "SELECTED_FOR_PROSPECTIVE_GATE",
        "candidate_id": selected_candidate,
        "selection_basis": "first preregistered candidate in fixed order that passed A1",
        "candidate_order": order,
        "A1_attempts": attempts,
        "parameters_frozen_before_A2_X0": True,
        "retuning_after_A1": "FORBIDDEN",
    }
    dump(evidence / "FAST_ROUTE_GATE" / "v6_candidate_selection.json", freeze)

    confirmation = run_suite_stage(selected, evidence, godot, preflight, "FAST_ROUTE_GATE/A1_CONFIRMATION", ["RT_ROUTE_A1"], selected_candidate, fail_fast=True)
    if confirmation["status"] != "PASS":
        return {"status": confirmation["status"], "stage": "A1_CONFIRMATION", "selected_candidate_id": selected_candidate, "confirmation": confirmation, "attempts": attempts}
    a2 = run_suite_stage(selected, evidence, godot, preflight, "FAST_ROUTE_GATE/A2_PROSPECTIVE", ["RT_ROUTE_A2"], selected_candidate, fail_fast=True)
    if a2["status"] != "PASS":
        return {"status": a2["status"], "stage": "A2_PROSPECTIVE", "selected_candidate_id": selected_candidate, "A1_confirmation": confirmation, "A2": a2, "attempts": attempts}
    x0 = run_suite_stage(selected, evidence, godot, preflight, "FAST_ROUTE_GATE/X0_PROSPECTIVE", ["RT_ROUTE_X0"], selected_candidate, fail_fast=True)
    if x0["status"] != "PASS":
        return {"status": x0["status"], "stage": "X0_PROSPECTIVE", "selected_candidate_id": selected_candidate, "A1_confirmation": confirmation, "A2": a2, "X0": x0, "attempts": attempts}
    gate = {
        "schema": "district_zero.p1a.v1_2_4i.fast_route_gate_result.v1",
        "status": "PASS",
        "selected_candidate_id": selected_candidate,
        "candidate_selection": freeze,
        "A1_confirmation": confirmation,
        "A2_prospective": a2,
        "X0_prospective": x0,
    }
    dump(evidence / "FAST_ROUTE_GATE" / "gate_result.json", gate)
    return gate


def run_selected_c1(selected: pathlib.Path, p0: pathlib.Path, evidence: pathlib.Path, godot: str) -> dict[str, Any]:
    stage = evidence / "C1_SELECTED"
    work = pathlib.Path(tempfile.mkdtemp(prefix="district-zero-v124i-c1-"))
    command = [
        sys.executable,
        "-B",
        str(selected / "tools" / "run_selected_c1.py"),
        "--godot",
        godot,
        "--p0-root",
        str(p0),
        "--evidence-dir",
        str(stage),
        "--work-root",
        str(work),
    ]
    try:
        completed = run(command, cwd=selected)
        write_process_record(evidence, "C1_SELECTED_WRAPPER", command, selected, completed)
        result = load(stage / "C1_result.json")
        if result is None:
            return {"status": "BLOCKED/NOT TESTABLE", "blocker": "selected C1 result absent/unreadable"}
        if result.get("status") == "PASS" and float(result.get("maximum_absolute_difference", 1.0)) == 0.0:
            return {"status": "PASS", "result": result}
        if result.get("status") == "BLOCKED/NOT TESTABLE":
            return {"status": "BLOCKED/NOT TESTABLE", "result": result}
        return {"status": "FAIL", "result": result}
    finally:
        shutil.rmtree(work, ignore_errors=True)


def finalize_terminal(evidence: pathlib.Path, output_zip: pathlib.Path, *, status: str, stage: str, instruction: str, details: dict[str, Any], exit_code: int) -> dict[str, Any]:
    gate_result = {
        "schema": "district_zero.p1a.v1_2_4i.gate_result.v1",
        "status": status,
        "terminal_stage": stage,
        "instruction": instruction,
        "exit_code": exit_code,
        "execution_overlay_authority_version": OVERLAY,
        "harness_repair_revision": HARNESS_REPAIR_REVISION,
        "world_data_authority_version": WORLD,
        "human_world_gate": "AUTHORIZED_NOT_PERFORMED" if status == "PASS" and stage == "COMPLETE_40_VECTOR_SUITE" else "NOT PERFORMED",
        "P1B": "FROZEN",
        "details": details,
    }
    dump(evidence / "gate_result.json", gate_result)
    dump(
        evidence / "EVIDENCE_PACKAGE_MANIFEST.json",
        {
            "schema": "district_zero.p1a.v1_2_4i_r1.evidence_package_manifest.v1",
            "execution_overlay_authority_version": OVERLAY,
            "harness_repair_revision": HARNESS_REPAIR_REVISION,
            "terminal_status": status,
            "terminal_stage": stage,
            "per_vector_required_files": [
                "argv.json", "stdout.txt", "stderr.txt", "engine.txt", "runtime_result_line.txt",
                "runtime_result.json", "suite_classification.json", "events.jsonl",
                "post_result_events.jsonl", "result.json", "SHA256SUMS.txt",
            ],
            "raw_result_is_not_suite_classification": True,
            "disposable_project_cleanup_rule": "delete only after checksum verification, ZIP write, ZIP test, duplicate scan, and forbidden-entry scan",
            "forbidden_entries": [".godot", "__MACOSX", "._*", ".DS_Store", "editor state", "nested archives"],
        },
    )
    bad = forbidden_evidence_entries(evidence)
    if bad:
        raise RuntimeError(f"forbidden evidence entries: {bad[:20]}")
    count = checksum_inventory(evidence)
    ok, checksum_errors = verify_checksum_inventory(evidence)
    if not ok:
        raise RuntimeError(f"evidence checksum verification failed: {checksum_errors[:20]}")
    deterministic_zip(evidence, output_zip)
    with zipfile.ZipFile(output_zip) as archive:
        bad_member = archive.testzip()
        names = archive.namelist()
    if bad_member is not None:
        raise RuntimeError(f"evidence ZIP failed at {bad_member}")
    if len(names) != len(set(names)):
        raise RuntimeError("evidence ZIP duplicate entries")
    return {"durably_packaged": True, "checksum_record_count": count, "zip_path": str(output_zip), "zip_byte_size": output_zip.stat().st_size, "zip_sha256": sha256(output_zip), "exit_code": exit_code}


def terminal(evidence: pathlib.Path, output_zip: pathlib.Path, durable: dict[str, Any], **kwargs: Any) -> int:
    packaged = finalize_terminal(evidence, output_zip, **kwargs)
    durable.update(packaged)
    print(json.dumps(packaged, sort_keys=True))
    return int(kwargs["exit_code"])


def execute(args: argparse.Namespace, evidence: pathlib.Path, output_zip: pathlib.Path, version: str, durable: dict[str, Any]) -> int:
    disposable_parent = pathlib.Path(tempfile.mkdtemp(prefix="district-zero-v124i-"))
    selected = disposable_parent / "selected"
    try:
        copied = copy_selected_project(selected, evidence)
        if copied["status"] != "PASS":
            return terminal(evidence, output_zip, durable, status="BLOCKED/NOT TESTABLE", stage="COPY_SELECTED_PROJECT", instruction="Stop; disposable copy identity failed.", details=copied, exit_code=2)
        preflight = import_and_parse_preflight(selected, evidence, args.godot, version)
        if preflight["status"] != "PASS":
            return terminal(evidence, output_zip, durable, status="BLOCKED/NOT TESTABLE", stage="DISPOSABLE_IMPORT_AND_RUNNER_PARSE", instruction="Stop before gameplay vectors; import/class/runner parse preflight is not green.", details=preflight, exit_code=2)
        preflight_path = evidence / "DISPOSABLE_IMPORT" / "result.json"

        fast = run_v6_fast_route_gate(selected, evidence, args.godot, preflight_path)
        if fast["status"] != "PASS":
            terminal_status = "BLOCKED/NOT TESTABLE" if fast["status"] == "BLOCKED/NOT TESTABLE" else "FAIL"
            return terminal(evidence, output_zip, durable, status=terminal_status, stage="FAST_ROUTE_GATE", instruction="Stop with exact V6 evidence; do not change movement/world and do not run C1/full suite.", details=fast, exit_code=2 if terminal_status.startswith("BLOCKED") else 1)

        selected_candidate = str(fast["selected_candidate_id"])
        c1 = run_selected_c1(selected, pathlib.Path(args.p0_root).resolve(), evidence, args.godot)
        if c1["status"] != "PASS":
            terminal_status = "BLOCKED/NOT TESTABLE" if c1["status"] == "BLOCKED/NOT TESTABLE" else "FAIL"
            return terminal(evidence, output_zip, durable, status=terminal_status, stage="C1_SELECTED", instruction="Stop with selected-C1 evidence; do not run complete suite.", details=c1, exit_code=2 if terminal_status.startswith("BLOCKED") else 1)

        full = run_suite_stage(selected, evidence, args.godot, preflight_path, "COMPLETE_40_VECTOR_SUITE", None, selected_candidate, fail_fast=False)
        if full["status"] != "PASS":
            terminal_status = "BLOCKED/NOT TESTABLE" if full["status"] == "BLOCKED/NOT TESTABLE" else "FAIL"
            return terminal(evidence, output_zip, durable, status=terminal_status, stage="COMPLETE_40_VECTOR_SUITE", instruction="Stop with complete-suite evidence; Human World Gate remains unauthorized.", details=full, exit_code=2 if terminal_status.startswith("BLOCKED") else 1)
        return terminal(evidence, output_zip, durable, status="PASS", stage="COMPLETE_40_VECTOR_SUITE", instruction="40/40 automated PASS authorizes—but does not conduct—the Human World Gate. Stop before human testing and P1B.", details=full, exit_code=0)
    finally:
        if durable.get("durably_packaged"):
            shutil.rmtree(disposable_parent, ignore_errors=False)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--godot", required=True)
    parser.add_argument("--p0-root", required=True)
    parser.add_argument("--baseline-root", required=True)
    parser.add_argument("--evidence-dir", required=True)
    parser.add_argument("--standalone-evidence-zip")
    args = parser.parse_args()
    evidence = pathlib.Path(args.evidence_dir).resolve()
    if evidence == ROOT or ROOT in evidence.parents:
        raise SystemExit("--evidence-dir must be outside packet root")
    output_zip = pathlib.Path(args.standalone_evidence_zip).resolve() if args.standalone_evidence_zip else evidence.parent / f"{evidence.name}.zip"
    if evidence.exists():
        shutil.rmtree(evidence)
    evidence.mkdir(parents=True)
    durable: dict[str, Any] = {}

    static = run_static_verifier(args, evidence)
    if static["status"] != "PASS":
        return terminal(evidence, output_zip, durable, status="BLOCKED/NOT TESTABLE", stage="STATIC_VERIFIER", instruction="Stop before exact-engine work; static identity is not green.", details=static, exit_code=2)
    engine = run_engine_identity(args.godot, evidence)
    if engine["status"] != "PASS":
        return terminal(evidence, output_zip, durable, status="BLOCKED/NOT TESTABLE", stage="ENGINE_IDENTITY", instruction="Stop before disposable copy; exact engine is unavailable/mismatched.", details=engine, exit_code=2)
    return execute(args, evidence, output_zip, str(engine["observed"]), durable)


if __name__ == "__main__":
    raise SystemExit(main())
