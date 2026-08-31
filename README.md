# District Zero

District Zero is a clean-room Godot movement game built around a transforming
hover craft: **Spread** is controlled and terrain-friendly, while **Drive** is
fast, committed, and wonderfully drifty.

This repository snapshot contains the current playable **Vehicle Integration
R7 owner-review build** and the completed, frozen P1B gameplay/reward design
lab. R7 is fun and playable, but it is not labeled `P1A PASS`, and the courier
gameplay described in the design lab has not been implemented yet.

## Play it

Requirements:

- Godot `4.7.1.stable.official.a13da4feb` exactly
- Forward+ renderer
- Python 3.10+ for the portable verification and launch helpers

From the repository root:

```sh
python3 tools/verify_repo.py
python3 tools/launch.py
```

You can also import [`game/project.godot`](game/project.godot) directly in the
Godot project manager. On the validated Mac setup, double-clicking
[`game/PLAY_DISTRICT_ZERO_VEHICLE_R7.command`](game/PLAY_DISTRICT_ZERO_VEHICLE_R7.command)
uses the preserved R7 launcher.

The portable launcher searches `GODOT_BIN`, `godot`, `godot4`, and common
installation locations. To select an installation explicitly:

```sh
GODOT_BIN=/path/to/godot python3 tools/launch.py
```

Windows PowerShell equivalent:

```powershell
$env:GODOT_BIN = "C:\Path\To\Godot_v4.7.1-stable_win64.exe"
py -3 tools\verify_repo.py
py -3 tools\launch.py
```

## Controls

- `W / S`: thrust and brake
- `A / D`: steer
- `Shift`: hold Drive; release for Spread
- `Space`: Hop while supported in Spread
- `R`: reset
- `Tab`: diagnostic segments
- `F1`: telemetry
- `Escape`: pause

## Repository map

- [`game/`](game/) — exact 234-record R7 source snapshot plus its checksum
  inventory; runtime, world data, tests, and provenance are kept together.
- [`design/p1b-gameplay-reward-lab/`](design/p1b-gameplay-reward-lab/) — the
  frozen eight-iteration courier gameplay and reward study. It is planning,
  not active product code.
- [`tools/verify_repo.py`](tools/verify_repo.py) — validates source hashes,
  repository hygiene, size limits, and the frozen design-lab snapshot.
- [`tools/launch.py`](tools/launch.py) — cross-platform exact-engine preflight,
  clean import, parse check, smoke, and launch helper.
- [`docs/`](docs/) — repository layout, provenance, and GitHub setup guidance.

## Current verification boundary

The copied R7 inventory verifies `234/234`; its inventory SHA-256 is
`e178f1d4b50518107dbbba0e4bc3eb0c22b41baefce029ecc704c2f6d7fe130c`.
The substantive frozen design lab contains 65 files and reports `844/844`
aggregate pure checks. Human feel, fun, comfort, and future courier balancing
remain human decisions.

Run a clean engine preparation without opening a window:

```sh
python3 tools/launch.py --prepare-only
```

Run a bounded headless scene smoke:

```sh
python3 tools/launch.py --smoke-frames 180
```

## Git and large generated data

The repository is about 80 MiB before Git compression. Its largest file is a
deterministic generated JSON file of about 32.5 MiB, so Git LFS is not needed
for this snapshot. The large generated world files are marked as generated and
non-diffable; checksum review remains authoritative. If those files begin
changing frequently or grow substantially, revisit the storage policy before
committing them.

Because one file is larger than GitHub's browser-upload limit, publish this
repository with Git, GitHub Desktop, or another Git client—not drag-and-drop
browser upload.

## Development status

R7 is the current playable baseline. The next gameplay direction is summarized
in [`design/p1b-gameplay-reward-lab/FINAL_RECOMMENDATION.md`](design/p1b-gameplay-reward-lab/FINAL_RECOMMENDATION.md),
but that document does not authorize product implementation by itself. See
[`CONTRIBUTING.md`](CONTRIBUTING.md) and the nested `game/AGENTS.md` before
changing the playable source.

## Privacy and license

Start with a **private GitHub repository**. The exact historical snapshot
contains a few old local-path/provenance references and names its owner; no
credentials or secrets were found, but publishing those records is still a
privacy choice.

No license has been selected. Unless a `LICENSE` file is added, this repository
is not offered under an open-source license; all rights are reserved. Choose a
license deliberately before describing a public copy as open source.

See [`docs/GITHUB_SETUP.md`](docs/GITHUB_SETUP.md) for the safe first publish
and cross-machine workflow.
