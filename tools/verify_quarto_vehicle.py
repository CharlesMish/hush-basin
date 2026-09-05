#!/usr/bin/env python3
"""Versioned Quarto visual-successor checks; never substitutes or installs Godot.

Default: independent source/data checks only. --native additionally requires the
exact engine and runs disposable baseline/successor projects on the same host.
All evidence goes to a new --evidence directory; historical records are untouched.
"""

from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import io
import json
import math
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "game/tests/fixtures/quarto_vehicle_v1_contract.json"
SPEC = ROOT / "game/presentation/quarto_native_v1.json"
IDENTITY = [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def add(a, b):
    return [x + y for x, y in zip(a, b)]


def sub(a, b):
    return [x - y for x, y in zip(a, b)]


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def cross(a, b):
    return [a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0]]


def mul(a, b):
    return [[sum(a[i][k]*b[k][j] for k in range(3)) for j in range(3)] for i in range(3)]


def vector(matrix, value):
    return [dot(row, value) for row in matrix]


def rotation(degrees):
    x, y, z = [math.radians(v) for v in degrees]
    cx, sx, cy, sy, cz, sz = math.cos(x), math.sin(x), math.cos(y), math.sin(y), math.cos(z), math.sin(z)
    rx = [[1, 0, 0], [0, cx, -sx], [0, sx, cx]]
    ry = [[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]]
    rz = [[cz, -sz, 0], [sz, cz, 0], [0, 0, 1]]
    return mul(mul(ry, rx), rz)  # Godot's default YXZ Euler order.


def sample(spec, form):
    states = {n["path"]: {"position": list(n.get("position", [0, 0, 0])),
                           "rotation_degrees": list(n.get("rotation_degrees", [0, 0, 0]))}
              for n in spec["nodes"]}
    for channel in spec["pose_channels"]:
        u = max(0.0, min(1.0, (form-channel["start"])/(channel["end"]-channel["start"])))
        index = channel["component"]
        if isinstance(index, str):
            index = {"x": 0, "y": 1, "z": 2}[index]
        states[channel["path"]][channel["property"]][index] += channel["travel"]*u*u*(3-2*u)
    nodes = {n["path"]: n for n in spec["nodes"]}
    transforms = {".": (IDENTITY, [0.0, 0.0, 0.0]), "": (IDENTITY, [0.0, 0.0, 0.0])}

    def transform(path, ancestors=()):
        if path in transforms:
            return transforms[path]
        if path in ancestors:
            raise ValueError("Cycle in pose hierarchy: " + path)
        node, state = nodes[path], states[path]
        parent_basis, parent_origin = transform(node["parent"], (*ancestors, path))
        basis = mul(parent_basis, rotation(state["rotation_degrees"]))
        origin = add(parent_origin, vector(parent_basis, state["position"]))
        transforms[path] = basis, origin
        return basis, origin

    posed = {}
    for node in spec["nodes"]:
        if not node.get("mesh"):
            continue
        basis, origin = transform(node["path"])
        mesh = spec["meshes"][node["mesh"]]
        posed[node["path"]] = [add(origin, vector(basis, v)) for v in mesh["vertices"]]
    return posed, transforms


def bounds(points):
    lo = [min(p[i] for p in points) for i in range(3)]
    hi = [max(p[i] for p in points) for i in range(3)]
    return {"min": lo, "max": hi, "size": sub(hi, lo)}


def axes_for(points, indices):
    normals, edges = [], []
    for i in range(0, len(indices), 3):
        a, b, c = [points[j] for j in indices[i:i+3]]
        normals.append(cross(sub(b, a), sub(c, a)))
        edges.extend([sub(b, a), sub(c, b), sub(a, c)])
    return unique_axes(normals), unique_axes(edges)


def unique_axes(axes):
    result = {}
    for axis in axes:
        length = math.sqrt(dot(axis, axis))
        if length < 1e-10:
            continue
        value = [v / length for v in axis]
        first = next((v for v in value if abs(v) > 1e-8), 1.0)
        if first < 0:
            value = [-v for v in value]
        result[tuple(round(v, 8) for v in value)] = value
    return list(result.values())


def is_convex(points, indices):
    for i in range(0, len(indices), 3):
        a, b, c = [points[j] for j in indices[i:i+3]]
        normal = cross(sub(b, a), sub(c, a))
        length = math.sqrt(dot(normal, normal))
        if length < 1e-10:
            continue
        distances = [dot(sub(p, a), normal) / length for p in points]
        if min(distances) < -1e-7 and max(distances) > 1e-7:
            return False
    return True


