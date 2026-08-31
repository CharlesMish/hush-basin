# Final Recommendation — District Zero P1B Gameplay & Reward Proof

Status: `DESIGN LAB COMPLETE — AWAITING EXPLICIT P1B IMPLEMENTATION AUTHORITY`

Decision: `THREE_JOB_MOMENTUM_COURIER_VERTICAL_SLICE_V1`

This is not P1B PASS. It does not authorize product implementation, human
testing, a Human World Gate, a shop, trails, saving, Reputation, or a
post-Gate-B expansion. The R7 player remained byte-preserved throughout this
design lab.

## Recommendation in one paragraph

Build one small, session-only momentum-courier proof around the unchanged R7
toy: three open endpoint deliveries, one forgiving impact-based cargo model,
soft condition-and-pace scoring, a receipt that explains every Credit, and one
free choice between two genuinely desirable presentation-only paints. Keep
every route legal, every valid delivery successful, every genuine repeat fully
paid, and Continue spatially honest at the destination. Stop after the whole
three-job owner session. The purpose is to learn whether cargo makes the long
drifts more exciting rather than more anxious, and whether one visible reward
makes Charlie want another drive.

## What to build—and no more

### Gate A

Gate A contains:

- the unchanged R7 world, craft controller, camera, route data, map, and R7
  vehicle presentation;
- one new P1B sibling/root adapter;
- C01 Market Parcel only;
- the dispatch, neutral-release, active, delivery-settle, terminal, and Results
  states;
- the read-only cargo observer and pure peak-episode reducer;
- the soft condition/pace receipt;
- active reset/abort with zero award;
- Continue at DEP; and
- District Standard plus Trail Off only.

Gate A contains no paid or free cosmetic drawer. It answers whether parcel
stakes improve the toy at all. If they make the drive worse, stop there.

### Gate B

Only after Gate A owner review passes, Gate B adds:

- C02 Relay Window and C03 Clinic Glass without changing the family;
- a single clearly labeled session Credit balance;
- two native-qualified and owner-selected proof paints;
- one deferable C01 first-clear issue choosing exactly one of those paints;
- the free-only finish drawer; and
- the complete three-job calibration and hostile-strategy evidence.

Gate B has no paid shop, trail stock, save, Reputation, XP, level, modifier
stack, sealed route, mechanical upgrade, or automatic fourth job. Stop after
one complete owner session and return the evidence for a new decision.

## Exact player-facing loop

```text
FREE_ROAM
  -> BOARD_OPEN (paused)
  -> WAITING_FOR_NEUTRAL(next=ACTIVE)
  -> ACTIVE
  -> DELIVERY_SETTLE
  -> terminal commit
  -> RESULTS (paused, receipt first)
  -> WAITING_FOR_NEUTRAL(next=FREE_ROAM)
  -> FREE_ROAM at the exact reached destination
```

### 1. Find and open Dispatch

The game starts at MRK in Free Roam with District Standard and Trail Off. No
board auto-opens.

A fresh Interact edge may open the origin board only after revalidating:

- horizontal distance to the authored inner pad `<=8 m`;
- at least two support probes;
- finite, nonnegative measured support height; and
- tangential speed `<=4 m/s` as the initial seed.

The visible prompt is advisory. The press rechecks the authoritative state.
Opening the board never accepts a job.

### 2. Accept without leaking movement

A later fresh Accept edge freezes:

- contract definition and scoring hashes;
- origin and destination;
- literal `B` and `P` for that version;
- shared cargo profile;
- attempt key `(session_epoch, monotonic_sequence)`;
- reset, impact, and Hop counter baselines; and
- accepted origin as the recovery anchor.

The board then enters paused `WAITING_FOR_NEUTRAL`. Every movement and UI alias,
including analog strengths and reset, must remain neutral for two complete
always-process samples. Unpause is deferred. Only the next real physics step
enters Active and starts session-owned active time.

One physical edge may cross one boundary only. Held keyboard repeat, gamepad
Accept, movement axes, Transform, Hop, Reset, Interact, Pause, or Cancel cannot
leak through a modal.

### 3. Drive any route

Active HUD shows:

