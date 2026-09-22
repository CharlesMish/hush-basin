# Provisional alpha targets — evidence, not final balance

Accepted starting point: cargo v1.1, including Charlie's positive owner review.
There is no new cargo tuning. Historical P1B is retained research only.

## Three distinct incentives, one per contract

| Job | Advisory route / authored length | Base | Single optional bonus |
|---|---|---:|---|
| Market → Depot / Freight seals | Reverse L1, 129.43 m; open-yard direct line about 123 m | 100 | Style: longest existing BRRR streak ≥0.4 s, +25 |
| Market → Relay / Signal spares | Reverse L5 + reverse L4, 247.80 m; west sweep alternative 523.62 m | 150 | Express: active delivery time ≤55 s, +40 |
| Market → Works / Bench instruments | L6, 118.07 m; northern L5/R0 alternative 305.51 m | 120 | Care: condition ≥75%, +35 |

All endpoints/inner radii are resolved from current `destination_pads`. Suggested
map lines come from the retained route IDs, but neither their length, chainage,
direction nor occupancy enters acceptance or reward. Yard shortcuts are valid.
Depot remains the quick familiarization; its forgiving Style target lets three
jobs represent all three incentives without stacking modifiers. Relay reaches
the northern district and offers longer sweep commitments. Works has an angled
industrial approach and a rough northern alternative; no obstacle was added.
Actual differentiation in human play is still an owner question.

## Sampling method and margins

`alpha_route_study.gd` reads the current baked road arrays, places the unchanged
craft only before each trial, then drives using ordinary input actions. Its
conservative diagnostic driver is not a competent-human/optimal-line model.
Source geometry, controller, impact response and BRRR are unchanged.

The initial study completed Depot direct in 9.03 s (2.067 s longest BRRR streak)
and road in 11.97 s (0.483 s streak), with 100% condition. The 0.4 s Style target
fits both samples with room for the direct line. It intentionally introduces
BRRR gently rather than requiring a sustained stunt. The metric still requires
Drive at ≥20 m/s, using the unchanged existing BRRR formula.

Relay spine completed in 20.97 s; the longer west sweep in 41.20 s. Both had
100% condition. 55 seconds adds roughly 34% over the slower successful sample,
including arrival margin. It is a visible reference, not a deadline; the clock
counts up, paused time does not count, and missing it still pays all 150 base.

Works Way completed in 10.07 s, 100% condition. The loop fixture also completes
the northern rough alternative cleanly in about 40 s. A 75% Care target allows
one maximum 24-point accepted episode from full condition, with another point
of margin. Ordinary rough support does not itself damage cargo. There is no
new fragile model, time requirement or hidden impact-count condition.

The initial automated east approach via Clinic/GE/L7 stalled against existing
geometry near (166,4) and ended at 99.5% condition. Its failed 120 s trace is
retained. It is not a successful sample or evidence that this route is illegal;
the diagnostic driver cuts turns and is not a route validator. No world repair
was made. The completed northern Works alternative supplies the second driven
approach. All final integration route receipts are retained separately.

## Earnings and exactly one purchase

Base earnings are fixed 100 / 150 / 120; optional awards are fixed 25 / 40 / 35.
One mixed base-only set earns 370; with all bonuses, 470. A 400-Credit liner is
therefore about three ordinary mixed deliveries with some bonuses or four
base-only deliveries (also four base-only Depot repeats). Successful repeats
pay the same amounts. There is no cargo/time/style multiplication or other term.

The liner reduces the accepted nominal cargo bill by 25%, rounded to the nearest
0.1 condition point, before clamping to remaining condition. A maximum episode
falls from 24 to 18 points; cargo remains damageable and can still reach zero.
Diagnostics preserve nominal raw loss, raw capped loss, nominal/actual protection
reduction and committed loss. At near-zero condition, capping can make the actual
saved amount smaller than the nominal 25% reduction; this is recorded explicitly.

The original v1.1 reducer still owns attribution and grouping. The alpha wrapper
changes only its committed cargo balance. One session receipt ID commits once;
Results/retry/reopen cannot award it twice. No persistent save, debt, shop,
scarcity, diminishing returns, random rotation or future progression promise.
