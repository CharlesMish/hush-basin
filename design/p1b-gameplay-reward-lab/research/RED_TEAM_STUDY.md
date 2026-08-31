# District Zero P1B — Red-Team Study

Status: `DESIGN REVIEW — NO R7 SOURCE CHANGE`

Read-only baseline:
`District-Zero-P1A-v1.2.8-Vehicle-Integration-R7-Run-1/District-Zero-P1A-v1.2.8-Vehicle-R7-Player`

This review deliberately tries to break the current gameplay, reward, and
cosmetic proposals before they become implementation commitments. It treats
the studies as hypotheses, not authority.

## Executive verdict

The courier idea fits District Zero very well. The current combined proposal,
however, is closer to a small production roadmap than a first playable slice.
It simultaneously asks the player to understand cargo integrity, impact
episodes, time bands, route efficiency, cleanliness, Flow, grades, Credits,
Reputation, unlock predicates, purchases, paints, trails, sealed routes, route
direction, pickup dwell, delivery settle, and a multi-panel modal flow. That is
too many unproved reasons for a delivery to feel good or bad.

The central question is much smaller:

> Does having a parcel make the already-enjoyable driving more exciting, and
> does the delivery receipt make the player want one more run?

Prove that with a three-job, geographically chained session, one cargo profile,
three visible reward lines, and one immediate paint choice. Do not build
Reputation, sealed-route adjudication, route efficiency pay, Flow money, a
shop, durable saving, or trails before that question is answered.

The strongest current work is the separation of gameplay observation from R7
movement, the authored-distance anti-farming principle, peak-based impact
episodes, soft time pressure, and reserved functional vehicle cues. Preserve
those. Simplify everything the player has to parse.

## Highest-priority contradictions

| Conflict | Why it matters | Red-team disposition |
| --- | --- | --- |
| The gameplay/economy studies keep manual/fall reset deliveries recoverable; the feasibility study makes any active reset an abort with no award. | These are different games. One promises that struggling finishes still count; the other makes a late fall erase the run. Tests cannot be written until one rule wins. | For the first slice, select **active reset aborts the attempt**. R7 reset returns to its own spawn and clears impact/Hop counters; pretending the same attempt continued would be difficult to explain and easy to exploit. Mark this as a human-frustration risk, not a settled long-term design. |
| The principles say open jobs preserve route choice; the payout and grade reduce a route-efficiency factor based on actual/reference distance. | A longer but faster, safer, or more enjoyable route becomes statistically worse even though the offer said the path was open. | Remove actual-distance efficiency from both money and grade in the first slice. Show distance as a receipt statistic only. |
| Clean impacts reduce integrity and separately reduce a cleanliness share. | The same mistake is charged twice, while the receipt presents the charges as different virtues. | Keep impact history as a badge/incident line. Let verified impact severity affect cargo condition once. No cleanliness money initially. |
| Flow is described as optional, yet it adds up to 6% Credits. | Anything that pays is economically required for optimization even if it does not affect grade. It also creates the hardest anti-farming machinery before the basic loop is proved. | Flow is a non-monetary badge and celebratory receipt line in the first slice. Add money only after unique-chainage behavior survives deliberate farming and players actually value the callout. |
| The economy study proposes a new immutable impact record at the controller decision point; the feasibility study proposes observing existing public snapshots while preserving R7 byte-for-byte. | The former touches a frozen movement file and creates a new preservation burden; the latter has less source identity but may be adequate. | First attempt a late-priority read-only observer of `impact_count` plus `last_impact_severity`. If exact-engine tests cannot group fair episodes from it, stop. Do not edit the controller merely to rescue cargo scoring without separate authority. |
| The reward study keeps resets recoverable and grade-capped; its own implementation feasibility resets `impact_count` to zero and says abort. | A recoverable reset would need an attempt-owned monotonic ledger across a controller counter discontinuity and a clear teleport rule. | Delete reset recovery from the first scoring fixture. Test it later as a distinct feature, not as a tuning toggle. |
| Reputation is supposed to gate content, but the first playtest exposes all jobs to obtain coverage. | In that build Reputation has no real job beyond adding a second number and fake unlock ceremony. | Defer Reputation entirely. One spendable Credit balance is already more economy than the core feel test needs. |
| Saving is deferred while ownership and prices are elaborated. | A player can mistake session-only rewards for durable progress; conversely, implementing persistence before cadence is known hardens the wrong schema. | Label the first build `SESSION PREVIEW`. If the slice is played across days, durable save outranks adding the second or third trail. |

