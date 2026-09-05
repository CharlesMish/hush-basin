#!/usr/bin/env python3
"""Launch the candidate or its isolated review scenes with the pinned engine."""

from pathlib import Path
import argparse
import subprocess
import sys

from launch import LaunchError, prepare_project, resolve_engine

ROOT = Path(__file__).resolve().parents[1]
SCENES = {
    "game": "res://scenes/district_zero_run.tscn",
    "compare": "res://scenes/quarto_vehicle_world_compare.tscn",
    "studio": "res://scenes/quarto_vehicle_studio.tscn",
}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--view", choices=SCENES, default="compare")
    parser.add_argument("--godot", help="Path to the existing exact engine")
    args = parser.parse_args()
    try:
        binary, version = resolve_engine(args.godot)
        prepare_project(binary, force_parse=True)
    except LaunchError as error:
        print(error, file=sys.stderr)
        return 2
    print(f"Quarto vehicle v1 candidate; {args.view}; engine {version}")
    return subprocess.call([
        str(binary), "--path", str(ROOT / "game"),
        "--resolution", "1280x720", SCENES[args.view],
    ])


if __name__ == "__main__":
    raise SystemExit(main())