def closed_surface(points, indices):
    edges = Counter()
    for i in range(0, len(indices), 3):
        triangle = [tuple(round(v, 8) for v in points[j]) for j in indices[i:i+3]]
        if len(set(triangle)) != 3:
            return False
        for a, b in zip(triangle, [triangle[1], triangle[2], triangle[0]]):
            edges[tuple(sorted((a, b)))] += 1
    return bool(edges) and all(count == 2 for count in edges.values())


def bounds_overlap(a, b):
    return all(min(a["max"][i], b["max"][i]) - max(a["min"][i], b["min"][i]) > 1e-7 for i in range(3))


def convex_overlap(a, ai, b, bi, tolerance=1e-7):
    """Actual convex mesh SAT; intended shared boundaries are not penetration."""
    an, ae = axes_for(a, ai)
    bn, be = axes_for(b, bi)
    for axis in [*an, *bn, *unique_axes(cross(x, y) for x in ae for y in be)]:
        length = math.sqrt(dot(axis, axis))
        if length < 1e-10:
            continue
        axis = [v/length for v in axis]
        pa, pb = [dot(p, axis) for p in a], [dot(p, axis) for p in b]
        if min(max(pa), max(pb)) - max(min(pa), min(pb)) <= tolerance:
            return False
    return True


def point_inside(point, points, indices):
    hits = []
    direction = [1.0, 0.3713907, 0.2191213]
    for i in range(0, len(indices), 3):
        hit = ray_triangle(point, direction, *[points[j] for j in indices[i:i+3]])
        if hit is not None and hit > 1e-7 and not any(abs(hit - value) < 1e-7 for value in hits):
            hits.append(hit)
    return len(hits) % 2 == 1


def mesh_overlap(a, ai, b, bi, both_convex):
    if not bounds_overlap(bounds(a), bounds(b)):
        return False
    if both_convex:
        return convex_overlap(a, ai, b, bi)
    # Actual triangle surfaces for nonconvex parts such as hollow tubes.
    for p, pi, q, qi in [(a, ai, b, bi), (b, bi, a, ai)]:
        targets = [([q[k] for k in qi[j:j+3]], bounds([q[k] for k in qi[j:j+3]]))
                   for j in range(0, len(qi), 3)]
        for i in range(0, len(pi), 3):
            triangle = [p[j] for j in pi[i:i+3]]
            tri_bounds = bounds(triangle)
            for start, end in zip(triangle, [triangle[1], triangle[2], triangle[0]]):
                direction = sub(end, start)
                for target, target_bounds in targets:
                    # Inclusive broad phase: triangles can be planar on an axis.
                    if any(tri_bounds["max"][axis] < target_bounds["min"][axis]-1e-8 or
                           target_bounds["max"][axis] < tri_bounds["min"][axis]-1e-8 for axis in range(3)):
                        continue
                    hit = ray_triangle(start, direction, *target)
                    if hit is not None and 1e-7 < hit < 1.0-1e-7:
                        return True
    return point_inside(a[0], b, bi) or point_inside(b[0], a, ai)


def ray_triangle(start, direction, a, b, c):
    e1, e2 = sub(b, a), sub(c, a)
    h = cross(direction, e2)
    det = dot(e1, h)
    if abs(det) < 1e-10:
        return None
    inverse = 1.0 / det
    s = sub(start, a)
    u = inverse * dot(s, h)
    if u < -1e-8 or u > 1.0 + 1e-8:
        return None
    q = cross(s, e1)
    v = inverse * dot(direction, q)
    if v < -1e-8 or u + v > 1.0 + 1e-8:
        return None
    t = inverse * dot(e2, q)
    return t if t >= -1e-8 else None


def parse_materials(scene):
    result = {}
    for name, body in re.findall(r'\[sub_resource type="StandardMaterial3D" id="Material_([^"\n]+)"\]\n(.*?)(?=\n\[|\Z)', scene, re.S):
        values = {}
        for key in ["albedo_color", "metallic", "roughness", "emission_enabled", "emission", "emission_energy_multiplier"]:
            match = re.search(r"^" + key + r" = (.+)$", body, re.M)
            if match:
                literal = match[1]
                values[key] = ([float(v) for v in literal[6:-1].split(",")]
                               if literal.startswith("Color(") else literal == "true"
                               if literal in {"true", "false"} else float(literal))
        result[name] = values
    return result


