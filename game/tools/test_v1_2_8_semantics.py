#!/usr/bin/env python3
"""Behavioral semantic regression suite for every registered v1.2.8 case."""
from __future__ import annotations

import argparse
import json
import pathlib
import sys
from typing import Any, Callable

ROOT_DEFAULT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DEFAULT / "tools"))

from p1a_v1_2_8_contract import (
    AUTOMATION_PASS,
    HARNESS_BLOCKER,
    MEASUREMENT_BLOCKER,
    NO_INTERVAL,
    NO_SAMPLE,
    ORIGINAL_CENTER,
    TARGET_FACE,
    TARGET_NODE,
    TARGET_SOURCE,
    acceptance_cardinality,
    adjudicate_branch,
    assign_visible_components,
    automation_terminal,
    branch_b_delta_allowed,
    candidate_gate,
    delivery_path_allowed,
    diagnostic_counters_valid,
    footprint,
    fresh_calibration_state_valid,
    historical_record_valid,
    influence_subset,
    no_interval_admissible,
    normalized_to_pixel,
    outer_branch,
    outer_feasible,
    pixel_center_normalized,
    prepared_session_write_order,
    select_sample,
    selector_parameter_names,
    sensitivity_result,
    terminal_actions,
)


class Suite:
    def __init__(self) -> None:
        self.results: list[dict[str, Any]] = []

    def check(self, case_id: str, condition: bool, detail: str = "") -> None:
        self.results.append({"id": case_id, "status": "PASS" if condition else "FAIL", "detail": detail})


def background_map() -> dict[tuple[int, int], dict[str, Any]]:
    return {
        (x, y): {
            "x": x,
            "y": y,
            "decode_status": "BACKGROUND",
            "source_geometry_id": None,
            "render_node": None,
            "face_class": None,
            "connected_side_component_id": None,
            "side_plane_id_or_null": None,
            "triangle_id_or_null": None,
        }
        for y in range(206, 283)
        for x in range(218, 295)
    }


def set_target(
    owner_map: dict[tuple[int, int], dict[str, Any]],
    points: list[tuple[int, int]],
    component: str = "OUTER_CLOSURE_MASK_C02",
    face: str = TARGET_FACE,
) -> None:
    for x, y in points:
        if (x, y) not in owner_map:
            continue
        owner_map[(x, y)] = {
            "x": x,
            "y": y,
            "decode_status": "EXACT",
            "source_geometry_id": TARGET_SOURCE,
            "render_node": TARGET_NODE,
            "face_class": face,
            "connected_side_component_id": component,
            "side_plane_id_or_null": None,
            "triangle_id_or_null": None,
        }


def full_target_map() -> dict[tuple[int, int], dict[str, Any]]:
    result = background_map()
    set_target(result, list(result))
    return assign_visible_components(result)


def block_map(center: tuple[int, int], *, component: str = "OUTER_CLOSURE_MASK_C02", extra: list[tuple[int, int]] | None = None) -> dict[tuple[int, int], dict[str, Any]]:
    result = background_map()
    set_target(result, footprint(center, 6), component)
    if extra:
        set_target(result, extra, component)
    return assign_visible_components(result)


def history(on_y: float = 0.069, off_y: float = 0.069) -> dict[str, Any]:
    return {
        "integer_center_px": [256, 244],
        "normalized": [0.2, 0.34],
        "shadow_on_Y": on_y,
        "shadow_off_Y": off_y,
        "label": "v1.2.7R1_old_sample_historical_non_gating",
        "gating": False,
    }


def pass_checks() -> list[dict[str, Any]]:
    return [{"id": f"C{i:02d}", "observed": float(i), "pass": True} for i in range(21)]


def no_interval_state(**updates: Any) -> dict[str, Any]:
    value: dict[str, Any] = {
        "ownership_status": "PASS",
        "sensitivity_status": "PASS",
        "semantic_status": "PASS",
        "stage_transcript_complete": True,
        "all_records_executed_complete": True,
        "all_records_bound_v1_2_8": True,
        "eligible_count": 0,
        "cap_reached_before_completion": False,
    }
    value.update(updates)
    return value


