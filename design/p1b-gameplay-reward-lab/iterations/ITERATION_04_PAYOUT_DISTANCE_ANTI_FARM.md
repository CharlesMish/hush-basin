# Iteration 04 — Payout, Distance Valuation, and Anti-Farming

Heartbeat started local: `2026-08-26T04:10:48-05:00`

Completed local: `2026-08-26T04:36:00-05:00`

Status: `BOUNDED DESIGN ITERATION — NO PRODUCT CHANGE`

## Decision refined

Select `VERSIONED_DURATION_RATE_BASE_V1` as the base-value authoring seed while
preserving the already-selected three-line runtime payout:

```text
Credits = round_half_up(B * (0.50 + 0.35 * integrity + 0.15 * pace))
```

`B` is a literal positive integer shown on the offer and frozen at acceptance.
It is never recalculated during an attempt. Every genuinely new successful
delivery earns its full ordinary receipt; abort and invalid observation earn
zero.

This iteration answers how contracts with very different durations can be
worth comparable effort without turning the odometer, route choice, or repeat
count into money.

## Authoring a base from learned duration

Do not price from route metres. For each contract, reuse the iteration-03
human calibration cohort and keep two time values deliberately separate:

```text
M = median active time of five consecutive learned valid completions
V = round_half_up_to_0.1s(M)              # valuation duration
P = ceil_to_0.1s(1.10 * M)                # generous pace reference

B_raw = R * (V + H) / 60s * (1 + 0.075*K)
B = round_half_up_to_one_Credit(B_raw)
```

Provisional global authoring seeds:

- `R = 100` base Credits per reference cycle minute;
- `H = 12.0 s` common interaction/cadence allowance; and
- `K = 0` for every initial open endpoint contract using the shared cargo
  profile.

`R` and `H` are global scale seeds, not per-contract fudge factors. `V`, `P`,
and `B` become versioned catalog literals after calibration. Raising `P` to be
more generous may not raise `V` or `B`; otherwise a tuning change would silently
mint currency.

### Complexity premium

The bounded class `K` is prospective, visible authority only:

| `K` | Base premium | Allowed reason |
| ---: | ---: | --- |
| `0` | `0%` | initial open endpoint work |
| `1` | `7.5%` | one machine-enforced visible fragile, sealed-route, or multi-stop burden |
| `2` | `15%` | a declared combination of two such burdens |

Distance, road shape, highlighted route, player reputation, chosen line,
cosmetics, author intuition, and observed performance cannot justify `K`.
Higher classes remain unavailable until those contract families exist and can
actually fail their advertised rule.

### Illustrative vectors, not contract values

| Learned median `V` | Pace reference `P` | `K=0` base `B` | Learned clean award (`95%`) | Learned clean rate |
| ---: | ---: | ---: | ---: | ---: |
| `30.0 s` | `33.0 s` | `70` | `68` | `97.14 Cr/min` |
| `60.0 s` | `66.0 s` | `120` | `116` | `96.67 Cr/min` |
| `90.0 s` | `99.0 s` | `170` | `165` | `97.06 Cr/min` |

At par the same examples award `66 / 113 / 161`. A typical `90%` condition,
`1.25x` run awards `61 / 105 / 149`. Across valuation durations from `20.0` to
`180.0 s` in `0.1 s` increments, the deterministic learned-clean rates remain
between `95` and `99 Cr/min`, under a `4%` spread.

These numbers prove arithmetic behavior only. No C01/C02/C03 `M`, `V`, `P`, or
`B` is frozen before complete human interaction evidence.

## Why distance is a receipt fact only

The money evaluator has an exact input whitelist:

```text
terminal
contract_id + frozen definition hash
base Credits B
integrity units
active elapsed milliseconds
pace reference milliseconds
scoring version
```

It has no field for actual distance, authored route length, route ID, traversal,
Flow, odometer, Hop, form duty, grade, paint, trail, completion count, or repeat
count. Those may be immutable result facts but cannot enter money.

Consequences:

- circles, reversals, and detours cannot increase `B` and ordinarily reduce
  only the bounded pace share;
- a valid shortcut can improve pace only until the full-bonus cap; it can never
  pay above `B`;
- C03's inner and outer families use the same offer, `B`, and payout function;
- changing or highlighting a suggested route cannot rescore an accepted run;
- teleport displacement never becomes distance value; and
- no route-efficiency, cleanliness, or Flow payment is reintroduced under a
  different name.

The offer may show a descriptive authored distance. Results may show actual
distance as `Run details`. Neither is a rate or multiplier.

## Repeats and the rejected finite-pool idea

