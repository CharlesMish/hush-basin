# District Zero — Delivery Gameplay Loop Study

Status: design research only. This document does not modify Vehicle R7, authorize P1B implementation, perform the Human World Gate, or change movement, world, route, telemetry, or presentation authority.

## Recommendation

Build the first playable game layer as a **momentum-courier loop**:

> Choose a delivery at a district terminal, load while settled, drive any physically valid line to the destination, preserve cargo condition through impacts, settle inside the destination pad, then receive a transparent time/condition result and continue from the place reached.

The loop should reward the thing that is already wonderful—maintaining speed and shaping a long drift—without directly awarding “drift points.” A clean long drift naturally improves delivery time. It must never lose cargo condition merely because the craft is sideways, fast, in Drive, or using Hop.

The best first slice is three fixed, chained contracts using the existing MRK, DEP, RLY, and CLN pads. They should represent standard, express, and fragile play without changing craft physics. Time and condition are bonus axes, not hard fail timers. Even a damaged or late delivery should usually be finishable, because completing the route is the main play experience.

## What R7 already provides

The current player build contains more game-ready substrate than its diagnostic presentation suggests:

| Existing capability | Useful delivery role |
| --- | --- |
| Six destination pads at `MRK`, `DEP`, `CLN`, `QRY`, `RLY`, and `WRK` | Dispatch, pickup, and delivery terminals without changing terrain |
| Each pad has an 8 m flat radius, 13 m blend radius, and 18 m clear approach | Natural nested interaction and arrival zones |
| 11 graph nodes and 17 baked routes | Authored contract references and route-choice comparisons |
| Long Drive routes `A1` (321.864 m) and `A2` (442.282 m) | Sustained-speed and long-drift contracts |
| Mixed `X0` quarry shelf (499.881 m), rough `R0`, and the `HOP`/`DOG` pair | Later cargo and route-choice variety |
| Minimap route polylines and multi-route highlighting | Contract preview and recommended-route feedback |
| Live node, route-entry, traversal, gate, Hop, surface, collision, and reset observations | Results breakdown and test evidence without controlling motion |
| Craft impact severity, closing speed, speed loss, and monotonic impact count | Behavior-neutral cargo-shock observation |
| Stable manual/fall reset and configurable recovery transform | Contract recovery anchored to the pickup rather than exploitable teleporting |

Important caveats:

- The current route and diagnostic machinery is observational evidence infrastructure. A delivery should not inherit autonomous-driver thresholds or require a player to remain inside a route envelope.
- `P1ATelemetry` has a bounded 256-event queue and can emit a collision sample on every contact tick. Gameplay state should subscribe to the live signal or observe stable craft counters; it should not depend on later draining an overflow-prone diagnostic queue.
- Collision samples are per tick, not necessarily one physical incident. Cargo loss must aggregate contact into impact episodes rather than subtracting condition every physics tick.
- The present Tab menu teleports to diagnostic segments. Any future contract session must block that teleport, abandon the active run, or place diagnostics behind an explicit development-only boundary.

## Product principles

### 1. The delivery gives movement a reason; it does not replace movement

The contract creates a destination, a reason to learn the district, and a small amount of pressure. Moment-to-moment pleasure still comes from throttle, braking, form choice, Hop, and the long transition between heading and velocity.

### 2. Fast is valuable; sideways is not damage

Cargo condition responds to discrete shock, not speed alone. These must be condition-neutral:

- sustained sideslip;
- a clean high-speed drift;
- being in Drive;
- changing form;
- ordinary braking;
- normal supported terrain following;
- a clean Hop and ordinary landing;
- choosing a longer legitimate route.

### 3. Time pressure is opt-in pressure, not an expiration clock

An express delivery can lose its time bonus, but the player can still finish. A fragile delivery can reach poor condition, but the trip can still resolve and teach something. Hard-failure modifiers should arrive later, clearly labeled, after the base loop is trusted.

### 4. Destination-to-destination continuity matters

