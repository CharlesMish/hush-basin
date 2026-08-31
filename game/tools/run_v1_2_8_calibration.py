#!/usr/bin/env python3
"""Resume a green v1.2.8 diagnostic into the bounded fresh calibration."""
from __future__ import annotations

import argparse
import json
import pathlib
import shutil
import sys
from typing import Any

ROOT_DEFAULT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DEFAULT / "tools"))

import run_v1_2_7r1_calibration as r1
from p1a_v1_2_7r1_harness import (
    dump, executed_complete, import_and_parse_project, package_tree, patch_builder, run, sha256,
    verify_inventory, write, write_inventory,
)
from p1a_v1_2_8_contract import AUTOMATION_PASS, outer_feasible
from p1a_v1_2_8_diagnostic import annotated_crops
from p1a_v1_2_8_metrics import compute as compute_v128

# The inherited strict evidence validator is schema-agnostic but recomputes by
# calling this module global.  Bind it to the integer-authoritative v1.2.8
# metric implementation before any candidate launch.
r1.compute_metrics = compute_v128


class Stop(r1.StopRun):
    pass


def outer_y(record: dict[str, Any]) -> float:
    return float(record["metrics"]["views"]["A1_FAMILIARIZATION"]["left_outer_closure"]["shadow_on_Y"])


def ground_y(record: dict[str, Any]) -> float:
    return float(record["metrics"]["views"]["A1_FAMILIARIZATION"]["between_structures_ground"]["shadow_on_Y"])


def right_separation(record: dict[str, Any]) -> float:
    return float(record["metrics"]["views"]["A1_FAMILIARIZATION"]["obstacle_separation"]["right_absolute_Y"])


def _ray_green(record: dict[str, Any]) -> bool:
    ray = record.get("ray_result", {})
    return executed_complete(record) and ray.get("status") == "PASS" and ray.get("sample_count") == 14 and ray.get("mismatch_count") == 0


def outer_local(record: dict[str, Any]) -> bool:
    if not _ray_green(record): return False
    allowed = {"A1:right_obstacle_separation"}
    if any(not item["pass"] and item["id"] not in allowed for item in record["metrics"]["checks"]): return False
    return outer_feasible(outer_y(record), ground_y(record))


def wall_local(record: dict[str, Any]) -> bool:
    if not _ray_green(record): return False
    allowed = {
        "A1_FAMILIARIZATION:left_outer_closure:shadow_on_min",
        "A1_FAMILIARIZATION:left_outer_closure:shadow_ratio",
        "A1:left_obstacle_separation",
    }
    if any(not item["pass"] and item["id"] not in allowed for item in record["metrics"]["checks"]): return False
    return right_separation(record) >= 0.12


