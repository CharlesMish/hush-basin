# Changelog

Notable changes to this project are recorded here. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/). The project has no version number, so entries are dated (CT). New tags are not used for now. The existing tag `r7-owner-review-github-baseline` is historical.

## [Unreleased]

### Added
- Charter (`docs/CHARTER.md`), MIT license (`LICENSE`), and this changelog.
- README introduction that defines the craft, Spread, Drive, Hop, Run, and BRRR, and links to the browser build.

### Changed
- The README and CONTRIBUTING.md no longer use internal agent or approval language.
- Docs that said to keep the repository private now say that it is public (`AGENTS.md`, `docs/SOURCE_PROVENANCE.md`, `docs/GITHUB_SETUP.md`).

### Fixed
- The first-setup check in CONTRIBUTING.md now names the verifier that applies to `main` (`tools/verify_quarto_vehicle.py`). `tools/verify_repo.py` still checks the older R7 inventory.
- `docs/QUARTO_VEHICLE_V1.md` no longer describes the vehicle as a pending candidate.

## 2026-09-07

This entry covers `5845088` through `df22187`. All five commits were pushed to `main` directly, with no pull requests. Status records keep their failures on the record. For example, Quiet Surfaces missed the 10% frame-time target on one moving workload (+14.61%, `STATUS.md`).

### Added
- Initial repository (Aug 30):
  - the playable R7 vehicle-integration build in `game/`
  - the frozen P1B gameplay and reward design study
  - the `tools/verify_repo.py` and `tools/launch.py` helpers

  This commit is tagged `r7-owner-review-github-baseline` (`5845088`).
- Run v0 (Sep 2): a timed drive from Quarry to Relay with a clock and the provisional BRRR score (`3b245da`).
- World Polish v1 (Sep 5): three connected yards, terrain transitions, architectural detail, palette, sky and light, and the map (`9fd4c02`).
- Warm Overcast v1 (Sep 5): a fixed-seed cloud sky and native drizzle (`9fd4c02`).
- Working Neighborhood v1 (Sep 5): 14 buildings and six landmark families with uses, façades, signs, and wear (`9fd4c02`).
- Quiet Surfaces v1 (Sep 5): road and ground materials. This pass added charcoal paving, cleaner road edges, twelve resurfacing patches, and six service covers, with no change to collision or handling (`9fd4c02`).
- Native vehicle rig adapted from Quarto's shape (Sep 5), with the F6 comparison view, the vehicle studio, and a browser geometry preview (`0b0cc10`, from `feature/quarto-native-vehicle-v1`).
- Full-game checkpoint on `main` (Sep 7), with a native verification record (`docs/QUARTO_MAIN_CHECKPOINT_20260907.md`) and `PLAY_FULL_GAME.command` (`df22187`).

### Fixed
- Vehicle geometry test now reads render vertex and index arrays directly instead of rounded `Mesh.get_faces()` output. The runner adds a matched baseline world traversal and per-command logs (`df22187`).