- destination and advisory map highlight;
- current cargo condition;
- active elapsed time;
- calm pace state; and
- one highest-priority event or destination message.

Pace copy is:

```text
FULL BONUS OPEN
BONUS EASING
BONUS ENDED · DELIVERY CONTINUES
```

Never show projected Credits, live grade, a red countdown, route compliance,
or efficiency. Crossing the final pace anchor ends only the pace component; it
never fails the job.

Pause freezes the craft, active clock, cargo observer, odometer, and delivery
settle. Resume passes through the same neutral gate and adds no wall-clock
catch-up.

### 4. Deliver by arriving under control

Inside the destination inner pad, the initial completion seeds are:

- horizontal distance `<=8 m`;
- support probes `>=2`;
- finite state;
- tangential speed `<=6 m/s`;
- no Hop start; and
- no positive cargo-loss observation;
- continuously for `0.50 s`.

The UI shows exactly one current reason in this order:

1. `REACH <DESTINATION>`;
2. `TOUCH DOWN`;
3. `CARGO MOVING — STABILIZE`;
4. `SLOW · <speed> / <ceiling> m/s`; or
5. `UNLOADING <percent>%`.

A zero-loss contact may appear in run details but does not damage cargo or
reset an otherwise valid settle. A positive-loss impact or Hop start resets
settle without an extra penalty. Pause preserves settle but cannot advance it.

### 5. Resolve exactly one terminal

Post-controller order per physics tick is:

1. observe actual reset/fall reset;
2. reduce fresh impact evidence;
3. validate destination conditions;
4. accumulate active time and settle; and
5. test success.

Reset wins a shared tick. One terminal latch is written before any summary,
award, navigation, or UI side effect.

Success atomically:

1. freezes the AttemptSummary;
2. evaluates receipt and exact grade once;
3. commits the award, clear fact, and possible entitlement once;
4. clears active cargo/navigation state;
5. pauses; and
6. renders immutable Results.

Active or settling reset atomically aborts, awards zero, clears the attempt,
and uses the accepted origin recovery anchor. Duplicate manual/fall signals
cannot create a second terminal. Reset is consumed in Board, Results, and
other P1B modals.

### 6. Show the receipt, then get out of the way

Results opens immediately with Continue focused:

```text
DELIVERED · GRADE A
92 CREDITS                         BALANCE AFTER DELIVERY 164

DELIVERY                                             +50
CONDITION 92% · 1 EPISODE                            +32
PACE 1:42 · REF 1:35                                 +10

NEW SESSION BEST RECEIPT
SESSION PROTOTYPE — CREDITS AND FINISHES RESET WHEN THE APP CLOSES

[ CONTINUE AT DEP ]       [ FINISHES ]
Run details >
```

Delivery, Condition, and Pace integers must sum exactly to the one committed
award. Route, actual distance, Hops, form duty, and detailed contacts remain in
collapsed run details because they do not pay.

Grade summarizes the same frozen condition and pace evidence. It cannot alter
money, stock, entitlement, or Session Best. It must be derived by the exact
evaluator; the UI cannot supply a label.

At most one event-bound card may announce the C01 free issue. It never steals
focus or auto-opens Finishes. Reopening Results cannot replay it.

`CONTINUE AT <DESTINATION>` exits through the neutral gate, preserves the
exact reached transform and velocity, makes the destination the new recovery
anchor, leaves the local board closed, and allocates no attempt. The next job
still requires a fresh Interact and Accept.

Do not implement `RESTART AT <ORIGIN>` unless a separate authority explicitly
allows the relocation and exact-engine proof establishes one reset event,
clean observer/counter baselines, cleared render history, a closed board, and
no award replay. Continue is enough for this proof.

## Contract catalog

In the Gate-B build all three definitions are available from boot at their
local origin. Gate A contains only C01. The chain is spatially continuous.

### C01 — Market Parcel

- Origin/destination: `MRK → DEP`.
- Advisory line: reverse `L1`, `129.429845 m`.
- Purpose: familiarization, technical Gate A, and one stable C01 free-paint
  entitlement after the first genuine delivery.

### C02 — Relay Window

