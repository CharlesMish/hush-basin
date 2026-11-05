#!/usr/bin/env python3
"""Launch the Hem Loop rink natively with the exact Godot 4.7.1 engine.

The rink is its own scene (res://rink/rink.tscn): the usual story startup in
project.godot is untouched, and the rink writes no save file.
Set GODOT_BIN or pass --godot if Godot is not on PATH.
"""
import argparse, datetime, subprocess
from launch import ROOT, launch_lock, prepare_project, resolve_engine


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--godot", help="path to the exact Godot 4.7.1 executable")
    parser.add_argument("--compatibility", action="store_true", help="use the OpenGL Compatibility renderer (same as the Web build)")
    args = parser.parse_args()
    engine, version = resolve_engine(args.godot)
    prepare_project(engine, force_parse=True)
    logs = ROOT / "review_logs"
    logs.mkdir(exist_ok=True)
    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S-%f")
    print("Hem Loop ·", version,
          "\nW or Enter race the rink · C crew run (Tess at the Hem)"
          "\nW/S thrust · A/D steer · hold Shift Drive · Space Hop · R grid · Esc pause (T / C switch)", flush=True)
    command = [str(engine), "--path", str(ROOT / "game"), "--log-file", str(logs / f"rink-{stamp}.log")]
    if args.compatibility:
        command += ["--rendering-driver", "opengl3"]
    command.append("res://rink/rink.tscn")
    with launch_lock():
        return subprocess.call(command)


if __name__ == "__main__":
    raise SystemExit(main())
