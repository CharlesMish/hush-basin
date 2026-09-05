#!/usr/bin/env python3
"""Compare static GLB world vertices to canonical poses using direct Euler matrices.

The exporter builds YXZ quaternions. This check independently composes three
axis matrices, traverses both hierarchies and compares every mesh vertex. It also
checks exported winding against the supplied outward normals. This is geometry
interchange verification, not native Godot execution or collision validation.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def multiply(a: list, b: list) -> list:
    return [[sum(a[row][k] * b[k][col] for k in range(4)) for col in range(4)] for row in range(4)]


def point(matrix: list, vertex: list) -> list:
    return [sum(matrix[row][axis] * vertex[axis] for axis in range(3)) + matrix[row][3] for row in range(3)]


def euler_matrix(position: list, rotation: list) -> list:
    x, y, z = map(math.radians, rotation)
    sx, cx, sy, cy, sz, cz = math.sin(x), math.cos(x), math.sin(y), math.cos(y), math.sin(z), math.cos(z)
    rx = [[1, 0, 0, 0], [0, cx, -sx, 0], [0, sx, cx, 0], [0, 0, 0, 1]]
    ry = [[cy, 0, sy, 0], [0, 1, 0, 0], [-sy, 0, cy, 0], [0, 0, 0, 1]]
    rz = [[cz, -sz, 0, 0], [sz, cz, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]
    matrix = multiply(multiply(ry, rx), rz)
    for axis in range(3):
        matrix[axis][3] = position[axis]
    return matrix


def quaternion_matrix(position: list, q: list) -> list:
    x, y, z, w = q
    return [[1 - 2 * (y*y + z*z), 2 * (x*y - z*w), 2 * (x*z + y*w), position[0]],
            [2 * (x*y + z*w), 1 - 2 * (x*x + z*z), 2 * (y*z - x*w), position[1]],
            [2 * (x*z - y*w), 2 * (y*z + x*w), 1 - 2 * (x*x + y*y), position[2]],
            [0, 0, 0, 1]]


def inspect_glb(path: Path, source: dict, source_sha: str) -> dict:
    filename = path.name
    payload = path.read_bytes()
    magic, version, length = struct.unpack_from("<4sII", payload)
    assert (magic, version, length) == (b"glTF", 2, len(payload))
    json_size, kind = struct.unpack_from("<I4s", payload, 12)
    assert kind == b"JSON"
    gltf = json.loads(payload[20:20 + json_size])
    binary_size, binary_kind = struct.unpack_from("<I4s", payload, 20 + json_size)
    assert binary_kind == b"BIN\x00"
    binary = payload[28 + json_size:]
    assert len(binary) == binary_size
    extras = gltf["asset"]["extras"]
    assert extras["source_sha256"] == source_sha, "Export source hash differs from canonical input"
    amount = extras["form_amount"]

    def values(index: int) -> list:
        accessor = gltf["accessors"][index]
        view = gltf["bufferViews"][accessor["bufferView"]]
        components = {"VEC3": 3, "SCALAR": 1}[accessor["type"]]
        code = {5126: "f", 5125: "I"}[accessor["componentType"]]
        count = accessor["count"] * components
        offset = view.get("byteOffset", 0) + accessor.get("byteOffset", 0)
        flat = struct.unpack_from("<" + code * count, binary, offset)
        return [list(flat[i:i + components]) for i in range(0, count, components)] if components > 1 else list(flat)

    authored = {node["path"]: copy.deepcopy(node) for node in source["nodes"]}
    for channel in source["pose_channels"]:
        t = min(1, max(0, (amount - channel["start"]) / (channel["end"] - channel["start"])))
        delta = channel["travel"] * (3 * t * t - 2 * t * t * t)
        authored[channel["path"]][channel["property"]][channel["component"]] += delta
    source_matrices = {}

    def source_world(path: str) -> list:
        if path not in source_matrices:
            node = authored[path]
            matrix = euler_matrix(node.get("position", [0, 0, 0]), node.get("rotation_degrees", [0, 0, 0]))
            if node.get("parent") not in (None, ".", ""):
                matrix = multiply(source_world(node["parent"]), matrix)
            source_matrices[path] = matrix
        return source_matrices[path]

    parent_by_index = {}
    for i, node in enumerate(gltf["nodes"]):
        for child in node.get("children", []):
            assert child not in parent_by_index
            parent_by_index[child] = i
    export_matrices = {}

    def export_world(index: int) -> list:
        if index not in export_matrices:
            node = gltf["nodes"][index]
            assert "scale" not in node and "matrix" not in node
            matrix = quaternion_matrix(node.get("translation", [0, 0, 0]), node.get("rotation", [0, 0, 0, 1]))
            if index in parent_by_index:
                matrix = multiply(export_world(parent_by_index[index]), matrix)
            export_matrices[index] = matrix
        return export_matrices[index]

    maximum = 0.0
    comparisons = 0
    winding_checks = 0
    paths = set()
    for index, node in enumerate(gltf["nodes"]):
        path = node["extras"]["native_node_path"]
        assert path not in paths
        paths.add(path)
        if "mesh" not in node:
            continue
        native = authored[path]
        primitive = gltf["meshes"][node["mesh"]]["primitives"][0]
        vertices = values(primitive["attributes"]["POSITION"])
        normals = values(primitive["attributes"]["NORMAL"])
        source_vertices = source["meshes"][native["mesh"]]["vertices"]
        assert len(vertices) == len(source_vertices)
        for before, after in zip(source_vertices, vertices):
            expected = point(source_world(path), before)
            actual = point(export_world(index), after)
            error = math.sqrt(sum((a - b) ** 2 for a, b in zip(expected, actual)))
            maximum = max(maximum, error)
            comparisons += 1
        indices = values(primitive["indices"])
        for i in range(0, len(indices), 3):
            ia, ib, ic = indices[i:i + 3]
            a, b, c = vertices[ia], vertices[ib], vertices[ic]
            u, v = [b[j] - a[j] for j in range(3)], [c[j] - a[j] for j in range(3)]
            cross = [u[1]*v[2] - u[2]*v[1], u[2]*v[0] - u[0]*v[2], u[0]*v[1] - u[1]*v[0]]
            assert sum(cross[j] * normals[ia][j] for j in range(3)) > 0, f"Non-outward exported triangle: {path}"
            winding_checks += 1
    assert paths == set(authored), "Node identity or count differs"
    assert maximum < 0.000001, f"World vertex discrepancy {maximum} exceeds 1 μm"
    return {"file": filename, "form_amount": amount,
            "nodes": len(paths), "world_vertex_comparisons": comparisons,
            "outward_triangle_checks": winding_checks, "maximum_world_vertex_error_m": maximum,
            "status": "PASS"}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=ROOT / "game/presentation/quarto_native_v1.json")
    parser.add_argument("--exports", type=Path, required=True)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    raw = args.source.read_bytes()
    source = json.loads(raw)
    sha = hashlib.sha256(raw).hexdigest()
    paths = sorted(args.exports.glob("*.glb"))
    assert len(paths) == 3, "Expected Spread, midpoint and Drive GLBs"
    records = []
    for path in paths:
        record = inspect_glb(path, source, sha)
        record["file"] = path.name
        records.append(record)
    assert sorted(item["form_amount"] for item in records) == [0, 0.5, 1]
    report = {"status": "PASS", "source_sha256": sha, "scope": "Static interchange geometry; native Godot unverified",
              "poses": records}
    text = json.dumps(report, indent=2) + "\n"
    if args.report:
        if args.report.exists():
            parser.error("Report already exists; preserve earlier results")
        args.report.write_text(text)
    print(text, end="")


if __name__ == "__main__":
    main()