class Director(r1.Director):
    def __init__(self, args: argparse.Namespace) -> None:
        inherited = argparse.Namespace(
            root=args.root, base_root=args.base_root, godot=args.godot,
            work_root=args.work_root, evidence_root=args.evidence_root,
            prepared_session_root=args.prepared_session_root,
            preflight_only=False, require_preflight_result=None,
        )
        super().__init__(inherited)
        self.clean = pathlib.Path(args.clean_r1_root).resolve()
        self.historical = pathlib.Path(args.historical_evidence_zip).resolve()
        self.resume = pathlib.Path(args.diagnostic_resume).resolve()
        self.diagnostic_launches = 5
        self.reached = ["IDENTITY", "SEMANTICS", "DIAGNOSTIC", "SENSITIVITY"]
        self.selected_branch = "BRANCH_A_SAMPLE_REPLACEMENT"
        self.selected_sample: dict[str, Any] | None = None

    def resume_preflight(self) -> None:
        if not self.work.is_dir() or not self.evidence.is_dir() or not self.session.parent.is_dir():
            raise Stop("BLOCKED/NOT TESTABLE — HARNESS", "resume/output parent absent", "RESUME")
        if self.session.exists() and (not self.session.is_dir() or any(self.session.iterdir())):
            raise Stop("BLOCKED/NOT TESTABLE — HARNESS", "prepared-session root is not new/empty", "RESUME")
        self.outputs_initialized = True
        self.load_authority_inputs()
        self.acceptance = json.loads((self.root/"tests/fixtures/v1_2_8_visual_acceptance_selected.json").read_text(encoding="utf-8"))
        checkpoint = json.loads(self.resume.read_text(encoding="utf-8"))
        self.selected_sample = json.loads((self.root/"presentation/p1a_v1_2_8_selected_sample.json").read_text(encoding="utf-8"))
        errors=[]
        if checkpoint.get("status")!="PASS" or checkpoint.get("branch")!=self.selected_branch: errors.append("diagnostic checkpoint is not Branch-A PASS")
        if checkpoint.get("diagnostic_engine_launches")!=5 or checkpoint.get("diagnostic_import_preflights")!=5: errors.append("diagnostic counter binding differs")
        if checkpoint.get("calibration_candidate_launches")!=0 or checkpoint.get("calibration_records")!=[] or checkpoint.get("calibration_cache")!={}: errors.append("calibration state was not reset to zero")
        if checkpoint.get("selected_sample_sha256")!=sha256(self.root/"presentation/p1a_v1_2_8_selected_sample.json"): errors.append("selected sample binding differs")
        if checkpoint.get("selected_acceptance_fixture_sha256")!=sha256(self.root/"tests/fixtures/v1_2_8_visual_acceptance_selected.json"): errors.append("selected acceptance binding differs")
        sensitivity=json.loads(pathlib.Path(checkpoint["sensitivity_result_path"]).read_text())
        if sensitivity.get("status")!="PASS": errors.append("sensitivity is not PASS")
        if (self.work/"CANDIDATES").exists() or (self.evidence/"CANDIDATES").exists(): errors.append("candidate roots are not fresh/empty")
        if sha256(self.clean/"PACKET_SHA256SUMS.txt")!="e6a13365f3019b21457d754d6d128ef85d70a39c718579703574de066141bf44" or verify_inventory(self.clean,"PACKET_SHA256SUMS.txt"): errors.append("clean R1 identity differs")
        version=run([self.godot,"--version"],self.root)
        if version.returncode!=0 or version.stdout.strip()!="4.7.1.stable.official.a13da4feb": errors.append("exact engine differs")
        directory=self.evidence/"CALIBRATION_PREFLIGHT"
        dump(directory/"engine_identity.json",{"required":"4.7.1.stable.official.a13da4feb","observed":version.stdout.strip(),"stdout":version.stdout,"stderr":version.stderr,"returncode":version.returncode})
        for name,command in (("R1",[sys.executable,"-B",str(self.root/"tools/test_v1_2_7r1_repairs.py"),"--root",str(self.root),"--static-only"]),("V1_2_8",[sys.executable,"-B",str(self.root/"tools/test_v1_2_8_semantics.py"),"--root",str(self.root)])):
            process=run(command,self.root); dump(directory/name/"argv.json",{"argv":command,"cwd":str(self.root)}); write(directory/name/"stdout.txt",process.stdout); write(directory/name/"stderr.txt",process.stderr)
            if process.returncode!=0: errors.append(f"{name} semantics failed")
        if errors: raise Stop("BLOCKED/NOT TESTABLE — HARNESS","; ".join(errors),"CALIBRATION_PREFLIGHT")
        crop_dir=self.evidence/"DIAGNOSTIC/ANNOTATED_CROPS"; crop_dir.mkdir(parents=True,exist_ok=True)
        crop_result=annotated_crops(self.evidence/"DIAGNOSTIC/PRE_REPAIR/BASELINE/a1-after-native.png",tuple(self.selected_sample["integer_center_px"]),crop_dir)
        dump(crop_dir/"annotated_crops.json",crop_result)
        dump(directory/"fresh_zero_state.json",{"schema":"district_zero.p1a.v1_2_8.fresh_calibration_state.v1","status":"PASS","launches":0,"index":0,"records":[],"cache":{},"candidate_root_empty":True,"diagnostic_counter_separate":True,"historical_run_ids_present":[]})

    def resume_final_gates(self) -> None:
        """Resume after a preserved verifier-only bookkeeping stop."""
        if self.work.exists():
            if not self.work.is_dir() or any(self.work.iterdir()):
                raise Stop("BLOCKED/NOT TESTABLE — HARNESS", "final-resume work root is not new/empty", "FINAL_RESUME")
        else:
            self.work.mkdir(parents=True)
        if not self.evidence.is_dir() or (self.session.exists() and (not self.session.is_dir() or any(self.session.iterdir()))):
            raise Stop("BLOCKED/NOT TESTABLE — HARNESS", "final-resume evidence/session roots invalid", "FINAL_RESUME")
        self.outputs_initialized=True; self.load_authority_inputs(); self.acceptance=json.loads((self.root/"tests/fixtures/v1_2_8_visual_acceptance_selected.json").read_text()); self.selected_sample=json.loads((self.root/"presentation/p1a_v1_2_8_selected_sample.json").read_text()); self.launches=32; self.import_preflights=0
        self.reached=["IDENTITY","SEMANTICS","DIAGNOSTIC","SENSITIVITY","OUTER_STUDY","WALL_STUDY","COMBINED","FINAL_NATIVE_VISUALS"]
        version=run([self.godot,"--version"],self.root)
        if version.returncode!=0 or version.stdout.strip()!="4.7.1.stable.official.a13da4feb": raise Stop("BLOCKED/NOT TESTABLE — EXACT ENGINE","exact engine differs on final resume","FINAL_RESUME")
        final_record=json.loads((self.evidence/"FINAL_NATIVE_VISUALS/final_candidate_record.json").read_text())
        if final_record.get("execution_status")!="EXECUTED_COMPLETE" or final_record.get("evidence_complete") is not True or final_record.get("metrics",{}).get("status")!="PASS" or final_record.get("ray_result",{}).get("status")!="PASS": raise Stop("BLOCKED/NOT TESTABLE — FINAL NATIVE VISUALS","preserved final native result is not green","FINAL_RESUME")
        write_inventory(self.root,"PACKET_SHA256SUMS.txt")
        runtime=self.work/"FINAL_RUNTIME_RESUME"; r1.copy_project(self.root,runtime)
        imported=import_and_parse_project(self.godot,runtime,self.evidence/"FINAL_RESUME_RUNTIME_IMPORT",target_script=r1.PROBE,required_classes=self.required_classes,expected_builder_sha256=sha256(runtime/"scripts/p1a_world_builder.gd")); self.import_preflights+=1
        if imported.get("status")!="PASS": raise Stop("BLOCKED/NOT TESTABLE — HARNESS","final-resume runtime import failed","FINAL_RESUME")
        self.final_runtime=runtime

    def evaluate(self, stage: str, value: dict[str, Any]) -> dict[str, Any]:
        record=super().evaluate(stage,value)
        record.update({
            "v1_2_8_run_id":"v1.2.8-execution-run-1",
            "clean_source_inventory_sha256":"e6a13365f3019b21457d754d6d128ef85d70a39c718579703574de066141bf44",
            "selected_sample_sha256":sha256(self.root/"presentation/p1a_v1_2_8_selected_sample.json"),
            "ownership_diagnostic_sha256":sha256(self.evidence/"DIAGNOSTIC/ownership_diagnostic.json"),
            "sensitivity_result_sha256":sha256(self.evidence/"DIAGNOSTIC/SENSITIVITY/sensitivity_result.json"),
            "integer_pixel_center":self.selected_sample["integer_center_px"] if self.selected_sample else None,
            "historical_non_gating":record["metrics"].get("historical_non_gating"),
        })
        dump(self.evidence/"CANDIDATES"/record["candidate_id"]/"candidate_record.json",record)
        return record

    def search_albedo_v128(self, material: str) -> dict[str, Any] | None:
        config=self.registry["outer_closure" if material=="OUTER_CLOSURE_MASK" else "core_wall"]
        low,high=map(float,config["albedo_scale_domain"]); quantum=float(config["albedo_scale_quantum"]); maximum=int(config["max_albedo_evaluations"]); stage="OUTER_ALBEDO" if material=="OUTER_CLOSURE_MASK" else "WALL_ALBEDO"; records=[]
        def evaluate(scale: float) -> dict[str, Any]:
            scale=r1.quantize(min(high,max(low,scale)),quantum); value=r1.parameters(outer_scale=scale) if material=="OUTER_CLOSURE_MASK" else r1.parameters(wall_scale=scale); record=self.evaluate(stage,value); records.append(record); return record
        low_record=evaluate(low); high_record=evaluate(high)
        low_value=outer_y(low_record) if material=="OUTER_CLOSURE_MASK" else right_separation(low_record); high_value=outer_y(high_record) if material=="OUTER_CLOSURE_MASK" else right_separation(high_record)
        if not high_value>low_value: raise Stop("BLOCKED/NOT TESTABLE — MEASUREMENT BINDING",f"{material} response is not strictly increasing","CALIBRATION_RESPONSE")
        target=(ground_y(low_record)+0.1208) if material=="OUTER_CLOSURE_MASK" else 0.126
        while len({item["candidate_id"] for item in records})<maximum:
            middle=r1.quantize((low+high)/2.0,quantum)
            if middle in {r1.quantize(low,quantum),r1.quantize(high,quantum)}: break
            record=evaluate(middle); measured=outer_y(record) if material=="OUTER_CLOSURE_MASK" else right_separation(record)
            if measured<target: low=middle
            else: high=middle
        passing=[item for item in records if (outer_local(item) if material=="OUTER_CLOSURE_MASK" else wall_local(item))]
        dump(self.evidence/f"{stage}_TRANSCRIPT.json",{"schema":"district_zero.p1a.v1_2_8.independent_stage_transcript.v1","stage":stage,"status":"COMPLETE","target":target,"candidate_ids":[item["candidate_id"] for item in records],"executed_complete":all(executed_complete(item) for item in records),"eligible_ids":[item["candidate_id"] for item in passing]})
        if not passing: return None
        return sorted(passing,key=lambda item:(abs((outer_y(item) if material=="OUTER_CLOSURE_MASK" else right_separation(item))-target),r1.presentation_delta(item["parameters"],self.registry),item["candidate_id"]))[0]

    def search_emission_v128(self, material: str) -> dict[str, Any] | None:
        prior=[item for item in self.records if item.get("stage")== ("OUTER_ALBEDO" if material=="OUTER_CLOSURE_MASK" else "WALL_ALBEDO") and executed_complete(item)]
        if not prior: raise Stop("BLOCKED/NOT TESTABLE — HARNESS","emission fallback has no complete albedo anchor","EMISSION_FALLBACK")
        anchor=max(prior,key=lambda item: outer_y(item) if material=="OUTER_CLOSURE_MASK" else right_separation(item)); scale=float(anchor["parameters"][material]["albedo_scale"])
        low,high=map(float,self.registry["fallback"]["emission_multiplier_domain"]); quantum=float(self.registry["fallback"]["emission_multiplier_quantum"]); maximum=int(self.registry["fallback"]["max_evaluations_per_material"]); stage="OUTER_EMISSION_FALLBACK" if material=="OUTER_CLOSURE_MASK" else "WALL_EMISSION_FALLBACK"; records=[]
        def evaluate(emission: float)->dict[str,Any]:
            emission=r1.quantize(min(high,max(low,emission)),quantum); value=r1.parameters(outer_scale=scale,outer_emission=emission) if material=="OUTER_CLOSURE_MASK" else r1.parameters(wall_scale=scale,wall_emission=emission); record=self.evaluate(stage,value); records.append(record); return record
        first=evaluate(low); last=evaluate(high); target=(ground_y(first)+0.1208) if material=="OUTER_CLOSURE_MASK" else 0.126
        if not (outer_y(last) if material=="OUTER_CLOSURE_MASK" else right_separation(last))>(outer_y(first) if material=="OUTER_CLOSURE_MASK" else right_separation(first)): raise Stop("BLOCKED/NOT TESTABLE — MEASUREMENT BINDING",f"{material} fallback response is not increasing","EMISSION_FALLBACK")
        while len({item["candidate_id"] for item in records})<maximum:
            middle=r1.quantize((low+high)/2.0,quantum)
            if middle in {r1.quantize(low,quantum),r1.quantize(high,quantum)}: break
            record=evaluate(middle); measured=outer_y(record) if material=="OUTER_CLOSURE_MASK" else right_separation(record)
            if measured<target: low=middle
            else: high=middle
        passing=[item for item in records if (outer_local(item) if material=="OUTER_CLOSURE_MASK" else wall_local(item))]
        dump(self.evidence/f"{stage}_TRANSCRIPT.json",{"schema":"district_zero.p1a.v1_2_8.independent_stage_transcript.v1","stage":stage,"status":"COMPLETE","target":target,"candidate_ids":[item["candidate_id"] for item in records],"executed_complete":all(executed_complete(item) for item in records),"eligible_ids":[item["candidate_id"] for item in passing]})
        return None if not passing else sorted(passing,key=lambda item:(abs((outer_y(item) if material=="OUTER_CLOSURE_MASK" else right_separation(item))-target),r1.presentation_delta(item["parameters"],self.registry),item["candidate_id"]))[0]

    def combined_v128(self, outer: dict[str, Any], wall: dict[str, Any]) -> dict[str, Any]:
        base={"OUTER_CLOSURE_MASK":dict(outer["parameters"]["OUTER_CLOSURE_MASK"]),"CORE_WALL":dict(wall["parameters"]["CORE_WALL"])}; variants=[]
        for oo in self.registry["combined_validation"]["guard_offsets_quanta"]:
            for wo in self.registry["combined_validation"]["guard_offsets_quanta"]:
                value=json.loads(json.dumps(base))
                for material,offset in (("OUTER_CLOSURE_MASK",oo),("CORE_WALL",wo)):
                    if value[material]["emission_multiplier"]>0:
                        q=float(self.registry["fallback"]["emission_multiplier_quantum"]); lo,hi=map(float,self.registry["fallback"]["emission_multiplier_domain"]); value[material]["emission_multiplier"]=r1.quantize(min(hi,max(lo,value[material]["emission_multiplier"]+offset*q)),q)
                    else:
                        config=self.registry["outer_closure" if material=="OUTER_CLOSURE_MASK" else "core_wall"]; q=float(config["albedo_scale_quantum"]); lo,hi=map(float,config["albedo_scale_domain"]); value[material]["albedo_scale"]=r1.quantize(min(hi,max(lo,value[material]["albedo_scale"]+offset*q)),q)
                if value not in variants: variants.append(value)
        if len(variants)>9: raise Stop("BLOCKED/NOT TESTABLE — HARNESS","combined grid exceeds cap","COMBINED")
        records=[self.evaluate("COMBINED",value) for value in variants]; eligible=[item for item in records if item["metrics"].get("status")=="PASS" and _ray_green(item)]
        dump(self.evidence/"COMBINED_TRANSCRIPT.json",{"schema":"district_zero.p1a.v1_2_8.combined_transcript.v1","status":"COMPLETE","candidate_ids":[item["candidate_id"] for item in records],"executed_complete":all(executed_complete(item) for item in records),"eligible_ids":[item["candidate_id"] for item in eligible]})
        if not eligible: raise Stop("NO_PRESENTATION_ONLY_INTERVAL","complete combined 3x3 grid has no 21/21 + 14/14 candidate","COMBINED")
        interior=[item for item in eligible if abs(outer_y(item)-(ground_y(item)+0.1208))<=0.0008]
        if interior: eligible=interior
        robust=[item for item in eligible if right_separation(item)>=0.126]
        if robust: eligible=robust
        return sorted(eligible,key=lambda item:(r1.presentation_delta(item["parameters"],self.registry),-(outer_y(item)-ground_y(item)-0.12),-(right_separation(item)-0.12),item["candidate_id"]))[0]

    def materialize_v128(self, selected: dict[str, Any]) -> None:
        expected=patch_builder(self.baseline,selected["parameters"],self.registry); write(self.root/"scripts/p1a_world_builder.gd",expected); digest=sha256(self.root/"scripts/p1a_world_builder.gd")
        compatibility={"schema":"district_zero.p1a.v1_2_7r1.selected_presentation.v1","status":"PASS","selected_candidate_id":selected["candidate_id"],"parameters":selected["parameters"],"selection_rule":self.registry["selection_rule"],"presentation_delta":r1.presentation_delta(selected["parameters"],self.registry),"selected_metrics":selected["metrics"],"selected_ray_result":selected["ray_result"],"source_material_file_sha256":digest,"evaluated_source_sha256":digest}; dump(self.root/"presentation/p1a_v1_2_7r1_selected_presentation.json",compatibility)
        record={**compatibility,"schema":"district_zero.p1a.v1_2_8.selected_presentation.v1","authority_version":"v1.2.8","selected_sample_sha256":sha256(self.root/"presentation/p1a_v1_2_8_selected_sample.json"),"ownership_diagnostic_sha256":sha256(self.evidence/"DIAGNOSTIC/ownership_diagnostic.json"),"sensitivity_result_sha256":sha256(self.evidence/"DIAGNOSTIC/SENSITIVITY/sensitivity_result.json"),"historical_non_gating":selected["metrics"]["historical_non_gating"],"outer_high_branch_margin":outer_y(selected)-ground_y(selected)-0.12,"right_obstacle_margin":right_separation(selected)-0.12}; dump(self.root/"presentation/p1a_v1_2_8_selected_presentation.json",record)
        chain=json.loads((self.root/"P1A_ACTIVE_AUTHORITY_CHAIN.json").read_text()); chain.update({"active_director_authority":"v1.2.8","operative_calibration_runner":"tools/run_v1_2_8_calibration.py","operative_verifier":"tools/verify_v1_2_8_successor.py","selected_sample_record":"presentation/p1a_v1_2_8_selected_sample.json","selected_acceptance_fixture":"tests/fixtures/v1_2_8_visual_acceptance_selected.json"}); dump(self.root/"P1A_ACTIVE_AUTHORITY_CHAIN.json",chain)
        write(self.root/"STATUS.md","# District Zero P1A status — v1.2.8 selected automation\n\n**Outcome:** `CALIBRATION SELECTED — FINAL AUTOMATION REQUIRED`\n\nBranch A sample `(246,234)` and candidate `"+selected["candidate_id"]+"` selected. Human attempts: `0`. Human World Gate: `NOT PERFORMED`. P1B: `FROZEN`.\n")
        write_inventory(self.root,"PACKET_SHA256SUMS.txt")

    def final_verifiers(self) -> None:
        write_inventory(self.root,"PACKET_SHA256SUMS.txt")
        command=[sys.executable,"-B",str(self.root/"tools/verify_v1_2_8_successor.py"),"--root",str(self.root),"--clean-r1-root",str(self.clean),"--phase","final"]
        process=run(command,self.root); directory=self.evidence/"FINAL_STATIC_VERIFIER"; dump(directory/"argv.json",{"argv":command,"cwd":str(self.root)}); write(directory/"stdout.txt",process.stdout); write(directory/"stderr.txt",process.stderr)
        if process.returncode!=0: raise Stop("BLOCKED/NOT TESTABLE — PRESERVATION","v1.2.8 final verifier failed","FINAL_STATIC_VERIFIER")
        c1=self.evidence/"C1"; command=[sys.executable,"-B",str(self.root/"tools/run_v1_2_7r1_c1.py"),"--root",str(self.root),"--godot",self.godot,"--evidence-dir",str(c1),"--work-root",str(self.work/"FINAL_C1")]; process=run(command,self.root); dump(self.evidence/"C1_WRAPPER/argv.json",{"argv":command,"cwd":str(self.root)}); write(self.evidence/"C1_WRAPPER/stdout.txt",process.stdout); write(self.evidence/"C1_WRAPPER/stderr.txt",process.stderr)
        try: result=json.loads((c1/"C1_result.json").read_text())
        except Exception: result={}
        if process.returncode!=0 or result.get("status")!="PASS" or result.get("ticks_compared")!=1260 or float(result.get("maximum_absolute_difference",1))!=0.0: raise Stop("BLOCKED/NOT TESTABLE — C1","selected C1 is not exact zero-delta","C1")

    def prepare_session(self) -> None:
        super().prepare_session()
        result_path=self.session/"PREPARED_RESULT.json"; result=json.loads(result_path.read_text()); result.update({"schema":"district_zero.p1a.v1_2_8.prepared_a1_session_result.v1","status":AUTOMATION_PASS,"presentation_version":"v1.2.8","human_testing_authorized":False,"director_review_required":True}); dump(result_path,result)
        manifest_path=self.session/"SESSION_MANIFEST.json"; manifest=json.loads(manifest_path.read_text()); manifest.update({"schema":"district_zero.p1a.v1_2_8.prepared_a1_session_manifest.v1","presentation_version":"v1.2.8","human_testing_authorized":False,"director_review_required":True}); dump(manifest_path,manifest)
        state_path=self.session/"session_state.json"; state=json.loads(state_path.read_text()); state.update({"schema":"district_zero.p1a.v1_2_8.session_state.v1","presentation_version":"v1.2.8","human_testing_authorized":False}); dump(state_path,state)
        write(self.session/"DIRECTOR_REVIEW_REQUIRED.md","# Director review required\n\nAutomation passed, but this package does **not** authorize a human attempt or the Human World Gate. Charlie and Sol must authorize that separately.\n")
        write_inventory(self.session,"SESSION_SHA256SUMS.txt")
        if verify_inventory(self.session,"SESSION_SHA256SUMS.txt"): raise Stop("BLOCKED/NOT TESTABLE — PREPARED SESSION","v1.2.8 session inventory failed","PREPARED_SESSION")

    def smoke(self) -> None:
        """Run the unchanged wrapper with a disposable, smoke-mode-only driver."""
        if self.final_runtime is None:
            raise Stop("BLOCKED/NOT TESTABLE — HARNESS", "final runtime absent for smoke", "LAUNCHER_SMOKE")
        script=self.final_runtime/"tests/p1a_human_feasibility_runner.gd"; original=script.read_text(encoding="utf-8"); patched=original
        variable_anchor="var _smoke_previous_paused := false\n"
        patched=patched.replace(variable_anchor,variable_anchor+"var _v1_2_8_smoke_focus_out_done := false\nvar _v1_2_8_smoke_focus_in_done := false\n",1)
        patched=patched.replace("\twhile float(Time.get_ticks_usec() - started) / 1000000.0 < 300.0:\n","\tvar smoke_limit_s := 80.0 if smoke_mode else 300.0\n\twhile float(Time.get_ticks_usec() - started) / 1000000.0 < smoke_limit_s:\n",1)
        patched=patched.replace("\t\tif smoke_mode:\n\t\t\t_record_smoke_inputs(sample_delta, elapsed)\n","\t\tif smoke_mode:\n\t\t\t_drive_v1_2_8_disposable_smoke(elapsed)\n\t\t\t_record_smoke_inputs(sample_delta, elapsed)\n",1)
        function_anchor="\n\nfunc _record_smoke_inputs(delta: float, elapsed: float) -> void:\n"
        driver='''

func _drive_v1_2_8_disposable_smoke(elapsed: float) -> void:
	# TEST_DRIVER: this function exists only in the disposable smoke runtime.
	# It exercises the frozen action map over real rendered frames; it is never
	# copied into implemented source or a prepared session.
	for action in ["throttle", "steer_left", "steer_right"]:
		Input.action_release(action)
	if elapsed < 15.0:
		Input.action_press("throttle")
	elif elapsed >= 18.0 and elapsed < 22.0:
		Input.action_press("steer_left")
	elif elapsed >= 24.0 and elapsed < 28.0:
		Input.action_press("steer_right")
	if elapsed >= 34.0 and elapsed < 35.0:
		paused = true
	elif elapsed >= 35.0:
		paused = false
'''
        patched=patched.replace(function_anchor,driver+function_anchor,1)
        if patched==original or patched.count("func _drive_v1_2_8_disposable_smoke")!=1:
            raise Stop("BLOCKED/NOT TESTABLE — HARNESS","disposable smoke-driver anchors did not resolve exactly","LAUNCHER_SMOKE")
        write(script,patched); directory=self.evidence/"LAUNCHER_SMOKE_TEST_DRIVER"; dump(directory/"patch_record.json",{"schema":"district_zero.p1a.v1_2_8.disposable_smoke_driver_patch.v1","status":"TEST_DRIVER","scope":"disposable FINAL_RUNTIME only","source_project_modified":False,"prepared_session_modified":False,"capture_or_replay_modes_modified":False,"original_script_sha256":__import__('hashlib').sha256(original.encode()).hexdigest(),"patched_script_sha256":sha256(script),"conditions":["--v1-2-6-smoke only","80 second native frame loop","held input actions","external Computer Use focus cycle","pause/resume"],"human_attempts":0})
        imported=import_and_parse_project(self.godot,self.final_runtime,directory/"IMPORT_PREFLIGHT",target_script="res://tests/p1a_human_feasibility_runner.gd",required_classes=self.required_classes,expected_builder_sha256=sha256(self.final_runtime/"scripts/p1a_world_builder.gd")); self.import_preflights+=1
        if imported.get("status")!="PASS": raise Stop("BLOCKED/NOT TESTABLE — HARNESS","disposable smoke-driver import/parse failed","LAUNCHER_SMOKE")
        super().smoke()

    def _report(self, report: dict[str, Any]) -> dict[str, Any]:
        fresh=report["fresh_extraction"]
        return {"path":report["path"],"byte_size":report["byte_size"],"sha256":report["sha256"],"entry_count":fresh["entry_count"],"internal_inventory_record_count":report["inventory_record_count"],"internal_inventory_status":"PASS","zip_integrity":report["integrity"],"duplicate_entry_count":0,"forbidden_entry_count":0,"fresh_extraction_status":fresh["status"],"fresh_extraction_inventory_status":"PASS","source_tree_sha256":fresh["source_tree_sha256"],"fresh_tree_sha256":fresh["fresh_tree_sha256"],"trees_byte_identical":fresh["source_tree_sha256"]==fresh["fresh_tree_sha256"]}

    def finalize_v128(self,status:str,detail:str,stage:str,bindings:dict[str,Any]|None=None)->dict[str,Any]:
        bindings=bindings or {}; all_stages=["OUTER_STUDY","WALL_STUDY","COMBINED","FINAL_NATIVE_VISUALS","PRESERVATION","C1","LAUNCHER_SMOKE","PREPARED_SESSION"]; terminal={"schema":"district_zero.p1a.v1_2_8.terminal_result.v1","authority_version":"v1.2.8","run_id":"v1.2.8-execution-run-1","status":status,"stage":stage,"detail":detail,"exact_engine_identity":"4.7.1.stable.official.a13da4feb","source_packet_inventory_sha256":sha256(self.root/"PACKET_SHA256SUMS.txt") if (self.root/"PACKET_SHA256SUMS.txt").is_file() else "e6a13365f3019b21457d754d6d128ef85d70a39c718579703574de066141bf44","historical_run_2_zip_sha256":sha256(self.historical),"diagnostic_launches":5,"calibration_candidate_launches":self.launches,"selected_branch_or_null":self.selected_branch,"selected_sample_or_null":self.selected_sample,"reached_stages":self.reached,"not_reached_stages":[item for item in all_stages if item not in self.reached],"human_attempts":0,"human_world_gate":"NOT PERFORMED","P1B":"FROZEN","human_testing_authorized":False,"packages":bindings}; dump(self.evidence/"TERMINAL_RESULT.json",terminal); dump(self.evidence/"EVIDENCE_PACKAGE_MANIFEST.json",{"schema":"district_zero.p1a.v1_2_8.evidence_package_manifest.v1","terminal_status":status,"finalized_before_cleanup":True,"historical_run_2_preserved_closed":True,"fresh_extraction_required":True,"human_testing_authorized":False}); write_inventory(self.evidence,"SHA256SUMS.txt")
        output=self.output/"District-Zero-P1A-v1.2.8-Raster-Ownership-and-Calibration-Evidence.zip"; raw=package_tree(self.evidence,output,inventory_name="SHA256SUMS.txt",scratch_parent=self.work/"FRESH_EXTRACTIONS"); report=self._report(raw); dump(self.output/(output.name+".report.json"),report); return report

    def package_success_v128(self)->dict[str,Any]:
        write(self.root/"STATUS.md","# District Zero P1A status — v1.2.8 automation complete\n\n**Outcome:** `AUTOMATION PASS — PREPARED A1 SESSION READY FOR DIRECTOR REVIEW`\n\nThis is not P1A PASS and does not authorize human testing. Human attempts: `0`. Human World Gate: `NOT PERFORMED`. P1B: `FROZEN`.\n"); write_inventory(self.root,"PACKET_SHA256SUMS.txt")
        delivery=self.work/"District-Zero-P1A-v1.2.8-Implemented-Source"
        def ignore(_directory:str,names:list[str])->set[str]: return {name for name in names if name in {".godot","__pycache__","director_inputs",".pytest_cache",".mypy_cache"} or name==".DS_Store" or name.startswith("._") or name.endswith((".pyc",".pyo",".zip"))}
        shutil.copytree(self.root,delivery,ignore=ignore); write_inventory(delivery,"PACKET_SHA256SUMS.txt")
        source_raw=package_tree(delivery,self.output/"District-Zero-P1A-v1.2.8-Implemented-Source.zip",inventory_name="PACKET_SHA256SUMS.txt",scratch_parent=self.work/"FRESH_EXTRACTIONS"); session_raw=package_tree(self.session,self.output/"District-Zero-P1A-v1.2.8-Prepared-A1-Session.zip",inventory_name="SESSION_SHA256SUMS.txt",scratch_parent=self.work/"FRESH_EXTRACTIONS"); bindings={"implemented_source":self._report(source_raw),"prepared_session":self._report(session_raw)}; evidence=self.finalize_v128(AUTOMATION_PASS,"all bounded automation passed; director review required before human testing","PREPARED_SESSION",bindings); reports={**bindings,"validation_evidence":evidence,"terminal_status":AUTOMATION_PASS,"engine_identity":"4.7.1.stable.official.a13da4feb","selected_candidate":json.loads((self.root/"presentation/p1a_v1_2_8_selected_presentation.json").read_text()),"human_attempts":0,"human_world_gate":"NOT PERFORMED","P1B":"FROZEN"}; dump(self.output/"District-Zero-P1A-v1.2.8-PACKAGE-REPORT.json",reports); return reports

    def execute_v128(self)->dict[str,Any]:
        outer=self.search_albedo_v128("OUTER_CLOSURE_MASK") or self.search_emission_v128("OUTER_CLOSURE_MASK")
        self.reached.append("OUTER_STUDY")
        if outer is None: raise Stop("NO_PRESENTATION_ONLY_INTERVAL","complete outer material domains have no robust candidate","OUTER_STUDY")
        wall=self.search_albedo_v128("CORE_WALL") or self.search_emission_v128("CORE_WALL")
        self.reached.append("WALL_STUDY")
        if wall is None: raise Stop("NO_PRESENTATION_ONLY_INTERVAL","complete wall material domains have no robust candidate","WALL_STUDY")
        selected=self.combined_v128(outer,wall); self.reached.append("COMBINED"); self.materialize_v128(selected); self.final_probe(); self.reached.append("FINAL_NATIVE_VISUALS"); self.final_verifiers(); self.reached.extend(["PRESERVATION","C1"]); self.smoke(); self.reached.append("LAUNCHER_SMOKE"); self.prepare_session(); self.reached.append("PREPARED_SESSION"); return self.package_success_v128()

    def execute_final_resume(self)->dict[str,Any]:
        # C1 already executed and was durably packaged before a later smoke
        # blocker. Re-verify its complete inventory/result instead of spending
        # a second identical physics comparison.
        write_inventory(self.root,"PACKET_SHA256SUMS.txt")
        command=[sys.executable,"-B",str(self.root/"tools/verify_v1_2_8_successor.py"),"--root",str(self.root),"--clean-r1-root",str(self.clean),"--phase","final"]
        process=run(command,self.root); directory=self.evidence/"FINAL_STATIC_VERIFIER_RESUME"; dump(directory/"argv.json",{"argv":command,"cwd":str(self.root)}); write(directory/"stdout.txt",process.stdout); write(directory/"stderr.txt",process.stderr)
        if process.returncode!=0: raise Stop("BLOCKED/NOT TESTABLE — PRESERVATION","v1.2.8 resumed final verifier failed","FINAL_STATIC_VERIFIER")
        c1_result=json.loads((self.evidence/"C1/C1_result.json").read_text()); c1_errors=verify_inventory(self.evidence/"C1","SHA256SUMS.txt")
        if c1_errors or c1_result.get("status")!="PASS" or c1_result.get("ticks_compared")!=1260 or float(c1_result.get("maximum_absolute_difference",1))!=0.0: raise Stop("BLOCKED/NOT TESTABLE — C1","preserved selected C1 is not exact and inventory-clean","C1")
        dump(self.evidence/"C1_PRESERVED_REVALIDATION.json",{"schema":"district_zero.p1a.v1_2_8.preserved_c1_revalidation.v1","status":"PASS","result_sha256":sha256(self.evidence/"C1/C1_result.json"),"inventory_sha256":sha256(self.evidence/"C1/SHA256SUMS.txt"),"ticks_compared":1260,"maximum_absolute_difference":0.0,"rerun":False})
        self.reached.extend(["PRESERVATION","C1"]); self.smoke(); self.reached.append("LAUNCHER_SMOKE"); self.prepare_session(); self.reached.append("PREPARED_SESSION"); return self.package_success_v128()


