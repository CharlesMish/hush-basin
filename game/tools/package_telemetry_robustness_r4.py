#!/usr/bin/env python3
"""Create clean, round-trip-verified R4 source, player, and evidence ZIPs."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from p1a_v1_2_7r1_harness import package_tree, verify_inventory, write_inventory


def dump(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True)
    parser.add_argument("--player", required=True)
    parser.add_argument("--evidence", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--scratch", required=True)
    args = parser.parse_args()
    source = Path(args.source).resolve()
    player = Path(args.player).resolve()
    evidence = Path(args.evidence).resolve()
    output = Path(args.output_dir).resolve()
    scratch = Path(args.scratch).resolve()
    output.mkdir(parents=True, exist_ok=True)
    scratch.mkdir(parents=True, exist_ok=True)

    source_count = write_inventory(source, "PACKET_SHA256SUMS.txt")
    player_count = write_inventory(player, "PLAY_PROJECT_SHA256SUMS.txt")
    evidence_count = write_inventory(evidence, "SHA256SUMS.txt")
    inventory_errors = {
        "source": verify_inventory(source, "PACKET_SHA256SUMS.txt"),
        "player": verify_inventory(player, "PLAY_PROJECT_SHA256SUMS.txt"),
        "evidence": verify_inventory(evidence, "SHA256SUMS.txt"),
    }
    if any(inventory_errors.values()):
        raise RuntimeError(inventory_errors)

    packages = {
        "source": package_tree(source, output / "District-Zero-P1A-v1.2.8-Robustness-R4-Source.zip", inventory_name="PACKET_SHA256SUMS.txt", scratch_parent=scratch),
        "player": package_tree(player, output / "District-Zero-P1A-v1.2.8-Robustness-R4-Play-Project.zip", inventory_name="PLAY_PROJECT_SHA256SUMS.txt", scratch_parent=scratch),
        "evidence": package_tree(evidence, output / "District-Zero-P1A-v1.2.8-Robustness-R4-Evidence.zip", inventory_name="SHA256SUMS.txt", scratch_parent=scratch),
    }
    verification = json.loads((evidence / "VERIFICATION_REPORT.json").read_text(encoding="utf-8"))
    if verification.get("status") != "PASS":
        raise RuntimeError("verification report is not PASS")
    report = {
        "schema": "district_zero.p1a.telemetry_robustness_r4_package_report.v1",
        "status": "AUTOMATION PASS — TELEMETRY ROBUSTNESS R4 READY FOR OWNER REVIEW",
        "source_inventory": {"record_count": source_count, "status": "PASS"},
        "player_inventory": {"record_count": player_count, "status": "PASS"},
        "evidence_inventory": {"record_count": evidence_count, "status": "PASS"},
        "packages": packages,
        "verification": verification,
        "human_attempts": 0,
        "human_world_gate": "NOT PERFORMED",
        "P1B": "FROZEN",
    }
    report_path = output / "District-Zero-P1A-v1.2.8-Robustness-R4-PACKAGE-REPORT.json"
    dump(report_path, report)
    print(json.dumps({**report, "report_path": str(report_path)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
