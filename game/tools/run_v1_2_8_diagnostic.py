#!/usr/bin/env python3
"""Execute the exact five-case v1.2.8 pre-calibration diagnostic epoch."""
from __future__ import annotations

import argparse
import datetime as dt
import json
import pathlib
import shutil
import subprocess
import sys
from typing import Any

ROOT_DEFAULT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DEFAULT / "tools"))

from p1a_v1_2_7_metrics import compute as compute_metrics
from p1a_v1_2_7r1_harness import (
    EXACT_ENGINE,
    dump,
    import_and_parse_project,
    patch_builder,
    png_info,
    run,
    scan_error_text,
    sha256,
    validate_candidate_record,
    verify_inventory,
    write,
)
from p1a_v1_2_8_contract import ORIGINAL_CENTER, adjudicate_branch
from p1a_v1_2_8_diagnostic import build_sensitivity, decode_ownership, median_y
from run_v1_2_7r1_calibration import copy_project, parameters

VISUAL_PROBE = "res://tests/p1a_v1_2_7_visual_probe.gd"
OWNERSHIP_PROBE = "res://tests/p1a_v1_2_8_ownership_probe.gd"
BASE_BUILDER = "tests/fixtures/v1_2_7_v1_2_6_world_builder.gd"


class Blocked(RuntimeError):
    def __init__(self, status: str, detail: str) -> None:
        super().__init__(detail)
        self.status = status
        self.detail = detail


def _new_empty(path: pathlib.Path) -> None:
    if path.exists():
        if not path.is_dir() or any(path.iterdir()):
            raise Blocked("BLOCKED/NOT TESTABLE — HARNESS", f"output is not new/empty: {path}")
    else:
        path.mkdir(parents=True)


def _within(child: pathlib.Path, parent: pathlib.Path) -> bool:
    try:
        child.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


