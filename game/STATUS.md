# District Zero P1A status — vehicle integration R7

Historical R7 baseline record. Current Quiet Surfaces v1 status is ../STATUS.md;
its World Polish v1 geometry does not inherit these historical world gates.

**Outcome:** `AUTOMATION PASS — VEHICLE INTEGRATION R7 READY FOR OWNER REVIEW`

**This is not:** `P1A PASS` or Human World Gate authorization.

## Integrated presentation

- The verified native-Godot Babylon-transfer craft replaces only the prior
  primitive craft presentation subtree.
- Spread, midpoint, and Drive use the transfer's complete transformation
  choreography and inherited clearance-energy cue.
- All 56 mesh instances remain beneath `VisualRoot`; no collision object,
  collision shape, ray, or shape cast exists beneath the visual rig.
- The gameplay root, fixed collider, three support probes, hazard cast,
  movement, tuning, transform timing, terrain, walls, routes, camera, map,
  lighting, shadows, and thresholds remain frozen.
- The clean-extraction launcher now performs and validates its exact-engine
  script-class import before the first playable launch. This closes the
  intermittent first-open missing-class parse cascade without changing game
  behavior.

Human attempts: `0`. Human World Gate: `NOT PERFORMED`. P1B: `FROZEN`.

## Exact-engine verification

- Engine: `4.7.1.stable.official.a13da4feb`, native Forward+.
- R6 inventory: `220/220 PASS`; transfer inventory: `33/33 PASS`.
- R7 integration behavior: `19/19 PASS`.
- Transfer choreography validator: `PASS`; golden pose signature
  `045296bf018b6da5af5d89b37af831fd29eedfe16d8f085f80ba6fb113dfb44b`.
- R6 terrain/preservation behavior: `13/13 PASS`.
- Inherited R1 semantics: `65/65 PASS`.
- Inherited v1.2.8 semantics: `45/45 PASS`.
- C1: `1,260/1,260` ticks, raw traces byte-identical, maximum absolute
  movement delta `0.0`.
- Native vehicle poses: `3/3 PASS`, all meshes in frame.
- Native visual checks: `21/21 PASS`.
- Frozen rays: `14/14 PASS`, zero mismatches.
- Native route/view sweep: `14/14 PASS`, maximum camera pull-in `0.0 m`.
- Fresh cache-free double-click launcher import/parse/play smoke: `PASS`,
  `180` frames, clean shutdown, no retained lock.

## Inherited runtime accounting

The runnable automated set produced `35 PASS` and one inherited
`RT_FRESH_OPEN_IDENTITY` label mismatch. The unchanged R6 baseline produces
the same mismatch because that frozen v1.2.5 vector still demands the older
literal `DISTRICT ZERO · P1A WORLD GATE · v1.2.3`; it is not a vehicle,
movement, or runtime regression.

The complete 40-vector wrapper does not execute A1, A2, or X0 without the
separately authorized selected human-trace manifest. `RT_HOP_SUCCESS` also
remains not testable through this inherited wrapper because its controller
fixture does not expose the already-selected zero timing offset. These four
prerequisites were not changed or bypassed for R7. All other executed vectors
were preserved with their raw standalone evidence.
