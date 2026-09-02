#!/usr/bin/env python3
"""Verify the Git-friendly District Zero R7 repository snapshot."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path, PurePosixPath


ROOT = Path(__file__).resolve().parents[1]
GAME_ROOT = ROOT / "game"
DESIGN_ROOT = ROOT / "design" / "p1b-gameplay-reward-lab"
PROVENANCE_PATH = ROOT / "docs" / "SOURCE_PROVENANCE.json"
MANIFEST_PATH = GAME_ROOT / "VEHICLE_R7_SHA256SUMS.txt"

EXPECTED_MANIFEST_SHA256 = (
    "e178f1d4b50518107dbbba0e4bc3eb0c22b41baefce029ecc704c2f6d7fe130c"
)
EXPECTED_MANIFEST_RECORDS = 234
EXPECTED_DESIGN_FILES = 65
EXPECTED_DESIGN_TREE_SHA256 = (
    "150cfe8dcf9829595cfecbfbf7929f138da4d26efd42c6392eb91c8caf0ffe55"
)
GITHUB_HARD_FILE_LIMIT = 100 * 1024 * 1024
GITHUB_WARNING_FILE_SIZE = 50 * 1024 * 1024

REQUIRED_ROOT_FILES = {
    ".gitattributes",
    ".gitignore",
    "AGENTS.md",
    "CONTRIBUTING.md",
    "PLAY_RUN_V0.command",
    "README.md",
    "docs/GITHUB_SETUP.md",
    "docs/REPOSITORY_LAYOUT.md",
    "docs/RUN_V0.md",
    "docs/SOURCE_PROVENANCE.json",
    "docs/SOURCE_PROVENANCE.md",
    "tools/launch.py",
    "tools/verify_repo.py",
}

RUN_V0_GAME_OVERLAY_FILES = frozenset(
    {
        "game/scenes/district_zero_run.tscn",
        "game/scripts/run/brrr_seed.gd",
        "game/scripts/run/brrr_seed.gd.uid",
        "game/scripts/run/run_director.gd",
        "game/scripts/run/run_director.gd.uid",
        "game/scripts/run/run_hud.gd",
        "game/scripts/run/run_hud.gd.uid",
        "game/scripts/run/run_map_overlay.gd",
        "game/scripts/run/run_map_overlay.gd.uid",
    }
)

IGNORED_UNTRACKED_GAME_FILES = {
    "tests/p1a_vehicle_r7_pose_probe.gd.uid",
    "tests/p1a_vehicle_r7_runner.gd.uid",
    "tests/p1a_vehicle_r7_ui_probe.gd.uid",
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def parse_manifest(path: Path, errors: list[str]) -> dict[str, str]:
    records: dict[str, str] = {}
    if not path.is_file():
        errors.append(f"missing R7 manifest: {path.relative_to(ROOT)}")
        return records

    for line_number, raw_line in enumerate(
        path.read_text(encoding="utf-8").splitlines(), start=1
    ):
        match = re.fullmatch(r"([0-9a-f]{64})  (.+)", raw_line)
        if match is None:
            errors.append(f"malformed manifest record at line {line_number}")
            continue
        digest, relative = match.groups()
        pure = PurePosixPath(relative)
        if pure.is_absolute() or ".." in pure.parts or relative in {"", "."}:
            errors.append(f"unsafe manifest path at line {line_number}: {relative!r}")
            continue
        if relative in records:
            errors.append(f"duplicate manifest path: {relative}")
            continue
        records[relative] = digest
    return records


def design_tree_identity(root: Path) -> tuple[int, int, str]:
    def is_ignored_local_file(path: Path) -> bool:
        relative = path.relative_to(root)
        if any(part in {"__pycache__", ".pytest_cache", ".godot"} for part in relative.parts):
            return True
        if path.name == ".DS_Store" or path.name.startswith("._"):
            return True
        return path.suffix.lower() in {".pyc", ".pyo"}

    files = sorted(
        (
            path
            for path in root.rglob("*")
            if path.is_file() and not is_ignored_local_file(path)
        ),
        key=lambda path: path.relative_to(root).as_posix().encode("utf-8"),
    )
    rows: list[bytes] = []
    total_bytes = 0
    for path in files:
        relative = path.relative_to(root).as_posix()
        total_bytes += path.stat().st_size
        rows.append(f"{sha256_file(path)}  {relative}\n".encode("utf-8"))
    return len(files), total_bytes, hashlib.sha256(b"".join(rows)).hexdigest()


def git_output(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def tracked_paths() -> list[str] | None:
    probe = git_output("rev-parse", "--is-inside-work-tree")
    if probe.returncode != 0 or probe.stdout.strip() != "true":
        return None
    result = subprocess.run(
        ["git", "ls-files", "-z"],
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.decode("utf-8", errors="replace"))
    return [entry.decode("utf-8") for entry in result.stdout.split(b"\0") if entry]


def substantive_files_without_git() -> list[str]:
    paths: list[str] = []
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        relative = path.relative_to(ROOT)
        if any(part in {".git", ".godot", "__pycache__"} for part in relative.parts):
            continue
        if path.name == ".DS_Store" or path.name.startswith("._"):
            continue
        paths.append(relative.as_posix())
    return sorted(paths)


def is_forbidden_tracked_path(relative: str) -> bool:
    pure = PurePosixPath(relative)
    parts = set(pure.parts)
    name = pure.name
    lowered = name.lower()
    if parts.intersection({".godot", ".import", "__pycache__", "__MACOSX"}):
        return True
    if name == ".DS_Store" or name.startswith("._"):
        return True
    if lowered.endswith((".pyc", ".pyo", ".log", ".pid")):
        return True
    if lowered.endswith((".zip", ".7z", ".tar", ".tar.gz", ".dmg", ".pck")):
        return True
    if any(part.lower().endswith(".app") for part in pure.parts):
        return True
    return False


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--require-clean",
        action="store_true",
        help="also require a clean Git working tree",
    )
    args = parser.parse_args()

    errors: list[str] = []
    warnings: list[str] = []

    for relative in sorted(REQUIRED_ROOT_FILES):
        if not (ROOT / relative).is_file():
            errors.append(f"missing repository file: {relative}")

    try:
        provenance = json.loads(PROVENANCE_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"invalid provenance JSON: {exc}")
        provenance = {}
    if provenance.get("schema") != "district_zero.github_source_provenance.v1":
        errors.append("unexpected provenance schema")

    manifest_sha = sha256_file(MANIFEST_PATH) if MANIFEST_PATH.is_file() else ""
    if manifest_sha != EXPECTED_MANIFEST_SHA256:
        errors.append(
            f"R7 manifest SHA mismatch: expected {EXPECTED_MANIFEST_SHA256}, "
            f"observed {manifest_sha or 'MISSING'}"
        )

    manifest = parse_manifest(MANIFEST_PATH, errors)
    if len(manifest) != EXPECTED_MANIFEST_RECORDS:
        errors.append(
            f"R7 manifest count mismatch: expected {EXPECTED_MANIFEST_RECORDS}, "
            f"observed {len(manifest)}"
        )

    verified_records = 0
    for relative, expected_digest in sorted(manifest.items()):
        path = GAME_ROOT / relative
        if not path.is_file():
            errors.append(f"missing manifest-bound game file: {relative}")
            continue
        observed_digest = sha256_file(path)
        if observed_digest != expected_digest:
            errors.append(
                f"game SHA mismatch: {relative}: expected {expected_digest}, "
                f"observed {observed_digest}"
            )
            continue
        verified_records += 1

    tracked = tracked_paths()
    repository_files = tracked if tracked is not None else substantive_files_without_git()
    repository_set = set(repository_files)
    if tracked is not None:
        for relative in sorted(REQUIRED_ROOT_FILES):
            if relative not in repository_set:
                errors.append(f"required repository file is not tracked: {relative}")
    expected_r7_game = {f"game/{relative}" for relative in manifest}
    expected_r7_game.add("game/VEHICLE_R7_SHA256SUMS.txt")
    permitted_game = expected_r7_game | RUN_V0_GAME_OVERLAY_FILES
    actual_game = {relative for relative in repository_set if relative.startswith("game/")}
    unexpected_game = sorted(actual_game - permitted_game)
    missing_game = sorted(expected_r7_game - actual_game)
    for relative in unexpected_game:
        short = relative.removeprefix("game/")
        if tracked is not None or short not in IGNORED_UNTRACKED_GAME_FILES:
            errors.append(f"unexpected tracked game file: {relative}")
    for relative in missing_game:
        errors.append(f"manifest source is not tracked/present: {relative}")

    verified_run_overlay = 0
    for relative in sorted(RUN_V0_GAME_OVERLAY_FILES):
        if relative not in repository_set:
            errors.append(f"Run v0 overlay is not tracked/present: {relative}")
            continue
        if not (ROOT / relative).is_file():
            errors.append(f"Run v0 overlay file is missing: {relative}")
            continue
        verified_run_overlay += 1

    for relative in repository_files:
        if is_forbidden_tracked_path(relative):
            errors.append(f"forbidden repository path: {relative}")

    casefolded: dict[str, str] = {}
    for relative in repository_files:
        folded = relative.casefold()
        prior = casefolded.get(folded)
        if prior is not None and prior != relative:
            errors.append(f"case-colliding paths: {prior!r} and {relative!r}")
        casefolded[folded] = relative

    for relative in repository_files:
        path = ROOT / relative
        if path.is_symlink():
            errors.append(f"symlink is not allowed in the prepared source: {relative}")

    if not DESIGN_ROOT.is_dir():
        errors.append("missing frozen P1B design lab")
        design_count, design_bytes, design_sha = 0, 0, ""
    else:
        design_count, design_bytes, design_sha = design_tree_identity(DESIGN_ROOT)
        if design_count != EXPECTED_DESIGN_FILES:
            errors.append(
                f"design-lab count mismatch: expected {EXPECTED_DESIGN_FILES}, "
                f"observed {design_count}"
            )
        if design_sha != EXPECTED_DESIGN_TREE_SHA256:
            errors.append(
                f"design-lab tree SHA mismatch: expected {EXPECTED_DESIGN_TREE_SHA256}, "
                f"observed {design_sha}"
            )

    total_bytes = 0
    largest_path = ""
    largest_size = 0
    for relative in repository_files:
        path = ROOT / relative
        if not path.is_file() or path.is_symlink():
            continue
        size = path.stat().st_size
        total_bytes += size
        if size > largest_size:
            largest_size = size
            largest_path = relative
        if size >= GITHUB_HARD_FILE_LIMIT:
            errors.append(
                f"file reaches GitHub's 100 MiB hard limit: {relative} ({size} bytes)"
            )
        elif size >= GITHUB_WARNING_FILE_SIZE:
            warnings.append(f"large Git file: {relative} ({size} bytes)")

    if os.name != "nt":
        for relative in (
            "PLAY_RUN_V0.command",
            "tools/launch.py",
            "tools/verify_repo.py",
            "game/PLAY_DISTRICT_ZERO_VEHICLE_R7.command",
        ):
            path = ROOT / relative
            if path.is_file() and not os.access(path, os.X_OK):
                errors.append(f"launcher/verifier is not executable: {relative}")

    if args.require_clean:
        if tracked is None:
            errors.append("--require-clean needs an initialized Git repository")
        else:
            status = git_output("status", "--porcelain", "--untracked-files=all")
            if status.returncode != 0:
                errors.append(f"git status failed: {status.stderr.strip()}")
            elif status.stdout:
                errors.append("Git working tree is not clean")

    for warning in warnings:
        print(f"WARNING: {warning}")
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        print(f"FAILED: {len(errors)} repository issue(s)", file=sys.stderr)
        return 1

    mode = "tracked" if tracked is not None else "filesystem"
    print("PASS: District Zero repository source is GitHub-ready")
    print(f"R7 inventory: {verified_records}/{EXPECTED_MANIFEST_RECORDS} PASS")
    print(f"R7 manifest SHA-256: {manifest_sha}")
    print(
        f"Run v0 overlay: {verified_run_overlay}/"
        f"{len(RUN_V0_GAME_OVERLAY_FILES)} exact paths PASS"
    )
    print(f"P1B design lab: {design_count}/{EXPECTED_DESIGN_FILES} files PASS")
    print(f"P1B design tree SHA-256: {design_sha}")
    print(f"Repository scan mode: {mode}")
    print(f"Repository files scanned: {len(repository_files)}")
    print(f"Repository bytes: {total_bytes}")
    print(f"Largest file: {largest_path} ({largest_size} bytes)")
    print(f"Design-lab bytes: {design_bytes}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
