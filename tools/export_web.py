#!/usr/bin/env python3
"""Export the current game in a disposable cache with pinned Web tooling."""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import zipfile

from launch import EXPECTED_VERSION, LaunchError, resolve_engine

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_SHA256 = "b7b7d7da29fc6cc2f4934fdd26cc571a40e7af57f716ea3eb7e18da720dae28a"
PRESET = "Web Single Thread"


def sha(data):
    return hashlib.sha256(data).hexdigest()


def default_template():
    if sys.platform == "darwin":
        base = Path.home() / "Library/Application Support/Godot"
    elif os.name == "nt":
        base = Path(os.environ["APPDATA"]) / "Godot"
    else:
        base = Path(os.environ.get("XDG_DATA_HOME", str(Path.home()/".local/share"))) / "godot"
    return base / "export_templates/4.7.1.stable/web_nothreads_release.zip"


def source_files():
    # Include current working source, including new assets; never copy caches.
    return sorted(p for p in (ROOT / "game").rglob("*") if p.is_file()
                  and not any(part.startswith(".") or part == "__pycache__"
                              for part in p.relative_to(ROOT / "game").parts)
                  and p.suffix not in {".log", ".pyc", ".zip", ".pck"}
                  and p.name not in {"override.cfg", "export_credentials.cfg"})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--godot")
    parser.add_argument("--template", type=Path, default=default_template())
    parser.add_argument("--output", type=Path, required=True, help="New output directory; never overwritten")
    parser.add_argument("--smoke", action="store_true", help="Separate diagnostic entry; never use as the playable artifact")
    parser.add_argument("--courier-smoke", action="store_true", help="Separate first-courier diagnostic entry")
    parser.add_argument("--alpha-smoke", action="store_true", help="Separate three-job alpha diagnostic entry")
    args = parser.parse_args()
    if sum([args.smoke, args.courier_smoke, args.alpha_smoke]) > 1:
        parser.error("Choose one diagnostic entry")
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
    record = {"engine": version, "template_sha256": TEMPLATE_SHA256, "diagnostic_entry": args.smoke or args.courier_smoke or args.alpha_smoke,
              "source_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
              "source_sha256": inputs, "commands": [], "status": "INCOMPLETE"}
    try:
        with tempfile.TemporaryDirectory(prefix="hush-web-") as temporary:
            stage = Path(temporary) / "game"
            for name in inputs:
                target = stage / name
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / "game" / name, target)
            if args.smoke or args.courier_smoke or args.alpha_smoke:
                diagnostic = ROOT / ("tools/alpha_web_smoke.gd" if args.alpha_smoke else "tools/courier_web_smoke.gd" if args.courier_smoke else "tools/web_smoke.gd")
                record["diagnostic_kind"] = "alpha_loop" if args.alpha_smoke else "courier" if args.courier_smoke else "run_v0"
                record["diagnostic_script_sha256"] = sha(diagnostic.read_bytes())
                shutil.copyfile(diagnostic, stage / "web_smoke.gd")
                (stage / "web_smoke.tscn").write_text('[gd_scene load_steps=2 format=3]\n[ext_resource type="Script" path="res://web_smoke.gd" id="1"]\n[node name="WebSmoke" type="Node"]\nscript = ExtResource("1")\n')
                settings = stage / "project.godot"
                main_entries = ['run/main_scene="res://scenes/district_zero_run.tscn"',
                                'run/main_scene="res://review/alpha_loop/alpha_review.tscn"',
                                'run/main_scene="res://scenes/district_zero_courier.tscn"']
                entries = [entry for entry in main_entries if entry in settings.read_text()]
                if len(entries) != 1:
                    raise LaunchError("Smoke entry expects the documented full-game main scene")
                settings.write_text(settings.read_text().replace(entries[0],
                                    'run/main_scene="res://web_smoke.tscn"'))
            # Only the disposable preset receives this machine's template path.
            preset = stage / "export_presets.cfg"
            preset.write_text(preset.read_text().replace('custom_template/release=""',
                              'custom_template/release=' + json.dumps(str(template))))
            for label, flags in [("import", ["--editor", "--import", "--quit"]),
                                 ("export", ["--export-release", PRESET, str(web / "index.html")])]:
                command = [str(engine), "--headless", "--path", str(stage), *flags]
                record["commands"].append(command)
                result = subprocess.run(command, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=300)
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
        record["hosting"] = ("PAGES_PLUS_LARGE_ASSET_HOST" if any(f["bytes"] > 25*1024*1024 for f in record["files"])
                             else "DIRECT_PAGES_OK")
        record["status"] = "EXPORTED_RUNTIME_NOT_VERIFIED"
    finally:
        (out / "build.json").write_text(json.dumps(record, indent=2) + "\n")
    print(json.dumps({k: v for k, v in record.items() if k not in {"source_sha256", "commands"}}, indent=2))


if __name__ == "__main__":
    try:
        main()
    except (LaunchError, OSError, subprocess.SubprocessError) as error:
        sys.exit(str(error))