Completing at DEP should leave the player at DEP, where a DEP-origin contract is available. The world should feel like a connected place rather than a list of teleporting challenges.

### 5. Results must explain themselves

The player should be able to answer, at a glance:

- what was earned for completing;
- what condition remained;
- what time bonus was earned or missed;
- which impacts or reset mattered;
- whether this was a personal best;
- what, if anything, was unlocked.

No hidden multiplier should decide most of the payout.

## The complete player cycle

```text
FREE ROAM
  -> approach a destination terminal
  -> DISPATCH (preview contract and route)
  -> ACCEPTED / TO PICKUP (only when origin is elsewhere)
  -> PICKUP READY (settle and explicitly load)
  -> LOADED / START ARMED
  -> ACTIVE DELIVERY
       -> optional recovery to pickup, with visible cost
       -> approach destination
  -> DELIVERY SETTLING
  -> RESULT COMMITTED
  -> RESULTS
       -> continue at destination
       -> retry from original pickup
       -> open destination dispatch
       -> return to free roam
```

Pause is an overlay on every safe state. Abandonment is a deliberate transition from accepted/active states to free roam; it is not a mysterious failure.

## State contract

| State | Timer | Cargo condition | Craft control | Important rule |
| --- | --- | --- | --- | --- |
| `FREE_ROAM` | Off | None | Normal | Nearby terminal may offer dispatch |
| `DISPATCH_OPEN` | Off | None | Paused or safely menu-owned | Previewing never starts a run |
| `TO_PICKUP` | Off | None | Normal | No condition or time penalty before loading |
| `PICKUP_READY` | Off | 100% staged | Normal | Explicit load prevents accidental contract starts |
| `START_ARMED` | Off until first intent | 100% | Normal | Starts on first meaningful input/motion, not menu time |
| `ACTIVE` | On | Observed | Normal | Route highlight advises but never steers or gates |
| `DELIVERY_SETTLING` | On | Observed | Normal | Impact/reset on the completion tick resolves before delivery |
| `RESULTS` | Frozen | Frozen | Paused safely | Payout is committed once before buttons become active |

Suggested implementation invariant: there is exactly one authoritative `run_id`, one monotonic physics-tick interval, one result commit, and at most one payout commit for an attempt.

## Dispatch interaction

### Where dispatch lives

Use the existing six destination pads as terminals. The current neutral spawn at MRK therefore begins near a dispatch point. A later presentation pass can add a restrained pad ring or terminal marker, but the loop should not require new buildings or NPCs.

### Opening dispatch

- Show `E — DISPATCH` only inside a terminal’s approach area and below a comfortable speed.
- Pressing E opens a compact list of contracts whose pickup is that terminal.
- Free roam remains available; closing the board changes nothing.
- If a contract is active, E at unrelated terminals must not silently replace it. Offer `Continue delivery` or an explicit `Abandon delivery` confirmation.

### Contract card content

Each card should show, in this order:

1. cargo/contract name;
2. destination name;
3. contract distance and likely character (`short`, `long sweep`, `technical`);
4. cargo profile (`Standard`, `Express`, or `Fragile`);
5. base completion reward and the two possible bonus categories;
6. personal best or `NEW`;
7. a cosmetic reward preview only when the contract has a first-clear or mastery reward.

The map should highlight a **recommended** route set while the card is focused. The card should say “recommended route,” not “required route.” The player remains free to discover another physically valid line.

### Acceptance

For the first slice, offer only contracts originating at the current terminal. This removes a dead “drive somewhere merely to begin driving somewhere” step. Later, the board may also reserve remote contracts, but accepting one should enter `TO_PICKUP` with no timer or cargo condition yet.

## Pickup interaction

The existing pad geometry suggests three concentric roles:

- 18 m approach: navigation cue becomes prominent;
- approximately 8 m flat pad: pickup zone;
- approximately 6–7 m inner capture: stable interaction zone accounting for the craft footprint.

Recommended pickup sequence:

1. Enter the inner zone.
2. Reduce tangential speed below a provisional `2.0 m/s` threshold.
3. Press and hold E for a short `0.35–0.50 s` load confirmation.
4. Show cargo attached in the HUD and a clean `READY` cue.
5. Arm the start while the craft is nearly stationary.
6. Begin the timer on the first meaningful throttle/brake/steer input, transform input, or speed above a small noise floor.

This avoids charging the player for reading, loading animation, or an interruption. It also prevents building full speed inside the pickup zone before the clock starts.

Do not lock movement with a hidden physics rule. If the craft leaves the zone before loading completes, simply reset the short load progress. Once loaded, leaving is allowed immediately.

## Active delivery feedback

### Persistent HUD

Keep the active display sparse:

- contract name and destination;
- directional/distance cue to the destination pad;
- elapsed time;
- cargo condition as an integer percent and a short bar;
- current bonus status in plain language (`Pristine`, `On pace`) rather than a constantly changing projected payout;
- minimap with the recommended route highlighted and destination emphasized.

The current speed/form/controls display can remain, but diagnostic details should default closed. Contract information should not consume the view needed to judge a drift.

### Event feedback

- A qualifying cargo shock briefly pulses the condition bar and shows one consolidated loss, such as `IMPACT −4%`.
- A minor non-damaging contact may show a small neutral shake/pulse in the cargo UI, not a false condition loss.
- Missing the express target changes `ON PACE` to `BONUS WINDOW PASSED`; it does not announce failure.
- Entering the destination approach changes the cue to `ARRIVE BELOW 4 m/s`.
- A recovery states exactly what happened: `RECOVERED TO PICKUP · −12% · +6.0 s` (values provisional).

Avoid a drift combo meter, continuous money counter, ideal steering line, or live route-lateral warning. Those would turn an expressive movement system into meter maintenance.

### What to record silently

For results and tuning—not mechanical control—record:

- elapsed physics time;
- actual horizontal path distance;
- route entry/traversal and gate events;
- time in Spread/Drive;
- Hop count;
- maximum and mean speed;
- discrete impact episodes;
- recoveries/resets;
- pickup and delivery settle attempts;
- terminal condition.

Sideslip angle may be measured later for design research, but it should not initially affect payout.

## Cargo integrity

### Why a calculated state is preferable

The first cargo should not be a separate physics body. A rattling object would create new collision, camera, determinism, and tuning problems. Cargo condition can be a deterministic observer of the craft’s already-authored impacts, leaving the vehicle physics untouched.

Store condition at a fixed visible precision—recommended tenths of a percent internally and whole percent on the ordinary HUD. Start at `100.0`, clamp to `[0,100]`, and never regenerate condition during an active run.

### Damage inputs

Use one normalized shock input from the craft’s existing strongest-impact observation:

```text
u = clamp((closing_speed - safe_closing_speed)
          / (severe_closing_speed - safe_closing_speed), 0, 1)

episode_loss = maximum_loss * pow(u, response_exponent)
```

All numbers remain cargo-profile data. A useful initial response exponent is greater than one (roughly `1.4–1.8`) so tiny contacts are forgiving while obviously bad strikes matter.

The initial calibration goal is qualitative, not an arbitrary universal curve:

| Maneuver | Standard target | Fragile target |
| --- | ---: | ---: |
| Clean drift, any sideslip | 0% | 0% |
| Clean form change | 0% | 0% |
| Normal Hop and landing | 0% | 0% |
| Small brush that barely changes velocity | 0–1% | 1–3% |
| Noticeable glancing impact | 2–6% | 5–12% |
| Poor wall entry or hard landing | 8–18% | 18–35% |
| Severe crash/recovery | Visible major loss, but usually still deliverable | May reach compromised condition |

These are tuning targets, not selected constants.

### Aggregate impact episodes, not ticks

The present controller can increment impact observations across repeated contact, and telemetry can report the same hard collider every tick. A single wall strike must not become 30 independent cargo hits because it lasted half a second.

