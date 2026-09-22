# Mechanics Range v1 — verification and limits

Exact starting point: public `review/courier-alpha-v0.2`,
`feb30b6205b6b89ad66a3d6eada2c7b1feb18273`. Isolated local successor branch:
`feature/mechanics-range-v1`. The delivery's `DELIVERY.json` binds the final
commit, source ZIP and exported game hashes. No push, main update or deployment.

Engine: `4.7.1.stable.official.a13da4feb`. Native captures: Metal 4 Forward+,
Apple M5, 1280×720. Browser checks use the existing pinned single-thread Web
template and local Chromium; hosting source and production are untouched.

## Preservation and gameplay

| Lane | Observed result |
|---|---|
| Fresh review baseline | Native alpha 76/76; cargo 92/92; C1 captured before changes |
| Public source inventory | 581 baseline files checked; exactly six declared existing-file changes |
| Movement C1 | Exact 1,260-tick parity, with trail and with cargo protection |
| Cargo matrix | 92/92 unprotected and 92/92 protected |
| Raw controller evidence | All 3,440 records identical in both candidate cargo runs; unprotected full cargo events also identical |
| Quarto vehicle | 39/39 |
| Run v0 | 54/54; separate mode retained |
| Paused retry | 15/15 |
| World / entrances | 35/35, including all 12 entrance traversals |
| Weather reset/contact predicates | 30/30 headless; new bar is in the particle heightfield render mask |
| Native geometry | 16/16; all 162 old colliders and terrain arrays identical; one new matched visible/solid box |
| Final mechanics integration | 87/87 headless; 87/87 native; 87/87 sparse capture repeat |
| Web mechanics integration | 87/87 after diagnostic-wrapper repair; all three intended bonus runs and base-only alternatives delivered |
| Web Run / playable smoke | 13/13 Run; playable Dispatch/accept/drive/pause/F2/F3 smoke passed; no browser errors |

C1 baseline/candidate/protected SHA-256:
`29f1049f8e16ec65d288407c35e6ccae46e87c711bb6b54b134e6158c68b9443`.
This is exact parity on this engine/platform/fixture, not a cross-platform
determinism claim. Frozen movement, tuning, craft scene, camera, Quarto, BRRR,
cargo grouping and protection source are byte-identical to the review baseline.

The 87-check suite exercises real acceptance and ordinary-input routes, bonus
hits/misses, repeats, zero cargo, once-only receipts, liner purchase, unchanged
raw impact evidence, pause/reset/F3, Continue at destination and driving home.
Explicit synthetic endpoint/contact predicates are labeled in the suite; they
are not presented as whole-route human play. The final native easy Depot and
interior Relay runs miss their bonuses. Works hot-hit recovery delivers base
only. The northern Works bypass retains 100% cargo.

48 calibration trials, including failed attempts, are in
`docs/mechanics_calibration_matrix.csv`; definitions and target rationale are in
`MECHANICS_CALIBRATION.md`. Final ordinary native receipts include Depot Style
145.60 slip BRRR / 100% cargo, Relay sweep 6.30 s streak / 96.3% cargo, and Works
Hop / 100% cargo. All three earn their bonus. The across-bar Works path crosses
near its end, not the exact midpoint; projected evidence is retained.

## Native cost and Web size

Adjacent A1→B1 then B2→A2 workloads, review overlays hidden, no automated review
UI activity. Each samples eight seconds after two seconds of warmup. Every raw
frame time and workload is retained in the evidence directory.

| Workload | Baseline p95 | Candidate p95 | Movement |
|---|---:|---:|---:|
| Static, pair 1 | 16.760 ms | 16.760 ms | 0.00% |
| Moving, pair 1 | 16.817 ms | 16.878 ms | +0.36% |
| Static, pair 2 | 16.772 ms | 16.770 ms | −0.01% |
| Moving, pair 2 | 16.926 ms | 16.957 ms | +0.18% |

These are frame-paced process-frame measurements near 60 Hz, not GPU headroom
or district-wide worst-case proof. End positions are identical in each pair.
No unfavorable pair was dropped. Both moving pairs meet the +10% target.

| Playable Web artifact | Accepted alpha | Candidate | Increase |
|---|---:|---:|---:|
| PCK | 102,208,144 B | 102,341,552 B | 133,408 B |
| Complete export | 142,055,877 B | 142,189,285 B | 133,408 B |

