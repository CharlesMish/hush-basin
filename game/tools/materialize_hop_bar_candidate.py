#!/usr/bin/env python3
"""Materialize one preregistered HOP_BAR_01 height candidate without mutating the source packet."""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import pathlib
import re
import shutil

OVERLAY = "1.2.4D"
WORLD = "1.2.3"


def raw_json(obj):
    return (json.dumps(obj, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")


def compact(obj):
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")


def sha_bytes(data):
    return hashlib.sha256(data).hexdigest()


def sha(path):
    return sha_bytes(path.read_bytes())


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_bytes(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


def dump(path, obj):
    write_bytes(path, raw_json(obj))


def packet_sums(root):
    rows = []
    files = sorted(
        (path for path in root.rglob("*") if path.is_file() and path.name != "PACKET_SHA256SUMS.txt"),
        key=lambda path: path.relative_to(root).as_posix().encode(),
    )
    for path in files:
        rows.append(f"{sha(path)}  {path.relative_to(root).as_posix()}\n")
    (root / "PACKET_SHA256SUMS.txt").write_text("".join(rows), encoding="utf-8", newline="\n")


def candidate_solid(base, top):
    obj = copy.deepcopy(base)
    mesh = obj["meshes"]["MESH_HOP_BAR_01"]
    mesh["top_y_m"] = top
    for index in [2, 3, 6, 7]:
        mesh["vertices_xyz_m"][index][1] = top
    mesh["arrays_sha256"] = sha_bytes(
        compact({"triangles": mesh["triangles"], "vertices_xyz_m": mesh["vertices_xyz_m"]})
    )
    return obj


def patch_adapter(text, solid_hash):
    output, count = re.subn(
        r'(\bSOLIDS_PATH:\s*)"[0-9a-f]{64}"',
        lambda match: match.group(1) + f'"{solid_hash}"',
        text,
        count=1,
    )
    if count != 1:
        raise RuntimeError("could not patch SOLIDS_PATH expected hash exactly once")
    return output.encode("utf-8")


def set_artifact_identity(manifest, relative_path, data):
    record = manifest.get("required_generated_artifacts", {}).get(relative_path)
    if record is None:
        raise RuntimeError(f"manifest lacks required artifact record: {relative_path}")
    record["raw_byte_sha256"] = sha_bytes(data)
    record["byte_length"] = len(data)


def candidate_runtime_result(base, candidate_id, selected):
    current = copy.deepcopy(base)
    current["selected_candidate_id"] = candidate_id
    current["blocker"] = (
        "selected candidate C1 and complete suite have not been run"
        if selected
        else "isolated HOP gate has not been run"
    )
    return current


def candidate_vectors(base, selected_offset):
    vectors = copy.deepcopy(base)
    if selected_offset is None:
        return vectors
    hop = next(vector for vector in vectors["vectors"] if vector["id"] == "RT_HOP_SUCCESS")
    allowed = [float(value) for value in hop["controller_commands"]["timing_offsets_m"]]
    if not any(abs(selected_offset - value) <= 1e-9 for value in allowed):
        raise RuntimeError("selected Hop offset is outside preregistered values")
    hop["controller_commands"]["selected_timing_offset_m"] = selected_offset
    return vectors


def candidate_manifest(
    base,
    top,
    candidate_id,
    solid_bytes,
    adapter_bytes,
    vectors_bytes,
    runtime_result_bytes,
    selected_offset,
):
    manifest = copy.deepcopy(base)
    solid_hash = sha_bytes(solid_bytes)
    manifest["hard_geometry"]["credited_classes"]["HOP_BAR_01"]["top_y_m"] = top
    manifest["hard_geometry"]["mesh_artifact"]["raw_byte_sha256"] = solid_hash
    manifest["hard_geometry"]["mesh_artifact"]["byte_length"] = len(solid_bytes)
    for relative_path, data in [
        ("world/generated/solid_meshes.json", solid_bytes),
        ("scripts/p1a_world_data.gd", adapter_bytes),
        ("tests/fixtures/runtime_vectors.json", vectors_bytes),
        ("evidence/runtime_vector_results.json", runtime_result_bytes),
    ]:
        set_artifact_identity(manifest, relative_path, data)
    if selected_offset is None:
        manifest["status"] = (
            f"HOP CANDIDATE {candidate_id} MATERIALIZED — isolated four-question gate and C1 NOT PERFORMED; "
            "full suite blocked"
        )
        manifest["hop_gate_correction"]["status"] = "CANDIDATE_MATERIALIZED"
        manifest["hop_gate_correction"]["active_candidate"] = {
            "candidate_id": candidate_id,
            "top_y_m": top,
            "selection_status": "NOT TESTED",
        }
    else:
        manifest["status"] = (
            f"HOP CANDIDATE {candidate_id} SELECTED BY ISOLATED GATE — C1 NOT PERFORMED; full suite blocked"
        )
        manifest["hop_gate_correction"]["status"] = "SELECTED_ISOLATED_GATE_PASS_C1_PENDING"
        manifest["hop_gate_correction"]["active_candidate"] = {
            "candidate_id": candidate_id,
            "top_y_m": top,
            "selection_status": "ISOLATED_GATE_PASS_C1_PENDING",
            "selected_timing_offset_m": selected_offset,
        }
    return manifest


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-root", default=str(pathlib.Path(__file__).resolve().parents[1]))
    parser.add_argument("--output-root", required=True)
    parser.add_argument("--candidate-id", required=True)
    parser.add_argument("--selected-hop-offset-m", type=float)
    args = parser.parse_args()

    source = pathlib.Path(args.source_root).resolve()
    output = pathlib.Path(args.output_root).resolve()
    if source == output:
        raise SystemExit("source and output roots must differ")
    if output.exists():
        shutil.rmtree(output)
    shutil.copytree(source, output, ignore=shutil.ignore_patterns("PACKET_SHA256SUMS.txt"))

    registry = load(source / "world/generated/hop_bar_bracket_candidates.json")
    matches = [entry for entry in registry["candidates"] if entry["candidate_id"] == args.candidate_id]
    if len(matches) != 1:
        raise SystemExit(f"candidate ID must resolve exactly once: {args.candidate_id}")
    entry = matches[0]
    top = float(entry["top_y_m"])

    if sha(source / "world/generated/solid_meshes.json") != registry["base_solid_meshes_raw_sha256"]:
        raise SystemExit("base solid raw hash mismatch")
    if sha(source / "world/p1a_world_manifest.json") != registry["base_world_manifest_raw_sha256"]:
        raise SystemExit("base manifest raw hash mismatch")

    solid = candidate_solid(load(source / "world/generated/solid_meshes.json"), top)
    solid_bytes = raw_json(solid)
    solid_hash = sha_bytes(solid_bytes)
    if solid_hash != entry["solid_meshes_raw_byte_sha256"] or len(solid_bytes) != entry["solid_meshes_byte_length"]:
        raise SystemExit("candidate solid does not match registry")

    adapter_bytes = patch_adapter((source / "scripts/p1a_world_data.gd").read_text(encoding="utf-8"), solid_hash)
    if sha_bytes(adapter_bytes) != entry["candidate_world_data_adapter_raw_byte_sha256"]:
        raise SystemExit("candidate world-data adapter does not match registry")

    vectors = candidate_vectors(load(source / "tests/fixtures/runtime_vectors.json"), args.selected_hop_offset_m)
    vectors_bytes = raw_json(vectors)
    current = candidate_runtime_result(
        load(source / "evidence/runtime_vector_results.json"),
        args.candidate_id,
        args.selected_hop_offset_m is not None,
    )
    current_bytes = raw_json(current)

    manifest = candidate_manifest(
        load(source / "world/p1a_world_manifest.json"),
        top,
        args.candidate_id,
        solid_bytes,
        adapter_bytes,
        vectors_bytes,
        current_bytes,
        args.selected_hop_offset_m,
    )
    manifest_bytes = raw_json(manifest)
    if args.selected_hop_offset_m is None:
        if sha_bytes(current_bytes) != entry["candidate_runtime_results_raw_byte_sha256"]:
            raise SystemExit("candidate runtime-result identity does not match registry")
        if (
            sha_bytes(manifest_bytes) != entry["candidate_world_manifest_raw_byte_sha256"]
            or len(manifest_bytes) != entry["candidate_world_manifest_byte_length"]
        ):
            raise SystemExit("candidate manifest does not match registry")

    write_bytes(output / "world/generated/solid_meshes.json", solid_bytes)
    write_bytes(output / "scripts/p1a_world_data.gd", adapter_bytes)
    write_bytes(output / "tests/fixtures/runtime_vectors.json", vectors_bytes)
    write_bytes(output / "evidence/runtime_vector_results.json", current_bytes)
    write_bytes(output / "world/p1a_world_manifest.json", manifest_bytes)

    active = {
        "schema": "district_zero.p1a.hop_bar_active_candidate.v1",
        "authority_version": OVERLAY,
        "world_data_authority_version": WORLD,
        "candidate_id": args.candidate_id,
        "top_y_m": top,
        "status": (
            "SELECTED_ISOLATED_GATE_PASS_C1_PENDING"
            if args.selected_hop_offset_m is not None
            else "MATERIALIZED_NOT_TESTED"
        ),
        "selected_timing_offset_m": args.selected_hop_offset_m,
        "registry_identity": entry,
        "allowed_geometry_delta": "HOP_BAR_01 top y only",
        "human_world_gate": "NOT PERFORMED",
        "P1B": "FROZEN",
    }
    dump(output / "world/generated/hop_bar_active_candidate.json", active)
    packet_sums(output)
    print(
        json.dumps(
            {
                "status": "PASS",
                "candidate_id": args.candidate_id,
                "top_y_m": top,
                "output_root": str(output),
                "solid_meshes_sha256": sha(output / "world/generated/solid_meshes.json"),
                "world_manifest_sha256": sha(output / "world/p1a_world_manifest.json"),
                "selected_timing_offset_m": args.selected_hop_offset_m,
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
