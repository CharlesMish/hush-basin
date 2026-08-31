#!/usr/bin/env python3
"""Pure/static regression suite for the six authorized v1.2.7R1 repairs."""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
import pathlib
import shutil
import tempfile
from typing import Any, Callable

ROOT_DEFAULT = pathlib.Path(__file__).resolve().parents[1]

from p1a_v1_2_7_metrics import compute as compute_metrics
from p1a_v1_2_7r1_harness import (
    EXACT_ENGINE,
    IMAGE_KEYS,
    _safe_members,
    cache_resolution,
    dump,
    executed_complete,
    expected_builder_from_selected,
    package_tree,
    patch_builder,
    png_info,
    sha256,
    validate_candidate_record,
    validate_parameters,
    verify_inventory,
    write,
    write_inventory,
)
from run_v1_2_7r1_calibration import (
    Director,
    StopRun,
    complete_stage_records,
    copy_project,
    exhausted_domain_status,
    local_pass,
    parameters,
    presentation_delta,
    select_combined,
)
from prepare_v1_2_7r1_a1_session import copy_clean as copy_prepared_project
from run_v1_2_7r1_c1 import copy_runtime as copy_c1_runtime

PROBE = "res://tests/p1a_v1_2_7_visual_probe.gd"
VALIDATOR = "p1a_v1_2_7r1_harness.validate_candidate_record.v1"


class Suite:
    def __init__(self) -> None:
        self.cases: list[dict[str, Any]] = []

    def check(self, name: str, condition: bool, detail: str = "") -> None:
        self.cases.append({"name": name, "status": "PASS" if condition else "FAIL", "detail": detail})

    def raises(self, name: str, function: Callable[[], Any]) -> None:
        try:
            function()
        except Exception as exc:
            self.check(name, True, type(exc).__name__)
        else:
            self.check(name, False, "expected an exception")


def selected_record(builder: str, value: dict[str, Any], registry: dict[str, Any], checks: list[dict[str, Any]]) -> dict[str, Any]:
    digest = hashlib.sha256(builder.encode("utf-8")).hexdigest()
    return {
        "schema": "district_zero.p1a.v1_2_7r1.selected_presentation.v1",
        "status": "PASS",
        "selected_candidate_id": "TEST-CANDIDATE",
        "parameters": value,
        "selection_rule": registry["selection_rule"],
        "presentation_delta": presentation_delta(value, registry),
        "selected_metrics": {"status": "PASS", "checks": checks},
        "selected_ray_result": {
            "status": "PASS",
            "sample_count": 14,
            "mismatch_count": 0,
            "mismatches": [],
        },
        "source_material_file_sha256": digest,
        "evaluated_source_sha256": digest,
    }