The increase is about 130.3 KiB: +0.131% PCK and +0.094% complete export.
All 409 final export input hashes match the candidate game source. Export records
retain the pre-commit parent identity and their full input hashes; delivery binds
them to the final committed tree rather than rewriting historical build records.

Local browser: Chromium 151.0.7922.34, 1280×720, WebGL2 Compatibility. Full-build
rAF p95 was 18.2 ms for both active idle and sustained drive/steer; these unpaired
browser samples are smoke observations, not a before/after performance claim.
The small north-arrow glyph appears as a fallback box in the Web minimap; the
unchanged map code and functional direction/markers remain usable. No repair of
that carryover presentation issue is included here.

One bounded repair round followed the complete native/Web attempt: the new Web
diagnostic wrapper had overridden `_ready()` without the inherited ALWAYS
processing setup, so it stalled at paused Dispatch and timed out after 360 s.
Removing that redundant override restored the shared probe setup. Re-exported
diagnostic and browser rerun passed 87/87 in 207.3 s with no browser errors.
Playable game source, native results, full export and performance inputs did not
change. The failed browser attempt and corrected result are both retained. No
second repair round was used.

## Visual review and known limitations

Five matched before/after native camera views cover the Works approach/warning/
close view, Depot yard and Relay entry. Three native MovieWriter clips show
ordinary-input bonus runs at normal simulation speed, 30 fps; these are offline
review captures, not performance samples. Separate sparse PNG sequences are
retained but can perturb input timing and are not calibration authority.

The existing speed-responsive surface spray remains unchanged. The new bounded
twin ribbons add slip/streak feedback beside it; an earlier inspection statement
that there was no existing trail was too broad. There was no dedicated BRRR
ribbon, but the surface spray was already visible behind the craft. The ribbons
are legible in native captures and do not obscure the approaching service bar.
Whether their flat graphic appearance improves the aesthetic is unpassed owner
review. No shader, texture, particle emitter, light or handling change was added
for them. History is capped at 18 samples / 0.52 seconds.

No Depot furniture or Relay hazard was necessary. Works adds one 10×1.8×1.14 m
service conduit sampled from L6, amber face bands, a shallow top cover and a
35 m advance pavement label. The existing road, terrain and boundary are intact.
Hop, side-pass and northern bypass remain legal. The bar's ordinary driving
readability is shown; its full-width Hop margins and every possible approach
have not been exhaustively tested.

Relay's sampled completed interior runs miss the streak; the chosen outer line
earns it with a minor glance. This does not prove every interior shortcut is
incapable of earning six seconds. A failed collision-heavy interior experiment
accumulated a streak. The unchanged seed metric is not anti-farming enforcement.
Depot remains short, and deliberate repeated drifting can earn its objective
away from a particular yard location. Neither objective has hidden route checks.

Development failures were retained: an initial probe named the wrong telemetry
property; a mixed-indentation script failed parsing; an old synthetic wall strike
did not register the intended contact; initial road-following Hop trials skirted
the bar; an initially misaligned hot-input fixture did not spend Care. These were
corrected in probes/setup before the complete verification, without cargo or
movement retuning. Older historical geometry/contract freezes remain historical,
not relabeled passes. Prior reported performance failures are not erased.

Human difficulty, comfort, desire to improve, bonus anxiety and authored-road
feel remain Charlie's gates. See `START_HERE_MECHANICS_RANGE.md`. Stop here: no
fourth job, save, economy framework, story system, push or production deployment.

## Reproduction entry points

From this source tree, use the exact engine above and fresh external output paths:

```sh
python3 tools/verify_mechanics_range.py
/Applications/Godot.app/Contents/MacOS/Godot --path game --script res://tests/mechanics_loop_native.gd -- --result <LOCAL_TEMP>/mechanics-result.json --cargo-log <LOCAL_TEMP>/mechanics-cargo.jsonl
python3 tools/export_web.py --output <LOCAL_TEMP>/mechanics-playable
python3 tools/export_web.py --mechanics-smoke --output <LOCAL_TEMP>/mechanics-web-check
python3 tools/export_web.py --smoke --output <LOCAL_TEMP>/mechanics-run-check
```

The sibling evidence packet retains exact command arrays, fixture outputs,
calibration plans, native movies, browser logs and AB/BA samples. Historical
validators remain intact; use the explicit successor probes for changed bonus
and added-geometry expectations.
