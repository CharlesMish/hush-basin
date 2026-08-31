# District Zero P1A — Terrain Polish R6 execution report

## Outcome

`AUTOMATION PASS — TERRAIN POLISH R6 READY FOR OWNER REVIEW`

This is not P1A PASS or Human World Gate authorization. Human attempts remain
zero and P1B remains frozen.

## Selected delta

The selected render-only boundary blend is `0.22`. It operates only at
four-neighbor boundaries between ordinary terrain classes `0..9`. Same-class
interiors remain exact. Gate-band class `10` and hard-obstacle class `11` are
excluded and remain exact.

The implementation changes only the terrain vertex-color consumer. It does not
rewrite height data, surface classifications, vertices, indices, normals,
collision, movement, routes, walls, camera, lighting, shadows, or thresholds.
The exact-engine semantic probe observed `9,121` materially changed boundary
vertices after ArrayMesh color-storage quantization and zero changed protected
or same-class-interior vertices.

## Candidate bracket

Three preregistered native candidates were compared:

- `0.12`: valid but nearly imperceptible.
- `0.22`: visibly softens class-edge stair steps while retaining route/readability
  hierarchy; selected.
- `0.32`: valid but begins washing the road/shoulder hierarchy.

The `0.12 → 0.22` comparison changed `220,634` pixels with maximum channel
delta `7`; `0.22 → 0.32` changed `226,674` pixels with maximum channel delta
`8`. Candidate evidence is retained outside the player package.

## Verification results

- Exact Godot identity: `4.7.1.stable.official.a13da4feb`.
- Presentation behavior: `19/19 PASS`.
- Terrain/preservation behavior: `13/13 PASS`.
- R1 semantic suite: `65/65 PASS`.
- v1.2.8 semantic suite: `45/45 PASS`.
- Native visual metrics: `21/21 PASS`.
- Frozen rays: `14/14 PASS`, zero mismatches.
- Native 14-view route sweep: `14/14 PASS`; maximum camera pull-in `0.0 m`.
- C1: `1,260/1,260` ticks, raw trace bytes equal, maximum absolute delta `0.0`.
- R5 internal inventory: `208/208 PASS`.
- Undeclared R5 paths: `201` byte-identical.
- Frozen heightfield SHA-256:
  `f377a1034406ee2f35232c01f6cb80be8dd43d13267e3821d1edcab9a9735b88`.
- Frozen surface-class SHA-256:
  `3d7466384a52bb8033e5fad5acd014a2daedec76475d5ad21ff13a94cee73949`.
- Direct native smoke and actual launcher smoke: `PASS`; no engine/script error,
  telemetry leak, crash marker, or stale launcher lock.

The first authored GDScript import exposed an explicit local integer inference
error; it was corrected before candidate capture. One inherited probe was also
initially invoked from an unimported disposable copy and then correctly rerun
after exact-engine import. A shared default `user://` log open produced one
isolated engine crash; rerunning with an explicit evidence log completed
normally. Those preflight outputs are retained and are not product failures.

## Principal commands

```text
/opt/homebrew/bin/godot --headless --path <R6_SOURCE> --import
/opt/homebrew/bin/godot --headless --path <R6_SOURCE> --script res://tests/p1a_polish_r6_runner.gd
/opt/homebrew/bin/godot --headless --path <R6_SOURCE> --script res://tests/p1a_terrain_polish_r6_runner.gd
python3 -B tools/test_v1_2_7r1_repairs.py --root <DISPOSABLE_SEMANTIC_ROOT> --static-only
python3 -B tools/test_v1_2_8_semantics.py --root <DISPOSABLE_SEMANTIC_ROOT>
python3 -B tools/compare_terrain_polish_r6_c1.py <BASE_TRACE> <R6_TRACE> tests/fixtures/baseline_flat_support.json
python3 -B tools/verify_terrain_polish_r6.py <R5_PLAYER> <R6_SOURCE>
/opt/homebrew/bin/godot --path <R6_SOURCE> --quit-after 180
DISTRICT_ZERO_R6_SMOKE_FRAMES=180 ./PLAY_DISTRICT_ZERO_TERRAIN_POLISH_R6.command
```
