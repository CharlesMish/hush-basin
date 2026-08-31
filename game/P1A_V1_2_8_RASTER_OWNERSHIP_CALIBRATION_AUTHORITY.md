# District Zero P1A v1.2.8 — Raster Ownership, Then Bounded Calibration

## Status and scope

`READY FOR CODEX — RASTER OWNERSHIP DIAGNOSTIC THEN BOUNDED CALIBRATION`

This is not P1A PASS, not a human-testing authorization, and not P1B. It is a
narrow prospective authority overlay over the exact source and evidence bound
in `P1A_V1_2_8_SOURCE_AND_EVIDENCE_BINDING.json`.

The closed v1.2.7R1 Run-2 terminal remains
`NO_PRESENTATION_ONLY_INTERVAL`. All 21 historical candidates were genuinely
executed and evidence-complete. That run proved there was no passing candidate
for its exact control and sample binding; it did not prove that a final-raster
patch owned by `OUTER_CLOSURE_MASK` was insensitive or uncorrectable.

## Why a new preflight is mandatory

The inherited metric converts normalized coordinates with positive floor:

`pixel = clamp(floor(normalized * dimension), 0, dimension - 1)`

At `1280x720`, `(0.20,0.34)` therefore names integer pixel `(256,244)` and a
9x9 patch `x=252..260`, `y=240..248`. The historical continuous ray was cast
through `(256.0,244.8)`, not through an exact final-raster ownership cell.

In the closed evidence, maximum outer albedo changed 48,877 A1 pixels while
only one of the floor-convention patch's 81 pixels changed. Maximum outer
emission produced the same changed-pixel mask. The patch median remained
`0.06987974055145937`. This strongly supports a silhouette/ownership defect,
but it does not replace the required fresh exact-engine ownership diagnostic.

## Frozen boundary

Without exception, preserve movement, tuning, input, camera transform and
projection, canonical view timing, culling and depth behavior, routes, nodes,
spawns, HOP, gameplay thresholds, capture/replay semantics, terrain heights,
terrain colors and surface-classification bytes, source vertices, triangles,
topology, normals, masks, collision, global lighting, background, tonemapping,
shadows, and every non-target material. Preserve the v1.2.6 two-sided terrain
consumer and canonical render-normal corrections.

Keep the same 21 visual check IDs. Keep all true hard conditions, including:

- every required shadow-on sample `Y >= 0.075`;
- `abs(left_outer_closure_Y - adjacent_left_ground_Y) >= 0.12`;
- `abs(right_core_wall_Y - adjacent_right_ground_Y) >= 0.12`;
- every inherited ground/background and shadow-on/off ratio condition; and
- all 14 frozen ray classifications with zero mismatches.

The frozen `LEFT_GREY_STRUCTURE` ray stays at its old normalized coordinate.
New pixel-center diagnostic rays are supplemental evidence, not replacements.

## Exact disposable raster diagnostic

Before any new calibration candidate, copy the verified clean R1 source into a
new disposable root. Import and parse that exact root with Godot
`4.7.1.stable.official.a13da4feb`. Use Forward+, native `1280x720`, the
canonical A1 camera, transform, projection, shadow states, frame waits, culling,
depth, and renderer settings.

One `OWNERSHIP_ID` engine process may produce a finite sequence of internal
owner passes. Enumerate every enabled `MeshInstance3D` in sorted NodePath order.
Use a low reference plus one high-only pass per owner, with disposable material
duplicates that preserve each effective material's cull, transparency, depth,
and render priority. Preserve mesh RIDs, geometry, and transforms; create each
diagnostic material duplicate once and keep that duplicate's RID stable across
the passes. Decode one changed owner as
exact, zero as background, and more than one or unstable coverage as
mixed/boundary-unsafe. If necessary, use deterministic bit-plane classification
inside the same process to resolve source component and face/side-plane class;
any diagnostic mesh representation must have a byte-hashed position/normal/
triangle stream identical to the canonical rendered stream. No such override
may enter final source.