Recommended episode algorithm:

1. Open an episode when `impact_count` advances.
2. Group further impacts while fewer than roughly `10–15` physics ticks pass without impact.
3. Track the episode’s maximum normalized shock and source classification.
4. Charge only the increase in the maximum computed episode loss, allowing immediate UI feedback without double charging.
5. Close the episode after the quiet gap.

If a player hugs a wall, the strongest strike still matters and the time/speed loss still matters; frame-rate-scaled condition destruction does not. A later clearly bounded scrape mechanic may add slow capped wear if play proves wall riding profitable, but it is not needed for MVP.

### Event precedence

Use this order on each physics tick:

1. sample movement and impact evidence;
2. update the active impact episode and condition;
3. process fall/manual recovery;
4. test delivery completion;
5. commit at most one terminal result.

If a reset and impact coincide, apply the greater of the reset loss or the incident’s calculated impact loss, rather than blindly summing both. If an impact occurs on the tick that settles a delivery, the impact is included before the condition is frozen.

### Cargo profiles for the first slice

`STANDARD`

- Forgiving safe threshold.
- Condition affects bonus and grade, never route access.
- Best onboarding profile.

`EXPRESS`

- Uses the Standard shock curve.
- Shifts reward emphasis toward time.
- Late delivery still completes and keeps the completion floor.

`FRAGILE`

- Lower safe threshold and steeper loss curve.
- Shifts reward emphasis toward condition.
- Zero condition produces a `COMPROMISED DELIVERY`, not an automatic mid-route deletion.

Do not call cargo “heavy” while leaving physics unchanged; players reasonably expect mass to change the craft. Heavy cargo should wait for an explicitly authorized movement sidegrade study or remain purely narrative with very clear wording.

## Timing

### Clock semantics

- Accumulate active physics delta, never system wall-clock time.
- Pause freezes the contract clock.
- Dispatch, loading, results, and free roam do not consume delivery time.
- The clock starts at first meaningful movement intent after loading.
- The clock stops only after destination settle succeeds.
- Recovery adds a visible fixed time penalty or continues the already-running clock; do not secretly do both unless the result states both.

### Establishing reference times

Do not derive a target only from route distance divided by top speed. Tight turns, entry/exit, braking, form choice, and delivery settling are the game.

For each contract:

1. Run at least five clean, purposeful owner/developer deliveries.
2. Exclude runs with debugging teleports, invalid starts, or implementation faults—not merely slow runs.
3. Use the median clean run as the first `reference_time` candidate.
4. Treat approximately `0.85 × reference` as an aspirational high-skill region and `1.20–1.30 × reference` as the point where the time bonus reaches zero.
5. Revisit only after Charlie plays; do not tune solely to automated driving.

Time should yield a smooth capped bonus, not discontinuous cliffs at arbitrary medal boundaries. Labels may still show broad achievements (`Swift`, `Express`, personal best) after the underlying result is computed.

## Delivery interaction

Use the destination’s existing pad:

1. At 18 m, emphasize the destination and display the arrival requirement.
2. Enter a 6–7 m inner delivery zone.
3. Settle below a provisional `4.0 m/s` tangential speed for `0.4–0.6 s`.
4. If speed rises or the craft leaves, settle progress resets without penalty.
5. On success, process all same-tick impacts, stop the timer, freeze condition, and commit the result.

This requires an intentional arrival but should not feel like precision parking. The arrival threshold deserves its own small study; compare approximately `2.5`, `4.0`, and `6.0 m/s`. Select the highest threshold that still reads as “delivered” rather than “drove through.”

A high-speed pass through the pad never completes. Feedback should say `TOO FAST — SETTLE`, not leave the player wondering why the contract failed.

## Results, retry, and free-roam continuity

### Results layout

Present the result in layers:

1. `DELIVERED`, `LATE`, or `COMPROMISED` outcome label;
2. large total reward;
3. simple breakdown: completion + time + condition + first-clear/mastery;
4. condition percent and the two or three most important incidents;
5. time, personal best comparison, actual distance, and recoveries;
6. unlocked cosmetic preview, if any;
7. choices: `Continue`, `Retry`, `Dispatch here`, `Free roam`.

Never require reading a 10-line telemetry table to understand a low reward. Detailed route and impact information can expand under `Run details`.

### Result commit

Write or hold one immutable result before enabling buttons. Reopening results cannot award again. A retry creates a new run ID. Repeating a completed contract is legitimate play and may earn its configured repeat reward; repeatedly pressing a results button is not.

### Continue

Continue leaves the craft at the destination with cargo cleared. The destination becomes the free-roam recovery anchor. This makes the next contract in the chain feel spatially continuous.

### Retry

Retry starts a clean new attempt at the original pickup pad, zero velocity, full cargo condition, and no inherited timer/events. It does not roll back the already-committed prior result.

### Active recovery

Preserve the familiar R behavior, but make its contract meaning explicit:

- return to the active contract’s pickup pad, never a destination or arbitrary diagnostic spawn;
- preserve the same run ID and elapsed run;
- apply one visible condition and/or time cost;
- zero velocity and clear transient input as the current reset already does;
- do not count teleport distance as travelled;
- do not let recovery cross or complete a route/destination.

This turns a fall or bad wedge into a soft setback without creating a shortcut. The pickup remains the only safe anchor in MVP; intermediate checkpoints would complicate exploit resistance and route choice.

## Failure philosophy

### Soft outcomes in MVP

- **Late:** time bonus reaches zero; delivery remains possible.
- **Damaged:** condition bonus falls; delivery remains possible.
- **Compromised (0%):** small completion floor remains; results clearly state the cargo outcome.
- **Recovered:** visible time/condition cost; continue from pickup.
- **Abandoned:** no payout; return to free roam.
- **Application closed/reloaded:** active run is not awarded. MVP need not resume it.

The player should learn by finishing a run. Mid-route hard failure is reserved for later opt-in contracts whose card clearly says so.

### Later hard modifiers

Possible later challenge contracts may fail on zero condition, any recovery, or a strict delivery window. They should be separate named modifiers, carry visibly higher rewards, and unlock only after the base version has been completed. They must not become the default balance target.

## Suggested initial three-contract chain

The following sequence begins at the existing MRK spawn and leaves the player at the origin of the next contract.

### C01 — Market Parcel

| Field | Proposal |
| --- | --- |
| Origin → destination | `MRK → DEP` |
| Recommended route | `L1` in reverse |
| Reference distance | `129.429845 m` |
| Cargo profile | Standard |
| Purpose | Teach dispatch, loading, map cue, deliberate arrival, and transparent result |

This is short enough to retry immediately and curved enough to introduce the craft’s committed steering. It should have forgiving condition thresholds and a generous/no-pressure time bonus. Its first-clear reward should be visually immediate but modest, such as the first alternate body color or trail tint.

### C02 — Relay Window

| Field | Proposal |
| --- | --- |
| Origin → destination | `DEP → RLY` |
| Recommended routes | `L0` reverse, then `A1` |
| Reference distance | `72.321850 + 321.864198 = 394.186048 m` |
| Cargo profile | Express (Standard condition curve) |
| Purpose | Make the long west sweep and sustained drift the star of the loop |

This is the main “why this vehicle exists” contract. The player exits the denser market area, crosses the west gate, accelerates into A1, and has room to hold a long committed line. Reward time, but do not score yaw/slip directly. A clean long drift becomes valuable because it preserves speed.

The reference time must include braking and settling at RLY. Otherwise the contract would reward crashing through the mast approach rather than completing a courier run.

### C03 — Clinic Glass

| Field | Proposal |
| --- | --- |
| Origin → destination | `RLY → CLN` |
| Recommended core route | `L4 + L5 + L2` |
| Core reference distance | `80.000000 + 167.795314 + 129.429845 = 377.225159 m` |
| Legitimate outer alternative | `A2 + L3 = 514.603795 m` |
| Cargo profile | Fragile |
| Purpose | Ask whether the player chooses shorter technical control or a longer high-speed sweep |

