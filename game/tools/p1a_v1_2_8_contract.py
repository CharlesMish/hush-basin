#!/usr/bin/env python3
"""Pure v1.2.8 raster-ownership and continuation contract behavior."""
from __future__ import annotations

import inspect
import math
from collections import deque
from typing import Any, Iterable, Mapping

WIDTH = 1280
HEIGHT = 720
ORIGINAL_CENTER = (256, 244)
TARGET_SOURCE = "OUTER_CLOSURE_MASK"
TARGET_NODE = "/root/DistrictZeroP1A/World/MESH_OUTER_CLOSURE_Visual"
TARGET_FACE = "SIDE"
HARNESS_BLOCKER = "BLOCKED/NOT TESTABLE — HARNESS"
MEASUREMENT_BLOCKER = "BLOCKED/NOT TESTABLE — MEASUREMENT BINDING"
NO_SAMPLE = "DIRECTOR DECISION REQUIRED — NO ROBUST OUTER-CLOSURE SAMPLE"
NO_INTERVAL = "NO_PRESENTATION_ONLY_INTERVAL"
AUTOMATION_PASS = "AUTOMATION PASS — PREPARED A1 SESSION READY FOR DIRECTOR REVIEW"


def normalized_to_pixel(normalized: tuple[float, float] | list[float], width: int = WIDTH, height: int = HEIGHT) -> tuple[int, int]:
    """The inherited positive-floor conversion, made explicit and testable."""
    return (
        min(width - 1, max(0, math.floor(float(normalized[0]) * width))),
        min(height - 1, max(0, math.floor(float(normalized[1]) * height))),
    )


def pixel_center_normalized(center: tuple[int, int], width: int = WIDTH, height: int = HEIGHT) -> tuple[float, float]:
    return ((center[0] + 0.5) / width, (center[1] + 0.5) / height)


def footprint(center: tuple[int, int], radius: int, width: int = WIDTH, height: int = HEIGHT) -> list[tuple[int, int]]:
    x0, y0 = center
    points = [(x, y) for y in range(y0 - radius, y0 + radius + 1) for x in range(x0 - radius, x0 + radius + 1)]
    if any(x < 0 or y < 0 or x >= width or y >= height for x, y in points):
        return []
    return points


def _exact_target(record: Mapping[str, Any]) -> bool:
    return (
        record.get("decode_status") == "EXACT"
        and record.get("source_geometry_id") == TARGET_SOURCE
        and record.get("render_node") == TARGET_NODE
        and record.get("face_class") == TARGET_FACE
        and isinstance(record.get("connected_side_component_id"), str)
        and bool(record.get("connected_side_component_id"))
    )


def owner_key(record: Mapping[str, Any]) -> tuple[Any, ...] | None:
    if record.get("decode_status") != "EXACT":
        return None
    return (
        record.get("source_geometry_id"),
        record.get("render_node"),
        record.get("face_class"),
        record.get("connected_side_component_id"),
        record.get("visible_component_id"),
    )


def assign_visible_components(owner_map: Mapping[tuple[int, int], Mapping[str, Any]]) -> dict[tuple[int, int], dict[str, Any]]:
    """Assign deterministic four-connected IDs without consulting image values."""
    output = {point: dict(record) for point, record in owner_map.items()}
    unseen = {point for point, record in output.items() if _exact_target(record)}
    groups: list[list[tuple[int, int]]] = []
    while unseen:
        seed = min(unseen, key=lambda p: (p[1], p[0]))
        source_component = output[seed]["connected_side_component_id"]
        queue: deque[tuple[int, int]] = deque([seed])
        unseen.remove(seed)
        group: list[tuple[int, int]] = []
        while queue:
            point = queue.popleft()
            group.append(point)
            x, y = point
            for neighbor in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
                if neighbor in unseen and output[neighbor].get("connected_side_component_id") == source_component:
                    unseen.remove(neighbor)
                    queue.append(neighbor)
        groups.append(sorted(group, key=lambda p: (p[1], p[0])))
    groups.sort(key=lambda points: (points[0][1], points[0][0]))
    per_source: dict[str, int] = {}
    for points in groups:
        source_component = str(output[points[0]]["connected_side_component_id"])
        per_source[source_component] = per_source.get(source_component, 0) + 1
        visible_id = f"{source_component}:VISIBLE_{per_source[source_component]:03d}"
        for point in points:
            output[point]["visible_component_id"] = visible_id
    return output


def map_complete(owner_map: Mapping[tuple[int, int], Mapping[str, Any]], bounds: tuple[int, int, int, int] = (218, 294, 206, 282)) -> bool:
    xmin, xmax, ymin, ymax = bounds
    expected = {(x, y) for y in range(ymin, ymax + 1) for x in range(xmin, xmax + 1)}
    if set(owner_map) != expected:
        return False
    return all(record.get("decode_status") in {"EXACT", "BACKGROUND", "MIXED"} for record in owner_map.values())