These choices should be made explicitly in the living decision matrix. Leaving
both sides in prose will produce a harness that passes one contract and a UI
that promises another.

## Invalid or unproved world assumptions

### Distance-shortest is not gameplay-shortest

The route-network report uses undirected Dijkstra over baked metres. That is a
valid geometric calculation, but its conclusion is too strong. District Zero
routes have different widths, turn radii, surfaces, and intended forms:

- `A1` is `321.864 m`, smooth, wide, and explicitly `DRIVE_COMMITMENT`;
- `R0` is `137.716 m`, narrow/rough, and explicitly `SPREAD_ROUGH`; and
- HOP and DOG share endpoints but promise very different traversal behavior.

A longer route can be faster, safer for cargo, or more fun. Therefore the fact
that HOP, DOG, A2, or X0 is absent from a length-shortest path does **not** prove
it is economically irrational. Before adding sealed-route rules, record native
human and deterministic-driver travel times, incident rates, and form usage on
the plausible alternatives. If players naturally select a characteristic
route for time or safety, an additional route-enforcement system is needless.

Consequences:

- do not use actual/reference distance as a grade component;
- do not call the distance-shortest path the optimal path in player-facing UI;
- base Credits should be authored after observed completion time and risk, not
  mechanically generated from metres alone; and
- sealed routes remain a later content type, justified by a desired authored
  challenge rather than by Dijkstra alone.

### Logical pads are not proven interaction affordances

The world has six exact destination pads and an `8 m` inner-flat radius. That
proves adjudication geometry, not that a new player can see, name, or approach
the correct pad. The current minimap is a route drawing with nodes, not a fully
proved delivery navigator. A target needs a distinct non-colliding world cue,
an equally distinct map treatment, and a distance/direction HUD cue. Test all
three against the existing gold landmarks, cyan vehicle energy, shadows, and
dark horizon.

Do not solve confusion with a permanent route ribbon or screen-edge arrow
before testing the smallest target beacon plus highlighted map node. The
driving line should remain the player's choice.

### Open contracts do not need route-direction machinery

Telemetry's `TRAVERSED` event omits direction. The proposed adapter can derive
it, but that is new failure surface across 17 bidirectional routes. Endpoint
jobs need only a valid origin acceptance and destination settle. Do not build
or certify the route-direction adapter until a selected sealed-route contract
actually needs it.

### Spawn location should drive the tutorial sequence

The R7 player begins at MRK (`Vector3(0, 1.65, 20)`) and the world identifies
that location as the neutral MRK spawn. A first job beginning elsewhere creates
dead travel before the player understands the loop. Start at MRK and chain
destinations so each completed job leaves the craft at the next offer.

The gameplay study's proposed “recovery to pickup,” “destination becomes the
free-roam recovery anchor,” and result-screen retry are not free consequences
of that continuity principle. R7 has one mutable reset transform, and resetting
also clears impact/Hop counters. Changing the anchor per contract or
teleporting on Retry is new gameplay authority with its own exploit and
preservation tests. Omit both in the first slice: an active reset aborts, and a
completed delivery continues from the reached destination. Add intentional
replay teleporting only if native play proves it is more valuable than spatial
continuity.

## Reward-model red team

### The five-factor receipt is too dense