This is the most interesting initial route-choice contract. The map recommends the inner route but does not enforce it. The player may take the longer A2 outer sweep if that feels safer or more enjoyable at speed. Actual distance should not generate extra credits, and the longer choice should not be punished merely for being longer. Time and condition together determine whether that choice was worthwhile.

The result should explicitly compare `recommended 377 m / travelled X m` without calling deviation a mistake.

## High-value later contracts

These are good extensions only after the three-contract loop proves itself:

### Quarry Choice — QRY to RLY

- Fast graph route: `A0 + A1 = 398.374130 m`.
- Mixed shelf alternative: `X0 = 499.881048 m`.
- Strong candidate for a later Courier’s Choice contract with two visually distinct lines.

### Southline Multi-stop — DEP to CLN via HJW/HJE

- Market direct: `L1 + L2 = 258.859690 m`.
- South HOP line: `S0 + HOP + S1 = 304.355164 m`.
- South bent line: `S0 + DOG + S1 = 338.869245 m`.

Without a transit pickup/scan, the direct market way dominates. A later multi-stop contract can require a legitimate handoff at HJW and HJE, then let the player choose HOP or DOG. This gives Hop a delivery reason without arbitrarily declaring that every DEP→CLN courier must take the longer route.

### Works Materials — MRK/WRK/GE

`L6` and `L7` form a readable works corridor, while `R0` provides a rough alternative between GN and WRK. This is suitable for a later robust-versus-fragile cargo comparison, not for the first onboarding trio.

## Optional modifiers

### Suitable early, as fixed contract profiles

- `STANDARD`: balanced time/condition weights.
- `EXPRESS`: larger time bonus, no hard expiration.
- `FRAGILE`: steeper shock loss and larger condition bonus.

These should be authored contract identities in MVP, not a combinatorial modifier picker.

### Suitable after the base loop

- `NO RECOVERY`: one recovery removes the modifier bonus but may still allow normal completion.
- `PRISTINE REQUESTED`: unusually large 100% condition bonus; ordinary condition payout remains.
- `COURIER’S CHOICE`: two recommended route sets, with neither mechanically required.
- `MULTI-STOP`: two or three destination-pad handoffs; later HJW/HJE transit scanners may support the South choice.
- `SEALED`: resets or unauthorized diagnostic state mark cargo unsealed, removing one bonus rather than deleting the run.
- `TIGHT WINDOW`: narrow time bonus for mastered contracts; late still resolves unless the card explicitly says otherwise.
- `HOP-CERTIFIED`: a transit objective that is designed around HOP/DOG choice, introduced only after the Southline route is proven readable.

### Avoid or defer

- Drift distance paid directly: farmable by circles and makes the player watch a combo meter.
- Actual distance paid positively: farmable by detours.
- Permanent speed upgrades: disturb the carefully matched routes, braking, camera, HOP clearance, and movement evidence.
- “Heavy” cargo with unchanged movement: misleading premise.
- Random cargo failure or random fragility: conflicts with learnable, mechanical driving.
- Hidden route requirements: undermine exploration and create confusing non-completions.
- Constant freshness decay layered on top of express time: redundant pressure until play proves a distinct need.

## Protecting long-drift fun

The following should be written as gameplay acceptance invariants:

1. Cargo condition cannot read heading/velocity sideslip angle as damage.
2. Cargo condition cannot read Drive duty as damage.
3. No direct drift-length currency exists in MVP.
4. Route envelopes are observational; leaving a recommended route does not fail or damage cargo.
5. Condition is charged once per physical impact episode, not once per contact tick.
6. Express rewards include arrival braking and settling, not only reaching the destination radius.
7. A clean long drift should improve time without requiring UI acknowledgment.
8. Form choice and Hop remain entirely player controlled.
9. No contract silently modifies thrust, steering, drag, hover, impact response, collider, or camera.
10. Standard and fragile calibration explicitly include clean high-sideslip runs that must lose `0%` condition.

