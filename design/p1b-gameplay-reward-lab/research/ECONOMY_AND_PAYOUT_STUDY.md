# District Zero P1B — Economy, Payout, Grading, and Progression Study

Status: `DESIGN STUDY — NO R7 SOURCE CHANGE`

Read-only reference: `District-Zero-P1A-v1.2.8-Vehicle-R7-Player`

This document recommends a transparent, bounded reward model for a momentum
courier game. It is a tuning proposal, not product authority. Vehicle R7,
movement, world geometry, and the verified P1A acceptance record remain
unchanged.

## Executive recommendation

Build the first game loop around a simple promise:

> Take a real contract between named district pads, arrive quickly, and return
> the cargo in the best condition your chosen line permits.

The scoring model should reward completion first, condition second, and speed
third. It should recognize a clean long drift without making drifting mandatory
or allowing donuts to print money.

Use:

- one fixed integer base value authored into each contract;
- a `45%` completion share, so an imperfect delivery still moves the player
  forward;
- up to `30%` for cargo integrity, `15%` for time, `6%` for clean execution,
  and `4%` for route efficiency;
- a separate optional Flow bonus capped at `6%` of base value;
- grades calculated from the same four quality components, excluding the
  completion floor and optional Flow;
- Reputation as a permanent, non-spendable permission track;
- Credits as the only spendable currency, used for presentation only;
- no speed, braking, hover, integrity-resistance, or payout upgrades in the
  first progression layer.

This model makes a battered completion worth roughly half a contract, makes an
ordinary respectable run worth roughly `0.8S` where `S` is the published base,
and lets a near-perfect flowing run reach at most about `1.06S`. The spread is
large enough to make skill visible without turning a bad delivery into wasted
time.

## What the existing district supports

The R7 source already supplies unusually useful foundations for delivery play:

- `17` frozen routes and `11` named nodes;
- `6` destination pads: `CLN`, `DEP`, `MRK`, `QRY`, `RLY`, and `WRK`;
- baked route chainage and lateral-distance projection;
- route enter/traverse events with reset-safe continuity rules;
- collision source, normal, horizontal speed, and craft velocity evidence;
- controller-local `last_impact_severity`, `last_impact_closing_speed`, and
  `impact_count` state, but no durable telemetry event that binds normalized
  severity to its pre-slide velocity, collision normal, and source identity;
- Hop, surface-class, gate-crossing, manual-reset, and fall-reset observations;
- route highlighting on the existing map; and
- a presentation-only vehicle rig suitable for cosmetic rewards.

The route graph also gives useful fixed contract distances. These are authored
facts, not odometer measurements:

| Example | Frozen path | Distance |
| --- | --- | ---: |
| `MRK -> WRK` | `L6` | `118.071 m` |
| `DEP -> QRY` | `L0 + A0` | `148.832 m` |
| `DEP -> CLN` | `L1 + L2` | `258.860 m` |
| `MRK -> RLY` | `L5 + L4` | `247.795 m` |
| sealed `RLY -> CLN` via east gate | `A2 + L3` | `514.604 m` |
| `QRY -> RLY` | `A0 + A1` | `398.374 m` |
| optional shelf alternative | `X0` | `499.881 m` |

This is enough structure to price jobs from contract authority. There is no
need to pay by actual distance driven, procedurally regenerate routes, or
change the movement system.

## Complete player-facing loop

### State sequence

```text
FREE ROAM
  -> CONTRACT OFFER AT ORIGIN PAD
  -> ACCEPTED / PICKUP ARMED
  -> CARGO SECURED
  -> ACTIVE DELIVERY
  -> ARRIVAL PENDING
  -> DELIVERED / RESULTS
  -> EQUIP OR CONTINUE
  -> FREE ROAM
```

There is exactly one active contract. No contract state may steer, brake,
transform, move, or retune the craft.

### Offer and acceptance

- Offers appear only at their authored origin pad. The player cannot accept a
  `MRK -> WRK` contract while parked beside `WRK`.
- The card shows destination, cargo profile, authored distance, soft par time,
  base credits, and one suggested route family.
- Suggested routes on ordinary contracts are highlights, not compulsory
  corridors. A shortcut or improvised line remains legal. A separately named
  `SEALED ROUTE` variant may require declared route traversals/checkpoints, but
  must say so on the offer and still end at a real destination pad.
- The contract is not timed and carries no cargo until pickup completes.