The proposed ordinary payout contains completion, nonlinear integrity, time,
cleanliness, and efficiency, followed by a separate Flow award. Grade then
recombines four of those factors. Even with explicit receipt lines, the player
must reason about six contributors and why two different summaries disagree.

The scenario table exposes the problem:

- a `95%` integrity, no-impact, par-time run is only `A`, partly because it took
  `1.10x` reference distance on a supposedly open job;
- a reset-recovery scenario earns more than the damaged-delivery scenario even
  though the former is marked assisted and the latter may have completed
  continuously; and
- a deliberately impossible circle-farm record with maximum Flow still earns
  `102` versus `116` for the clean-par run, making the economic meaning of
  “optional” Flow visible even though the real collector is meant to reject it.

Those outputs are mathematically consistent. They are not yet player-legible.

### Minimum scoring hypothesis

For the first playable slice, test only:

```text
credits = round_half_up(B * (0.50 + 0.35*I + 0.15*T))
```

Where:

- `B` is the fixed, displayed contract value authored from observed duration
  and declared cargo/route difficulty;
- `I` is final cargo integrity in `[0,1]`;
- `T` is the soft time factor in `[0,1]`; and
- successful delivery is the only terminal that pays.

The receipt has exactly three money lines:

1. `DELIVERY — 50%`;
2. `CARGO CONDITION — up to 35%`; and
3. `PACE — up to 15%`.

Authored distance is visible on the offer and is already reflected in `B`.
Actual distance, incidents, Hops, form use, and Flow may appear as facts or
badges but do not alter money. A one-line grade may summarize condition and
pace, but it must not apply another multiplier.

This is an exploratory simplification, not a selected production formula. It
has useful falsification properties: a completed run always earns at least
half base, condition remains the main skill term, and no odometer or style
collector exists to farm.

### Base values need rate normalization

The current `B_seed = nearest_5(40 + 0.25*D_ref + 40*K)` is a useful worksheet,
not safe economy authority. It omits pickup/results overhead, route width,
surface, turn commitment, likely form, and actual human completion time. A
short contract can become the dominant Credits-per-minute farm even when all
per-run formulas are exploit-safe.

After pars are observed, target respectable Credits per active minute within
roughly `15%` across the initial jobs. A specialist job may exceed that range
only for a visible risk the player can actually fail. Test deliberate low-grade
speed farming as well as clean play; the fastest repeatable bad strategy should
not beat a respectable run's rate.

### Reputation does not earn its complexity yet

Credits already answer the immediate reward question. Reputation adds another
ledger, grade conversion, first-clear flags, four gates, and stock rules before
there is enough content to gate. Defer it. If the game later needs a trust
track, introduce it when at least two meaningfully different contract families
exist and players can explain why Credits alone are insufficient.

## Interaction and frustration audit

### Pickup

A visible `HOLD/WAIT 0.6 s` pickup dwell adds friction without proving a skill.
The player is already required to be inside the inner pad, supported, and slow.
For the first slice, one explicit `E` press at `<=4 m/s` should atomically accept
and secure cargo after the contract card closes. Start the timer on the first
unpaused physics step after all gameplay controls return to neutral. If native
play shows accidental acceptances, add a short hold later.

### Delivery

Delivery settle does test a relevant skill: shedding momentum. Keep it, but
start with a short range (`0.35–0.60 s`) and a somewhat generous speed ceiling
(`6–8 m/s`) inside the exact `8 m` inner pad. The prompt must communicate which
condition is failing: `ENTER DELIVERY ZONE`, `SLOW TO UNLOAD`, or `HOLD LINE`.
Do not require Spread, do not auto-transform, and do not fail a fast fly-through.

### Reset

The simplest technically honest first rule is:

```text
R or fall reset during ACTIVE/DELIVERY_SETTLE
  -> ABORTED
  -> no payout
  -> one clear acknowledgement
  -> FREE_ROAM at the unchanged R7 spawn
```

