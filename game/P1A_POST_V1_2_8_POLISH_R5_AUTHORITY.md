# District Zero P1A — bounded owner-authorized polish R5

## Trigger

After playing the repaired R4 project, the owner explicitly authorized the
bounded polish sequence recorded in the 2026-08-25 read-only audit. The owner
reported that the repaired walls looked great and asked Codex to proceed while
preserving the game rather than rewriting it.

## Narrow R5 authority

R5 may change only:

1. HUD layout, style, default diagnostic-menu visibility, pause indication,
   development-build wording, and responsive safe-area margins;
2. minimap drawing hierarchy and highlighted-route presentation without
   changing route or node data;
3. the environment background from a flat near-black color to a subtle native
   procedural horizon, without changing global light, sun, shadows, exposure,
   tonemapping, camera, or fog;
4. non-colliding node-marker render mesh/material presentation while preserving
   every node identity, position, elevation, semantic color family, and render
   ownership expected by frozen ray evidence; and
5. a terrain render-color study only if it preserves every terrain/data/
   collision byte and all inherited visual/ray gates. No terrain study delta is
   required to be selected.

## Frozen without exception

Movement, tuning, input, craft scene/collider/support/controller, world data,
terrain heights and classification bytes, source and render positions,
triangles, topology, normals, collision, routes, nodes, spawns, HOP, gameplay
thresholds, telemetry semantics, capture/replay, camera position/FOV/look target/
obstruction behavior, sun, lighting, shadows, tonemapping, fog, landmark
geometry, and every repaired wall material/culling value remain frozen.

The R3 two-sided solid repair and selected wall-face presentation are retained
exactly. R4 telemetry robustness and standalone-launch behavior are retained.

## Acceptance boundary

- Exact Godot remains `4.7.1.stable.official.a13da4feb`, Forward+, native
  `1280x720` for validation.
- All 21 inherited native visual checks and all 14 frozen ray classifications
  remain mandatory.
- Registered camera starts remain unchanged when unobstructed.
- Inherited semantic suites and R3 visibility behavior remain green, with only
  the review-identity assertion superseded by the R5 identity.
- C1 remains 1,260 ticks with maximum delta `0.0`.
- Work occurs in a new successor root and never mutates R4.

R5 is a development/owner-review build. It is not P1A PASS, does not conduct or
claim the Human World Gate, and does not enter P1B.