An optional post-run accolade such as `FLOWING LINE` may later recognize a fast, no-impact, no-recovery run. It should be a small badge, not a large economic multiplier, and should not measure raw seconds sideways.

## Exploit and edge-case matrix

| Case | Required behavior |
| --- | --- |
| Drive in circles before leaving pickup | Timer begins on meaningful input/motion; cannot pre-accelerate for free |
| Drive extra laps to increase distance | Base reward uses authored contract distance; actual distance never increases base pay |
| Discover a shorter off-route line | Allowed if physically valid; no route-envelope punishment; investigate only if it crosses broken geometry |
| High-speed destination fly-through | Does not complete; shows settle instruction |
| Repeated collision samples while scraping | One aggregated episode with incremental maximum loss, not per-tick loss |
| Impact on completion tick | Condition updates before result commit |
| Reset on completion tick | Reset/recovery wins; no ambiguous payout |
| Manual reset during active run | Return to pickup with explicit cost; never teleport forward |
| Fall reset | Same recovery contract as manual reset, with one record and no double penalty |
| Diagnostic segment teleport | Blocked during active run or explicitly abandons it; never credited |
| Pause/Alt-Tab | Physics timer does not advance while paused; wall clock is irrelevant |
| Queue overflow | Gameplay consumes live signal/counters, not only the bounded diagnostic queue |
| Condition reaches zero | Mark compromised; allow ordinary MVP delivery and reduced reward |
| Player abandons | Confirmation, no payout, cargo cleared, free roam restored |
| App closes mid-run | No payout; MVP may discard the run rather than implement fragile resume |
| Reopen results | Previously committed result cannot pay again |
| Retry after payout | New run ID; prior result remains committed |
| Route polylines overlap at a junction | Completion uses destination pad, not whichever telemetry route wins |
| Spawn/reset begins inside a route | Never counts as route traversal; existing telemetry semantics already enforce this |
| Throttle against a wall indefinitely | Condition episode is bounded, but time/speed cost remains; monitor before adding scrape wear |

## Contract data shape

A small data-driven contract record is enough; do not build a general quest framework. Suggested fields:

```text
id
display_name
origin_node_id
destination_node_id
cargo_profile_id
recommended_route_ids[]
alternative_route_sets[][]
reference_distance_m
reference_time_s (selected only after play)
completion_reward_id
first_clear_reward_id
mastery_conditions[]
result_copy
```

Runtime state should be separate:

```text
run_id
contract_id
state
start_physics_tick
elapsed_s
actual_distance_m
condition_tenths
impact_episode_ledger[]
recovery_count
hop_count
route/gate observations[]
result_committed
payout_committed
```

The result should preserve the literal contract definition identity used by the run. This makes balance changes reviewable and prevents an old attempt from being silently rescored under new values.

## MVP boundary

### Include

- Three fixed contracts: Market Parcel, Relay Window, Clinic Glass.
- Dispatch at the relevant existing pads.
- Explicit pickup and deliberate destination settle.
- Standard, Express, and Fragile authored profiles.
- One deterministic impact-episode condition model.
- Soft recovery to the pickup.
- Timer, condition, result breakdown, personal best in memory, and a reward interface.
- Recommended route highlighting without enforcement.
- Continue, retry, dispatch-here, free-roam, and abandon transitions.
- Behavior-equivalence test proving no-contract/free-roam movement remains unchanged.
- A three-contract owner playtest before saves, procedural generation, or mechanical upgrades.

### Do not include yet

- Procedural or rotating contracts.
- Persistent save/economy migration.
- NPCs or traffic.
- Physical cargo bodies.
- Multi-stop delivery.
- Hard-failure default contracts.
- Drift combos or style-score economy.
- Mechanical upgrades or cargo mass effects.
- Route enforcement/checkpoint corridors.
- Contract-specific movement/camera/tuning changes.
- A large shop; cosmetic reward presentation can be prototyped separately.

