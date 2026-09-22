# Courier alpha loop v1 — owner-review record

2026-09-15. Local candidate only; production and remote main were not changed.
Accepted baseline: Courier v1.1 commit `55eff6f4573f53a5a54c7e97d4c9d327b49b9d64`.
Engine: `4.7.1.stable.official.a13da4feb`, native Metal4 Forward+, Apple M5,
1280 × 720. Web uses the established single-thread Compatibility export.

## What is playable

Market Dispatch offers three permanently replayable session contracts: Depot
Style (100 + 25), Relay Express (150 + 40), and Works Care (120 + 35). Each has
exactly one optional objective; no hidden reward terms. The 400-Credit cargo
liner reduces accepted cargo bills by 25%, with raw evidence preserved. No
handling, cargo attribution/grouping/curve or BRRR changes were made.

Continue leaves the craft at its reached destination. A small map cue and a
warm crown on the existing Market Hall roof help the normal drive home. The
crown uses 37 native parts in three material batches; no collision or lights.
Targets and pricing are justified in `ALPHA_TARGETS.md`; play instructions and
all eight human review questions are in `START_HERE_ALPHA_LOOP.md`.

## Preservation and native verification

The baseline was freshly prepared and its movement/cargo fixtures run before
implementation. `tools/verify_alpha_loop.py` audits all 540 baseline files. Only
four existing files have narrowly bound integration changes: main-scene entry,
the review wrapper's configurable scene, Web diagnostic selector, and Web
resource inclusion for the retained review instrumentation. Historical source,
authorities and manifests remain available and unchanged otherwise.

| Check | Observed result |
|---|---|
| Accepted-source inventory | PASS, 540 files / four explicit exceptions |
| Movement fixture | Exact 1,260-tick parity, unprotected and liner-equipped |
| C1 trace SHA-256, all three versions | `29f1049f8e16ec65d288407c35e6ccae46e87c711bb6b54b134e6158c68b9443` |
| Cargo matrix | 92/92 unprotected; 92/92 protected |
| Raw controller contact records | All 3,440 identical to baseline in each candidate mode |
| Accepted unprotected cargo loss / episode counts | All 50 cases unchanged |
| Native alpha loop | 76/76, final repair-round run |
| Quarto vehicle | 39/39 |
| Run v0 | 54/54 |
| Run paused retry | 15/15 |
| World / entrances | 35/35, including all 12 traversals |
| Weather regression | 30/30 headless; alpha native pause/reset integration also passes |
| Native runtime geometry comparison | 9/9: all 162 collision shapes identical; terrain vertices, normals and indices identical |

The alpha suite drives six complete delivery approaches with ordinary inputs:
Depot direct/road, Relay spine/west sweep, Works Way/northern alternative. It
also drives back from Depot and reopens Market Dispatch without relocation.
Separate explicitly synthetic fixtures test all three missed objectives with
zero condition, fixed base payouts, objective awards, repeat/idempotent receipt
commit, paused retry/fall/diagnostic cancellation, purchase-once, protected real
wall contact and raw → reduction → committed diagnostics. Synthetic cases are
not presented as human drives. Both unprotected and protected cargo can reach
zero and still deliver. Session close resets the balance and purchase.

## Native cost and Web size

Adjacent comparisons ran in A1/B1 then B2/A2 order, with the review overlay
hidden and no other automated UI workload. Each measures eight seconds after
two seconds of warmup, active courier in both builds. All raw frame times and
workload results are retained. This is SceneTree process-frame cadence, not a
GPU headroom measurement or a claim about every district.

| Pair / workload | Accepted p95 ms | Alpha p95 ms | Change |
|---|---:|---:|---:|
| A1/B1 static | 11.039 | 10.094 | −8.56% |
| A1/B1 moving | 14.751 | 14.754 | +0.02% |
| B2/A2 static | 10.160 | 10.006 | −1.52% |
| B2/A2 moving | 14.754 | 14.492 | −1.78% |

All four comparisons meet a +10% review target; unfavorable samples were not
discarded. The older Quiet Surfaces Market–Clinic +14.61% finding remains a
historical failure, not retroactively a pass from this narrower workload.

| Full playable Web export | Accepted bytes | Alpha bytes | Change |
|---|---:|---:|---:|
| PCK | 101,999,860 | 102,208,144 | +208,284 (+0.204%) |
| Complete export | 141,847,593 | 142,055,877 | +208,284 (+0.147%) |

Repaired Web exports passed in local Chromium 151.0.7922.34: alpha 76/76,
including all six delivery routes and the drive home, and separate Run smoke
13/13. The full playable entry passed startup, keyboard Dispatch/Relay
acceptance, drive/steer, pause/resume and F2/F3 smoke at 1280 × 720, with no
console/page/script errors. Initial ready time was 3.782 s. Ten-second browser
rAF samples measured active-idle p95 18.60 ms and drive/steer p95 18.70 ms
(moving maximum 66.70 ms). These unpaired browser samples describe observed
cadence only; they do not establish Web performance parity or GPU headroom.

## Repairs, retained failures and limits

One bounded repair round followed complete verification. The first Web export
omitted the review wrapper because its historical resource filter excluded all
review files. The filter now includes the cargo/alpha runtime wrappers while
still excluding the historical Quarto comparison assets. No hosting redesign
or deployment occurred.

An intermediate native run passed 75/76: the test driver held throttle after
another window stole focus, and the unchanged controller correctly required
neutral input. The diagnostic driver now releases controls when it observes
that existing lock; it never writes the lock or movement. Final native passed
76/76. The initial geometry comparator also reported false differences from
auto-generated node IDs and Dummy-renderer MultiMesh readback. Stable hierarchy
IDs and native GPU readback resolved those diagnostic issues; collision did
not change. The initial capture wait hung and was terminated; fresh captures
use explicit render synchronization. Failed logs remain in the evidence.

The first route study's east Works approach stalled on existing geometry near
(166, 4); its failed 120-second trace is retained. This is a limitation of the
conservative driver, not a reason to change the world or invalidate that route.
The northern alternate completed. No new reproducible cargo defect appeared.

Eight matched native before/after views cover all six destinations and both
sweeps, looking toward Market from ordinary camera height. The crown is useful
across several districts but is hidden by buildings on the east sweep and can
leave the frame when close to Market. It does not guarantee omnipresent
visibility. Three sparse 5-fps clips show delivery, normal return and the Relay
approach; they do not measure real-time smoothness.

Human job differentiation, bonus anxiety, return-trip chore, desire for more
content, comfort and physical gamepad feel remain Charlie's gates. No claims
are made for other hardware/browsers or deterministic physics across platforms.

## Reproduction and evidence

Sibling `../evidence/ALPHA_LOOP_REVIEW.html` is the visual owner packet.
`DELIVERY.json` binds the final source ZIP/commit and Web input hashes. Exact
command arrays, exits and timings are retained in `baseline-commands.json`,
`preservation-commands.json`, `regression-commands.json`,
`native-r1-commands.json`, `browser-r1-commands.json` and the three
`web-r1-*/build.json` files. `performance.json` retains every comparison;
`cargo-parity.json`, `geometry-native.json` and `alpha-r1-native.json` hold the
individual assertions. `package-check.json` records clean ZIP verification.

For a quick source check: `python3 tools/verify_alpha_loop.py`. For play,
double-click `PLAY_COURIER_ALPHA.command`; it resolves the pinned installed
engine, prepares resources and records F2/F3 receipts locally. Run v0 remains
available separately through its existing launcher.
