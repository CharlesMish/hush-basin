# Current external review — courier alpha v0.2

This branch publishes the played courier-alpha candidate, not a finished release.
Game/source baseline: `57456768dba28e571d8c19d4e9c66db16388786d`; this publication
changes only this README and redacts a Cloudflare account identifier in three
historical hosting documents. Game files are byte-for-byte identical. This is
a publication snapshot atop existing main, without unpublished local history.
The production site below is an older build,
not this candidate. Earlier sections and authorities remain historical records.

Use exact Godot `4.7.1.stable.official.a13da4feb` and Python 3.10+.
From the repository root, run `python3 tools/play_alpha_loop.py`, or double-click
`PLAY_COURIER_ALPHA.command` on macOS. Set `GODOT_BIN` if needed. Nothing is
installed automatically. `python3 tools/verify_alpha_loop.py` checks the current
preservation inventory (this publication reports the intentional README and
three hosting-document privacy differences). The older R7-only verifier is a
historical baseline. Redactions preserve the recorded results; raw original
records remain local.

Market is home and Dispatch: choose a job, drive any legal route, settle at the
destination, read Results, then drive back normally. Three replayable jobs offer
one optional objective each: Depot Style, Relay Express, Works Care. Cargo
condition never invalidates delivery, even at zero; missing a bonus still pays
the fixed base. BRRR measures expressive driving and pays only where explicitly
requested. Session Credits and one 25% cargo-protection liner are provisional;
they reset when the app closes and never alter vehicle handling.

Controls: W/S thrust/brake, A/D steer, hold Shift for Drive (release for Spread),
Space supported Hop, Escape pause, R reset. At Market, E/Enter opens Dispatch;
1/2/3 selects a job and Enter accepts. C buys the liner on Dispatch. F2 shows
cargo receipts; F3 bookmarks surprising contact. See the
[play card](START_HERE_ALPHA_LOOP.md), [target rationale](ALPHA_TARGETS.md), and
[recorded verification](ALPHA_LOOP_RESULTS.md). Raw local logs, captures and
exported builds referenced in historical records are not included in this branch.

**Current owner feedback:** the loop is fun, but the present jobs/routes are
substantially too easy. Their challenge calibration is not representative of
intended difficulty. This publication does not rebalance them.

---

# Production Web play target (historical accepted deployment)

Play the accepted build at [hush-basin.cmish.dev](https://hush-basin.cmish.dev/).
Native Forward+ remains authoritative; Web is a provisional regression/play target.
Production uses small Pages assets and private, immutable R2 artifacts through
same-origin routes. The [production runbook](docs/PRODUCTION_WEB_V1.md) records
build identity, verification, explicit preview/promotion commands, and rollback.

---

# Local Web build lane

The native Forward+ game remains unchanged. From the repository root, run
`python3 tools/export_web.py --output build/web-1`, then
`python3 -m http.server 8067 --bind 127.0.0.1 --directory build/web-1/web`.
Open `http://127.0.0.1:8067/` in Chromium at 1280×720 or larger.
Use a new output directory for each export. Exact engine and template required;
nothing is installed automatically. See the [Web decision packet](docs/WEB_FEASIBILITY_V1.md)
for measured sizes, compatibility differences, checks and remaining limitations.
This local lane is also the input to intentional production Web promotion.

---

# Hush Basin — current full-game checkpoint

The complete Quiet Surfaces city now uses the Quarto-derived native vehicle.
Charlie approved putting this played version on main on September 7, 2026.
Native integration passed on Godot `4.7.1.stable.official.a13da4feb`; see the
[current checkpoint record](docs/QUARTO_MAIN_CHECKPOINT_20260907.md) for exact
verification and remaining limitations. Earlier handoffs below remain history.

Run `python3 tools/launch.py`, or open **PLAY_FULL_GAME.command** on macOS.
For the separate F6 comparison or vehicle studio, run
`python3 tools/launch_quarto_vehicle.py --view compare` or `--view studio`.
The full project is `game/project.godot`. No engine installation is automatic.

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
# Temporary Cloudflare hosting proof

The hosting-only successor is documented in
[`docs/CLOUDFLARE_HOSTING_PROOF_V1.md`](docs/CLOUDFLARE_HOSTING_PROOF_V1.md).
It preserves the accepted export and tests Pages with same-origin R2 routes.
No production domain or game changes are part of this proof.

---
