# Agent Instructions — District Zero Git Repository

Read this file before changing the repository. Read the nearest nested
`AGENTS.md` before changing anything under its directory.

## Current authority

- `game/` is the exact manifest-bound District Zero Vehicle Integration R7
  owner-review source. Its nested authority and verification documents control
  gameplay, world, movement, presentation, and evidence changes.
- `design/p1b-gameplay-reward-lab/` is a frozen design study. It is not product
  implementation authority and must remain unchanged unless the owner
  explicitly reopens the study.
- Repository-level documentation and helpers may improve portability and Git
  hygiene, but must not silently change game behavior or reinterpret evidence.

## Engine and verification

- Require Godot `4.7.1.stable.official.a13da4feb`; do not install, upgrade, or
  substitute an engine silently.
- Before changing the playable source, run `python3 tools/verify_repo.py` and
  record the clean R7 result.
- After repository-wrapper changes, rerun `python3 tools/verify_repo.py`.
- After an explicitly authorized gameplay successor, use its own versioned
  authority and evidence. Do not merely rewrite the R7 checksum inventory to
  make an unexplained change pass.

## Repository safety

- Never commit `.godot/`, import caches, logs, exports, archives, credentials,
  editor state, or Python caches.
- Do not broadly ignore `*.uid`; authoritative Godot UID files are tracked.
- Do not hand-edit the large generated world JSON/BIN files. Regeneration must
  be versioned, deterministic, and verified.
- Do not add external packages, assets, analytics, network services, or
  dependencies without explicit owner authorization and license review.
- Do not publish, push, create a remote, change repository visibility, or alter
  an external account unless the owner explicitly asks for that action.
- Never put a GitHub token or other secret in a remote URL, source file, log,
  or command transcript.

## Product boundary

- Preserve the R7 craft, world, movement, camera, terrain, routes, and current
  player exactly unless a later task explicitly authorizes a successor.
- Cosmetics remain presentation-only. They may not affect movement, cargo,
  payout, grade, routes, or telemetry semantics.
- P1B courier gameplay, economy, progression, trails, saves, and additional
  contracts remain unimplemented until a fresh authority explicitly selects
  their scope.
- Do not claim a Human World Gate, P1A PASS, P1B PASS, cross-platform physics
  determinism, or public-release readiness from automated checks alone.

## License and public release

No open-source license is currently granted. Keep the first remote private.
Public release requires a deliberate license and privacy review of frozen
historical provenance records.