- Origin/destination: `DEP → RLY`.
- Advisory line: reverse `L0` then `A1`, `394.186048 m`.
- Purpose: sustained long sweep with the same shared cargo.
- The inner path remains legal and unpenalized. “Window” is flavor, not an
  Express or timer mechanic.

### C03 — Clinic Glass

- Origin/destination: `RLY → CLN`.
- Advisory inner family: `L4 + L5 + L2`, `377.225159 m`.
- Declared legal outer family: `A2` then reverse `L3`, `514.603795 m`.
- Purpose: test whether one P/B version treats legitimate route families
  fairly.
- “Glass” is flavor, not a Fragile profile.

Every contract is:

```text
OPEN_ENDPOINT_V1
R7_COUNTER_EPOCH_FORGIVING_PEAK_EPISODE_V1
PAD_8M_SUPPORT_6MPS_SETTLE_050_V1
DZ_P1B_50_35_15_REFERENCE_RATIO_V1
K0 / NONE
```

## Cargo integrity

### Observation seam

R7 remains unchanged. A late-priority P1B observer reads the controller only
after its physics response. It samples severity only when reset-local
`impact_count` advances exactly one from the accepted baseline.

The observer must treat reset as a counter epoch. Sticky last-impact fields on
an unchanged tick are not new evidence. A missed/jumped count, invalid
severity, unexpected reset, or nonfinite sample invalidates the attempt rather
than guessing.

R7 support probes are pre-move and there is no authoritative landing event.
Support transitions, Hop, and landing therefore cannot damage cargo by
themselves. Ordinary rough travel likewise has no surcharge.

### Peak-episode reducer

Selected seed:

- `1000` integer integrity units;
- severity dead zone `0.20`;
- maximum one-episode loss `240` units / `24%`;
- response exponent `1.50`;
- quiet window `0.250 s` of Active time.

Within an episode, charge only the positive increase in the episode's mapped
peak. Sustained pressure cannot be billed once per frame. A lower contact
inside the same episode adds nothing. A later higher peak charges only its
increment.

Integrity is monotone and clamped to `[0,1000]`. A valid delivery at zero
integrity still completes and receives the delivery/pace portions. Cargo is a
quality stake, not a fail state.

### Mandatory separation proof

Before Gate A owner testing, exact-engine evidence must show:

- clean long drift: zero loss;
- Spread/Drive transformations: zero loss;
- supported Hop and ordinary landing: zero loss;
- ordinary braking: zero loss;
- ordinary rough-route travel: zero loss;
- brush/glance/strike: increasing, understandable loss;
- sustained wall pressure: one bounded episode, not repeated frame billing;
- 30/60/120 representation-equivalent streams: equal final units; and
- reset epochs: no stale event replay.

If clean play loses cargo or obvious hard impacts do not separate, stop and
repair only the new P1B observation/reducer layer. Do not retune R7 to make the
test pass without new authority.

## Pace, payout, grade, and Session Best

### Pace factor

Let `r = elapsed_active_time / P`. Use piecewise linear interpolation through:

```text
T = 1.00 at r <= 0.85
T = 0.75 at r = 1.00
T = 0.40 at r = 1.25
T = 0.00 at r >= 1.75
```

There is no timeout, late failure, or negative pace. Pause/modal time is
excluded. Delivery settle time is included.

### Award

For delivered attempts:

```text
A = round_half_up(B × (0.50 + 0.35 × I + 0.15 × T))
```

where `I = integrity_units / 1000`. Aborted or observer-invalid attempts award
zero.

Compute the three raw components, round the total once, floor each line, then
allocate remaining Credits by fractional remainder with stable tie order
Delivery → Condition → Pace. Never independently round three lines.

Only these fields enter money:

- frozen contract identity;
- literal base `B`;
- integer integrity units;
- integer active elapsed time;
- integer reference `P`; and
- scoring version.

Actual distance, authored distance, route, Flow, Hops, form duty, grade,
cosmetic, clear count, balance, retry count, and repeat count are excluded.

Every genuine repeat pays its full ordinary receipt. Do not add diminishing
returns, reset fees, cooldowns, dailies, or a best-receipt pool.

### Exact grade

