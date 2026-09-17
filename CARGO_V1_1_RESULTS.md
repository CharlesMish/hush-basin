# Cargo feel adjudication — exact results

Baseline: accepted Courier v1 `90d2c3ee7e3286dc82001daf7be4149f158387f8`.
Independent baseline and successor checkouts; exact installed Godot
`4.7.1.stable.official.a13da4feb`, Apple M5/macOS. No external action/deployment.

## Diagnosis and narrow correction

No random damage was found. All 3,440 fresh impact samples in **each** final
matrix agree with the captured same-frame pre-impact argument and the unchanged
controller severity formula. All corresponding controller evidence fields are
byte-for-byte equal between the two matrices. The cargo curve is monotonic at
all 1,001 quantized severity values and is unchanged in v1.1.

The baseline failed three successor criteria: a resting/slow Spread touch gained
1.4% extra loss through continued pressure; three clearly separated contacts
0.1 seconds apart merged into one episode in each form. The final correction
removes pressure escalation and recognizes clear outward separation.

This does not establish the cause of the owner's particular unrecorded Spread
incident. In the controlled fresh-cargo head-on cases, nominal 2 m/s costs zero;
nominal 8 / 9 / 9.3 m/s in Spread costs **15.7 / 20.9 / 22.4%**. Angles, episode
history, remaining condition, and pre/post-impact timing matter. Do not call
the original incident “explained” without its trace.

## Observed checks

| Lane | Observed result |
|---|---|
| Untouched v1 inventory + exact-engine preparation | PASS |
| Untouched v1 cargo regression | 19/19 PASS |
| Corrected identical 50-case fixture, v1 policy | 89/92 successor criteria; three diagnosed failures retained |
| Same fixture, final v1.1 | **92/92 PASS** |
| Clean controls | Drift, braking, transformation, supported Hop/landing, normal travel and stale telemetry: zero loss |
| Pressure from rest near wall | Spread 1.4% → 0%; Drive 0% → 0%; one episode in both |
| High-speed arrival then 10 s pressure | One episode, one 24% charge; no per-frame rebilling |
| Three distinct 12 m/s hits, 0.5 s clearance | Three episodes, 72% total in both forms |
| Three distinct 12 m/s hits, 0.1 s clearance and 3.5 m gap | v1 one episode/24%; v1.1 three episodes/72%, both forms |
| Native review entry / receipt / bookmark / pause | **8/8 PASS**, Forward+ at 1280 × 720 |
| Fresh baseline vs final review-hook C1 | **Exact 1,260-row byte parity** |
| Courier native integration | 20/20 PASS, including zero-condition/slow delivery and continue at Depot |
| Original Run | 54/54 PASS |
| Original paused retry | 15/15 PASS |
| Historical v1 cargo test on successor | 18/19; only `rising_peak_only` intentionally superseded by entry-only billing |
| Full 514-file accepted inventory | PASS except the two explicitly bound cargo files |
| Web courier diagnostic | 20/20 PASS |
| Web Run diagnostic | 13/13 PASS |
| Playable Web keyboard smoke | PASS; no script/page errors |

C1 SHA256:
`29f1049f8e16ec65d288407c35e6ccae46e87c711bb6b54b134e6158c68b9443`.
Parity is established on this engine/platform/fixture, not across platforms.

Only `cargo_observer.gd` and `courier_rules.gd` change existing accepted source.
Controller, impact response, motion math, tuning, craft scene, vehicle rig,
collider/probes, camera, world/terrain/collision, weather, Run, BRRR, courier loop,
UI and Web export/hosting tools remain byte-identical. New files are review
instrumentation, fixtures, documentation and a separate review launcher.

## Instrumentation and evidence

The disposable `review_craft.gd` captures the existing `pre_move_velocity`
argument and immediately calls the unchanged superclass method. It does not
override integration, movement inputs or collision response. Native trace parity
proves this hook did not change the recorded movement fixture.

Every accepted loss records incoming world speed/vector, controller closing
speed/severity/form/fold/counter, physics-frame freshness, parcel/episode identity,
billed episode peak, increment, cumulative loss and remaining condition. Raw
fresh impacts without new charges are recorded too. Contact normals/source IDs,
native realized speed and position delta provide extra context. `episode_prior_peak_units`
is the observer's value before the current sample; if the episode changes, it
belongs to the prior episode. `controller_episode_peak_severity` can keep rising
under pressure; `episode_peak_severity` is the frozen billed entry.

The matrix uses one flat plane and one vertical wall, controlled initial
velocities, and the unchanged craft. Repeated-contact grouping uses explicit
synthetic placements, including 3.5 m outward clearance. These are reproducible
mechanism tests, not owner drives. The world receipt smoke also uses an explicit
synthetic starting placement; its camera view is not a gameplay-camera review.

Initial diagnostic logs retain a case-name format error, a drift control that
actually reached the wall, and a repeated-hit fixture with insufficient contact
ticks. The corrected baseline and candidate use the identical 50-case method.
One bounded repair of the first candidate prevented ambiguous/nonfresh contact
reports from opening a zero-charge episode before a genuine fresh impact. Final
matrix, receipt, movement and integration checks pass. No damage-curve tuning
was performed.

## Web and limits

Chromium 151.0.7922.34, existing single-thread Compatibility export lane. PCK:
101,958,300 → **101,999,860 bytes**. Complete export: 141,806,033 →
**141,847,593 bytes**. Both increased 41,560 bytes. Production remains unchanged.
No native/Web GPU-headroom benchmark was commissioned or claimed for this pass.

Human cargo fairness, physical gamepad, lower-end hardware and Safari/Firefox
remain untested. Continuously touching connected walls is still one conservative
episode and can forgive a secondary corner strike until clear separation.
Mixed/terrain contact is deliberately forgiven. Existing performance findings,
including the historical Market–Clinic +14.61% p95 result, remain historical.
The obsolete R7 repository freeze still fails on the untouched accepted source;
its result is retained, not relabeled as a new regression.

## Reproduce

`python3 tools/verify_cargo_v1_1.py` audits the accepted inventory without Git.
`python3 tools/launch.py --prepare-only` checks exact-engine import/parse.
Use the installed engine with `--path game --script res://tests/cargo_feel_matrix.gd`,
an **absolute** `--log-file`, then `-- --result <absolute-JSON-path>`.
`cargo_review_c1.gd` uses `--output <JSONL-path>` instead. `cargo_review_smoke.gd`
uses `--result` and `--cargo-log <JSONL-path>`; run it natively for the receipt image.
The unchanged courier/Run/paused scripts and Web export/smoke commands are retained.
Exact executed commands and raw results are in the adjacent evidence folder.

Stop here for cargo-feel review. No second contract, economy or progression.