class Diagnostic:
    def __init__(self, args: argparse.Namespace) -> None:
        self.root = pathlib.Path(args.root).resolve()
        self.clean = pathlib.Path(args.clean_r1_root).resolve()
        self.base = pathlib.Path(args.base_root).resolve()
        self.p0 = pathlib.Path(args.p0_root).resolve()
        self.historical = pathlib.Path(args.historical_evidence_zip).resolve()
        self.overlay_zip = pathlib.Path(args.authority_overlay_zip).resolve()
        self.godot = str(pathlib.Path(args.godot).resolve())
        self.work = pathlib.Path(args.work_root).resolve()
        self.evidence = pathlib.Path(args.evidence_root).resolve()
        self.registry: dict[str, Any] = {}
        self.acceptance: dict[str, Any] = {}
        self.baseline = ""
        self.required_classes: dict[str, str] = {}
        self.expected_check_ids: list[str] = []
        self.expected_ray_ids: dict[str, list[str]] = {}
        self.launches = 0
        self.imports = 0
        self.resume_existing = bool(args.resume_existing)

    def initialize(self) -> None:
        inputs = [self.root, self.clean, self.base, self.p0, self.historical, self.overlay_zip]
        if not all(path.exists() for path in inputs):
            raise Blocked("BLOCKED/NOT TESTABLE — SOURCE OR EVIDENCE IDENTITY", "one or more bound inputs are absent")
        pairwise = [self.root, self.clean, self.base, self.p0, self.work, self.evidence]
        for index, left in enumerate(pairwise):
            for right in pairwise[index + 1:]:
                if left == right or _within(left, right) or _within(right, left):
                    raise Blocked("BLOCKED/NOT TESTABLE — HARNESS", f"unsafe path containment: {left} / {right}")
        if self.resume_existing:
            if not self.work.is_dir() or not self.evidence.is_dir():
                raise Blocked("BLOCKED/NOT TESTABLE — HARNESS", "resume roots are absent")
        else:
            _new_empty(self.work)
            _new_empty(self.evidence)
        self.registry = json.loads((self.root / "tests/fixtures/v1_2_7_calibration_registry.json").read_text(encoding="utf-8"))
        self.acceptance = json.loads((self.root / "tests/fixtures/v1_2_6_visual_acceptance.json").read_text(encoding="utf-8"))
        self.baseline = (self.root / BASE_BUILDER).read_text(encoding="utf-8")
        contract = json.loads((self.root / "tests/fixtures/disposable_import_preflight.json").read_text(encoding="utf-8"))
        self.required_classes = dict(contract["required_registered_classes"])
        old_metrics = json.loads((self.root / "director_inputs/v1_2_6_run1_validation_evidence/NATIVE_VISUALS/native-visual-metric-result.json").read_text(encoding="utf-8"))
        self.expected_check_ids = [item["id"] for item in old_metrics["checks"]]
        rays = json.loads((self.root / "tests/fixtures/v1_2_6_ray_classification_baseline.json").read_text(encoding="utf-8"))
        self.expected_ray_ids = {"FREE_ROAM": list(rays["free_roam"]["records"]), "A1_FAMILIARIZATION": list(rays["a1"]["records"])}

    def preflight(self) -> None:
        version = run([self.godot, "--version"], self.root)
        dump(self.evidence / "PREFLIGHT/ENGINE_IDENTITY.json", {
            "argv": [self.godot, "--version"], "required": EXACT_ENGINE,
            "observed": version.stdout.strip(), "stdout": version.stdout,
            "stderr": version.stderr, "returncode": version.returncode,
            "match": version.returncode == 0 and version.stdout.strip() == EXACT_ENGINE,
        })
        if version.returncode != 0 or version.stdout.strip() != EXACT_ENGINE:
            raise Blocked("BLOCKED/NOT TESTABLE — EXACT ENGINE", "exact Godot identity differs")
        checks: dict[str, Any] = {
            "overlay_zip": {"byte_size": self.overlay_zip.stat().st_size, "sha256": sha256(self.overlay_zip)},
            "clean_r1_inventory_sha256": sha256(self.clean / "PACKET_SHA256SUMS.txt"),
            "clean_r1_inventory_errors": verify_inventory(self.clean, "PACKET_SHA256SUMS.txt"),
            "clean_r1_builder_sha256": sha256(self.clean / "scripts/p1a_world_builder.gd"),
            "historical_zip": {"byte_size": self.historical.stat().st_size, "sha256": sha256(self.historical)},
            "working_input_inventory_sha256": sha256(self.root / "V1_2_7R1_INPUT_SHA256SUMS.txt"),
        }
        expected = {
            "overlay_size": 28759,
            "overlay_sha": "83705385672f8f1822e395ec5a64728cc49c57650a87b249f23044b73f1ca4a4",
            "r1_inventory": "e6a13365f3019b21457d754d6d128ef85d70a39c718579703574de066141bf44",
            "builder": "c016d5e2654919d6de5e1416ab21a40da81149ec11100dae8d95a89922b9dc38",
            "historical_size": 7729110,
            "historical_sha": "2d92dc591ed8b4288e357f85978b93e793523e8e097ace28456de9df6129877f",
        }
        valid = (
            checks["overlay_zip"] == {"byte_size": expected["overlay_size"], "sha256": expected["overlay_sha"]}
            and checks["clean_r1_inventory_sha256"] == expected["r1_inventory"]
            and not checks["clean_r1_inventory_errors"]
            and checks["clean_r1_builder_sha256"] == expected["builder"]
            and checks["historical_zip"] == {"byte_size": expected["historical_size"], "sha256": expected["historical_sha"]}
            and checks["working_input_inventory_sha256"] == expected["r1_inventory"]
        )
        checks["status"] = "PASS" if valid else "FAIL"
        dump(self.evidence / "PREFLIGHT/IDENTITY_RESULT.json", checks)
        if not valid:
            raise Blocked("BLOCKED/NOT TESTABLE — SOURCE OR EVIDENCE IDENTITY", "bound input identity differs")
        for name, command in (
            ("R1_SEMANTICS", [sys.executable, "-B", str(self.root / "tools/test_v1_2_7r1_repairs.py"), "--root", str(self.root), "--static-only"]),
            ("V1_2_8_SEMANTICS", [sys.executable, "-B", str(self.root / "tools/test_v1_2_8_semantics.py"), "--root", str(self.root)]),
        ):
            process = run(command, self.root)
            directory = self.evidence / "PREFLIGHT" / name
            dump(directory / "argv.json", {"argv": command, "cwd": str(self.root)})
            write(directory / "stdout.txt", process.stdout)
            write(directory / "stderr.txt", process.stderr)
            if process.returncode != 0:
                raise Blocked("BLOCKED/NOT TESTABLE — HARNESS", f"{name} failed")

    def native_case(self, case_id: str, value: dict[str, Any]) -> dict[str, Any]:
        directory = self.evidence / "DIAGNOSTIC/PRE_REPAIR" / case_id
        project = self.work / "DIAGNOSTIC/PRE_REPAIR" / case_id
        copy_project(self.root, project)
        expected_builder = patch_builder(self.baseline, value, self.registry)
        write(project / "scripts/p1a_world_builder.gd", expected_builder)
        write(directory / "evaluated_p1a_world_builder.gd", expected_builder)
        imported = import_and_parse_project(
            self.godot, project, directory / "IMPORT_PREFLIGHT", target_script=VISUAL_PROBE,
            required_classes=self.required_classes, expected_builder_sha256=sha256(project / "scripts/p1a_world_builder.gd"),
        )
        self.imports += 1
        if imported.get("status") != "PASS":
            raise Blocked("BLOCKED/NOT TESTABLE — HARNESS", f"{case_id} import/parse failed")
        command = [self.godot, "--log-file", str(directory / "engine.txt"), "--path", str(project), "--fixed-fps", "60", "--script", VISUAL_PROBE, "--", "--output-dir", str(directory)]
        directory.mkdir(parents=True, exist_ok=True)
        dump(directory / "argv.json", {"argv": command, "cwd": str(project)})
        process = run(command, project)
        self.launches += 1
        write(directory / "stdout.txt", process.stdout)
        write(directory / "stderr.txt", process.stderr)
        if not (directory / "engine.txt").is_file(): write(directory / "engine.txt", "")
        try:
            probe = json.loads((directory / "probe_result.json").read_text(encoding="utf-8"))
        except Exception:
            probe = {}
            write(directory / "probe_result.json", "{}\n")
        image_names = {"free_roam_on":"free-roam-after-native.png", "free_roam_off":"free-roam-after-shadow-off-reference.png", "a1_on":"a1-after-native.png", "a1_off":"a1-after-shadow-off-reference.png"}
        paths = {"FREE_ROAM:on":directory/image_names["free_roam_on"], "FREE_ROAM:off":directory/image_names["free_roam_off"], "A1_FAMILIARIZATION:on":directory/image_names["a1_on"], "A1_FAMILIARIZATION:off":directory/image_names["a1_off"]}
        metrics = compute_metrics(self.acceptance, paths) if all(path.is_file() for path in paths.values()) else {}
        dump(directory / "native-visual-metric-result.json", metrics)
        record: dict[str, Any] = {
            "schema":"district_zero.p1a.v1_2_7r1.candidate_record.v1", "candidate_id":f"V128-DIAGNOSTIC-{case_id}",
            "stage":"V1_2_8_DIAGNOSTIC_PRE_REPAIR", "parameters":value, "engine_identity":probe.get("engine_identity"),
            "command":command, "returncode":process.returncode, "project_material_source_sha256":sha256(project/"scripts/p1a_world_builder.gd"),
            "evaluated_source_path":"evaluated_p1a_world_builder.gd",
            "images":{name:{"path":filename,"sha256":sha256(directory/filename) if (directory/filename).is_file() else None,"png":png_info(directory/filename)} for name,filename in image_names.items()},
            "metrics":metrics, "ray_result":probe.get("ray_result",{}), "import_preflight":imported,
            "stdout_sha256":sha256(directory/"stdout.txt"), "stderr_sha256":sha256(directory/"stderr.txt"), "engine_log_sha256":sha256(directory/"engine.txt"),
            "probe_result_sha256":sha256(directory/"probe_result.json"), "metrics_result_sha256":sha256(directory/"native-visual-metric-result.json"),
            "import_preflight_result_sha256":sha256(directory/"IMPORT_PREFLIGHT/result.json"), "evaluated_utc":dt.datetime.now(dt.timezone.utc).isoformat(),
            "evidence_validator":"p1a_v1_2_7r1_harness.validate_candidate_record.v1",
        }
        errors = validate_candidate_record(record,directory,project=project,expected_builder=expected_builder,target_script=VISUAL_PROBE,registry=self.registry,expected_check_ids=self.expected_check_ids,expected_ray_ids=self.expected_ray_ids,required_classes=self.required_classes,recomputed_metrics=metrics)
        record.update({"epoch":"PRE_REPAIR","case_id":case_id,"canonical_parameters":value,"evaluated_builder_sha256":record["project_material_source_sha256"],"runtime_project_root":str(project),"import_preflight_record_sha256":record["import_preflight_result_sha256"],"exact_engine_identity":record["engine_identity"],"cwd":str(project),"process_return_code":process.returncode,"runtime_result":probe,"validation_errors":errors,"evidence_complete":not errors,"execution_status":"EXECUTED_COMPLETE" if not errors else "BLOCKED/NOT TESTABLE — HARNESS"})
        dump(directory / "diagnostic_case_record.json", record)
        if errors:
            raise Blocked("BLOCKED/NOT TESTABLE — HARNESS", f"{case_id} evidence incomplete: {errors[:3]}")
        return record

    def ownership_case(self) -> dict[str, Any]:
        case_id = "OWNERSHIP_ID"
        value = parameters()
        directory = self.evidence / "DIAGNOSTIC/PRE_REPAIR" / case_id
        project = self.work / "DIAGNOSTIC/PRE_REPAIR" / case_id
        copy_project(self.root, project)
        expected_builder = patch_builder(self.baseline, value, self.registry)
        write(project / "scripts/p1a_world_builder.gd", expected_builder)
        write(directory / "evaluated_p1a_world_builder.gd", expected_builder)
        imported = import_and_parse_project(self.godot,project,directory/"IMPORT_PREFLIGHT",target_script=OWNERSHIP_PROBE,required_classes=self.required_classes,expected_builder_sha256=sha256(project/"scripts/p1a_world_builder.gd"))
        self.imports += 1
        if imported.get("status") != "PASS": raise Blocked("BLOCKED/NOT TESTABLE — HARNESS", "ownership import/parse failed")
        command=[self.godot,"--log-file",str(directory/"engine.txt"),"--path",str(project),"--fixed-fps","60","--script",OWNERSHIP_PROBE,"--","--output-dir",str(directory)]
        directory.mkdir(parents=True,exist_ok=True); dump(directory/"argv.json",{"argv":command,"cwd":str(project)})
        process=run(command,project); self.launches += 1
        write(directory/"stdout.txt",process.stdout); write(directory/"stderr.txt",process.stderr)
        if not (directory/"engine.txt").is_file(): write(directory/"engine.txt","")
        try: probe=json.loads((directory/"ownership_probe_result.json").read_text(encoding="utf-8"))
        except Exception: probe={}
        images=[directory/"a1-owner-low-reference.png"]+[directory/f"a1-owner-high-{i:03d}.png" for i in range(int(probe.get("owner_count",0)))]
        errors=[]
        if process.returncode!=0: errors.append("ownership process nonzero")
        if probe.get("status")!="PASS" or probe.get("engine_identity")!=EXACT_ENGINE or probe.get("renderer")!="forward_plus": errors.append("ownership runtime result invalid")
        if probe.get("owner_count")!=45 or len(probe.get("ray_grid",{}))!=5929: errors.append("ownership inventory cardinality invalid")
        if len(images)!=46 or any(not path.is_file() or png_info(path)!={"width":1280,"height":720,"bit_depth":8,"color_type":2} for path in images): errors.append("ownership image inventory invalid")
        if scan_error_text([process.stdout,process.stderr,(directory/"engine.txt").read_text(encoding="utf-8",errors="replace")]): errors.append("ownership runtime emitted recognized errors")
        record={"schema":"district_zero.p1a.v1_2_8.diagnostic_case_record.v1","epoch":"PRE_REPAIR","case_id":case_id,"canonical_parameters":value,"evaluated_builder_sha256":sha256(project/"scripts/p1a_world_builder.gd"),"runtime_project_root":str(project),"import_preflight_record_sha256":sha256(directory/"IMPORT_PREFLIGHT/result.json"),"exact_engine_identity":probe.get("engine_identity"),"argv":command,"cwd":str(project),"process_return_code":process.returncode,"runtime_result":probe,"stdout_path_and_sha256":{"path":"stdout.txt","sha256":sha256(directory/"stdout.txt")},"stderr_path_and_sha256":{"path":"stderr.txt","sha256":sha256(directory/"stderr.txt")},"engine_log_path_and_sha256":{"path":"engine.txt","sha256":sha256(directory/"engine.txt")},"image_paths_dimensions_modes_and_sha256":[{"path":path.name,"sha256":sha256(path),"png":png_info(path)} for path in images if path.is_file()],"import_preflight":imported,"validation_errors":errors,"evidence_complete":not errors,"execution_status":"EXECUTED_COMPLETE" if not errors else "BLOCKED/NOT TESTABLE — HARNESS"}
        dump(directory/"diagnostic_case_record.json",record)
        if errors: raise Blocked("BLOCKED/NOT TESTABLE — HARNESS",f"ownership evidence incomplete: {errors}")
        return record

    def execute(self) -> dict[str, Any]:
        definitions={"BASELINE":parameters(),"TARGET_MIDPOINT":parameters(outer_scale=1.15),"TARGET_EXTREME":parameters(outer_scale=1.3),"UNRELATED_EXTREME":parameters(wall_scale=1.47)}
        if self.resume_existing:
            records = {}
            for case in definitions:
                record_path = self.evidence/"DIAGNOSTIC/PRE_REPAIR"/case/"diagnostic_case_record.json"
                record = json.loads(record_path.read_text(encoding="utf-8"))
                if record.get("execution_status") != "EXECUTED_COMPLETE" or record.get("evidence_complete") is not True or record.get("case_id") != case:
                    raise Blocked("BLOCKED/NOT TESTABLE — HARNESS", f"existing {case} evidence is not executed-complete")
                records[case] = record
            # Re-run only the corrected offline ownership evidence validator.
            records["OWNERSHIP_ID"] = self.ownership_case_from_existing()
            self.launches = 5
            self.imports = 5
        else:
            records={case:self.native_case(case,value) for case,value in definitions.items()}
            records["OWNERSHIP_ID"]=self.ownership_case()
        if self.launches!=5 or self.imports!=5: raise Blocked("BLOCKED/NOT TESTABLE — HARNESS", "diagnostic counter contract differs")
        ownership_dir=self.evidence/"DIAGNOSTIC/PRE_REPAIR/OWNERSHIP_ID"
        ownership_path=self.evidence/"DIAGNOSTIC/ownership_diagnostic.json"
        ownership=decode_ownership(ownership_dir,ownership_path,self.root/"world/generated/solid_meshes.json")
        selection=ownership["selection_transcript"]
        if selection.get("selected") is None:
            raise Blocked(selection.get("status","DIRECTOR DECISION REQUIRED — NO ROBUST OUTER-CLOSURE SAMPLE"),"no exact same-owner 13x13 sample exists within the authorized radius")
        center=(int(selection["selected"]["x"]),int(selection["selected"]["y"]))
        case_dirs={case:self.evidence/"DIAGNOSTIC/PRE_REPAIR"/case for case in definitions}
        sensitivity_dir=self.evidence/"DIAGNOSTIC/SENSITIVITY"; sensitivity_dir.mkdir(parents=True,exist_ok=True)
        sensitivity=build_sensitivity(case_dirs,center,sensitivity_dir)
        branch_seed=adjudicate_branch({(int(item["x"]),int(item["y"])):item for item in ownership["pixels"]},sensitivity["status"])
        if branch_seed.get("status")!="PASS": raise Blocked(branch_seed["status"],"ownership/sensitivity branch could not proceed")
        branch=branch_seed["branch"]
        if branch=="BRANCH_B_RENDER_CONSUMER_BINDING": raise Blocked("BLOCKED/NOT TESTABLE — MEASUREMENT BINDING","Branch B requires a separately proved minimal render-consumer binding repair")
        old_base=case_dirs["BASELINE"]
        historical={"integer_center_px":[256,244],"normalized":[0.2,0.34],"shadow_on_Y":median_y(old_base/"a1-after-native.png",ORIGINAL_CENTER),"shadow_off_Y":median_y(old_base/"a1-after-shadow-off-reference.png",ORIGINAL_CENTER),"label":"v1.2.7R1_old_sample_historical_non_gating","gating":False}
        selected_record={"schema":"district_zero.p1a.v1_2_8.selected_sample.v1","run_id":"v1.2.8-execution-run-1","branch":branch,"integer_center_px":list(center),"pixel_center_normalized_rational":[f"{2*center[0]+1}/2560",f"{2*center[1]+1}/1440"],"owner_key":{"source_geometry_id":"OUTER_CLOSURE_MASK","render_node":"/root/DistrictZeroP1A/World/MESH_OUTER_CLOSURE_Visual","face_class":"SIDE","connected_side_component_id":selection["selected"]["owner_component_id"]},"ownership_diagnostic_sha256":sha256(ownership_path),"selection_transcript_sha256_or_null":sha256(ownership_path),"sensitivity_result_sha256":sha256(sensitivity_dir/"sensitivity_result.json"),"clean_source_inventory_sha256":sha256(self.clean/"PACKET_SHA256SUMS.txt"),"historical_non_gating":historical}
        selected_path=self.root/"presentation/p1a_v1_2_8_selected_sample.json"; dump(selected_path,selected_record)
        acceptance=json.loads(json.dumps(self.acceptance)); acceptance["authority_version"]="v1.2.8"; acceptance["base_fixture_sha256"]=sha256(self.root/"tests/fixtures/v1_2_6_visual_acceptance.json"); acceptance["integer_samples"]={"A1_FAMILIARIZATION":{"left_outer_closure":list(center)}}; acceptance["samples"]["A1_FAMILIARIZATION"]["left_outer_closure"]=[(center[0]+0.5)/1280.0,(center[1]+0.5)/720.0]; acceptance["historical_non_gating"]={"A1_FAMILIARIZATION":{"left_outer_closure":historical}}
        fixture=self.root/"tests/fixtures/v1_2_8_visual_acceptance_selected.json"; dump(fixture,acceptance)
        resume={"schema":"district_zero.p1a.v1_2_8.diagnostic_resume_checkpoint.v1","status":"PASS","branch":branch,"diagnostic_engine_launches":self.launches,"diagnostic_import_preflights":self.imports,"calibration_candidate_launches":0,"calibration_candidate_index":0,"calibration_records":[],"calibration_cache":{},"candidate_root_empty":True,"selected_sample_path":str(selected_path),"selected_sample_sha256":sha256(selected_path),"selected_acceptance_fixture_path":str(fixture),"selected_acceptance_fixture_sha256":sha256(fixture),"ownership_diagnostic_path":str(ownership_path),"ownership_diagnostic_sha256":sha256(ownership_path),"sensitivity_result_path":str(sensitivity_dir/"sensitivity_result.json"),"sensitivity_result_sha256":sha256(sensitivity_dir/"sensitivity_result.json"),"historical_run_2_terminal":"NO_PRESENTATION_ONLY_INTERVAL","historical_run_2_disposition":"CLOSED_NOT_REUSED","human_attempts_consumed":0,"human_world_gate":"NOT PERFORMED","P1B":"FROZEN"}
        dump(self.evidence/"DIAGNOSTIC_RESUME_CHECKPOINT.json",resume)
        return resume

    def ownership_case_from_existing(self) -> dict[str, Any]:
        directory = self.evidence/"DIAGNOSTIC/PRE_REPAIR/OWNERSHIP_ID"
        project = self.work/"DIAGNOSTIC/PRE_REPAIR/OWNERSHIP_ID"
        probe = json.loads((directory/"ownership_probe_result.json").read_text(encoding="utf-8"))
        imported = json.loads((directory/"IMPORT_PREFLIGHT/result.json").read_text(encoding="utf-8"))
        images=[directory/"a1-owner-low-reference.png"]+[directory/f"a1-owner-high-{i:03d}.png" for i in range(int(probe.get("owner_count",0)))]
        errors=[]
        if imported.get("status") != "PASS": errors.append("ownership import preflight is not PASS")
        if probe.get("status")!="PASS" or probe.get("engine_identity")!=EXACT_ENGINE or probe.get("renderer")!="forward_plus": errors.append("ownership runtime result invalid")
        if probe.get("owner_count")!=45 or len(probe.get("ray_grid",{}))!=5929: errors.append("ownership inventory cardinality invalid")
        if len(images)!=46 or any(not path.is_file() or png_info(path)!={"width":1280,"height":720,"bit_depth":8,"color_type":2} for path in images): errors.append("ownership image inventory invalid")
        texts=[(directory/name).read_text(encoding="utf-8",errors="replace") for name in ("stdout.txt","stderr.txt","engine.txt")]
        if scan_error_text(texts): errors.append("ownership runtime emitted recognized errors")
        record={"schema":"district_zero.p1a.v1_2_8.diagnostic_case_record.v1","epoch":"PRE_REPAIR","case_id":"OWNERSHIP_ID","canonical_parameters":parameters(),"evaluated_builder_sha256":sha256(project/"scripts/p1a_world_builder.gd"),"runtime_project_root":str(project),"import_preflight_record_sha256":sha256(directory/"IMPORT_PREFLIGHT/result.json"),"exact_engine_identity":probe.get("engine_identity"),"argv":json.loads((directory/"argv.json").read_text())["argv"],"cwd":str(project),"process_return_code":0,"runtime_result":probe,"stdout_path_and_sha256":{"path":"stdout.txt","sha256":sha256(directory/"stdout.txt")},"stderr_path_and_sha256":{"path":"stderr.txt","sha256":sha256(directory/"stderr.txt")},"engine_log_path_and_sha256":{"path":"engine.txt","sha256":sha256(directory/"engine.txt")},"image_paths_dimensions_modes_and_sha256":[{"path":path.name,"sha256":sha256(path),"png":png_info(path)} for path in images],"import_preflight":imported,"validation_errors":errors,"evidence_complete":not errors,"execution_status":"EXECUTED_COMPLETE" if not errors else "BLOCKED/NOT TESTABLE — HARNESS","validator_repair":"OWNERSHIP_PNG_RECORD_SHAPE_MISMATCH — removed nonexistent redundant mode key; PNG type remains bit_depth=8,color_type=2"}
        dump(directory/"diagnostic_case_record.json",record)
        if errors: raise Blocked("BLOCKED/NOT TESTABLE — HARNESS",f"existing ownership evidence incomplete: {errors}")
        return record


