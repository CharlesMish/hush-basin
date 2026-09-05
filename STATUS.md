# Quiet Surfaces v1 — implementation and verification

2026-09-05. Isolated successor from delivered Working Neighborhood v1 source ZIP SHA256 `9d2ab3d884243e2992c7753ba82adec6d84a7668c21696476d5d9eb8a4af450e`. Original source, inventories and evidence remain intact. Exact engine: `4.7.1.stable.official.a13da4feb`; native Metal Forward+ on Apple M5 at 1280 × 720.

Road and ground presentation now uses two 2048 × 2048 offline maps: muted charcoal paving, boundaries evaluated from the original baked routes, 0.6 m worn road transitions, broader dusty shoulders and fixed-seed 8/16/24 m tonal variation. Twelve resurfacing patches and six flush service-cover graphics add sparse maintenance cues. No physical surface changes or new scene objects.

The albedo map is encoded from explicitly linear palette values into sRGB. Native images carry offline mip chains and fixed resource IDs; their RGBA8 and R8 uploads total 27,962,025 bytes (26.667 MiB), below 32 MiB. One existing terrain surface uses clamped linear mip filtering. No runtime surface or mip generation, extra material pass, shader, normal map, reflection pass, light or particle was added.

## Verification

Before edits: baseline inventory (640 checks), preservation (392 checks), exact-engine preparation, 180-frame smoke, 25 native district views and five moving workloads/captures passed. Edge-only native views of both sweeps, Quarry Shelf and Market courtyard were reviewed before maintenance details.

Complete command: `python3 tools/verify_quiet_surface_suite.py --evidence ../evidence/complete-3 --native`.

Observed suite status: **FAIL** (39 command/result records). Expanded arguments, exit codes and logs are retained in `../evidence/complete-3/suite.json`.

Remaining failure: the 10% performance target is not met on every individual moving workload. Pair 1: MARKET_CLINIC, 17.479 to 20.032 ms (+14.61%). No further repairs after the two-round limit.

Final capture interruption: the original native motion capture stalled after two complete routes and eight Market–Clinic frames; its process was stopped with SIGTERM and the suite records FAIL. The unchanged-source, evidence-only recapture returned PASS. Original partial frames and command results remain; no timing was rerun. UI inspection was unavailable (CUA inventory timed out).

| Check | Observed result |
|---|---|
| static | PASS; 259 checks |
| preservation | PASS; 394 checks |
| runtime | PASS; 35 checks |
| architecture | PASS; 39 checks |
| surface | PASS; 28 checks |
| weather | PASS; 31 checks |
| run_v0 | PASS; 54 checks |
| paused_retry | PASS; 15 checks |
| Movement fixture | Exact 1,260-tick C1 parity |
| Vehicle R7 | PASS |
| Entrances | All 12 Spread/Drive traversals |
| Weather isolation | Five weather-enabled/disabled sequences, zero craft-state component difference |
| Rain contact | Native particle roof/ground controls retained |

C1 trace SHA256: `29f1049f8e16ec65d288407c35e6ccae46e87c711bb6b54b134e6158c68b9443`. Same-host/version evidence; not a cross-platform determinism claim.

Loaded terrain vertices, normals, indices and collision-face hashes match the baseline exactly. Scene geometry and collider counts also match. Every patch/cover corner hits exposed heightfield ground; none adds collision. Historical world/classification, architecture, weather, movement, camera, vehicle and Run inputs are preserved by the narrow inventory verifier. Native resources and PNG bytes repeat in a fresh generation directory.

## Performance

Static median of 25 view p95 values: 17.235 → 17.246 ms (+0.06%).

Two adjacent moving pairs ran with the review UI idle, AB then BA. Both are retained. Timing includes desktop/compositor pacing; moving samples exclude image capture. Target: no more than 10% p95 increase. Individual results follow.

