# Foundation Synthesis

Status: `SELECTED FOUNDATION — HOURLY REFINEMENT ACTIVE`

This is the first convergence of the gameplay-loop, payout, cosmetics, route,
and implementation studies. It is deliberately not final authority and does
not modify R7.

## The game

District Zero becomes a momentum-courier game:

> Choose work at the pad where you are, carry it across the real district,
> preserve cargo by avoiding meaningful impacts, settle deliberately at the
> destination, then turn the result into visible expression for the craft.

The contract makes an already-good drift consequential. It does not replace
the driving with a combo meter or punish the craft simply for being sideways.

## Minimum complete loop

```text
FREE ROAM AT PAD
  -> DISPATCH (paused preview)
  -> WAITING FOR NEUTRAL
  -> ACTIVE DELIVERY
  -> DELIVERY SETTLE
  -> RESULT COMMIT
  -> RESULTS / REWARD
  -> CONTINUE AT DESTINATION

ACTIVE DELIVERY / DELIVERY SETTLE
  -> ABORTED on reset
  -> FREE ROAM after acknowledgement
```

- Dispatch opens only while supported and slow inside the pad's existing
  `8 m` inner-flat area.
- Accepting a local offer loads cargo. The timer starts on the first unpaused
  physics tick after the modal closes and every gameplay control returns
  neutral. There is no separate pickup dwell or start-arming subgame.
- Delivery requires support, the destination inner pad, no more than an initial
  `6 m/s`, and a provisional continuous `0.50 s` settle. Native interaction
  play compares bounded `4/6/8 m/s` and `0.35/0.50/0.60 s` candidates rather
  than pretending these seeds are already feel authority.
- The player stays at the reached destination. Its board provides the next
  work; contracts are a connected journey, not teleported stages.
- Late, damaged, and zero-integrity deliveries still resolve in the first
  slice. Hard-failure variants come later and must advertise themselves.

## Launch contract chain

### C01 — Market Parcel

- `MRK -> DEP`
- open route; suggested reverse `L1`
- `129.429845 m`
- shared proof cargo / familiarization
- teaches the entire interaction and grants one launch-finish choice

### C02 — Relay Window

- `DEP -> RLY`
- open route; suggested reverse `L0`, then `A1`
- suggested-path distance `394.186048 m`
- same forgiving cargo profile as C01
- makes the long west sweep and the vehicle's committed drift the star

Distance alone does not establish that a route is economically irrational:
A1 may be faster, safer, or simply more enjoyable than the shorter inner path.
Observe human time and incident evidence before authorizing a route seal.

### C03 — Clinic Glass

- `RLY -> CLN`
- open route; suggested `L4 + L5 + L2` (`377.225159 m`)
- declared outer alternative `A2 + reverse L3` (`514.603795 m`)
- same forgiving cargo profile as C01/C02
- asks whether a shorter technical line or a longer fast sweep preserves more
  condition for this player

Actual distance is a receipt fact only. The outer line may trade length for
pace, condition, or joy; the first-slice result never calls that choice invalid
or lowers pay merely because it was longer.

Later authored work should give X0 and the South HOP/DOG pair their own sealed
or multi-stop reason. Endpoint-only contracts do not naturally select them.

## Cargo integrity

Cargo is an abstract deterministic observer, never a rigid body or movement
modifier.

- Read `impact_count` and normalized impact severity from the existing craft
  snapshot after the controller's physics update.
- Open an impact episode on a new count and hold it across a provisional
  `0.25 s` quiet gap.
- Charge only the increase in the episode's peak damage curve.
- Never charge from speed, Drive state, transform, sideslip, ordinary braking,
  clean Hop, or clean terrain following.
- The three proof jobs share one forgiving response curve so route feel is the
  variable under study. Standard/Express/Fragile remain researched later
  contract families, not simultaneous MVP variables.

The first calibration gate is not a reward number. It is evidence that a clean
long drift, normal Hop, and ordinary route travel each lose exactly `0%` cargo
while recognizable impacts produce legible, non-random differences.

## Payout and grade

Every contract freezes an integer base `B`, a par, and an authored reference
distance before the run starts.

```text
first-slice payout share
  50% completion
  35% integrity
  15% soft pace
```

- Components are additive and shown separately.
- Late time bonus decays smoothly to zero; there is no routine timeout.
- Actual distance, incidents, Hop/form use, Flow, paint, and trail never enter
  first-slice money. They may appear as receipt facts or badges.
- Grade reuses the quality components and never multiplies money a second time.
- `B`, par, and prices remain scenario seeds until complete human runs establish
  interaction-to-interaction duration and fair Credits per minute.

The economy study's five-line formula and capped Flow credit remain documented
challengers, not first-slice authority. Flow is initially a post-run badge and
improves pace naturally. If owner play says the receipt fails to notice the
game's defining pleasure, test the unique-forward-chainage collector later;
never pay raw drift seconds or donuts.

## First-slice reset rule

R/fall during an active or settling delivery aborts the attempt, awards
nothing, clears observer state, and returns to free roam through the unchanged
R7 reset path. This is technically honest and avoids pretending an attempt can
continue across a counter-clearing MRK teleport. It is also a major human-feel
risk: if one late abort makes the player unwilling to retry, stop and design a
real recovery/checkpoint feature in its own bounded pass.

## Reward bridge

Credits eventually buy only presentation. Reputation remains a researched
later option; it has no necessary job while all three proof contracts are
exposed and progression is session-only.

Researched launch palette:

- paint: Orchid Static, Saltglass, Ember Relay;
- trails: Twin Vector, Courier Pulse, Comet Ledger;
- permanent accessibility defaults: District Standard and Trail Off.

Authorized proof reward:

- District Standard plus two cue-safe paint finalists;
- one free choice after C01, with immediate equip or keep-default;
- session Credits displayed after C02/C03 but no shop yet; and
- no trail until the three-job loop passes its owner feel gate.

Paint affects explicit shell/frame/lift/trim/can roles. It never overwrites the
dynamic energy/nozzle cue or dark bore. Trails share one bounded render-history
core, stay low and behind the craft, depth-occlude behind walls, clear on reset,
and provide Trail Off plus reduced-motion behavior.

## Smallest implementation sequence

1. New P1B scene around byte-identical R7 movement/world/camera files.
2. Pure catalog, state, integrity-episode, payout, and profile reducers with
   boundary tests.
3. C01 only: dispatch, active HUD, delivery settle, results, and
   session-only award.
4. Owner interaction/condition playtest before adding breadth.
5. C02/C03, session Credits, and two proof paint finalists.
6. Owner whole-loop playtest.
7. Select exactly one felt-missing expansion: trail, sealed/HOP job, Flow
   recognition, small shop, Reputation, or durable save.

Do not build a shop, quest framework, procedural board, physical cargo, save
migration, or mechanical upgrades before the one-contract loop is fun.

## Foundation proof already present

- deterministic 15-pair route analysis;
- deterministic six-case payout model;
- 33 passing design-lab graph/math checks across the broad and minimum payout
  challengers (not Godot gameplay or feel proof);
- complete gameplay, economy, cosmetics, and feasibility studies;
- a hashed three-direction cosmetic concept sheet; and
- an hourly eight-pass refinement agenda.

The only product-facing next step after convergence is a fresh, explicitly
authorized P1B successor. The verified R7 player remains untouched.
