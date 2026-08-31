#!/usr/bin/env python3
"""v1.2.8 native visual metrics with an integer-authoritative target sample."""
from __future__ import annotations

import argparse
import json
import pathlib
import statistics
from typing import Any

from p1a_v1_2_7_metrics import _linear, _read_png_rgb8


def patch_rgb_pixel(path: pathlib.Path, center: tuple[int, int] | list[int], radius: int = 4) -> list[tuple[int, int, int]]:
    width, height, rows = _read_png_rgb8(path)
    cx, cy = int(center[0]), int(center[1])
    if cx - radius < 0 or cy - radius < 0 or cx + radius >= width or cy + radius >= height:
        raise ValueError(f"{path}: sample patch clipped at {center}")
    pixels: list[tuple[int, int, int]] = []
    for y in range(cy - radius, cy + radius + 1):
        row = rows[y]
        for x in range(cx - radius, cx + radius + 1):
            offset = x * 3
            pixels.append((row[offset], row[offset + 1], row[offset + 2]))
    expected = (radius * 2 + 1) ** 2
    if len(pixels) != expected:
        raise ValueError(f"{path}: expected {expected} pixels, observed {len(pixels)}")
    return pixels


def rgb_y(pixel: tuple[int, int, int]) -> float:
    return 0.2126 * _linear(pixel[0]) + 0.7152 * _linear(pixel[1]) + 0.0722 * _linear(pixel[2])


def patch_y_pixel(path: pathlib.Path, center: tuple[int, int] | list[int]) -> float:
    return statistics.median(rgb_y(pixel) for pixel in patch_rgb_pixel(path, center))


def _floor_center(normalized: list[float], width: int = 1280, height: int = 720) -> tuple[int, int]:
    return (
        min(width - 1, max(0, int(float(normalized[0]) * width))),
        min(height - 1, max(0, int(float(normalized[1]) * height))),
    )


def _center(acceptance: dict[str, Any], view: str, name: str) -> tuple[int, int]:
    integer = acceptance.get("integer_samples", {}).get(view, {}).get(name)
    if integer is not None:
        return int(integer[0]), int(integer[1])
    return _floor_center(acceptance["samples"][view][name])


def compute(acceptance: dict[str, Any], images: dict[str, pathlib.Path]) -> dict[str, Any]:
    samples = acceptance["samples"]
    thresholds = acceptance["hard_thresholds"]
    views: dict[str, Any] = {}
    for view in ("FREE_ROAM", "A1_FAMILIARIZATION"):
        on = images[f"{view}:on"]
        off = images[f"{view}:off"]
        records: dict[str, Any] = {}
        for name in samples[view]:
            center = _center(acceptance, view, name)
            on_y = patch_y_pixel(on, center)
            off_y = patch_y_pixel(off, center)
            records[name] = {
                "integer_center_px": list(center),
                "shadow_on_Y": on_y,
                "shadow_off_Y": off_y,
                "on_to_off_ratio": on_y / off_y if off_y > 0.0 else float("inf"),
            }
        views[view] = records
    checks: list[dict[str, Any]] = []

    def add(check_id: str, observed: float, passed: bool) -> None:
        checks.append({"id": check_id, "observed": observed, "pass": bool(passed)})

    free = views["FREE_ROAM"]
    background_y = free["background"]["shadow_on_Y"]
    for name in ("aperture_ground", "left_ground", "right_ground"):
        difference = free[name]["shadow_on_Y"] - background_y
        free[name]["minus_background_Y"] = difference
        add(f"FREE_ROAM:{name}:minus_background", difference, difference >= thresholds["each_ground_minus_same_view_background_Y_min"])
    for name in ("aperture_ground", "left_ground", "right_ground"):
        add(f"FREE_ROAM:{name}:shadow_on_min", free[name]["shadow_on_Y"], free[name]["shadow_on_Y"] >= thresholds["shadow_on_Y_min"])
        add(f"FREE_ROAM:{name}:shadow_ratio", free[name]["on_to_off_ratio"], free[name]["on_to_off_ratio"] >= thresholds["shadow_on_to_shadow_off_Y_ratio_min"])
    a1 = views["A1_FAMILIARIZATION"]
    background_y = a1["background"]["shadow_on_Y"]
    for name in ("between_structures_ground", "right_ground"):
        difference = a1[name]["shadow_on_Y"] - background_y
        a1[name]["minus_background_Y"] = difference
        add(f"A1_FAMILIARIZATION:{name}:minus_background", difference, difference >= thresholds["each_ground_minus_same_view_background_Y_min"])
    for name in ("between_structures_ground", "left_outer_closure", "right_core_wall", "right_ground"):
        add(f"A1_FAMILIARIZATION:{name}:shadow_on_min", a1[name]["shadow_on_Y"], a1[name]["shadow_on_Y"] >= thresholds["shadow_on_Y_min"])
        add(f"A1_FAMILIARIZATION:{name}:shadow_ratio", a1[name]["on_to_off_ratio"], a1[name]["on_to_off_ratio"] >= thresholds["shadow_on_to_shadow_off_Y_ratio_min"])
    left = abs(a1["between_structures_ground"]["shadow_on_Y"] - a1["left_outer_closure"]["shadow_on_Y"])
    right = abs(a1["right_core_wall"]["shadow_on_Y"] - a1["right_ground"]["shadow_on_Y"])
    a1["obstacle_separation"] = {"left_absolute_Y": left, "right_absolute_Y": right}
    add("A1:left_obstacle_separation", left, left >= thresholds["left_outer_closure_minus_adjacent_ground_absolute_Y_min"])
    add("A1:right_obstacle_separation", right, right >= thresholds["right_core_wall_minus_adjacent_ground_absolute_Y_min"])
    old_center = (256, 244)
    historical = {
        "integer_center_px": [256, 244],
        "normalized": [0.2, 0.34],
        "shadow_on_Y": patch_y_pixel(images["A1_FAMILIARIZATION:on"], old_center),
        "shadow_off_Y": patch_y_pixel(images["A1_FAMILIARIZATION:off"], old_center),
        "label": "v1.2.7R1_old_sample_historical_non_gating",
        "gating": False,
    }
    return {
        "schema": "district_zero.p1a.v1_2_8.native_visual_metric_result.v1",
        "status": "PASS" if all(check["pass"] for check in checks) else "FAIL",
        "checks": checks,
        "views": views,
        "historical_non_gating": historical,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--acceptance", required=True)
    parser.add_argument("--image-dir", required=True)
    parser.add_argument("--output")
    args = parser.parse_args()
    acceptance = json.loads(pathlib.Path(args.acceptance).read_text(encoding="utf-8"))
    directory = pathlib.Path(args.image_dir)
    images = {
        "FREE_ROAM:on": directory / "free-roam-after-native.png",
        "FREE_ROAM:off": directory / "free-roam-after-shadow-off-reference.png",
        "A1_FAMILIARIZATION:on": directory / "a1-after-native.png",
        "A1_FAMILIARIZATION:off": directory / "a1-after-shadow-off-reference.png",
    }
    result = compute(acceptance, images)
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        pathlib.Path(args.output).write_text(text, encoding="utf-8")
    print(text, end="")
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