def execute(root: pathlib.Path) -> dict[str, Any]:
    suite = Suite()
    suite.check("COORD_FLOOR_ORIGINAL", normalized_to_pixel((0.20, 0.34)) == (256, 244))
    patch = footprint((256, 244), 4)
    suite.check("COORD_PATCH_BOUNDS", len(patch) == 81 and min(x for x, _ in patch) == 252 and max(x for x, _ in patch) == 260 and min(y for _, y in patch) == 240 and max(y for _, y in patch) == 248)
    margin = footprint((256, 244), 6)
    suite.check("COORD_FOOTPRINT_BOUNDS", len(margin) == 169 and len(set(margin)) == 169)
    suite.check("COORD_SELECTED_ROUNDTRIP", all(normalized_to_pixel(pixel_center_normalized((x, y))) == (x, y) for x, y in [(0, 0), (246, 234), (1279, 719)]))

    safe = full_target_map()
    suite.check("OWNER_ALL_SAFE_RESPONSIVE_ORIGINAL_VALID", adjudicate_branch(safe, "PASS")["branch"] == "ORIGINAL_VALID")
    foreign_metric = {point: dict(record) for point, record in safe.items()}
    foreign_metric[(256, 244)].update({"source_geometry_id": "HEIGHTFIELD_SUPPORT", "render_node": "/terrain", "face_class": None})
    suite.check("OWNER_FOREIGN_METRIC_PIXEL_BRANCH_A", adjudicate_branch(foreign_metric, "PASS")["branch"] == "BRANCH_A_SAMPLE_REPLACEMENT")
    foreign_margin = {point: dict(record) for point, record in safe.items()}
    foreign_margin[(250, 238)].update({"source_geometry_id": "HEIGHTFIELD_SUPPORT", "render_node": "/terrain", "face_class": None})
    suite.check("OWNER_FOREIGN_PERIMETER_PIXEL_BRANCH_A", adjudicate_branch(foreign_margin, "PASS")["branch"] == "BRANCH_A_SAMPLE_REPLACEMENT")
    mixed = {point: dict(record) for point, record in safe.items()}
    mixed[(256, 244)]["decode_status"] = "MIXED"
    suite.check("OWNER_MIXED_BOUNDARY_BRANCH_A", adjudicate_branch(mixed, "PASS")["branch"] == "BRANCH_A_SAMPLE_REPLACEMENT")
    incomplete = {point: dict(record) for point, record in safe.items()}
    incomplete.pop((218, 206))
    suite.check("OWNER_INCOMPLETE_MAP_HARNESS", adjudicate_branch(incomplete, "PASS")["status"] == HARNESS_BLOCKER)
    suite.check("OWNER_SAFE_FLAT_BRANCH_B", adjudicate_branch(safe, MEASUREMENT_BLOCKER)["branch"] == "BRANCH_B_RENDER_CONSUMER_BINDING")

    radius_in = block_map((288, 244))
    radius_out = block_map((288, 245))
    suite.check("SEARCH_RADIUS_INCLUSIVE", select_sample(radius_in)["selected"] is not None and select_sample(radius_in)["selected"]["squared_distance"] == 1024 and select_sample(radius_out)["selected"] is None)
    components = background_map()
    set_target(components, footprint((246, 244), 6), "OUTER_CLOSURE_MASK_C02")
    set_target(components, footprint((276, 244), 6), "OUTER_CLOSURE_MASK_C03")
    components = assign_visible_components(components)
    selected_components = select_sample(components)
    suite.check("SEARCH_COMPONENT_FILTER", selected_components["selected"]["owner_component_id"].startswith("OUTER_CLOSURE_MASK_C02") and all(item["owner_component_id"].startswith("OUTER_CLOSURE_MASK_C02") for item in selected_components["sorted_eligible"]))
    top = background_map()
    set_target(top, footprint((256, 244), 6), face="TOP")
    top = assign_visible_components(top)
    suite.check("SEARCH_FACE_FILTER", select_sample(top)["selected"] is None)
    short = block_map((256, 244))
    short[(262, 250)].update({"decode_status": "BACKGROUND", "source_geometry_id": None, "render_node": None, "face_class": None, "connected_side_component_id": None, "visible_component_id": None})
    suite.check("SEARCH_FULL_169_FILTER", select_sample(short)["selected"] is None)
    tied = background_map()
    set_target(tied, footprint((246, 244), 6) + footprint((266, 244), 6) + [(x, 244) for x in range(253, 260)])
    tied = assign_visible_components(tied)
    tied_result = select_sample(tied)
    suite.check("SEARCH_TIE_D2_Y_X", tied_result["selected"]["x"] == 246 and tied_result["selected"]["y"] == 244)
    suite.check("SEARCH_NO_ELIGIBLE_EXACT_TERMINAL", select_sample(background_map())["status"] == NO_SAMPLE)
    permutation_a = select_sample(tied)
    permutation_b = select_sample({point: dict(record) for point, record in tied.items()})
    suite.check("SEARCH_LUMINANCE_BLIND_PERMUTATION", permutation_a == permutation_b)
    suite.check("SEARCH_SELECTOR_SIGNATURE_BLIND", selector_parameter_names() == ["owner_map", "original", "width", "height"])
    suite.check("SEARCH_BRIGHTER_FARTHER_CANNOT_WIN", tied_result["selected"]["x"] == 246)

    rgb = [(10, 20, 30)] * 81
    sensitivity = sensitivity_result(0.2, 0.3, 0.4, rgb, rgb, owner_margin_pass=True)
    suite.check("SENSITIVITY_STRICT_MONOTONIC_PASS", sensitivity["status"] == "PASS")
    suite.check("SENSITIVITY_GLOBAL_CHANGE_FLAT_PATCH_BLOCKER", sensitivity_result(0.2, 0.2, 0.2, rgb, rgb, owner_margin_pass=True)["status"] == MEASUREMENT_BLOCKER)
    suite.check("SENSITIVITY_OPPOSITE_OR_NONMONOTONIC_BLOCKER", sensitivity_result(0.3, 0.2, 0.4, rgb, rgb, owner_margin_pass=True)["status"] == MEASUREMENT_BLOCKER)
    unrelated = list(rgb); unrelated[40] = (11, 20, 30)
    suite.check("SENSITIVITY_UNRELATED_ONE_PIXEL_BLOCKER", sensitivity_result(0.2, 0.3, 0.4, rgb, unrelated, owner_margin_pass=True)["status"] == MEASUREMENT_BLOCKER)
    suite.check("SENSITIVITY_SHADOW_OFF_OBSERVATIONAL", "shadow_off" not in sensitivity["shadow_on_medians"] and sensitivity["status"] == "PASS")

    suite.check("OUTER_PREDICATE_LOW_BRANCH", outer_feasible(0.078, 0.1991557292161208) and outer_branch(0.078, 0.1991557292161208) == "LOW")
    suite.check("OUTER_PREDICATE_HIGH_BRANCH", outer_feasible(0.32, 0.1991557292161208) and outer_branch(0.32, 0.1991557292161208) == "HIGH")
    high_values = [0.2950366856, 0.3840860532, 0.4754721832]
    suite.check("OUTER_HIGH_BRANCH_REGRESSION", not outer_feasible(high_values[0], 0.1991557292161208) and outer_feasible(high_values[1], 0.1991557292161208) and outer_feasible(high_values[2], 0.1991557292161208))
    suite.check("OUTER_ACTUAL_HARD_PREDICATES_ONLY", outer_feasible(0.4, 0.2) and not (0.075 <= 0.4 <= 0.0791557292161208))

    good_history = history()
    suite.check("HISTORICAL_SAMPLE_REQUIRED_NON_GATING", historical_record_valid(good_history))
    mislabeled = dict(good_history); mislabeled["gating"] = True
    suite.check("HISTORICAL_SAMPLE_CANNOT_ENTER_CHECKS", not candidate_gate(pass_checks(), True, mislabeled) and candidate_gate(pass_checks(), True, good_history))
    suite.check("HISTORICAL_VALUE_INVARIANCE", candidate_gate(pass_checks(), True, history(0.01, 0.02)) == candidate_gate(pass_checks(), True, history(0.99, 0.98)))

    fresh = {"launches": 0, "index": 0, "records": [], "cache": {}, "candidate_root_empty": True, "diagnostic_counter_separate": True, "historical_run_ids_present": []}
    suite.check("FRESH_CALIBRATION_STATE", fresh_calibration_state_valid(fresh))
    old = dict(fresh); old["historical_run_ids_present"] = ["v1.2.7R1"]
    suite.check("OLD_RUN_RECORD_REJECTED", not fresh_calibration_state_valid(old))
    suite.check("DIAGNOSTIC_CAP_SEPARATE", diagnostic_counters_valid(5, 82) and diagnostic_counters_valid(10, 0, branch_b=True) and not diagnostic_counters_valid(6, 0))

    suite.check("NO_INTERVAL_COMPLETE_TRANSCRIPT_ONLY", no_interval_admissible(no_interval_state()))
    suite.check("NO_INTERVAL_INCOMPLETE_PLAN_REJECTED", not no_interval_admissible(no_interval_state(stage_transcript_complete=False)))
    suite.check("NO_INTERVAL_CAP_BEFORE_COMPLETION_REJECTED", not no_interval_admissible(no_interval_state(cap_reached_before_completion=True)))
    suite.check("NO_INTERVAL_BINDING_FAILURE_REJECTED", not no_interval_admissible(no_interval_state(sensitivity_status=MEASUREMENT_BLOCKER)))
    suite.check("BRANCH_B_DELTA_WHITELIST", branch_b_delta_allowed(["scripts/p1a_world_builder.gd"]) and not branch_b_delta_allowed(["scripts/p1a_world_builder.gd", "world/generated/solid_meshes.json"]))
    suite.check("BRANCH_B_INFLUENCE_SUBSET", influence_subset([(1, 1)], [(1, 1), (2, 2)]) and not influence_subset([(3, 3)], [(1, 1), (2, 2)]))

    metrics = json.loads((root / "director_inputs/v1_2_6_run1_validation_evidence/NATIVE_VISUALS/native-visual-metric-result.json").read_text(encoding="utf-8"))
    rays = json.loads((root / "tests/fixtures/v1_2_6_ray_classification_baseline.json").read_text(encoding="utf-8"))
    check_ids = [item["id"] for item in metrics["checks"]]
    # Ray IDs are scoped by capture view in the frozen fixture.  Qualify them
    # before asserting the global 14-record cardinality so repeated semantic
    # labels across A1 and free-roam remain distinct evidence records.
    ray_ids = [f"A1_FAMILIARIZATION:{item}" for item in rays["a1"]["records"]]
    ray_ids += [f"FREE_ROAM:{item}" for item in rays["free_roam"]["records"]]
    suite.check("CHECK_AND_RAY_CARDINALITY_FROZEN", acceptance_cardinality(check_ids, ray_ids))

    terminals = json.loads((root / "tests/fixtures/v1_2_8_raster_ownership_contract.json").read_text(encoding="utf-8"))["terminal_statuses"]
    suite.check("TERMINAL_FINALIZER_ALL_PATHS", all(terminal_actions(status).index("fresh_extract_verify") < terminal_actions(status).index("cleanup") for status in terminals))
    suite.check("DIAGNOSTIC_OVERRIDE_EXCLUDED", not delivery_path_allowed(".godot/cache") and not delivery_path_allowed("evidence/ownership-pass-001.png") and delivery_path_allowed("tests/fixtures/v1_2_8_visual_acceptance_selected.json"))
    order = prepared_session_write_order()
    suite.check("PREPARED_SESSION_COMPLETE_INVENTORY", order.index("PREPARED_RESULT.json") < order.index("SESSION_SHA256SUMS.txt") < order.index("PACKAGE") < order.index("FRESH_EXTRACT_VERIFY"))
    terminal = automation_terminal()
    suite.check("AUTOMATION_SUCCESS_DOES_NOT_AUTHORIZE_HUMAN", terminal["status"] == AUTOMATION_PASS and terminal["human_attempts"] == 0 and terminal["human_world_gate"] == "NOT PERFORMED" and terminal["P1B"] == "FROZEN" and terminal["human_testing_authorized"] is False)

    registered = json.loads((root / "tests/fixtures/v1_2_8_semantic_regression_contract.json").read_text(encoding="utf-8"))["required_cases"]
    expected_ids = [item["id"] for item in registered]
    observed_ids = [item["id"] for item in suite.results]
    inventory_errors: list[str] = []
    if observed_ids != expected_ids:
        inventory_errors.append("implemented case order/IDs do not exactly match contract")
    failures = [item for item in suite.results if item["status"] != "PASS"]
    return {
        "schema": "district_zero.p1a.v1_2_8.semantic_test_result.v1",
        "status": "PASS" if not failures and not inventory_errors else "FAIL",
        "case_count": len(suite.results),
        "pass_count": len(suite.results) - len(failures),
        "failure_count": len(failures) + len(inventory_errors),
        "failures": failures,
        "inventory_errors": inventory_errors,
        "cases": suite.results,
        "godot_processes_launched": 0,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=str(ROOT_DEFAULT))
    args = parser.parse_args()
    result = execute(pathlib.Path(args.root).resolve())
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
