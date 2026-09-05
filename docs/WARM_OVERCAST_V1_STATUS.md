# Warm Overcast v1 status — September 5, 2026

State: IMPLEMENTED; COMPLETE AUTOMATED NATIVE SUITE PASS; OWNER REVIEW PENDING.
One bounded repair round was used. No second repair round was needed.

Source baseline: World Polish v1 ZIP SHA-256
`73da6d12be0301e036047dcbdebbfbd65de3e2dbb839dafedbcd30a97883923d`.
Original repository and previous source/evidence remain intact. Installed
engine: `4.7.1.stable.official.a13da4feb`, native Metal Forward+, Apple M5.

## Changes and preservation

One presentation configuration controls a stationary native-noise panorama,
soft warm daylight, 384 world-space GPU drizzle streaks over a 48 m footprint,
static particle-only roof/ground collision, and classified damp paving.
Pause freezes weather. Retry, fall reset and diagnostic relocation restart it.
The Run overlay now shares the base minimap projection. Rendering and its
verifier share the explicit 0.0001 m decorative-edge minimum: 14,147 eligible
edges, six accounted-for microscopic omissions, 169,764 finite band vertices.

All v1 world inputs, generated geometry, terrain heights, classifications and
configuration bytes are unchanged. Terrain vertex positions, normals, indices
and collision construction are preserved; visual colors, UVs and materials
change. Craft, tuning, collider/probes, vehicle rig, controls, camera, Run
director/HUD/BRRR and Run scene are unchanged. Only Run's map overlay changes.

## Exact verification

Evidence root:
`/Users/cmish/Desktop/Hush-Basin-Movement-Lab-Handoff/District-Zero-Warm-Overcast-V1-Run-1/evidence`.

Fresh pre-edit baseline: inventory 605/605 PASS, exact-engine import/parse and
180-frame smoke PASS, 25 native views and five native moving comparisons.

Complete command from successor source:

```sh
python3 tools/verify_overcast_suite.py --evidence /Users/cmish/Desktop/Hush-Basin-Movement-Lab-Handoff/District-Zero-Warm-Overcast-V1-Run-1/evidence/complete-2 --native
```

Observed: overall PASS, 27/27 suite records. `complete-2/suite.json` records
every subprocess argv, cwd, exit code and result; companion JSONs contain checks.

| Check | Result |
|---|---|
| World integrity, finite geometry, byte-repeatable generation | 259/259 PASS |
| v1 preservation and presentation configuration | 340/340 PASS |
| Import/parse and vehicle R7 choreography | PASS |
| Unchanged C1 movement fixture | Exact 1,260-tick SHA-256 match |
| Run startup, finish, retry, fall and free roam | 54/54 PASS |
| Paused retry | 15/15 PASS |
| World runtime and carryover wall check | 35/35 PASS |
| Six entrances in both Spread and Drive | 12/12 PASS; zero impacts/unsupported ticks/resets |
| Native weather, seam/repeatability, map, mask and transitions | 31/31 PASS |
| Native particle contact with ground, roof and retaining top | 3/3 PASS with collision-disabled visibility controls |
| Weather enabled/disabled movement | 1,500 samples exact; maximum component difference 0.0 |
| Native static survey | 25/25 matched 1280 × 720 images |
| Native moving survey | Five matched sequences; 75 frames per clip at 1280 × 720 |

C1 SHA-256:
`29f1049f8e16ec65d288407c35e6ccae46e87c711bb6b54b134e6158c68b9443`.
This is exact parity on the installed engine and machine, not a cross-platform
physics determinism claim. The weather A/B uses identical successor resource
construction with weather processing/visibility enabled or disabled.

The native particle diagnostic emits test drops inside three real surfaces.
Hide-on-contact produces zero visible drop pixels at each surface; disabling
contact produces visible drops at each. The shipped emitter remains faint and
bounded. No diagnostic material or camera is used during normal play.

## Performance and visual review

Complete-2 static median of 25 view p95 values: **17.494 → 13.357 ms**.
Complete-2 moving pooled p95 across five sequences: **16.870 → 15.257 ms**.
Both aggregate comparisons are within the +10% target. Three individual clips
(Market–Clinic, West Sweep and East Sweep) exceed +10% against the earlier
baseline; the per-clip data is retained, not hidden by the aggregate result.
An additional adjacent baseline/successor pair measures pooled p95
**16.222 → 15.415 ms**; all five individual clips stay within +10%, with a
maximum increase of 3.5802% (Relay–Works). Both sets of results are retained.
The earlier per-clip regression did not reproduce in this adjacent pair.
These are desktop/compositor wall-clock samples,
not GPU-only benchmarks or evidence of a speedup. Video capture I/O is excluded
from timing. The first complete run's timings are retained separately.

All 25 native views were reviewed, including all destinations, sweeps, yards,
Quarry Shelf, South and boundaries. Cool cloud layers and the pale warm horizon
separate silhouettes; roads and accents remain readable. Damp paving is broad
and subdued. The rain is deliberately fine and intermittent in a still frame.
Moving clips cover the three yards and both sweeps, with acceleration, sustained
steering and braking. Relay–Works' long moving clip contacts a retained obstacle
in both builds; the separate entrance tests establish clear passage. Evidence
overview cameras can see the finite terrain sheet edge outside ordinary play.
Owner comfort, taste and drizzle preference remain untested.

## Bounded repair record

`complete-1` passed the planned fixture, world, Run, weather, rain-contact and
aggregate performance checks. An additional strict cross-version moving-trace
comparison failed only in the Relay clip after tick 243, while settling against
a retained obstacle (maximum component difference 0.1199715). Four clips were
exact. Its FAIL and raw evidence are preserved.

Repair round 1 changed only that added verification: require exact weather
enabled/disabled motion on the same successor resource construction, retaining
cross-version motion as a diagnostic. The narrow A/B and the complete rerun both
report 0.0 difference, including contact. No gameplay code or tolerance changed.
The unchanged 1,260-tick C1 comparison remains mandatory. No further product
changes followed the complete rerun.

## Handoff

The new source ZIP has its own `WARM_OVERCAST_V1_SHA256SUMS.txt`; historical
manifests remain unchanged. Packaging verifies ZIP CRC and every source byte,
then performs a fresh extraction. Exact package hashes and fresh-extraction
results are in companion `FINAL_HANDOFF.md` and JSON, outside the hashed source.
The HTML survey includes paired native stills and short moving videos.
Use WARM_OVERCAST_PLAYTEST.md for Charlie's review.

Original repository final integrity: R7 234/234, Run overlay 9/9, retained P1B
65/65; clean. Previous World Polish package integrity: 605/605 PASS.
No external assets/dependencies, installation, publication or account changes.