## Tuning and refinement plan

### Pass 1 — Interaction feel

Test pickup hold, destination speed, and settle duration independently of payout.

Questions:

- Does loading feel explicit without feeling ceremonial?
- Can the player understand a too-fast arrival immediately?
- Does deliberate delivery add a satisfying braking decision?
- Can results be reached without reading documentation?

Compare only a few bounded arrival candidates, for example:

- delivery speed `2.5 / 4.0 / 6.0 m/s`;
- settle duration `0.25 / 0.50 / 0.75 s`.

### Pass 2 — Integrity calibration

Capture a small repeatable maneuver set in both Spread and Drive:

- clean long drift;
- ordinary cornering;
- gentle brush;
- glancing wall strike;
- direct wall strike;
- ordinary Hop landing;
- intentionally poor landing;
- rough-route traversal;
- manual/fall recovery.

Select profile curves only if clean drift/form/Hop remain zero-loss and obvious driving errors produce legible, non-random differences.

### Pass 3 — Time calibration

Run each contract cleanly at least five times. Select reference times from human runs, then verify:

- C01 does not make a new player rush the UI;
- C02 visibly rewards maintaining the long sweep;
- C03 leaves both inner and outer route choices plausible;
- braking into the destination is part of the time decision;
- a late run still feels worth finishing.

### Pass 4 — Reward comprehension

Before adding more cosmetics, ask whether the results screen can be predicted:

- Did the player know which impact mattered?
- Did a one-second improvement produce a proportionate—not cliff-like—change?
- Was 100% condition visibly special?
- Was the next attainable reward clear?
- Did the player want one more run for the driving, not only to fill a bar?

### Pass 5 — Whole-loop play

Play the three contracts as a chain without diagnostic teleporting. Evaluate:

- time from launch to first active delivery;
- whether transitions interrupt movement too much;
- whether results encourage retry or continuation;
- whether the district begins to feel connected;
- whether stakes make long drifts more exciting or merely more anxious;
- which contract the owner voluntarily repeats.

## Automated checks worth planning

- Free roam with the contract system idle has a zero-delta movement trace against R7.
- Accepting/reading dispatch cannot change craft velocity or condition.
- Timer begins once and pauses correctly.
- Clean drift at high speed and large sideslip yields zero condition loss.
- Impact aggregation is invariant to repeated identical contact samples and physics-tick count within the episode window.
- One severe event produces more loss than one mild event for every cargo profile.
- Same-tick impact is included before delivery.
- Payout/result commit is idempotent.
- Actual distance above reference never raises the authored-distance reward.
- Reset cannot advance the craft toward the destination.
- Diagnostic spawn cannot preserve an active payout-eligible run.
- Delivery requires zone, speed, and dwell simultaneously.
- Every contract’s origin/destination and route IDs resolve exactly once in existing world data.
- The three reference-distance sums match the frozen route lengths.

Automated checks cannot decide whether the pressure is fun, whether the destination settle feels fussy, or whether the reward feels worth another run. Those remain owner-play questions.

## Decisions to carry into implementation planning

Recommended defaults for the first prototype:

- Destination-based completion; routes are advice and observations.
- Contract distance, not actual travelled distance, determines base value.
- Time and condition bonuses are independent and plainly itemized.
- Standard/Express/Fragile are fixed contracts, not stackable modifiers.
- Low condition and late arrival are soft outcomes.
- Active recovery returns to pickup with one visible cost.
- No drift scoring, speed upgrade, physical cargo, persistence, or procedural board in the first slice.
- Three chained contracts, followed by an owner playtest before expansion.

The central playtest question is:

> Does carrying something make a clean long drift feel more consequential and satisfying without making the player afraid to use the craft expressively?

If yes, the delivery loop is a strong foundation for cosmetics, economy, and later contract variety. If not, refine condition feedback and timing pressure before producing more content; do not compensate by adding a larger reward catalog.