From unrounded exact `I` and `T`:

```text
Q = 100 × (0.70 × I + 0.30 × T)

S: Q >= 94, I >= 0.95, r <= 0.95
A: Q >= 82, I >= 0.80
B: Q >= 65, I >= 0.55
C: Q >= 45
D: otherwise
```

Use integer, Decimal, or exact-rational arithmetic. The study's older binary
float implementation has known `Q=45/65/82` boundary errors. Derive grade in
the same canonical evaluator or verify its fingerprint before presentation.

Grade labels are `S EXCEPTIONAL`, `A STRONG`, `B SOLID`, `C COMPLETE`, and
`D ROUGH`. The terminal headline remains Delivered at every grade.

### Session Best

Call it `SESSION BEST RECEIPT`, not fastest time. Key by contract definition
and scoring hash. Compare completed ordinary receipts by:

1. higher ordinary Credits;
2. higher displayed integrity unit;
3. lower displayed elapsed tenth; and
4. earlier result on an exact tie.

Exclude aborts and first-clear grants. A retry cannot erase or roll back a
committed receipt or best.

## Authoring B and P

No C01/C02/C03 `B`, `P`, definition hash, or final catalog identity is frozen
by this lab.

For each contract:

1. run two familiarization deliveries;
2. capture five consecutive valid learned completions without cherry-picking;
3. require at least three of five at `>=90%` condition or repair cargo/route
   calibration first;
4. let `M` be median active time;
5. let valuation duration `V = round_half_up_0.1s(M)`;
6. let pace reference `P = ceil_0.1s(1.10 × M)`;
7. derive K0 base from one versioned global Credit rate `R` and measured loop
   allowance `H`; and
8. confirm with five fresh completions.

C03 additionally needs at least three fresh confirmations on each declared
route family. One P/B version must not force a legal family below B solely due
to elapsed time.

The provisional authoring relation is:

```text
B_raw = R × (V + H) / 60 seconds
B = round_half_up(B_raw)
```

All proof jobs are K0. `R=100 Credits/min` and `H=12 s` are stress seeds, not
authority. Measure complete Accept-to-next-fresh-Accept-ready cycles for
Continue and any separately authorized Restart. Target respectable max/min
rate spread `<=5%`; re-author at `5–15%`; stop above `15%`.

## Anti-exploit evidence

Pure arithmetic cannot prove wall riding suboptimal. The selected formula
allows one maximum-loss full-pace synthetic run to approach or slightly beat
learned-clean Credits/minute in medium/long illustrative jobs.

For every implemented job, preserve consecutive exact-engine captures of:

- respectable learned-clean play;
- fastest intentional wall-pressure line;
- intentional low-integrity direct rush;
- pristine long-drift line; and
- every declared legal route family.

Also run ten complete shortest-job repeat cycles including Results, neutral
release, and next fresh Accept eligibility.

Hard stop if:

- any hostile median Credits/minute exceeds its respectable comparator;
- shortest-repeat full-cycle rate exceeds the cross-job target band;
- C03's legal outer route is forced below B solely by time;
- wall pressure becomes the recommended economic line;
- early abort/retry pressure makes players abandon most damaged runs; or
- a pristine long drift's B grade reads as failure despite the healthy award.

Do not fix these by raising prices, adding repeat tax, paying distance, or
changing R7 movement. Recalibrate/version the P1B cargo or economy evidence as
authorized.

## Progression and rewards

### Gate-B profile

Gate B has:

- District Standard, always free;
- Trail Off, always free;
- one session Credit balance;
- one C01 first-clear entitlement;
- exactly two native-qualified proof paint choices; and
- one free claim that may be deferred while keeping Standard.

Every relevant surface repeats:

```text
SESSION PROTOTYPE — CREDITS AND FINISHES RESET WHEN THE APP CLOSES
```

Until a later shop study exists, balance is labeled:

```text
SESSION CREDITS · NO SHOP IN THIS PROOF
```

Claiming a paint is atomic, costs zero, and may equip it. Keeping Standard does
not consume the entitlement. Exact replay is a no-op; altered reuse is a
conflict. A new app session resets balance, ledgers, clear facts, pending issue,
nondefault ownership/equipment, cards, and Session Best together.

