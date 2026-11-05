#!/usr/bin/env python3
"""Export the Hem Loop rink as its own single-thread Web build.

Same lane as tools/export_web.py: the exact Godot 4.7.1 engine, the pinned
`web_nothreads_release.zip` template (SHA-256 checked), the repository's
"Web Single Thread" preset, and a disposable staged copy of game/. Only the
disposable copy is edited: its main scene becomes the rink, its app/user-dir
names become Hem Loop's, and its pack is narrowed to the rink's dependencies.
The repository's project.godot, preset and story saves are never touched.

  python3 tools/export_rink_web.py --output /new/dir            # playable build
  python3 tools/export_rink_web.py --output /new/dir --zip      # + hem_loop_web.zip
  python3 tools/export_rink_web.py --output /new/dir --smoke    # browser checks build
"""
from __future__ import annotations

import argparse
import gzip
import json
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from export_web import PRESET, TEMPLATE_SHA256, default_template, sha, source_files  # noqa: E402
from launch import LaunchError, resolve_engine  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
RINK_SCENE = "res://rink/rink.tscn"
SMOKE_SCENE = "res://rink_web_smoke.tscn"
APP_NAME = "Hush Basin — Hem Loop"
USER_DIR = "Hush Basin Hem Loop v01"
STORY_MAIN = 'run/main_scene="res://review/narrative_slices/review.tscn"'
# Files the rink reads by path at runtime (FileAccess), beyond scene dependencies.
# Heavy resources no rink scene uses; everything else stays as in the story preset.
EXCLUDE = ("evidence/*,tools/*,review/quarto_vehicle_v1/*,presentation/generated/*,presentation/fine_ground/*,world/generated/*,tests/fixtures/*,"
           "presentation/narrative/ivo.png,presentation/narrative/bea.png,presentation/narrative/nell.png,presentation/narrative/ren.png")
RUNTIME_FILES = [
    "rink/hem_loop_course.json",
    "world/world_polish_v1.json",
    "presentation/warm_overcast_v1.json",
    "presentation/quarto_native_v1.json",
]

SERVE_PY = '''#!/usr/bin/env python3
"""Serve this folder on http://127.0.0.1:8765/ and open Hem Loop in the browser."""
import functools, http.server, os, socketserver, sys, threading, webbrowser
HERE = os.path.dirname(os.path.abspath(__file__))
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8765
Handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=os.path.join(HERE, "web"))
Handler.extensions_map = {**http.server.SimpleHTTPRequestHandler.extensions_map, ".wasm": "application/wasm", ".pck": "application/octet-stream"}
socketserver.TCPServer.allow_reuse_address = True
with socketserver.TCPServer(("127.0.0.1", PORT), Handler) as httpd:
    url = "http://127.0.0.1:%d/" % PORT
    print("Hem Loop is at " + url + "  (Ctrl+C to stop)")
    threading.Timer(0.8, lambda: webbrowser.open(url)).start()
    httpd.serve_forever()
'''

COMMAND = '''#!/bin/bash
# Double-click on macOS: serves the Web build locally and opens your browser.
cd "$(dirname "$0")" && exec python3 serve_hem_loop.py
'''

README = '''HEM LOOP · Hush Basin rink experiment (Web build)

1. Unzip anywhere.
2. macOS: double-click PLAY_IN_BROWSER.command
   Anywhere:   python3 serve_hem_loop.py
   (or any static server pointed at the web/ folder; file:// will not work)
3. A browser tab opens at http://127.0.0.1:8765/ — click the game once to focus.

W or Enter   race the rink (solo time trial; the clock starts at the line)
C            crew run (Tess is at the Hem with a jacket)
W/S thrust · A/D steer · hold Shift Drive · Space Hop (Spread only)
R back to the grid (fresh attempt) · Esc pause (then T time trial / C crew run)

Nothing is saved. Session bests reset when the tab closes.
Build record: web/build.json
'''


def stage_settings(stage: Path, main_scene: str) -> None:
    settings = stage / "project.godot"
    text = settings.read_text()
    if text.count(STORY_MAIN) != 1:
        raise LaunchError("Expected the story main scene in project.godot; refusing to guess.")
    text = text.replace(STORY_MAIN, 'run/main_scene="%s"' % main_scene)
    text = text.replace('config/name="Hush Basin — Narrative Chapters v0.1"', 'config/name="%s"' % APP_NAME)
    text = text.replace('config/custom_user_dir_name="Hush Basin Relay Experiment v01"', 'config/custom_user_dir_name="%s"' % USER_DIR)
    if 'custom_user_dir_name="%s"' % USER_DIR not in text:
        raise LaunchError("Could not isolate the rink's user directory in the staged project.")
    settings.write_text(text)


