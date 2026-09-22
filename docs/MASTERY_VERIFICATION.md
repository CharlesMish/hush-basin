# Mastery Alpha v1 — observed verification

Engine: `/Applications/Godot.app/Contents/MacOS/Godot`, exact
`4.7.1.stable.official.a13da4feb`. Native Forward+, 1280 × 720 on the existing
Apple M5/macOS host. No engine, template, system tool or dependency installed.

Runtime implementation commit:
`21f29a72e4f179972d349f6b84dcf10e188e3c6e`. The later handoff commit contains
documentation only. Final export manifests hash the exact game source; the
delivery record and source ZIP identify the final handoff commit.

## Preservation and integration

| Check | Observed result |
|---|---|
| Accepted inventory before work | V1.1 verifier PASS, 612 historical entries; exact accepted Git source has 640 tracked files |
| Successor inventory | PASS, all 640 baseline files present; only six existing files changed under the narrow authority |
| Movement | Four 1,260-row traces exactly equal the fresh accepted trace: ordinary, liner, amber palette, both |
| Trace SHA256 | `29f1049f8e16ec65d288407c35e6ccae46e87c711bb6b54b134e6158c68b9443` |
| Cargo | 92/92 unprotected and 92/92 protected; unprotected matrix is JSON-value-identical to fresh baseline, including 3,440 events |
| Quarto vehicle | 39/39 |
| Run v0 | 54/54 |
| Paused retry addendum | 15/15 |
| World | 35/35, including all twelve entrance traversals |
| Weather | 30/30 reset/contact/preservation checks |
| Successor line/payment predicates | 42/42 |
| Route observer predicates | 23/23 |
| Mastery/session/palette | 47/47 |
| Three-card HUD fixture | 120/120 after integration wording adjustment |
| Integrated headless game | 127/127 |
| Integrated native game | 127/127; no engine/script errors |
| Local Web launch and controls | PASS, 1280 × 720, no browser/script errors |
| Local Web Run diagnostic | 13/13, no browser/script errors |
| Local Web courier/mastery diagnostic | 127/127, no browser/script errors |

The integrated checks include all five accepted/delivered jobs, normal-input
return home, zero-condition/all-objective-missed base payment, repeated/once-only
receipts, all five seals earned by driving, still-open contracts, liner and
appearance purchase guards, free equip with unchanged craft state, Continue at
the reached destination, F3 cargo evidence, weather restart and partial Haul
cancellation through manual retry, fall and diagnostic relocation. Synthetic
endpoint/contact/reset cases are explicitly separated from driven routes.

Movement equality is a local same-engine/platform result, not a claim of Godot
physics determinism across versions or platforms. All movement, rig, collider,
camera, world, weather, BRRR, cargo and accepted drift-observer source is
byte-identical. Six previously untracked V1.1 UID metadata files are supplied
with the successor; the owner's original six files remain untouched.

## Calibration and native visual review

The independent challenge lane retained 21 ordinary-input route trials, with
four exact trace/result repeats locally. The integrated game then delivered
fourteen route cases natively and headlessly, plus a driven return to Market.
Every delivered route remained valid even when its optional objective missed.
The matrices retain naive routes, alternate routes, intended successes and
contact failures, including the old Haul recipe that now correctly misses.

Native full-game examples: Depot straight 9.23 s misses Style; deliberately
shaped 20.48 s drive earns a 3.78 s chain. Relay interior 21.75 s misses; outer
33.70 s delivery records a 9.00 s Sweep. Works early-mode 9.88 s succeeds with 100%
cargo; hot recovery 11.53 s still delivers at 76.1%, missing Care. Thread direct
10.12 s misses; dogleg 49.87 s and Hop 47.05 s both qualify. Haul short 22.87 s
misses; long 89.22 s completes both geographic phases at100% cargo.

The isolated calibration explains provisional Relay 10 s: organized 24/27 m/s
recipes measured 10.00/9.00 s, versus conservative 12.40, slower 11.30/13.00 and
Spread 24.17. Three clean mixed Haul variants measured 87.45–88.00 s; hot Drive
61.02 s contacts Shelf and misses; all-Spread 117.63 s is valid. No thresholds
were changed to make an automated example pass. Improved Shelf lookahead is a
test driver's ordinary steering recipe, not a craft tuning change.