Decode the full rectangle `x=218..294`, `y=206..282`, which covers every
radius-32 center and its radius-6 ownership footprint. For every pixel record
source geometry ID, render node, face class, visible connected side-component
ID, side-plane ID where exact, triangle ID where unambiguous, and explicit
decode status. Preserve the original 81-pixel ownership table, raw owner passes,
decoded masks, target influence masks, annotated crops, camera and geometry
hashes, import/parse evidence, argv, cwd, exact engine identity, stdout, stderr,
engine logs, return/result contract, and hashes.

Record six explanatory rays separately from the frozen 14 gates: pixel-center
rays for `(256,244)`, the four 9x9 corners `(252,240)`, `(260,240)`,
`(252,248)`, `(260,248)`, and the legacy continuous point `(256.0,244.8)`.
Record origin, direction, physics hit, render node, source/triangle mapping when
available, and distance. These rays never substitute for owner-raster evidence.

## Deterministic branch adjudication

The complete diagnostic produces exactly one branch:

1. `ORIGINAL_VALID`: the original full 13x13 footprint has one exact target
   owner key and the target response is valid. Keep pixel `(256,244)`; do not
   change the sample or product source.
2. `BRANCH_A_SAMPLE_REPLACEMENT`: any original 9x9 pixel or its two-pixel
   perimeter is background, mixed, another owner, another component, or not a
   `SIDE` face. Mark the old coordinate invalid for gating and select a new
   coordinate using only owner data.
3. `BRANCH_B_RENDER_CONSUMER_BINDING`: the original 13x13 is exactly target
   owned, but baseline/midpoint/extreme response is flat, reversed, or otherwise
   not governed by the target material. Authorize only the smallest proven
   render-consumer binding repair, then repeat the complete diagnostic epoch.

Incomplete, ambiguous, malformed, or non-repeatable ownership evidence is
`BLOCKED/NOT TESTABLE — HARNESS`; it is not Branch A or B.

For Branch A, form 4-connected visible components from exact owner labels. The
intended component is the target `OUTER_CLOSURE_MASK` `SIDE` component with the
nearest exact target-owned pixel to `(256,244)`, ranked by
`(squared_distance,y,x)`. Resolve and record its source component and side-plane
identity; never use brightness, luminance, a pass/fail check, or target response
to choose it.

Enumerate integer centers satisfying `dx^2 + dy^2 <= 1024`. A center is eligible
only when all 169 pixels in center +/-6 resolve to the same intended
`OUTER_CLOSURE_MASK` source component and `SIDE` face class. Record exact
side-plane and triangle IDs where the diagnostic can resolve them, but do not
mistake an internal triangle/quad seam within the same owner component for a
foreign raster owner. Select the first tuple in ascending
`(squared_distance,y,x)`. Store the
integer pixel as authority. Store its pixel-center normalized representation as
`((x+0.5)/1280,(y+0.5)/720)`; the metric consumes the integer pixel directly.

The selection transcript may contain only owner fields and `(x,y,d2)` tuples.
It must state `luminance_inputs_used:false`. If no center is eligible, stop:

`DIRECTOR DECISION REQUIRED — NO ROBUST OUTER-CLOSURE SAMPLE`

Retain the old `(256,244)` on/off values and coordinate in all later records as
`historical_non_gating`. They must not enter the 21-check array, candidate
status, local-pass logic, or selection.

Leave the bound `tests/fixtures/v1_2_6_visual_acceptance.json` byte-identical.
After adjudication, derive a v1.2.8 selected-acceptance fixture bound to the
selected-sample record. It retains every inherited check ID, coordinate, and
threshold except that Branch A replaces only
`samples.A1_FAMILIARIZATION.left_outer_closure`. `ORIGINAL_VALID` and Branch B
retain the original integer sample. Provenance and the old non-gating result
belong in the selected-sample record, not as a 22nd acceptance gate.

Branch B may change only the canonical target render-consumer binding. It may
not add geometry, screen-space overlays, vertices, faces, new world data, or a
new material family. The exact expected source bytes must be derived from the
frozen builder and selected binding record. Prove the target influence mask is
contained within target-owner pixels and that unrelated geometry is not rebound.

## Sensitivity preflight

The diagnostic budget is separate from calibration. Pre-repair cases are:

1. baseline: outer `1.0`, wall `1.0`;
2. target midpoint: outer `1.15`, wall `1.0`;
3. target extreme: outer `1.30`, wall `1.0`;
4. unrelated extreme: outer `1.0`, wall `1.47`; and
5. ownership ID at baseline.