def scene_binding(scene, spec):
    actual = {}
    for header, body in re.findall(r"\[node ([^\n]+)\]\n(.*?)(?=\n\[|\Z)", scene, re.S):
        fields = dict(re.findall(r'(\w+)="([^"\n]*)"', header))
        if "parent" not in fields:
            if fields.get("name") != "VisualRoot" or fields.get("type") != "Node3D":
                return False, "Unexpected visual root"
            continue
        parent = fields["parent"]
        path = fields["name"] if parent == "." else parent + "/" + fields["name"]
        if path in actual:
            return False, "Duplicate scene path: " + path
        entry = {"parent": parent, "type": fields["type"], "position": [0, 0, 0],
                 "rotation_degrees": [0, 0, 0], "scale": [1, 1, 1]}
        for prop in ["position", "rotation", "rotation_degrees", "scale"]:
            match = re.search(r"^" + prop + r" = Vector3\(([^)]+)\)$", body, re.M)
            if match:
                value = [float(x) for x in match[1].split(",")]
                entry["rotation_degrees" if prop == "rotation" else prop] = [math.degrees(x) for x in value] if prop == "rotation" else value
        for source, key in [(r'metadata/quarto_mesh = "([^"]+)"', "mesh"),
                            (r'material_override = SubResource\("([^"]+)"\)', "material")]:
            match = re.search("^" + source + "$", body, re.M)
            if match:
                entry[key] = match[1]
        if re.search(r"^visible = false$", body, re.M):
            return False, "Hidden source mesh: " + path
        actual[path] = entry
    expected = {node["path"]: node for node in spec["nodes"]}
    if actual.keys() != expected.keys():
        return False, {"missing": sorted(expected.keys()-actual.keys()), "extra": sorted(actual.keys()-expected.keys())}
    for path, row in expected.items():
        for key in ["parent", "type", "mesh", "material"]:
            if row.get(key) != actual[path].get(key):
                return False, path + ": " + key
        for key, default in [("position", [0, 0, 0]), ("rotation_degrees", [0, 0, 0]), ("scale", [1, 1, 1])]:
            if max(abs(a-b) for a, b in zip(row.get(key, default), actual[path][key])) > 1e-6:
                return False, path + ": " + key
    return True, {"nodes": len(actual), "scope": "Exact hierarchy/type/material/mesh binding; rest transforms within 1e-6 after radians-to-degrees conversion."}


def separation_controls():
    points = [[x, y, z] for x in [-1, 1] for y in [-1, 1] for z in [-1, 1]]
    indices = [0, 1, 3, 0, 3, 2, 4, 6, 7, 4, 7, 5, 0, 4, 5, 0, 5, 1,
               2, 3, 7, 2, 7, 6, 0, 2, 6, 0, 6, 4, 1, 5, 7, 1, 7, 3]
    moved = lambda x: [[v[0]+x, v[1], v[2]] for v in points]
    return (closed_surface(points, indices) and is_convex(points, indices)
            and convex_overlap(points, indices, moved(1.5), indices)
            and not convex_overlap(points, indices, moved(2.0), indices)
            and not convex_overlap(points, indices, moved(2.1), indices)
            and ray_triangle([0, 0, -1], [0, 0, 1], [-1, -1, 0], [1, -1, 0], [0, 1, 0]) == 1.0)