def material_cases(root: pathlib.Path, suite: Suite) -> None:
    baseline_path = root / "tests/fixtures/v1_2_7_v1_2_6_world_builder.gd"
    baseline = baseline_path.read_text(encoding="utf-8")
    registry = json.loads((root / "tests/fixtures/v1_2_7_calibration_registry.json").read_text(encoding="utf-8"))
    run1 = json.loads((root / "director_inputs/v1_2_6_run1_validation_evidence/NATIVE_VISUALS/native-visual-metric-result.json").read_text(encoding="utf-8"))
    passing_checks = [{**check, "pass": True} for check in run1["checks"]]
    suite.check("frozen builder fixture SHA-256", sha256(baseline_path) == "c016d5e2654919d6de5e1416ab21a40da81149ec11100dae8d95a89922b9dc38")
    vectors = {
        "identity": (parameters(), "65271efe6128580bf79c8b275da52188a2e41e4d6a7aeee45b12573a630f1b1d"),
        "outer-only": (parameters(outer_scale=1.01), "0980450cb6a044d764a84c5453162d4fabb160f158f343318ebdcd856fd92b51"),
        "wall-only": (parameters(wall_scale=1.01), "d80910083024e76024f1f9673d9b557c7fcb201b887ea4b4a0a83201e1b9f6c4"),
        "outer-emission": (parameters(outer_emission=0.01), "b0863c6e889cad0f2e4309e9ba4dd69d76bf372f747df2a622da10fa6dd8b649"),
        "combined": (parameters(outer_scale=1.01, outer_emission=0.01, wall_scale=1.02, wall_emission=0.02), "ddae624e042f14892251c25a0af1a2db8a9e1633ac8d2e718507c8c64eb21376"),
    }
    outputs: dict[str, str] = {}
    for name, (value, expected_hash) in vectors.items():
        output = patch_builder(baseline, value, registry)
        outputs[name] = output
        observed = hashlib.sha256(output.encode("utf-8")).hexdigest()
        suite.check(f"canonical material bytes: {name}", observed == expected_hash, observed)
    emission = outputs["outer-emission"]
    suite.check(
        "emission indentation remains inside solid-material branch",
        "\t\t# V1_2_7_CALIBRATION_EMISSION_BEGIN\n\t\tif source_id == \"OUTER_CLOSURE_MASK\":\n\t\t\tmaterial.emission_enabled = true" in emission,
    )
    suite.check(
        "emission retains normal per-pixel material settings",
        "BaseMaterial3D.SHADING_MODE_PER_PIXEL" in emission
        and "material.metallic = 0.0" in emission
        and "material.roughness = 0.74" in emission,
    )
    valid_selected = selected_record(outputs["combined"], vectors["combined"][0], registry, passing_checks)
    derived, errors = expected_builder_from_selected(baseline, valid_selected, registry)
    suite.check("selected record derives exact canonical bytes", derived == outputs["combined"] and errors == [], str(errors))
    suite.check("unmaterialized baseline cannot satisfy nonidentity selection", derived != baseline)
    suite.check("unauthorized neighboring edit is rejected by exact-byte comparison", derived != outputs["combined"] + "# unauthorized\n")
    bad_hash = copy.deepcopy(valid_selected)
    bad_hash["source_material_file_sha256"] = "0" * 64
    suite.check("selected source-hash mismatch rejected", bool(expected_builder_from_selected(baseline, bad_hash, registry)[1]))
    extra = copy.deepcopy(valid_selected)
    extra["unauthorized"] = True
    suite.check("selected extra key rejected", "selected presentation key set is not exact" in expected_builder_from_selected(baseline, extra, registry)[1])
    for name, value in (
        ("nonfinite", math.nan),
        ("outside-domain", 9.0),
        ("off-quantum", 1.0001),
    ):
        bad = parameters(wall_scale=value)
        suite.check(f"material parameter {name} rejected", bool(validate_parameters(bad, registry)))
    suite.raises("duplicate material anchor rejected", lambda: patch_builder(baseline + "\treturn Color(0.60, 0.63, 0.68)\n", parameters(), registry))