Fresh baseline board and seven approach views precede editing. Native candidate
captures cover the compact board, all jobs' Results, mastery/reward, F3 and
return cue. Seven 1280 × 720/30 fps clips show accepted Style, candidate standard
and amber Style, Relay, Works, Thread and Haul at ordinary gameplay cadence.
Amber is forced only in its diagnostic visual comparison; normal play requires
the purchase. Both palettes retain the same visible response to qualifying slip. Their complete
Style driving traces and receipts are exactly equal, in addition to the movement
fixture comparison.
No new furniture was integrated. Owner preference/comfort are not marked passed.

## Performance — all adjacent AB/BA workloads retained

Each workload measures 8 s native process-frame cadence after 2 s warmup, with
the review overlay hidden and no concurrent automated GUI workload. A=accepted
V1.1; B=candidate. All four workloads run in A/B then B/A order.

| Pair | Workload | Baseline p95 ms | Candidate p95 ms | Change |
|---|---|---:|---:|---:|
| AB | Static |16.786|16.801|+0.09%|
| AB | Moving Style |16.888|16.914|+0.15%|
| AB | Moving Sweep |16.884|16.920|+0.21%|
| AB | Moving Haul |16.927|16.876|-0.30%|
| BA | Static |16.797|16.812|+0.09%|
| BA | Moving Style |16.866|16.922|+0.33%|
| BA | Moving Sweep |16.877|16.865|-0.07%|
| BA | Moving Haul |16.869|16.910|+0.24%|

Pooled static p95: 16.793→16.806 ms(+0.077%). Pooled moving
p95: 16.882→16.906 ms(+0.142%). Every individual workload is within 10%.
These vsync-limited pacing samples do not establish unused GPU headroom. Raw
samples, positions, draw counts and both orders remain in the evidence.

## Web size and architecture

| Artifact | Accepted V1.1 bytes | Candidate bytes | Change |
|---|---:|---:|---:|
| Web PCK |102,499,916|102,750,828|+250,912(+0.245%)|
| Complete full export |142,347,649|142,598,557|+250,908(+0.176%)|

Pinned single-thread release template and WASM integrity checks pass. Complete
and diagnostic exports are separate. Hosting/Cloudflare source is unchanged;
browser regression uses localhost only. No production URL was touched.

## Historical failures and preparation issues

- Historical `verify_repo.py` already rejected successor vehicle/.gitignore
  bytes at baseline. It is retained as historical evidence, not silently reset.
- Unmodified V1.1 payment predicates now report 38/40: two old positive-payment
  assertions expect the replaced Relay/Haul mode counters to award bonuses.
  New 42-check successor predicates explicitly reject those counters and require
  the new route evidence. All old drift/control predicate assertions still pass.
- Initial headless import encountered sandbox denial creating the newly named
  user-data directory, plus the host CA-certificate warning. Normal authorized
  Godot preparation resolved the directory issue. Native game logs are clean.
- A pre-integration HUD assertion failed when a T-key label omitted the word
  “switch”; the clearer label restored 120/120. Early lane parse/bootstrap logs
  and failed calibration routes are retained, not relabeled as successful runs.
- Zero bounded repair rounds after the first complete integrated verification. No gameplay change followed the successful native/Web gates.

Remaining owner gates: Sweep section entry legibility and human 10 s difficulty;
Shelf no-touch forgiveness; mastery motivation; reward desirability; five-job
favorite/replay behavior; return-to-Market fatigue; controller comfort. No work
tier was validated, and no claim of long-term progression across app sessions
is possible without future persistence. No persistent save was added.

## Reproduction and evidence index

`python3 tools/verify_mastery_alpha.py` verifies exact preserved source.
Run installed Godot with `--headless --fixed-fps 60 --path game --log-file ABS_LOG
--script res://tests/mastery_native.gd -- --result ABS_JSON`. Native captures
omit `--headless` and add
`--captures ABS_DIRECTORY`. The standalone preservation scripts remain at their
historical paths; `mastery_c1.gd` selects the owned palette in the same fixture.

Web: `python3 tools/export_web.py --output NEW_DIRECTORY`; diagnostic flags are
`--mastery-smoke` and `--smoke`. These export only; use the retained local browser
lane to exercise them. No deployment command is part of this review.

The sibling `evidence/` folder contains exact command arrays in
`baseline-commands.json`, `integration-check-commands.json`,
`preservation-commands.json`, `challenge-lane-commands.json`,
`cost-commands.json` and `finish-review-commands.json`. Results include
`movement-parity.json`, `native.json`, `integrated.json`,
`integrated-calibration-matrix.json`, `challenge-route-matrix.json`,
`performance.json`, `build-size-comparison.json`, browser results/console logs,
export build manifests, individual traces, native PNGs and seven MP4s.