There is no paid command, price, locked silhouette, rarity, rotating stock,
sale, countdown, Reputation, permanent-ownership claim, or future-content
tease in Gate B.

### Why no shop yet

The one free issue proves the reward bridge without asking for grind. Session
Credits prove that the receipt creates legible value. A paid shop before
persistence or calibrated bases would make session loss and provisional
prices feel misleading.

The researched exact-clear `80/160` shelf remains a possible later experiment,
not part of this slice. If Gate B says the missing thing is a use for Credits,
and not saving or a new drive, a separate authority may expose one unchosen
paint and one trail. If Charlie asks for persistence first, save outranks more
stock.

## Cosmetic recommendation

### Research shortlist

Strongest desk paints:

1. Orchid Static;
2. Saltglass; and
3. Ember Relay.

Reserves: Vesper Ceramic; Moss Circuit for Ember's preregistered warm-cue
failure.

Strongest desk trails:

1. Twin Vector;
2. Courier Pulse; and
3. Comet Ledger.

Reserves: One Wake; Tide Script. A shared history/occlusion/reset failure blocks
the whole ribbon architecture.

### Gate-B paint selection

`Orchid Static + Saltglass` is a capture seed, not an authorized pair.

1. Native-gate all three desk finalists independently.
2. Promote a reserve only for its named failure class and rerun all gates.
3. Show each surviving pair twice with left/right order reversed using unnamed,
   identical Spread → midpoint → Drive previews.
4. Require stable preference plus “worth choosing over District Standard” for
   each candidate.
5. Require the pair to be distinguishable from each other and Standard in a
   brief matched preview.
6. Exactly two stable qualifiers freeze the pair. Three require Charlie's
   explicit ranking. Cycles/order effects/fewer than two stop for review.

Native paint gates require exact engine, fourteen matched `1280×720` captures,
four readable body masses, preserved reserved materials and functional cues,
initialization-only allocation, and cosmetic-on/off movement C1 maximum delta
`0.0`.

### No trail in Gate B

Gate B ships Trail Off only. Twin Vector R1 remains the lead research trail,
with two bounded actual-path rails, reduced motion, wall occlusion, reset and
relocation clears, no gameplay access, and finite geometry/history.

A future trail needs matched straight/drift/brake/Hop/landing/wall/pause/reset/
relocation/reduced-motion/surface-spray evidence, ten-minute no-growth soak,
zero post-warm-up allocation, movement delta `0.0`, and owner confirmation that
it celebrates drift rather than suggesting a route.

## Implementation sequence after new authority

### 0. Authority and preservation preflight

- Create a fresh P1B successor/output root.
- Require exact Godot `4.7.1.stable.official.a13da4feb`.
- Verify the complete R7 byte inventory.
- Run untouched R7 static verifier, runtime suite, and C1.
- Stop on any mismatch. Do not install/substitute an engine or repair R7 inside
  P1B authority.

### 1. Empty P1B shell

- Add one small sibling/root scene around existing R7 nodes.
- Disable diagnostic menu/spawn mutation in the P1B entry point.
- Own pause/modal routing explicitly.
- Prove idle shell and modal-open movement delta `0.0` before gameplay.

### 2. Pure core

Implement small typed/versioned reducers, not a quest framework:

- exact three-record catalog;
- state/transition reducer;
- cargo observer adapter and peak-episode reducer;
- exact payout, grade, line-reconciliation, and Session Best evaluator;
- attempt/award/clear/entitlement/profile ledgers; and
- immutable result view model.

Run all lab boundary/hostile tests before world integration. Replace the known
float grade seam with exact arithmetic and bind grade to receipt evidence.

### 3. Input and spatial seam

- Revalidate origin eligibility on fresh Interact.
- Implement paused Board and two-frame neutral barrier.
- Own active time rather than borrowing telemetry tick.
- Add destination marker/map cleanup and settle feedback.
- Prove keyboard and gamepad held/stale/simultaneous input cases.

### 4. C01 technical Gate A