def candidate_fixture(root: pathlib.Path, temporary: pathlib.Path) -> tuple[dict[str, Any], dict[str, Any]]:
    registry = json.loads((root / "tests/fixtures/v1_2_7_calibration_registry.json").read_text(encoding="utf-8"))
    baseline = (root / "tests/fixtures/v1_2_7_v1_2_6_world_builder.gd").read_text(encoding="utf-8")
    builder = patch_builder(baseline, parameters(), registry)
    project = temporary / "project"
    candidate = temporary / "candidate"
    (project / "scripts").mkdir(parents=True)
    write(project / "scripts/p1a_world_builder.gd", builder)
    write(candidate / "evaluated_p1a_world_builder.gd", builder)
    source_images = root / "director_inputs/v1_2_6_run1_validation_evidence/NATIVE_VISUALS"
    image_names = {
        "free_roam_on": "free-roam-after-native.png",
        "free_roam_off": "free-roam-after-shadow-off-reference.png",
        "a1_on": "a1-after-native.png",
        "a1_off": "a1-after-shadow-off-reference.png",
    }
    for filename in image_names.values():
        shutil.copy2(source_images / filename, candidate / filename)
    acceptance = json.loads((root / "tests/fixtures/v1_2_6_visual_acceptance.json").read_text(encoding="utf-8"))
    paths = {
        "FREE_ROAM:on": candidate / image_names["free_roam_on"],
        "FREE_ROAM:off": candidate / image_names["free_roam_off"],
        "A1_FAMILIARIZATION:on": candidate / image_names["a1_on"],
        "A1_FAMILIARIZATION:off": candidate / image_names["a1_off"],
    }
    metrics = compute_metrics(acceptance, paths)
    dump(candidate / "native-visual-metric-result.json", metrics)
    write(candidate / "stdout.txt", "")
    write(candidate / "stderr.txt", "")
    write(candidate / "engine.txt", "")
    class_contract = json.loads((root / "tests/fixtures/disposable_import_preflight.json").read_text(encoding="utf-8"))
    required_classes = dict(class_contract["required_registered_classes"])
    class_summary = {
        name: {
            "resource_path": path,
            "class_present": True,
            "path_present": True,
            "resolved": True,
        }
        for name, path in required_classes.items()
    }
    import_result = {
        "schema": "district_zero.p1a.v1_2_7r1.project_import_preflight.v1",
        "status": "PASS",
        "project_root": str(project.resolve()),
        "required_engine": EXACT_ENGINE,
        "observed_engine": EXACT_ENGINE,
        "target_script": PROBE,
        "material_source_sha256": hashlib.sha256(builder.encode()).hexdigest(),
        "expected_material_source_sha256": hashlib.sha256(builder.encode()).hexdigest(),
        "class_cache": {"cache_generated": True, "classes": class_summary},
        "required_classes": required_classes,
        "parse_or_import_errors": [],
    }
    dump(candidate / "IMPORT_PREFLIGHT/result.json", import_result)
    ray_baseline = json.loads((root / "tests/fixtures/v1_2_6_ray_classification_baseline.json").read_text(encoding="utf-8"))
    expected_ray_ids = {
        "FREE_ROAM": list(ray_baseline["free_roam"]["records"]),
        "A1_FAMILIARIZATION": list(ray_baseline["a1"]["records"]),
    }
    views = {
        view: {"records": {identifier: {} for identifier in identifiers}, "images": {}, "ray_mismatches": []}
        for view, identifiers in expected_ray_ids.items()
    }
    ray = {
        "schema": "district_zero.p1a.v1_2_7.ray_classification_comparison.v1",
        "status": "PASS",
        "sample_count": 14,
        "mismatch_count": 0,
        "mismatches": [],
    }
    probe = {
        "schema": "district_zero.p1a.v1_2_7.visual_probe_result.v1",
        "status": "PASS",
        "engine_identity": EXACT_ENGINE,
        "viewport_size_px": [1280, 720],
        "views": views,
        "ray_result": ray,
    }
    dump(candidate / "probe_result.json", probe)
    record = {
        "schema": "district_zero.p1a.v1_2_7r1.candidate_record.v1",
        "candidate_id": "STATIC-CANDIDATE",
        "stage": "OUTER_ALBEDO",
        "parameters": parameters(),
        "engine_identity": EXACT_ENGINE,
        "command": ["godot", "--path", str(project), "--script", PROBE, "--", "--output-dir", str(candidate)],
        "returncode": 0,
        "project_material_source_sha256": hashlib.sha256(builder.encode()).hexdigest(),
        "evaluated_source_path": "evaluated_p1a_world_builder.gd",
        "images": {
            name: {"path": filename, "sha256": sha256(candidate / filename), "png": png_info(candidate / filename)}
            for name, filename in image_names.items()
        },
        "metrics": metrics,
        "ray_result": ray,
        "import_preflight": import_result,
        "stdout_sha256": sha256(candidate / "stdout.txt"),
        "stderr_sha256": sha256(candidate / "stderr.txt"),
        "engine_log_sha256": sha256(candidate / "engine.txt"),
        "probe_result_sha256": sha256(candidate / "probe_result.json"),
        "metrics_result_sha256": sha256(candidate / "native-visual-metric-result.json"),
        "import_preflight_result_sha256": sha256(candidate / "IMPORT_PREFLIGHT/result.json"),
        "evidence_validator": VALIDATOR,
    }
    context = {
        "candidate": candidate,
        "project": project,
        "builder": builder,
        "registry": registry,
        "check_ids": [check["id"] for check in metrics["checks"]],
        "ray_ids": expected_ray_ids,
        "required_classes": required_classes,
        "metrics": metrics,
    }
    return record, context


def validate(record: dict[str, Any], context: dict[str, Any]) -> list[str]:
    return validate_candidate_record(
        record,
        context["candidate"],
        project=context["project"],
        expected_builder=context["builder"],
        target_script=PROBE,
        registry=context["registry"],
        expected_check_ids=context["check_ids"],
        expected_ray_ids=context["ray_ids"],
        required_classes=context["required_classes"],
        recomputed_metrics=context["metrics"],
    )