def original_footprint_safe(owner_map: Mapping[tuple[int, int], Mapping[str, Any]]) -> bool:
    points = footprint(ORIGINAL_CENTER, 6)
    records = [owner_map.get(point) for point in points]
    if len(records) != 169 or any(record is None or not _exact_target(record) for record in records):
        return False
    keys = {owner_key(record) for record in records if record is not None}
    return len(keys) == 1


def adjudicate_branch(owner_map: Mapping[tuple[int, int], Mapping[str, Any]], sensitivity_status: str | None) -> dict[str, Any]:
    if not map_complete(owner_map):
        return {"branch": "NONE", "status": HARNESS_BLOCKER}
    if not original_footprint_safe(owner_map):
        return {"branch": "BRANCH_A_SAMPLE_REPLACEMENT", "status": "PASS"}
    if sensitivity_status == "PASS":
        return {"branch": "ORIGINAL_VALID", "status": "PASS"}
    return {"branch": "BRANCH_B_RENDER_CONSUMER_BINDING", "status": "PASS"}


def select_sample(
    owner_map: Mapping[tuple[int, int], Mapping[str, Any]],
    original: tuple[int, int] = ORIGINAL_CENTER,
    width: int = WIDTH,
    height: int = HEIGHT,
) -> dict[str, Any]:
    """Luminance-blind Branch-A selection. The signature intentionally has no raster/metric input."""
    candidates = [
        point
        for point, record in owner_map.items()
        if _exact_target(record) and record.get("visible_component_id")
    ]
    if not candidates:
        return {
            "original_center_px": list(original),
            "intended_component_derivation": None,
            "sorted_eligible": [],
            "selected": None,
            "luminance_inputs_used": False,
            "status": NO_SAMPLE,
        }
    ox, oy = original
    seed = min(candidates, key=lambda p: ((p[0] - ox) ** 2 + (p[1] - oy) ** 2, p[1], p[0]))
    intended = str(owner_map[seed]["visible_component_id"])
    eligible: list[dict[str, Any]] = []
    for y in range(max(0, oy - 32), min(height - 1, oy + 32) + 1):
        for x in range(max(0, ox - 32), min(width - 1, ox + 32) + 1):
            distance = (x - ox) ** 2 + (y - oy) ** 2
            if distance > 1024:
                continue
            points = footprint((x, y), 6, width, height)
            records = [owner_map.get(point) for point in points]
            if len(records) != 169 or any(record is None or not _exact_target(record) for record in records):
                continue
            if any(record.get("visible_component_id") != intended for record in records if record is not None):
                continue
            eligible.append({
                "x": x,
                "y": y,
                "squared_distance": distance,
                "owner_component_id": intended,
                "footprint_owner_count": 169,
            })
    eligible.sort(key=lambda item: (item["squared_distance"], item["y"], item["x"]))
    selected = eligible[0] if eligible else None
    return {
        "original_center_px": list(original),
        "intended_component_derivation": {
            "seed_px": list(seed),
            "seed_squared_distance": (seed[0] - ox) ** 2 + (seed[1] - oy) ** 2,
            "owner_component_id": intended,
            "rule": "nearest exact target SIDE pixel by (squared_distance,y,x), then four-connected component",
        },
        "sorted_eligible": eligible,
        "selected": selected,
        "luminance_inputs_used": False,
        "status": "PASS" if selected is not None else NO_SAMPLE,
    }


def sensitivity_result(
    baseline_y: float,
    midpoint_y: float,
    extreme_y: float,
    baseline_rgb: Iterable[tuple[int, int, int]],
    unrelated_rgb: Iterable[tuple[int, int, int]],
    *,
    owner_margin_pass: bool,
) -> dict[str, Any]:
    base = list(baseline_rgb)
    unrelated = list(unrelated_rgb)
    errors: list[str] = []
    if not owner_margin_pass:
        errors.append("owner/margin failed")
    if not all(math.isfinite(value) for value in (baseline_y, midpoint_y, extreme_y)):
        errors.append("nonfinite target response")
    elif not baseline_y < midpoint_y < extreme_y:
        errors.append("target response is not strictly increasing")
    if len(base) != 81 or len(unrelated) != 81:
        errors.append("corrected patch RGB inventory is not 81")
    elif base != unrelated:
        errors.append("unrelated control changed corrected patch")
    return {
        "status": "PASS" if not errors else MEASUREMENT_BLOCKER,
        "errors": errors,
        "shadow_on_medians": {"baseline": baseline_y, "midpoint": midpoint_y, "extreme": extreme_y},
        "unrelated_patch_exact_equal": base == unrelated and len(base) == 81,
    }


