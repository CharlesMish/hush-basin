#!/usr/bin/env python3
"""Prepare, smoke, or launch District Zero with the exact Godot engine."""

from __future__ import annotations

import argparse
import contextlib
import os
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Iterator


ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = ROOT / "game"
EXPECTED_VERSION = "4.7.1.stable.official.a13da4feb"
REQUIRED_CLASS_TOKEN = '"VehicleVisualRig"'
PARSE_ERROR_PATTERN = re.compile(
    r"SCRIPT ERROR:|Parse Error:|Failed to load script|"
    r"Could not resolve class|Cannot get class",
    re.IGNORECASE,
)


class LaunchError(RuntimeError):
    """A user-actionable exact-engine or project preparation failure."""


def candidate_binaries(explicit: str | None) -> Iterator[Path]:
    raw_candidates: list[str] = []
    if explicit:
        raw_candidates.append(explicit)
    if os.environ.get("GODOT_BIN"):
        raw_candidates.append(os.environ["GODOT_BIN"])
    for command in ("godot", "godot4"):
        resolved = shutil.which(command)
        if resolved:
            raw_candidates.append(resolved)
    raw_candidates.extend(
        [
            "/opt/homebrew/bin/godot",
            "/usr/local/bin/godot",
            "/Applications/Godot.app/Contents/MacOS/Godot",
            r"C:\Program Files\Godot\Godot_v4.7.1-stable_win64.exe",
        ]
    )
    seen: set[str] = set()
    for raw in raw_candidates:
        expanded = str(Path(raw).expanduser())
        key = os.path.normcase(os.path.abspath(expanded))
        if key in seen:
            continue
        seen.add(key)
        yield Path(expanded)


