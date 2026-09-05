# World Polish v1 status — September 5, 2026

State: IMPLEMENTED REVIEW BUILD — FINAL COMPLETE SUITE FAIL; TWO OPEN ISSUES.
Both permitted bounded repair rounds are exhausted. No further implementation
changes followed the final complete verification. This is not an acceptance PASS.

Baseline: clean commit 3b245da432b5a20a1606b3a9b2d9559ba409db39 in the original
District-Zero-GitHub-Ready-Run-1 repository, which remains unchanged. Engine:
4.7.1.stable.official.a13da4feb, Apple M5, native Metal Forward+.

## Implemented

Three deterministic yard cuts open Quarry–Depot, Relay–Works and Market–Clinic.
Each has two 24 m clear entrances and a 40 × 40 m clear maneuvering square.
Protected foundations remain beneath retained buildings and landmarks. The
offline generator creates shared render/collision solids and terrain height
data. Original roads, destination/pad heights, outer wall and South fixture
remain. Only exposed ground and shoulder/bank transitions inside yards change.
The existing rough R0 Works road remains rough; the smooth new Works entrance
leaves its pad westward. Warm mineral/concrete/steel colors, static industrial
details, procedural daylight, yard map fills and spatial classifications use
the explicit World Polish v1 identity. No external assets or packages were used.

Craft, tuning, movement, collider/probes, input, rig and camera implementation
are unchanged. Run v0 code/scene and its BRRR formula remain byte-identical.
The main project scene now launches the existing Run v0 scene.

## Observed verification

Run directory used for evidence:
`/Users/cmish/Desktop/Hush-Basin-Movement-Lab-Handoff/District-Zero-World-Polish-V1-Run-1`.
All exact subprocess argv, cwd and exit codes are in `evidence/complete-3/suite.json`.

From the original repository:

```sh
python3 tools/verify_repo.py --require-clean
python3 tools/launch.py --prepare-only
python3 tools/launch.py --smoke-frames 180
```

Original integrity PASS: R7 234/234, Run overlay 9/9, retained P1B design 65/65;
322 tracked files, 83,008,036 bytes. Import/parse and 180-frame smoke PASS.
Fresh pre-edit native survey: 25 registered views at 1280 × 720, Forward+.
Historical source and recorded R7 evidence are retained unchanged.

From this successor source, final complete command:

```sh
python3 tools/verify_world_polish_suite.py --evidence /Users/cmish/Desktop/Hush-Basin-Movement-Lab-Handoff/District-Zero-World-Polish-V1-Run-1/evidence/complete-3 --native
```

Observed exit 1, overall FAIL. Individual results:

| Verification | Observed result |
|---|---|
| Offline generation/integrity/spatial checks | 260/260 PASS, including byte-repeatable regeneration |
| Import and script parse | PASS |
| C1 unchanged movement fixture | All 1260 synchronized records byte-identical to baseline |
| Vehicle R7 choreography | PASS |
| Run v0 startup, finish/retry/reset/free-roam checks | 54/54 PASS |
| Paused retry addendum | 15/15 PASS |
| World runtime | 34/35 PASS; decorative band count FAIL |
| New entrances in Spread and Drive | 12/12 PASS; zero impacts, unsupported ticks or resets |
| Native survey | 25/25 PNGs, Forward+, 1280 × 720 |
| Matched performance target | PASS; median of view p95: 17.078 → 17.164 ms (+0.504%) |
| Final UI visual review | FAIL: Run Relay overlay marker vertically mirrored |

Performance is desktop/compositor wall-clock sampling of 25 static matched
views, 120 measured frames each. It is not an uncapped GPU benchmark or moving
gameplay p95 claim. The raw survey's word "uncapped" records the requested
`--disable-vsync` mode; observed pacing still follows the desktop compositor.

Physical squares were checked using 121 downward collision samples each, with
height agreement under 0.02 m. Entrance corridors were sampled offline over
their full 24 m width and crossed under normal input actions with the shipped
controller. Wall contact, camera obstruction, acceleration, steering, braking,
Hop and landing were also exercised. The shortcut finish trace uses a controlled
start inside the Relay yard, then normal inputs. It proves finish crossing from
the new approach; it is not a full owner-driven Quarry-to-Relay run.

C1 reference SHA-256:
`29f1049f8e16ec65d288407c35e6ccae46e87c711bb6b54b134e6158c68b9443`.
Same test-only synchronization subclass was run in the archived baseline and
successor. No cross-version/platform determinism is claimed.

## Open issues at the bounded stop

1. **Run minimap finish marker is mirrored vertically.** The base map now puts
   north (-z) at the top, but preserved `scripts/run/run_map_overlay.gd` still
   uses `1 - normalized.y`. The orange RLY marker is near the bottom while the
   actual Relay node/craft are at the top. See `complete-3/run_results.png`.
   World-space finish detection passes; this is a misleading UI destination
   marker. A follow-up must align both map projections and verify them together.
2. **CONTINUOUS_WALL_BANDS strict count fails.** The generated boundary has
   14,153 edges. Presentation intentionally skips edges shorter than 0.0001 m;
   six generated edges are between approximately 0.0000001 and 0.00000656 m.
   The new check expects 169,836 vertices for all edges; 169,764 finite vertices
   are emitted for the 14,147 nondegenerate edges. This exactly explains the
   72-vertex difference. The test and renderer need one consistent degeneracy
   rule. The failure remains in the source and raw reports; it is not waived.

## Repair history and visual review

Development checkpoints corrected decorative transform order and the exposed
Quarry shoulder transition. A proposed Works trace crossed frozen rough R0;
the final test uses the actual new smooth westward entrance.

First complete verification (`complete-1`) failed the old C1 comparison only.
Repair 1 froze startup/synchronized sampling and corrected a stale R7 footer.
`complete-2` again failed only C1: 19 initial camera-basis values differed by one
ULP. Repair 2 initializes the test camera transform before snap, giving exact
C1 parity, and extends retaining-wall bands to tiny curved contour segments.
`complete-3` is the final complete run. The two issues above remain; no third
repair round was attempted.

All 25 final views were inspected: six destinations, both sweeps, Quarry Shelf,
South fixtures, representative boundaries, three yards and two overview views.
Walls have readable top/mid bands and the exposed ground remains sparse.
Retained buildings still occlude some landmark bases; high silhouettes remain
the approach cues. Static frames do not establish recognition at speed. The
oblique evidence camera can see the finite terrain sheet edge; that camera is
not available during ordinary play. No playable boundary opening was observed.

## Delivery and owner gates

`tools/package_world_polish.py` writes a complete source ZIP and full SHA-256
inventory, excluding caches/imports/builds/logs/editor-local files/older ZIPs.
The companion `evidence/WORLD_POLISH_SURVEY.html` contains before/after images
and links to raw results. Package and fresh-extraction results are recorded in
the companion `FINAL_HANDOFF.md` and package JSON, outside the hashed source.

All owner feel, preference, freedom, comfort, physical-gamepad and desire gates
remain UNTESTED. See WORLD_POLISH_PLAYTEST.md. No publish, push, PR, external
account change, system install or new dependency was performed.