def candidate_cases(root: pathlib.Path, suite: Suite) -> None:
    with tempfile.TemporaryDirectory(prefix="v127r1-candidate-") as temp_text:
        record, context = candidate_fixture(root, pathlib.Path(temp_text))
        errors = validate(record, context)
        suite.check("fully executed probe PASS evidence accepted", errors == [], str(errors))
        complete = copy.deepcopy(record)
        complete.update({"validation_errors": [], "evidence_complete": True, "execution_status": "EXECUTED_COMPLETE"})
        suite.check("strict executed-complete record recognized", executed_complete(complete))

        fail_record = copy.deepcopy(record)
        fail_record["ray_result"] = {**fail_record["ray_result"], "status": "FAIL", "mismatch_count": 1, "mismatches": [{"record_id": "STATIC"}]}
        probe_path = context["candidate"] / "probe_result.json"
        probe = json.loads(probe_path.read_text(encoding="utf-8"))
        probe["status"] = "FAIL"
        probe["ray_result"] = fail_record["ray_result"]
        dump(probe_path, probe)
        fail_record["returncode"] = 1
        fail_record["probe_result_sha256"] = sha256(probe_path)
        suite.check("fully executed probe FAIL evidence accepted", validate(fail_record, context) == [])
        dump(probe_path, {**probe, "status": "PASS", "ray_result": record["ray_result"]})

        def rejected(name: str, mutate: Callable[[dict[str, Any]], None], token: str | None = None) -> None:
            value = copy.deepcopy(record)
            mutate(value)
            observed = validate(value, context)
            suite.check(name, bool(observed) and (token is None or any(token in error for error in observed)), str(observed))

        rejected("null image hash rejected", lambda value: value["images"]["a1_on"].update({"sha256": None}), "image identity")
        rejected("wrong image dimensions metadata rejected", lambda value: value["images"]["a1_on"].update({"png": {"width": 1, "height": 1, "bit_depth": 8, "color_type": 2}}), "PNG metadata")
        rejected("invalid stdout digest rejected", lambda value: value.update({"stdout_sha256": "x"}), "SHA-256")
        rejected("wrong engine identity rejected", lambda value: value.update({"engine_identity": "wrong"}), "engine identity")
        rejected("material source hash mismatch rejected", lambda value: value.update({"project_material_source_sha256": "0" * 64}), "material-source")
        rejected("process/result return-code mismatch rejected", lambda value: value.update({"returncode": 1}), "process/result")
        rejected("missing import class rejected", lambda value: value["import_preflight"]["class_cache"]["classes"].pop("P1AWorldGate"), "registered classes")
        rejected("import project-root mismatch rejected", lambda value: value["import_preflight"].update({"project_root": "/wrong"}), "project-root")

        metrics_20 = copy.deepcopy(context["metrics"])
        metrics_20["checks"] = metrics_20["checks"][:-1]
        rejected("20-check metric inventory rejected", lambda value: value.update({"metrics": metrics_20}), "check inventory")
        duplicate_metrics = copy.deepcopy(context["metrics"])
        duplicate_metrics["checks"][-1]["id"] = duplicate_metrics["checks"][0]["id"]
        rejected("duplicate metric ID rejected", lambda value: value.update({"metrics": duplicate_metrics}), "check inventory")
        rejected("13-ray summary rejected", lambda value: value["ray_result"].update({"sample_count": 13}), "sample inventory")
        rejected("incoherent ray mismatch count rejected", lambda value: value["ray_result"].update({"mismatch_count": 1}), "incoherent")

        engine_path = context["candidate"] / "engine.txt"
        original_engine = engine_path.read_text(encoding="utf-8")
        write(engine_path, "SCRIPT ERROR: synthetic parse failure\n")
        dirty = copy.deepcopy(record)
        dirty["engine_log_sha256"] = sha256(engine_path)
        suite.check("parse-error runtime log rejected", any("parse/load" in error for error in validate(dirty, context)))
        write(engine_path, original_engine)

        image_path = context["candidate"] / record["images"]["a1_on"]["path"]
        original_image = image_path.read_bytes()
        image_path.write_bytes(b"\x89PNG\r\n\x1a\nmalformed")
        malformed = copy.deepcopy(record)
        malformed["images"]["a1_on"]["sha256"] = sha256(image_path)
        malformed["images"]["a1_on"]["png"] = None
        suite.check("malformed PNG rejected", any("supported 1280x720" in error for error in validate(malformed, context)))
        image_path.write_bytes(original_image)

        probe_path = context["candidate"] / "probe_result.json"
        original_probe = probe_path.read_bytes()
        probe_path.unlink()
        suite.check("absent probe result rejected", bool(validate(record, context)))
        probe_path.write_bytes(original_probe)

        hollow = {
            "schema": "district_zero.p1a.v1_2_7r1.candidate_record.v1",
            "stage": "OUTER_ALBEDO",
            "execution_status": "EXECUTED_COMPLETE",
            "evidence_complete": True,
            "validation_errors": [],
        }
        suite.check("hollow candidate cannot claim executed completeness", not executed_complete(hollow))
        suite.check("hollow candidate cannot enter independent selection", not local_pass(hollow, "OUTER_CLOSURE_MASK", context["registry"]))
        suite.check("hollow candidate cannot enter combined selection", select_combined([hollow], context["registry"]) is None)
        suite.check("hollow candidate cannot anchor fallback", complete_stage_records([hollow], "OUTER_ALBEDO") == [])
        suite.check("incomplete domain maps to harness blocker", exhausted_domain_status([hollow]) == "BLOCKED/NOT TESTABLE — HARNESS")
        suite.check("complete ineligible domain alone may map to no interval", exhausted_domain_status([complete]) == "NO_PRESENTATION_ONLY_INTERVAL")


