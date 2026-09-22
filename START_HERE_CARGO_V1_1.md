# Cargo feel v1.1 — small owner candidate

Double-click **PLAY_CARGO_FEEL_V1_1.command**. This opens the same Market → Depot
job with a disposable recording panel. The normal courier launcher also uses
the corrected cargo grouping, but does not load the review instrumentation.

Use E / Enter to open Dispatch and accept. Movement, transformation, Hop,
camera, world, weather, Run and BRRR are unchanged. Poor/zero cargo still delivers.
There is no new contract, economy, grade, progression or deployment.

## What changed

The loss curve is unchanged. A contact episode now charges its **first fresh,
unambiguous impact**, including an entry too weak to cost anything. Continuing
pressure cannot inflate that bill. A new hit is recognized after the existing
quarter-second quiet interval, or a quarter-metre outward separation while no
wall contact is present. Contact jitter should not become repeated billing.

## Five-minute comparison

1. Collect the parcel. At one wall, try a genuinely slow approach, then a faster
   head-on approach with the same form. Return to Market for fresh cargo when
   comparing losses; remaining condition caps the amount that can be lost.
2. Compare a fast glance with a slower head-on hit. Read **incoming**, **closing**
   and **after** speed separately. A faster glance can correctly cost less.
3. Push against the wall after contact. The charge should stop growing.
4. Pull clearly away and hit it again. The receipt should show a new episode.
5. Drift, transform, brake and Hop normally, then finish the delivery.

**F2** hides/shows the recording panel. **F3** bookmarks a surprising contact.
Recording continues with the panel hidden. Each new parcel clears the old receipt.

The top panel reports the last charged event, not current driving speed. It
shows the incremental loss and total loss separately. “Incoming” is the actual
world-space velocity passed into the unchanged controller impact response.
“Closing” is its component toward the contact normal; “after” is the controller's
post-response speed. Native collision-resolved movement is also recorded in
the log, separately from these script-owned velocity values.

Receipts are saved in **review_logs/cargo-*.jsonl** beside this source. The
launcher prints the exact path. F3 adds a bookmark and flushes it immediately;
normal recording flushes every quarter second and on a normal close. These are
local review logs, not progression saves or analytics.

Please bring back the JSONL for a surprising hit and say whether you were slow
**before** contact or appeared stopped **after** it. The original unrecorded
near-stop Spread result cannot be identified retrospectively with confidence.

See **CARGO_DIAGNOSIS.md**, **CARGO_CASE_MATRIX.md** and **CARGO_V1_1_RESULTS.md**
for the observed evidence. The premise is already accepted; this playtest is
about whether the parcel now reacts legibly and fairly.