def static_checks(contract):
    checks = []

    def check(name, ok, detail=None):
        checks.append({"id": name, "pass": bool(ok), "detail": detail})

    check("SEPARATION_METHOD_CONTROLS", separation_controls(),
          "Independent box overlap/separation/exact-touch controls and a deliberate axial cap triangle.")

    wrappers = contract.get("wrapper_preamble_only", {})
    allowed = set(contract["allowed_baseline_changes"])
    for name, expected in contract["baseline_files_sha256"].items():
        path = ROOT / name
        if name in allowed:
            check("DECLARED_VISUAL_SUCCESSOR:" + name, path.is_file())
        elif name in wrappers:
            check("PRESERVED_WRAPPER_SUFFIX:" + name,
                  path.is_file() and path.read_text().endswith(wrappers[name]))
        else:
            check("PRESERVED:" + name, path.is_file() and sha(path) == expected)
    scene = (ROOT / "game/scenes/vehicle_visual.tscn").read_text()
    rig = (ROOT / "game/scripts/vehicle_visual_rig.gd").read_text()
    check("EXACT_ELEVEN_SOURCE_MATERIALS", parse_materials(scene) == contract["baseline_materials"])
    material_blocks = {name: body.strip() for name, body in re.findall(
        r'\[sub_resource type="StandardMaterial3D" id="Material_([^"\n]+)"\]\n(.*?)(?=\n\[|\Z)', scene, re.S)}
    check("COMPLETE_ORIGINAL_MATERIAL_DECLARATIONS", material_blocks == contract["baseline_material_blocks"])
    colors = {k: [float(v) for v in raw.split(",")] for k, raw in
              re.findall(r"^const (\w+_ENERGY) := Color\(([^)]+)\)", rig, re.M)}
    check("EXACT_FOUR_STATE_COLORS", colors == contract["baseline_state_colors"])
    check("VISUAL_API", "class_name VehicleVisualRig" in rig and
          all("func " + method + "(" in rig for method in ["set_form_amount", "set_energy_state"]))
    forbidden = ["move_and_slide(", "Input.action_", "set_physics_process(",
                 "get_parent(", "CharacterBody3D.new(", "CollisionShape3D.new(",
                 "PhysicsServer3D", "register_authority", "runS5Authority"]
    mesh_library = (ROOT / "game/scripts/quarto_mesh_library.gd").read_text()
    check("NO_KNOWN_SIMULATION_OR_AUTHORITY_WRITES", not any(s in rig + "\n" + mesh_library for s in forbidden))
    spec = json.loads(SPEC.read_text())
    bound, binding_detail = scene_binding(scene, spec)
    check("NATIVE_SCENE_MATCHES_AUTHORED_DATA", bound, binding_detail)
    nodes = spec["nodes"]
    paths = {n["path"] for n in nodes}
    check("UNIQUE_NODE_PATHS", len(paths) == len(nodes))
    check("PRESENTATION_NODE_TYPES", all(n["type"] in {"Node3D", "MeshInstance3D"} for n in nodes))
    check("PARENT_PATHS", all(n["parent"] in paths | {".", ""} for n in nodes))
    check("NO_SCALE_OR_VISIBILITY_ANIMATION", all(c["property"] in {"position", "rotation_degrees"}
                                                for c in spec["pose_channels"]))
    check("FINITE_MONOTONE_CHANNEL_WINDOWS", all(math.isfinite(c["travel"]) and
          0 <= c["start"] < c["end"] <= 1 and c["path"] in paths for c in spec["pose_channels"]))
    check("UNIT_POSITIVE_NODE_SCALES", all(n.get("scale", [1, 1, 1]) == [1, 1, 1] for n in nodes))
    check("FINITE_NODE_REST_TRANSFORMS", all(len(n.get(key, [0, 0, 0])) == 3 and
          all(math.isfinite(v) for v in n.get(key, [0, 0, 0]))
          for n in nodes for key in ["position", "rotation_degrees"]))
    valid_meshes = True
    triangle_count = 0
    for mesh in spec["meshes"].values():
        vertices, indices = mesh["vertices"], mesh["indices"]
        valid_meshes &= bool(vertices) and len(indices) % 3 == 0
        valid_meshes &= all(len(v) == 3 and all(math.isfinite(x) for x in v) for v in vertices)
        valid_meshes &= all(isinstance(i, int) and 0 <= i < len(vertices) for i in indices)
        normals = mesh.get("normals", [])
        valid_meshes &= len(normals) == len(vertices) and all(len(n) == 3 and
                        all(math.isfinite(v) for v in n) and abs(dot(n, n)-1.0) < 1e-5 for n in normals)
        triangle_count += len(indices) // 3
    check("FINITE_INDEXED_MESHES", valid_meshes, {"unique_meshes": len(spec["meshes"]), "triangles": triangle_count})
    if not valid_meshes:
        return checks, {}
    by_path = {n["path"]: n for n in nodes}
    leaves = [n["path"] for n in nodes if n.get("mesh") and n["path"].split("/")[-1] in {"InnerLeaf", "OuterLeaf"}]
    check("EIGHT_DISTINCT_PRIMARY_LEAVES", len(leaves) == 8)
    fold_channels = [c for c in spec["pose_channels"] if c["path"].endswith("/OuterFold")]
    check("FOUR_TRUE_CHORDWISE_HALF_TURNS", len(fold_channels) == 4 and all(
          c["property"] == "rotation_degrees" and c["component"] in {2, "z"} and
          abs(c["travel"]) == 180 for c in fold_channels))
    for family in ["Front", "Rear"]:
        paired = [c for c in fold_channels if c["path"].startswith(family)]
        check(f"{family.upper()}_COUNTERPART_FOLD_SIGNS", len(paired) == 2 and
              sum(c["travel"] for c in paired) == 0)
    channels_by_path = {c["path"]: c for c in spec["pose_channels"]}
    ordered = True
    for family in ["Front", "Rear"]:
        for side in ["Port", "Starboard"]:
            prefix = family + side + "Rig/SocketSlide"
            fold = channels_by_path[prefix + "/YawPivot/HaunchPivot/OuterFold"]
            yaw = channels_by_path[prefix + "/YawPivot"]
            haunch = channels_by_path[prefix + "/YawPivot/HaunchPivot"]
            slide = channels_by_path[prefix]
            ordered &= fold["end"] <= yaw["start"] and yaw["end"] <= haunch["start"]
            ordered &= slide["end"] <= contract["can"]["start_form"] and haunch["end"] <= contract["can"]["start_form"]
            ordered &= abs(haunch["travel"]) == 70
    check("FOLD_REORIENT_SEAT_BEFORE_CAN", ordered)
    check("HIGHER_REAR_ROOT_STATIONS", all(by_path["Rear"+side+"Rig"]["position"][1] >
          by_path["Front"+side+"Rig"]["position"][1] for side in ["Port", "Starboard"]))
    convex = {name: is_convex(mesh["vertices"], mesh["indices"]) for name, mesh in spec["meshes"].items()}
    check("CLOSED_PRIMARY_LEAF_SURFACES", all(closed_surface(spec["meshes"][by_path[path]["mesh"]]["vertices"],
          spec["meshes"][by_path[path]["mesh"]]["indices"]) for path in leaves),
          {path: "convex SAT" if convex[by_path[path]["mesh"]] else "actual triangles and containment" for path in leaves})
    central = [n["path"] for n in nodes if n.get("mesh") and n["path"].startswith("CentralStructure/")]
    measured, intersections, bilateral_failures, central_intersections = [], [], [], []
    fixed_core = None
    can_stowed = None
    count = sum(bool(n.get("mesh")) for n in nodes)
    for i in range(contract["sampling"]["steps"] + 1):
        form = i / contract["sampling"]["steps"]
        posed, transforms = sample(spec, form)
        envelope = bounds([p for vertices in posed.values() for p in vertices])
        measured.append({"form_amount": form, **envelope})
        check_count = len(posed) == count
        if not check_count:
            check("CONSTANT_MATERIAL_INSTANCES_AT_" + str(form), False)
        for family in ["Front", "Rear"]:
            port = bounds([v for p, points in posed.items() if p.startswith(family + "PortRig/") for v in points])
            starboard = bounds([v for p, points in posed.items() if p.startswith(family + "StarboardRig/") for v in points])
            errors = [abs(port["min"][0] + starboard["max"][0]), abs(port["max"][0] + starboard["min"][0]),
                      *[abs(port[key][j] - starboard[key][j]) for key in ["min", "max"] for j in [1, 2]]]
            if max(errors) > contract["numeric_tolerance_m"] or port["max"][0] > starboard["min"][0] + 1e-7:
                bilateral_failures.append({"form": form, "family": family, "max_error": max(errors)})
        for j, a in enumerate(leaves):
            for b in leaves[j+1:]:
                am, bm = by_path[a]["mesh"], by_path[b]["mesh"]
                if mesh_overlap(posed[a], spec["meshes"][am]["indices"],
                                posed[b], spec["meshes"][bm]["indices"], convex[am] and convex[bm]):
                    intersections.append({"form": form, "a": a, "b": b})
            for b in central:
                am, bm = by_path[a]["mesh"], by_path[b]["mesh"]
                if mesh_overlap(posed[a], spec["meshes"][am]["indices"],
                                posed[b], spec["meshes"][bm]["indices"], convex[am] and convex[bm]):
                    central_intersections.append({"form": form, "leaf": a, "central_part": b})
        core_path = "CentralStructure/DriveBay/FixedCore"
        can_path = "CentralStructure/DriveBay/MovingCan"
        if i == 0:
            fixed_core, can_stowed = transforms.get(core_path), transforms.get(can_path)
        if transforms.get(core_path) != fixed_core:
            check("FIXED_CORE_AT_" + str(form), False)
        if form <= contract["can"]["start_form"] and transforms.get(can_path) != can_stowed:
            check("CAN_STOWED_AT_" + str(form), False)
    limits, tolerance = contract["bounds_m"], contract["numeric_tolerance_m"]
    spread, drive = measured[0], measured[-1]
    check("SPREAD_WIDTH", limits["spread_width"][0]-tolerance <= spread["size"][0] <= limits["spread_width"][1]+tolerance, spread)
    check("DRIVE_WIDTH", drive["size"][0] <= limits["drive_width_max"]+tolerance, drive)
    check("ENDPOINT_LENGTHS", all(limits["endpoint_length"][0]-tolerance <= p["size"][2] <= limits["endpoint_length"][1]+tolerance for p in [spread, drive]))
    check("ENDPOINT_HEIGHTS", spread["size"][1] <= limits["spread_height_max"]+tolerance and drive["size"][1] <= limits["drive_height_max"]+tolerance)
    check("ENTIRE_SAMPLED_VERTICAL_ENVELOPE", all(p["min"][1] >= limits["sample_y"][0]-tolerance and p["max"][1] <= limits["sample_y"][1]+tolerance for p in measured))
    check("BILATERAL_SYMMETRY_AND_CENTER_SEPARATION", not bilateral_failures, bilateral_failures[:12])
    check("PRIMARY_LEAF_SURFACE_SEPARATION", not intersections, intersections[:24])
    check("PRIMARY_LEAVES_CLEAR_CENTRAL_SURFACES_AND_POCKETS", not central_intersections,
          {"defect_count": len(central_intersections), "first_defects": central_intersections[:32],
           "methods": "AABB reject; actual convex-part SAT or triangle intersections/containment for nonconvex parts. No central-structure exception."})
    check("FIXED_CORE_PRESENT", fixed_core is not None)
    _, terminal = sample(spec, 1.0)
    can_final = terminal.get("CentralStructure/DriveBay/MovingCan")
    check("EXACT_LATE_CAN_STROKE", can_final is not None and can_stowed is not None and
          max(abs(v-e) for v, e in zip(sub(can_final[1], can_stowed[1]), [0, 0, contract["can"]["stroke_m"]])) <= tolerance)
    tube_path = "CentralStructure/DriveBay/MovingCan/CanBody"
    tube = spec["meshes"][by_path[tube_path]["mesh"]]
    radial = [math.hypot(v[0], v[1]) for v in tube["vertices"]]
    inner, outer = min(radial), max(radial)
    check("CAN_POSITIVE_WALL_THICKNESS", inner > 0 and outer-inner >= contract["can"]["minimum_wall_m"], {"inner_radius": inner, "outer_radius": outer})
    zmin = min(v[2] for v in tube["vertices"])
    zmax = max(v[2] for v in tube["vertices"])
    aperture_clear = True
    for x, y in [(0, 0), *[(inner*0.8*math.cos(a*math.pi/4), inner*0.8*math.sin(a*math.pi/4)) for a in range(8)]]:
        for i in range(0, len(tube["indices"]), 3):
            a, b, c = [tube["vertices"][j] for j in tube["indices"][i:i+3]]
            hit = ray_triangle([x, y, zmin-0.01], [0, 0, 1], a, b, c)
            if hit is not None and hit <= zmax-zmin+0.02:
                aperture_clear = False
    check("CAN_OPEN_THROUGH_NINE_AXIAL_RAYS", aperture_clear)
    final_points, _ = sample(spec, 1.0)
    core_points = final_points["CentralStructure/DriveBay/FixedCore"]
    inverse_basis = [list(row) for row in zip(*can_final[0])]
    core_radial = [math.hypot(*vector(inverse_basis, sub(p, can_final[1]))[:2]) for p in core_points]
    check("FIXED_CORE_CLEAR_INSIDE_CAN_BORE", max(core_radial) < inner-tolerance,
          {"maximum_core_radius": max(core_radial), "minimum_bore_radius": inner})
    core_local = [vector(inverse_basis, sub(p, can_final[1])) for p in core_points]
    core_indices = spec["meshes"][by_path["CentralStructure/DriveBay/FixedCore"]["mesh"]]["indices"]
    shifted_core = [[p[0]+inner, p[1], p[2]] for p in core_local]
    check("HOLLOW_PASSAGE_METHOD_CONTROL", not mesh_overlap(core_local, core_indices,
          tube["vertices"], tube["indices"], False) and mesh_overlap(shifted_core, core_indices,
          tube["vertices"], tube["indices"], False),
          "Core in empty bore stays clear; a detached copy shifted into the tube wall must intersect. Authored geometry is unchanged.")
    measurements = {"mesh_instances": count, "unique_meshes": len(spec["meshes"]),
                    "primary_leaves": len(leaves), "samples": measured,
                    "leaf_central_defects": central_intersections,
                    "scope": "Independent Python evaluation of authored mesh/pose data. Actual Godot runtime agreement remains a separate required check. Eight principal leaves are checked against each other and every central-structure mesh, including pockets. This is sampled presentation geometry, not whole-vehicle clearance authority."}
    return checks, measurements


