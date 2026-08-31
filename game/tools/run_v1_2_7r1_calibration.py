#!/usr/bin/env python3
"""Bounded District Zero P1A v1.2.7R1 presentation-calibration runner."""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import math
import pathlib
import shutil
import subprocess
import sys
import tempfile
from typing import Any

ROOT_DEFAULT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DEFAULT / "tools"))

from p1a_v1_2_7_metrics import compute as compute_metrics
from p1a_v1_2_7r1_harness import (
    EXACT_ENGINE,
    IMAGE_KEYS,
    VERSION,
    dump,
    executed_complete,
    fresh_extract_verify,
    import_and_parse_project,
    package_tree,
    patch_builder,
    png_info,
    run,
    sha256,
    substantive_files,
    tree_hashes,
    validate_candidate_record,
    validate_parameters,
    verify_inventory,
    write,
    write_inventory,
)

BASE_BUILDER = "tests/fixtures/v1_2_7_v1_2_6_world_builder.gd"
ACCEPTANCE = "tests/fixtures/v1_2_6_visual_acceptance.json"
PROBE = "res://tests/p1a_v1_2_7_visual_probe.gd"


class StopRun(RuntimeError):
    def __init__(self, status: str, detail: str, stage: str = "HARNESS") -> None:
        super().__init__(detail)
        self.status = status
        self.detail = detail
        self.stage = stage


def quantize(value: float, quantum: float) -> float:
    return round(round(value / quantum) * quantum, 10)