def engine_version(binary: Path) -> str | None:
    if not binary.is_file() or not os.access(binary, os.X_OK):
        return None
    try:
        result = subprocess.run(
            [str(binary), "--version"],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            timeout=20,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    if result.returncode != 0:
        return None
    return result.stdout.strip()


def resolve_engine(explicit: str | None) -> tuple[Path, str]:
    observed: list[str] = []
    for candidate in candidate_binaries(explicit):
        version = engine_version(candidate)
        if version is None:
            continue
        observed.append(f"{candidate}: {version}")
        if version == EXPECTED_VERSION:
            return candidate.resolve(), version
    detail = "\n".join(f"  {entry}" for entry in observed) or "  none found"
    raise LaunchError(
        f"District Zero requires exact Godot {EXPECTED_VERSION}.\n"
        f"Observed candidates:\n{detail}\n"
        "Set GODOT_BIN or pass --godot with the exact executable."
    )


def run_checked(
    label: str,
    command: list[str],
    log_path: Path,
    *,
    reject_parse_errors: bool = True,
) -> str:
    rendered = shlex.join(command)
    print(f"{label}: {rendered}")
    log_path.unlink(missing_ok=True)
    result = subprocess.run(
        command,
        cwd=PROJECT_ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    log_text = ""
    if log_path.is_file():
        log_text = log_path.read_text(encoding="utf-8", errors="replace")
    combined = "\n".join((result.stdout, result.stderr, log_text))
    if result.returncode != 0:
        raise LaunchError(
            f"{label} failed with process code {result.returncode}.\n{combined[-8000:]}"
        )
    if reject_parse_errors and PARSE_ERROR_PATTERN.search(combined):
        raise LaunchError(f"{label} reported a script/parse error.\n{combined[-8000:]}")
    return combined


def prepare_project(binary: Path, *, force_parse: bool) -> None:
    if not (PROJECT_ROOT / "project.godot").is_file():
        raise LaunchError(f"Godot project not found: {PROJECT_ROOT / 'project.godot'}")

    cache_path = PROJECT_ROOT / ".godot" / "global_script_class_cache.cfg"
    cache_ready = (
        cache_path.is_file()
        and cache_path.stat().st_size > 0
        and REQUIRED_CLASS_TOKEN
        in cache_path.read_text(encoding="utf-8", errors="replace")
    )

    with tempfile.TemporaryDirectory(prefix="district-zero-prepare-") as temp:
        temp_root = Path(temp)
        newly_imported = False
        if not cache_ready:
            print("Preparing District Zero's local Godot cache...")
            import_log = temp_root / "import.log"
            run_checked(
                "Godot import",
                [
                    str(binary),
                    "--headless",
                    "--editor",
                    "--path",
                    str(PROJECT_ROOT),
                    "--import",
                    "--quit",
                    "--log-file",
                    str(import_log),
                ],
                import_log,
            )
            newly_imported = True

        if not cache_path.is_file() or cache_path.stat().st_size == 0:
            raise LaunchError("Godot import did not generate a global script-class cache.")
        cache_text = cache_path.read_text(encoding="utf-8", errors="replace")
        if REQUIRED_CLASS_TOKEN not in cache_text:
            raise LaunchError("Godot's class cache does not resolve VehicleVisualRig.")

        if newly_imported or force_parse:
            parse_log = temp_root / "parse.log"
            run_checked(
                "Godot parse check",
                [
                    str(binary),
                    "--headless",
                    "--editor",
                    "--path",
                    str(PROJECT_ROOT),
                    "--quit-after",
                    "2",
                    "--log-file",
                    str(parse_log),
                ],
                parse_log,
            )


def pid_is_alive(pid: int) -> bool:
    if pid <= 0:
        return False
    if os.name == "nt":
        try:
            result = subprocess.run(
                ["tasklist", "/FI", f"PID eq {pid}", "/FO", "CSV", "/NH"],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
                timeout=10,
            )
        except (OSError, subprocess.TimeoutExpired):
            return False
        return result.returncode == 0 and f'"{pid}"' in result.stdout
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    except OSError:
        return False
    return True


@contextlib.contextmanager
def launch_lock() -> Iterator[None]:
    lock_root = Path(tempfile.gettempdir()) / "district-zero-github-ready.lock"
    pid_path = lock_root / "launcher.pid"
    try:
        lock_root.mkdir()
    except FileExistsError:
        prior_pid = -1
        try:
            prior_pid = int(pid_path.read_text(encoding="ascii").strip())
        except (OSError, ValueError):
            pass
        if pid_is_alive(prior_pid):
            raise LaunchError(
                f"District Zero is already running through this launcher (PID {prior_pid})."
            )
        try:
            pid_path.unlink(missing_ok=True)
            lock_root.rmdir()
            lock_root.mkdir()
        except OSError as exc:
            raise LaunchError(f"Could not clear stale launch lock: {lock_root}: {exc}") from exc

    pid_path.write_text(f"{os.getpid()}\n", encoding="ascii")
    try:
        yield
    finally:
        pid_path.unlink(missing_ok=True)
        try:
            lock_root.rmdir()
        except OSError:
            pass


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--godot", help="path to an exact Godot executable")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--verify-engine",
        action="store_true",
        help="only resolve and print the exact Godot identity",
    )
    mode.add_argument(
        "--prepare-only",
        action="store_true",
        help="import and parse-check the project, then stop",
    )
    mode.add_argument(
        "--smoke-frames",
        type=int,
        metavar="N",
        help="run the main scene headlessly for N frames, then stop",
    )
    args = parser.parse_args()

    if args.smoke_frames is not None and args.smoke_frames <= 0:
        parser.error("--smoke-frames must be a positive integer")

    try:
        binary, version = resolve_engine(args.godot)
        print(f"Godot: {binary}")
        print(f"Identity: {version}")
        print(f"Project: {PROJECT_ROOT}")

        if args.verify_engine:
            return 0

        prepare_project(binary, force_parse=args.prepare_only or args.smoke_frames is not None)
        if args.prepare_only:
            print("PASS: exact-engine import and parse preparation")
            return 0

        with launch_lock():
            log_path = Path(tempfile.gettempdir()) / "district-zero-github-ready.log"
            command = [str(binary)]
            if args.smoke_frames is not None:
                command.append("--headless")
            command.extend(["--path", str(PROJECT_ROOT), "--log-file", str(log_path)])
            if args.smoke_frames is not None:
                command.extend(["--quit-after", str(args.smoke_frames)])
                run_checked("Godot scene smoke", command, log_path)
                print(f"PASS: main scene remained clean for {args.smoke_frames} frames")
                return 0

            print("Launching District Zero...")
            result = subprocess.run(command, cwd=PROJECT_ROOT, check=False)
            if result.returncode != 0:
                raise LaunchError(
                    f"District Zero exited with process code {result.returncode}. "
                    f"Log: {log_path}"
                )
            return 0
    except LaunchError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    except KeyboardInterrupt:
        print("Interrupted.", file=sys.stderr)
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
