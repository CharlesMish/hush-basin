#!/usr/bin/env python3
"""Offline, deterministic decoding for the v1.2.8 ownership diagnostic."""
from __future__ import annotations

import hashlib
import json
import math
import pathlib
import statistics
import struct
import zlib
from typing import Any, Iterable

from p1a_v1_2_7_metrics import _linear, _read_png_rgb8
from p1a_v1_2_8_contract import (
    ORIGINAL_CENTER,
    TARGET_NODE,
    TARGET_SOURCE,
    adjudicate_branch,
    assign_visible_components,
    footprint,
    select_sample,
    sensitivity_result,
)

WIDTH = 1280
HEIGHT = 720
DECODE_BOUNDS = (218, 294, 206, 282)


def sha256(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def pixel(rows: list[bytes], x: int, y: int) -> tuple[int, int, int]:
    offset = x * 3
    return tuple(rows[y][offset:offset + 3])  # type: ignore[return-value]


def patch_rgb(path: pathlib.Path, center: tuple[int, int], radius: int = 4) -> list[tuple[int, int, int]]:
    width, height, rows = _read_png_rgb8(path)
    if (width, height) != (WIDTH, HEIGHT):
        raise ValueError(f"{path}: expected {WIDTH}x{HEIGHT} RGB8")
    points = footprint(center, radius)
    if len(points) != (radius * 2 + 1) ** 2 or any(not (0 <= x < width and 0 <= y < height) for x, y in points):
        raise ValueError("metric patch clipped")
    return [pixel(rows, x, y) for x, y in points]


def median_y(path: pathlib.Path, center: tuple[int, int], radius: int = 4) -> float:
    values = [0.2126 * _linear(r) + 0.7152 * _linear(g) + 0.0722 * _linear(b) for r, g, b in patch_rgb(path, center, radius)]
    return statistics.median(values)


def _png_chunk(kind: bytes, data: bytes) -> bytes:
    return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)


def write_rgb8(path: pathlib.Path, width: int, height: int, rows: Iterable[bytes]) -> None:
    raw = b"".join(b"\x00" + row for row in rows)
    payload = b"\x89PNG\r\n\x1a\n"
    payload += _png_chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
    payload += _png_chunk(b"IDAT", zlib.compress(raw, 9))
    payload += _png_chunk(b"IEND", b"")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(payload)


def annotated_crops(image_path: pathlib.Path, selected: tuple[int, int], output_dir: pathlib.Path) -> dict[str, Any]:
    """Write literal RGB8 crops with non-gating diagnostic rectangles."""
    width, height, rows = _read_png_rgb8(image_path)
    if (width, height) != (WIDTH, HEIGHT):
        raise ValueError("annotated-crop input differs from native viewport")

    def make(name: str, bounds: tuple[int, int, int, int]) -> dict[str, Any]:
        xmin, xmax, ymin, ymax = bounds
        crop = [bytearray(rows[y][xmin * 3:(xmax + 1) * 3]) for y in range(ymin, ymax + 1)]
        for center, color in ((ORIGINAL_CENTER, (255, 48, 48)), (selected, (48, 255, 96))):
            for radius in (4, 6):
                x0, x1 = center[0] - radius, center[0] + radius
                y0, y1 = center[1] - radius, center[1] + radius
                for x, y in [(x, y0) for x in range(x0, x1 + 1)] + [(x, y1) for x in range(x0, x1 + 1)] + [(x0, y) for y in range(y0, y1 + 1)] + [(x1, y) for y in range(y0, y1 + 1)]:
                    if xmin <= x <= xmax and ymin <= y <= ymax:
                        offset = (x - xmin) * 3
                        crop[y - ymin][offset:offset + 3] = bytes(color)
        path = output_dir / name
        write_rgb8(path, xmax - xmin + 1, ymax - ymin + 1, [bytes(row) for row in crop])
        return {"path": path.name, "sha256": sha256(path), "bounds_inclusive": {"x": [xmin, xmax], "y": [ymin, ymax]}, "legend": {"red": "historical non-gating center footprints", "green": "selected gating center footprints"}}

    return {
        "search_region": make("annotated-search-region.png", DECODE_BOUNDS),
        "original_region": make("annotated-original-region.png", (240, 272, 228, 260)),
    }


def difference_mask(reference: pathlib.Path, candidate: pathlib.Path, output: pathlib.Path, selected: tuple[int, int]) -> dict[str, Any]:
    width, height, base = _read_png_rgb8(reference)
    cw, ch, other = _read_png_rgb8(candidate)
    if (width, height, cw, ch) != (WIDTH, HEIGHT, WIDTH, HEIGHT):
        raise ValueError("difference-mask input dimensions differ from authority")
    changed: list[tuple[int, int]] = []
    out_rows: list[bytes] = []
    for y in range(height):
        row = bytearray(width * 3)
        for x in range(width):
            differs = pixel(base, x, y) != pixel(other, x, y)
            if differs:
                changed.append((x, y))
                row[x * 3:x * 3 + 3] = b"\xff\xff\xff"
        out_rows.append(bytes(row))
    write_rgb8(output, width, height, out_rows)
    bbox = None
    if changed:
        bbox = [min(x for x, _ in changed), min(y for _, y in changed), max(x for x, _ in changed), max(y for _, y in changed)]
    corrected = set(footprint(selected, 4))
    original = set(footprint(ORIGINAL_CENTER, 4))
    changed_set = set(changed)
    return {
        "raw_mask_path": output.name,
        "sha256": sha256(output),
        "changed_pixel_count": len(changed),
        "bounding_box_or_null": bbox,
        "corrected_patch_changed_count": len(corrected & changed_set),
        "original_patch_changed_count": len(original & changed_set),
    }