def package_cases(suite: Suite) -> None:
    with tempfile.TemporaryDirectory(prefix="v127r1-packages-") as temp_text:
        temp = pathlib.Path(temp_text)
        reports: dict[str, Any] = {}
        for name, status, inventory in (
            ("early-blocker", "BLOCKED/NOT TESTABLE — HARNESS", "SHA256SUMS.txt"),
            ("no-interval", "NO_PRESENTATION_ONLY_INTERVAL", "SHA256SUMS.txt"),
            ("success-source", "PASS", "PACKET_SHA256SUMS.txt"),
            ("success-evidence", "PASS", "SHA256SUMS.txt"),
            ("success-session", "PASS", "SESSION_SHA256SUMS.txt"),
        ):
            tree = temp / name
            dump(tree / "TERMINAL_RESULT.json", {"status": status})
            if name == "success-session":
                dump(tree / "PREPARED_RESULT.json", {"status": "READY", "attempts": 0})
            write_inventory(tree, inventory)
            report = package_tree(tree, temp / f"{name}.zip", inventory_name=inventory, scratch_parent=temp / "fresh")
            reports[name] = report
            suite.check(f"{name} package fresh-extraction verified", report["integrity"] == "PASS" and report["fresh_extraction"]["status"] == "PASS")
            if name == "success-session":
                inventory_text = (tree / inventory).read_text(encoding="utf-8")
                suite.check("prepared result precedes and is covered by final inventory", "  PREPARED_RESULT.json\n" in inventory_text)
        suite.check("all synthetic terminal package identities recorded", all(reports[name]["sha256"] and reports[name]["byte_size"] > 0 for name in reports))

        changed = temp / "changed-after-inventory"
        write(changed / "a.txt", "a\n")
        write_inventory(changed, "SHA256SUMS.txt")
        write(changed / "b.txt", "b\n")
        suite.check("post-inventory added file detected", bool(verify_inventory(changed, "SHA256SUMS.txt")))
        suite.raises(
            "post-inventory source cannot be packaged",
            lambda: package_tree(changed, temp / "changed.zip", inventory_name="SHA256SUMS.txt", scratch_parent=temp / "fresh"),
        )
        suite.check("duplicate ZIP entries rejected", "duplicate ZIP entries" in _safe_members(["root/a", "root/a"], "root"))
        suite.check("path traversal ZIP member rejected", any("unsafe ZIP member" in error for error in _safe_members(["root/../escape"], "root")))


