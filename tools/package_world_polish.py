#!/usr/bin/env python3
"""Package source without local caches, then verify an optional fresh extraction."""
from pathlib import Path
import argparse
import hashlib
import json
import stat
import zipfile

ROOT = Path(__file__).resolve().parents[1]
INVENTORY = 'QUIET_SURFACES_V1_SHA256SUMS.txt'
PREFIX = 'District-Zero-Quiet-Surfaces-V1'
SKIP_DIRS = {'.git', '.godot', '.import', '.mono', '__pycache__', 'build', 'builds',
             '.pytest_cache', '.idea', '.vscode', 'dist', 'exports', 'artifacts', 'run-output'}
SKIP_FILES = {'.DS_Store', 'export_credentials.cfg', 'override.cfg',
              'p1a_vehicle_r7_pose_probe.gd.uid', 'p1a_vehicle_r7_runner.gd.uid',
              'p1a_vehicle_r7_ui_probe.gd.uid'}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def included(path):
    rel = path.relative_to(ROOT)
    return (path.is_file() and not path.is_symlink()
            and not any(part in SKIP_DIRS for part in rel.parts)
            and path.name not in SKIP_FILES and not path.name.startswith('._')
            and path.suffix not in {'.zip', '.log', '.stdout', '.pyc', '.tmp'})


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--extract', type=Path)
    args = parser.parse_args()
    output = args.output.resolve()
    if output.is_relative_to(ROOT) or output.exists():
        parser.error('Use a new output ZIP outside source.')
    if args.extract and args.extract.exists():
        parser.error('Use a new extraction directory.')
    files = sorted(p for p in ROOT.rglob('*') if included(p) and p.name != INVENTORY)
    inventory = ROOT / INVENTORY
    inventory.write_text(''.join(f'{sha(p)}  {p.relative_to(ROOT).as_posix()}\n' for p in files))
    files.append(inventory)
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in sorted(files):
            name = PREFIX + '/' + path.relative_to(ROOT).as_posix()
            info = zipfile.ZipInfo(name, date_time=(2026, 9, 5, 0, 0, 0))
            info.create_system = 3
            info.external_attr = (stat.S_IFREG | stat.S_IMODE(path.stat().st_mode)) << 16
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, path.read_bytes(), compresslevel=9)
    with zipfile.ZipFile(output) as archive:
        assert archive.testzip() is None, 'ZIP CRC error'
        names = archive.namelist()
        assert len(names) == len(set(names)) == len(files)
        for path in files:
            assert archive.read(PREFIX + '/' + path.relative_to(ROOT).as_posix()) == path.read_bytes()
        if args.extract:
            args.extract.mkdir(parents=True)
            for info in archive.infolist():
                target = args.extract / info.filename
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(archive.read(info))
                target.chmod((info.external_attr >> 16) & 0o777)
    report = {'status': 'PASS', 'source_files': len(files), 'zip': str(output),
              'bytes': output.stat().st_size, 'sha256': sha(output),
              'crc_and_source_bytes': 'PASS',
              'extraction': str(args.extract.resolve() / PREFIX) if args.extract else None}
    output.with_suffix('.package.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