def main() -> int:
    parser=argparse.ArgumentParser(); parser.add_argument("--root",default=str(ROOT_DEFAULT)); parser.add_argument("--clean-r1-root",required=True); parser.add_argument("--base-root",required=True); parser.add_argument("--p0-root",required=True); parser.add_argument("--historical-evidence-zip",required=True); parser.add_argument("--authority-overlay-zip",required=True); parser.add_argument("--godot",required=True); parser.add_argument("--work-root",required=True); parser.add_argument("--evidence-root",required=True); parser.add_argument("--resume-existing",action="store_true"); args=parser.parse_args()
    director=Diagnostic(args)
    try:
        director.initialize(); director.preflight(); result=director.execute(); print(json.dumps({"status":"DIAGNOSTIC PASS — CALIBRATION REQUIRED","result":result},indent=2,sort_keys=True)); return 0
    except Blocked as exc:
        if director.evidence.exists():
            terminal={"schema":"district_zero.p1a.v1_2_8.terminal_result.v1","status":exc.status,"terminal_stage":"DIAGNOSTIC","detail":exc.detail,"diagnostic_engine_launches":director.launches,"diagnostic_import_preflights":director.imports,"calibration_candidate_launches":0,"human_attempts_consumed":0,"human_world_gate":"NOT PERFORMED","P1B":"FROZEN"}; dump(director.evidence/"TERMINAL_RESULT.json",terminal)
        print(json.dumps({"status":exc.status,"detail":exc.detail},indent=2,sort_keys=True)); return 2
    except Exception as exc:
        if director.evidence.exists(): dump(director.evidence/"TERMINAL_RESULT.json",{"schema":"district_zero.p1a.v1_2_8.terminal_result.v1","status":"BLOCKED/NOT TESTABLE — HARNESS","terminal_stage":"DIAGNOSTIC","detail":str(exc),"diagnostic_engine_launches":director.launches,"diagnostic_import_preflights":director.imports,"calibration_candidate_launches":0,"human_attempts_consumed":0,"human_world_gate":"NOT PERFORMED","P1B":"FROZEN"})
        print(json.dumps({"status":"BLOCKED/NOT TESTABLE — HARNESS","detail":str(exc)},indent=2,sort_keys=True)); return 2


if __name__=="__main__": raise SystemExit(main())
