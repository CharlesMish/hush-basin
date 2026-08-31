# Repository Layout

## `game/`

The playable Godot project lives one level below the Git repository root so a
friendly GitHub README and portable tooling can coexist with the exact R7
snapshot. Open `game/project.godot` in Godot.

`game/VEHICLE_R7_SHA256SUMS.txt` binds 234 authoritative files. The repository
adds only that inventory file beside them. The three post-package editor UID
files and `.godot/` cache were deliberately excluded.

The largest generated files are kept in ordinary Git because they are below
GitHub's per-file limit and compress well. `.gitattributes` suppresses noisy
line diffs for those files without changing their bytes.

## `design/p1b-gameplay-reward-lab/`

This is the substantive 65-file snapshot of the completed overnight design
lab. Python bytecode caches were excluded. Its `NIGHTLY_STATE.json` is
`COMPLETE_FROZEN`; product gameplay is `NOT STARTED`.

Read `FINAL_RECOMMENDATION.md` for the selected three-job courier proof and
`DECISION_MATRIX.md` for the alternatives. The models and reports are design
evidence, not runtime dependencies.

## `tools/`

`verify_repo.py` checks the R7 inventory, frozen design-lab tree, tracked-file
hygiene, path portability, and GitHub file-size limits.

`launch.py` resolves exact Godot, prepares a clean script-class cache, checks
parse cleanliness, and either opens the game or runs a bounded headless smoke.
It writes only ignored `.godot/` state and temporary logs.

## `docs/`

Repository-facing documentation lives outside the verified game subtree. This
lets Git and GitHub guidance evolve without rewriting gameplay evidence.
