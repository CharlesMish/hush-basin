#!/usr/bin/env python3
"""Exercise the two-need store, including real process exits/restarts; no game driving."""
import argparse
import json
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
ENGINE = "/Applications/Godot.app/Contents/MacOS/Godot"
EXPECTED_ENGINE = "4.7.1.stable.official.a13da4feb"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--godot", default=ENGINE)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    version = subprocess.check_output([args.godot, "--version"], text=True).strip()
    if version != EXPECTED_ENGINE:
        raise SystemExit(f"Expected {EXPECTED_ENGINE}; got {version}")
    commands = []
    observations = []
    checks = {}
    with tempfile.TemporaryDirectory(prefix="hush-relay-project-") as directory:
        save = str(Path(directory) / "project.json")

        def run(operation):
            index = len(observations)
            result_path = output / f"{index:02d}-{operation}.json"
            command = [args.godot, "--headless", "--path", str(ROOT / "game"),
                       "--log-file", str(output / f"{index:02d}-{operation}.engine.log"),
                       "--script", "res://tests/relay_project_probe.gd", "--",
                       "--save", save, "--operation", operation, "--result", str(result_path)]
            commands.append(command)
            completed = subprocess.run(command, text=True, capture_output=True, timeout=40)
            (output / f"{index:02d}-{operation}.console.log").write_text(completed.stdout + completed.stderr)
            if completed.returncode or not result_path.exists():
                raise RuntimeError(f"{operation} failed: {completed.stdout}\n{completed.stderr}")
            result = json.loads(result_path.read_text())
            observations.append(result)
            return result

        fresh = run("inspect")
        checks["fresh_process_starts_empty"] = fresh["load"]["status"] == "fresh" and fresh["state"]["stage"] == 0
        stock = run("stock")
        checks["first_process_contributes_stock"] = stock["event"]["changed"] and stock["state"]["stage"] == 1
        intermediate = run("inspect")
        checks["restart_recreates_intermediate_and_no_dispatch"] = intermediate["load"]["status"] == "loaded" and intermediate["state"]["stage"] == 1 and not intermediate["state"]["outbound_available"]
        receiver = run("receiver")
        checks["second_process_contributes_receiver"] = receiver["event"]["changed"] and receiver["state"]["stage"] == 2
        final = run("inspect")
        checks["restart_recreates_final_and_dispatch"] = final["load"]["status"] == "loaded" and final["state"]["stage"] == 2 and final["state"]["outbound_available"]
        replay = run("receiver")
        checks["restart_replay_is_idempotent"] = replay["event"]["status"] == "already_complete" and not replay["event"]["changed"]
        reset = run("reset")
        checks["owner_reset_commits_fresh_state"] = reset["event"]["ok"] and reset["state"]["stage"] == 0
        after_reset = run("inspect")
        checks["restart_after_reset_stays_fresh"] = after_reset["state"]["stage"] == 0 and not after_reset["state"]["outbound_available"]
        unit = run("unit")
        checks.update(unit["checks"])
        checks["every_restart_uses_a_distinct_process"] = len({row["pid"] for row in observations}) == len(observations)
    report = {"status": "PASS" if all(checks.values()) else "FAIL", "engine": version,
              "checks": checks, "count": len(checks), "processes": len(observations),
              "scope": "Finite save/state logic; integration must separately reproduce actual world meshes, dispatch and browser reloads."}
    (output / "commands.json").write_text(json.dumps(commands, indent=2) + "\n")
    (output / "result.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))
    raise SystemExit(0 if all(checks.values()) else 1)


if __name__ == "__main__":
    main()
