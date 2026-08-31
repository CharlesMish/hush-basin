# District Zero P1A — Vehicle Integration R7 execution report

## Result

The Babylon-transfer vehicle is integrated as a presentation-only successor
to Terrain Polish R6 and is ready for owner play review. Movement equivalence
is exact: the 1,260-tick C1 baseline and R7 traces are byte-identical with
maximum absolute delta `0.0`.

## Source boundaries

- Immutable baseline: `District-Zero-P1A-v1.2.8-Terrain-Polish-R6-Player`.
- Immutable transfer: `District-Zero-Vehicle-Babylon-Transfer-R1-Polish`.
- Changed product presentation: `scenes/craft.tscn`,
  `scripts/craft_controller.gd`, `scenes/vehicle_visual.tscn`, and
  `scripts/vehicle_visual_rig.gd`.
- The craft scene and controller are byte-identical to the verified transfer.
- The fixed physics root/collider/probes/casts and all movement code are
  unchanged from R6 after normalization of the authorized presentation calls.
- World, terrain, routes, camera, lighting, map, thresholds, capture/replay,
  Human World Gate, and P1B are unchanged.

## Verification results

| Lane | Result |
| --- | --- |
| Static R6/transfer preservation | PASS — 220 R6 and 33 transfer records |
| Transfer validator | PASS |
| R7 integration behavior | 19/19 PASS |
| Terrain preservation | 13/13 PASS |
| R1 semantic regressions | 65/65 PASS |
| v1.2.8 semantic regressions | 45/45 PASS |
| C1 | PASS — 1,260 ticks, raw-identical, max delta 0.0 |
| Spread/mid/Drive native capture | 3/3 PASS, 56 meshes in frame |
| Native visual metrics | 21/21 PASS |
| Frozen ray classifications | 14/14 PASS, 0 mismatches |
| Route/view capture sweep | 14/14 PASS, 0.0 m pull-in |
| Cache-free launcher smoke | PASS — import, parse, 180 playable frames |

## Runtime-vector disposition

Thirty-five inherited automated vectors executed real gameplay and passed.
`RT_FRESH_OPEN_IDENTITY` executed and failed only its obsolete exact build-label
literal; the unchanged R6 baseline reproduces that exact failure.

The A1, A2, and X0 vectors require a selected human trace manifest that is not
an input to this bounded vehicle-integration turn. `RT_HOP_SUCCESS` is blocked
by the inherited wrapper's missing selected zero-offset binding. None was
weakened, repaired, or reclassified as a pass. Their complete raw evidence is
retained.

## First-launch robustness repair

The first direct smoke from the clean R7 source reproduced the known missing
global-script-class cache cascade. The launcher now detects a missing
`VehicleVisualRig` registration, runs the exact installed Godot editor import,
requires a nonempty class cache with that class, runs a second parse-clean
editor open, and only then starts the game. A new cache-free disposable copy
completed that whole sequence and shut down cleanly.

## Stop boundary

This is an owner-review player build. No human attempt was recorded, the Human
World Gate was not started, and P1B remains frozen.