### Pickup

- The craft must be inside the origin pad, supported, at no more than roughly
  `4 m/s`, for a proposed `0.6 s` dwell.
- Leaving or accelerating cancels dwell without failing the contract.
- On completion, emit one `CARGO_SECURED` transition and start time, distance,
  integrity, cleanliness, and Flow accounting on the next physics tick.
- Cargo is an abstract scored state. Do not create a loose rigid body, mass
  change, collider, or visual object whose physics can destabilize R7.

### Active delivery

- The timer is soft. No ordinary contract expires.
- The HUD shows destination, integrity, elapsed time versus par, and a compact
  next-direction/map cue. It does not continuously calculate projected payout;
  that would encourage dashboard play instead of driving.
- Pause freezes both physics and the contract clock. Ordinary UI that does not
  pause the game must not slow time or alter input.
- Manual and fall resets keep the contract recoverable, apply their declared
  scoring consequences, invalidate efficiency/Flow across the teleport, and
  mark the run assisted.
- Explicit abandon returns to free roam with no payout, no Reputation loss,
  and no hidden penalty.

### Arrival

- Entering the destination at speed never causes an arbitrary failure.
- Inside a proposed `9 m` pad radius, show `SLOW TO UNLOAD` until horizontal
  speed is at most roughly `6 m/s`.
- Require support plus a proposed `0.6 s` settle. Do not require Spread and do
  not auto-transform; a sufficiently controlled Drive arrival is valid.
- A new impact or leaving the radius resets only the settle timer.
- The first valid settle atomically freezes the run record. One run ID can
  commit payout exactly once.

### Results

Present the reward in this order:

1. `DELIVERED` and cargo integrity;
2. time, actual distance, efficiency, and incident summary;
3. grade and optional badges (`PERFECT CARGO`, `CLEAN LINE`, `FLOW`);
4. an explicit credit breakdown and new balance;
5. Reputation gain and any newly available stock/contracts;
6. cosmetic preview/equip if relevant; and
7. continue or retry.

Never hide all reward arithmetic behind one multiplier. A player should be able
to see, for example, that completion earned `45% of base`, condition earned
`24%`, and Flow added `+4` credits.

## Authoritative scoring inputs

For one completed run define:

| Symbol | Range | Meaning |
| --- | ---: | --- |
| `B` | positive integer | authored base credits; immutable during the run |
| `I` | `[0,1]` | final cargo integrity |
| `r_t` | `>=0` | elapsed time divided by stored par time |
| `T` | `[0,1]` | soft time factor derived from `r_t` |
| `C` | `[0,1]` | clean-execution factor derived from contact episodes/resets |
| `D_ref` | `>0 m` | authored reference path distance |
| `D_actual` | `>=0 m` | continuous horizontal distance after pickup |
| `E` | `[0,1]` | route-efficiency factor |
| `F` | `[0,1]` | optional, bounded clean-drift Flow factor |

All factors are clamped before use. Display values may be quantized, but payout
must use the frozen terminal run record rather than strings rounded for UI.

## Cargo integrity

### Principle

Integrity responds to energy directed into a contact, not to sideslip itself.
A `25 m/s` clean drift can preserve `100%`; a `15 m/s` near-normal wall strike
can damage cargo. Hop costs no integrity merely because it occurred. A rough
landing can damage cargo through the same impact observation as any other
contact.

### Contact-episode aggregation

`P1ATelemetry` can emit hard-geometry collision samples on consecutive physics
ticks during sustained contact, but those records contain the post-response
craft velocity rather than the pre-slide velocity used by the movement impact
calculation. `CraftController` retains only mutable last-impact fields and a
count. That is enough to show an observation seam exists, but not enough to
claim a durable, source-bound cargo-damage record.

Before cargo scoring, add one behavior-neutral impact observation at the same
point where the existing controller already has `pre_move_velocity`, strongest
normal, closing speed, and normalized severity. The immutable record should
also bind the collider/source identity and physics tick. It may enqueue or emit
data only; it must not change the existing response, velocity, collider, or
tuning. Alternatively, a pure observer may reproduce
`MotionMath.impact_response` severity from captured pre-slide velocity and
normal, but it must prove exact equality with the controller result.

Charging any observation per tick would make wall hugging catastrophic and
potentially rate-dependent. Aggregate the proposed records first:

1. Begin an episode on the first qualifying impact.
2. Keep it open while related contacts continue; source identity, a strongly
   similar normal, and a proposed `0.25 s` contact gap define continuity.
3. Track the maximum verified normalized severity `p` in `[0,1]` from the new
   immutable observation record.
4. When the peak rises, apply only the incremental difference between the new
   and already-accounted peak loss.
5. Close after the contact gap. A long scrape with a constant peak therefore
   costs the same at 30, 60, or 120 physics observations.

For cargo profile maximum loss `L_max`, the total loss of one episode is:

```text
episode_loss(p) = L_max * p^1.35

incremental_loss = episode_loss(new_peak) - episode_loss(old_peak)
I_next = clamp(I_current - incremental_loss, 0, 1)
```

Candidate profile seeds:

| Cargo profile | `L_max` | reset loss | Role |
| --- | ---: | ---: | --- |
| Rugged | `0.18` | `0.12` | forgiving familiarization |
| Standard | `0.28` | `0.18` | ordinary contracts |
| Fragile | `0.40` | `0.25` | deliberate braking/line choice |

Resulting whole-episode losses illustrate the range:

| Peak severity | Rugged | Standard | Fragile |
| ---: | ---: | ---: | ---: |
| `0.20` | `2.05%` | `3.19%` | `4.55%` |
| `0.50` | `7.06%` | `10.98%` | `15.69%` |
| `0.75` | `12.21%` | `18.99%` | `27.13%` |
| `1.00` | `18.00%` | `28.00%` | `40.00%` |

These are deliberately tuning seeds. Native owner play must decide whether the
existing impact-severity curve maps to these perceived consequences.

### Integrity rules

- No passive decay and no damage from elapsed time.
- No damage from steering angle, yaw rate, sideslip, Drive duty, or trail use.
- Do not double-charge a landing as both a landing rule and the same impact
  episode. The episode is the source of truth.
- A reset applies one declared profile loss and marks the run assisted.
- For the first slice, integrity reaching zero does not destroy or fail the
  contract. The player may deliver compromised cargo for a low grade and the
  completion floor. This keeps learning runs productive.
- Later high-risk modifiers may fail at zero, but only after the forgiving loop
  proves itself; they must advertise that rule before acceptance.

## Soft time factor

Store a fixed `par_time_s` per contract. Time never raises the base value or
causes routine failure. Convert elapsed/par ratio with a piecewise-linear curve:

| `r_t = elapsed / par` | `T` |
| ---: | ---: |
| `<=0.85` | `1.00` |
| `1.00` | `0.85` |
| `1.25` | `0.55` |
| `1.75` | `0.20` |
| `>=2.50` | `0.00` |

Interpolate linearly between anchors. The curve gives a clear expert band,
does not sharply punish missing par by one frame, and gradually stops paying a
time bonus rather than failing the run.

Initial par values should be seeded from route length and conservative form
speeds, then replaced by recorded owner runs. A practical calibration protocol:

1. record five successful runs after learning the interaction;
2. use the median of runs 2–5 as the observed clean baseline;
3. seed par at roughly `1.10–1.18` times that median;
4. keep the `0.85 par` full-time-score anchor; and
5. do not silently personalize or dynamically lower par.

## Distance and efficiency

### Reference distance

`D_ref` is stored in the contract registry. It is normally the sum of a named
frozen route bundle. If several route bundles are intentionally legal, use the
shortest authored bundle and list all suggestions separately.

Do not calculate base credits from `D_actual`. Paying by odometer turns circles
into employment.

### Actual distance

Accumulate craft-center XZ distance between consecutive normal physics samples
while cargo is active. Exclude:

- pickup and post-completion movement;
- pause time;
- reset/teleport displacement; and
- the first sample after any discontinuity.

A shortcut with `D_actual < D_ref` receives full efficiency but no value above
full. The soft factor is:

```text
r_d = max(1, D_actual / D_ref)
E = clamp((1.40 - r_d) / 0.40, 0, 1)
```

Thus `E=1` at or under reference distance, `0.75` at `1.10x`, `0.50` at
`1.20x`, and `0` at `1.40x` or more. Efficiency is only `4%` of ordinary
payout, so exploration is permitted rather than harshly taxed.

## Clean execution

Classify completed contact episodes by peak verified normalized impact
severity from the behavior-neutral observation seam described above:

- below `0.15`: microcontact, ignored;
- `0.15 <= p < 0.50`: brush;
- `p >= 0.50`: hard impact.

For hard count `H`, brush count `N`, and reset count `R`:

```text
C = clamp(1 - 0.18*H - 0.05*N - 0.35*R, 0, 1)
```

This factor is intentionally small in payout because integrity already captures
impact intensity. Its main job is distinguishing one large hit from a truly
clean line and making resets visible without deleting completion earnings.

## Clean-drift Flow

Flow should celebrate the discovered long-drift pleasure, not become a required
driving technique.

### Eligibility

Count a `5 m` route-chainage bin at most once when all are true:

- cargo is active;
- horizontal tangential speed is at least a proposed `12–15 m/s`;
- absolute sideslip between velocity course and craft forward is within a
  proposed `12–75 degrees`;
- the craft is on a contract-declared Flow-eligible route and advancing in the
  destination direction;
- no qualifying impact occurs during the bin or within a short proposed
  `0.4 s` invalidation window; and
- the bin has not previously been credited in this run.

Chainage direction and unique bins prevent donuts, back-and-forth oscillation,
and repeated wall-side drifting from farming Flow. Off-route creativity remains
legal and unpenalized; it simply does not create an easily verifiable Flow
bonus in the first slice.

Define:

```text
flow_target_m = 0.20 * D_ref
F = clamp(unique_qualified_flow_progress_m / flow_target_m, 0, 1)
```

Flow does not enter the grade. A clean straight run can still earn `S`. It adds
only this bounded style amount:

```text
flow_credits = round_half_up(B * 0.06 * F * (0.50 + 0.50*I))
```

The integrity factor keeps a dramatic but badly damaged run from being the best
credit strategy without making style disappear completely.

## Recommended payout formula

For a completed contract:

```text
quality_multiplier =
    0.45
  + 0.30 * I^1.40
  + 0.15 * T
  + 0.06 * C
  + 0.04 * E

ordinary_credits = round_half_up(B * quality_multiplier)
credits_awarded = ordinary_credits + flow_credits
```

Interpretation:

| Component | Share of `B` | Reason |
| --- | ---: | --- |
| Completed delivery | `45%` | protects learning and makes every finish matter |
| Cargo integrity | up to `30%` | primary risk/reward expression |
| Time | up to `15%` | speed matters without dominating condition |
| Clean execution | up to `6%` | acknowledges incidents/resets |
| Efficiency | up to `4%` | lightly rewards line knowledge |
| Optional Flow | up to `6%` extra | celebrates style without requiring it |

`quality_multiplier` lies in `[0.45,1.00]`; Flow raises the absolute maximum to
`1.06B`. Use explicit half-up integer rounding (`floor(x + 0.5)` for
nonnegative values), not host-dependent text formatting.

### Why this model wins

| Model | Strength | Failure |
| --- | --- | --- |
| Credits per metre | instantly legible | circles and detours print currency |
| Pure time trial | exciting ceiling | wall rides and restarts dominate; cargo becomes decorative |
| Pure integrity | cargo matters | optimal play becomes slow crawling |
| Multiplicative condition x time x style | compact | opaque; one weak factor can erase a whole run |
| Single weighted score converted to money | tuneable | completion floor is unclear and badges become transactional |
| **Fixed base plus bounded visible shares** | transparent, forgiving, exploitable inputs capped | needs one results breakdown, which is desirable anyway |

## Grade model

Use the same quality terms rather than inventing a second unrelated score:

```text
Q = 100 * (
      0.30 * I^1.40
    + 0.15 * T
    + 0.06 * C
    + 0.04 * E
  ) / 0.55
```

Flow and the `45%` completion share are excluded. Apply the first eligible row:

| Grade | Quality | Additional gate |
| --- | ---: | --- |
| `S` | `Q >= 92` | `I >= 0.92`, no reset |
| `A` | `Q >= 80` | `I >= 0.78` |
| `B` | `Q >= 64` | `I >= 0.55` |
| `C` | `Q >= 48` | none |
| `D` | otherwise | completed, but compromised |

Any reset caps the final grade at `B`, even if the numerical result is higher.
It does not block first completion, Credits, or Reputation. This prevents reset
teleports from producing prestige grades while letting a struggling player
finish.

Badges are orthogonal observations:

- `PERFECT CARGO`: `I >= 0.99`;
- `CLEAN LINE`: no brush, hard impact, or reset;
- `ON PARCEL TIME`: elapsed at or under par;
- `FLOW`: `F >= 1`; and
- route-specific Hop/shortcut badges only after those interactions are tested.

## Deterministic scenario table

The following uses `B=120` and the exact recommended formulas. It is suitable
as the first golden-vector fixture for a future pure scoring test.

| Scenario | `I` | time/par | hard / brush / reset | distance/ref | `F` | `Q` | Grade | Credits |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | ---: |
| Near-perfect flowing run | `0.99` | `0.90` | `0 / 0 / 0` | `1.03` | `1.00` | `97.33` | `S` | `125` |
| Clean par run | `0.95` | `1.00` | `0 / 0 / 0` | `1.10` | `0.25` | `90.31` | `A` | `116` |
| Typical learner finish | `0.78` | `1.25` | `1 / 1 / 0` | `1.22` | `0.15` | `65.19` | `B` | `98` |
| Damaged but delivered | `0.42` | `1.55` | `2 / 2 / 0` | `1.35` | `0.10` | `32.26` | `D` | `76` |
| Reset recovery | `0.70` | `1.70` | `1 / 1 / 1` | `1.55` | `0.20` | `44.10` | `D` | `84` |
| Circle-farming attempt | `0.95` | `2.40` | `0 / 0 / 0` | `2.50` | `1.00` | `62.40` | `C` | `102` |

The farming attempt can reach the Flow cap only in this deliberately hostile
synthetic record. Its payout is still below a clean par run and its credit rate
per minute is far worse. The real unique-chainage rule should prevent `F=1`
from circles at all.

## Base contract values

Base value is an integer contract-authoring field. A useful initial sanity seed
is:

```text
B_seed = nearest_5(40 + 0.25*D_ref + 40*K)
```

`K` is a declared complexity value `[0,1]` covering fragility, route demand,
and stop structure. It is not inferred from the player's behavior. After
playtesting, store the selected integer and never recalculate it mid-run.

### Three-contract slice

| Contract | Origin -> destination | Route rule | Profile | `D_ref` | `K` | Seed par | `B` |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: |
| Familiar Parcel | `MRK -> WRK` | `L6` | Rugged | `118.071 m` | `0.10` | `23 s` | `75` |
| Cross-Market Glass | `DEP -> CLN` | `L1 + L2` | Fragile | `258.860 m` | `0.45` | `43 s` | `125` |
| Eastline Sealed Express | `RLY -> CLN` | required `A2`, cross `GE`, then reverse `L3` | Standard / express | `514.604 m` | `0.65` | `43 s` | `195` |

The par values are intentionally labelled seeds. The familiarization tests the
interaction, Cross-Market tests condition and braking through tighter routes,
and Eastline gives Drive and long drifting room to matter. `GE` is a gate, not
a destination pad: it is only the declared intermediate checkpoint where `A2`
hands the sealed run to `L3`. Completion occurs at the real `CLN` destination.
The exact reference sum is `442.281945 + 72.321850 = 514.603795 m`, displayed
as `514.604 m`.

At the typical-learner record in the scenario table, expected awards are
approximately `62`, `102`, and `160` credits. A clean result pays close to the
published base; perfection adds only the capped Flow amount.

For the first owner playtest, expose all three contracts and simulate unlock
events rather than withholding test coverage behind progression.

## Reputation and Credits

### Keep exactly two progression concepts

- **Reputation** is never spent. It answers, “What work trusts this courier?”
- **Credits** are spent on paint and trails. They answer, “How does this courier
  want the craft to look?”

Do not add parts tokens, trail shards, premium currency, fuel, repair bills,
maintenance fees, or random loot. Grades, badges, and personal bests are records,
not wallets.

### Reputation award

```text
reputation = tier_completion + grade_bonus + first_clear_bonus
```

| Contract tier | Completion Reputation |
| --- | ---: |
| Local | `8` |
| District | `12` |
| Specialist | `16` |

| Grade | Bonus Reputation |
| --- | ---: |
| `D` | `0` |
| `C` | `1` |
| `B` | `2` |
| `A` | `4` |
| `S` | `6` |

The first successful clear of a contract adds `6`. Reputation is never lost.
Suggested gates after the loop proves itself:

| Reputation | Opens |
| ---: | --- |
| `0` | familiarization and two local jobs |
| `30` | district-standard, fragile, and first express jobs |
| `75` | multi-stop and declared no-reset variants |
| `140` | mastery variants and prestige cosmetic stock |

An A-grade first clear of two local jobs yields `36`, so a capable player opens
the district after two jobs. Two D first clears yield `28`; one ordinary repeat
opens it. Skill accelerates access slightly, but imperfect play never stalls.

### Cosmetic earning cadence

The companion cosmetics study defines one ordinary respectable standard payout
as `S`. Under this model, with a standard base near `125`, `S` is approximately
`95–105 credits`. Convert its selected relative prices as follows, then retune
all prices together if observed `S` changes:

| Reward | Availability | Launch price target |
| --- | --- | ---: |
| District Standard / Trail Off | start | free |
| first choice of Orchid / Saltglass / Ember | first familiarization clear | one free choice |
| each remaining launch paint | after familiarization | `80` |
| Twin Vector | after first standard clear | `160` |
| Courier Pulse | after two clears | `190` |
| Comet Ledger | after A or high-integrity result | `220` |

This means:

- the first delivery changes the vehicle immediately;
- one respectable standard job nearly buys a remaining paint;
- roughly two standard jobs buy a trail;
- the five paid launch items total `730` credits, roughly seven to nine ordinary
  successful jobs rather than dozens; and
- a player who dislikes progression can keep District Standard and Trail Off
  without a statistical disadvantage.

Target cadence by contracts, not by an assumed session duration: this compact
district can produce much shorter runs than a large open world. The first paid
choice should take no more than two ordinary completions and the first trail no
more than three after familiarization.

### Economy guardrails

- Never charge for retry, repair, reset, repainting to an already owned finish,
  or changing equipped cosmetics.
- Never remove Credits or Reputation on failure/abandon.
- No random stock, duplicate items, rotating scarcity, or escalating prices.
- Every item previews on the actual R7 visual rig before purchase.
- Unlocking stock and affording it are separate, but neither should require an
  unexplained hidden achievement.
- A future save writes ownership and balances atomically. The first loop
  playtest should use session-only progression until the economy feels good.

## Exploit and frustration audit

| Risk | Guard |
| --- | --- |
| Driving circles for distance money | `B` and `D_ref` are authored; `D_actual` can only reduce a `4%` bonus |
| Donuts for drift money | count unique forward route-chainage bins once; Flow caps at `6%` |
| Slow crawling for perfect cargo | time supplies up to `15%`, while microcontacts are ignored |
| Wall riding for fast time | integrity and cleanliness use contact-episode peak severity |
| One sustained contact damages every tick | incremental peak-loss episode aggregation |
| Higher physics rate changes cargo loss | episode result depends on peak severity, not sample count |
| Reset teleport shortens a route | exclude teleport distance, mark assisted, zero later Flow/efficiency across discontinuity, cap grade at `B` |
| Accepting near the destination | offers load only at authored origin pads |
| Re-entering delivery zone pays twice | atomic terminal state plus unique run ID payout ledger |
| Repeating first-clear Reputation | persistent/session first-clear bit per contract ID |
| Pausing to preserve score while moving | pause freezes both physics and timer; no movement occurs |
| Results rounding changes payout | compute from clamped raw record; explicit half-up integer rule |
| Off-route shortcut earns extra base | base never changes; efficiency caps at full |
| Very slow damaged run becomes worthless | `45%` completion share remains |
| Best grade requires drifting | Flow is outside `Q`; straight perfection can earn `S` |
| Currency buys easier physics | cosmetics have no gameplay fields or influence |

## Deterministic implementation tests

Before owner tuning, implement payout and integrity as pure functions and lock
these behavioral properties:

1. **Bounds:** all finite inputs produce `I,T,C,E,F` in `[0,1]`; ordinary
   multiplier stays in `[0.45,1.00]`.
2. **Monotonic integrity:** holding other inputs constant, greater `I` never
   lowers Credits or grade score.
3. **Monotonic time:** a lower elapsed/par ratio never lowers `T` or Credits.
4. **No odometer reward:** increasing `D_actual` cannot increase payout.
5. **Shortcut cap:** any `D_actual <= D_ref` gives exactly `E=1`, never more.
6. **Flow cap:** any amount beyond target leaves `F=1`; a credited chainage bin
   cannot be credited twice.
