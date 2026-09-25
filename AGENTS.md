# Current task — Opening Chapter v0.1

The owner accepted Narrative Presence Lab and explicitly authorized sections
2–6 and 13 of `docs/OPENING_CHAPTER_PLAN_V0_1.md`. Read
`OPENING_CHAPTER_REVIEW.md`, `START_OPENING_CHAPTER.md` and the current `STATUS.md`.
The new chapter extends accepted source `d8e921068819a86ca888aaa26d9bfbb9fb8e4476`.
Preserve vehicle, camera, cargo, scoring, world geometry and authored routes.
Only the named local Ren/Ivo/Tess work, anonymous receipts, minimal anchors and
cosmetic craft patch are authorized. No Chapter 2, additional faces, relationship
systems, production deployment, push or main update. Stop for owner review.
Use `tools/verify_opening_chapter.py` and `tools/verify_opening_preservation.py`;
historical inventories below remain provenance, not successor pass criteria.

---

# Previous task — Narrative Presence Lab v0.1

The owner's explicit narrative implementation request controls this branch.
Read `NARRATIVE_PRESENCE_REVIEW.md`, `START_NARRATIVE.md` and the current section
of `STATUS.md`. Preserve the reviewed `1afd28a253a3dbc0387cd3f339e5a56ab29dabf4`
gameplay/world source. New narrative files extend the existing courier logic;
the historical restrictions below apply only outside the newly authorized slice.
No main update, push, production deployment, third character or additional arc.
Stop for Charlie's playtest; automation cannot establish attachment or comfort.

---

# Current Web shell presentation

The owner confirmed production hosting works and authorized a shell-only sizing
and fullscreen pass. Preserve all game/native/export artifacts and private R2
routes. Version the presentation separately; never overwrite immutable build
HTML. See `docs/WEB_SHELL_PRESENTATION_V1.md`. No gameplay, HUD, mobile, renderer,
package, DNS, or resource-cleanup successor is part of this pass.

---

# Current production Web promotion

The owner accepted `SAME_ORIGIN_R2_HOSTING_PROVED` and explicitly authorized
production-named Pages/R2 resources, intentional promotion of the exact accepted
build to `hush-basin.cmish.dev`, and proof-resource cleanup after independent
production/domain verification. See `docs/PRODUCTION_WEB_V1.md`. Preserve the
proven same-origin architecture and all game/native source. No unrelated
Cloudflare properties, account R2 subscription, or gameplay successor is in scope.

---

# Current Cloudflare hosting proof

The owner accepted Web Feasibility v1 and authorized a temporary Pages/R2
preview to prove same-origin streaming of the exact accepted export. See
`docs/CLOUDFLARE_HOSTING_PROOF_V1.md`. This narrowly supersedes the earlier
no-deployment boundary. No production domain, release, unrelated resources,
game changes, package reduction, or alternate-origin shell work is authorized.

---

# Current Web feasibility task

Read `WEB_FEASIBILITY_V1_AUTHORITY.md` and `docs/WEB_FEASIBILITY_V1.md` first.
The owner authorized local single-thread Web export tooling from the September 7
played main checkpoint. Preserve native gameplay and Forward+; no deployment.
The prior vehicle and historical instructions follow unchanged.

---

# Current vehicle task

Read `QUARTO_VEHICLE_V1_AUTHORITY.md` and `docs/QUARTO_VEHICLE_V1.md` first on this branch. The owner explicitly requested building on the existing native rig after reviewing the Quarto visual successor proposal. That authorizes the bounded visual scene/rig changes and their comparison tools; inherited gameplay, world, camera, engine and publication boundaries remain. Use the new versioned vehicle verifier for this successor; preserve historical inventories and their truthful results. The inherited instructions follow unchanged.

---

# Agent Instructions — District Zero Git Repository

Current authority: QUIET_SURFACES_V1_AUTHORITY.md for the approved surface pass.
Previous authority: NEIGHBORHOOD_V1_AUTHORITY.md for the architecture pass.

Previous authority: WARM_OVERCAST_V1_AUTHORITY.md. The approved weather plan
supersedes the named historical presentation freezes and two carryover checks.

This is the isolated World Polish v1 successor. Read WORLD_POLISH_V1_AUTHORITY.md
first; the owner's approved plan supersedes the historical freezes below for
the fields it names. Verify using tools/verify_world_polish.py.

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
