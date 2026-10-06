#!/usr/bin/env python3
"""Package only the story-room packet and its named source authorities; stdlib only."""
import argparse
import hashlib
import json
from pathlib import Path
import stat
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parents[1]
IMPLEMENTED_GAME_COMMIT = "5be7feeef34dbed468e007f5ff4de594d41b0f80"
CORE = (
    "STORY_CANON_CURRENT.md", "CHARACTER_LEDGER.md", "WORLD_AND_ROUTE_STORY_MAP.md",
    "WORLD_STATE_LEDGER.md", "SEED_PAYOFF_LEDGER.md", "NARRATIVE_RULES.md",
)
SOURCES = (
    "game/scripts/courier/chapter_text.gd", "game/scripts/courier/slices_text.gd",
    "docs/OPENING_CHAPTER_PLAN_V0_1.md", "docs/QUARRY_SLICE_V1_1.md",
    "docs/CHAPTER_3_SLICE_V1_1.md", "NARRATIVE_SLICES_REVIEW.md",
    "OPENING_CHAPTER_REVIEW.md", "OPENING_CHAPTER_UX_REVIEW.md",
)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def regular_bytes(root, name):
    path = root / name
    for component in (path, *path.parents):
        if component == root:
            break
        if component.is_symlink():
            raise ValueError(f"Symlink source rejected: {name}")
    if not stat.S_ISREG(path.stat().st_mode):
        raise ValueError(f"Source is not a regular file: {name}")
    return path.read_bytes()


def git_identity(root):
    def git(*args):
        return subprocess.check_output(["git", *args], cwd=root, text=True).strip()
    return {"git_head": git("rev-parse", "HEAD"),
            "git_branch": git("branch", "--show-current")}


def package(root, output):
    if root.is_symlink():
        raise ValueError("Symlink source root rejected.")
    root, output = root.resolve(), output.resolve()
    if output.is_relative_to(root) or output.exists():
        raise ValueError("Use a new ZIP path outside the source checkout; no overwrite.")
    room = root / "docs/story_room"
    names = {f"docs/story_room/{name}" for name in CORE}
    names.update(p.relative_to(root).as_posix() for p in room.glob("*.md"))
    names.update(SOURCES)
    # Top-level Markdown plus the explicit source list is the complete allowlist.
    files = {name: regular_bytes(root, name) for name in sorted(names)}
    aggregate = ["# Hush Basin writer packet\n\n"
                 "Generated from the six core documents below. Their authority labels apply.\n"
                 "Prompts and source scripts remain separate files in this bundle.\n"]
    for name in CORE:
        path = f"docs/story_room/{name}"
        aggregate.append(f"\n---\n\nSource: `{path}`\n\n" + files[path].decode("utf-8"))
    files["writer_packet.md"] = "\n".join(aggregate).encode("utf-8")
    manifest = {"format": "hush-basin-story-room-bundle-v1", **git_identity(root),
                "implemented_game_commit": IMPLEMENTED_GAME_COMMIT,
                "snapshot": "Exact working-tree file bytes; Git HEAD alone does not identify uncommitted packet edits.",
                "generated": ["writer_packet.md"],
                "files": {n: {"sha256": sha(b), "bytes": len(b)} for n, b in files.items()}}
    encoded = (json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode("utf-8")
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "x", compression=zipfile.ZIP_DEFLATED) as archive:
        for name, data in {**files, "manifest.json": encoded}.items():
            info = zipfile.ZipInfo(name, date_time=(2026, 10, 6, 0, 0, 0))
            info.create_system = 3
            info.external_attr = (stat.S_IFREG | 0o644) << 16
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, data)
    with zipfile.ZipFile(output) as archive:
        if archive.testzip() is not None or set(archive.namelist()) != set(files) | {"manifest.json"}:
            raise ValueError("ZIP integrity or entry-set verification failed.")
        if archive.read("manifest.json") != encoded:
            raise ValueError("Manifest byte verification failed.")
        for name, data in files.items():
            if archive.read(name) != data:
                raise ValueError(f"ZIP byte verification failed: {name}")
    return {"status": "PASS", "zip": str(output), "bytes": output.stat().st_size,
            "sha256": sha(output.read_bytes()), "files": len(files),
            "git_head": manifest["git_head"], "git_branch": manifest["git_branch"]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True, help="Fresh ZIP path outside source")
    args = parser.parse_args()
    try:
        result = package(ROOT, args.output)
    except (OSError, ValueError, subprocess.CalledProcessError) as error:
        parser.error(str(error))
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
