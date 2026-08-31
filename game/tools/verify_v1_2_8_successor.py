#!/usr/bin/env python3
"""Strict preservation and derived-authority verifier for v1.2.8."""
from __future__ import annotations

import argparse
import ast
import json
import pathlib
import re
import subprocess
import sys
from typing import Any

ROOT_DEFAULT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DEFAULT / "tools"))

from p1a_v1_2_7r1_harness import patch_builder, sha256, verify_inventory

R1_INVENTORY_SHA = "e6a13365f3019b21457d754d6d128ef85d70a39c718579703574de066141bf44"
BASE_BUILDER_SHA = "c016d5e2654919d6de5e1416ab21a40da81149ec11100dae8d95a89922b9dc38"

NEW_PATHS = {
    "V1_2_7R1_INPUT_SHA256SUMS.txt",
    "V1_2_8_AUTHORITY_OVERLAY_SHA256SUMS.txt",
    "presentation/p1a_v1_2_8_selected_sample.json",
    "presentation/p1a_v1_2_8_selected_presentation.json",
    # Exact compatibility record consumed by the unchanged R1 C1 helper. Its
    # canonical bytes are independently re-derived and checked below.
    "presentation/p1a_v1_2_7r1_selected_presentation.json",
    "tests/fixtures/v1_2_8_visual_acceptance_selected.json",
    "tests/p1a_v1_2_8_ownership_probe.gd",
    "tools/p1a_v1_2_8_contract.py",
    "tools/p1a_v1_2_8_diagnostic.py",
    "tools/p1a_v1_2_8_metrics.py",
    "tools/run_v1_2_8_diagnostic.py",
    "tools/run_v1_2_8_calibration.py",
    "tools/test_v1_2_8_semantics.py",
    "tools/verify_v1_2_8_successor.py",
}


def records(path: pathlib.Path) -> dict[str, str]:
    output: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        match = re.fullmatch(r"([0-9a-f]{64})  (.+)", line)
        if match is None or match.group(2) in output:
            raise ValueError(f"invalid inventory row: {line}")
        output[match.group(2)] = match.group(1)
    return output


def substantive(root: pathlib.Path) -> set[str]:
    return {
        path.relative_to(root).as_posix()
        for path in root.rglob("*")
        if path.is_file()
        and not any(part in {".godot", "__pycache__", ".pytest_cache", ".mypy_cache"} for part in path.relative_to(root).parts)
        and path.name != ".DS_Store"
        and not path.name.startswith("._")
        and not path.name.endswith((".pyc", ".pyo"))
    }