def execute_native(contract, args, evidence):
    from launch import LaunchError, resolve_engine
    try:
        engine, version = resolve_engine(args.godot)
    except LaunchError as error:
        return {"status": "BLOCKED", "reason": str(error), "records": []}
    records = []

    def run(name, command, cwd):
        try:
            process = subprocess.run([str(x) for x in command], cwd=cwd, text=True,
                                     stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=600)
            output, code = process.stdout, process.returncode
        except (OSError, subprocess.TimeoutExpired) as error:
            output, code = str(error), -1
        (evidence / (name + ".stdout")).write_text(output)
        ok = code == 0 and not re.search(r"SCRIPT ERROR:|Parse Error:|Failed to load script|Cannot get class", output, re.I)
        records.append({"name": name, "argv": [str(x) for x in command], "cwd": str(cwd), "returncode": code, "pass": ok})
        print(("PASS " if ok else "FAIL ") + name, flush=True)
        return ok

    with tempfile.TemporaryDirectory(prefix="quarto-native-validation-") as temporary:
        temp = Path(temporary)
        before, after = temp / "baseline", temp / "successor"
        if args.baseline:
            shutil.copytree(args.baseline, before, ignore=shutil.ignore_patterns(".git", ".godot", "__pycache__"))
        else:
            try:
                archive = subprocess.check_output(["git", "archive", contract["baseline_commit"]], cwd=ROOT)
                with tarfile.open(fileobj=io.BytesIO(archive)) as source:
                    for member in source:
                        target = before / member.name
                        if not target.resolve().is_relative_to(before.resolve()) or member.issym() or member.islnk():
                            raise ValueError("Unsafe baseline archive member")
                        if member.isdir():
                            target.mkdir(parents=True, exist_ok=True)
                        elif member.isfile():
                            target.parent.mkdir(parents=True, exist_ok=True)
                            target.write_bytes(source.extractfile(member).read())
            except (OSError, ValueError, subprocess.CalledProcessError) as error:
                return {"status": "BLOCKED", "engine": version, "reason": "Supply --baseline with the exact preserved source: " + str(error), "records": records}
        baseline_ok = all((before/name).is_file() and sha(before/name) == digest for name, digest in contract["baseline_files_sha256"].items())
        records.append({"name": "EXACT_DISPOSABLE_BASELINE", "pass": baseline_ok})
        if not baseline_ok:
            return {"status": "FAIL", "engine": version, "records": records}
        shutil.copytree(ROOT / "game", after / "game", ignore=shutil.ignore_patterns(".godot", "__pycache__"))
        for label, project in [("baseline", before), ("successor", after)]:
            if not run(label + "_import", [engine, "--headless", "--editor", "--path", project/"game", "--import", "--quit"], project):
                return {"status": "FAIL", "engine": version, "records": records}
            if not run(label + "_parse", [engine, "--headless", "--editor", "--path", project/"game", "--quit-after", "2"], project):
                return {"status": "FAIL", "engine": version, "records": records}
            run(label + "_c1", [engine, "--headless", "--path", project/"game", "--script", "res://tests/world_polish_c1.gd", "--", "--output", evidence/(label+"-c1.jsonl")], project)
        traces = [evidence/(name+"-c1.jsonl") for name in ["baseline", "successor"]]
        c1_ok = all(p.is_file() and len(p.read_text().splitlines()) == 1260 for p in traces)
        c1_ok = c1_ok and traces[0].read_bytes() == traces[1].read_bytes()
        records.append({"name": "C1_MATCHED_SAME_HOST_1260_TICKS", "pass": c1_ok,
                        "hashes": {p.name: sha(p) for p in traces if p.is_file()}})
        fixtures = [("quarto_vehicle", "quarto_vehicle_v1.gd", True),
                    ("run_v0", "run_v0_probe.gd", True),
                    ("paused_retry", "paused_retry_addendum.gd", True),
                    ("world_and_entrances", "world_polish_runtime.gd", False)]
        for name, script, headless in fixtures:
            result = evidence/(name+".json")
            flags = ["--headless"] if headless else ["--resolution", "1280x720", "--rendering-method", "forward_plus"]
            run(name, [engine, *flags, "--path", after/"game", "--script", "res://tests/"+script, "--", "--result", result], after)
            try:
                passed = result.is_file() and json.loads(result.read_text()).get("status") == "PASS"
            except (OSError, ValueError, TypeError, AttributeError):
                passed = False
            records.append({"name": name + "_result", "pass": passed})
        for label, project in [("baseline", before), ("successor", after)]:
            folder = evidence / (label + "-camera-poses")
            run(label + "_camera_pose_capture", [engine, "--resolution", "1280x720",
                "--rendering-method", "forward_plus", "--path", project/"game", "--script",
                "res://tests/p1a_vehicle_r7_pose_probe.gd", "--", "--output-dir", folder], project)
            try:
                capture = json.loads((folder/"pose_probe_result.json").read_text())
                passed = capture.get("status") == "PASS" and len(capture.get("records", [])) == 3
            except (OSError, ValueError, TypeError, AttributeError):
                passed = False
            records.append({"name": label + "_camera_pose_result", "pass": passed,
                            "scope": "Borrowed unchanged three-pose camera/framing probe, not an R7 kinematic or authority certification."})
    return {"status": "PASS" if all(r["pass"] for r in records) else "FAIL", "engine": version,
            "records": records, "scope": "Native sampled geometry/API tests, same-host matched C1, Run/reset and current world/entrance fixtures. Human feel, visual approval and performance are separate."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evidence", required=True, type=Path, help="New empty evidence directory")
    parser.add_argument("--native", action="store_true", help="Require exact installed engine and native display for world tests")
    parser.add_argument("--godot", help="Exact installed executable; no substitution or installation")
    parser.add_argument("--baseline", type=Path, help="Exact baseline source; otherwise export recorded Git commit")
    args = parser.parse_args()
    evidence = args.evidence.resolve()
    evidence.mkdir(parents=True, exist_ok=False)
    contract = json.loads(FIXTURE.read_text())
    try:
        checks, measurements = static_checks(contract)
    except (OSError, ValueError, KeyError, TypeError, IndexError) as error:
        checks, measurements = [{"id": "STATIC_COMPLETION", "pass": False, "detail": str(error)}], {}
    static_ok = all(c["pass"] for c in checks)
    (evidence/"static.json").write_text(json.dumps({"status": "PASS" if static_ok else "FAIL", "checks": checks, "measurements": measurements}, indent=2)+"\n")
    native = {"status": "NOT_RUN", "reason": "No native validation requested. Python data checks do not establish Godot runtime fidelity."}
    if args.native and static_ok:
        native = execute_native(contract, args, evidence)
    elif args.native:
        native = {"status": "NOT_RUN", "reason": "Static checks failed; native dependent work was not started."}
    result = {"schema": "hush_basin.quarto_vehicle_v1.verification.v1", "baseline_commit": contract["baseline_commit"],
              "authority_participation": "none", "static_status": "PASS" if static_ok else "FAIL",
              "native": native, "status": "FAIL" if not static_ok or native["status"] == "FAIL" else
              "BLOCKED" if native["status"] == "BLOCKED" else "PASS" if native["status"] == "PASS" else "STATIC_PASS_NATIVE_NOT_RUN",
              "static_check_count": len(checks), "failures": [c["id"] for c in checks if not c["pass"]],
              "not_claimed": ["MT1-S5HR3R1 authority or manufacturing clearance", "Human gameplay feel or visual acceptance", "Performance acceptance", "Cross-platform physics determinism"]}
    (evidence/"suite.json").write_text(json.dumps(result, indent=2)+"\n")
    print(json.dumps(result, indent=2))
    return 1 if result["status"] == "FAIL" else 2 if result["status"] == "BLOCKED" else 0


if __name__ == "__main__":
    raise SystemExit(main())
