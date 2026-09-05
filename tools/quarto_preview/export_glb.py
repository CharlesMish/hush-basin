#!/usr/bin/env python3
"""Export review-only static GLBs directly from the native rig's canonical data.

This is an interchange preview, not a Godot export or native round-trip proof.
The source's right-handed coordinates stay +Y up / -Z nose, in metres. Godot
clockwise triangle indices are reversed for glTF's counterclockwise winding.
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
SOURCE = ROOT / "game/presentation/quarto_native_v1.json"


def stage(start: float, end: float, value: float) -> float:
    t = max(0.0, min(1.0, (value - start) / max(end - start, 0.0001)))
    return t * t * (3.0 - 2.0 * t)


def multiply(a: list[float], b: list[float]) -> list[float]:
    x, y, z, w = a
    X, Y, Z, W = b
    return [w * X + x * W + y * Z - z * Y,
            w * Y - x * Z + y * W + z * X,
            w * Z + x * Y - y * X + z * W,
            w * W - x * X - y * Y - z * Z]


def quaternion(rotation: list[float]) -> list[float]:
    x, y, z = (math.radians(v) / 2 for v in rotation)
    return multiply(multiply([0, math.sin(y), 0, math.cos(y)],
                             [math.sin(x), 0, 0, math.cos(x)]),
                    [0, 0, math.sin(z), math.cos(z)])


def linear(value: float) -> float:
    return value / 12.92 if value <= 0.04045 else ((value + 0.055) / 1.055) ** 2.4


def material(source: dict, name: str) -> dict:
    albedo = source.get("albedo_color", [0.5, 0.5, 0.5, 1])
    emission = [v * source.get("emission_energy_multiplier", 1.0)
                for v in source.get("emission", [0, 0, 0])[:3]]
    if source.get("emission_enabled") is False:
        emission = [0, 0, 0]
    strength = max(1.0, *emission)
    result = {
        "name": name,
        "pbrMetallicRoughness": {
            "baseColorFactor": [linear(v) for v in albedo[:3]] + [albedo[3] if len(albedo) > 3 else 1],
            "metallicFactor": source.get("metallic", 0),
            "roughnessFactor": source.get("roughness", 0.5),
        },
        "emissiveFactor": [v / strength for v in emission],
        "doubleSided": False,
    }
    if strength > 1:
        result["extensions"] = {"KHR_materials_emissive_strength": {"emissiveStrength": strength}}
    if result["pbrMetallicRoughness"]["baseColorFactor"][3] < 1:
        result["alphaMode"] = "BLEND"
    return result


def build_glb(data: dict, amount: float, source_sha: str) -> bytes:
    gltf = {
        "asset": {"version": "2.0", "generator": "Hush Basin Quarto canonical geometry preview",
                  "extras": {"source_sha256": source_sha, "form_amount": amount,
                             "scope": "Presentation geometry only; not native Godot validation or MT1 authority"}},
        "scene": 0, "scenes": [{"nodes": []}], "nodes": [], "meshes": [], "materials": [],
        "accessors": [], "bufferViews": [], "buffers": [],
    }
    binary = bytearray()

    def accessor(values: list, components: int, component_type: int, bounds: bool = False) -> int:
        flat = [v for row in values for v in row] if components > 1 else values
        while len(binary) % 4:
            binary.append(0)
        start = len(binary)
        pack_code = "f" if component_type == 5126 else "I"
        packed = struct.pack("<" + pack_code * len(flat), *flat)
        binary.extend(packed)
        view = len(gltf["bufferViews"])
        gltf["bufferViews"].append({"buffer": 0, "byteOffset": start, "byteLength": len(packed),
                                    "target": 34962 if components > 1 else 34963})
        item = {"bufferView": view, "componentType": component_type, "count": len(values),
                "type": {1: "SCALAR", 3: "VEC3"}[components]}
        if bounds:
            # Bounds describe actual float32 payload, not pre-quantized doubles.
            actual = struct.unpack("<" + pack_code * len(flat), packed)
            item["min"] = [min(actual[axis::components]) for axis in range(components)]
            item["max"] = [max(actual[axis::components]) for axis in range(components)]
        index = len(gltf["accessors"])
        gltf["accessors"].append(item)
        return index

    geometry = {}
    for mesh_id, spec in data["meshes"].items():
        indices = spec["indices"].copy()
        for i in range(0, len(indices), 3):
            indices[i + 1], indices[i + 2] = indices[i + 2], indices[i + 1]
        geometry[mesh_id] = {"attributes": {
            "POSITION": accessor(spec["vertices"], 3, 5126, bounds=True),
            "NORMAL": accessor(spec["normals"], 3, 5126)},
            "indices": accessor(indices, 1, 5125), "mode": 4}

    materials = {}
    for key, spec in data["materials"].items():
        materials[key] = len(gltf["materials"])
        gltf["materials"].append(material(spec, key))
    energy_paths = set(data.get("energy_material_paths", []))
    propulsion_paths = set(data.get("propulsion_material_paths", []))
    colors = data.get("energy_colors", {})
    spread = colors.get("SPREAD", [1, 0.58, 0.16])
    drive = colors.get("DRIVE", [0.2, 0.95, 1])
    current = [a + (b - a) * amount for a, b in zip(spread[:3], drive[:3])]
    propulsion_window = data.get("propulsion_window", [0.88, 1.0])
    propulsion_t = stage(*propulsion_window, amount)
    posed = copy.deepcopy(data["nodes"])
    by_path = {node["path"]: node for node in posed}
    for channel in data["pose_channels"]:
        node = by_path[channel["path"]]
        node.setdefault(channel["property"], [0, 0, 0])[channel["component"]] += channel["travel"] * stage(channel["start"], channel["end"], amount)
    mesh_cache = {}
    for node in posed:
        record = {"name": node["path"].split("/")[-1],
                  "translation": node.get("position", [0, 0, 0]),
                  "rotation": quaternion(node.get("rotation_degrees", [0, 0, 0])),
                  "extras": {"native_node_path": node["path"]}}
        if "mesh" in node:
            material_index = materials[node["material"]]
            if node["path"] in energy_paths or node["path"] in propulsion_paths:
                spec = copy.deepcopy(data["materials"][node["material"]])
                if node["path"] in energy_paths:
                    spec.update(albedo_color=current + [1], emission=[v * 0.58 for v in current] + [1],
                                emission_energy_multiplier=0.7 + 0.65 * amount)
                else:
                    spec.update(albedo_color=[v + (1 - v) * 0.18 for v in current] + [1],
                                emission=[v * 0.82 for v in current] + [1],
                                emission_energy_multiplier=0.22 + 1.23 * propulsion_t)
                material_index = len(gltf["materials"])
                gltf["materials"].append(material(spec, f"{node['path']}:energy"))
            key = node["mesh"], material_index
            if key not in mesh_cache:
                primitive = copy.deepcopy(geometry[node["mesh"]])
                primitive["material"] = material_index
                mesh_cache[key] = len(gltf["meshes"])
                gltf["meshes"].append({"name": node["mesh"], "primitives": [primitive]})
            record["mesh"] = mesh_cache[key]
        gltf["nodes"].append(record)
    index_by_path = {node["path"]: i for i, node in enumerate(posed)}
    for index, node in enumerate(posed):
        parent = node.get("parent")
        if parent and parent != ".":
            gltf["nodes"][index_by_path[parent]].setdefault("children", []).append(index)
        else:
            gltf["scenes"][0]["nodes"].append(index)
    if any("extensions" in spec for spec in gltf["materials"]):
        gltf["extensionsUsed"] = ["KHR_materials_emissive_strength"]
    gltf["buffers"].append({"byteLength": len(binary)})
    encoded = json.dumps(gltf, separators=(",", ":"), allow_nan=False).encode()
    encoded += b" " * (-len(encoded) % 4)
    binary += b"\x00" * (-len(binary) % 4)
    length = 12 + 8 + len(encoded) + 8 + len(binary)
    return (struct.pack("<4sII", b"glTF", 2, length) + struct.pack("<I4s", len(encoded), b"JSON") + encoded
            + struct.pack("<I4s", len(binary), b"BIN\x00") + binary)


def validate_container(payload: bytes) -> dict:
    magic, version, length = struct.unpack_from("<4sII", payload)
    assert magic == b"glTF" and version == 2 and length == len(payload)
    json_size, kind = struct.unpack_from("<I4s", payload, 12)
    assert kind == b"JSON" and json_size % 4 == 0
    gltf = json.loads(payload[20:20 + json_size])
    binary_size, binary_kind = struct.unpack_from("<I4s", payload, 20 + json_size)
    assert binary_kind == b"BIN\x00" and 28 + json_size + binary_size == length
    assert gltf["buffers"][0]["byteLength"] <= binary_size
    for view in gltf["bufferViews"]:
        assert view.get("byteOffset", 0) + view["byteLength"] <= gltf["buffers"][0]["byteLength"]
    assert not any("uri" in buffer for buffer in gltf["buffers"])
    assert not any(key in gltf for key in ("skins", "images", "textures", "cameras"))
    return {"nodes": len(gltf["nodes"]), "mesh_instances": sum("mesh" in node for node in gltf["nodes"]),
            "materials": len(gltf["materials"]), "bytes": len(payload),
            "container_check": "PASS", "native_round_trip": "NOT RUN"}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=SOURCE)
    parser.add_argument("--output", type=Path, required=True, help="New external output directory")
    args = parser.parse_args()
    if args.output.exists():
        parser.error("Output directory must be new; previous review exports are never overwritten")
    source = args.source.read_bytes()
    source_sha = hashlib.sha256(source).hexdigest()
    data = json.loads(source)
    args.output.mkdir(parents=True)
    records = {}
    for name, amount in (("spread", 0.0), ("mid", 0.5), ("drive", 1.0)):
        payload = build_glb(data, amount, source_sha)
        records[name] = validate_container(payload)
        records[name]["form_amount"] = amount
        records[name]["sha256"] = hashlib.sha256(payload).hexdigest()
        (args.output / f"quarto_native_v1_{name}.glb").write_bytes(payload)
    report = {"scope": "Review geometry only; not a Godot export or MT1 authority evidence",
              "source_sha256": source_sha, "poses": records}
    (args.output / "export-report.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
