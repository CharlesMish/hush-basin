# District Zero P1A — bounded owner-authorized terrain polish R6

## Trigger

After playing Polish R5 without a crash, the owner approved a practical,
non-pristine touch-up to reduce jagged terrain-color transitions and better
match the updated horizon, map, and presentation.

## Narrow authority

R6 may change only the runtime terrain visual vertex-color consumer. It may
blend the existing `SURFACE_COLORS` across boundaries among ordinary terrain
classes `0..9` using a deterministic, bounded local neighborhood. Class `10`
gate bands and class `11` hard-obstacle footprints remain exact and may not
participate in the blend.

The selected blend must be the smallest reviewed value that materially softens
the road/shoulder/base silhouette without erasing functional color hierarchy.
No new texture, shader, asset, geometry, vertex, triangle, normal, light,
shadow, fog, camera, collision, or surface class is authorized.

## Frozen without exception

All R5 presentation except terrain vertex colors; every world/data byte;
terrain heights and surface-class bytes; terrain positions, indices, topology,
normals and collision; all solid/wall render meshes and materials; movement,
tuning, craft, input, routes, nodes, spawns, HOP, telemetry, capture/replay,
camera, sun, lighting, shadows, tonemapping, fog, acceptance thresholds, and
Human World Gate/P1B boundaries remain frozen.

## Acceptance

- Exact Godot remains `4.7.1.stable.official.a13da4feb`, native Forward+.
- R5 behavior remains `19/19 PASS` and the new terrain-consumer semantic suite
  passes.
- All `21/21` native visual checks and `14/14` frozen rays remain green.
- The registered `14/14` camera sweep remains unchanged when unobstructed.
- C1 remains `1,260` ticks with maximum delta `0.0` and byte-identical traces.
- Fresh player extraction imports, parses, and passes its behavior suite.

R6 is an owner-review build, not P1A PASS or Human World Gate authorization.
It does not enter P1B.