This is a major feel risk. A late accidental fall can erase several minutes.
If Charlie's first two such incidents feel punitive, do not hide the problem
with a larger completion floor; the attempt never completed. Design a real
recovery/checkpoint rule in a later bounded pass. Do not silently continue an
attempt across an MRK teleport.

### Modal input

The neutral-release latch is not optional. The craft polls action state in
physics, so handled UI events can still become held movement/transform/Hop
inputs. Use the currently free contextual `E` action for interact, keep the
tree paused behind boards/results, and resume only after every gameplay action
is neutral. Test keyboard and gamepad.

## Cosmetic and accessibility red team

The three-paint/three-trail catalogue is an excellent **concept palette** and
an oversized first implementation target. Including the default creates at
least 16 paint/trail combinations before testing Spread, midpoint, Drive,
CLEAR, CAUTION, STRIKE, bright wall, dark horizon, ordinary road, reset,
pause, occlusion, reduced motion, and performance. The actual visual evidence
matrix grows much faster than “six cosmetics” suggests.

Risks already visible in the selected set:

- Ember Relay may compete with Spread-orange and caution-amber functional
  energy;
- Saltglass may lose the vehicle silhouette against pale walls;
- a warm Comet Ledger may resemble gold world markers;
- cyan Twin Vector may compete with Drive energy and teal map/UI cues;
- trails make motion more readable for some players and less comfortable for
  others; and
- color-distinct paints are still color-only changes, so names and preview
  cards need value/silhouette context rather than tiny color swatches.

For the minimum lovable slice:

- implement District Standard plus **two** cue-safe paint finalists;
- grant one free choice after the first completed delivery;
- keep owned/equipped state session-only and clearly labelled;
- do not build a shop yet; and
- do not implement a trail until the delivery/retry loop passes its feel gate.

Orchid Static is the safer first finalist. Saltglass is the second if bright
wall captures pass. Ember Relay should remain a concept until all functional
energy states are unmistakable. If one trail is later authorized, start with
Twin Vector on the shared bounded history core and ship `TRAIL OFF` plus reduced
motion in the same change.

The first delivery needs to change something visible, but the reward does not
need six assets and a storefront to prove that promise.

## Ruthless minimum lovable slice

### Product surface

Preserve R7 movement, world, camera, routes, terrain, and vehicle geometry.
Add only:

- one P1B scene/root;
- one contract-session state machine;
- one pure impact-episode reducer and one pure reward evaluator;
- one tiny authored contract catalog;
- one contextual target marker/map highlight;
- one compact active HUD and one result panel;
- one in-memory Credit balance; and
- District Standard plus two presentation-only paint profiles.

No route-direction adapter, sealed route, efficiency score, Flow collector,
Reputation, garage/shop, trail, save file, cargo rigid body, mechanical upgrade,
multi-stop contract, daily system, or generated content.

### Three geographically chained jobs

Build the first job completely and test it before adding the next two. The final
minimum lovable review session contains this chain:

| Order | Job | Natural authored path | Distance | Purpose |
| ---: | --- | --- | ---: | --- |
| 1 | `MRK -> DEP` | reverse `L1` | `129.430 m` | Spawn-local, forgiving explanation of accept, cargo, arrival, and receipt. |
| 2 | `DEP -> RLY` | reverse `L0`, then `A1` | `394.186 m` | Makes the wide Drive-commitment sweep and long-drift fantasy the second, unmistakable payoff. |
| 3 | `RLY -> CLN` | `L4 + L5 + L2`; legitimate outer alternative `A2 + L3` | `377.225 m` inner / `514.604 m` outer | Tests whether an open job produces a meaningful technical-versus-long-sweep choice without enforcing either route. |

All three are open endpoint jobs. Suggested path highlighting is guidance, not
adjudication. This sequence starts at the actual MRK spawn and every result
leaves the player at the next origin. It tests compact control, rough control,
and long Drive without implementing HOP/sealed-route machinery merely to claim
feature coverage.

