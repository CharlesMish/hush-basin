# First Courier Slice v1 — verification, 2026-09-15

Candidate only; no deployment or remote push. Baseline is accepted World Identity
/ Detail v2 `0e995643c36d32e4ce03ef0d1b3b390949080480`, copied into independent
baseline/candidate checkouts. Exact installed engine verified and used:
`4.7.1.stable.official.a13da4feb`. Native captures use Forward+ Metal4, Apple M5,
1280 × 720. Baseline and final inventory audits cover 480 accepted tracked files.

## Observed results

| Lane | Result |
|---|---|
| Untouched baseline preparation | PASS, exact engine import/parse |
| Untouched baseline Detail v2 integrity | PASS |
| Untouched baseline C1 / vehicle / Run | 1,260 ticks / 39 checks / 54 checks PASS |
| Candidate accepted-file preservation | PASS; only main-scene selection and reviewed Web diagnostic-helper diff permitted |
| Candidate C1 | All 1,260 JSONL rows byte-identical to fresh baseline |
| C1 with real cargo observer attached | All 1,260 JSONL rows byte-identical to fresh baseline |
| Cargo native physics/reducer probe | 19/19 PASS |
| Courier native Forward+ integration | 20/20 PASS |
| Quarto vehicle | 39/39 PASS |
| Run v0 | 54/54 PASS |
| Run paused retry | 15/15 PASS |
| World/entrances | 35/35 PASS, including all 12 entrance traversals |
| Weather/reset | 31/31 PASS |
| Native rain contact | 3/3 PASS |
| Courier Web diagnostic | 20/20 PASS, Compatibility in Chromium 151.0.7922.34 |
| Original Run Web diagnostic | 13/13 PASS |
| Playable Web keyboard smoke | PASS: Dispatch, accept, active drive/steer, pause/resume, 1280 × 720 canvas; no script/page errors |

Shared C1 SHA256:
`29f1049f8e16ec65d288407c35e6ccae46e87c711bb6b54b134e6158c68b9443`.
This is exact parity on this engine/platform/fixture, not a cross-platform
physics-determinism claim.

Cargo fixture: clean sustained Drive drift, transform/brake and supported Hop
all lost 0 units. Brush lost 0; glance 4; strike 186. Eight seconds of sustained
wall pressure generated 462 raw impact samples but **one** episode and 139
units loss. The reducer also passes 30/60/120 Hz peak-charge equivalence,
increasing-peak charging and zero-condition clamping.

The integration probe drove the direct Market–Depot yard shortcut using ordinary
input actions from acceptance through delivery, with no pose/velocity writes.
Both forms were used; cargo remained 100%. A typical captured run took about
12 active seconds. The origin/destination centers are about 123 m apart, so
the shortest route is deliberately brief. Separate **synthetic** placements
test fast-crossing rejection, settle time, zero-condition delivery after an
hour of elapsed evidence, fall/reset cancellation and diagnostic relocation.
They are not represented as human drives. Continue leaves transform/velocity
untouched. Results evidence is read-only. Clock and weather pause together.

## Cost and build size

Adjacent native order A1/B1/B2/A2, no review browser running. Accepted free roam
versus active courier, same Market start, unchanged ordinary camera and input
sequence; two-second warmup then eight seconds each of static/moving sampling.
Every workload and raw sample is retained.

| Pair | Static baseline → candidate p95 | Moving baseline → candidate p95 |
|---|---|---|
| AB | 16.767 → 16.796 ms (+0.17%) | 16.780 → 16.792 ms (+0.07%) |
| BA | 16.785 → 16.789 ms (+0.02%) | 16.794 → 16.785 ms (−0.05%) |

These runs remained frame-paced near 60 Hz despite the requested disabled vsync.
They show no observed pacing regression in these workloads; they do **not**
measure spare GPU headroom or settle the district's historical performance issue.
Web requestAnimationFrame p95 was 18.6 ms for both ten-second idle and steering
workloads on this Chromium/M5 run; no matched-browser performance claim is made.

| Artifact | Accepted Detail v2 | Courier | Change |
|---|---:|---:|---:|
| Playable Web PCK | 101,862,156 B | 101,958,300 B | +96,144 B (+0.094%) |
| Complete playable export | 141,709,889 B | 141,806,033 B | +96,144 B (+0.068%) |

The before sizes are retained accepted-delivery measurements. Final exports use
the unchanged pinned single-thread template and established Compatibility lane.
The hosting split, loader and production build are unchanged. Diagnostics are
separate exports and must not be deployed as the playable game.

## Limits and retained findings

- Cargo attribution is deliberately conservative: terrain, upward-facing and
  ambiguous mixed contacts are forgiven. Some genuine angled/mixed impacts may
  therefore cost nothing. Human fairness remains unproven.
- Physical gamepad, Safari/Firefox, low-end hardware, comfort and enjoyment were
  not tested. Keyboard and synthetic game-action tests do not pass those gates.
- The default route is short. Arrival currently uses the existing pad and a
  Results card, without a new handoff animation/audio/NPC. Judge whether that
  is satisfying before adding systems.
- The historical minimap's Web north-arrow glyph can render as a missing glyph;
  the existing map and projection were intentionally retained.
- Historical `verify_repo.py` fails its old R7 hash freeze on the untouched
  accepted baseline (`.gitignore`, `vehicle_visual.tscn`, `vehicle_visual_rig.gd`;
  3 failures among 389 checks). That result is retained. The current preservation audit
  uses the accepted Detail v2 inventory; no historical validator was rewritten.
- The retained Quiet Surfaces Market–Clinic **+14.61% p95** finding and recovered
  capture interruption are not erased or reclassified by this checkpoint.
- Early implementation logs retain resolved GDScript type-declaration errors
  and an incomplete synthetic keyboard-event test. Final events include both
  physical and logical keycodes, matching the existing regression helper.
  The final native/Web checks above pass. One bounded delivery-tool repair made
  the new inventory verifier independent of Git metadata for ZIP users; no
  post-verification gameplay repair was needed.

## Reproduce

From the candidate source root, `python3 tools/launch.py --prepare-only` and
`python3 tools/verify_courier_preservation.py`. Run the following scripts with
the exact engine, `--path game --script res://tests/<script> --log-file` followed
by an **absolute** log path, then `-- --result` and an absolute JSON path:

- `courier_cargo_probe.gd`, `courier_slice_native.gd`
- `quarto_vehicle_v1.gd`, `run_v0_probe.gd`, `paused_retry_addendum.gd`
- `world_polish_runtime.gd`, `quiet_surface_weather.gd`, `overcast_rain_contact.gd`

Use native rendering for weather/contact and UI captures. C1 scripts
`world_polish_c1.gd` and `courier_observed_c1.gd` use `--output`, not `--result`.
For courier screenshots add `--captures <absolute-directory>`; optional `--clip`
writes sampled frames. The supplied short clip is 15 fps diagnostic capture,
not a performance measurement.

Web (from the retained candidate Git checkout; the existing exporter records
Git metadata): `python3 tools/export_web.py --output <new-directory>`; add
`--courier-smoke` or `--smoke` for the two separate diagnostics. Never overwrite
an export or use a diagnostic as the playable build. Serve the output on local
loopback for Chromium; no production action is needed.

The adjacent evidence packet retains exact absolute commands, raw logs,
per-check JSON, inventories, exports, screenshots and the short moving clip.
The source ZIP excludes caches, raw captures, exports, other ZIPs and Git data.