def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("--root", default=str(ROOT_DEFAULT)); parser.add_argument("--clean-r1-root", required=True); parser.add_argument("--phase", choices=("diagnostic", "final"), default="final"); args = parser.parse_args()
    root = pathlib.Path(args.root).resolve(); clean = pathlib.Path(args.clean_r1_root).resolve(); errors: list[str] = []; counts: dict[str, Any] = {}
    def check(condition: bool, detail: str) -> None:
        if not condition: errors.append(detail)
    input_inventory = root/"V1_2_7R1_INPUT_SHA256SUMS.txt"
    check(input_inventory.is_file() and sha256(input_inventory) == R1_INVENTORY_SHA, "preserved R1 inventory identity mismatch")
    try: baseline_records = records(input_inventory)
    except Exception as exc: baseline_records = {}; errors.append(str(exc))
    check(len(baseline_records) == 2198, f"R1 inventory record count {len(baseline_records)} != 2198")
    check((clean/"PACKET_SHA256SUMS.txt").is_file() and sha256(clean/"PACKET_SHA256SUMS.txt") == R1_INVENTORY_SHA and not verify_inventory(clean,"PACKET_SHA256SUMS.txt"), "clean R1 root is not checksum-exact")
    overlay_inventory = root/"V1_2_8_AUTHORITY_OVERLAY_SHA256SUMS.txt"
    try: overlay_records = records(overlay_inventory)
    except Exception as exc: overlay_records = {}; errors.append(str(exc))
    check(len(overlay_records) == 10, f"overlay inventory count {len(overlay_records)} != 10")
    authority_mutable = {"STATUS.md", "P1A_ACTIVE_AUTHORITY_CHAIN.json", "README_FIRST.md", "PACKET_SHA256SUMS.txt"}
    strict_changes: list[str] = []
    for relative, digest in baseline_records.items():
        if relative in authority_mutable or relative == "scripts/p1a_world_builder.gd": continue
        expected = overlay_records.get(relative, digest)
        path = root/relative
        if not path.is_file() or sha256(path) != expected: strict_changes.append(relative)
    check(not strict_changes, f"protected R1/overlay bytes changed: {strict_changes[:10]}")
    counts["protected_input_files"] = len(baseline_records)-len(authority_mutable)-1
    baseline_path=root/"tests/fixtures/v1_2_7_v1_2_6_world_builder.gd"; check(sha256(baseline_path)==BASE_BUILDER_SHA,"canonical builder fixture changed")
    selected_sample=root/"presentation/p1a_v1_2_8_selected_sample.json"; acceptance=root/"tests/fixtures/v1_2_8_visual_acceptance_selected.json"
    check(selected_sample.is_file() and acceptance.is_file(),"selected sample/acceptance missing")
    if selected_sample.is_file():
        sample=json.loads(selected_sample.read_text()); check(sample.get("integer_center_px")==[246,234] and sample.get("branch")=="BRANCH_A_SAMPLE_REPLACEMENT","selected sample authority differs from diagnostic result"); check(sample.get("historical_non_gating",{}).get("gating") is False,"historical sample became gating")
    if acceptance.is_file():
        value=json.loads(acceptance.read_text()); check(value.get("integer_samples",{}).get("A1_FAMILIARIZATION",{}).get("left_outer_closure")==[246,234],"selected acceptance integer sample differs")
    if args.phase=="final":
        selected_path=root/"presentation/p1a_v1_2_8_selected_presentation.json"; check(selected_path.is_file(),"selected presentation missing")
        if selected_path.is_file():
            selected=json.loads(selected_path.read_text()); registry=json.loads((root/"tests/fixtures/v1_2_7_calibration_registry.json").read_text()); expected=patch_builder(baseline_path.read_text(),selected.get("parameters",{}),registry); check((root/"scripts/p1a_world_builder.gd").read_text()==expected,"world builder is not exact canonical selected materialization"); check(selected.get("source_material_file_sha256")==sha256(root/"scripts/p1a_world_builder.gd"),"selected presentation hash binding differs"); check(selected.get("selected_sample_sha256")==sha256(selected_sample),"selected presentation sample binding differs")
    else: check(sha256(root/"scripts/p1a_world_builder.gd")==BASE_BUILDER_SHA,"diagnostic phase changed world builder")
    actual=substantive(root); allowed_added=set(overlay_records)|NEW_PATHS|{"PACKET_SHA256SUMS.txt"}; additions=actual-set(baseline_records); check(additions<=allowed_added,f"unauthorized added paths: {sorted(additions-allowed_added)[:10]}")
    bad_python=[]
    for path in root.rglob("*.py"):
        if "__pycache__" in path.parts: continue
        try: ast.parse(path.read_text(encoding="utf-8"))
        except Exception as exc: bad_python.append(f"{path.relative_to(root)}:{exc}")
    check(not bad_python,f"Python parse failures: {bad_python[:5]}")
    bad_json=[]
    for path in root.rglob("*.json"):
        try: json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc: bad_json.append(f"{path.relative_to(root)}:{exc}")
    check(not bad_json,f"JSON parse failures: {bad_json[:5]}")
    for name,expected in (("r1",65),("v128",45)):
        command=[sys.executable,"-B",str(root/("tools/test_v1_2_7r1_repairs.py" if name=="r1" else "tools/test_v1_2_8_semantics.py")),"--root",str(root)]
        if name=="r1": command.append("--static-only")
        process=subprocess.run(command,cwd=root,capture_output=True,text=True,check=False)
        try: result=json.loads(process.stdout)
        except Exception: result={}
        check(process.returncode==0 and result.get("status")=="PASS" and result.get("case_count")==expected,f"{name} semantic suite failed"); counts[f"{name}_semantic_cases"]=result.get("case_count")
    packet_errors=verify_inventory(root,"PACKET_SHA256SUMS.txt"); check(not packet_errors,f"packet inventory failed: {packet_errors[:5]}"); counts["packet_records"]=len((root/"PACKET_SHA256SUMS.txt").read_text().splitlines()) if (root/"PACKET_SHA256SUMS.txt").is_file() else 0
    result={"schema":"district_zero.p1a.v1_2_8.successor_verifier_result.v1","status":"PASS" if not errors else "FAIL","phase":args.phase,"error_count":len(errors),"errors":errors,"counts":counts,"human_attempts":0,"human_world_gate":"NOT PERFORMED","P1B":"FROZEN"}; print(json.dumps(result,indent=2,sort_keys=True)); return 0 if not errors else 1


if __name__=="__main__": raise SystemExit(main())