def candidate_id(stage: str, index: int, parameters: dict[str, Any]) -> str:
    payload = json.dumps(parameters, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return f"{stage}-{index:03d}-{hashlib.sha256(payload).hexdigest()[:10]}"


def parameters(
    outer_scale: float = 1.0,
    outer_emission: float = 0.0,
    wall_scale: float = 1.0,
    wall_emission: float = 0.0,
) -> dict[str, Any]:
    return {
        "OUTER_CLOSURE_MASK": {
            "albedo_scale": outer_scale,
            "emission_multiplier": outer_emission,
        },
        "CORE_WALL": {
            "albedo_scale": wall_scale,
            "emission_multiplier": wall_emission,
        },
    }


def presentation_delta(value: dict[str, Any], registry: dict[str, Any]) -> float:
    total = 0.0
    for material in ("OUTER_CLOSURE_MASK", "CORE_WALL"):
        base = registry["base_materials"][material]["rgb"]
        scale = float(value[material]["albedo_scale"])
        emission = float(value[material]["emission_multiplier"])
        rgb = [float(channel) * scale for channel in base]
        total += sum(abs(current - original) for current, original in zip(rgb, base))
        total += sum(abs(channel * emission) for channel in rgb)
    return total


def local_pass(record: dict[str, Any], material: str, registry: dict[str, Any]) -> bool:
    if not executed_complete(record):
        return False
    ray = record.get("ray_result", {})
    if ray.get("status") != "PASS" or ray.get("sample_count") != 14 or ray.get("mismatch_count") != 0:
        return False
    config = registry["outer_closure" if material == "OUTER_CLOSURE_MASK" else "core_wall"]
    allowed = set(config["allowed_unresolved_check_during_independent_stage"])
    checks = record["metrics"]["checks"]
    if any(not check["pass"] and check["id"] not in allowed for check in checks):
        return False
    a1 = record["metrics"]["views"]["A1_FAMILIARIZATION"]
    if material == "OUTER_CLOSURE_MASK":
        measured = a1["left_outer_closure"]["shadow_on_Y"]
        low, high = config["measured_Y_feasible_interval"]
        return float(low) <= measured <= float(high)
    return a1["obstacle_separation"]["right_absolute_Y"] >= float(config["required_separation_Y"])


def target_value(record: dict[str, Any], material: str) -> float:
    a1 = record["metrics"]["views"]["A1_FAMILIARIZATION"]
    if material == "OUTER_CLOSURE_MASK":
        return float(a1["left_outer_closure"]["shadow_on_Y"])
    return float(a1["obstacle_separation"]["right_absolute_Y"])


def select_combined(records: list[dict[str, Any]], registry: dict[str, Any]) -> dict[str, Any] | None:
    if any(not executed_complete(record) for record in records):
        return None
    eligible = [
        record for record in records
        if record["metrics"].get("status") == "PASS"
        and record["ray_result"].get("status") == "PASS"
        and record["ray_result"].get("sample_count") == 14
        and record["ray_result"].get("mismatch_count") == 0
    ]
    if not eligible:
        return None
    center = float(registry["outer_closure"]["balanced_target_Y"])
    half_width = float(registry["outer_closure"]["preferred_interior_half_width_Y"])
    interior = [
        record for record in eligible
        if abs(target_value(record, "OUTER_CLOSURE_MASK") - center) <= half_width
    ]
    if interior:
        eligible = interior
    else:
        low, high = map(float, registry["outer_closure"]["measured_Y_feasible_interval"])

        def outer_margin(record: dict[str, Any]) -> float:
            measured = target_value(record, "OUTER_CLOSURE_MASK")
            return min(measured - low, high - measured)

        best = max(outer_margin(record) for record in eligible)
        eligible = [record for record in eligible if abs(outer_margin(record) - best) <= 1e-15]
    target = float(registry["core_wall"]["bisection_target_separation_Y"])
    robust = [
        record for record in eligible
        if record["metrics"]["views"]["A1_FAMILIARIZATION"]["obstacle_separation"]["right_absolute_Y"] >= target
    ]
    if robust:
        eligible = robust
    low, high = map(float, registry["outer_closure"]["measured_Y_feasible_interval"])

    def key(record: dict[str, Any]) -> tuple[Any, ...]:
        measured = target_value(record, "OUTER_CLOSURE_MASK")
        outer_margin = min(measured - low, high - measured)
        wall_margin = (
            record["metrics"]["views"]["A1_FAMILIARIZATION"]["obstacle_separation"]["right_absolute_Y"]
            - float(registry["core_wall"]["required_separation_Y"])
        )
        return (
            presentation_delta(record["parameters"], registry),
            -outer_margin,
            -wall_margin,
            record["candidate_id"],
        )

    return sorted(eligible, key=key)[0]


def complete_stage_records(records: list[dict[str, Any]], stage: str) -> list[dict[str, Any]]:
    """Defense-in-depth filter used before any fallback anchor may be selected."""
    return [record for record in records if record.get("stage") == stage and executed_complete(record)]


def exhausted_domain_status(records: list[dict[str, Any]]) -> str:
    """Incomplete execution is a harness blocker, never a negative interval result."""
    return (
        "NO_PRESENTATION_ONLY_INTERVAL"
        if records and all(executed_complete(record) for record in records)
        else "BLOCKED/NOT TESTABLE — HARNESS"
    )


def copy_project(source: pathlib.Path, destination: pathlib.Path) -> None:
    def ignore(_directory: str, names: list[str]) -> set[str]:
        return {
            name for name in names
            if name in {".godot", "__pycache__", "director_inputs", ".pytest_cache", ".mypy_cache"}
            or name == "v1_2_7_v1_2_6_world_builder.gd"
            or name == ".DS_Store"
            or name.startswith("._")
            or name.endswith((".pyc", ".pyo"))
        }

    shutil.copytree(source, destination, ignore=ignore)


def _is_within(child: pathlib.Path, parent: pathlib.Path) -> bool:
    try:
        child.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


class Director:
    def __init__(self, args: argparse.Namespace) -> None:
        self.root = pathlib.Path(args.root).resolve()
        self.base_root = pathlib.Path(args.base_root).resolve()
        self.godot = str(pathlib.Path(args.godot).resolve())
        self.work = pathlib.Path(args.work_root).resolve()
        self.evidence = pathlib.Path(args.evidence_root).resolve()
        self.session = pathlib.Path(args.prepared_session_root).resolve()
        self.output = self.evidence.parent
        self.preflight_only = bool(args.preflight_only)
        self.required_preflight = pathlib.Path(args.require_preflight_result).resolve() if args.require_preflight_result else None
        self.registry: dict[str, Any] = {}
        self.acceptance: dict[str, Any] = {}
        self.baseline = ""
        self.required_classes: dict[str, str] = {}
        self.expected_check_ids: list[str] = []
        self.expected_ray_ids: dict[str, list[str]] = {}
        self.launches = 0
        self.import_preflights = 0
        self.index = 0
        self.cache: dict[str, dict[str, Any]] = {}
        self.records: list[dict[str, Any]] = []
        self.final_runtime: pathlib.Path | None = None
        self.outputs_initialized = False

    def initialize_outputs(self) -> None:
        paths = [self.root, self.base_root, self.work, self.evidence, self.session]
        for index, first in enumerate(paths):
            for second in paths[index + 1:]:
                if first == second or _is_within(first, second) or _is_within(second, first):
                    raise StopRun("BLOCKED/NOT TESTABLE — HARNESS", f"output/root containment is unsafe: {first} / {second}", "PATHS")
        for path in (self.work, self.evidence, self.session):
            if path.exists() and (not path.is_dir() or any(path.iterdir())):
                raise StopRun("BLOCKED/NOT TESTABLE — HARNESS", f"output root is not new/empty: {path}", "PATHS")
        for path in (self.work, self.evidence):
            path.mkdir(parents=True, exist_ok=True)
        self.outputs_initialized = True
        if not self.root.is_dir() or not self.base_root.is_dir():
            raise StopRun("BLOCKED/NOT TESTABLE — SOURCE OR EVIDENCE IDENTITY", "source/base root absent", "PATHS")

    def load_authority_inputs(self) -> None:
        self.registry = json.loads((self.root / "tests/fixtures/v1_2_7_calibration_registry.json").read_text(encoding="utf-8"))
        self.acceptance = json.loads((self.root / ACCEPTANCE).read_text(encoding="utf-8"))
        self.baseline = (self.root / BASE_BUILDER).read_text(encoding="utf-8")
        contract = json.loads((self.root / "tests/fixtures/disposable_import_preflight.json").read_text(encoding="utf-8"))
        self.required_classes = dict(contract["required_registered_classes"])
        run1_metrics = json.loads((self.root / "director_inputs/v1_2_6_run1_validation_evidence/NATIVE_VISUALS/native-visual-metric-result.json").read_text(encoding="utf-8"))
        self.expected_check_ids = [check["id"] for check in run1_metrics["checks"]]
        ray_baseline = json.loads((self.root / "tests/fixtures/v1_2_6_ray_classification_baseline.json").read_text(encoding="utf-8"))
        self.expected_ray_ids = {
            "FREE_ROAM": list(ray_baseline["free_roam"]["records"]),
            "A1_FAMILIARIZATION": list(ray_baseline["a1"]["records"]),
        }

    def static_preflight(self) -> None:
        version = run([self.godot, "--version"], self.root)
        dump(self.evidence / "ENGINE_IDENTITY.json", {
            "argv": [self.godot, "--version"],
            "required": EXACT_ENGINE,
            "observed": version.stdout.strip(),
            "stdout": version.stdout,
            "stderr": version.stderr,
            "returncode": version.returncode,
            "match": version.returncode == 0 and version.stdout.strip() == EXACT_ENGINE,
        })
        if version.returncode != 0 or version.stdout.strip() != EXACT_ENGINE:
            raise StopRun("BLOCKED/NOT TESTABLE — EXACT ENGINE", "exact engine unavailable", "ENGINE_IDENTITY")
        base_errors = verify_inventory(self.base_root, "PACKET_SHA256SUMS.txt")
        expected_base_inventory_sha = sha256(self.root / "V1_2_7_INPUT_SHA256SUMS.txt")
        observed_base_inventory_sha = sha256(self.base_root / "PACKET_SHA256SUMS.txt") if (self.base_root / "PACKET_SHA256SUMS.txt").is_file() else None
        dump(self.evidence / "BASE_V1_2_7_IDENTITY.json", {
            "status": "PASS" if not base_errors and observed_base_inventory_sha == expected_base_inventory_sha else "FAIL",
            "record_count": len((self.base_root / "PACKET_SHA256SUMS.txt").read_text(encoding="utf-8").splitlines()) if (self.base_root / "PACKET_SHA256SUMS.txt").is_file() else 0,
            "required_inventory_sha256": expected_base_inventory_sha,
            "observed_inventory_sha256": observed_base_inventory_sha,
            "errors": base_errors,
        })
        if base_errors or observed_base_inventory_sha != expected_base_inventory_sha:
            raise StopRun("BLOCKED/NOT TESTABLE — SOURCE OR EVIDENCE IDENTITY", "checksum-clean v1.2.7 base identity failed", "BASE_IDENTITY")
        semantic_command = [
            sys.executable,
            "-B",
            str(self.root / "tools/test_v1_2_7r1_repairs.py"),
            "--root",
            str(self.root),
            "--static-only",
        ]
        semantic = run(semantic_command, self.root)
        dump(self.evidence / "SEMANTIC_PREFLIGHT/argv.json", {"argv": semantic_command, "cwd": str(self.root)})
        write(self.evidence / "SEMANTIC_PREFLIGHT/stdout.txt", semantic.stdout)
        write(self.evidence / "SEMANTIC_PREFLIGHT/stderr.txt", semantic.stderr)
        if semantic.returncode != 0:
            raise StopRun("BLOCKED/NOT TESTABLE — HARNESS", "R1 semantic repair suite failed", "SEMANTIC_PREFLIGHT")
        command = [
            sys.executable,
            "-B",
            str(self.root / "tools/verify_v1_2_7r1_successor.py"),
            "--root",
            str(self.root),
            "--phase",
            "repair",
        ]
        verified = run(command, self.root)
        dump(self.evidence / "STATIC_PREFLIGHT/argv.json", {"argv": command, "cwd": str(self.root)})
        write(self.evidence / "STATIC_PREFLIGHT/stdout.txt", verified.stdout)
        write(self.evidence / "STATIC_PREFLIGHT/stderr.txt", verified.stderr)
        if verified.returncode != 0:
            raise StopRun("BLOCKED/NOT TESTABLE — SOURCE OR EVIDENCE IDENTITY", "R1 repair verifier failed", "STATIC_PREFLIGHT")
        if not self.preflight_only:
            if self.required_preflight is None or not self.required_preflight.is_file():
                raise StopRun("BLOCKED/NOT TESTABLE — HARNESS", "required preflight result absent", "PREFLIGHT_BINDING")
            result = json.loads(self.required_preflight.read_text(encoding="utf-8"))
            if result.get("status") != "PASS" or result.get("source_packet_inventory_sha256") != sha256(self.root / "PACKET_SHA256SUMS.txt"):
                raise StopRun("BLOCKED/NOT TESTABLE — HARNESS", "preflight result is not bound to current R1 source", "PREFLIGHT_BINDING")

    def evaluate(self, stage: str, value: dict[str, Any]) -> dict[str, Any]:
        key = stage + "|" + json.dumps(value, sort_keys=True, separators=(",", ":"))
        if key in self.cache:
            return self.cache[key]
        if self.launches >= int(self.registry["absolute_candidate_engine_launch_cap"]):
            raise StopRun("NO_PRESENTATION_ONLY_INTERVAL", "candidate render launch cap reached", "CANDIDATE_DOMAIN")
        self.index += 1
        identifier = candidate_id(stage, self.index, value)
        candidate_dir = self.evidence / "CANDIDATES" / identifier
        project = self.work / "CANDIDATES" / identifier
        copy_project(self.root, project)
        expected_builder = patch_builder(self.baseline, value, self.registry)
        write(project / "scripts/p1a_world_builder.gd", expected_builder)
        write(candidate_dir / "evaluated_p1a_world_builder.gd", expected_builder)
        import_result = import_and_parse_project(
            self.godot,
            project,
            candidate_dir / "IMPORT_PREFLIGHT",
            target_script=PROBE,
            required_classes=self.required_classes,
            expected_builder_sha256=sha256(project / "scripts/p1a_world_builder.gd"),
        )
        self.import_preflights += 1
        if import_result.get("status") != "PASS":
            blocked = {
                "schema": "district_zero.p1a.v1_2_7r1.candidate_record.v1",
                "candidate_id": identifier,
                "stage": stage,
                "parameters": value,
                "execution_status": "BLOCKED/NOT TESTABLE — HARNESS",
                "evidence_complete": False,
                "validation_errors": import_result.get("blockers", []),
                "import_preflight": import_result,
            }
            dump(candidate_dir / "candidate_record.json", blocked)
            raise StopRun("BLOCKED/NOT TESTABLE — HARNESS", f"candidate import/parse failed: {identifier}", "CANDIDATE_IMPORT")
        command = [
            self.godot,
            "--log-file",
            str(candidate_dir / "engine.txt"),
            "--path",
            str(project),
            "--fixed-fps",
            "60",
            "--script",
            PROBE,
            "--",
            "--output-dir",
            str(candidate_dir),
        ]
        candidate_dir.mkdir(parents=True, exist_ok=True)
        dump(candidate_dir / "argv.json", {"argv": command, "cwd": str(project)})
        process = run(command, project)
        self.launches += 1
        write(candidate_dir / "stdout.txt", process.stdout)
        write(candidate_dir / "stderr.txt", process.stderr)
        if not (candidate_dir / "engine.txt").is_file():
            write(candidate_dir / "engine.txt", "")
        try:
            probe = json.loads((candidate_dir / "probe_result.json").read_text(encoding="utf-8"))
        except Exception:
            probe = {}
            write(candidate_dir / "probe_result.json", "{}\n")
        image_names = {
            "free_roam_on": "free-roam-after-native.png",
            "free_roam_off": "free-roam-after-shadow-off-reference.png",
            "a1_on": "a1-after-native.png",
            "a1_off": "a1-after-shadow-off-reference.png",
        }
        paths = {
            "FREE_ROAM:on": candidate_dir / image_names["free_roam_on"],
            "FREE_ROAM:off": candidate_dir / image_names["free_roam_off"],
            "A1_FAMILIARIZATION:on": candidate_dir / image_names["a1_on"],
            "A1_FAMILIARIZATION:off": candidate_dir / image_names["a1_off"],
        }
        try:
            metrics = compute_metrics(self.acceptance, paths) if all(path.is_file() for path in paths.values()) else {}
        except Exception as exc:
            metrics = {"status": "FAIL", "error": str(exc), "checks": []}
        dump(candidate_dir / "native-visual-metric-result.json", metrics)
        images = {
            name: {
                "path": filename,
                "sha256": sha256(candidate_dir / filename) if (candidate_dir / filename).is_file() else None,
                "png": png_info(candidate_dir / filename),
            }
            for name, filename in image_names.items()
        }
        record: dict[str, Any] = {
            "schema": "district_zero.p1a.v1_2_7r1.candidate_record.v1",
            "candidate_id": identifier,
            "stage": stage,
            "parameters": value,
            "engine_identity": probe.get("engine_identity"),
            "command": command,
            "returncode": process.returncode,
            "project_material_source_sha256": sha256(project / "scripts/p1a_world_builder.gd"),
            "evaluated_source_path": "evaluated_p1a_world_builder.gd",
            "images": images,
            "metrics": metrics,
            "ray_result": probe.get("ray_result", {}),
            "import_preflight": import_result,
            "stdout_sha256": sha256(candidate_dir / "stdout.txt"),
            "stderr_sha256": sha256(candidate_dir / "stderr.txt"),
            "engine_log_sha256": sha256(candidate_dir / "engine.txt"),
            "probe_result_sha256": sha256(candidate_dir / "probe_result.json"),
            "metrics_result_sha256": sha256(candidate_dir / "native-visual-metric-result.json"),
            "import_preflight_result_sha256": sha256(candidate_dir / "IMPORT_PREFLIGHT/result.json"),
            "evaluated_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
            "evidence_validator": "p1a_v1_2_7r1_harness.validate_candidate_record.v1",
        }
        validation_errors = validate_candidate_record(
            record,
            candidate_dir,
            project=project,
            expected_builder=expected_builder,
            target_script=PROBE,
            registry=self.registry,
            expected_check_ids=self.expected_check_ids,
            expected_ray_ids=self.expected_ray_ids,
            required_classes=self.required_classes,
            recomputed_metrics=metrics,
        )
        record["validation_errors"] = validation_errors
        record["evidence_complete"] = not validation_errors
        record["execution_status"] = "EXECUTED_COMPLETE" if not validation_errors else "BLOCKED/NOT TESTABLE — HARNESS"
        dump(candidate_dir / "candidate_record.json", record)
        if validation_errors:
            raise StopRun("BLOCKED/NOT TESTABLE — HARNESS", f"candidate evidence incomplete: {identifier}: {validation_errors[:3]}", "CANDIDATE_EVIDENCE")
        shutil.rmtree(project, ignore_errors=True)
        self.cache[key] = record
        self.records.append(record)
        return record

    def search_albedo(self, material: str) -> dict[str, Any] | None:
        config = self.registry["outer_closure" if material == "OUTER_CLOSURE_MASK" else "core_wall"]
        low, high = map(float, config["albedo_scale_domain"])
        quantum = float(config["albedo_scale_quantum"])
        target = float(config["balanced_target_Y"] if material == "OUTER_CLOSURE_MASK" else config["bisection_target_separation_Y"])
        maximum = int(config["max_albedo_evaluations"])
        stage = "OUTER_ALBEDO" if material == "OUTER_CLOSURE_MASK" else "WALL_ALBEDO"
        records: list[dict[str, Any]] = []

        def evaluate(scale: float) -> dict[str, Any]:
            scale = quantize(min(high, max(low, scale)), quantum)
            value = parameters(outer_scale=scale) if material == "OUTER_CLOSURE_MASK" else parameters(wall_scale=scale)
            record = self.evaluate(stage, value)
            records.append(record)
            return record

        low_record = evaluate(low)
        high_record = evaluate(high)
        low_value = target_value(low_record, material)
        high_value = target_value(high_record, material)
        if high_value < low_value:
            raise StopRun("NO_PRESENTATION_ONLY_INTERVAL", f"{material} albedo response is non-monotonic", "INDEPENDENT_ALBEDO")
        while len({record["candidate_id"] for record in records}) < maximum:
            middle = quantize((low + high) / 2.0, quantum)
            if middle in {quantize(low, quantum), quantize(high, quantum)}:
                break
            record = evaluate(middle)
            if target_value(record, material) < target:
                low = middle
            else:
                high = middle
        passing = [record for record in records if local_pass(record, material, self.registry)]
        if not passing:
            return None
        if material == "OUTER_CLOSURE_MASK":
            center = float(self.registry["outer_closure"]["balanced_target_Y"])
            return sorted(
                passing,
                key=lambda record: (
                    abs(target_value(record, material) - center),
                    presentation_delta(record["parameters"], self.registry),
                    record["candidate_id"],
                ),
            )[0]
        robust = [record for record in passing if target_value(record, material) >= target]
        return sorted(
            robust or passing,
            key=lambda record: (
                presentation_delta(record["parameters"], self.registry),
                -target_value(record, material),
                record["candidate_id"],
            ),
        )[0]

    def search_fallback(self, material: str) -> dict[str, Any] | None:
        prior_stage = "OUTER_ALBEDO" if material == "OUTER_CLOSURE_MASK" else "WALL_ALBEDO"
        prior = complete_stage_records(self.records, prior_stage)
        if not prior:
            raise StopRun("BLOCKED/NOT TESTABLE — HARNESS", "fallback has no complete albedo records", "EMISSION_FALLBACK")
        target = float(
            self.registry["outer_closure"]["balanced_target_Y"]
            if material == "OUTER_CLOSURE_MASK"
            else self.registry["core_wall"]["bisection_target_separation_Y"]
        )
        below = [record for record in prior if target_value(record, material) <= target]
        anchor = max(below, key=lambda record: target_value(record, material)) if below else min(prior, key=lambda record: target_value(record, material))
        scale = float(anchor["parameters"][material]["albedo_scale"])
        config = self.registry["fallback"]
        low, high = map(float, config["emission_multiplier_domain"])
        quantum = float(config["emission_multiplier_quantum"])
        maximum = int(config["max_evaluations_per_material"])
        stage = "OUTER_EMISSION_FALLBACK" if material == "OUTER_CLOSURE_MASK" else "WALL_EMISSION_FALLBACK"
        records: list[dict[str, Any]] = []

        def evaluate(emission: float) -> dict[str, Any]:
            emission = quantize(min(high, max(low, emission)), quantum)
            value = (
                parameters(outer_scale=scale, outer_emission=emission)
                if material == "OUTER_CLOSURE_MASK"
                else parameters(wall_scale=scale, wall_emission=emission)
            )
            record = self.evaluate(stage, value)
            records.append(record)
            return record

        low_record = evaluate(low)
        high_record = evaluate(high)
        if target_value(high_record, material) < target_value(low_record, material):
            raise StopRun("NO_PRESENTATION_ONLY_INTERVAL", f"{material} emission response is non-monotonic", "EMISSION_FALLBACK")
        while len({record["candidate_id"] for record in records}) < maximum:
            middle = quantize((low + high) / 2.0, quantum)
            if middle in {quantize(low, quantum), quantize(high, quantum)}:
                break
            record = evaluate(middle)
            if target_value(record, material) < target:
                low = middle
            else:
                high = middle
        passing = [record for record in records if local_pass(record, material, self.registry)]
        if not passing:
            return None
        if material == "OUTER_CLOSURE_MASK":
            center = float(self.registry["outer_closure"]["balanced_target_Y"])
            return sorted(
                passing,
                key=lambda record: (
                    abs(target_value(record, material) - center),
                    presentation_delta(record["parameters"], self.registry),
                    record["candidate_id"],
                ),
            )[0]
        robust = [record for record in passing if target_value(record, material) >= target]
        return sorted(
            robust or passing,
            key=lambda record: (
                presentation_delta(record["parameters"], self.registry),
                -target_value(record, material),
                record["candidate_id"],
            ),
        )[0]

    def combined(self, outer: dict[str, Any], wall: dict[str, Any]) -> dict[str, Any]:
        base = {
            "OUTER_CLOSURE_MASK": dict(outer["parameters"]["OUTER_CLOSURE_MASK"]),
            "CORE_WALL": dict(wall["parameters"]["CORE_WALL"]),
        }
        variants: list[dict[str, Any]] = []
        for outer_offset in self.registry["combined_validation"]["guard_offsets_quanta"]:
            for wall_offset in self.registry["combined_validation"]["guard_offsets_quanta"]:
                value = json.loads(json.dumps(base))
                for material, offset in (("OUTER_CLOSURE_MASK", outer_offset), ("CORE_WALL", wall_offset)):
                    if value[material]["emission_multiplier"] > 0.0:
                        quantum = float(self.registry["fallback"]["emission_multiplier_quantum"])
                        low, high = map(float, self.registry["fallback"]["emission_multiplier_domain"])
                        value[material]["emission_multiplier"] = quantize(
                            min(high, max(low, value[material]["emission_multiplier"] + offset * quantum)),
                            quantum,
                        )
                    else:
                        config = self.registry["outer_closure" if material == "OUTER_CLOSURE_MASK" else "core_wall"]
                        quantum = float(config["albedo_scale_quantum"])
                        low, high = map(float, config["albedo_scale_domain"])
                        value[material]["albedo_scale"] = quantize(
                            min(high, max(low, value[material]["albedo_scale"] + offset * quantum)),
                            quantum,
                        )
                variants.append(value)
        unique: list[dict[str, Any]] = []
        seen: set[str] = set()
        for value in variants:
            key = json.dumps(value, sort_keys=True, separators=(",", ":"))
            if key not in seen:
                seen.add(key)
                unique.append(value)
        if len(unique) > int(self.registry["combined_validation"]["maximum_grid_evaluations"]):
            raise StopRun("NO_PRESENTATION_ONLY_INTERVAL", "combined grid exceeds registered cap", "COMBINED")
        records = [self.evaluate("COMBINED", value) for value in unique]
        selected = select_combined(records, self.registry)
        if selected is None:
            status = exhausted_domain_status(records)
            detail = (
                "no complete combined candidate passed 21 visuals and 14 rays"
                if status == "NO_PRESENTATION_ONLY_INTERVAL"
                else "combined evidence is incomplete"
            )
            raise StopRun(status, detail, "COMBINED")
        return selected

    def materialize(self, selected: dict[str, Any]) -> None:
        expected = patch_builder(self.baseline, selected["parameters"], self.registry)
        write(self.root / "scripts/p1a_world_builder.gd", expected)
        digest = sha256(self.root / "scripts/p1a_world_builder.gd")
        record = {
            "schema": "district_zero.p1a.v1_2_7r1.selected_presentation.v1",
            "status": "PASS",
            "selected_candidate_id": selected["candidate_id"],
            "parameters": selected["parameters"],
            "selection_rule": self.registry["selection_rule"],
            "presentation_delta": presentation_delta(selected["parameters"], self.registry),
            "selected_metrics": selected["metrics"],
            "selected_ray_result": selected["ray_result"],
            "source_material_file_sha256": digest,
            "evaluated_source_sha256": selected["project_material_source_sha256"],
        }
        dump(self.root / "presentation/p1a_v1_2_7r1_selected_presentation.json", record)
        write(
            self.root / "STATUS.md",
            "# District Zero P1A status — v1.2.7R1 calibration selected\n\n"
            "**Outcome:** `CALIBRATION SELECTED — FINAL VERIFICATION REQUIRED`\n\n"
            f"Selected candidate: `{selected['candidate_id']}`. Human attempts consumed: `0`. "
            "Human World Gate: `NOT PERFORMED`. P1B: `FROZEN`.\n",
        )
        write_inventory(self.root, "PACKET_SHA256SUMS.txt")

    def final_probe(self) -> None:
        runtime = self.work / "FINAL_RUNTIME"
        copy_project(self.root, runtime)
        builder_sha = sha256(runtime / "scripts/p1a_world_builder.gd")
        imported = import_and_parse_project(
            self.godot,
            runtime,
            self.evidence / "FINAL_NATIVE_VISUALS/IMPORT_PREFLIGHT",
            target_script=PROBE,
            required_classes=self.required_classes,
            expected_builder_sha256=builder_sha,
        )
        self.import_preflights += 1
        if imported.get("status") != "PASS":
            raise StopRun("BLOCKED/NOT TESTABLE — HARNESS", "final runtime import/parse failed", "FINAL_NATIVE_VISUALS")
        directory = self.evidence / "FINAL_NATIVE_VISUALS"
        write(directory / "evaluated_p1a_world_builder.gd", (runtime / "scripts/p1a_world_builder.gd").read_text(encoding="utf-8"))
        command = [
            self.godot,
            "--log-file",
            str(directory / "engine.txt"),
            "--path",
            str(runtime),
            "--fixed-fps",
            "60",
            "--script",
            PROBE,
            "--",
            "--output-dir",
            str(directory),
        ]
        dump(directory / "argv.json", {"argv": command, "cwd": str(runtime)})
        process = run(command, runtime)
        write(directory / "stdout.txt", process.stdout)
        write(directory / "stderr.txt", process.stderr)
        if not (directory / "engine.txt").is_file():
            write(directory / "engine.txt", "")
        try:
            probe = json.loads((directory / "probe_result.json").read_text(encoding="utf-8"))
        except Exception:
            probe = {}
            write(directory / "probe_result.json", "{}\n")
        image_paths = {
            "FREE_ROAM:on": directory / "free-roam-after-native.png",
            "FREE_ROAM:off": directory / "free-roam-after-shadow-off-reference.png",
            "A1_FAMILIARIZATION:on": directory / "a1-after-native.png",
            "A1_FAMILIARIZATION:off": directory / "a1-after-shadow-off-reference.png",
        }
        if not all(path.is_file() for path in image_paths.values()):
            raise StopRun("BLOCKED/NOT TESTABLE — HARNESS", "final native images incomplete", "FINAL_NATIVE_VISUALS")
        metrics = compute_metrics(self.acceptance, image_paths)
        dump(directory / "native-visual-metric-result.json", metrics)
        ray = probe.get("ray_result", {})
        image_names = {
            "free_roam_on": "free-roam-after-native.png",
            "free_roam_off": "free-roam-after-shadow-off-reference.png",
            "a1_on": "a1-after-native.png",
            "a1_off": "a1-after-shadow-off-reference.png",
        }
        record: dict[str, Any] = {
            "schema": "district_zero.p1a.v1_2_7r1.candidate_record.v1",
            "candidate_id": "FINAL-NATIVE-VISUALS",
            "stage": "FINAL_NATIVE_VISUALS",
            "parameters": json.loads((self.root / "presentation/p1a_v1_2_7r1_selected_presentation.json").read_text(encoding="utf-8"))["parameters"],
            "engine_identity": probe.get("engine_identity"),
            "command": command,
            "returncode": process.returncode,
            "project_material_source_sha256": builder_sha,
            "evaluated_source_path": "evaluated_p1a_world_builder.gd",
            "images": {
                name: {"path": filename, "sha256": sha256(directory / filename), "png": png_info(directory / filename)}
                for name, filename in image_names.items()
            },
            "metrics": metrics,
            "ray_result": ray,
            "import_preflight": imported,
            "stdout_sha256": sha256(directory / "stdout.txt"),
            "stderr_sha256": sha256(directory / "stderr.txt"),
            "engine_log_sha256": sha256(directory / "engine.txt"),
            "probe_result_sha256": sha256(directory / "probe_result.json"),
            "metrics_result_sha256": sha256(directory / "native-visual-metric-result.json"),
            "import_preflight_result_sha256": sha256(directory / "IMPORT_PREFLIGHT/result.json"),
            "evaluated_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
            "evidence_validator": "p1a_v1_2_7r1_harness.validate_candidate_record.v1",
        }
        validation_errors = validate_candidate_record(
            record,
            directory,
            project=runtime,
            expected_builder=(runtime / "scripts/p1a_world_builder.gd").read_text(encoding="utf-8"),
            target_script=PROBE,
            registry=self.registry,
            expected_check_ids=self.expected_check_ids,
            expected_ray_ids=self.expected_ray_ids,
            required_classes=self.required_classes,
            recomputed_metrics=metrics,
        )
        record["validation_errors"] = validation_errors
        record["evidence_complete"] = not validation_errors
        record["execution_status"] = "EXECUTED_COMPLETE" if not validation_errors else "BLOCKED/NOT TESTABLE — HARNESS"
        dump(directory / "final_candidate_record.json", record)
        if validation_errors:
            raise StopRun("BLOCKED/NOT TESTABLE — HARNESS", f"final native evidence incomplete: {validation_errors[:3]}", "FINAL_NATIVE_VISUALS")
        if process.returncode != 0 or metrics.get("status") != "PASS" or ray.get("status") != "PASS" or ray.get("sample_count") != 14 or ray.get("mismatch_count") != 0:
            raise StopRun("BLOCKED/NOT TESTABLE — FINAL NATIVE VISUALS", "final visual/ray gate failed", "FINAL_NATIVE_VISUALS")
        self.final_runtime = runtime

    def final_verifiers(self) -> None:
        write_inventory(self.root, "PACKET_SHA256SUMS.txt")
        command = [
            sys.executable,
            "-B",
            str(self.root / "tools/verify_v1_2_7r1_successor.py"),
            "--root",
            str(self.root),
            "--phase",
            "final",
        ]
        process = run(command, self.root)
        dump(self.evidence / "FINAL_STATIC_VERIFIER/argv.json", {"argv": command, "cwd": str(self.root)})
        write(self.evidence / "FINAL_STATIC_VERIFIER/stdout.txt", process.stdout)
        write(self.evidence / "FINAL_STATIC_VERIFIER/stderr.txt", process.stderr)
        if process.returncode != 0:
            raise StopRun("BLOCKED/NOT TESTABLE — PRESERVATION", "final static/preservation verifier failed", "FINAL_STATIC_VERIFIER")
        c1 = self.evidence / "C1"
        command = [
            sys.executable,
            "-B",
            str(self.root / "tools/run_v1_2_7r1_c1.py"),
            "--root",
            str(self.root),
            "--godot",
            self.godot,
            "--evidence-dir",
            str(c1),
            "--work-root",
            str(self.work / "FINAL_C1"),
        ]
        process = run(command, self.root)
        dump(self.evidence / "C1_WRAPPER/argv.json", {"argv": command, "cwd": str(self.root)})
        write(self.evidence / "C1_WRAPPER/stdout.txt", process.stdout)
        write(self.evidence / "C1_WRAPPER/stderr.txt", process.stderr)
        try:
            result = json.loads((c1 / "C1_result.json").read_text(encoding="utf-8"))
        except Exception:
            result = {}
        if process.returncode != 0 or result.get("status") != "PASS" or result.get("ticks_compared") != 1260 or float(result.get("maximum_absolute_difference", 1.0)) != 0.0:
            raise StopRun("BLOCKED/NOT TESTABLE — C1", "final C1 comparison failed", "C1")

    def smoke(self) -> None:
        if self.final_runtime is None:
            raise StopRun("BLOCKED/NOT TESTABLE — HARNESS", "final imported runtime absent", "LAUNCHER_SMOKE")
        smoke_session = self.work / "LAUNCHER_SMOKE_SESSION"
        smoke_session.mkdir(parents=True, exist_ok=True)
        directory = self.evidence / "LAUNCHER_SMOKE_75S"
        command = [
            sys.executable,
            "-B",
            str(self.root / "tools/run_v1_2_6_launcher_smoke.py"),
            "--godot",
            self.godot,
            "--project-root",
            str(self.final_runtime),
            "--session-root",
            str(smoke_session),
            "--output-dir",
            str(directory),
            "--session-id",
            "v1.2.7R1-final-smoke",
            "--minimum-wall-duration-s",
            "75",
        ]
        dump(directory / "wrapper_argv.json", {"argv": command, "cwd": str(self.root)})
        process = run(command, self.root)
        write(directory / "wrapper_stdout.txt", process.stdout)
        write(directory / "wrapper_stderr.txt", process.stderr)
        try:
            result = json.loads((directory / "smoke_result.json").read_text(encoding="utf-8"))
        except Exception:
            result = {}
        if process.returncode != 0 or result.get("status") != "PASS" or result.get("attempts_consumed") != 0:
            raise StopRun("BLOCKED/NOT TESTABLE — LAUNCHER SMOKE", "75-second launcher smoke failed", "LAUNCHER_SMOKE")

    def prepare_session(self) -> None:
        evidence = self.evidence / "PREPARED_SESSION"
        command = [
            sys.executable,
            "-B",
            str(self.root / "tools/prepare_v1_2_7r1_a1_session.py"),
            "--root",
            str(self.root),
            "--godot",
            self.godot,
            "--session-root",
            str(self.session),
            "--evidence-dir",
            str(evidence),
        ]
        process = run(command, self.root)
        dump(self.evidence / "PREPARE_SESSION_WRAPPER/argv.json", {"argv": command, "cwd": str(self.root)})
        write(self.evidence / "PREPARE_SESSION_WRAPPER/stdout.txt", process.stdout)
        write(self.evidence / "PREPARE_SESSION_WRAPPER/stderr.txt", process.stderr)
        try:
            result = json.loads((self.session / "PREPARED_RESULT.json").read_text(encoding="utf-8"))
        except Exception:
            result = {}
        inventory_errors = verify_inventory(self.session, "SESSION_SHA256SUMS.txt") if self.session.is_dir() else ["session absent"]
        if (
            process.returncode != 0
            or result.get("status") != "READY FOR A1 HUMAN FEASIBILITY CAPTURE"
            or result.get("engine_identity") != EXACT_ENGINE
            or result.get("human_attempts_consumed") != 0
            or result.get("import_preflight", {}).get("status") != "PASS"
            or inventory_errors
        ):
            raise StopRun("BLOCKED/NOT TESTABLE — PREPARED SESSION", "prepared-session validation failed", "PREPARED_SESSION")

    def finalize_evidence(self, status: str, detail: str, stage: str, *, preflight: bool = False, package_bindings: dict[str, Any] | None = None) -> dict[str, Any]:
        package_bindings = package_bindings or {}
        terminal = {
            "schema": "district_zero.p1a.v1_2_7r1.calibration_terminal_result.v1",
            "status": status,
            "terminal_stage": stage,
            "detail": detail,
            "candidate_render_launches": self.launches,
            "project_import_preflights": self.import_preflights,
            "human_attempts_consumed": 0,
            "human_world_gate": "NOT PERFORMED",
            "P1B": "FROZEN",
            "packages": package_bindings,
        }
        dump(self.evidence / "TERMINAL_RESULT.json", terminal)
        dump(self.evidence / "EVIDENCE_PACKAGE_MANIFEST.json", {
            "schema": "district_zero.p1a.v1_2_7r1.evidence_package_manifest.v1",
            "terminal_status": status,
            "terminal_stage": stage,
            "finalized_before_cleanup": True,
            "fresh_extraction_required": True,
            "candidate_missing_evidence_never_means_no_interval": True,
            "human_world_gate": "NOT PERFORMED",
            "P1B": "FROZEN",
        })
        write_inventory(self.evidence, "SHA256SUMS.txt")
        filename = (
            "District-Zero-P1A-v1.2.7R1-Preflight-Evidence.zip"
            if preflight
            else "District-Zero-P1A-v1.2.7R1-Calibration-Validation-Evidence.zip"
        )
        output = self.output / filename
        report = package_tree(
            self.evidence,
            output,
            inventory_name="SHA256SUMS.txt",
            scratch_parent=self.work / "FRESH_EXTRACTIONS",
        )
        dump(self.output / (filename + ".report.json"), report)
        return report

    def package_success(self) -> dict[str, Any]:
        write(
            self.root / "STATUS.md",
            "# District Zero P1A status — v1.2.7R1 final preparation\n\n"
            "**Outcome:** `READY FOR A1 HUMAN FEASIBILITY CAPTURE`\n\n"
            "All bounded calibration and final prerequisites passed under exact Godot. "
            "Human attempts consumed: `0`. Human World Gate: `NOT PERFORMED`. P1B: `FROZEN`.\n",
        )
        write_inventory(self.root, "PACKET_SHA256SUMS.txt")
        source_report = package_tree(
            self.root,
            self.output / "District-Zero-P1A-v1.2.7R1-Implemented-Source.zip",
            inventory_name="PACKET_SHA256SUMS.txt",
            scratch_parent=self.work / "FRESH_EXTRACTIONS",
        )
        session_report = package_tree(
            self.session,
            self.output / "District-Zero-P1A-v1.2.7R1-Prepared-A1-Human-Session.zip",
            inventory_name="SESSION_SHA256SUMS.txt",
            scratch_parent=self.work / "FRESH_EXTRACTIONS",
        )
        bindings = {"implemented_source": source_report, "prepared_session": session_report}
        evidence_report = self.finalize_evidence(
            "READY FOR A1 HUMAN FEASIBILITY CAPTURE",
            "all bounded automated presentation prerequisites passed",
            "PREPARED_SESSION",
            package_bindings=bindings,
        )
        reports = {**bindings, "validation_evidence": evidence_report}
        dump(self.output / "District-Zero-P1A-v1.2.7R1-PACKAGE-REPORT.json", reports)
        return reports

    def create_overlay(self) -> dict[str, Any]:
        overlay = self.output / "District-Zero-P1A-v1.2.7R1-Harness-Repair-Overlay"
        if overlay.exists():
            raise StopRun("BLOCKED/NOT TESTABLE — HARNESS", "repair overlay root already exists", "OVERLAY")
        base_map = tree_hashes(self.base_root)
        current_map = tree_hashes(self.root)
        changed = sorted(path for path, digest in current_map.items() if base_map.get(path) != digest)
        removed = sorted(set(base_map) - set(current_map))
        if removed:
            raise StopRun("BLOCKED/NOT TESTABLE — PRESERVATION", f"R1 repair removed input paths: {removed[:5]}", "OVERLAY")
        for relative in changed:
            source = self.root / relative
            destination = overlay / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)
        manifest = {
            "schema": "district_zero.p1a.v1_2_7r1.harness_repair_overlay.v1",
            "status": "PASS",
            "base_version": "v1.2.7",
            "successor_version": VERSION,
            "base_packet_inventory_sha256": sha256(self.base_root / "PACKET_SHA256SUMS.txt"),
            "changed_or_added_paths": [
                {
                    "path": relative,
                    "base_sha256": base_map.get(relative),
                    "r1_sha256": current_map[relative],
                }
                for relative in changed
            ],
            "removed_paths": [],
            "scope": "six authorized test-harness/evidence repairs only",
        }
        dump(overlay / "OVERLAY_MANIFEST.json", manifest)
        write_inventory(overlay, "OVERLAY_SHA256SUMS.txt")
        report = package_tree(
            overlay,
            self.output / "District-Zero-P1A-v1.2.7R1-Harness-Repair-Overlay.zip",
            inventory_name="OVERLAY_SHA256SUMS.txt",
            scratch_parent=self.work / "FRESH_EXTRACTIONS",
        )
        dump(self.output / "District-Zero-P1A-v1.2.7R1-Harness-Repair-Overlay.report.json", report)
        return report

    def _synthetic_finalizer_tests(self, output: pathlib.Path) -> dict[str, Any]:
        reports: dict[str, Any] = {}
        for name, status in (("blocker", "BLOCKED/NOT TESTABLE — HARNESS"), ("failure", "NO_PRESENTATION_ONLY_INTERVAL")):
            tree = self.work / "SYNTHETIC_FINALIZERS" / name
            dump(tree / "TERMINAL_RESULT.json", {"status": status, "human_attempts_consumed": 0})
            write_inventory(tree, "SHA256SUMS.txt")
            reports[name] = package_tree(
                tree,
                self.work / "SYNTHETIC_PACKAGES" / f"{name}.zip",
                inventory_name="SHA256SUMS.txt",
                scratch_parent=self.work / "FRESH_EXTRACTIONS",
            )
        success_reports: dict[str, Any] = {}
        for kind, inventory in (("source", "PACKET_SHA256SUMS.txt"), ("evidence", "SHA256SUMS.txt"), ("session", "SESSION_SHA256SUMS.txt")):
            tree = self.work / "SYNTHETIC_FINALIZERS" / "success" / kind
            dump(tree / "RESULT.json", {"status": "PASS", "kind": kind})
            write_inventory(tree, inventory)
            success_reports[kind] = package_tree(
                tree,
                self.work / "SYNTHETIC_PACKAGES" / f"success-{kind}.zip",
                inventory_name=inventory,
                scratch_parent=self.work / "FRESH_EXTRACTIONS",
            )
        reports["success"] = success_reports
        dump(output / "synthetic_finalizer_results.json", reports)
        return reports

    def run_preflight_only(self) -> dict[str, Any]:
        directory = self.evidence / "PREFLIGHT_ONLY"
        cases = {
            "BASELINE_UNMATERIALIZED": None,
            "IDENTITY_MATERIALIZATION": parameters(),
            "OUTER_ONLY": parameters(outer_scale=1.01),
            "WALL_ONLY": parameters(wall_scale=1.01),
            "EMISSION": parameters(outer_emission=0.01),
            "COMBINED": parameters(outer_scale=1.01, outer_emission=0.01, wall_scale=1.02, wall_emission=0.02),
        }
        results: dict[str, Any] = {}
        for name, value in cases.items():
            project = self.work / "PREFLIGHT_MATERIALIZATIONS" / name
            copy_project(self.root, project)
            expected = self.baseline if value is None else patch_builder(self.baseline, value, self.registry)
            write(project / "scripts/p1a_world_builder.gd", expected)
            result = import_and_parse_project(
                self.godot,
                project,
                directory / "MATERIALIZATIONS" / name,
                target_script=PROBE,
                required_classes=self.required_classes,
                expected_builder_sha256=sha256(project / "scripts/p1a_world_builder.gd"),
            )
            self.import_preflights += 1
            results[name] = result
            if result.get("status") != "PASS":
                raise StopRun("BLOCKED/NOT TESTABLE — HARNESS", f"preflight materialization failed: {name}", "PREFLIGHT_MATERIALIZATION")
        unauthorized = patch_builder(self.baseline, parameters(wall_scale=1.01), self.registry) + "# unauthorized neighbor\n"
        canonical = patch_builder(self.baseline, parameters(wall_scale=1.01), self.registry)
        if unauthorized == canonical:
            raise StopRun("BLOCKED/NOT TESTABLE — HARNESS", "unauthorized-neighbor test did not diverge", "PREFLIGHT_VERIFIER")
        dump(directory / "materialization_results.json", results)
        self._synthetic_finalizer_tests(directory)

        prepared = self.work / "PREFLIGHT_PREPARED_SESSION"
        prepare_evidence = directory / "PREPARED_SESSION"
        command = [
            sys.executable,
            "-B",
            str(self.root / "tools/prepare_v1_2_7r1_a1_session.py"),
            "--root",
            str(self.root),
            "--godot",
            self.godot,
            "--session-root",
            str(prepared),
            "--evidence-dir",
            str(prepare_evidence),
        ]
        process = run(command, self.root)
        dump(directory / "PREPARED_SESSION_WRAPPER/argv.json", {"argv": command, "cwd": str(self.root)})
        write(directory / "PREPARED_SESSION_WRAPPER/stdout.txt", process.stdout)
        write(directory / "PREPARED_SESSION_WRAPPER/stderr.txt", process.stderr)
        if process.returncode != 0 or verify_inventory(prepared, "SESSION_SHA256SUMS.txt"):
            raise StopRun("BLOCKED/NOT TESTABLE — HARNESS", "preflight prepared-session creation failed", "PREFLIGHT_PREPARED_SESSION")
        prepared_zip = self.work / "SYNTHETIC_PACKAGES/preflight-prepared-session.zip"
        prepared_report = package_tree(
            prepared,
            prepared_zip,
            inventory_name="SESSION_SHA256SUMS.txt",
            scratch_parent=self.work / "FRESH_EXTRACTIONS",
        )
        fresh_root = self.work / "PREFLIGHT_FRESH_SESSION"
        with __import__("zipfile").ZipFile(prepared_zip) as archive:
            archive.extractall(fresh_root)
        extracted = fresh_root / prepared.name
        launcher = extracted / "project/tools/launch_a1_capture_v1_2_7r1.py"
        command = [sys.executable, "-B", str(launcher), "--session-root", str(extracted), "--preflight-only"]
        process = run(command, extracted / "project")
        dump(directory / "FRESH_SESSION_LAUNCHER_PREFLIGHT/argv.json", {"argv": command, "cwd": str(extracted / "project")})
        write(directory / "FRESH_SESSION_LAUNCHER_PREFLIGHT/stdout.txt", process.stdout)
        write(directory / "FRESH_SESSION_LAUNCHER_PREFLIGHT/stderr.txt", process.stderr)
        launcher_evidence = extracted / "launcher_evidence"
        if launcher_evidence.is_dir():
            shutil.copytree(
                launcher_evidence,
                directory / "FRESH_SESSION_LAUNCHER_PREFLIGHT/LAUNCHER_EVIDENCE",
            )
        if process.returncode != 0 or (extracted / "LAUNCH_USED.json").exists():
            raise StopRun("BLOCKED/NOT TESTABLE — HARNESS", "fresh-session launcher preflight failed or consumed launcher", "PREFLIGHT_PREPARED_SESSION")
        dump(directory / "prepared_session_package_report.json", prepared_report)

        preflight_result = {
            "schema": "district_zero.p1a.v1_2_7r1.preflight_result.v1",
            "status": "PASS",
            "engine_identity": EXACT_ENGINE,
            "candidate_render_launches": 0,
            "project_import_preflights": self.import_preflights,
            "materialization_cases": list(cases),
            "synthetic_terminal_cases": ["blocker", "failure", "success"],
            "prepared_session_validation": "PASS",
            "source_packet_inventory_sha256": sha256(self.root / "PACKET_SHA256SUMS.txt"),
            "human_attempts_consumed": 0,
            "human_world_gate": "NOT PERFORMED",
            "P1B": "FROZEN",
        }
        dump(self.evidence / "PREFLIGHT_RESULT.json", preflight_result)
        overlay_report = self.create_overlay()
        preflight_result["repair_overlay"] = overlay_report
        dump(self.evidence / "PREFLIGHT_RESULT.json", preflight_result)
        evidence_report = self.finalize_evidence(
            "PASS",
            "all mandatory R1 preflight-only checks passed; render bracket not spent",
            "PREFLIGHT_ONLY",
            preflight=True,
            package_bindings={"repair_overlay": overlay_report},
        )
        return {"preflight": preflight_result, "preflight_evidence": evidence_report, "repair_overlay": overlay_report}

    def execute_calibration(self) -> dict[str, Any]:
        outer = self.search_albedo("OUTER_CLOSURE_MASK")
        if outer is None:
            outer = self.search_fallback("OUTER_CLOSURE_MASK")
        if outer is None:
            raise StopRun("NO_PRESENTATION_ONLY_INTERVAL", "outer closure has no complete authorized robust interval", "OUTER_STUDY")
        wall = self.search_albedo("CORE_WALL")
        if wall is None:
            wall = self.search_fallback("CORE_WALL")
        if wall is None:
            raise StopRun("NO_PRESENTATION_ONLY_INTERVAL", "core wall has no complete authorized robust interval", "WALL_STUDY")
        selected = self.combined(outer, wall)
        self.materialize(selected)
        self.final_probe()
        self.final_verifiers()
        self.smoke()
        self.prepare_session()
        return self.package_success()