def stage_preset(stage: Path, template: Path, extra: list[str]) -> None:
    preset = stage / "export_presets.cfg"
    text = preset.read_text()
    replacements = {
        'include_filter="world/*.json,world/generated/*.json,world/generated/*.bin,presentation/*.json,tests/fixtures/*.json"':
            'include_filter="%s"' % ",".join(RUNTIME_FILES + extra),
        'exclude_filter="evidence/*,tools/*,review/quarto_vehicle_v1/*"': 'exclude_filter="%s"' % EXCLUDE,
        'custom_template/release=""': "custom_template/release=" + json.dumps(str(template)),
    }
    for before, after in replacements.items():
        if text.count(before) != 1:
            raise LaunchError("Unexpected export preset layout: " + before)
        text = text.replace(before, after)
    preset.write_text(text)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--godot")
    parser.add_argument("--template", type=Path, default=default_template())
    parser.add_argument("--output", type=Path, required=True, help="New output directory; never overwritten")
    parser.add_argument("--smoke", action="store_true", help="Main scene runs tests/rink_checks.gd in the browser")
    parser.add_argument("--zip", action="store_true", help="Also write hem_loop_web.zip with a local server")
    args = parser.parse_args()
    engine, version = resolve_engine(args.godot)
    template = args.template.expanduser().resolve()
    if not template.is_file() or sha(template.read_bytes()) != TEMPLATE_SHA256:
        raise LaunchError(f"Matching pinned single-thread release template required: {template}; expected SHA256 {TEMPLATE_SHA256}")
    out = args.output.resolve()
    if out.is_relative_to(ROOT / "game"):
        raise LaunchError("Output must be outside game/")
    out.mkdir(parents=True, exist_ok=False)
    web = out / "web"
    web.mkdir()
    inputs = {str(p.relative_to(ROOT / "game")): sha(p.read_bytes()) for p in source_files()}
    record = {
        "build": "hem-loop-web-smoke" if args.smoke else "hem-loop-web",
        "engine": version, "template_sha256": TEMPLATE_SHA256, "preset": PRESET,
        "main_scene": SMOKE_SCENE if args.smoke else RINK_SCENE,
        "source_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "source_dirty": bool(subprocess.check_output(["git", "status", "--porcelain", "--", "game", "tools"], cwd=ROOT, text=True).strip()),
        "source_sha256": inputs, "commands": [], "status": "INCOMPLETE",
    }
    try:
        with tempfile.TemporaryDirectory(prefix="hem-loop-web-") as temporary:
            stage = Path(temporary) / "game"
            for name in inputs:
                target = stage / name
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / "game" / name, target)
            scenes = [RINK_SCENE]
            extra: list[str] = []
            if args.smoke:
                (stage / "rink_web_smoke.tscn").write_text(
                    '[gd_scene load_steps=2 format=3]\n[ext_resource type="Script" path="res://tests/rink_checks.gd" id="1"]\n'
                    '[node name="HemLoopWebChecks" type="Node"]\nscript = ExtResource("1")\n')
                scenes = [SMOKE_SCENE, RINK_SCENE]
            stage_settings(stage, scenes[0])
            stage_preset(stage, template, extra)
            for label, flags in [("import", ["--editor", "--import", "--quit"]),
                                 ("export", ["--export-release", PRESET, str(web / "index.html")])]:
                command = [str(engine), "--headless", "--path", str(stage), *flags]
                record["commands"].append(command)
                result = subprocess.run(command, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=600)
                (out / (label + ".log")).write_text(result.stdout)
                if result.returncode or any(s in result.stdout for s in ["ERROR:", "Parse Error:", "Failed to export"]):
                    raise LaunchError(f"{label} failed; inspect {out / (label + '.log')}")
            if inputs != {str(p.relative_to(ROOT / "game")): sha(p.read_bytes()) for p in source_files()}:
                raise LaunchError("Source changed during export; retry from a stable working tree")
        for name in ["index.html", "index.js", "index.wasm", "index.pck"]:
            if not (web / name).is_file() or not (web / name).stat().st_size:
                raise LaunchError("Missing build output: " + name)
        with zipfile.ZipFile(template) as archive:
            if sha((web / "index.wasm").read_bytes()) != sha(archive.read("godot.wasm")):
                raise LaunchError("Exported WASM does not match pinned template")
        record["files"] = [{"name": p.name, "bytes": p.stat().st_size,
                            "gzip_bytes": len(gzip.compress(p.read_bytes(), mtime=0)),
                            "sha256": sha(p.read_bytes())} for p in sorted(web.iterdir()) if p.is_file()]
        record["raw_bytes"] = sum(f["bytes"] for f in record["files"])
        record["gzip_estimate_bytes"] = sum(f["gzip_bytes"] for f in record["files"])
        record["status"] = "EXPORTED_RUNTIME_NOT_VERIFIED"
    finally:
        (out / "build.json").write_text(json.dumps(record, indent=2) + "\n")
    (web / "build.json").write_text(json.dumps({k: v for k, v in record.items() if k not in {"source_sha256", "commands"}}, indent=2) + "\n")
    if args.zip and not args.smoke:
        bundle = out / "hem_loop_web.zip"
        with zipfile.ZipFile(bundle, "w", zipfile.ZIP_DEFLATED) as z:
            for p in sorted(web.iterdir()):
                z.write(p, "hem_loop_web/web/" + p.name)
            for name, body, mode in [("serve_hem_loop.py", SERVE_PY, 0o755), ("PLAY_IN_BROWSER.command", COMMAND, 0o755), ("README.txt", README, 0o644)]:
                info = zipfile.ZipInfo("hem_loop_web/" + name)
                info.external_attr = (0o100000 | mode) << 16
                info.compress_type = zipfile.ZIP_DEFLATED
                z.writestr(info, body)
        record["zip"] = {"path": str(bundle), "bytes": bundle.stat().st_size, "sha256": sha(bundle.read_bytes())}
        (out / "build.json").write_text(json.dumps(record, indent=2) + "\n")
    print(json.dumps({k: v for k, v in record.items() if k not in {"source_sha256", "commands"}}, indent=2))


if __name__ == "__main__":
    try:
        main()
    except (LaunchError, OSError, subprocess.SubprocessError) as error:
        sys.exit(str(error))