This uses the gameplay study's stronger geographically continuous endpoint
sequence while rejecting its immediate expansion to Standard/Express/Fragile
profiles. Use one forgiving cargo profile across all three so route feel is the
changed variable. Record time from the start, but do not freeze par or base
values until owner runs establish real completion distributions.

### Minimal state machine

```text
FREE_ROAM
  -> OFFER                    # E at correct origin, supported and slow
  -> WAITING_FOR_NEUTRAL
  -> ACTIVE
  -> DELIVERY_SETTLE         # reversible while conditions hold
  -> RESULTS                 # immutable result; award exactly once
  -> WAITING_FOR_NEUTRAL
  -> FREE_ROAM

ACTIVE / DELIVERY_SETTLE
  -> ABORTED on reset
  -> FREE_ROAM after acknowledgement
```

There is no separate pickup dwell or `PICKUP_ARMED` state. The contract snapshot
is frozen at acceptance. Results commit before they render. One attempt ID can
award once.

### Reward beat

- Job 1 completion: show the three-line receipt, grant one free choice between
  Orchid Static and the second native-approved finish, and equip it immediately
  or retain District Standard at the player's choice.
- Jobs 2 and 3: award session Credits and show the growing balance, but do not
  open a store yet.
- End of chain: show a non-interactive preview of the next potential reward
  (for example Twin Vector) only if the loop itself passed; do not promise an
  unlock date or price.

This is enough to test whether delivery changes the meaning of driving and
whether visible rewards feel desirable. A shop would only test menu work.

## Explicit falsification tests

### Pure semantic tests

| ID | Test | Failure meaning |
| --- | --- | --- |
| `RT-PAY-01` | Holding `B,T` fixed, higher integrity never lowers Credits. | Formula or rounding is unfit. |
| `RT-PAY-02` | Holding `B,I` fixed, slower time never raises Credits. | Pace curve is exploitable. |
| `RT-PAY-03` | Credits are independent of actual odometer, route chainage, Flow, paint, and trail IDs. | Extra loops/style/equipment can mint money. |
| `RT-PAY-04` | Every successful finite record pays in `[0.50B,1.00B]` after one declared half-up rounding. | Completion floor or caps are false. |
| `RT-PAY-05` | Re-evaluating or reopening one attempt ID changes the balance exactly once. | Delivery-zone/result farming exists. |
| `RT-STATE-01` | Every illegal state transition is rejected; settle completion and reset racing on one tick produce one terminal only. | Double terminal/award risk. |
| `RT-STATE-02` | Pause advances neither active time nor settle time; unpause does not synthesize a large delta. | Menu use alters grade. |
| `RT-STATE-03` | Active manual and fall reset each create one `ABORTED`, zero award, cleared observer state, and no later completion for that attempt. | Teleport continuation or duplicate terminal exists. |
| `RT-IMPACT-01` | 30/60/120-sample representations of one equal peak impact episode yield equal damage within a preregistered tolerance. | Damage depends on physics sampling. |
| `RT-IMPACT-02` | A rising peak applies only incremental damage; `0.2 -> 0.5 -> 0.75` equals one `0.75` episode. | Sustained contact is double-charged. |
| `RT-IMPACT-03` | Two genuine impacts separated beyond the quiet window form two episodes; continuous wall pressure forms one. | Episode boundary is unfair. |
| `RT-IMPACT-04` | A stream with no `impact_count` increment, regardless of speed/sideslip/form/Hop count, produces zero cargo loss. | Expressive driving is being punished. |

### Exact-engine integration tests

