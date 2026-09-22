# Session mastery and one reward — isolated lane proposal

Baseline: Mechanics Range V1.1, `39d098c52b028db3d2b2ca0c41c7c71de89b8791`.
This is a proposal for lead review, not an independent playable successor.
The existing session ledger, contracts, cargo, trail, craft and world are unchanged.

## Human evidence retained

Charlie says the five-job version is fun; Thread and Haul make previously unused
geography valuable. The board is becoming busy, and he wants variety without a
large quest-center menu. He distinguishes enjoyable straight Drive traversal
from genuine drift skill. He wants repeated work to feel cumulative. These are
requests for the next experiment, not evidence against the core vehicle.

## Recommended small loop

Keep all five ordinary jobs available immediately. A completed delivery records
that the work was done. Its first successful optional objective records one
mastery stamp for that contract. A replay still pays the full authored base and
optional bonus but cannot add another stamp for the same contract.

One line-control mastery (Depot or Relay) plus one care/geographic mastery (Works,
Thread or Haul) makes **Lantern amber trail** available for **200 Credits**. This
asks for contrasting work rather than farming one easy job twice. It does not
claim every member of a family has equal difficulty. In particular, Care remains
an accessible way into the reward. The challenge audit determines what each job
actually asks; progression never changes its predicate.

The appearance is the only new purchasable reward. The accepted 400-Credit cargo
liner remains independent. Owning amber allows a free choice between the current
teal trail and amber at Dispatch. It changes RGB only: same qualification,
geometry, width, alpha, lifetime, sampling and streak response. Standard teal
remains fully functional whether or not anything is mastered or purchased.

Price rationale uses observed/authored V1.1 receipts: Depot mastery pays 140 and
Thread mastery pays 400, totaling 540. The player can buy amber immediately or
buy the existing 400-Credit liner first, leaving 140. One ordinary base-only Depot
delivery pays 80, enough to buy amber afterward with 20 remaining. This gives a
small visible choice and perhaps one more run, rather than an extended grind.
Haul or Relay earnings can reach it sooner; there is no diminishing return,
randomness or secret payout multiplier. This is provisional session economy.

All state resets on app closure. A 20–30 minute owner review can evaluate the
sequence honestly in one session. Longer-term return motivation cannot be judged
without persistence; no save/account architecture was added to pretend otherwise.

## State model and API

`mastery_state.gd` observes only final receipt dictionaries. It does not inspect
the craft, raw telemetry or score. A receipt must have a known job ID, positive
integer attempt ID and Boolean delivered/objective fields. Attempt IDs are
deduplicated. A failed/canceled attempt can never become a stamp afterward.

| Event | Credits | Delivery record | Mastery/reward |
|---|---|---|---|
| Successful base-only delivery | Existing base | Increment once | No stamp |
| First successful optional objective | Existing base + bonus | Increment once | One stamp; unlock if both families represented |
| Valid repeat success | Same authored payout | Increment once | No duplicate stamp/unlock |
| Retry/cancel/non-delivery | Existing zero payout | None | None |
| Reopen/re-settle same receipt | None again | None again | None again |
| Buy amber, unlocked + sufficient balance | Exactly -200 | Unchanged | Own/equip amber once |
| Buy while locked/poor/already owned | No charge | Unchanged | No change |
| Equip owned appearance | No charge | Unchanged | Appearance only |

`MasteryState.status(job_id)` returns `available`, `lock_reason`, `delivered`,
`mastered`, `deliveries`. Every known ordinary job is available.
`mastery_count()` returns 0–5. `reward_unlocked()` implements the two-family rule.
`reward_progress()` is one short explanatory line. `observe_receipt(receipt)`
returns `accepted`, `first_mastery`, `mastery_count`, `unlocks` (short names).
`snapshot()` returns a detached diagnostic copy.

`mastery_session.gd` extends the unchanged AlphaSession. `settle()` calls its
parent exactly once under the parent's existing guard and returns the same
immutable receipt; mastery evidence is kept alongside it. `mastery_receipt(id)`
returns the detached progression event for that accepted parcel. Existing HUD
receipt fields remain valid. The adapter exposes `mastery`, `buy_trail()` and
`set_trail_style("standard" | "lantern_amber")`. Only `buy_trail()` debits the
new fixed cost; equip is free. Existing `buy_liner()` is inherited unchanged.

Lead integration should replace the session preload with this subclass, then
bind `session.mastery` and `session.mastery_receipt(attempt_id)` to the small HUD
adapter. Only offer purchases/equip while Dispatch is open. A single palette
function call can select the RGB role from `session.mastery.trail_style`; the
trail must continue owning the existing alpha/geometry/qualification behavior.

## Reward appearance study

The palette helper changes teal `69c9b9` / highlight `d7c18d` to amber `d5b579` /
highlight `d5b986`, using the same slip × 0.35 interpolation. Across 101 slip
values the maximum relative linear-luminance difference is **0.6932%**. Alpha
is unchanged and standard RGB is exact. This is a code/palette check, not proof
that amber reads well against every district; matched native moving captures
must decide adoption. No rig, container or paint implementation was attempted.

## Rejected or deferred

- Locking Thread or Haul: these are already accepted strengths and geographic
  exploration should remain immediate. Roads and deliveries never lock.
- Count-only `2 → tier`, `4 → Quarry`: arbitrary thresholds do not establish
  readiness and would reopen access the owner already values.
- A sixth job or renamed duplicate: additional catalog size would hide the
  motivation question and worsen the board issue.
- An untested harder work tier: the challenge lane has not established one
  distinct and fair enough to earn that label. No dormant entitlement framework
  was left in runtime. Mastery → one reward is the smaller honest experiment.
- Mastery payout multiplier, XP, repeat penalties, RNG: opaque incentives would
  obscure the authored optional challenge and existing additive receipts.
- Paint/container/catalog: more authoring and UI than needed to test one reward.
- Saving: unnecessary for this bounded session test; longer-term motivation
  remains an explicit future boundary.

## Lane verification

Godot `4.7.1.stable.official.a13da4feb` (unchanged installed executable).
Accepted `verify_range_v11.py` inventory passed before and after (612 files,
only its six historical permitted edits). Pure `mastery_progression_probe.gd`:
**44/44 PASS**. The probe covers delivery/mastery separation, zero-cargo Style,
cancellation, duplicate settlement/receipt observation, valid repeat payout,
family diversity, unknown/malformed input, event-copy isolation, once-only
purchases, no debt, free equip, existing liner independence, fresh-session reset,
all five original ledger receipts/value equality and palette constraints.

Exact command, with absolute lab/evidence paths:

```text
/Applications/Godot.app/Contents/MacOS/Godot --headless --path LAB/game --log-file LAB/lane/evidence/pure-test.log --script res://tests/mastery_progression_probe.gd -- --result LAB/lane/evidence/pure-test.json
```

The engine emitted its host CA-certificate lookup warning; there were no script
or test failures. Headless import completed and generated the new script UIDs;
its editor-settings save reported a sandbox write denial outside the lab.
No editor-local file is part of the candidate. This pure lab does not certify native visual fit, movement
parity, full-loop/UI behavior or Web operation. Those remain integration checks.
