#!/usr/bin/env python3
"""Run selected-source C1 with parse-clean exact-engine imports and durable evidence.

The caller owns --work-root and must not delete it until the enclosing v1.2.4J
evidence package has been checksummed and ZIP-tested.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import re
import shutil
import subprocess
import sys
from typing import Any

ROOT = pathlib.Path(__file__).resolve().parents[1]
EXACT = "4.7.1.stable.official.a13da4feb"
EXECUTION_OVERLAY = "1.2.4I"
WORLD_AUTHORITY = "1.2.3"
IMPORT_ERROR_PATTERNS = (
    re.compile(r"SCRIPT ERROR", re.IGNORECASE),
    re.compile(r"Parse Error", re.IGNORECASE),
    re.compile(r"Could not find type", re.IGNORECASE),
    re.compile(r"not declared in the current scope", re.IGNORECASE),
    re.compile(r"Failed to load script", re.IGNORECASE),
    re.compile(r"ERROR:\s+Failed", re.IGNORECASE),
)


def dump(path: pathlib.Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")


def sha(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path: pathlib.Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def run(cmd: list[str], cwd: pathlib.Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, check=False)


def sums(root: pathlib.Path) -> None:
    rows: list[str] = []
    for path in sorted(
        (p for p in root.rglob("*") if p.is_file() and p.name != "SHA256SUMS.txt"),
        key=lambda p: p.relative_to(root).as_posix().encode("utf-8"),
    ):
        rows.append(f"{sha(path)}  {path.relative_to(root).as_posix()}\n")
    write(root / "SHA256SUMS.txt", "".join(rows))


def scan_errors(paths: list[pathlib.Path]) -> list[str]:
    out: list[str] = []
    seen: set[str] = set()
    for path in paths:
        if not path.is_file():
            continue
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            if any(pattern.search(line) for pattern in IMPORT_ERROR_PATTERNS):
                normalized = line.strip()
                if normalized and normalized not in seen:
                    out.append(normalized)
                    seen.add(normalized)
    return out


def discover_script_classes(root: pathlib.Path) -> dict[str, str]:
    classes: dict[str, str] = {}
    for path in sorted((root / "scripts").rglob("*.gd")) if (root / "scripts").is_dir() else []:
        match = re.search(r"(?m)^class_name\s+([A-Za-z_][A-Za-z0-9_]*)\s*$", path.read_text(encoding="utf-8", errors="replace"))
        if match:
            classes[match.group(1)] = "res://" + path.relative_to(root).as_posix()
    return classes


def cache_resolution(cache: pathlib.Path, expected: dict[str, str]) -> tuple[list[str], dict[str, Any]]:
    text = cache.read_text(encoding="utf-8", errors="replace") if cache.is_file() else ""
    missing: list[str] = []
    records: dict[str, Any] = {}
    for name, path in expected.items():
        class_ok = re.search(rf'"class"\s*:\s*&?"{re.escape(name)}"', text) is not None
        path_ok = path in text
        records[name] = {"path": path, "class_entry_present": class_ok, "path_present": path_ok, "resolved": class_ok and path_ok}
        if not class_ok or not path_ok:
            missing.append(name)
    return missing, {
        "cache_generated": cache.is_file() and cache.stat().st_size > 0,
        "cache_byte_size": cache.stat().st_size if cache.is_file() else 0,
        "cache_sha256": sha(cache) if cache.is_file() else None,
        "classes": records,
    }


def import_and_validate(name: str, runtime: pathlib.Path, evidence: pathlib.Path, godot: str, version: str) -> dict[str, Any]:
    prefix = evidence / f"C1_{name}_IMPORT"
    prefix.mkdir(parents=True, exist_ok=True)
    import_engine = prefix / "import_engine.txt"
    import_cmd = [godot, "--headless", "--path", str(runtime), "--import", "--log-file", str(import_engine)]
    dump(prefix / "import_argv.json", {"argv": import_cmd, "cwd": str(runtime)})
    completed = run(import_cmd, cwd=runtime)
    write(prefix / "import_stdout.txt", completed.stdout)
    write(prefix / "import_stderr.txt", completed.stderr)
    if not import_engine.is_file():
        write(import_engine, "")

    validation_engine = prefix / "validation_engine.txt"
    validation_cmd = [godot, "--headless", "--editor", "--quit", "--path", str(runtime), "--log-file", str(validation_engine)]
    dump(prefix / "validation_argv.json", {"argv": validation_cmd, "cwd": str(runtime)})
    validated = run(validation_cmd, cwd=runtime)
    write(prefix / "validation_stdout.txt", validated.stdout)
    write(prefix / "validation_stderr.txt", validated.stderr)
    if not validation_engine.is_file():
        write(validation_engine, "")

    expected_classes = discover_script_classes(runtime)
    missing_classes, cache = cache_resolution(runtime / ".godot" / "global_script_class_cache.cfg", expected_classes)
    dump(prefix / "class_cache_summary.json", cache)
    errors = scan_errors(
        [
            prefix / "import_stdout.txt",
            prefix / "import_stderr.txt",
            import_engine,
            prefix / "validation_stdout.txt",
            prefix / "validation_stderr.txt",
            validation_engine,
        ]
    )
    blockers: list[str] = []
    if version != EXACT:
        blockers.append("exact engine mismatch")
    if completed.returncode != 0:
        blockers.append("import process returned nonzero")
    if validated.returncode != 0:
        blockers.append("validation process returned nonzero")
    if not cache["cache_generated"]:
        blockers.append("global script-class cache was not generated")
    if missing_classes:
        blockers.append(f"registered classes unresolved: {missing_classes}")
    if errors:
        blockers.append("parse/import errors were emitted")
    result = {
        "schema": "district_zero.p1a.v1_2_4j.c1_import_result.v1",
        "status": "PASS" if not blockers else "BLOCKED/NOT TESTABLE",
        "project": name,
        "project_root": str(runtime),
        "required_godot_version": EXACT,
        "observed_godot_version": version,
        "import_returncode": completed.returncode,
        "validation_returncode": validated.returncode,
        "required_class_count": len(expected_classes),
        "missing_classes": missing_classes,
        "parse_error_count": len(errors),
        "parse_errors": errors,
        "blockers": blockers,
    }
    dump(prefix / "result.json", result)
    sums(prefix)
    return result


def copy_without_generated_cache(source: pathlib.Path, destination: pathlib.Path) -> None:
    def ignore(_directory: str, names: list[str]) -> set[str]:
        return {name for name in names if name in {".godot", "__pycache__", "__MACOSX"} or name == ".DS_Store" or name.startswith("._") or name.endswith((".pyc", ".pyo"))}
    shutil.copytree(source, destination, ignore=ignore)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--godot", required=True)
    parser.add_argument("--p0-root", required=True)
    parser.add_argument("--evidence-dir", required=True)
    parser.add_argument("--work-root", required=True)
    args = parser.parse_args()

    p0 = pathlib.Path(args.p0_root).resolve()
    evidence = pathlib.Path(args.evidence_dir).resolve()
    work = pathlib.Path(args.work_root).resolve()
    if evidence.exists():
        shutil.rmtree(evidence)
    evidence.mkdir(parents=True)
    if work.exists():
        shutil.rmtree(work)
    work.mkdir(parents=True)

    try:
        version_process = run([args.godot, "--version"], cwd=ROOT)
        version = version_process.stdout.strip()
    except OSError as exc:
        dump(evidence / "C1_result.json", {"status": "BLOCKED/NOT TESTABLE", "blocker": str(exc)})
        sums(evidence)
        return 2
    dump(evidence / "engine_identity.json", {"required": EXACT, "observed": version, "match": version == EXACT})
    if version != EXACT:
        dump(evidence / "C1_result.json", {"status": "BLOCKED/NOT TESTABLE", "blocker": "exact Godot version mismatch", "observed": version, "required": EXACT})
        sums(evidence)
        return 2

    p0_copy = work / "p0"
    p1_copy = work / "p1a"
    copy_without_generated_cache(p0, p0_copy)
    copy_without_generated_cache(ROOT, p1_copy)
    (p0_copy / "tests").mkdir(exist_ok=True)
    shutil.copy2(p1_copy / "tests" / "p1a_baseline_runner.gd", p0_copy / "tests" / "p1a_baseline_runner.gd")

    traces: list[pathlib.Path] = []
    for name, runtime in (("p0", p0_copy), ("p1a", p1_copy)):
        imported = import_and_validate(name, runtime, evidence, args.godot, version)
        if imported["status"] != "PASS":
            dump(
                evidence / "C1_result.json",
                {
                    "status": "BLOCKED/NOT TESTABLE",
                    "stage": f"{name}_import",
                    "blocker": imported["blockers"],
                    "execution_overlay_authority_version": EXECUTION_OVERLAY,
                    "world_data_authority_version": WORLD_AUTHORITY,
                },
            )
            sums(evidence)
            return 2

        trace = evidence / f"C1_{name}_trace.jsonl"
        traces.append(trace)
        engine = evidence / f"C1_{name}_engine.txt"
        cmd = [
            args.godot,
            "--headless",
            "--log-file",
            str(engine),
            "--path",
            str(runtime),
            "--fixed-fps",
            "60",
            "--script",
            "res://tests/p1a_baseline_runner.gd",
            "--",
            "--output",
            str(trace),
        ]
        completed = run(cmd, cwd=runtime)
        dump(evidence / f"C1_{name}_argv.json", {"argv": cmd, "cwd": str(runtime)})
        write(evidence / f"C1_{name}_stdout.txt", completed.stdout)
        write(evidence / f"C1_{name}_stderr.txt", completed.stderr)
        if not engine.is_file():
            write(engine, "")
        launch_errors = scan_errors([evidence / f"C1_{name}_stdout.txt", evidence / f"C1_{name}_stderr.txt", engine])
        if completed.returncode != 0 or not trace.is_file() or launch_errors:
            dump(
                evidence / "C1_result.json",
                {
                    "status": "BLOCKED/NOT TESTABLE",
                    "stage": name,
                    "returncode": completed.returncode,
                    "trace_present": trace.is_file(),
                    "launch_errors": launch_errors,
                },
            )
            sums(evidence)
            return 2

    compare = [
        sys.executable,
        "-B",
        str(p1_copy / "tools" / "compare_p1a_baseline.py"),
        str(traces[0]),
        str(traces[1]),
        str(p1_copy / "tests" / "fixtures" / "baseline_flat_support.json"),
    ]
    compared = run(compare, cwd=p1_copy)
    dump(evidence / "C1_compare_argv.json", {"argv": compare, "cwd": str(p1_copy)})
    write(evidence / "C1_compare_stdout.txt", compared.stdout)
    write(evidence / "C1_compare_stderr.txt", compared.stderr)
    try:
        result = json.loads(compared.stdout.strip().splitlines()[-1])
    except Exception:
        result = {"status": "FAIL", "error": "comparator output was not parseable"}
    result.update(
        returncode=compared.returncode,
        godot_version=version,
        p0_trace_sha256=sha(traces[0]),
        p1a_trace_sha256=sha(traces[1]),
        execution_overlay_authority_version=EXECUTION_OVERLAY,
        world_data_authority_version=WORLD_AUTHORITY,
        disposable_work_root=str(work),
        disposable_cleanup_owner="tools/run_v1_2_5_gate.py after durable evidence packaging",
    )
    dump(evidence / "C1_result.json", result)
    dump(ROOT / "evidence" / "v1_2_5_selected_c1_result.json", result)
    sums(evidence)
    return 0 if compared.returncode == 0 and result.get("status") == "PASS" and float(result.get("maximum_absolute_difference", 1.0)) == 0.0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