| ID | Test | Failure meaning |
| --- | --- | --- |
| `RT-INT-01` | R7 comparison and C1 remain zero-delta with P1B scene idle, each paint selected, contract active, and results open. | Gameplay/presentation has coupled to movement. |
| `RT-INT-02` | The MRK prompt appears only inside the 8 m inner pad while supported and under the threshold; no prompt at the 8–13 m blend, airborne, or at another pad. | Logical/visual pickup authority is wrong. |
| `RT-INT-03` | Delivery settle resets immediately on radius exit, speed excess, support loss, or new impact, but merely pauses while the tree is paused. | Fly-through or menu completion exists. |
| `RT-INT-04` | Keyboard and gamepad modal close cannot produce throttle, brake, steering, transform, Hop, reset, accept, or cancel on the first resumed tick. | Input leak can launch the craft or dismiss screens. |
| `RT-INT-05` | Filling telemetry's 256-record evidence queue does not break gameplay observation. | Gameplay incorrectly drains evidence infrastructure. |
| `RT-INT-06` | Diagnostic menu, diagnostic spawn, and spawn-transform mutation are unreachable in the P1B scene. | Contract position/route evidence is invalidatable. |
| `RT-INT-07` | Ten no-contact high-speed drifts and supported Hops produce zero damage; a controlled wall strike produces one visible condition loss. | Cargo scoring attacks the movement fantasy or is inert. |
| `RT-INT-08` | Target marker, map highlight, and HUD clear atomically on result/abort and never identify a wrong destination after rapid state changes. | Navigation state is stale or misleading. |
| `RT-COS-01` | Paint changes mutate no energy/nozzle/bore material, physics node, collision state, controller property, or scoring input. | Cosmetic reward is not presentation-only. |
| `RT-COS-02` | Spread/Drive/CLEAR/CAUTION/STRIKE remain recognizable for every implemented paint against bright wall, road, shadow, and horizon captures. | Paint obscures functional state. |

### Economy and exploit simulations

1. Calibrate each job from at least five learned owner runs. Compare complete
   interaction-to-interaction duration, not route travel alone.
2. Respectable Credit rate across the three jobs must remain within a proposed
   `15%` band. If not, author new base values; do not pay actual distance.
3. For each job, run the fastest intentional low-integrity strategy. Its median
   Credits/minute must not exceed the respectable strategy.
4. Add arbitrary loops, reversals, detours, and off-route time. None may raise
   Credits or grade at identical terminal integrity/time.
5. Repeat the shortest job ten times. It may remain a valid preference, but it
   must not dominate both Credits/minute and progression because there is no
   progression track yet.
6. Deliver at every rounding boundary and repeat on all supported platforms;
   the integer award and receipt components must agree exactly.

### Human feel falsifiers

These are stop conditions, not questions automation may mark passed:

- Without a written manual, Charlie cannot accept the MRK job and identify the
  target within 30 seconds.
- The cargo HUD causes cautious play to reduce ordinary route speed by more
  than roughly 15% relative to an immediately preceding free-roam run, or makes
  the player avoid a previously enjoyable drift.
- A clean long drift is reported as cargo damage even once.
- The delivery settle produces two consecutive “I was in the zone; why did it
  not count?” reactions.
- The three-line receipt cannot be explained back as “delivery, condition,
  pace” after two results.
- Missing par feels like contract failure rather than lost bonus.
- One active reset late in Job 3 makes the player unwilling to retry. That is
  evidence to design recovery, not to quietly keep abort semantics.
- The first paint choice is not visibly meaningful in both Spread and Drive.
- The player chooses a route for joy or safety and then feels punished for not
  taking the highlighted path. Any such reaction rejects route-efficiency pay.
- After the three-job chain, the player does not want either a retry for grade
  or a new job. Cosmetics must not be used to disguise that result.

## Stage gates and stop rules

### Gate A — one-job proof

Implement only MRK-to-DEP, impact observation, target cue, settle, and the
three-line receipt. Stop for native play. If the parcel makes driving worse,
repair interaction/damage feedback before adding content or economy.

### Gate B — minimum lovable session

Add the DEP-to-RLY and RLY-to-CLN jobs, in-memory Credits, and the two-paint
first-clear choice. Stop again. This is the first point at which “gameplay
loop” and “reward bridge” can be judged together.