Cases 1-4 preserve matched A1 shadow-on and shadow-off RGB8 native renders.
Branch A and `ORIGINAL_VALID` spend exactly five diagnostic launches. Branch B
may repeat the same five in one post-repair epoch. The pre-repair cap is `5` and
the absolute cap is `10`; matching import/parse-preflight caps apply. Offline
decoding, crops, and masks spend no engine launch.

Sensitivity passes only if ownership and margin pass, and the corrected
shadow-on 9x9 has strict
`medianY(base) < medianY(midpoint) < medianY(extreme)`. All 81 corrected-patch
RGB triplets must be byte-identical between baseline and the unrelated wall
extreme. Record shadow-off medians and masks without adding a new hard visual
threshold. Flat, opposite, zero, or unrelated response stops:

`BLOCKED/NOT TESTABLE — MEASUREMENT BINDING`

That status can never be rewritten as `NO_PRESENTATION_ONLY_INTERVAL`.

## Corrected outer-search mathematics

The v1.2.7 registry's outer `measured_Y_feasible_interval` and
`balanced_target_Y` were derived from the invalid historical coordinate. They
are historical evidence, not hard acceptance requirements. The true frozen
conditions are the original `Y >= 0.075` and absolute separation `>= 0.12`.

For an adjacent-ground value `G`, the exact feasible luminance set is:

`Y >= 0.075 and (Y <= G - 0.12 or Y >= G + 0.12)`.

After corrected sensitivity passes, derive and record the reachable low and/or
high branch from the fresh baseline, midpoint, and extreme records. Search the
unchanged quantized material domain against the actual hard predicates. A
correct high-branch candidate must not be rejected by the obsolete low-only
interval. Preserve the existing guard probes, all-21-check eligibility, primary
minimum-presentation-delta objective, maximin/margin preferences, and registered
tie breaks. Any interior target needed by the bounded search is derived from the
active branch boundary using the unchanged preferred interior half-width; it is
not a relaxed threshold.

## Fresh bounded continuation

Only after diagnostic and sensitivity PASS:

- start from another clean unmaterialized R1 copy;
- assert calibration state `launches=0`, `index=0`, empty records/cache, and an
  empty candidate root;
- keep the outer/wall albedo and conditional emission domains, quanta, guard
  probes, finite study sizes, and the separate 82-candidate absolute cap;
- bind every candidate to the selected-sample, ownership-diagnostic, sensitivity,
  clean-source, and exact-engine hashes;
- recompute both the current gating sample and old historical non-gating sample
  from the preserved PNGs; and
- never import a Run-2 candidate or cache entry.

`NO_PRESENTATION_ONLY_INTERVAL` may be emitted only after the owner and
sensitivity gates pass and a complete registered stage transcript proves every
planned candidate executed-complete and bound to v1.2.8, with no eligible result.
Missing evidence, a flat target, a cap hit before plan completion, or an
incomplete transcript is a blocker, not a no-interval result.

If outer passes, continue without interruption through wall calibration, the
bounded 3x3 combined validation, selected materialization, all 21 visual checks,
all 14 frozen rays, protected-file verification, selected C1 with maximum delta
`0.0`, 75-second launcher smoke, and creation plus exact-engine import/parse of
the prepared A1 session.

Automation success is:

`AUTOMATION PASS — PREPARED A1 SESSION READY FOR DIRECTOR REVIEW`

It does not authorize launching the prepared session. Stop before human testing
and P1B.

## Evidence and cleanup

Use the inherited v1.2.7R1 common terminal finalizer on every registered terminal
path. Preserve all reached-stage raw data, structured results, commands, logs,
hashes, and classifications. Generate a complete internal inventory, a
deterministic evidence ZIP, ZIP-integrity and forbidden-entry results, and a
fresh-extraction byte/tree verification before deleting any disposable copy.

On automation success, additionally package uniquely named clean implemented
source and prepared-session ZIPs with the same complete round-trip verification.
No `.godot`, editor state, caches, AppleDouble, `.DS_Store`, diagnostic override,
nested archive, or unretained log may enter a source or session deliverable.
