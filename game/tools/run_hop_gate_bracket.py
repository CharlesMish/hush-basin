#!/usr/bin/env python3
"""Execute the preregistered v1.2.4D HOP gate and its locked validation lane."""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import pathlib
import shutil
import subprocess
import sys
import tempfile
import zipfile


REQUIRED_ENGINE = "4.7.1.stable.official.a13da4feb"
QUESTIONS = [
    "RT_HOP_DIRECT_NON_HOP_SPAN",
    "RT_HOP_SUCCESS",
    "RT_HOP_NO_SLIP_NORTH",
    "RT_HOP_NO_SLIP_SOUTH",
]
FORBIDDEN_PARTS = {"__MACOSX", ".godot", ".cache", "cache", "caches", "logs"}
FORBIDDEN_SUFFIXES = {".pyc", ".pyo", ".log", ".tmp", ".zip", ".7z", ".rar", ".tar", ".tgz", ".gz"}


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def dump(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(obj, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def write_text(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(cmd, cwd=None):
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, check=False)


def forbidden_reason(relative):
    parts = relative.parts
    for part in parts:
        lowered = part.lower()
        if part in FORBIDDEN_PARTS or "pycache" in lowered:
            return f"forbidden path component {part!r}"
        if part == ".DS_Store" or part.startswith("._"):
            return f"forbidden Mac transport metadata {part!r}"
    if relative.suffix.lower() in FORBIDDEN_SUFFIXES:
        return f"forbidden archive/cache/log suffix {relative.suffix!r}"
    return None


def assert_clean_tree(root):
    for path in root.rglob("*"):
        reason = forbidden_reason(path.relative_to(root))
        if reason:
            raise RuntimeError(f"{reason}: {path.relative_to(root).as_posix()}")


def assert_outside(path, roots, label):
    resolved = path.resolve()
    for root in roots:
        root = root.resolve()
        if resolved == root or root in resolved.parents:
            raise RuntimeError(f"{label} must be outside {root}")


def checksum_rows(root, excluded_name):
    files = sorted(
        (
            path
            for path in root.rglob("*")
            if path.is_file() and path.name != excluded_name
        ),
        key=lambda path: path.relative_to(root).as_posix().encode(),
    )
    return [f"{sha(path)}  {path.relative_to(root).as_posix()}\n" for path in files]


def sums(root):
    assert_clean_tree(root)
    write_text(root / "SHA256SUMS.txt", "".join(checksum_rows(root, "SHA256SUMS.txt")))


def packet_sums(root):
    assert_clean_tree(root)
    write_text(
        root / "PACKET_SHA256SUMS.txt",
        "".join(checksum_rows(root, "PACKET_SHA256SUMS.txt")),
    )


def verify_inventory(root, inventory_name):
    inventory = root / inventory_name
    expected = {}
    for line in inventory.read_text(encoding="utf-8").splitlines():
        digest, relative = line.split("  ", 1)
        expected[relative] = digest
    actual = {
        path.relative_to(root).as_posix(): sha(path)
        for path in root.rglob("*")
        if path.is_file() and path.name != inventory_name
    }
    if actual != expected:
        missing = sorted(set(expected) - set(actual))[:8]
        extra = sorted(set(actual) - set(expected))[:8]
        changed = sorted(
            relative
            for relative in set(actual) & set(expected)
            if actual[relative] != expected[relative]
        )[:8]
        raise RuntimeError(
            f"{inventory_name} mismatch missing={missing} extra={extra} changed={changed}"
        )
    return len(actual)


def deterministic_zip(source, output):
    assert_clean_tree(source)
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in sorted(
            (path for path in source.rglob("*") if path.is_file()),
            key=lambda path: path.relative_to(source).as_posix().encode(),
        ):
            relative = path.relative_to(source).as_posix()
            info = zipfile.ZipInfo(relative, (1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, path.read_bytes())


def verify_zip(output, inventory_name):
    with tempfile.TemporaryDirectory(prefix="district-zero-zip-check-") as temporary:
        extracted = pathlib.Path(temporary) / "root"
        extracted.mkdir()
        with zipfile.ZipFile(output) as archive:
            for name in archive.namelist():
                relative = pathlib.PurePosixPath(name)
                if relative.is_absolute() or ".." in relative.parts:
                    raise RuntimeError(f"unsafe ZIP member {name!r}")
                reason = forbidden_reason(pathlib.Path(*relative.parts))
                if reason:
                    raise RuntimeError(f"{reason} in ZIP member {name!r}")
            archive.extractall(extracted)
        assert_clean_tree(extracted)
        records = verify_inventory(extracted, inventory_name)
    return {"path": str(output), "sha256": sha(output), "checksum_records": records}


def materialize(source, work, candidate_id, offset=None):
    cmd = [
        sys.executable,
        "-B",
        str(source / "tools/materialize_hop_bar_candidate.py"),
        "--source-root",
        str(source),
        "--output-root",
        str(work),
        "--candidate-id",
        candidate_id,
    ]
    if offset is not None:
        cmd += ["--selected-hop-offset-m", format(offset, ".12g")]
    completed = run(cmd)
    if completed.returncode != 0:
        raise RuntimeError(
            "candidate materialization failed: " + completed.stdout + "\n" + completed.stderr
        )
    assert_clean_tree(work)


def vector_trial(root, godot, vector_id, output, offset=None):
    evidence = output / "evidence"
    report = output / "result.json"
    cmd = [
        sys.executable,
        "-B",
        str(root / "tools/run_p1a_runtime_suite.py"),
        "--godot",
        godot,
        "--only",
        vector_id,
        "--output",
        str(report),
        "--evidence-dir",
        str(evidence),
    ]
    if offset is not None:
        cmd += ["--hop-offset-m", format(offset, ".12g")]
    completed = run(cmd, cwd=root)
    write_text(output / "wrapper_stdout.txt", completed.stdout)
    write_text(output / "wrapper_stderr.txt", completed.stderr)
    dump(output / "wrapper_argv.json", {"argv": cmd, "cwd": str(root)})
    if not report.is_file():
        return {
            "id": vector_id,
            "status": "FAIL",
            "failures": ["suite wrapper emitted no report"],
            "wrapper_returncode": completed.returncode,
        }
    report_data = load(report)
    result = (
        report_data.get("results", [{}])[0]
        if report_data.get("results")
        else {
            "id": vector_id,
            "status": "FAIL",
            "failures": [report_data.get("blocker", "no result")],
        }
    )
    result["wrapper_returncode"] = completed.returncode
    if offset is not None and any(
        "supported-Hop bracket requires --hop-offset-m" in failure
        for failure in result.get("failures", [])
    ):
        raise RuntimeError(
            "TEST_DRIVER: supported-Hop offset was present in argv but unresolved by the runtime controller"
        )
    return result


def adjacent_passes(offsets, passed):
    return any(offsets[index] in passed and offsets[index + 1] in passed for index in range(len(offsets) - 1))


def choose_offset(results):
    def key(item):
        offset, result = item
        clearance = result.get("hop_gate_evidence", {}).get(
            "minimum_bar_overlap_vertical_clearance_m"
        )
        clearance = -1e99 if clearance is None else float(clearance)
        return (-clearance, abs(offset), offset)

    return sorted(results.items(), key=key)[0][0]


def find_p0_root(path):
    path = path.resolve()
    if (path / "project.godot").is_file():
        return path
    hits = [candidate.parent for candidate in path.rglob("project.godot")]
    if len(hits) != 1:
        raise RuntimeError(f"P0 root must contain exactly one project.godot, found {len(hits)}")
    return hits[0]


def repair_support_controller_order(root):
    """Apply the authorized controller init-order fix only to a disposable copy."""
    path = root / "tests/p1a_runtime_runner.gd"
    text = path.read_text(encoding="utf-8")
    assignment = (
        '\thop_timing_offset_m = _resolved_hop_timing_offset(vector.get("controller_commands", {})) '
        'if String(vector.get("controller_commands", {}).get("type", "")) == '
        '"SUPPORTED_HOP_BRACKET_CONTROLLER" else INF\n'
    )
    validation = "\tpreflight_failures = _validate_vector_contract()\n"
    if text.count(assignment) != 1 or text.count(validation) != 1:
        raise RuntimeError("support-controller init-order repair anchors do not resolve exactly once")
    before = sha(path)
    text = text.replace(assignment, "", 1)
    text = text.replace(validation, assignment + validation, 1)
    path.write_text(text, encoding="utf-8", newline="\n")
    return {
        "classification": "TEST_DRIVER",
        "scope": "disposable runtime copy only",
        "repair": "resolve preregistered Hop offset before vector contract validation",
        "before_sha256": before,
        "after_sha256": sha(path),
    }


def prepare_godot_copy(root, godot, evidence, prefix="import", repair=None):
    """Build editor-local script-class state only inside a disposable runtime copy."""
    evidence.mkdir(parents=True, exist_ok=True)
    cmd = [
        godot,
        "--headless",
        "--log-file",
        str(evidence / f"{prefix}_engine.txt"),
        "--path",
        str(root),
        "--import",
    ]
    completed = run(cmd)
    dump(evidence / f"{prefix}_argv.json", {"argv": cmd})
    write_text(evidence / f"{prefix}_stdout.txt", completed.stdout)
    write_text(evidence / f"{prefix}_stderr.txt", completed.stderr)
    cache = root / ".godot/global_script_class_cache.cfg"
    result = {
        "returncode": completed.returncode,
        "global_script_class_cache_created": cache.is_file(),
        "status": "PASS" if completed.returncode == 0 and cache.is_file() else "FAIL",
    }
    if repair is not None:
        result["support_controller_repair"] = repair
    dump(evidence / f"{prefix}_result.json", result)
    return result["status"] == "PASS", result


def run_c1(candidate, p0_root, godot, evidence):
    """Run both C1 sides from disposable copies and retain only named evidence."""
    evidence.mkdir(parents=True, exist_ok=True)
    p0_source = find_p0_root(p0_root)
    result = {"status": "FAIL", "stage": "setup", "records": []}
    temporary_path = None
    with tempfile.TemporaryDirectory(prefix="district-zero-c1-") as temporary:
        temporary_path = pathlib.Path(temporary).resolve()
        assert_outside(temporary_path, [candidate, evidence], "C1 temporary root")
        p0_copy = temporary_path / "p0"
        candidate_copy = temporary_path / "candidate"
        shutil.copytree(p0_source, p0_copy)
        shutil.copytree(candidate, candidate_copy)
        (p0_copy / "tests").mkdir(exist_ok=True)
        shutil.copy2(
            candidate_copy / "tests/p1a_baseline_runner.gd",
            p0_copy / "tests/p1a_baseline_runner.gd",
        )
        p0_trace = evidence / "C1_p0_trace.jsonl"
        candidate_trace = evidence / "C1_p1a_trace.jsonl"
        prepared = True
        for name, runtime_root in [("p0", p0_copy), ("p1a", candidate_copy)]:
            ok, import_result = prepare_godot_copy(
                runtime_root, godot, evidence, f"C1_{name}_import"
            )
            result["records"].append({"name": f"{name}_import", **import_result})
            if not ok:
                result.update(status="FAIL", stage=f"{name}_import")
                prepared = False
                break
        if prepared:
            commands = [
                [
                    godot,
                    "--headless",
                    "--log-file",
                    str(evidence / "C1_p0_engine.txt"),
                    "--path",
                    str(p0_copy),
                    "--fixed-fps",
                    "60",
                    "--script",
                    "res://tests/p1a_baseline_runner.gd",
                    "--",
                    "--output",
                    str(p0_trace),
                ],
                [
                    godot,
                    "--headless",
                    "--log-file",
                    str(evidence / "C1_p1a_engine.txt"),
                    "--path",
                    str(candidate_copy),
                    "--fixed-fps",
                    "60",
                    "--script",
                    "res://tests/p1a_baseline_runner.gd",
                    "--",
                    "--output",
                    str(candidate_trace),
                ],
            ]
            traces = [p0_trace, candidate_trace]
            ran = True
            for name, cmd, trace in zip(["p0", "p1a"], commands, traces):
                completed = run(cmd)
                write_text(evidence / f"C1_{name}_stdout.txt", completed.stdout)
                write_text(evidence / f"C1_{name}_stderr.txt", completed.stderr)
                dump(evidence / f"C1_{name}_argv.json", {"argv": cmd})
                result["records"].append(
                    {
                        "name": name,
                        "returncode": completed.returncode,
                        "trace_created": trace.is_file(),
                    }
                )
                if completed.returncode != 0 or not trace.is_file():
                    result.update(status="FAIL", stage=name)
                    ran = False
                    break
            if ran:
                compare = [
                    sys.executable,
                    "-B",
                    str(candidate_copy / "tools/compare_p1a_baseline.py"),
                    str(p0_trace),
                    str(candidate_trace),
                    str(candidate_copy / "tests/fixtures/baseline_flat_support.json"),
                ]
                completed = run(compare, cwd=candidate_copy)
                write_text(evidence / "C1_compare_stdout.txt", completed.stdout)
                write_text(evidence / "C1_compare_stderr.txt", completed.stderr)
                dump(
                    evidence / "C1_compare_argv.json",
                    {"argv": compare, "cwd": str(candidate_copy)},
                )
                try:
                    result = json.loads(completed.stdout.strip().splitlines()[-1])
                except Exception:
                    result = {"status": "FAIL", "error": "comparator output was not parseable"}
                result["returncode"] = completed.returncode
                result["p0_trace_sha256"] = sha(p0_trace)
                result["p1a_trace_sha256"] = sha(candidate_trace)
    result["disposable_runtime_copies_removed"] = bool(
        temporary_path is not None and not temporary_path.exists()
    )
    dump(evidence / "C1_result.json", result)
    sums(evidence)
    passed = result.get("returncode") == 0 and result.get("status") == "PASS"
    return passed, result


def run_verifier(root, baseline_root, p0_root, evidence):
    cmd = [
        sys.executable,
        "-B",
        str(root / "tools/verify_p1a_implementation.py"),
        "--root",
        str(root),
        "--baseline-root",
        str(baseline_root),
        "--p0-root",
        str(p0_root),
        "--allow-blocked-runtime",
    ]
    completed = run(cmd, cwd=root)
    dump(evidence / "argv.json", {"argv": cmd, "cwd": str(root)})
    write_text(evidence / "stdout.txt", completed.stdout)
    write_text(evidence / "stderr.txt", completed.stderr)
    result = {"returncode": completed.returncode, "status": "PASS" if completed.returncode == 0 else "FAIL"}
    try:
        result["verifier"] = json.loads(completed.stdout if completed.returncode == 0 else completed.stderr)
    except Exception:
        result["parse_error"] = "verifier output was not one JSON object"
    dump(evidence / "result.json", result)
    return completed.returncode == 0, result


def promote_after_c1(root, summary):
    active = load(root / "world/generated/hop_bar_active_candidate.json")
    active["status"] = "SELECTED_ISOLATED_GATE_PASS_C1_PASS"
    active["C1"] = summary["C1"]
    active["isolated_gate_summary"] = summary["isolated_gate"]
    dump(root / "world/generated/hop_bar_active_candidate.json", active)
    current = load(root / "evidence/runtime_vector_results.json")
    current["selected_candidate_id"] = active["candidate_id"]
    current["blocker"] = "complete 40-vector suite authorized but NOT PERFORMED"
    current["isolated_hop_gate_executed_question_count"] = 4
    dump(root / "evidence/runtime_vector_results.json", current)
    dump(root / "evidence/v1_2_4d_hop_gate_selection.json", summary)
    manifest = load(root / "world/p1a_world_manifest.json")
    manifest["status"] = (
        f'HOP CANDIDATE {active["candidate_id"]} SELECTED — isolated four-question gate and C1 PASS; '
        "complete 40-vector suite authorized but NOT PERFORMED"
    )
    manifest["hop_gate_correction"]["status"] = "SELECTED_ISOLATED_GATE_PASS_C1_PASS"
    manifest["hop_gate_correction"]["full_suite_locked"] = False
    manifest["hop_gate_correction"]["active_candidate"]["selection_status"] = (
        "ISOLATED_GATE_PASS_C1_PASS"
    )
    for relative in [
        "world/generated/solid_meshes.json",
        "scripts/p1a_world_data.gd",
        "tests/fixtures/runtime_vectors.json",
        "evidence/runtime_vector_results.json",
    ]:
        record = manifest["required_generated_artifacts"][relative]
        record["raw_byte_sha256"] = sha(root / relative)
        record["byte_length"] = (root / relative).stat().st_size
    dump(root / "world/p1a_world_manifest.json", manifest)
    packet_sums(root)


def run_full_suite(selected, godot, evidence):
    """Run all 40 vectors from a disposable selected-root copy."""
    evidence.mkdir(parents=True, exist_ok=True)
    temporary_path = None
    result = {"status": "FAIL", "blocker": "full-suite wrapper emitted no report"}
    with tempfile.TemporaryDirectory(prefix="district-zero-full-suite-") as temporary:
        temporary_path = pathlib.Path(temporary).resolve()
        assert_outside(temporary_path, [selected, evidence], "full-suite temporary root")
        runtime_copy = temporary_path / "selected"
        shutil.copytree(selected, runtime_copy)
        controller_repair = repair_support_controller_order(runtime_copy)
        import_ok, import_result = prepare_godot_copy(
            runtime_copy,
            godot,
            evidence / "RUNTIME_IMPORT",
            repair=controller_repair,
        )
        if not import_ok:
            result = {
                "status": "FAIL",
                "blocker": "disposable full-suite copy import failed",
                "runtime_import": import_result,
                "wrapper_returncode": None,
            }
            return False, result
        report = evidence / "runtime_vector_results.json"
        runtime_evidence = evidence / "runtime_vectors"
        cmd = [
            sys.executable,
            "-B",
            str(runtime_copy / "tools/run_p1a_runtime_suite.py"),
            "--godot",
            godot,
            "--output",
            str(report),
            "--evidence-dir",
            str(runtime_evidence),
        ]
        completed = run(cmd, cwd=runtime_copy)
        dump(evidence / "wrapper_argv.json", {"argv": cmd, "cwd": str(runtime_copy)})
        write_text(evidence / "wrapper_stdout.txt", completed.stdout)
        write_text(evidence / "wrapper_stderr.txt", completed.stderr)
        if report.is_file():
            result = load(report)
        result["wrapper_returncode"] = completed.returncode
    result["disposable_runtime_copy_removed"] = bool(
        temporary_path is not None and not temporary_path.exists()
    )
    dump(evidence / "full_suite_result.json", result)
    return result.get("status") == "PASS" and result.get("wrapper_returncode") == 0, result


def finalize_evidence(evidence, output, summary):
    dump(evidence / "hop_gate_bracket_result.json", summary)
    sums(evidence)
    evidence_zip = output / "District-Zero-P1A-v1.2.4D-Validation-Evidence.zip"
    deterministic_zip(evidence, evidence_zip)
    identity = verify_zip(evidence_zip, "SHA256SUMS.txt")
    return evidence_zip, identity


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--godot", required=True)
    parser.add_argument(
        "--source-root", default=str(pathlib.Path(__file__).resolve().parents[1])
    )
    parser.add_argument("--baseline-root", required=True)
    parser.add_argument("--p0-root", required=True)
    parser.add_argument("--output-root", required=True)
    args = parser.parse_args()

    source = pathlib.Path(args.source_root).resolve()
    baseline_root = pathlib.Path(args.baseline_root).resolve()
    p0_root = pathlib.Path(args.p0_root).resolve()
    output = pathlib.Path(args.output_root).resolve()
    assert_outside(output, [source], "output root")
    output.mkdir(parents=True, exist_ok=True)
    evidence = output / "District-Zero-P1A-v1.2.4D-Validation-Evidence"
    if evidence.exists() and any(evidence.iterdir()):
        raise RuntimeError(f"evidence root is not empty: {evidence}")
    evidence.mkdir(exist_ok=True)

    try:
        version = run([args.godot, "--version"]).stdout.strip()
    except OSError as exc:
        print(json.dumps({"status": "BLOCKED/NOT TESTABLE", "blocker": str(exc)}))
        return 2
    if version != REQUIRED_ENGINE:
        print(
            json.dumps(
                {
                    "status": "BLOCKED/NOT TESTABLE",
                    "blocker": "exact Godot version mismatch",
                    "observed": version,
                    "required": REQUIRED_ENGINE,
                }
            )
        )
        return 2

    fixture = load(source / "tests/fixtures/hop_gate_bracket.json")
    registry = load(source / "world/generated/hop_bar_bracket_candidates.json")
    checkpoint_path = source / fixture["run4_resume_checkpoint"]["path"]
    checkpoint = load(checkpoint_path)
    resume = checkpoint["resume"]
    resume_candidate_id = resume["candidate_id"]
    if resume.get("skip_source_C1_prerequisite") is not True or resume.get("skip_Q2_for_resume_candidate") is not True:
        raise RuntimeError("Run-4 resume checkpoint does not authorize the required C1/Q2 skips")
    offsets = [float(value) for value in fixture["question_order"][1]["timing_offset_scan_m"]]
    if offsets != [float(value) for value in resume["timing_offsets_m"]]:
        raise RuntimeError("Run-4 resume offsets do not match the preregistered Q1 scan")
    candidate_ids = [entry["candidate_id"] for entry in registry["candidates"]]
    if candidate_ids.count(resume_candidate_id) != 1:
        raise RuntimeError("Run-4 resume candidate must resolve exactly once")
    resume_index = candidate_ids.index(resume_candidate_id)
    if any(float(entry["top_y_m"]) < float(resume["top_y_m"]) for entry in registry["candidates"][resume_index:]):
        raise RuntimeError("candidate registry is not monotonic at Run-4 resume point")
    work = output / ".candidate_work"
    summary = {
        "schema": "district_zero.p1a.hop_gate_bracket_result.v1",
        "authority_version": "1.2.4D",
        "engine_version": version,
        "run_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "run4_resume_checkpoint": checkpoint,
        "candidate_trials": [],
        "status": "RUNNING",
        "human_world_gate": "NOT PERFORMED",
        "P1B": "FROZEN",
    }
    dump(evidence / "RUN4_RESUME_CHECKPOINT.json", checkpoint)

    # v1.2.4D does not rerun preserved source C1 or Q2. It discards the historical
    # fixed-horizon Q1 classification, runs all five offsets fresh with event-based
    # completion, then preserves the existing adjacency/repetition locks.
    summary["C1_source_prerequisite"] = {
        "status": checkpoint["source_C1"]["status"],
        "maximum_delta": checkpoint["source_C1"]["maximum_delta"],
        "evidence_basis": checkpoint["evidence_disposition"],
        "rerun_in_v1_2_4d": False,
    }
    print("[Run-4 checkpoint] source C1 PASS/max delta 0.0 preserved; lower Q2 reruns skipped", flush=True)

    selected = None
    try:
        for entry in registry["candidates"][resume_index:]:
            candidate_id = entry["candidate_id"]
            materialize(source, work, candidate_id)
            controller_repair = repair_support_controller_order(work)
            import_ok, import_result = prepare_godot_copy(
                work,
                args.godot,
                evidence / candidate_id / "RUNTIME_IMPORT",
                repair=controller_repair,
            )
            if not import_ok:
                raise RuntimeError(
                    f"candidate disposable-copy import failed for {candidate_id}: {import_result}"
                )
            candidate_summary = {
                "candidate_id": candidate_id,
                "top_y_m": entry["top_y_m"],
                "direct": [],
            }
            if candidate_id == resume_candidate_id:
                preserved = checkpoint["Q2_first_robust_denial"]
                candidate_summary["direct"] = [{
                    "status": "PASS",
                    "evidence_basis": checkpoint["evidence_disposition"],
                    "preserved_repetition_count": preserved["repetitions"],
                    "rerun_in_v1_2_4d": False,
                }]
                direct_ok = preserved["status"] == "PASS_ROBUST_DIRECT_DENIAL" and int(preserved["pass_count"]) == 3
                print(f"[{candidate_id}] Q2 3/3 preserved; resuming Q1 offset scan", flush=True)
            else:
                print(f"[{candidate_id}] Q2 direct denial: 3 repetitions", flush=True)
                direct_ok = True
                for repetition in range(1, int(fixture["candidate_acceptance"]["direct_repetitions"]) + 1):
                    result = vector_trial(
                        work,
                        args.godot,
                        "RT_HOP_DIRECT_NON_HOP_SPAN",
                        evidence / candidate_id / "Q2_DIRECT" / f"rep_{repetition:02d}",
                    )
                    candidate_summary["direct"].append(result)
                    direct_ok &= result.get("status") == "PASS"
                    print(f"[{candidate_id}] Q2 rep {repetition}: {result.get('status')}", flush=True)
            if not direct_ok:
                summary["candidate_trials"].append(candidate_summary)
                continue

            print(f"[{candidate_id}] Q1 support-ready offset scan", flush=True)
            hop_results = {}
            for offset in offsets:
                result = vector_trial(
                    work,
                    args.godot,
                    "RT_HOP_SUCCESS",
                    evidence / candidate_id / "Q1_SUPPORTED" / ("offset_%+.2f" % offset),
                    offset,
                )
                hop_results[offset] = result
                print(f"[{candidate_id}] Q1 offset {offset:+.2f}: {result.get('status')}", flush=True)
            passed = {offset for offset, result in hop_results.items() if result.get("status") == "PASS"}
            candidate_summary["supported_offset_scan"] = {str(key): value for key, value in hop_results.items()}
            if not adjacent_passes(offsets, passed):
                support_ready_offsets = [
                    offset for offset, result in hop_results.items()
                    if int(result.get("hop_gate_evidence", {}).get("support_ready_tick", -1)) >= 0
                ]
                if not support_ready_offsets:
                    candidate_summary["stop"] = "TEST_DRIVER_SUPPORT_READINESS_UNESTABLISHED"
                    summary["candidate_trials"].append(candidate_summary)
                    summary.update(
                        status="TEST_DRIVER_BLOCKED",
                        blocker=(
                            "corrected readiness still produced no SUPPORT_READY offset; no powered Hop attempt exists, "
                            "so NO_HEIGHT_ONLY_GEOMETRY_INTERVAL is not established"
                        ),
                    )
                    break
                candidate_summary["stop"] = "NO_HEIGHT_ONLY_GEOMETRY_INTERVAL"
                summary["candidate_trials"].append(candidate_summary)
                summary.update(
                    status="NO_HEIGHT_ONLY_GEOMETRY_INTERVAL",
                    blocker=(
                        "preserved first robust direct-denial height has valid support readiness but no two adjacent "
                        "passing supported-Hop timing offsets"
                    ),
                )
                break

            offset = choose_offset({key: value for key, value in hop_results.items() if key in passed})
            candidate_summary["selected_offset_m"] = offset
            candidate_summary["supported_repeats"] = []
            robust = True
            for repetition in range(1, int(fixture["candidate_acceptance"]["selected_supported_hop_repetitions"]) + 1):
                result = vector_trial(
                    work,
                    args.godot,
                    "RT_HOP_SUCCESS",
                    evidence / candidate_id / "Q1_SUPPORTED_SELECTED" / f"rep_{repetition:02d}",
                    offset,
                )
                candidate_summary["supported_repeats"].append(result)
                robust &= result.get("status") == "PASS"
                print(f"[{candidate_id}] Q1 selected rep {repetition}: {result.get('status')}", flush=True)
            if not robust:
                candidate_summary["stop"] = "NO_ROBUST_HEIGHT_ONLY_GEOMETRY_INTERVAL"
                summary["candidate_trials"].append(candidate_summary)
                summary.update(
                    status="NO_HEIGHT_ONLY_GEOMETRY_INTERVAL",
                    blocker="selected timing offset did not repeat robustly at the preserved first direct-denial height",
                )
                break

            all_seams = True
            for vector_id, label, key in [
                ("RT_HOP_NO_SLIP_NORTH", "Q3_NORTH", "north"),
                ("RT_HOP_NO_SLIP_SOUTH", "Q4_SOUTH", "south"),
            ]:
                candidate_summary[key] = []
                for repetition in range(1, int(fixture["candidate_acceptance"][key + "_repetitions"]) + 1):
                    result = vector_trial(
                        work, args.godot, vector_id,
                        evidence / candidate_id / label / f"rep_{repetition:02d}",
                    )
                    candidate_summary[key].append(result)
                    all_seams &= result.get("status") == "PASS"
                    print(f"[{candidate_id}] {label} rep {repetition}: {result.get('status')}", flush=True)
            summary["candidate_trials"].append(candidate_summary)
            if not all_seams:
                continue
            selected = (entry, offset, candidate_summary)
            break
    finally:
        if work.exists():
            shutil.rmtree(work)

    if selected is None:
        if summary["status"] == "RUNNING":
            summary.update(
                status="NO_HEIGHT_ONLY_GEOMETRY_INTERVAL",
                blocker="no candidate through 1.800 m passed all four isolated questions",
            )
        evidence_zip, evidence_identity = finalize_evidence(evidence, output, summary)
        print(
            json.dumps(
                {
                    "status": summary["status"],
                    "evidence": str(evidence),
                    "evidence_zip": str(evidence_zip),
                    "evidence_zip_sha256": evidence_identity["sha256"],
                },
                sort_keys=True,
            )
        )
        return 1

    entry, offset, _candidate_summary = selected
    selected_root = output / "District-Zero-P1A-v1.2.4D-Selected"
    materialize(source, selected_root, entry["candidate_id"], offset)
    c1_directory = evidence / entry["candidate_id"] / "C1_SELECTED"
    print(f'[{entry["candidate_id"]}] selected C1 starting from disposable copies', flush=True)
    c1_ok, c1_result = run_c1(selected_root, p0_root, args.godot, c1_directory)
    summary["isolated_gate"] = {
        "status": "PASS",
        "candidate_id": entry["candidate_id"],
        "top_y_m": entry["top_y_m"],
        "selected_timing_offset_m": offset,
        "questions": QUESTIONS,
    }
    summary["C1"] = c1_result
    summary["selected_candidate_root"] = str(selected_root)
    if not c1_ok:
        summary.update(
            status="SELECTED_ISOLATED_GATE_PASS_C1_FAIL",
            blocker="selected-candidate C1 zero-delta failed; complete suite remains locked",
        )
        evidence_zip, evidence_identity = finalize_evidence(evidence, output, summary)
        print(
            json.dumps(
                {
                    "status": summary["status"],
                    "selected_root": str(selected_root),
                    "evidence_zip": str(evidence_zip),
                    "evidence_zip_sha256": evidence_identity["sha256"],
                },
                sort_keys=True,
            )
        )
        return 1

    summary["status"] = "SELECTED_ISOLATED_GATE_PASS_C1_PASS"
    promote_after_c1(selected_root, summary)
    verify_ok, verify_result = run_verifier(
        selected_root,
        baseline_root,
        p0_root,
        evidence / entry["candidate_id"] / "POST_PROMOTION_VERIFIER",
    )
    summary["post_promotion_verifier"] = verify_result
    if not verify_ok:
        summary.update(
            status="SELECTED_POST_PROMOTION_VERIFIER_FAIL",
            blocker="selected root failed strengthened verifier; complete suite remains locked",
        )
        evidence_zip, evidence_identity = finalize_evidence(evidence, output, summary)
        print(
            json.dumps(
                {
                    "status": summary["status"],
                    "selected_root": str(selected_root),
                    "evidence_zip": str(evidence_zip),
                    "evidence_zip_sha256": evidence_identity["sha256"],
                },
                sort_keys=True,
            )
        )
        return 1

    print("[40-vector suite] starting from a separate disposable selected-root copy", flush=True)
    full_ok, full_result = run_full_suite(
        selected_root, args.godot, evidence / entry["candidate_id"] / "COMPLETE_40_VECTOR_SUITE"
    )
    summary["complete_runtime_suite"] = full_result
    summary["status"] = "PASS" if full_ok else "COMPLETE_40_VECTOR_SUITE_FAIL"
    if not full_ok:
        summary["blocker"] = "complete 40-vector suite did not pass; human World Gate remains locked"

    source_zip = output / "District-Zero-P1A-v1.2.4D-Selected-Source.zip"
    deterministic_zip(selected_root, source_zip)
    source_identity = verify_zip(source_zip, "PACKET_SHA256SUMS.txt")
    summary["selected_source_zip"] = source_identity
    summary["selected_source_packet_records"] = verify_inventory(
        selected_root, "PACKET_SHA256SUMS.txt"
    )

    # Re-run the strengthened verifier from a fresh extraction of the exact source ZIP.
    with tempfile.TemporaryDirectory(prefix="district-zero-source-verify-") as temporary:
        extracted = pathlib.Path(temporary) / "selected"
        extracted.mkdir()
        with zipfile.ZipFile(source_zip) as archive:
            archive.extractall(extracted)
        fresh_ok, fresh_result = run_verifier(
            extracted,
            baseline_root,
            p0_root,
            evidence / entry["candidate_id"] / "FRESH_EXTRACTION_VERIFIER",
        )
    summary["fresh_extraction_verifier"] = fresh_result
    if not fresh_ok:
        summary.update(
            status="FRESH_EXTRACTION_VERIFIER_FAIL",
            blocker="selected source ZIP fresh extraction failed strengthened verifier",
        )

    evidence_zip, evidence_identity = finalize_evidence(evidence, output, summary)
    identities = {
        "schema": "district_zero.p1a.v1_2_4d.deliverable_identities.v1",
        "selected_source_zip": source_identity,
        "validation_evidence_zip": evidence_identity,
    }
    dump(output / "DELIVERABLE_IDENTITIES.json", identities)
    print(
        json.dumps(
            {
                "status": summary["status"],
                "candidate_id": entry["candidate_id"],
                "top_y_m": entry["top_y_m"],
                "selected_timing_offset_m": offset,
                "selected_root": str(selected_root),
                "source_zip": str(source_zip),
                "source_zip_sha256": source_identity["sha256"],
                "evidence_zip": str(evidence_zip),
                "evidence_zip_sha256": evidence_identity["sha256"],
            },
            sort_keys=True,
        )
    )
    return 0 if summary["status"] == "PASS" else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(
            json.dumps({"status": "BLOCKED/NOT TESTABLE", "blocker": str(exc)}, sort_keys=True),
            file=sys.stderr,
        )
        raise SystemExit(2)