- Integrate post-controller impact observation.
- Add abort, one terminal, receipt, and Continue.
- Run drift/Hop/rough/brush/glance/strike/wall/landing evidence.
- Run reset races, pause, queue overflow, duplicate, reopen, and invalid-observer
  tests.
- Then conduct owner Gate A and stop if cargo stakes weaken the toy.

### 5. Recovery-anchor proof

- Set accepted origin before an active attempt.
- Set reached destination after Continue without moving the craft.
- Prove exactly one reset event, no movement-source change, clean counter
  baselines, and correct C02/C03 recovery.
- If unproved, stop after C01. Do not let later resets silently return to MRK.

### 6. Reward proof

- Qualify at least two paints natively.
- Use an explicit 56-mesh render-role registry and cached materials.
- Add the free C01 issue/drawer.
- Preview with the render-only rig or omit preview; do not instantiate a
  controller/collider/input/route/cargo/payout scene.
- Prove cues, roles, session reset, allocation, and movement delta.

### 7. Gate-B breadth and calibration

- Add C02/C03 unchanged.
- Collect consecutive owner runs and version final P/B/remaining seeds.
- Run C03 family fairness and all hostile/cadence strategies.
- Package a clean fresh session starting at MRK.

### 8. Whole-chain Gate B

- Conduct one owner session plus deliberate alternative/reset/retry probes.
- Preserve receipts, answers, exact-engine evidence, and blockers.
- Return and stop. A PASS may nominate one next study; it does not authorize it.

## Required test layers

### Pure deterministic

- All `844/844` current lab checks must remain green.
- Add product tests for exact contract/terms/catalog identities.
- Test every state transition, illegal transition, neutral gate, and terminal
  precedence.
- Test impact counter epoch, peak episodes, integer quantization, queue jump,
  invalid input, and 30/60/120 stream equivalence.
- Test exact payout at every pace anchor and integrity boundary.
- Test grade thresholds `45/65/82/94`, S/A/B gates, and known float-seam points.
- Test receipt lines, one-award ledger, duplicate/no-op/conflict, overflow, and
  session reset.
- Test route/distance/Flow/Hop/form/grade/cosmetic/repeat metamorphic neutrality.
- Test entitlement deferral/claim/replay/conflict and no-debit behavior.

### Exact-engine integration

- Idle/modal/cosmetic movement C1 max delta `0.0`.
- Keyboard/gamepad held inputs never cross two boundaries.
- Pause produces no time/settle/observer/odometer change or resume spike.
- Reset beats success on the same tick and produces one terminal/zero award.
- Airborne, outer-blend, or fast fly-through cannot deliver.
- Continue preserves exact reached transform/velocity and leaves board closed.
- Recovery reset uses the accepted origin for every contract.
- Cosmetic registry covers all 56 meshes and never touches reserved materials.

### Native calibration and owner evidence

- Five consecutive learned runs after two warmups per contract.
- Five fresh confirmations per contract.
- Three or more C03 confirmations on each legal family.
- Ten full shortest-job repeat cycles.
- Learned-clean, wall-pressure, direct-rush, and pristine-long-drift captures.
- Paint native/cue/owner matrix.
- Owner Gate A and Gate B questions below.

## Hard blockers

Stop rather than broadening or tuning around any of these:

- no explicit P1B implementation authority;
- wrong Godot, changed R7 bytes, nonzero R7/C1/cosmetic movement delta;
- reachable diagnostic spawn/teleport mutation;
- a held input or one edge crossing multiple states;
- observer counter miss/jump/stale replay or clean play cargo loss;
- hard impacts failing to separate or sustained contact double billing;
- unproved accepted-origin recovery before C02/C03;
- airborne/fast/outer-blend delivery or persistently fussy settle;
- duplicate/reopen/reset race changing balance, entitlement, or best twice;
- wall-pressure/direct-rush median rate beating respectable play;
- shortest job dominating the measured full cycle;
- respectable cross-job spread above `15%`;
- legal C03 alternative forced below B by time alone;
- proof paint cue/readability/reserved-material/allocation failure;
- session-loss disclosure surprising Charlie;
- Credits without a shop feeling manipulative rather than informative;
- reward UI delaying the desire to Continue;
- clean long drift becoming anxious or clearly economically wrong; or
- the three-job chain producing no desire for another drive.

