# Relay consequence v0.1 — verification

Engine: `4.7.1.stable.official.a13da4feb`, native Forward+ at 1280×720.
Baseline: played `66b4c228264d6c2966a8af68243898fc21c6573d`.
Runtime candidate: `6f6e823` plus documentation-only handoff records.

| Lane | Observed result |
|---|---|
| Source authority | All 696 baseline inventory entries and delivered ZIP SHA verified; played log identifies Mastery Alpha v1. |
| Preservation | 412/412: cargo 92 + protected 92, vehicle 39, Run 54, paused retry 15, world 35 including 12 entrances, weather 30, drift predicates 42, trail 13. |
| Movement | Ordinary and protected traces exactly match all 1,260 accepted ticks. SHA256 `29f1049f8e16ec65d288407c35e6ccae46e87c711bb6b54b134e6158c68b9443`. |
| Frozen source | 69 gameplay/world/cargo/weather/BRRR/camera/vehicle files unchanged. Of 696 existing files, only project identity, trail presentation and export diagnostic selection changed. New project code is additive. |
| Native integration | 44/44 in Forward+; three normal-input legs, exact Continue pose, zero-condition deliveries, no double payout, paused retry, liner purchase and bounded reset behavior. |
| Native process restarts | 63 checks across eight separate processes: reset, real leg 1, reopen intermediate state, real leg 2, reopen active state, outbound, reset, reopen fresh. |
| Neutral control | 44/44 integrated checks; same legs/payouts, no annex geometry. |
| Store logic | 56/56 across nine processes: strict two-flag validation, order, unrelated/repeated/canceled jobs, write failure, corruption and reset. |
| Catalog / precision | 58/58; four ordinary challenges unchanged, no basic/project mastery, exact additive rewards, neutral mechanical parity, 2,001 samples each at time/duration display boundaries. |
| Annex geometry | 31/31: finite, positive scales, occupied-footprint bounds, no physics/lights/particles, native materials, bounded batches and repeatable stage visibility. |
| Reset dialog | 10/10 real scene/modal input checks: E cannot accept through modal, Esc cancels dialog, Enter confirms reset without payment/parcel/movement. |
| Web project | 107/107 across nine browser sessions, including actual browser close/reopen with one isolated profile and the same origin; final full integration 44/44. No script/page errors. |
| Playable Web / Run | Real browser launch, three-card board, reset modal, input, pause and F2/F3 smoke pass at 1280×720; retained Run Web lane passes 13/13. No script/page errors. |

The three normal-input native legs delivered at 100% condition: stock 11.067 s,
receiver 19.867 s, return pouch 22.000 s. These are reproducible route examples,
not challenge targets. Endpoint placement cases are explicitly synthetic in the
logs; they isolate zero cargo, terminal/retry and once-only receipt behavior.

Web persistence uses the engine's existing IndexedDB-backed local filesystem.
The browser restart test allowed 2.2 seconds of ordinary main-loop synchronization
before closing. Instant tab/process kill during asynchronous storage synchronization
was not validated. Clearing browser storage removes the project. No cloud save.

Native AB/BA comparison retains every workload and raw frame sample. Mean p95
movement: static **+0.119%**, moving **−0.523%**; worst individual **+0.191%**.
All individual p95 values were 16.78–16.94 ms. These 8-second, 60 Hz frame-pacing
samples do not measure spare GPU headroom. The first baseline preparation
overlapped the tail of headless checks/export; the reverse pair was quiet.
No concurrent browser workload or active review UI. Nothing was discarded.

Playable Web PCK: **102,750,828 → 102,963,448 bytes** (+212,620; +0.207%).
Complete export: **142,598,557 → 142,811,183 bytes** (+212,626; +0.149%).
Pinned template/WASM and existing hosting architecture remain unchanged.
Export source hashes match the committed runtime source, even where the export
record's HEAD predates the integration commit.

Retained evidence includes fresh matched Relay stages from four approach angles,
six native flow captures, and matched 25.5-second before/after trail clips.
Trail route JSON and receipts match exactly between appearances. The historical
Depot Style overlay in those visual-comparison clips is not the current basic
Depot definition.

Limits: east-sweep arrivals can face away from Relay's mast. Natural noticeability,
motivation, memory, comfort and trail preference remain human gates. New equipment
uses the particle-only weather mask and a bounded heightfield refresh; preserved
weather contact tests pass, but individual rain drops striking the new small
receiver surfaces were not quantitatively tracked. There is no claim that the
project hypothesis has succeeded.

Preflight history is retained: one sandboxed startup could not create its review
log in the new user directory and exited before gameplay. The authorized run with
an explicit evidence log passed. Headless macOS CA-store warnings were unrelated
to these offline checks. No gameplay repair was needed after complete verification.

The adjacent evidence directory contains commands/results for every lane. No
historical validator was rewritten to relabel intentionally changed basic-job,
cosmetic-gate or presentation expectations. No main update, push or deployment.