def outer_feasible(y_value: float, ground_y: float, shadow_min: float = 0.075, separation: float = 0.12) -> bool:
    return y_value >= shadow_min and abs(y_value - ground_y) >= separation


def outer_branch(y_value: float, ground_y: float, separation: float = 0.12) -> str | None:
    if y_value <= ground_y - separation:
        return "LOW"
    if y_value >= ground_y + separation:
        return "HIGH"
    return None


def outer_margin(y_value: float, ground_y: float, shadow_min: float = 0.075, separation: float = 0.12) -> float:
    branch = outer_branch(y_value, ground_y, separation)
    if branch == "LOW":
        return min(y_value - shadow_min, ground_y - separation - y_value)
    if branch == "HIGH":
        return min(y_value - shadow_min, y_value - (ground_y + separation))
    return -min(abs(y_value - (ground_y - separation)), abs(y_value - (ground_y + separation)))


def historical_record_valid(record: Mapping[str, Any]) -> bool:
    return (
        record.get("integer_center_px") == [256, 244]
        and record.get("normalized") == [0.2, 0.34]
        and record.get("label") == "v1.2.7R1_old_sample_historical_non_gating"
        and record.get("gating") is False
        and all(isinstance(record.get(key), (int, float)) for key in ("shadow_on_Y", "shadow_off_Y"))
    )


def candidate_gate(checks: Iterable[Mapping[str, Any]], ray_pass: bool, historical: Mapping[str, Any]) -> bool:
    """History is required provenance, but its numerical values are never a gate."""
    check_list = list(checks)
    return historical_record_valid(historical) and len(check_list) == 21 and all(item.get("pass") is True for item in check_list) and ray_pass


def fresh_calibration_state_valid(state: Mapping[str, Any]) -> bool:
    return (
        state.get("launches") == 0
        and state.get("index") == 0
        and state.get("records") == []
        and state.get("cache") == {}
        and state.get("candidate_root_empty") is True
        and state.get("diagnostic_counter_separate") is True
        and state.get("historical_run_ids_present") == []
    )


def diagnostic_counters_valid(diagnostic_launches: int, calibration_launches: int, *, branch_b: bool = False) -> bool:
    diagnostic_cap = 10 if branch_b else 5
    return 0 <= diagnostic_launches <= diagnostic_cap and 0 <= calibration_launches <= 82


def no_interval_admissible(state: Mapping[str, Any]) -> bool:
    return (
        state.get("ownership_status") == "PASS"
        and state.get("sensitivity_status") == "PASS"
        and state.get("semantic_status") == "PASS"
        and state.get("stage_transcript_complete") is True
        and state.get("all_records_executed_complete") is True
        and state.get("all_records_bound_v1_2_8") is True
        and state.get("eligible_count") == 0
        and state.get("cap_reached_before_completion") is False
    )


def branch_b_delta_allowed(changed_paths: Iterable[str], binding_path: str = "scripts/p1a_world_builder.gd") -> bool:
    return set(changed_paths) <= {binding_path}


def influence_subset(target_changed: Iterable[tuple[int, int]], target_owner: Iterable[tuple[int, int]]) -> bool:
    return set(target_changed) <= set(target_owner)


def acceptance_cardinality(check_ids: Iterable[str], ray_ids: Iterable[str]) -> bool:
    checks = list(check_ids)
    rays = list(ray_ids)
    return len(checks) == 21 and len(set(checks)) == 21 and len(rays) == 14 and len(set(rays)) == 14


def terminal_actions(status: str) -> list[str]:
    _ = status
    return ["freeze", "write_result", "inventory", "package", "fresh_extract_verify", "cleanup"]


def delivery_path_allowed(path: str) -> bool:
    parts = path.replace("\\", "/").split("/")
    name = parts[-1]
    return not (
        any(part in {".godot", "__MACOSX", "__pycache__"} for part in parts)
        or name == ".DS_Store"
        or name.startswith("._")
        or name.endswith((".pyc", ".pyo", ".zip"))
        or "ownership-pass" in name
        or "diagnostic_override" in name
    )


def prepared_session_write_order() -> list[str]:
    return ["PREPARED_RESULT.json", "SESSION_SHA256SUMS.txt", "PACKAGE", "FRESH_EXTRACT_VERIFY"]


def automation_terminal() -> dict[str, Any]:
    return {
        "status": AUTOMATION_PASS,
        "human_attempts": 0,
        "human_world_gate": "NOT PERFORMED",
        "P1B": "FROZEN",
        "human_testing_authorized": False,
    }


def selector_parameter_names() -> list[str]:
    return list(inspect.signature(select_sample).parameters)
