#!/usr/bin/env python3
"""Exact same-host C1 for R1, with the frozen builder fixture kept out of runnable imports."""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import shutil
import sys
from typing import Any

ROOT_DEFAULT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DEFAULT / "tools"))

from p1a_v1_2_7r1_harness import (
    EXACT_ENGINE,
    dump,
    import_and_parse_project,
    run,
    scan_error_text,
    sha256,
    write,
    write_inventory,
)

BASELINE_RUNNER = "res://tests/p1a_baseline_runner.gd"
FROZEN_BUILDER_FIXTURE = "tests/fixtures/v1_2_7_v1_2_6_world_builder.gd"


def copy_runtime(source: pathlib.Path, destination: pathlib.Path) -> None:
    def ignore(_directory: str, names: list[str]) -> set[str]:
        return {
            name for name in names
            if name in {".godot", "__pycache__", "director_inputs", ".pytest_cache", ".mypy_cache"}
            or name == pathlib.Path(FROZEN_BUILDER_FIXTURE).name
            or name == ".DS_Store"
            or name.startswith("._")
            or name.endswith((".pyc", ".pyo"))
        }

    shutil.copytree(source, destination, ignore=ignore)


def finish(evidence: pathlib.Path, result: dict[str, Any], returncode: int) -> int:
    dump(evidence / "C1_result.json", result)
    write_inventory(evidence, "SHA256SUMS.txt")
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return returncode


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True)
    parser.add_argument("--godot", required=True)
    parser.add_argument("--evidence-dir", required=True)
    parser.add_argument("--work-root", required=True)
    args = parser.parse_args()
    root = pathlib.Path(args.root).resolve()
    evidence = pathlib.Path(args.evidence_dir).resolve()
    work = pathlib.Path(args.work_root).resolve()
    godot = str(pathlib.Path(args.godot).resolve())
    if (evidence.exists() and (not evidence.is_dir() or any(evidence.iterdir()))) or (work.exists() and (not work.is_dir() or any(work.iterdir()))):
        print(json.dumps({"status": "BLOCKED/NOT TESTABLE", "blocker": "C1 outputs are not new/empty"}, sort_keys=True))
        return 2
    evidence.mkdir(parents=True, exist_ok=True)
    work.mkdir(parents=True, exist_ok=True)
    version = run([godot, "--version"], root)
    dump(evidence / "engine_identity.json", {
        "argv": [godot, "--version"],
        "required": EXACT_ENGINE,
        "observed": version.stdout.strip(),
        "stdout": version.stdout,
        "stderr": version.stderr,
        "returncode": version.returncode,
        "match": version.returncode == 0 and version.stdout.strip() == EXACT_ENGINE,
    })
    if version.returncode != 0 or version.stdout.strip() != EXACT_ENGINE:
        return finish(evidence, {"status": "BLOCKED/NOT TESTABLE", "blocker": "exact engine mismatch"}, 2)
    contract = json.loads((root / "tests/fixtures/disposable_import_preflight.json").read_text(encoding="utf-8"))
    required_classes = dict(contract["required_registered_classes"])
    projects = {
        "v1_2_6_runtime_baseline": work / "v1_2_6_runtime_baseline",
        "v1_2_7r1_selected": work / "v1_2_7r1_selected",
    }
    for project in projects.values():
        copy_runtime(root, project)
    baseline_bytes = (root / FROZEN_BUILDER_FIXTURE).read_bytes()
    (projects["v1_2_6_runtime_baseline"] / "scripts/p1a_world_builder.gd").write_bytes(baseline_bytes)
    traces: list[pathlib.Path] = []
    for name, project in projects.items():
        directory = evidence / name
        builder_sha = sha256(project / "scripts/p1a_world_builder.gd")
        imported = import_and_parse_project(
            godot,
            project,
            directory / "IMPORT_PREFLIGHT",
            target_script=BASELINE_RUNNER,
            required_classes=required_classes,
            expected_builder_sha256=builder_sha,
        )
        if imported.get("status") != "PASS":
            return finish(evidence, {
                "status": "BLOCKED/NOT TESTABLE",
                "stage": f"{name}:IMPORT_PREFLIGHT",
                "blocker": "C1 runtime copy failed exact import/parse/class resolution",
            }, 2)
        trace = directory / "trace.jsonl"
        engine_log = directory / "run-engine.txt"
        command = [
            godot,
            "--headless",
            "--log-file",
            str(engine_log),
            "--path",
            str(project),
            "--fixed-fps",
            "60",
            "--script",
            BASELINE_RUNNER,
            "--",
            "--output",
            str(trace),
        ]
        dump(directory / "run-argv.json", {"argv": command, "cwd": str(project)})
        process = run(command, project)
        write(directory / "run-stdout.txt", process.stdout)
        write(directory / "run-stderr.txt", process.stderr)
        if not engine_log.is_file():
            write(engine_log, "")
        runtime_errors = scan_error_text((process.stdout, process.stderr, engine_log.read_text(encoding="utf-8", errors="replace")))
        dump(directory / "run-process-result.json", {
            "returncode": process.returncode,
            "trace_present": trace.is_file(),
            "trace_sha256": sha256(trace) if trace.is_file() else None,
            "recognized_errors": runtime_errors,
        })
        if process.returncode != 0 or not trace.is_file() or runtime_errors:
            return finish(evidence, {
                "status": "BLOCKED/NOT TESTABLE",
                "stage": f"{name}:RUN",
                "blocker": "C1 baseline runner did not execute cleanly",
            }, 2)
        traces.append(trace)
    compare_command = [
        sys.executable,
        "-B",
        str(root / "tools/compare_p1a_baseline.py"),
        str(traces[0]),
        str(traces[1]),
        str(root / "tests/fixtures/baseline_flat_support.json"),
    ]
    comparison = run(compare_command, root)
    dump(evidence / "COMPARE/argv.json", {"argv": compare_command, "cwd": str(root)})
    write(evidence / "COMPARE/stdout.txt", comparison.stdout)
    write(evidence / "COMPARE/stderr.txt", comparison.stderr)
    try:
        result = json.loads(comparison.stdout.strip().splitlines()[-1])
    except Exception:
        result = {"status": "FAIL", "error": "unparseable comparator output"}
    result.update({
        "schema": "district_zero.p1a.v1_2_7r1.c1_result.v1",
        "required_ticks": 1260,
        "exact_engine": EXACT_ENGINE,
        "comparison": "selected v1.2.7R1 vs exact embedded v1.2.6 builder baseline",
        "runtime_fixture_excluded_from_imports": FROZEN_BUILDER_FIXTURE,
    })
    passed = (
        comparison.returncode == 0
        and result.get("status") == "PASS"
        and result.get("ticks_compared") == 1260
        and float(result.get("maximum_absolute_difference", 1.0)) == 0.0
    )
    return finish(evidence, result, 0 if passed else 1)


if __name__ == "__main__":
    raise SystemExit(main())
