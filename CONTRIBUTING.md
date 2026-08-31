# Contributing and Local Development

District Zero is currently an owner-review project rather than an open-source
project. This guide describes a safe local workflow; it does not grant a
license or invite external contributions.

## First setup

1. Install exact Godot `4.7.1.stable.official.a13da4feb` and Python 3.10+.
2. Clone the repository with Git.
3. Run `python3 tools/verify_repo.py`.
4. Run `python3 tools/launch.py --prepare-only` once.
5. Run `python3 tools/launch.py` to play.

Godot will create `game/.godot/` locally. It is intentionally ignored and must
never be committed.

## Branch workflow

Keep `main` as the verified owner-review baseline. Use a narrowly named branch
for each authorized successor, for example:

```sh
git switch -c feature/p1b-c01-technical-gate
```

Before editing `game/`, read `game/AGENTS.md` and every document it requires.
The R7 checksum inventory is a baseline alarm: an intentional successor will
need a new versioned authority and inventory rather than a casual checksum
rewrite.

## Before a commit

```sh
python3 tools/verify_repo.py
git diff --check
git status --short
```

For an authorized engine change, also run:

```sh
python3 tools/launch.py --prepare-only
python3 tools/launch.py --smoke-frames 180
```

Run only the validation command named by the relevant authority. Historical
scripts under `game/tools/` preserve earlier evidence workflows; some manage
disposable output directories and are not a general-purpose test suite.

## Generated world data

The large files in `game/world/generated/` and
`game/presentation/generated/` are deterministic source data. Do not edit them
by hand, run formatters over them, or accept bulk line-ending changes. A future
regeneration must preserve its inputs, exact command, hashes, and runtime
validation.

## Commit quality

- Keep behavior, tests, and authority records in the same reviewable change.
- Never mix an engine/gameplay change with a cache cleanup or repository
  reorganization.
- Preserve executable mode on `.command` and shell launchers.
- Do not commit secrets, local paths, generated logs, archives, or personal
  editor settings.
- Do not add a license, publish a release, or push a remote without the owner's
  explicit decision.