| Workload | Baseline p95 ms | Successor p95 ms | Change |
|---|---:|---:|---:|
| T00_NEUTRAL_ROAM | 17.231 | 17.350 | +0.69% |
| T01_WEST_GATE | 17.200 | 17.205 | +0.03% |
| T02_WEST_SWEEP | 17.105 | 17.190 | +0.50% |
| T03_EAST_SWEEP | 17.380 | 17.186 | -1.12% |
| T04_QUARRY_SHELF | 17.042 | 17.127 | +0.50% |
| T05_MARKET_LOOP | 17.142 | 17.223 | +0.47% |
| T06_RELAY_LINK | 17.324 | 17.353 | +0.17% |
| T07_WORKS_LINK | 17.241 | 17.301 | +0.35% |
| T08_SOUTH_STRAIGHT | 17.233 | 17.331 | +0.57% |
| T09_SOUTH_BENT | 17.236 | 17.418 | +1.06% |
| T10_BOUNDARY_EDGE_A | 17.235 | 17.304 | +0.40% |
| T11_BOUNDARY_EDGE_B | 17.404 | 17.462 | +0.33% |
| T12_BOUNDARY_EDGE_C | 17.146 | 17.373 | +1.32% |
| T13_BOUNDARY_EDGE_D | 17.459 | 17.108 | -2.01% |
| destination_QRY | 17.208 | 17.112 | -0.56% |
| destination_DEP | 17.215 | 17.246 | +0.18% |
| destination_MRK | 17.075 | 17.121 | +0.27% |
| destination_RLY | 17.322 | 17.078 | -1.41% |
| destination_WRK | 17.375 | 17.204 | -0.98% |
| destination_CLN | 17.280 | 17.099 | -1.05% |
| yard_west | 17.382 | 17.266 | -0.67% |
| yard_north | 17.152 | 17.361 | +1.22% |
| yard_market | 17.264 | 17.403 | +0.81% |
| overview | 17.121 | 17.283 | +0.95% |
| oblique | 17.276 | 17.146 | -0.75% |

Pair 1 (AB): pooled p95 17.656 → 18.093 ms (+2.48%), FAIL.

| Workload | Baseline p95 ms | Successor p95 ms | Change |
|---|---:|---:|---:|
| QUARRY_DEPOT | 17.495 | 17.464 | -0.18% |
| RELAY_WORKS | 17.641 | 17.750 | +0.62% |
| MARKET_CLINIC | 17.479 | 20.032 | +14.61% |
| T02_WEST_SWEEP | 18.009 | 18.441 | +2.40% |
| T03_EAST_SWEEP | 17.615 | 17.614 | -0.01% |

Pair 2 (BA): pooled p95 18.086 → 17.647 ms (-2.43%), PASS.

| Workload | Baseline p95 ms | Successor p95 ms | Change |
|---|---:|---:|---:|
| QUARRY_DEPOT | 17.557 | 17.736 | +1.02% |
| RELAY_WORKS | 17.225 | 17.361 | +0.79% |
| MARKET_CLINIC | 18.654 | 17.446 | -6.48% |
| T02_WEST_SWEEP | 19.716 | 17.916 | -9.13% |
| T03_EAST_SWEEP | 18.941 | 17.562 | -7.28% |

## Development findings and review limits

Before the first complete run: edge-only review led to the same narrow feather on circular junction/pad boundaries. Repeatability exposed unstable nested resource IDs; native root Image resources now carry fixed root and scene IDs. A numeric JSON-type mismatch in the geometry verifier was corrected without changing its hash values. One cover candidate lay over retained Relay-side geometry and was moved to an exposed Market frontage. Development failures remain in evidence.

Both bounded repair rounds used; no further repair rounds. Complete-1 automated checks passed, but manual review of all 25 views found stepped amber rough-cue and gate-band edges. Repair 1 evaluates the same R0 active interval/width and gate radii continuously with a narrow material feather; the full suite reruns as complete-2. Original source-map snapshot, failed visual review and commands remain in evidence. No geometry or classification changes. Complete-2 then passed functional checks but failed moving pair 2: 17.720 to 21.248 ms (+19.91%), including four individual workloads above 10%. Repair 2 lowers broad albedo variation from 0.035 to 0.020, reduces maintenance contrast and removes roughness noise; complete-3 is the final full run. Texture lookup count and memory are unchanged, so any timing recovery cannot be attributed causally to this simplification. All earlier performance results remain in evidence.

No owner acceptance is inferred from checks. Full-speed shimmer, comfort, authenticity and physical-gamepad feel remain unjudged. Native still views and sampled moving frames are reviewed; five paired five-second clips are supplied. The offline survey has verified local asset links and video streams; its interactive browser layout has not received a rendered review in this pass. The long Relay–Works moving clip reaches a retained obstacle; the separate entrance tests establish passage.

The source ZIP excludes caches, logs, editor state, previous ZIPs and builds. Fresh extraction receives an inventory/world check, preservation check, exact-engine preparation and 180-frame smoke. Package hashes and those final results are in the external FINAL_HANDOFF.md and evidence reports.

Launch `PLAY_QUIET_SURFACES.command`; use `QUIET_SURFACES_PLAYTEST.md`. Generate with `python3 tools/generate_quiet_surfaces.py`. No dependencies, external assets or external actions.