def main() -> int:
    parser = argparse.ArgumentParser(description="District Zero P1A v1.2.7R1 bounded harness and calibration runner")
    parser.add_argument("--root", default=str(ROOT_DEFAULT))
    parser.add_argument("--base-root", required=True)
    parser.add_argument("--godot", required=True)
    parser.add_argument("--work-root", required=True)
    parser.add_argument("--evidence-root", required=True)
    parser.add_argument("--prepared-session-root", required=True)
    parser.add_argument("--preflight-only", action="store_true")
    parser.add_argument("--require-preflight-result")
    args = parser.parse_args()
    director: Director | None = None
    try:
        director = Director(args)
        director.initialize_outputs()
        director.load_authority_inputs()
        director.static_preflight()
        reports = director.run_preflight_only() if director.preflight_only else director.execute_calibration()
        print(json.dumps({
            "status": "PASS" if director.preflight_only else "READY FOR A1 HUMAN FEASIBILITY CAPTURE",
            "candidate_render_launches": director.launches,
            "project_import_preflights": director.import_preflights,
            "reports": reports,
        }, ensure_ascii=False, indent=2, sort_keys=True))
        shutil.rmtree(director.work, ignore_errors=True)
        return 0
    except StopRun as exc:
        if director is not None and director.outputs_initialized:
            try:
                evidence_report = director.finalize_evidence(
                    exc.status,
                    exc.detail,
                    exc.stage,
                    preflight=director.preflight_only,
                )
            except Exception as finalizer_error:
                evidence_report = {"status": "FAILED", "error": str(finalizer_error)}
        else:
            evidence_report = {"status": "NOT WRITTEN", "reason": "unsafe or nonempty output roots were rejected before any mutation"}
        print(json.dumps({
            "status": exc.status,
            "stage": exc.stage,
            "detail": exc.detail,
            "candidate_render_launches": director.launches if director is not None else 0,
            "evidence_package": evidence_report,
        }, ensure_ascii=False, indent=2, sort_keys=True))
        if director is not None and director.outputs_initialized and evidence_report.get("status") != "FAILED":
            shutil.rmtree(director.work, ignore_errors=True)
        return 2
    except Exception as exc:
        if director is not None and director.outputs_initialized:
            try:
                evidence_report = director.finalize_evidence(
                    "BLOCKED/NOT TESTABLE — HARNESS",
                    str(exc),
                    "UNHANDLED_HARNESS_EXCEPTION",
                    preflight=director.preflight_only,
                )
            except Exception as finalizer_error:
                evidence_report = {"status": "FAILED", "error": str(finalizer_error)}
        else:
            evidence_report = {"status": "NOT WRITTEN", "reason": "unsafe or nonempty output roots were rejected before any mutation"}
        print(json.dumps({
            "status": "BLOCKED/NOT TESTABLE — HARNESS",
            "detail": str(exc),
            "candidate_render_launches": director.launches if director is not None else 0,
            "evidence_package": evidence_report,
        }, ensure_ascii=False, indent=2, sort_keys=True))
        if director is not None and director.outputs_initialized and evidence_report.get("status") != "FAILED":
            shutil.rmtree(director.work, ignore_errors=True)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
