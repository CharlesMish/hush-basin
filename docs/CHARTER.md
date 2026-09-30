# Charter: the hush-basin repository

This page says what this project is for and what it is not. How to run it is in the [README](../README.md) and [CONTRIBUTING.md](../CONTRIBUTING.md). Rules for coding agents are in [AGENTS.md](../AGENTS.md), and notable changes are in [CHANGELOG.md](../CHANGELOG.md).

**Names.** The repository and its README title use **Hush Basin**. The Godot project, the in-game build label, the launchers, and older records use **District Zero**. This charter uses the names as the repository already does and renames nothing.

## 1. Purpose

This is a driving game made in Godot 4.7.1. You drive a small **craft** through a city district in warm drizzle. The district has named destinations: Quarry, Depot, Market, Relay, Works, and Clinic.

- The craft has two forms. **Spread** is the default and more maneuverable, and it tops out at about 17 m/s. **Drive** is the faster form, held with Shift.
- W/S thrust and brake, and A/D steer. In Spread, Space makes a **Hop**, which trades forward speed for lift.
- On `main`, the game opens a **Run**: a timed drive from Quarry to Relay. The results card shows the clock and **BRRR**, a provisional score for fast, sideways Drive motion. From the results you can retry or go back to free roam.

Demos showed that a story adds meaning and anticipation to the fun of the driving. For now, the game is being fleshed out as a story to build toward that. No story is on `main` yet. `main` is a working checkpoint of the driving, the city, and the vehicle.

The repository also holds the development record: a scope document for each change, verifiers, status reports with their failures left in, and a frozen design study for a three-job courier loop.

## 2. What it deliberately is not

- **Not a finished game or a release.** No finished-game or performance acceptance is claimed. One moving workload missed the 10% frame-time target (+14.61%).
- **Not a cross-platform claim.** Native verification ran on one Apple M5 / Metal machine.
- **Not yet a courier game on `main`.** Cargo, Credits, saves, and progression are not implemented there. Courier work exists only on the `review/` branches.
- **BRRR is not a balance claim.** It is a seed metric for observation.
- **No outside dependencies.** No external packages, assets, analytics, or network services are used.
- **The vehicle is not a Quarto model.** It is a presentation-only rig with no physics or collision parts.

## 3. Audience

- Charles, who plays each checkpoint and judges comfort and feel.
- Developers and coding agents who follow AGENTS.md and use the exact Godot build.
- External design reviewers, who read the `review/` branches.
- Browser players at https://hush-basin.cmish.dev/. The native Godot build is the reference. The browser build is a provisional play target, deployed separately, and its hosting records live on the `review/` branches.

The project is released under the MIT License (see [LICENSE](../LICENSE)). CONTRIBUTING.md describes a local workflow and does not invite outside contributions.

## 4. Voice

- Write plain, measured sentences. Say what was checked and what wasn't ("unjudged", "not certified"). Keep failures on the record. Don't rewrite them.
- The game's own words are *craft*, *Spread*, *Drive*, *Hop*, *Run*, and *BRRR*. Define each one where it first appears, and don't pile them up.
- Visual passes (World Polish, Warm Overcast, Working Neighborhood, Quiet Surfaces) are proper nouns.
- The README, CONTRIBUTING.md, this charter, and the game's text don't use internal agent or approval language such as "owner review", "director", "Codex", or "Charlie approved".
- Leave archival records as they are. That includes scope and status documents, inventories, P1A/P1B, R7, and the old gate names.
- No marketing language.

## 5. Versions and change record

- `main` holds the played, accepted checkpoint (`df22187`, Sep 7, 2026). Candidates live on `feature/` and `review/` branches. The review branches are snapshots published for review, and they have not been merged.
- Each change is a named pass with a version suffix, such as Run v0 or Quiet Surfaces v1. The four visual passes each have their own scope document, playtest card, SHA-256 inventory, and verifier. Earlier inventories are kept, not rewritten to make a new change pass.
- Notable changes are recorded in [CHANGELOG.md](../CHANGELOG.md), in Keep a Changelog style, with dates and commit SHAs. There is no version number.
- The engine is pinned exactly: Godot `4.7.1.stable.official.a13da4feb`.
- New tags are not used for now. The one existing tag, `r7-owner-review-github-baseline` (`5845088`, Aug 30, 2026), is historical.

## 6. Relationship to other repos

- [Quarto](https://github.com/CharlesMish/quarto) is a separate study of one vehicle transformation. The current craft uses a simplified rig adapted from Quarto's shape. It was an intermediate step, not a geometry export, and it changes nothing in Quarto.
- The two projects inform each other through motion, shape, and readability. Neither pins a version of the other. Quarto identifiers cited in older scope documents are archival.
- cmish.dev lists the game in its Workshop and links to the browser build.
