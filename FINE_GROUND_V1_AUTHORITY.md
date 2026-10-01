# Fine Ground v1 — near-range ground detail and atmosphere

On October 1, 2026 the owner asked: “I was thinking I might have you give the
world a polish on your own branch? I particularly could stand to have some
nicer floors … can you try to improve them without increasing asset size too
much? I’d love to see your low hanging fruit elsewhere too.”

This authorizes a presentation-only successor on branch `claude/fine-ground-v1`
from main commit `df221870b45de53e4ebb5ea8889b6cf1114054c6` (Quarto full-game
checkpoint). It does not authorize merging, publication or external actions.

## Bounded change

Ground: the one existing terrain surface keeps its Quiet Surfaces 2048-square
albedo/roughness maps unchanged and gains a single original 256-square,
seamlessly tiling RGBA detail map (slope u/v, mineral grain, asphalt grain),
generated offline by `tools/generate_fine_ground.py` with no dependencies or
external assets. A small spatial shader replaces the terrain's
`StandardMaterial3D` and samples the detail twice in world metres (3.0 m and a
rotated 11.3 m layer), chooses mineral or asphalt grain from the existing macro
roughness, perturbs the shading normal, and fades all detail to zero between
28 and 85 m so the approved distant appearance is retained. Budgets: detail PNG
≤ 512 KiB, resident detail with mipmaps ≤ 1 MiB, total terrain textures
≤ 32 MiB. One surface, no next pass, no new geometry or scene objects.

Atmosphere and filtering: screen-space ambient occlusion, a light exponential
distance haze (sky unaffected) applied after the existing weather lighting, and
16× anisotropic texture filtering. All values live in
`game/presentation/fine_ground_v1.json` and can be disabled there.

Playable baseline files permitted to change: `game/project.godot` (one
setting), `game/scripts/p1a_world_builder.gd` (terrain material line) and
`game/scripts/p1a_world_gate.gd` (one atmosphere call). Preambles may be added
to `README.md`, `AGENTS.md` and `game/AGENTS.md`. Every other file tracked at
the baseline commit stays byte-identical; `tools/verify_fine_ground.py`
enforces the exact wiring diff and the declared file set.

## Preserved boundaries

Terrain vertices, normals, indices, UVs and collision; world/classification
data; architecture; vehicle; controller, tuning, camera, input, telemetry, Run
rules, routes, weather particles, sky and lighting values; and all historical
inventories, tests and evidence remain unchanged. Detail never affects
movement, surface classification or gameplay.

Historical checks expected to reject this intentional successor, unpatched:
`quiet_surface_runtime.gd` (typed StandardMaterial3D terrain material),
R5/R6/R7 runners' `FOG_REMAINS_DISABLED`, and `verify_world_polish.py`'s
package inventory for the three wiring files. The two Quarto vehicle
inventory failures of `verify_repo.py` are inherited and unchanged.

## Verification and review

`python3 tools/verify_fine_ground.py --regenerate` checks preservation, declared
files, bounded wiring diffs, budgets, repeatable bytes, zero-mean channels and
seamless wrapping. `--native --evidence DIR` with the exact Godot
`4.7.1.stable.official.a13da4feb` runs disposable baseline and successor
copies sequentially: import/parse, matched 1,260-tick C1 movement, terrain/
collision/UV/node identity, shader-error log scan, the current Run, paused
retry, vehicle and world/entrance fixtures, and four gameplay-camera captures
from each version. If the engine is unavailable, native validation is pending,
not passed. Charlie alone judges appearance, shimmer, comfort and performance.
