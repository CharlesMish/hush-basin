# District Zero P1A — bounded post-v1.2.8 visibility repair

## Trigger

The owner supplied two native screenshots from the correct v1.2.8 diagnostic
project showing that wall side faces remain visually confusable with terrain and
that the chase camera can occupy the far side of wall collision from the craft.
The owner explicitly requested a repair from the correct version.

## Narrow authority

This turn may change only:

1. render-only face-class presentation for `CORE_WALL`,
   `OUTER_CLOSURE_MASK`, and `OUTER_WALL`; and
2. camera-position obstruction resolution between the craft-side pivot and the
   otherwise unchanged desired chase-camera position.

The validated v1.2.8 source remains untouched in its prior execution root. Work
occurs only in this isolated successor copy.

## Frozen without exception

Movement, tuning coefficients, input, craft collider, support logic, terrain
data and colors, world geometry positions, source and render triangle streams,
normals, collision, routes, nodes, spawns, HOP, gameplay thresholds, camera FOV,
camera look target, unobstructed camera frame, global lighting, shadows,
background, tonemapping, capture/replay semantics, Human World Gate, and P1B
remain frozen.

Render surfaces may be partitioned by the already-authored `TOP` / `SIDE` /
`BOTTOM` source-face labels only if the concatenated render triangle stream is
proved byte-equivalent to v1.2.8. No vertex, normal, triangle, collision shape,
wall height, aperture, or world transform may change.

Camera obstruction may only shorten the target-to-camera segment on a verified
world collision. It must preserve the exact old result when unobstructed, must
exclude the craft collider, and must never move the craft or affect simulation.

## Required evidence

- behavioral camera obstruction tests for clear and blocked lines of sight;
- exact wall render-triangle/position/normal preservation;
- exact terrain and collision preservation;
- exact-engine import and parse;
- native before/after captures at registered visibility probes;
- inherited semantic suites;
- frozen movement/world comparison and C1 maximum delta `0.0`;
- clean package and checksums.

This work is not P1A PASS and does not authorize the Human World Gate or P1B.