def import_lifecycle_cases(root: pathlib.Path, suite: Suite) -> None:
    with tempfile.TemporaryDirectory(prefix="v127r1-import-") as temp_text:
        temp = pathlib.Path(temp_text)
        cache = temp / "global_script_class_cache.cfg"
        required = dict(json.loads((root / "tests/fixtures/disposable_import_preflight.json").read_text(encoding="utf-8"))["required_registered_classes"])

        def cache_text(records: list[tuple[str, str]]) -> str:
            blocks = [f'{{\n"class": &"{name}",\n"path": "{path}"\n}}' for name, path in records]
            return "list=Array[Dictionary]([" + ", ".join(blocks) + "])\n"

        write(cache, cache_text(list(required.items())))
        summary, missing = cache_resolution(cache, required)
        suite.check("all ten class-cache entries resolve exact same-entry class/path pairs", missing == [] and len(summary["classes"]) == 10 and all(item["resolved"] for item in summary["classes"].values()))
        swapped = list(required.items())
        first_name, first_path = swapped[0]
        second_name, second_path = swapped[1]
        swapped[0] = (first_name, second_path)
        swapped[1] = (second_name, first_path)
        write(cache, cache_text(swapped))
        _summary, swapped_missing = cache_resolution(cache, required)
        suite.check("swapped class-cache paths are rejected", set(swapped_missing) == {first_name, second_name})
        duplicated = list(required.items()) + [next(iter(required.items()))]
        write(cache, cache_text(duplicated))
        _summary, duplicate_missing = cache_resolution(cache, required)
        suite.check("duplicate class-cache entries are rejected", next(iter(required)) in duplicate_missing)

        source = temp / "copy-source"
        write(source / "scripts/p1a_world_builder.gd", "class_name P1AWorldBuilder\n")
        write(source / "tests/fixtures/v1_2_7_v1_2_6_world_builder.gd", "class_name P1AWorldBuilder\n")
        write(source / "project.godot", "[application]\n")
        copy_functions = {
            "candidate": copy_project,
            "prepared": copy_prepared_project,
            "c1": copy_c1_runtime,
        }
        for name, function in copy_functions.items():
            destination = temp / f"copy-{name}"
            function(source, destination)
            suite.check(
                f"{name} runnable copy excludes duplicate class fixture",
                (destination / "scripts/p1a_world_builder.gd").is_file()
                and not (destination / "tests/fixtures/v1_2_7_v1_2_6_world_builder.gd").exists(),
            )

    import argparse as _argparse
    with tempfile.TemporaryDirectory(prefix="v127r1-safe-base-") as safe_base_text:
        unsafe = root / ".v127r1-semantic-unsafe-work"
        unsafe_evidence = root / ".v127r1-semantic-unsafe-evidence"
        arguments = _argparse.Namespace(
            root=str(root),
            base_root=safe_base_text,
            godot="/opt/homebrew/bin/godot",
            work_root=str(unsafe),
            evidence_root=str(unsafe_evidence),
            prepared_session_root=str(root / ".v127r1-semantic-unsafe-session"),
            preflight_only=True,
            require_preflight_result=None,
        )
        director = Director(arguments)
        try:
            director.initialize_outputs()
        except StopRun:
            rejected = True
        else:
            rejected = False
        suite.check(
            "unsafe output containment is rejected before mutation or finalization",
            rejected and not director.outputs_initialized and not unsafe.exists() and not unsafe_evidence.exists(),
        )


def static_source_cases(root: pathlib.Path, suite: Suite) -> None:
    runner = (root / "tools/run_v1_2_7r1_calibration.py").read_text(encoding="utf-8")
    prepare = (root / "tools/prepare_v1_2_7r1_a1_session.py").read_text(encoding="utf-8")
    launcher = (root / "tools/launch_a1_capture_v1_2_7r1.py").read_text(encoding="utf-8")
    suite.check("candidate import occurs before render launch", runner.index("import_and_parse_project(", runner.index("def evaluate")) < runner.index("process = run(command, project)", runner.index("def evaluate")))
    suite.check("candidate import failure is a harness blocker", 'raise StopRun("BLOCKED/NOT TESTABLE — HARNESS", f"candidate import/parse failed' in runner)
    suite.check("common terminal finalizer covers registered stops", "director.finalize_evidence(" in runner and "except StopRun" in runner and "except Exception" in runner)
    suite.check("prepared result written before final inventory", prepare.index('dump(session / "PREPARED_RESULT.json"') < prepare.index('write_inventory(session, "SESSION_SHA256SUMS.txt")'))
    suite.check("prepared readiness follows exact import", prepare.index("import_and_parse_project(") < prepare.index('"status": "READY FOR A1 HUMAN FEASIBILITY CAPTURE"'))
    suite.check("fresh-session import precedes single-use marker", launcher.index("import_and_parse_project(") < launcher.index('dump(session / "LAUNCH_USED.json"'))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=str(ROOT_DEFAULT))
    parser.add_argument("--static-only", action="store_true")
    args = parser.parse_args()
    root = pathlib.Path(args.root).resolve()
    suite = Suite()
    material_cases(root, suite)
    candidate_cases(root, suite)
    package_cases(suite)
    import_lifecycle_cases(root, suite)
    static_source_cases(root, suite)
    failures = [case for case in suite.cases if case["status"] != "PASS"]
    result = {
        "schema": "district_zero.p1a.v1_2_7r1.repair_semantic_test_result.v1",
        "status": "PASS" if not failures else "FAIL",
        "case_count": len(suite.cases),
        "pass_count": len(suite.cases) - len(failures),
        "failure_count": len(failures),
        "failures": failures,
        "cases": suite.cases,
        "godot_processes_launched": 0,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