### Gate C — progression expansion

Only after Gate B passes should the team select among:

- a Flow badge/collector;
- one bounded trail core and Twin Vector;
- sealed-route/HOP contracts;
- Reputation and contract-family unlocks;
- a small garage/shop; and
- durable profile saving.

Do not begin all six. Select the one whose absence was actually felt in Gate B.

## Foundation synthesis freeze blockers

`FOUNDATION_SYNTHESIS.md` is a useful convergence draft, but the following
changes are needed before treating it as a frozen foundation:

1. **Make C02 open for the first slice.** The statement that the shorter inner
   route makes A1 “economically irrational” is not established by the
   distance-only graph. A1 is wide, smooth, and Drive-oriented; the inner route
   may be slower or riskier. Measure routes before authorizing a seal. Remove
   the sealed-route adapter from the first implementation sequence.
2. **Remove route efficiency from first-slice payout and grade.** It conflicts
   directly with C03's legitimate longer A2 alternative and with the stated
   promise that open route choice is not invalid. Actual distance remains a
   receipt statistic. Use the three-line completion/condition/pace challenger
   until owner comprehension is proved.
3. **Use one cargo profile across C01–C03 initially.** Standard/Express/Fragile
   simultaneously change damage and reward emphasis, confounding whether the
   route or the profile caused the feel result. Route geometry should be the
   independent variable in the minimum slice.
4. **Select one reset policy for implementation, not a “pure policy switch.”**
   Soft recovery requires changing the runtime recovery anchor and preserving
   an attempt ledger across controller counter reset; abort does not. Those are
   different integration architectures, not merely two pure scoring outcomes.
   Implement abort first, record its frustration risk, and authorize recovery
   separately if native play rejects abort.
5. **Start time on the first unpaused tick after neutral release.** “First drive
   intent” adds a new arming detector, can be triggered by irrelevant held
   inputs, and offers room for slope/noise/pre-acceleration disputes. The modal
   is already paused, so reading time is excluded without a `START_ARMED`
   subgame.
6. **Remove Reputation from the minimum slice.** The same synthesis says the
   first playtest exposes the authored chain and saving is deferred. Reputation
   has no necessary permission decision there. Add it only with enough content
   to make trust gates meaningful.
7. **Resolve the cosmetic-count contradiction.** The reward bridge promises a
   free choice among three paints and three priced trails, while the smallest
   sequence reaches only “one proof paint” before the second owner gate.
   Foundation should distinguish the researched launch palette from the
   authorized first implementation. The red-team recommendation is District
   Standard plus two paint finalists and no trail/shop before Gate B.
8. **Qualify the 18 checks.** They are deterministic design-lab arithmetic and
   graph checks, not gameplay, impact fairness, route optimality, exact-engine,
   or reward-feel evidence. Calling them simply “semantic checks” risks
   overstating foundation maturity.
9. **Do not freeze pars or base values yet.** They require complete human
   interaction-to-interaction runs, including braking and settle. Retain the
   formulas and current numbers as scenario seeds only.

With those edits, the synthesis would express one coherent first slice rather
than embedding both the broad roadmap and the ruthless experiment as if they
were the same authorization.

## Final red-team recommendation

Proceed, but narrow the first build aggressively. The current design is
strongest when it treats the contract as a lens on movement rather than a stack
of scoring systems. Three chained open deliveries, peak-based abstract cargo,
soft pace, an atomic receipt, session Credits, and one meaningful paint choice
are sufficient to answer the important question.

Reject for the first slice: efficiency pay, cleanliness pay, Flow money,
Reputation, sealed routes, route-direction adjudication, shop, trails, save,
and mechanical upgrades. Preserve those as researched options, not promises.

If the simplified loop is fun, the existing studies provide a credible path to
expand it. If it is not fun, six cosmetics and a more precise economy will only
make the wrong game more expensive.