A genuine repeat is genuine work and receives its full ordinary receipt. There
is no diminishing return, cooldown, daily cap, rotating bonus, repair fee, or
repeat tax. Rate imbalance is repaired in versioned `B` literals after evidence,
not hidden in player state.

This pass explicitly rejects a finite “best receipt tops up a contract pool”
challenger. It blocked infinite farming, but a worse repeat would visibly total
a positive Delivery + Condition + Pace receipt and then award zero. An
improvement would award only the delta. That contradicts iteration 03's rule
that the three displayed lines equal the one atomic award and makes normal
completion harder to understand. One-time mastery reserves could be researched
later as a separate unlock system, never disguised as ordinary pay.

## Atomic award and entitlement ledgers

At acceptance, freeze the contract/scoring hash, literal `B`, literal `P`,
weights, and pace curve into the attempt snapshot. One active attempt uses a
key `(session_epoch, monotonic_sequence)`.

On terminal:

1. reset/abort wins a same-tick delivery race;
2. reduce the final cargo observation;
3. build one canonical immutable receipt;
4. verify its hash, line sum, bounds, contract identity, and scoring version;
5. commit its balance delta once; and
6. render only the committed record.

An identical duplicate terminal is `DUPLICATE_NOOP`. Reusing an attempt key
with different terminal, evidence, components, hash, or value is
`LEDGER_CONFLICT`; it is never silently clamped or accepted. Skipped, reused,
wrapped, blank, or overflowing attempt sequences stop. A balance overflow stops
without consuming the transaction or mutating the prior balance.

Continue and the conditionally authorized `RESTART AT <ORIGIN>` cannot award,
revoke, or recompute anything. Only a fresh Dispatch/Accept allocates the next
attempt.

The first C01 paint choice uses a stable reward-entitlement ID in a separate
one-shot ledger. It is not in ordinary Credits or Session Best Receipt. A
scoring-version change may start a new comparison table, but it may not grant
the same cosmetic again.

Because the proof has no save file, app closure discards an active attempt
without award. If session state is reset, balance, attempt namespace/ledger,
first-clear claims, best receipts, owned/equipped session cosmetics, and active
attempt must reset together. Preserving balance while forgetting its award
ledger is forbidden.

## Rounding contract

Terminal evidence uses integer integrity units and integer active time. Payout
uses exact deterministic decimal/rational arithmetic with one nonnegative
half-up rounding of the raw total. The visible Delivery, Condition, and Pace
lines use stable largest remainder, ties `Delivery -> Condition -> Pace`, so
they sum exactly to the committed integer.

Never independently round three lines, use banker's rounding, rescore from UI
strings, or clamp a corrupt receipt into validity.

## Truthful remaining rate risks

The static model is deliberately not labeled wall-ride-proof.

### Maximum-episode wall pressure

The selected cargo seed leaves `76%` integrity after one maximum-loss episode.
At full pace (`r=0.85`), that synthetic record is about `0.25–0.29 Cr/min`
above the learned-clean comparator in the illustrative 60/90-second cases. It
is below the 30-second comparator. The difference is small but real.

Only exact-engine hostile driving can show whether sustained wall pressure can
actually obtain that time while paying only one episode. Capture clean learned,
fast wall-pressure, intentional low-condition speedrun, and direct clean
full-pace strategies on every initial job. If the repeatable damaged strategy
beats respectable play, stop. Do not weaken episode fairness, add scrape ticks,
or hide a repeat penalty; reconsider payout weights or the gameplay observation
in a separate bounded decision.

### Interaction allowance

`H=12 s` currently does much of the short-job normalization. If measured repeat
interaction overhead is only `4 s`, the illustrative short/long learned-clean
rate spread becomes `13.94%`, close to the `15%` stop band. Measure complete
Accept-to-next-fresh-Accept-ready cycles separately for destination Continue
and explicit restart. Target `<=5%`; stop above `15%`. Re-author/version the
global scale and literal bases rather than paying metres.

### Early abort pressure

After a maximum cargo episode, abandoning for a hypothetical perfect rerun can
improve raw rate only if the incident happened in roughly the first `9.2%` of
the trip. This is a review metric, not a reset fee. Capture whether players
naturally exploit or feel pushed by it before changing abort semantics.

## Paint contribution — Fixed Measure

One original matte drafting-ink/stone finish:

| Role | Color | Emission ceiling |
| --- | --- | ---: |
| Frame | `#171B1C` carbon ink | `0.12` |
| Shell | `#3E4947` graphite sage | `0.21` |
| Lift | `#ADA690` measured stone | `0.34` |
| Underlay | `#29313A` blue-black drafting slate | `0.18` |
| Trim/seams | `#D9D8CC` paper ivory | `0.46` |
| Drive can | `#626B68` oxidized nickel | `0.24` |
| Derived joint target | `#2B3030` | `<=0.18` |

