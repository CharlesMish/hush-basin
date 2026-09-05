# Hush Basin — Quarto vehicle v1 candidate

This task branch develops a native visual successor to the vehicle in Quiet Surfaces v1. Start with [the vehicle handoff](docs/QUARTO_VEHICLE_V1.md) and [its bounded scope](QUARTO_VEHICLE_V1_AUTHORITY.md). Native validation and owner acceptance are not implied by this branch. The inherited baseline README follows unchanged.

---

# District Zero — Quiet Surfaces v1

A material-only successor to Working Neighborhood v1: cleaner road boundaries,
muted charcoal paving, broad mineral-ground variation, twelve resurfacing patches
and six flush service-cover graphics. Existing architecture and warm drizzle remain.

Launch **PLAY_QUIET_SURFACES.command** or `python3 tools/launch.py` with installed
Godot `4.7.1.stable.official.a13da4feb`. The launcher prepares the cache and opens
Run v0 at Quarry. W/S thrust/brake, A/D steer, hold Shift for Drive, Space for
supported Hop. R retries, Escape pauses, F on results returns to free roam.
Tab opens diagnostic locations. See QUIET_SURFACES_PLAYTEST.md.

## Authoring and verification

`game/presentation/quiet_surfaces_v1.json` owns the palette, widths, seed and
fixed maintenance placements. `python3 tools/generate_quiet_surfaces.py` writes
two 2048-square PNGs and native Image resources with offline mipmaps. Do not
hand-edit generated maps. The native material uploads these images unchanged;
there is no runtime surface generator or new scene object. Two texture maps
account for 27,962,025 bytes including mipmaps (RGBA8 + R8).

All historical terrain positions, normals, triangles, collision and gameplay
classifications remain unchanged. UVs and the terrain material change only.
Architecture, weather, movement, camera, vehicle, minimap and Run rules remain.
The original Neighborhood inventory and its status are retained as history.
QUIET_SURFACES_V1_AUTHORITY.md authorizes only this surface successor.

```sh
python3 tools/verify_quiet_surfaces.py --regenerate
python3 tools/verify_world_polish.py --regenerate
python3 tools/verify_quiet_surface_suite.py --evidence /absolute/new/evidence --native --baseline /absolute/extracted-working-neighborhood
```

Run native Godot processes sequentially. Keep the review UI idle during matched
performance arms; both AB and BA moving pairs are retained. Without `--native`,
GPU visuals, rain contact and performance are unverified. STATUS.md records actual
results and failures. The companion survey includes before/after views and clips.

No dependencies, external assets, custom shaders, new geometry, objectives or
publication. Flat patches/covers are cosmetic, with no handling effect. Charlie
judges comfort, ground readability and whether the surfaces belong to the city.
