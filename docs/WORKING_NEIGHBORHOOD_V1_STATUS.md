# Working Neighborhood v1 — verified successor

2026-09-05. Implemented from the delivered Warm Overcast v1 source ZIP; original source and evidence remain intact. Exact installed engine: `4.7.1.stable.official.a13da4feb`, native Metal Forward+ on Apple M5, 1280 × 720.

All 14 buildings and six landmark families have assigned functions, varied façades, roof equipment, native signs and localized repair/wear. Ten building service fronts and three compound fronts ground the exposed foundations. Closed entrances remain façades. Architecture uses 2,816 native parts, 38 text labels and 161 matching structural colliders; substantial changes remain within occupied plots.

Terrain/world JSON and BIN inputs, roads, pads, boundary, yards, movement, vehicle, camera, minimap, weather and Run rules retain their historical bytes except the explicitly authorized architecture integration and build identity. Runtime architecture collision is intentionally revised within plots.

## Verification

Fresh baseline inventory (623 checks), preservation (340 checks), exact-engine preparation and 180-frame smoke passed before playable edits. Fresh 25-view native baseline and five moving comparisons were captured before edits. The first native launch temporarily waited for a Metal drawable; its diagnostic sample is retained.

Final command: `python3 tools/verify_neighborhood_suite.py --evidence ../evidence/complete-2 --native`.

Final suite: FAIL, 33 command/result records; only the moving performance target failed. All functional checks passed. Full expanded commands and outcomes are in `../evidence/complete-2/suite.json`.

| Check | Result |
|---|---|
| static | PASS; 259 checks |
| preservation | PASS; 392 checks |
| runtime | PASS; 35 checks |
| architecture | PASS; 39 checks |
| weather | PASS; 31 checks |
| run_v0 | PASS; 54 checks |
| paused_retry | PASS; 15 checks |
| C1 unchanged fixture | Exact 1,260-tick parity |
| Vehicle R7 | PASS |
| Entrances | All 12 traversals in Spread/Drive passed |
| Weather on/off | Five input sequences: maximum craft-state component difference 0 |
| Structural render/collision | Shared definitions; native transform maximum delta 0 m; all 28 owner roof rays supported |
| Rain contact | Native roof/ground contact controls passed; all new mesh batches join the static rain mask |
| Contact/recovery | Sustained contact beside altered B01, steering/brake/recovery and clean reset passed |

C1 trace SHA256: `29f1049f8e16ec65d288407c35e6ccae46e87c711bb6b54b134e6158c68b9443`. This is same-platform fixture parity, not a cross-platform determinism claim.

## Performance

Static median of 25 view p95 values: 17.280 → 17.284 ms (+0.02%).

Moving pooled p95 across five routes: 17.745 → 20.263 ms (+14.19%).

Adjacent baseline/successor workloads; desktop/compositor wall-clock timing, not uncapped GPU timing. Moving performance excludes image capture. Individual workloads follow.

Moving performance is variable: complete-1 passed (+0.08%), complete-2 missed (+14.19%). One planned confirmation pair with the review UI idle measured 17.635 → 17.793 ms (+0.90%), passing. No source changes or further repair rounds were made for this repeat. Preserve the miss: there is no unconditional performance pass. Confirmation commands and every workload are in `../evidence/moving-confirmation/performance.json`.

| Workload | Baseline p95 ms | Successor p95 ms | Change |
|---|---:|---:|---:|
| T00_NEUTRAL_ROAM | 17.221 | 17.346 | +0.73% |
| T01_WEST_GATE | 17.206 | 17.353 | +0.85% |
| T02_WEST_SWEEP | 17.207 | 17.383 | +1.02% |
| T03_EAST_SWEEP | 17.168 | 17.309 | +0.82% |
| T04_QUARRY_SHELF | 17.210 | 17.280 | +0.41% |
| T05_MARKET_LOOP | 17.108 | 17.264 | +0.91% |
| T06_RELAY_LINK | 17.303 | 17.535 | +1.34% |
| T07_WORKS_LINK | 17.151 | 17.170 | +0.11% |
| T08_SOUTH_STRAIGHT | 17.215 | 17.126 | -0.52% |
| T09_SOUTH_BENT | 17.373 | 17.326 | -0.27% |
| T10_BOUNDARY_EDGE_A | 17.340 | 17.277 | -0.36% |
| T11_BOUNDARY_EDGE_B | 17.294 | 17.382 | +0.51% |
| T12_BOUNDARY_EDGE_C | 17.286 | 17.217 | -0.40% |
| T13_BOUNDARY_EDGE_D | 17.296 | 17.267 | -0.17% |
| destination_QRY | 17.309 | 17.284 | -0.14% |
| destination_DEP | 17.494 | 17.406 | -0.50% |
| destination_MRK | 17.313 | 17.097 | -1.25% |
| destination_RLY | 17.236 | 17.068 | -0.97% |
| destination_WRK | 17.211 | 17.245 | +0.20% |
| destination_CLN | 17.281 | 17.348 | +0.39% |
| yard_west | 17.241 | 17.408 | +0.97% |
| yard_north | 17.459 | 17.396 | -0.36% |
| yard_market | 17.271 | 17.284 | +0.08% |
| overview | 17.407 | 17.249 | -0.91% |
| oblique | 17.280 | 17.128 | -0.88% |
| QUARRY_DEPOT | 16.856 | 17.595 | +4.38% |
| RELAY_WORKS | 17.624 | 20.433 | +15.94% |
| MARKET_CLINIC | 17.849 | 20.916 | +17.18% |
| T02_WEST_SWEEP | 18.086 | 18.235 | +0.82% |
| T03_EAST_SWEEP | 17.606 | 20.915 | +18.79% |

## Repair history and limits

One bounded repair round used; second unused. Complete-1 automated suite passed, but manual close review failed because Clinic/Depot compound panels were behind curved retaining faces. Repair 1 placed three 2 m closed fronts on visible facets and added six unobstructed approach rays per frontage. Complete-2 reran the whole suite; initial failures/logs remain in evidence.

The survey contains all 25 matched district views, eight close pairs including all six destination families, and five paired five-second native clips. Still views and sampled moving frames were inspected. Full-speed shimmer, comfort, authenticity and physical-gamepad feel are owner judgments; no owner acceptance is claimed. The long Relay–Works moving sequence contacts an unchanged obstacle; separate entrance tests pass. Local HTML browser rendering was unavailable under the browser file policy; offline links and video streams are verified.

## Handoff

Launch `PLAY_WORKING_NEIGHBORHOOD.command`. Read `NEIGHBORHOOD_PLAYTEST.md`. The separate source ZIP, evidence ZIP, before/after survey, exact package/fresh-extraction reports and final handoff are outside this source directory. See `../evidence/WORKING_NEIGHBORHOOD_SURVEY.html` in the unpacked delivery.

Generation: `python3 tools/generate_neighborhood.py`. Preservation: `python3 tools/verify_neighborhood.py`. Package: `python3 tools/package_world_polish.py --output ../District-Zero-Working-Neighborhood-V1-Source.zip --extract ../fresh-extraction`. No dependencies were installed or external actions performed.
