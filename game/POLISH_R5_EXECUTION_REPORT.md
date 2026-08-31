# District Zero P1A — Polish R5 execution report

## Outcome

`AUTOMATION PASS — POLISH R5 READY FOR OWNER REVIEW`

This is not P1A PASS and does not authorize the Human World Gate. No human
attempt was conducted. P1B remains frozen.

## Baseline and engine

- Immutable baseline: checksum-clean Robustness R4 player project.
- Baseline inventory: `2,247/2,247 PASS`.
- Exact engine: `4.7.1.stable.official.a13da4feb` at
  `/opt/homebrew/bin/godot`.
- Work was performed in a new R5 successor root; the R4 project was not edited.

## Selected delta

- HUD, route panel, pause card, minimap hierarchy, and development wording.
- Procedural sky/horizon only; sun, shadows, ambient light, tonemapping, and
  fog state remain frozen.
- Noncolliding node-marker ring/center mesh at the exact existing positions.
- Standalone launcher identity and duplicate-launch lock.

One larger marker-ring candidate was rejected because it failed one frozen A1
render-owner ray. The selected bounded ring restored `14/14` frozen rays.
Terrain-edge polish was studied but not materialized: the visible jagged bands
are discrete frozen terrain surface-class transitions, not missing wall faces.

## Exact automated results

- Polish R5 behavior: `19/19 PASS`.
- Repaired R1 semantics: `65/65 PASS`.
- v1.2.8 semantics: `45/45 PASS`.
- Native visual acceptance: `21/21 PASS`.
- Frozen native rays: `14/14 PASS`, zero mismatches.
- Registered-start native sweep: `14/14 PASS`, maximum camera pull-in `0.0 m`.
- Inherited R3 behavior: `38/39`; only the deliberately superseded exact R3
  title assertion failed. All geometry, normals, triangles, two-sided
  materials, collision, and camera checks passed.
- C1: two `1,260`-tick traces, raw bytes identical, maximum absolute
  difference `0.0`.
- Native Metal standalone smoke: `180` frames, one logical runtime-ready event,
  zero ordinary-play telemetry JSONL lines, zero recognized errors.
- Actual launcher smoke: return code `0`; lock removed afterward.
- Concurrent-launch test: first launcher return `0`, second launch refused with
  return `2`, lock removed afterward.
- Preservation: `21` authorized changed/added/renamed paths, `0` unauthorized;
  six protected scene nodes and all builder bytes outside the marker region are
  byte-identical to R4.

## Crash/cache robustness evidence

During final capture a forgotten headless vehicle-preview process (PID `3381`)
was found alive. Concurrent exact-engine launches then reproduced a native
Metal shader-conversion crash. The process, project-local `.godot` cache, and
R5-specific Godot user shader/log cache were preserved before recovery.
Terminating the stale process and rebuilding generated state restored clean
exact-engine execution. No gameplay or presentation source repair was used to
hide the crash. The launcher now prevents two copies of this R5 project from
starting concurrently.

## Stop boundary

Owner feel and the Human World Gate are not marked passed. The next action is
Charlie's ordinary owner review of the packaged Polish R5 player project.
