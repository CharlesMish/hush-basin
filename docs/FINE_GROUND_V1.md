# Fine Ground v1 — implementation and verification record

2026-10-01, branch `claude/fine-ground-v1` from `df221870b45de53e4ebb5ea8889b6cf1114054c6`.
Authority: `FINE_GROUND_V1_AUTHORITY.md`.

## What changed

**Ground detail.** The Quiet Surfaces maps cover 660 × 600 m with 2048 texels,
about 0.32 m per texel, so the ground near the craft read as flat colour. A 256 × 256
seamless tile (`game/presentation/fine_ground/fine_ground_detail.png`, 234,015
bytes; 349,524 bytes resident with mipmaps) now adds close-range detail:

| Channel | Content |
| --- | --- |
| R, G | Signed slope of a relief: proud pebbles over a softly undulating grain bed |
| B | Mineral grain: individual stone tones, darker gaps, dusty mottling |
| A | Asphalt grain: pale aggregate chips in darker binder, mid-scale wear |

The terrain shader (in `game/scripts/fine_ground.gd`) samples it at a 3.0 m and
a rotated, offset 11.3 m world tile to hide repetition. The existing macro
roughness picks asphalt grain for paving and patches (≤ 0.70), mineral grain for
ground, yards, shoulders and the amber rough cue (≥ 0.80), and blends between
them. Signed channels are zero-mean, so the macro palette's average tone is
kept. Detail fades out between 28 and 85 m, leaving distant views as approved.
Four texture lookups per terrain fragment instead of two. Macro albedo and
roughness are also sampled with anisotropic filtering.

**Atmosphere.** SSAO (radius 1.4 m, intensity 1.6) darkens the contact between the box
architecture, walls and ground. A light exponential haze (density 0.0016, about 15%
at 100 m, about 38% at 300 m) uses the warm-grey horizon tone with aerial
perspective and leaves the sky itself untouched. The project-wide anisotropic
filtering level is 16× so ground textures stay sharp at grazing angles.

**Edges and gradients (October 2).** 2× MSAA on the game viewport smooths the
stair-stepped silhouettes of box architecture, walls, poles and road-edge
geometry. Unlike FXAA, it leaves the new ground detail sharp. Debanding removes 8-bit
stepping in the smooth overcast sky and haze. Both are in the config's `display` block
(`msaa_3d`: 0 off, 1 = 2×, 2 = 4×). Considered and left alone: shadows on
non-solid decorative modules (deliberately off), screen-space reflections on damp
asphalt (expensive, little gain at its roughness), glow and a tonemapper change
(would shift the approved palette).

**Loading.** The detail folder carries `.gdignore`; the loader decodes the PNG
from bytes and builds its mipmaps at startup (a 256-square tile). An existing
`.godot` cache therefore never needs a reimport, and no `.import` file is created.

## Tuning

Every value is in `game/presentation/fine_ground_v1.json`. If the result is too strong,
lower `mineral_albedo`, `asphalt_albedo` or the two `relief` values. If tiling or
shimmer is visible, reduce `fade_end_m`. If edges cost too much frame time, set
`display.msaa_3d` to 0. Set `ssao.enabled` or `fog.enabled` to
`false` to remove either. To change the tile itself, edit the `detail` block, then
run `python3 tools/generate_fine_ground.py`. Do not hand-edit the PNG.

## Verification (this pass)

Pre-edit baseline: `verify_repo.py` 389 checks, FAIL only on the two inherited
Quarto vehicle inventory entries; `verify_quarto_vehicle.py` source checks PASS.

Successor static: `python3 tools/verify_fine_ground.py --regenerate`: **PASS**
(see the commit's recorded output). The historical verifiers report the same
results as on main, apart from the expected `verify_world_polish.py` package
rejections of `game/project.godot`, `p1a_world_builder.gd` and `p1a_world_gate.gd`.

**Native validation: PENDING.** This pass ran in a cloud container without the
pinned engine, and its network policy blocked downloading it. The shader has
not been compiled and nothing has been rendered in Godot. Run, on the review machine:

```sh
python3 tools/verify_fine_ground.py --regenerate --native --evidence /absolute/new/evidence
python3 tools/launch.py
```

The native suite saves `baseline-captures/` and `successor-captures/` (four
matched gameplay-camera views) for side-by-side review. Offline Python previews
used during tuning approximate albedo and Lambert shading only; they say nothing
about Godot photometry, SSAO, haze, shimmer or performance.

Not claimed: visual acceptance, comfort, shimmer-free motion, performance
(four lookups instead of two, plus SSAO and 2× MSAA, are real GPU work; the inherited Quiet Surfaces
Market–Clinic +14.61% miss remains open), or any gameplay change.