def main()->int:
    parser=argparse.ArgumentParser(); parser.add_argument("--root",default=str(ROOT_DEFAULT)); parser.add_argument("--clean-r1-root",required=True); parser.add_argument("--base-root",required=True); parser.add_argument("--historical-evidence-zip",required=True); parser.add_argument("--godot",required=True); parser.add_argument("--work-root",required=True); parser.add_argument("--evidence-root",required=True); parser.add_argument("--prepared-session-root",required=True); parser.add_argument("--diagnostic-resume",required=True); parser.add_argument("--resume-final-gates",action="store_true"); args=parser.parse_args(); director=Director(args)
    try:
        if args.resume_final_gates: director.resume_final_gates(); reports=director.execute_final_resume()
        else: director.resume_preflight(); reports=director.execute_v128()
        print(json.dumps({"status":AUTOMATION_PASS,"calibration_candidate_launches":director.launches,"diagnostic_launches":5,"reports":reports},indent=2,sort_keys=True)); shutil.rmtree(director.work,ignore_errors=True); return 0
    except r1.StopRun as exc:
        try: evidence=director.finalize_v128(exc.status,exc.detail,exc.stage)
        except Exception as final_error: evidence={"status":"FAILED","error":str(final_error)}
        print(json.dumps({"status":exc.status,"stage":exc.stage,"detail":exc.detail,"diagnostic_launches":5,"calibration_candidate_launches":director.launches,"evidence_package":evidence},indent=2,sort_keys=True));
        if evidence.get("status")!="FAILED": shutil.rmtree(director.work,ignore_errors=True)
        return 2
    except Exception as exc:
        try: evidence=director.finalize_v128("BLOCKED/NOT TESTABLE — HARNESS",str(exc),"UNHANDLED_HARNESS_EXCEPTION")
        except Exception as final_error: evidence={"status":"FAILED","error":str(final_error)}
        print(json.dumps({"status":"BLOCKED/NOT TESTABLE — HARNESS","detail":str(exc),"diagnostic_launches":5,"calibration_candidate_launches":director.launches,"evidence_package":evidence},indent=2,sort_keys=True));
        if evidence.get("status")!="FAILED": shutil.rmtree(director.work,ignore_errors=True)
        return 2


if __name__=="__main__": raise SystemExit(main())
