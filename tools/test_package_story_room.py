#!/usr/bin/env python3
"""Focused allowlist, identity and refusal checks for the portable packet."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import zipfile

import package_story_room as bundle


class PacketTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.root = self.base / "source"
        self.out = self.base / "packet.zip"
        for name in (*bundle.SOURCES, *(f"docs/story_room/{n}" for n in bundle.CORE)):
            path = self.root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(f"Content from {name}\n", encoding="utf-8")
        self.git = patch.object(bundle, "git_identity", return_value={
            "git_head": "a" * 40, "git_branch": "fixture"})
        self.git.start()
        self.addCleanup(self.git.stop)

    def test_exact_bytes_manifest_aggregate_and_allowlist(self):
        room = self.root / "docs/story_room"
        (room / "LOOP_SPEC.md").write_text("Prompt stays separate.\n")
        (room / "credentials.json").write_text("excluded fixture")
        (room / "old.zip").write_bytes(b"excluded fixture")
        (room / "nested").mkdir()
        (room / "nested/UNLISTED.md").write_text("excluded fixture")
        result = bundle.package(self.root, self.out)
        self.assertEqual(result["status"], "PASS")
        with zipfile.ZipFile(self.out) as archive:
            manifest = json.loads(archive.read("manifest.json"))
            self.assertEqual(manifest["implemented_game_commit"], bundle.IMPLEMENTED_GAME_COMMIT)
            self.assertEqual(manifest["git_head"], "a" * 40)
            self.assertEqual(set(archive.namelist()), set(manifest["files"]) | {"manifest.json"})
            for name, record in manifest["files"].items():
                data = archive.read(name)
                self.assertEqual(record, {"sha256": bundle.sha(data), "bytes": len(data)})
                if name != "writer_packet.md":
                    self.assertEqual(data, (self.root / name).read_bytes())
            aggregate = archive.read("writer_packet.md").decode()
            for name in bundle.CORE:
                self.assertIn(f"Source: `docs/story_room/{name}`", aggregate)
            self.assertNotIn("Prompt stays separate", aggregate)
            self.assertNotIn("excluded fixture", "\n".join(archive.namelist()))
            self.assertNotIn("docs/story_room/credentials.json", archive.namelist())
            self.assertNotIn("docs/story_room/old.zip", archive.namelist())
            self.assertNotIn("docs/story_room/nested/UNLISTED.md", archive.namelist())

    def test_overwrite_and_inside_source_refused(self):
        self.out.write_bytes(b"preserve")
        with self.assertRaisesRegex(ValueError, "no overwrite"):
            bundle.package(self.root, self.out)
        self.assertEqual(self.out.read_bytes(), b"preserve")
        with self.assertRaises(ValueError):
            bundle.package(self.root, self.root / "packet.zip")

    def test_source_symlinks_refused(self):
        path = self.root / bundle.SOURCES[0]
        target = self.base / "outside"
        target.write_text("do not package")
        path.unlink()
        path.symlink_to(target)
        with self.assertRaisesRegex(ValueError, "Symlink source"):
            bundle.package(self.root, self.out)
        self.assertFalse(self.out.exists())

    def test_ancestor_symlink_and_directory_refused(self):
        room = self.root / "docs/story_room"
        moved = self.base / "moved"
        room.rename(moved)
        room.symlink_to(moved, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, "Symlink source"):
            bundle.package(self.root, self.out)
        room.unlink()
        moved.rename(room)
        (room / "folder.md").mkdir()
        with self.assertRaisesRegex(ValueError, "not a regular file"):
            bundle.package(self.root, self.out)


if __name__ == "__main__":
    unittest.main()
