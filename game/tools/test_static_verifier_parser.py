#!/usr/bin/env python3
"""Semantic regression cases for the v1.2.4I-R1 static-verifier parser."""
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import sys
from typing import Any

from run_v1_2_4i_gate import parse_static_verifier_result

ROOT = pathlib.Path(__file__).resolve().parents[1]


def sha256(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=str(ROOT))
    parser.add_argument("--output")
    args = parser.parse_args()
    root = pathlib.Path(args.root).resolve()
    metadata = json.loads((root / "tests/fixtures/static_verifier_parser_cases.json").read_text(encoding="utf-8"))
    fixture_path = root / metadata["captured_fixture"]["path"]
    fixture_bytes = fixture_path.read_bytes()
    fixture_text = fixture_bytes.decode("utf-8")
    fixture_object = json.loads(fixture_text)

    cases: list[tuple[str, str, int, bool]] = []
    cases.append(("captured_pretty_pass_rc0", fixture_text, 0, True))
    cases.append(("compact_pass_rc0", json.dumps(fixture_object, ensure_ascii=False, separators=(",", ":")), 0, True))
    cases.append(("surrounding_whitespace_pass_rc0", " \t\n" + fixture_text + "\n \t", 0, True))
    status_fail = dict(fixture_object); status_fail["status"] = "FAIL"
    cases.append(("pretty_status_fail_rc0", json.dumps(status_fail, ensure_ascii=False, indent=2, sort_keys=True) + "\n", 0, False))
    count_fail = dict(fixture_object); count_fail["error_count"] = 2
    cases.append(("pretty_nonzero_error_count_rc0", json.dumps(count_fail, ensure_ascii=False, indent=2, sort_keys=True) + "\n", 0, False))
    cases.append(("pass_nonzero_process_return", fixture_text, 1, False))
    cases.append(("empty_stdout", "", 0, False))
    cases.append(("malformed_stdout", "{\n  \"status\": \"PASS\"", 0, False))
    cases.append(("multiple_json_documents", fixture_text + "\n{}\n", 0, False))
    cases.append(("trailing_nonwhitespace_output", fixture_text + "not-json\n", 0, False))
    cases.append(("non_object_array", "[]\n", 0, False))
    cases.append(("non_object_string", "\"PASS\"\n", 0, False))
    cases.append(("non_object_number", "0\n", 0, False))

    results: list[dict[str, Any]] = []
    failures: list[str] = []
    observed_ids = [case[0] for case in cases]
    if observed_ids != metadata["required_case_ids"]:
        failures.append("case ID/order mismatch against fixture metadata")
    if sha256(fixture_path) != metadata["captured_fixture"]["sha256"]:
        failures.append("captured fixture SHA-256 mismatch")
    if len(fixture_bytes) != int(metadata["captured_fixture"]["byte_size"]):
        failures.append("captured fixture byte-size mismatch")

    for case_id, stdout, returncode, expected_accept in cases:
        parsed = parse_static_verifier_result(stdout, returncode)
        accepted = parsed.get("status") == "PASS"
        passed = accepted is expected_accept
        if not passed:
            failures.append(f"{case_id}: expected accepted={expected_accept}, observed {accepted}")
        results.append({
            "case_id": case_id,
            "process_returncode": returncode,
            "expected_accept": expected_accept,
            "observed_accept": accepted,
            "case_pass": passed,
            "parser_errors": parsed.get("parser_errors", []),
        })

    output = {
        "schema": "district_zero.p1a.v1_2_4i_r1.static_verifier_parser_test_result.v1",
        "status": "PASS" if not failures else "FAIL",
        "error_count": len(failures),
        "errors": failures,
        "case_count": len(results),
        "pass_count": sum(bool(item["case_pass"]) for item in results),
        "captured_fixture_sha256": sha256(fixture_path),
        "results": results,
    }
    text = json.dumps(output, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if args.output:
        pathlib.Path(args.output).write_text(text, encoding="utf-8", newline="\n")
    sys.stdout.write(text)
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
