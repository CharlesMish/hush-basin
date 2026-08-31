#!/usr/bin/env python3
"""Inventory and round-trip package the Visibility R3 successor and evidence."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from p1a_v1_2_7r1_harness import package_tree, verify_inventory, write_inventory


def write(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True)
    parser.add_argument("--evidence", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--scratch", required=True)
    args = parser.parse_args()
    source = Path(args.source).resolve()
    evidence = Path(args.evidence).resolve()
    output = Path(args.output_dir).resolve()
    scratch = Path(args.scratch).resolve()
    output.mkdir(parents=True, exist_ok=True)
    scratch.mkdir(parents=True, exist_ok=True)

    source_count = write_inventory(source, "PACKET_SHA256SUMS.txt")
    evidence_count = write_inventory(evidence, "SHA256SUMS.txt")
    source_errors = verify_inventory(source, "PACKET_SHA256SUMS.txt")
    evidence_errors = verify_inventory(evidence, "SHA256SUMS.txt")
    if source_errors or evidence_errors:
        raise RuntimeError({"source": source_errors, "evidence": evidence_errors})

    source_zip = output / "District-Zero-P1A-v1.2.8-Visibility-R3-Source.zip"
    evidence_zip = output / "District-Zero-P1A-v1.2.8-Visibility-R3-Evidence.zip"
    source_package = package_tree(
        source,
        source_zip,
        inventory_name="PACKET_SHA256SUMS.txt",
        scratch_parent=scratch,
    )
    evidence_package = package_tree(
        evidence,
        evidence_zip,
        inventory_name="SHA256SUMS.txt",
        scratch_parent=scratch,
    )
    verification = json.loads((evidence / "STATIC_VERIFICATION" / "report.json").read_text(encoding="utf-8"))
    report = {
        "human_attempts": 0,
        "human_world_gate": "NOT PERFORMED",
        "p1b": "FROZEN",
        "packages": {
            "implemented_source": source_package,
            "validation_evidence": evidence_package,
        },
        "schema": "district_zero.p1a.visibility_repair_r3_package_report.v1",
        "source_inventory": {"record_count": source_count, "status": "PASS"},
        "status": "AUTOMATION PASS — ALL-SOLID VISIBILITY R3 READY FOR OWNER REVIEW",
        "validation_evidence_inventory": {"record_count": evidence_count, "status": "PASS"},
        "verification": {
            "c1_maximum_absolute_difference": verification["visibility_c1"]["maximum_absolute_difference"],
            "frozen_byte_identical_file_count": verification["frozen_byte_identical_file_count"],
            "native_metrics": verification["native_metrics"],
            "native_rays": verification["native_rays"],
            "registered_sweep_count": verification["registered_sweep_count"],
            "status": verification["status"],
            "two_sided_solid_families": verification["two_sided_solid_families"],
            "user_facing_identity": verification["user_facing_identity"],
            "visibility_behavior_checks": verification["visibility_behavior_checks"],
            "visible_left_wall_separation": verification["visible_left_wall_separation"],
        },
    }
    report_path = output / "District-Zero-P1A-v1.2.8-Visibility-R3-PACKAGE-REPORT.json"
    write(report_path, report)
    print(json.dumps({**report, "report_path": str(report_path)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
