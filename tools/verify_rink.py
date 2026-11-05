#!/usr/bin/env python3
"""Verify the Hem Loop rink experiment against its recorded base.

Static (default, needs Git only):
  - every file tracked at the base commit is byte-identical, except the two
    AGENTS.md files, which may only gain a prepended Hem Loop section;
  - every added file lives under the rink's own paths;
  - project.godot still starts the story with its own user directory;
  - rink runtime code contains no file writes (no saves);
  - the course closes (tools/rink_layout.py --check).
--native additionally runs, with the exact Godot 4.7.1 engine:
  - the rink suite headless (tests/rink_suite.gd);
  - the contiguous story flow (tools/verify_slices.py --phase complete).
Evidence goes to a new --evidence directory.
"""
from __future__ import annotations

import argparse
import fnmatch
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE_COMMIT = "a9d7aceffb07fe6326bfa6021645d4a6d43c7755"
PREPENDED = {"AGENTS.md", "game/AGENTS.md"}
ADDED_PATTERNS = [
    "game/rink/*", "game/tests/rink_*", "tools/*rink*.py", "PLAY_RINK.command",
    "docs/HEM_LOOP_*", "HEM_LOOP_PLAY_CARD.md",
]
STORY_MAIN = 'run/main_scene="res://review/narrative_slices/review.tscn"'
STORY_USER_DIR = 'config/custom_user_dir_name="Hush Basin Relay Experiment v01"'
WRITE_PATTERNS = [r"FileAccess\.open\([^)]*WRITE", r"\.save\(", r"user://", r"ResourceSaver", r"DirAccess\.(make|remove|rename)"]


def git(*args: str) -> bytes:
    return subprocess.check_output(["git", *args], cwd=ROOT)


def static_checks() -> list[dict]:
    checks: list[dict] = []

    def check(cid: str, ok: bool, detail=None) -> None:
        checks.append({"id": cid, "pass": bool(ok), "detail": detail})

    tracked = {}
    for line in git("ls-tree", "-r", BASE_COMMIT).decode().splitlines():
        meta, name = line.split("\t", 1)
        tracked[name] = meta.split()[2]
    changed = []
    for name, blob in sorted(tracked.items()):
        path = ROOT / name
        same = path.is_file() and git("hash-object", str(path)).decode().strip() == blob
        if not same and name not in PREPENDED:
            changed.append(name)
    check("BASE_FILES_UNCHANGED", not changed, changed[:20])
    for name in sorted(PREPENDED):
        base = git("show", f"{BASE_COMMIT}:{name}").decode()
        now = (ROOT / name).read_text()
        check("PREPEND_ONLY:" + name, now.endswith(base) and "Hem Loop" in now[: len(now) - len(base)])
    current = set(git("ls-files", "--cached", "--others", "--exclude-standard").decode().splitlines())
    added = sorted(current - set(tracked))
    stray = [n for n in added if not any(fnmatch.fnmatch(n, p) for p in ADDED_PATTERNS)]
    check("ADDITIONS_SCOPED", not stray, stray)
    check("ADDITIONS_PRESENT", any(n.startswith("game/rink/") for n in added), len(added))
    settings = (ROOT / "game/project.godot").read_text()
    check("STORY_STARTUP_PRESERVED", settings.count(STORY_MAIN) == 1)
    check("STORY_USER_DIR_PRESERVED", settings.count(STORY_USER_DIR) == 1)
    offenders = []
    for path in sorted((ROOT / "game/rink").glob("*.gd")):
        text = path.read_text()
        for pattern in WRITE_PATTERNS:
            if re.search(pattern, text):
                offenders.append(f"{path.name}: {pattern}")
    check("RINK_WRITES_NO_FILES", not offenders, offenders)
    layout = subprocess.run([sys.executable, str(ROOT / "tools/rink_layout.py"), "--check"], capture_output=True, text=True)
    check("COURSE_CLOSES", layout.returncode == 0, layout.stdout.strip())
    scene = (ROOT / "game/rink/rink.tscn").read_text()
    check("RINK_USES_SHARED_CRAFT_AND_CAMERA", 'path="res://scenes/craft.tscn"' in scene and 'path="res://scripts/camera_rig.gd"' in scene
          and 'path="res://resources/default_tuning.tres"' in scene)
    return checks


def native_checks(evidence: Path) -> list[dict]:
    sys.path.insert(0, str(ROOT / "tools"))
    from launch import resolve_engine  # noqa: E402
    engine, version = resolve_engine(None)
    checks: list[dict] = []
    evidence.mkdir(parents=True, exist_ok=False)
    suite = evidence / "rink_suite.json"
    cmd = [str(engine), "--headless", "--fixed-fps", "60", "--path", str(ROOT / "game"),
           "--log-file", str(evidence / "rink_suite.log"), "--script", "res://tests/rink_suite.gd", "--", "--result", str(suite)]
    code = subprocess.run(cmd, cwd=ROOT, stdout=(evidence / "rink_suite.stdout").open("w"), stderr=subprocess.STDOUT, timeout=1800).returncode
    data = json.loads(suite.read_text()) if suite.exists() else {}
    checks.append({"id": "NATIVE_RINK_SUITE", "pass": code == 0 and data.get("status") == "PASS",
                   "detail": {"exit": code, "checks": data.get("check_count"), "failed": data.get("failed"), "engine": version, "command": cmd}})
    story = evidence / "story_complete"
    code = subprocess.run([sys.executable, str(ROOT / "tools/verify_slices.py"), "--phase", "complete", "--output", str(story)],
                          cwd=ROOT, capture_output=True, text=True, timeout=1800).returncode
    record = json.loads((story / "command.json").read_text()) if (story / "command.json").exists() else {}
    checks.append({"id": "NATIVE_STORY_CONTIGUOUS_FLOW", "pass": code == 0 and record.get("status") == "PASS",
                   "detail": {"exit": code, "checks": record.get("checks"), "failed": record.get("failed")}})
    return checks


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--native", action="store_true")
    parser.add_argument("--evidence", type=Path, help="new directory for native evidence")
    args = parser.parse_args()
    report = {"schema": "hush_basin.hem_loop_verify.v1", "base_commit": BASE_COMMIT,
              "head": git("rev-parse", "HEAD").decode().strip(), "static": static_checks()}
    if args.native:
        if args.evidence is None:
            parser.error("--native needs --evidence /new/directory")
        report["native"] = native_checks(args.evidence.resolve())
    failures = [c["id"] for part in ("static", "native") for c in report.get(part, []) if not c["pass"]]
    report["status"] = "PASS" if not failures else "FAIL"
    report["failures"] = failures
    print(json.dumps(report, indent=2))
    if args.evidence:
        (args.evidence.resolve() / "verify_rink.json").write_text(json.dumps(report, indent=2) + "\n")
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