def _component_map(solid_path: pathlib.Path) -> tuple[list[str], list[dict[str, Any]], dict[str, Any]]:
    artifact = json.loads(solid_path.read_text(encoding="utf-8"))
    record = artifact["meshes"]["MESH_OUTER_CLOSURE"]
    vertices = record["vertices_xyz_m"]
    parent = list(range(len(vertices)))

    def find(value: int) -> int:
        while parent[value] != value:
            parent[value] = parent[parent[value]]
            value = parent[value]
        return value

    def union(a: int, b: int) -> None:
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[max(ra, rb)] = min(ra, rb)

    for triangle in record["triangles"]:
        a, b, c = map(int, triangle["indices"])
        union(a, b)
        union(b, c)
    roots = sorted({find(index) for index in range(len(vertices))})
    names = {root: f"OUTER_CLOSURE_MASK_C{index + 1:02d}" for index, root in enumerate(roots)}
    top = [triangle for triangle in record["triangles"] if triangle["surface"] == "TOP"]
    shape_components = [names[find(int(triangle["indices"][0]))] for triangle in top]
    return shape_components, top, record


def decode_ownership(capture: pathlib.Path, output: pathlib.Path, solid_path: pathlib.Path) -> dict[str, Any]:
    probe_path = capture / "ownership_probe_result.json"
    probe = json.loads(probe_path.read_text(encoding="utf-8"))
    if probe.get("status") != "PASS" or probe.get("engine_identity") != "4.7.1.stable.official.a13da4feb":
        raise ValueError("ownership probe did not emit an exact-engine PASS")
    owners = probe.get("owners", [])
    if probe.get("owner_count") != len(owners) or not owners:
        raise ValueError("ownership owner inventory is incoherent")
    low_path = capture / probe["low_reference"]
    width, height, low = _read_png_rgb8(low_path)
    if (width, height) != (WIDTH, HEIGHT):
        raise ValueError("ownership low reference is not native RGB8")
    high_rows: list[list[bytes]] = []
    high_identities: list[dict[str, Any]] = []
    for owner in owners:
        index = int(owner["owner_index"])
        path = capture / (probe["high_pass_pattern"] % index)
        iw, ih, rows = _read_png_rgb8(path)
        if (iw, ih) != (WIDTH, HEIGHT):
            raise ValueError(f"owner pass {index} is not native RGB8")
        high_rows.append(rows)
        high_identities.append({"owner_index": index, "path": path.name, "sha256": sha256(path)})
    shape_components, top_triangles, solid_record = _component_map(solid_path)
    xmin, xmax, ymin, ymax = DECODE_BOUNDS
    decoded: dict[tuple[int, int], dict[str, Any]] = {}
    for y in range(ymin, ymax + 1):
        for x in range(xmin, xmax + 1):
            base = pixel(low, x, y)
            changed = [index for index, rows in enumerate(high_rows) if pixel(rows, x, y) != base]
            ray = probe["ray_grid"][f"{x},{y}"]
            record: dict[str, Any] = {
                "x": x,
                "y": y,
                "decode_status": "BACKGROUND" if not changed else "MIXED_OR_UNSAFE" if len(changed) != 1 else "EXACT",
                "source_geometry_id": None,
                "render_node": None,
                "face_class": None,
                "connected_side_component_id": None,
                "side_plane_id_or_null": None,
                "triangle_id_or_null": None,
                "triangle_null_reason": "raster pass identifies a surface owner, not one unambiguous source triangle",
                "changed_owner_indices": changed,
                "physics_ray": ray,
            }
            if len(changed) == 1:
                owner = owners[changed[0]]
                record["source_geometry_id"] = owner.get("source_geometry_id")
                record["render_node"] = owner.get("render_node")
                if owner.get("source_geometry_id") == TARGET_SOURCE and owner.get("render_node") == TARGET_NODE:
                    normal = ray.get("normal")
                    side = isinstance(normal, list) and len(normal) == 3 and abs(float(normal[1])) <= 0.5
                    shape = int(ray.get("shape_index", -1))
                    if ray.get("source_geometry_id") == TARGET_SOURCE and side and 0 <= shape < len(shape_components):
                        record["face_class"] = "SIDE"
                        record["connected_side_component_id"] = shape_components[shape]
                        record["side_plane_id_or_null"] = f"TOP_PRISM_{shape:05d}_SIDE_HIT"
                        record["source_top_triangle_indices"] = top_triangles[shape]["indices"]
                    else:
                        record["decode_status"] = "MIXED_OR_UNSAFE"
                        record["triangle_null_reason"] = "raster target owner and pixel-center physics owner/face do not agree"
            decoded[(x, y)] = record
    decoded = assign_visible_components(decoded)
    selection = select_sample(decoded)
    branch_seed = adjudicate_branch(decoded, "PASS")
    original_table = [decoded[point] for point in footprint(ORIGINAL_CENTER, 4)]
    original_margin = [decoded[point] for point in footprint(ORIGINAL_CENTER, 6)]
    different = [
        ((x - ORIGINAL_CENTER[0]) ** 2 + (y - ORIGINAL_CENTER[1]) ** 2, x, y, value["decode_status"], value.get("source_geometry_id"))
        for (x, y), value in decoded.items()
        if not (
            value.get("decode_status") == "EXACT"
            and value.get("source_geometry_id") == TARGET_SOURCE
            and value.get("render_node") == TARGET_NODE
            and value.get("face_class") == "SIDE"
        )
    ]
    different.sort()
    maximum_radius = -1
    for radius in range(0, 39):
        points = footprint(ORIGINAL_CENTER, radius)
        if any(point not in decoded or decoded[point].get("decode_status") != "EXACT" or decoded[point].get("source_geometry_id") != TARGET_SOURCE or decoded[point].get("render_node") != TARGET_NODE or decoded[point].get("face_class") != "SIDE" for point in points):
            break
        maximum_radius = radius
    serial_pixels = [decoded[(x, y)] for y in range(ymin, ymax + 1) for x in range(xmin, xmax + 1)]
    result = {
        "schema": "district_zero.p1a.v1_2_8.ownership_diagnostic.v1",
        "status": "PASS",
        "probe_result_sha256": sha256(probe_path),
        "low_reference": {"path": low_path.name, "sha256": sha256(low_path)},
        "high_passes": high_identities,
        "decoded_bounds_inclusive": {"x": [xmin, xmax], "y": [ymin, ymax]},
        "decoded_pixel_count": len(serial_pixels),
        "pixels": serial_pixels,
        "original_81_pixel_table": original_table,
        "original_169_footprint": original_margin,
        "nearest_different_or_unsafe_owner": None if not different else {"squared_distance": different[0][0], "x": different[0][1], "y": different[0][2], "decode_status": different[0][3], "source_geometry_id": different[0][4]},
        "maximum_all_target_chebyshev_radius": maximum_radius,
        "selection_transcript": selection,
        "pre_sensitivity_branch": branch_seed,
        "supplemental_rays": probe.get("supplemental_rays"),
        "canonical_solid_arrays_sha256": solid_record.get("arrays_sha256"),
        "component_stats": solid_record.get("component_stats"),
        "luminance_inputs_used_for_selection": False,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result


def build_sensitivity(case_dirs: dict[str, pathlib.Path], center: tuple[int, int], output_dir: pathlib.Path) -> dict[str, Any]:
    paths = {case: directory / "a1-after-native.png" for case, directory in case_dirs.items()}
    off_paths = {case: directory / "a1-after-shadow-off-reference.png" for case, directory in case_dirs.items()}
    medians = {case: median_y(path, center) for case, path in paths.items()}
    off_medians = {case: median_y(path, center) for case, path in off_paths.items()}
    baseline_patch = patch_rgb(paths["BASELINE"], center)
    unrelated_patch = patch_rgb(paths["UNRELATED_EXTREME"], center)
    semantic = sensitivity_result(
        medians["BASELINE"],
        medians["TARGET_MIDPOINT"],
        medians["TARGET_EXTREME"],
        baseline_patch,
        unrelated_patch,
        owner_margin_pass=True,
    )
    masks = {
        "BASELINE_TO_TARGET_MIDPOINT": difference_mask(paths["BASELINE"], paths["TARGET_MIDPOINT"], output_dir / "baseline-to-target-midpoint-mask.png", center),
        "BASELINE_TO_TARGET_EXTREME": difference_mask(paths["BASELINE"], paths["TARGET_EXTREME"], output_dir / "baseline-to-target-extreme-mask.png", center),
        "BASELINE_TO_UNRELATED_EXTREME": difference_mask(paths["BASELINE"], paths["UNRELATED_EXTREME"], output_dir / "baseline-to-unrelated-extreme-mask.png", center),
    }
    result = {
        "schema": "district_zero.p1a.v1_2_8.sensitivity_result.v1",
        "status": semantic["status"],
        "selected_integer_center_px": list(center),
        "shadow_on_medians": medians,
        "shadow_off_medians": off_medians,
        "strict_target_relation": medians["BASELINE"] < medians["TARGET_MIDPOINT"] < medians["TARGET_EXTREME"],
        "unrelated_patch_exact_rgb8_equality": baseline_patch == unrelated_patch,
        "unrelated_patch_mismatch_count": sum(a != b for a, b in zip(baseline_patch, unrelated_patch)),
        "masks": masks,
        "semantic_adjudication": semantic,
    }
    path = output_dir / "sensitivity_result.json"
    path.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result