## Provisional tuning envelope

Change one axis at a time and version every tested build.

| Area | Seed | Bounded comparison/range |
| --- | ---: | ---: |
| Cargo dead zone | `0.20` | `0.18–0.23` |
| Cargo max episode loss | `24%` | `20–28%` |
| Cargo exponent | `1.50` | `1.35–1.70` |
| Cargo quiet window | `0.250 s` | `0.20–0.30 s` |
| Pickup speed | `4 m/s` | keep unless owner friction proves need |
| Delivery speed | `6 m/s` | owner compare `4/6/8 m/s` |
| Delivery settle | `0.50 s` | owner compare `0.35/0.50/0.60 s` |
| Pace anchors | `.85/1/1.25/1.75` | freeze during first cargo study |
| Payout shares | `50/35/15` | do not co-tune with cargo |
| Reference | `ceil_0.1s(1.10M)` | verify alternative routes |
| Credit rate | `100/min` | provisional global scale |
| Cadence allowance | `12 s` | stress `4/8/12/16/20 s`; replace with measured |
| Respectable rate spread | `<=5%` | re-author `5–15%`; stop `>15%` |
| Conditional paid paint | `80` | not Gate-B authority |
| Conditional trail | `160` | not Gate-B authority |

Do not change payout shares and cargo response simultaneously. Do not use
price inflation or repeat friction to conceal a rate problem.

## Rejected and deferred alternatives

Rejected for this proof:

- movement, terrain, camera, world, or vehicle retuning;
- raw speed, brake, handling, cargo-protection, or integrity upgrades;
- physical cargo or landing surcharge;
- route-specific damage or cargo rigid body;
- actual-distance, route-efficiency, cleanliness, Flow, drift, Hop, or grade
  money;
- hard timer/failure;
- sealed route, Express, Fragile, multistop, SOUTH handoff, modifier stack, or
  K2;
- automatic next board, pickup dwell, or hidden retry teleport;
- Reputation, XP, level, random/rotating/daily/premium economy;
- fourth Gate-B contract or C04–C07 circuit; and
- procedural contract framework.

Deferred behind Gate B and a new decision:

- one of the mutually exclusive QRY/SOUTH/WORKS studies;
- any trail implementation;
- paid clear-set shelf and `80/160` prices;
- durable save;
- Results restart relocation;
- route sealing/direction adapter;
- K1 valuation; and
- any broader progression.

## Owner playtest questions

Ask these after the technical evidence is green. Do not answer them with
automation.

1. Did carrying the parcel make the long drifts feel more exciting and
   consequential, or more cautious and anxious?
2. Without instructions, was it obvious how to accept a job, find the
   destination, and finish unloading? When unloading stopped, did you know why?
3. Which contact changed cargo condition? Did any clean drift, Hop, landing,
   braking, or rough travel feel falsely punished?
4. Did pace invite a better run while still making a slow finish feel
   worthwhile? Did either C03 route feel unfairly penalized?
5. After two Results screens, what do Delivery, Condition, Pace, and Grade each
   mean to you?
6. Did active reset/abort feel clear and fair enough to try again? Did Continue
   preserve the journey naturally?
7. Was the first finish visibly worth earning in both Spread and Drive, and was
   the session-only warning unmistakable?
8. At CLN, what did you genuinely want next: another drive, a retry, a new kind
   of job, a cosmetic use for Credits, saving, or nothing?

## Evidence and final boundary

The lab's eight iteration suites plus foundation report `844/844` pure checks.
They establish arithmetic, identity, reducer, graph, scope, hostile-input, and
evidence-boundary properties. They do not establish Godot execution, physics
integration, performance, balance, aesthetic desirability, comfort, or human
feel.

No R7 or product file was changed. No Godot runtime or Human World Gate ran in
iteration 08. P1B product implementation remains `NOT STARTED` and P1B PASS is
false.

The next legitimate step is a fresh, explicit P1B implementation authority
that accepts this bounded Gate-A/Gate-B scope and preserves the stop gates. It
is not another overnight design iteration.