7. **Straight S:** a perfect no-Flow record can reach `S`.
8. **Episode rate invariance:** synthetic 30/60/120 Hz streams with the same
   peak severities yield the same integrity to a declared small tolerance.
9. **Peak increment equivalence:** charging peaks `0.2 -> 0.5 -> 0.75` equals
   charging one episode whose terminal peak is `0.75`.
10. **Microcontact immunity:** episodes below `0.15` alter neither `I` nor `C`.
11. **No landing double charge:** one contact/landing identity creates one loss.
12. **Discontinuity:** reset displacement adds no actual distance or Flow bin.
13. **Reset grade cap:** a numerically perfect assisted record is at most `B`.
14. **Completion floor:** a completed zero-integrity, zero-time-factor,
    zero-cleanliness, zero-efficiency run receives exactly rounded `0.45B`.
15. **Atomic award:** completing/evaluating the same run ID twice changes
    balances once.
16. **Reputation separation:** buying/equipping cannot change Reputation;
    earning Reputation cannot spend Credits.
17. **Cosmetic neutrality:** equipped paint/trail ID cannot enter any scoring
    input or contract registry calculation.
18. **Golden scenarios:** reproduce the six rows above exactly.

Runtime checks should additionally prove that contract observation never writes
craft velocity, transform, `fold_amount`, input, collider, probes, tuning,
terrain, route data, or camera state.

## Tuning plan

### Pass 1 — interaction only

Expose all three contracts with economy persistence disabled. Test pickup,
arrival, result clarity, and retry. Ignore whether prices feel perfect. Success
means the loop can be completed without reading technical instructions.

### Pass 2 — integrity calibration

Record representative events:

- clean long drift with no contact;
- shallow brush;
- ordinary wall strike;
- severe Drive strike;
- supported Hop and clean landing;
- hard landing; and
- sustained wall contact.

Verify drift and clean Hop produce zero damage, then tune only `L_max`, episode
continuity, and severity category boundaries. Do not retune craft impacts to fit
the cargo model.

### Pass 3 — par and grade

Run each contract five times after learning it. Select par from observed runs,
then verify:

- a comfortable clean run tends toward `A`, not automatic `S`;
- a learning run with one meaningful error tends toward `B` or `C`;
- `S` requires a genuinely strong run but not one exact route;
- missing par does not feel like failure; and
- reset recovery remains worth finishing.

### Pass 4 — earning cadence

Simulate ten deliveries with the observed grade mix. Check:

- first free paint appears after familiarization;
- first remaining paint takes at most two ordinary successes;
- first trail takes about two standard successes;
- no item requires repeating one optimal job far more than alternatives; and
- total launch catalogue is reachable in roughly `7–12` successful jobs.

Retune base values or the entire price scale, not one item designed to drain a
temporary surplus.

### Pass 5 — Flow falsification

Try intentionally to farm Flow with donuts, reversals, leaving/re-entering one
route bin, reset teleports, low-speed steering, and wall contact. If unique
chainage proves too constraining for the enjoyable drifts, keep Flow as a badge
only for the first slice rather than weakening its anti-farm proof.

## Human-feel questions automation cannot answer

- Does cargo integrity add exciting stakes or make the player afraid to use the
  joyful Drive drift?
- Does the `45%` completion share feel generous or make condition irrelevant?
- Are results understandable without mentally parsing five bars?
- Does a soft par invite a second attempt without turning free roam into a race?
- Does the arrival settle feel satisfying, or merely interrupt momentum?
- Is Flow recognition delightful, distracting, or exploitable?
- Does the first free finish make the reward loop immediately tangible?
- Is one trail after roughly two standard jobs aspirational enough without
  feeling withheld?
- Do Reputation and Credits read as distinct purposes, or as unnecessary dual
  currencies?

## Final study decision

Proceed with a three-contract, session-only reward slice using the recommended
fixed-base formula. Keep cargo abstract, timers soft, delivery always
recoverable, and results transparent. Use Reputation to reveal work and Credits
to purchase only the three selected paints and three selected trails. Make the
first paint choice free, target a first paid paint within two completions, and a
first trail within about two standard completions.

Treat the cargo episode curve, seed par times, arrival speed/dwell, and Flow
eligibility ranges as bounded tuning fields for owner play. Keep movement,
terrain, routes, camera, and vehicle physics frozen while tuning them. Do not add
performance upgrades until this loop proves that the existing movement remains
fun when something is at stake.