Native metallic/roughness and every functional material/cue remain fixed. The
profile is immutable while equipped and has zero inputs from payout, balance,
grade, cargo, time, route, odometer, completion, or retry. Reward copy may call
it `a deliberately issued matte finish`; never `fairer`, `balanced`,
`efficient`, or any implied stat advantage.

Reject if native Spread/mid/Drive captures collapse into fewer than three
grayscale masses, ivory clips or blooms, the dark silhouette disappears,
functional cue priority falls, CVD review confuses caution/strike, a role
exceeds its ceiling, reserved material hashes change, or movement trace delta
is nonzero.

## Trail contribution — Paired Proof

One finite `MultiMeshInstance3D` of simultaneous mirrored diamond pairs:

- 24 instances maximum: 12 port/starboard pairs at `-0.115/+0.115 m`;
- each camera-facing diamond is `0.050 x 0.050 m`, two triangles;
- pair centers every `0.78 m` of private visual-history chord accumulation;
- maximum `0.48 s` or `9.36 m`, sample at most `30 Hz`;
- paper ivory `#D9D8CC` and quiet sage `#879B96`, swapped by pair ordinal;
- alpha `<=0.40` at head, monotonically to exactly zero at tail;
- one fixed buffer/material, 48 triangles maximum, no RNG or per-frame
  allocation;
- depth test on; depth write, shadow, GI, lights, collision, particles,
  forward projection, and gameplay query off; and
- reset/scene change/invalid craft/generic clear or one-frame jump `>8 m`
  clears before render; pause freezes.

Its private chord history is unsaved and unavailable to contracts. It is not
the gameplay odometer. Reduced motion uses at most six neutral-ivory pairs,
`1.40 m` spacing, `0.22 s`, alpha `<=0.18`; Trail Off stays free.

Reject if it resembles a route/lane/checkpoint/tally, survives relocation,
renders through a wall, shimmers across common frame rates/speeds, occupies
`>=3%` of `1280x720`, competes with the nozzle, grows during a ten-minute soak,
exceeds `0.20 ms` median or `0.45 ms` p95, changes movement, or imports any
economy/route state.

Visual mockup: `concepts/ITERATION_04_FIXED_MEASURE_PAIRED_PROOF.svg`  
SHA-256: `c94a26034896722a7488d86d7806ac07ac77a458f6641897458c2959ccf768ff`

## Deterministic evidence

Command:

```text
PYTHONPATH=tools python3 -B tools/test_iteration_04_payout.py \
  --report analysis/ITERATION_04_PAYOUT_REPORT.json
```

Result: `105/105 PASS WITH NATIVE RATE FALSIFIERS REMAINING`.

Report SHA-256:
`147a57a923aaee4f481d2d279a917b0d9d5925b1e718526e592c4f06aab5ba8e`

The vectors cover exact pace anchors, duration/base authoring, half-up sentinels,
complexity authorization, accepted-snapshot immutability, scoring whitelist,
all-unit integrity and elapsed monotonicity, exact-sum receipts, abort/invalid
zero, global duration-rate grids, duplicate and altered-terminal handling,
attempt sequencing/overflow, forged receipt rejection, balance overflow,
separate first-clear entitlement, detour/shortcut properties, wall-rate
vulnerability disclosure, and interaction-overhead sensitivity.

The report regenerated byte-identically. It proves arithmetic and ledger
semantics only—not fair human bases, measured cadence overhead, wall-pressure
viability, route enjoyment, native UI comprehension, or Godot transaction
ordering.

## Human and exact-engine falsifiers

Stop before progression pricing if any is true:

1. respectable full-cycle rates differ by more than `15%` across C01–C03;
2. a repeatable damaged/wall-pressure strategy beats respectable play on rate;
3. the shortest job becomes the obvious cosmetic farm under measured overhead;
4. C03's outer route feels economically punished despite being declared legal;
5. the player cannot predict Delivery + Condition + Pace from two receipts;
6. a genuine repeat unexpectedly pays less because it is a repeat;
7. any odometer, route, Flow, grade, or cosmetic change alters fixed `B/I/T`
   money;
8. reset/settle race, result reopen, or altered duplicate changes balance twice;
9. Continue/restart grants Credits or repeats the first-clear choice; or
10. fixed-rate pressure makes the joyful long drift meaningfully less likely.

No product file was changed. R7 remains read-only.

