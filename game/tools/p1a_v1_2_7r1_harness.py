#!/usr/bin/env python3
"""Shared v1.2.7R1 test-only import, material, evidence, and package helpers."""
from __future__ import annotations

import hashlib
import json
import math
import pathlib
import re
import shutil
import struct
import subprocess
import tempfile
import zipfile
import zlib
from typing import Any, Iterable

EXACT_ENGINE = "4.7.1.stable.official.a13da4feb"
VERSION = "v1.2.7R1"
MATERIALS = ("OUTER_CLOSURE_MASK", "CORE_WALL")
IMAGE_KEYS = ("free_roam_on", "free_roam_off", "a1_on", "a1_off")
ERROR_PATTERNS = tuple(re.compile(value, re.I) for value in (
    r"SCRIPT ERROR", r"Parse Error", r"Failed to load script", r"ERROR:\s+Failed",
    r"not declared in the current scope", r"Could not find type", r"Cannot infer the type",
))
IGNORED_PARTS = {".godot", "__pycache__", ".pytest_cache", ".mypy_cache"}
REQUIRED_CLASS_NAMES = {
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
}


def sha256(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def dump(path: pathlib.Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def write(path: pathlib.Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value, encoding="utf-8", newline="\n")


def run(command: list[str], cwd: pathlib.Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=cwd, capture_output=True, text=True, check=False)


def _number(value: Any, label: str, errors: list[str]) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        errors.append(f"{label} is not a number")
        return 0.0
    number = float(value)
    if not math.isfinite(number):
        errors.append(f"{label} is not finite")
        return 0.0
    return number


def validate_parameters(parameters: Any, registry: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if not isinstance(parameters, dict) or set(parameters) != set(MATERIALS):
        return ["material parameter key set is not exact"]
    for material in MATERIALS:
        record = parameters.get(material)
        if not isinstance(record, dict) or set(record) != {"albedo_scale", "emission_multiplier"}:
            errors.append(f"{material} parameter key set is not exact")
            continue
        scale = _number(record.get("albedo_scale"), f"{material}.albedo_scale", errors)
        emission = _number(record.get("emission_multiplier"), f"{material}.emission_multiplier", errors)
        config = registry["outer_closure" if material == "OUTER_CLOSURE_MASK" else "core_wall"]
        scale_min, scale_max = map(float, config["albedo_scale_domain"])
        scale_quantum = float(config["albedo_scale_quantum"])
        emission_min, emission_max = map(float, registry["fallback"]["emission_multiplier_domain"])
        emission_quantum = float(registry["fallback"]["emission_multiplier_quantum"])
        if not scale_min <= scale <= scale_max:
            errors.append(f"{material}.albedo_scale outside registered domain")
        if not emission_min <= emission <= emission_max:
            errors.append(f"{material}.emission_multiplier outside registered domain")
        if abs(scale / scale_quantum - round(scale / scale_quantum)) > 1e-8:
            errors.append(f"{material}.albedo_scale is off quantum")
        if abs(emission / emission_quantum - round(emission / emission_quantum)) > 1e-8:
            errors.append(f"{material}.emission_multiplier is off quantum")
    return errors


def patch_builder(baseline: str, parameters: dict[str, Any], registry: dict[str, Any]) -> str:
    errors = validate_parameters(parameters, registry)
    if errors:
        raise ValueError("; ".join(errors))
    outer_anchor = "\t\treturn Color(0.38, 0.42, 0.44)"
    wall_anchor = "\treturn Color(0.60, 0.63, 0.68)"
    material_anchor = "\t\tmaterial.transparency = BaseMaterial3D.TRANSPARENCY_DISABLED\n"
    if baseline.count(outer_anchor) != 1 or baseline.count(wall_anchor) != 1:
        raise ValueError("frozen material literal anchors are not unique")
    if baseline.count(material_anchor) != 1:
        raise ValueError("solid material insertion anchor is not unique")
    colors: dict[str, list[float]] = {}
    for material in MATERIALS:
        scale = float(parameters[material]["albedo_scale"])
        colors[material] = [float(channel) * scale for channel in registry["base_materials"][material]["rgb"]]
        if any(channel < 0.0 or channel > 1.0 for channel in colors[material]):
            raise ValueError(f"{material} channel outside [0,1]")
    outer = ", ".join(f"{channel:.8f}" for channel in colors["OUTER_CLOSURE_MASK"])
    wall = ", ".join(f"{channel:.8f}" for channel in colors["CORE_WALL"])
    output = baseline.replace(outer_anchor, f"\t\treturn Color({outer})", 1)
    output = output.replace(wall_anchor, f"\treturn Color({wall})", 1)
    emission_lines: list[str] = []
    for material in MATERIALS:
        multiplier = float(parameters[material]["emission_multiplier"])
        if multiplier > 0.0:
            emission_lines.extend((
                f'\t\tif source_id == "{material}":',
                "\t\t\tmaterial.emission_enabled = true",
                f"\t\t\tmaterial.emission = material.albedo_color * {multiplier:.8f}",
            ))
    if emission_lines:
        block = (
            material_anchor
            + "\t\t# V1_2_7_CALIBRATION_EMISSION_BEGIN\n"
            + "\n".join(emission_lines)
            + "\n\t\t# V1_2_7_CALIBRATION_EMISSION_END\n"
        )
        output = output.replace(material_anchor, block, 1)
    return output


def expected_builder_from_selected(
    baseline: str,
    selected: Any,
    registry: dict[str, Any],
) -> tuple[str | None, list[str]]:
    errors: list[str] = []
    if not isinstance(selected, dict):
        return None, ["selected presentation is not an object"]
    required_keys = {
        "schema",
        "status",
        "selected_candidate_id",
        "parameters",
        "selection_rule",
        "presentation_delta",
        "selected_metrics",
        "selected_ray_result",
        "source_material_file_sha256",
        "evaluated_source_sha256",
    }
    if set(selected) != required_keys:
        errors.append("selected presentation key set is not exact")
    if selected.get("schema") != "district_zero.p1a.v1_2_7r1.selected_presentation.v1":
        errors.append("selected presentation schema mismatch")
    if selected.get("status") != "PASS":
        errors.append("selected presentation status is not PASS")
    if not isinstance(selected.get("selected_candidate_id"), str) or not selected["selected_candidate_id"]:
        errors.append("selected candidate id absent")
    if selected.get("selection_rule") != registry.get("selection_rule"):
        errors.append("selected presentation rule differs from frozen registry")
    errors.extend(validate_parameters(selected.get("parameters"), registry))
    if errors:
        return None, errors
    try:
        expected = patch_builder(baseline, selected["parameters"], registry)
    except ValueError as exc:
        return None, [str(exc)]
    digest = hashlib.sha256(expected.encode("utf-8")).hexdigest()
    if selected.get("source_material_file_sha256") != digest:
        errors.append("selected source hash is not bound to canonical bytes")
    if selected.get("evaluated_source_sha256") != digest:
        errors.append("selected evaluated-source hash is not bound to canonical bytes")
    delta = 0.0
    for material in MATERIALS:
        base = [float(value) for value in registry["base_materials"][material]["rgb"]]
        scale = float(selected["parameters"][material]["albedo_scale"])
        emission = float(selected["parameters"][material]["emission_multiplier"])
        rgb = [channel * scale for channel in base]
        delta += sum(abs(current - original) for current, original in zip(rgb, base))
        delta += sum(abs(channel * emission) for channel in rgb)
    observed_delta = selected.get("presentation_delta")
    if (
        isinstance(observed_delta, bool)
        or not isinstance(observed_delta, (int, float))
        or not math.isfinite(float(observed_delta))
        or abs(float(observed_delta) - delta) > 1e-12
    ):
        errors.append("selected presentation delta is not canonical")
    metrics = selected.get("selected_metrics")
    checks = metrics.get("checks", []) if isinstance(metrics, dict) else []
    if (
        not isinstance(metrics, dict)
        or metrics.get("status") != "PASS"
        or len(checks) != 21
        or len({check.get("id") for check in checks if isinstance(check, dict)}) != 21
        or any(not isinstance(check, dict) or check.get("pass") is not True for check in checks)
    ):
        errors.append("selected visual evidence is not 21/21 PASS")
    ray = selected.get("selected_ray_result")
    if (
        not isinstance(ray, dict)
        or ray.get("status") != "PASS"
        or ray.get("sample_count") != 14
        or ray.get("mismatch_count") != 0
        or ray.get("mismatches") != []
    ):
        errors.append("selected ray evidence is not 14/14 PASS")
    return expected, errors


def scan_error_text(texts: Iterable[str]) -> list[str]:
    errors: list[str] = []
    for text in texts:
        for line in text.splitlines():
            value = line.strip()
            if value and any(pattern.search(value) for pattern in ERROR_PATTERNS) and value not in errors:
                errors.append(value)
    return errors


def discover_script_classes(project: pathlib.Path) -> dict[str, str]:
    classes: dict[str, str] = {}
    for path in sorted((project / "scripts").glob("*.gd")):
        match = re.search(r"(?m)^class_name\s+([A-Za-z_][A-Za-z0-9_]*)\s*$", path.read_text(encoding="utf-8"))
        if match:
            classes[match.group(1)] = "res://" + path.relative_to(project).as_posix()
    return classes


def cache_resolution(cache: pathlib.Path, required: dict[str, str]) -> tuple[dict[str, Any], list[str]]:
    text = cache.read_text(encoding="utf-8", errors="replace") if cache.is_file() else ""
    pairs: dict[str, list[str]] = {}
    for match in re.finditer(r"\{(.*?)\}", text, re.S):
        block = match.group(1)
        class_match = re.search(r'"class"\s*:\s*&?"([A-Za-z_][A-Za-z0-9_]*)"', block)
        path_match = re.search(r'"path"\s*:\s*"(res://[^"]+)"', block)
        if class_match and path_match:
            pairs.setdefault(class_match.group(1), []).append(path_match.group(1))
    classes: dict[str, Any] = {}
    missing: list[str] = []
    for name, resource_path in required.items():
        observed_paths = pairs.get(name, [])
        class_present = name in pairs
        path_present = resource_path in observed_paths
        resolved = observed_paths == [resource_path]
        classes[name] = {
            "resource_path": resource_path,
            "class_present": class_present,
            "path_present": path_present,
            "observed_paths": observed_paths,
            "resolved": resolved,
        }
        if not resolved:
            missing.append(name)
    summary = {
        "cache_generated": cache.is_file() and cache.stat().st_size > 0,
        "cache_byte_size": cache.stat().st_size if cache.is_file() else 0,
        "cache_sha256": sha256(cache) if cache.is_file() else None,
        "parsed_class_paths": pairs,
        "classes": classes,
    }
    return summary, missing


def _run_stage(
    godot: str,
    project: pathlib.Path,
    evidence: pathlib.Path,
    name: str,
    arguments: list[str],
) -> tuple[subprocess.CompletedProcess[str], str]:
    stage = evidence / name
    stage.mkdir(parents=True, exist_ok=True)
    engine_log = stage / "engine.txt"
    command = [godot, *arguments, "--log-file", str(engine_log)]
    dump(stage / "argv.json", {"argv": command, "cwd": str(project)})
    process = run(command, project)
    write(stage / "stdout.txt", process.stdout)
    write(stage / "stderr.txt", process.stderr)
    if not engine_log.is_file():
        write(engine_log, "")
    dump(stage / "process_result.json", {"returncode": process.returncode})
    return process, engine_log.read_text(encoding="utf-8", errors="replace")


def import_and_parse_project(
    godot: str,
    project: pathlib.Path,
    evidence: pathlib.Path,
    *,
    target_script: str,
    required_classes: dict[str, str],
    expected_builder_sha256: str,
) -> dict[str, Any]:
    evidence.mkdir(parents=True, exist_ok=True)
    version = run([godot, "--version"], project)
    dump(evidence / "engine_identity.json", {
        "argv": [godot, "--version"],
        "required": EXACT_ENGINE,
        "observed": version.stdout.strip(),
        "returncode": version.returncode,
        "match": version.returncode == 0 and version.stdout.strip() == EXACT_ENGINE,
    })
    imported, import_log = _run_stage(
        godot, project, evidence, "IMPORT", ["--headless", "--path", str(project), "--import"],
    )
    parsed, parse_log = _run_stage(
        godot, project, evidence, "PARSE", ["--headless", "--editor", "--quit", "--path", str(project)],
    )
    checked, check_log = _run_stage(
        godot,
        project,
        evidence,
        "TARGET_CHECK",
        ["--headless", "--path", str(project), "--check-only", "--script", target_script],
    )
    summary, missing = cache_resolution(project / ".godot/global_script_class_cache.cfg", required_classes)
    dump(evidence / "class_cache_summary.json", summary)
    discovered = discover_script_classes(project)
    builder = project / "scripts/p1a_world_builder.gd"
    target = project / target_script.removeprefix("res://")
    errors = scan_error_text((
        imported.stdout, imported.stderr, import_log,
        parsed.stdout, parsed.stderr, parse_log,
        checked.stdout, checked.stderr, check_log,
    ))
    blockers: list[str] = []
    if version.returncode != 0 or version.stdout.strip() != EXACT_ENGINE:
        blockers.append("exact engine mismatch")
    if imported.returncode != 0:
        blockers.append("import process returned nonzero")
    if parsed.returncode != 0:
        blockers.append("parse validation returned nonzero")
    if checked.returncode != 0:
        blockers.append("target check-only returned nonzero")
    if not summary["cache_generated"]:
        blockers.append("global script-class cache absent")
    if missing:
        blockers.append(f"registered classes unresolved: {missing}")
    if discovered != required_classes:
        blockers.append("discovered registered-class map differs from authority")
    if errors:
        blockers.append("parse/import/load errors emitted")
    if not target.is_file():
        blockers.append("target script absent")
    if not builder.is_file() or sha256(builder) != expected_builder_sha256:
        blockers.append("material source identity mismatch")
    result = {
        "schema": "district_zero.p1a.v1_2_7r1.project_import_preflight.v1",
        "status": "PASS" if not blockers else "BLOCKED/NOT TESTABLE — HARNESS",
        "project_root": str(project.resolve()),
        "required_engine": EXACT_ENGINE,
        "observed_engine": version.stdout.strip(),
        "target_script": target_script,
        "target_script_sha256": sha256(target) if target.is_file() else None,
        "material_source_sha256": sha256(builder) if builder.is_file() else None,
        "expected_material_source_sha256": expected_builder_sha256,
        "import_returncode": imported.returncode,
        "parse_returncode": parsed.returncode,
        "target_check_returncode": checked.returncode,
        "class_cache": summary,
        "required_classes": required_classes,
        "discovered_classes": discovered,
        "parse_or_import_errors": errors,
        "blockers": blockers,
    }
    dump(evidence / "result.json", result)
    return result


def validate_import_binding(
    record: Any,
    *,
    project: pathlib.Path,
    target_script: str,
    builder_sha256: str,
    required_classes: dict[str, str],
) -> list[str]:
    if not isinstance(record, dict):
        return ["import preflight record absent"]
    errors: list[str] = []
    if record.get("status") != "PASS":
        errors.append("import preflight status is not PASS")
    if record.get("project_root") != str(project.resolve()):
        errors.append("import preflight project-root binding mismatch")
    if record.get("observed_engine") != EXACT_ENGINE:
        errors.append("import preflight engine mismatch")
    if record.get("target_script") != target_script:
        errors.append("import preflight target mismatch")
    if record.get("material_source_sha256") != builder_sha256:
        errors.append("import preflight material-source binding mismatch")
    if record.get("expected_material_source_sha256") != builder_sha256:
        errors.append("import preflight expected material-source binding mismatch")
    if record.get("required_classes") != required_classes or set(required_classes) != REQUIRED_CLASS_NAMES:
        errors.append("import preflight required-class authority mismatch")
    if record.get("parse_or_import_errors"):
        errors.append("import preflight contains parse/import errors")
    cache = record.get("class_cache", {})
    if not isinstance(cache, dict) or cache.get("cache_generated") is not True:
        errors.append("import preflight class cache missing")
    classes = cache.get("classes", {}) if isinstance(cache, dict) else {}
    if (
        not isinstance(classes, dict)
        or set(classes) != set(required_classes)
        or not all(
            isinstance(value, dict)
            and value.get("resolved") is True
            and value.get("resource_path") == required_classes[name]
            for name, value in classes.items()
        )
    ):
        errors.append("import preflight registered classes unresolved")
    return errors


def png_info(path: pathlib.Path) -> dict[str, Any] | None:
    if not path.is_file():
        return None
    data = path.read_bytes()
    if len(data) < 45 or data[:8] != b"\x89PNG\r\n\x1a\n":
        return None
    position = 8
    chunks: list[tuple[bytes, bytes]] = []
    try:
        while position + 12 <= len(data):
            length = struct.unpack(">I", data[position:position + 4])[0]
            end = position + 12 + length
            if end > len(data):
                return None
            kind = data[position + 4:position + 8]
            payload = data[position + 8:position + 8 + length]
            observed_crc = struct.unpack(">I", data[position + 8 + length:end])[0]
            if zlib.crc32(kind + payload) & 0xFFFFFFFF != observed_crc:
                return None
            chunks.append((kind, payload))
            position = end
            if kind == b"IEND":
                break
    except (struct.error, zlib.error):
        return None
    if position != len(data) or not chunks or chunks[0][0] != b"IHDR" or chunks[-1][0] != b"IEND":
        return None
    if len([kind for kind, _payload in chunks if kind == b"IHDR"]) != 1:
        return None
    ihdr = chunks[0][1]
    if len(ihdr) != 13:
        return None
    width, height, bit_depth, color_type, compression, filter_method, interlace = struct.unpack(">IIBBBBB", ihdr)
    if (bit_depth, color_type, compression, filter_method, interlace) != (8, 2, 0, 0, 0):
        return None
    compressed = b"".join(payload for kind, payload in chunks if kind == b"IDAT")
    if not compressed:
        return None
    try:
        raw = zlib.decompress(compressed)
    except zlib.error:
        return None
    expected_length = height * (1 + width * 3)
    if len(raw) != expected_length:
        return None
    stride = 1 + width * 3
    if any(raw[row * stride] > 4 for row in range(height)):
        return None
    return {"width": width, "height": height, "bit_depth": bit_depth, "color_type": color_type}


def validate_candidate_record(
    record: Any,
    candidate_dir: pathlib.Path,
    *,
    project: pathlib.Path,
    expected_builder: str,
    target_script: str,
    registry: dict[str, Any],
    expected_check_ids: list[str],
    expected_ray_ids: dict[str, list[str]],
    required_classes: dict[str, str],
    recomputed_metrics: dict[str, Any],
) -> list[str]:
    if not isinstance(record, dict):
        return ["candidate record is not an object"]
    errors: list[str] = []
    builder_digest = hashlib.sha256(expected_builder.encode("utf-8")).hexdigest()
    if record.get("schema") != "district_zero.p1a.v1_2_7r1.candidate_record.v1":
        errors.append("candidate schema mismatch")
    if not isinstance(record.get("candidate_id"), str) or not record.get("candidate_id"):
        errors.append("candidate id absent")
    if not isinstance(record.get("stage"), str) or not record.get("stage"):
        errors.append("candidate stage absent")
    errors.extend(validate_parameters(record.get("parameters"), registry))
    if record.get("engine_identity") != EXACT_ENGINE:
        errors.append("candidate engine identity mismatch")
    if record.get("project_material_source_sha256") != builder_digest:
        errors.append("candidate material-source hash mismatch")
    evaluated_path = candidate_dir / str(record.get("evaluated_source_path", ""))
    if (
        record.get("evaluated_source_path") != "evaluated_p1a_world_builder.gd"
        or not evaluated_path.is_file()
        or evaluated_path.read_text(encoding="utf-8") != expected_builder
        or sha256(evaluated_path) != builder_digest
    ):
        errors.append("preserved evaluated material source is absent or noncanonical")
    builder_path = project / "scripts/p1a_world_builder.gd"
    if not builder_path.is_file() or builder_path.read_text(encoding="utf-8") != expected_builder:
        errors.append("candidate material-source bytes are not canonical")
    command = record.get("command")
    if (
        not isinstance(command, list)
        or not all(isinstance(token, str) for token in command)
        or "--path" not in command
        or str(project) not in command
        or "--script" not in command
        or target_script not in command
        or "--output-dir" not in command
        or str(candidate_dir) not in command
    ):
        errors.append("candidate argv is absent or not bound to project/evidence roots")
    errors.extend(validate_import_binding(
        record.get("import_preflight"),
        project=project,
        target_script=target_script,
        builder_sha256=builder_digest,
        required_classes=required_classes,
    ))
    for name in (
        "stdout_sha256",
        "stderr_sha256",
        "engine_log_sha256",
        "probe_result_sha256",
        "metrics_result_sha256",
        "import_preflight_result_sha256",
    ):
        if re.fullmatch(r"[0-9a-f]{64}", str(record.get(name, ""))) is None:
            errors.append(f"{name} is not a SHA-256")
    for name, filename in (
        ("stdout_sha256", "stdout.txt"),
        ("stderr_sha256", "stderr.txt"),
        ("engine_log_sha256", "engine.txt"),
        ("probe_result_sha256", "probe_result.json"),
        ("metrics_result_sha256", "native-visual-metric-result.json"),
        ("import_preflight_result_sha256", "IMPORT_PREFLIGHT/result.json"),
    ):
        path = candidate_dir / filename
        if not path.is_file() or record.get(name) != sha256(path):
            errors.append(f"{filename} identity mismatch")
    images = record.get("images")
    if not isinstance(images, dict) or set(images) != set(IMAGE_KEYS):
        errors.append("candidate image key set is not exact")
    else:
        for name in IMAGE_KEYS:
            item = images.get(name)
            if not isinstance(item, dict) or set(item) != {"path", "sha256", "png"}:
                errors.append(f"{name} image record malformed")
                continue
            path = candidate_dir / str(item.get("path", ""))
            info = png_info(path)
            if not path.is_file() or item.get("sha256") != sha256(path):
                errors.append(f"{name} image identity mismatch")
            if info is None or info.get("width") != 1280 or info.get("height") != 720 or info.get("bit_depth") != 8 or info.get("color_type") != 2:
                errors.append(f"{name} is not a supported 1280x720 8-bit PNG")
            if item.get("png") != info:
                errors.append(f"{name} PNG metadata mismatch")
    metrics = record.get("metrics")
    if metrics != recomputed_metrics:
        errors.append("candidate metrics do not equal canonical recomputation")
    checks = metrics.get("checks", []) if isinstance(metrics, dict) else []
    ids = [check.get("id") for check in checks if isinstance(check, dict)]
    if len(checks) != 21 or len(set(ids)) != 21 or ids != expected_check_ids:
        errors.append("candidate metric check inventory is not exact")
    if any(not isinstance(check.get("pass"), bool) or isinstance(check.get("observed"), bool) or not isinstance(check.get("observed"), (int, float)) or not math.isfinite(float(check.get("observed", math.nan))) for check in checks if isinstance(check, dict)):
        errors.append("candidate metric check value malformed")
    expected_metric_status = "PASS" if checks and all(check.get("pass") is True for check in checks) else "FAIL"
    if not isinstance(metrics, dict) or metrics.get("status") != expected_metric_status:
        errors.append("candidate metric status incoherent")
    ray = record.get("ray_result")
    if not isinstance(ray, dict) or ray.get("sample_count") != 14:
        errors.append("candidate ray sample inventory is not exact")
    else:
        mismatches = ray.get("mismatches")
        count = ray.get("mismatch_count")
        if not isinstance(mismatches, list) or not isinstance(count, int) or count != len(mismatches):
            errors.append("candidate ray mismatch inventory incoherent")
        expected_ray_status = "PASS" if count == 0 else "FAIL"
        if ray.get("status") != expected_ray_status:
            errors.append("candidate ray status incoherent")
    probe_path = candidate_dir / "probe_result.json"
    try:
        probe = json.loads(probe_path.read_text(encoding="utf-8"))
    except Exception:
        probe = {}
    if (
        probe.get("schema") != "district_zero.p1a.v1_2_7.visual_probe_result.v1"
        or probe.get("engine_identity") != EXACT_ENGINE
        or probe.get("viewport_size_px") != [1280, 720]
        or probe.get("ray_result") != ray
    ):
        errors.append("candidate probe result is absent or incoherent")
    views = probe.get("views")
    if not isinstance(views, dict) or set(views) != set(expected_ray_ids):
        errors.append("candidate probe view inventory is not exact")
    else:
        observed_ray_count = 0
        for view_name, expected_ids in expected_ray_ids.items():
            view = views.get(view_name)
            records = view.get("records", {}) if isinstance(view, dict) else {}
            if not isinstance(records, dict) or list(records) != expected_ids:
                errors.append(f"candidate {view_name} ray-record inventory is not exact")
            else:
                observed_ray_count += len(records)
        if observed_ray_count != 14:
            errors.append("candidate probe does not contain exactly 14 ray records")
    expected_returncode = 0 if probe.get("status") == "PASS" else 1 if probe.get("status") == "FAIL" else None
    if expected_returncode is None or record.get("returncode") != expected_returncode:
        errors.append("candidate process/result contract mismatch")
    expected_probe_status = "PASS" if isinstance(ray, dict) and ray.get("mismatch_count") == 0 else "FAIL"
    if probe.get("status") != expected_probe_status:
        errors.append("candidate probe status is incoherent with ray mismatches")
    logs = []
    for filename in ("stdout.txt", "stderr.txt", "engine.txt"):
        path = candidate_dir / filename
        logs.append(path.read_text(encoding="utf-8", errors="replace") if path.is_file() else "")
    if scan_error_text(logs):
        errors.append("candidate runtime emitted parse/load errors")
    return errors


def executed_complete(record: Any) -> bool:
    if not isinstance(record, dict):
        return False
    metrics = record.get("metrics")
    checks = metrics.get("checks", []) if isinstance(metrics, dict) else []
    ray = record.get("ray_result")
    images = record.get("images")
    return (
        record.get("schema") == "district_zero.p1a.v1_2_7r1.candidate_record.v1"
        and record.get("evidence_validator") == "p1a_v1_2_7r1_harness.validate_candidate_record.v1"
        and record.get("execution_status") == "EXECUTED_COMPLETE"
        and record.get("evidence_complete") is True
        and record.get("validation_errors") == []
        and record.get("returncode") in (0, 1)
        and isinstance(images, dict)
        and set(images) == set(IMAGE_KEYS)
        and all(
            isinstance(item, dict)
            and re.fullmatch(r"[0-9a-f]{64}", str(item.get("sha256", ""))) is not None
            and item.get("png") == {"width": 1280, "height": 720, "bit_depth": 8, "color_type": 2}
            for item in images.values()
        )
        and isinstance(metrics, dict)
        and metrics.get("status") in ("PASS", "FAIL")
        and len(checks) == 21
        and len({check.get("id") for check in checks if isinstance(check, dict)}) == 21
        and isinstance(ray, dict)
        and ray.get("status") in ("PASS", "FAIL")
        and ray.get("sample_count") == 14
        and isinstance(ray.get("mismatch_count"), int)
        and isinstance(ray.get("mismatches"), list)
        and ray.get("mismatch_count") == len(ray.get("mismatches"))
    )


def _ignored(path: pathlib.Path, root: pathlib.Path) -> bool:
    relative = path.relative_to(root)
    return (
        any(part in IGNORED_PARTS for part in relative.parts)
        or path.name == ".DS_Store"
        or path.name.startswith("._")
        or path.name.endswith((".pyc", ".pyo"))
    )


def substantive_files(root: pathlib.Path, inventory_name: str | None = None) -> list[pathlib.Path]:
    return sorted(
        (
            path for path in root.rglob("*")
            if path.is_file()
            and not _ignored(path, root)
            and (inventory_name is None or path != root / inventory_name)
        ),
        key=lambda path: path.relative_to(root).as_posix().encode("utf-8"),
    )


def write_inventory(root: pathlib.Path, inventory_name: str) -> int:
    inventory = root / inventory_name
    paths = substantive_files(root, inventory_name)
    write(inventory, "".join(f"{sha256(path)}  {path.relative_to(root).as_posix()}\n" for path in paths))
    return len(paths)


def verify_inventory(root: pathlib.Path, inventory_name: str) -> list[str]:
    inventory = root / inventory_name
    if not inventory.is_file():
        return [f"missing inventory {inventory_name}"]
    errors: list[str] = []
    seen: set[str] = set()
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
        if not target.is_file() or sha256(target) != digest:
            errors.append(f"checksum mismatch: {relative}")
    actual = {path.relative_to(root).as_posix() for path in substantive_files(root, inventory_name)}
    if actual != seen:
        errors.append(f"inventory coverage mismatch missing={sorted(actual-seen)[:5]} extra={sorted(seen-actual)[:5]}")
    return errors


def tree_hashes(root: pathlib.Path) -> dict[str, str]:
    return {path.relative_to(root).as_posix(): sha256(path) for path in substantive_files(root)}


def _safe_members(names: list[str], root_name: str) -> list[str]:
    errors: list[str] = []
    if len(names) != len(set(names)):
        errors.append("duplicate ZIP entries")
    for name in names:
        pure = pathlib.PurePosixPath(name)
        if pure.is_absolute() or ".." in pure.parts or not pure.parts or pure.parts[0] != root_name:
            errors.append(f"unsafe ZIP member: {name}")
        if any(part in IGNORED_PARTS or part == "__MACOSX" for part in pure.parts) or pure.name == ".DS_Store" or pure.name.startswith("._"):
            errors.append(f"forbidden ZIP member: {name}")
    return errors


def deterministic_zip(source: pathlib.Path, output: pathlib.Path) -> None:
    if output.exists():
        raise FileExistsError(f"output already exists: {output}")
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in substantive_files(source):
            relative = source.name + "/" + path.relative_to(source).as_posix()
            info = zipfile.ZipInfo(relative, (1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = (0o100755 if path.stat().st_mode & 0o111 else 0o100644) << 16
            archive.writestr(info, path.read_bytes())


def fresh_extract_verify(
    source: pathlib.Path,
    archive_path: pathlib.Path,
    *,
    inventory_name: str,
    scratch_parent: pathlib.Path,
) -> dict[str, Any]:
    scratch_parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(archive_path) as archive:
        bad_member = archive.testzip()
        names = archive.namelist()
        member_errors = _safe_members(names, source.name)
        if bad_member is not None:
            member_errors.append(f"ZIP CRC failure at {bad_member}")
        if member_errors:
            return {"status": "FAIL", "errors": member_errors}
        temp = pathlib.Path(tempfile.mkdtemp(prefix="v127r1-fresh-", dir=scratch_parent))
        try:
            archive.extractall(temp)
            extracted = temp / source.name
            inventory_errors = verify_inventory(extracted, inventory_name)
            source_map = tree_hashes(source)
            extracted_map = tree_hashes(extracted)
            errors = list(inventory_errors)
            if source_map != extracted_map:
                errors.append("fresh-extracted tree differs from source tree")
            return {
                "status": "PASS" if not errors else "FAIL",
                "errors": errors,
                "entry_count": len(names),
                "source_file_count": len(source_map),
                "fresh_file_count": len(extracted_map),
                "source_tree_sha256": hashlib.sha256(json.dumps(source_map, sort_keys=True, separators=(",", ":")).encode()).hexdigest(),
                "fresh_tree_sha256": hashlib.sha256(json.dumps(extracted_map, sort_keys=True, separators=(",", ":")).encode()).hexdigest(),
            }
        finally:
            shutil.rmtree(temp, ignore_errors=True)


def package_tree(
    source: pathlib.Path,
    output: pathlib.Path,
    *,
    inventory_name: str,
    scratch_parent: pathlib.Path,
) -> dict[str, Any]:
    inventory_errors = verify_inventory(source, inventory_name)
    if inventory_errors:
        raise RuntimeError(f"source inventory invalid: {inventory_errors[:5]}")
    if output.exists():
        raise FileExistsError(f"package output already exists: {output}")
    temporary = output.with_name(output.name + ".partial")
    if temporary.exists():
        raise FileExistsError(f"partial package already exists: {temporary}")
    deterministic_zip(source, temporary)
    verification = fresh_extract_verify(
        source, temporary, inventory_name=inventory_name, scratch_parent=scratch_parent,
    )
    if verification.get("status") != "PASS":
        raise RuntimeError(f"fresh-extraction verification failed: {verification.get('errors')}")
    temporary.replace(output)
    return {
        "path": str(output),
        "byte_size": output.stat().st_size,
        "sha256": sha256(output),
        "integrity": "PASS",
        "fresh_extraction": verification,
        "inventory_name": inventory_name,
        "inventory_record_count": len((source / inventory_name).read_text(encoding="utf-8").splitlines()),
    }
