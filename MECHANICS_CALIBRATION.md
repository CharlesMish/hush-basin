# Mechanics Range v1 — provisional calibration

Baseline: exact public review branch commit
`feb30b6205b6b89ad66a3d6eada2c7b1feb18273`. Owner feedback accepts the loop but
rejects its old challenge calibration. No outside-review numbers were adopted.

## Definitions before / after

| Contract | Review v0.2 | Mechanics Range v1 |
|---|---|---|
| Depot | 0.4 s longest BRRR streak; 100 base +25 | 100 slip BRRR; 80 base +60 |
| Relay | ≤55 active seconds; 150 base +40 | One 6.0 s qualifying BRRR streak; 100 base +200 |
| Works | ≥75% cargo; 120 base +35 | ≥85% cargo; 120 base +35 |

All deliveries remain endpoint contracts. No route/zone membership enters
payment. Base is always paid on successful delivery, including at zero cargo.
Each bonus is one fixed award committed once. A player can invent a legal line
that earns the same evidence elsewhere; there is no promise of route exclusivity
or anti-farming enforcement.

**Slip BRRR** decomposes the existing earned BRRR increment:
`earned_increment × split_degrees / (30 + split_degrees)`. The old metric's
`(1 + split_degrees / 30)` factor already contains that contribution. Total
BRRR, its speed floor, slip clamp and streak multiplier are unchanged. This
separate objective evidence removes the straight-speed contribution; it does
not replace the formula or multiply other rewards.

## Method and complete matrix

48 standalone trials are retained in
`docs/mechanics_calibration_matrix.csv`. Full per-tick/sample evidence remains
in the sibling evidence directory. `mechanics_calibration.gd` starts each trial
at Market with a declared aligned launch heading, then uses ordinary inputs
only. It never writes pose or velocity during a drive. The fixture plans are in
`game/tests/fixtures/mechanics_calibration_plans.json`.

The separate integration suite accepts real contracts and includes ordinary
Spread steering/braking to organize the craft before its intended runs. That
setup counts in active time. `mechanics_lines_v1.json` stores its inputs. These
are reproducible diagnostic drivers, not models of human skill, optimal lines,
or cross-platform deterministic physics. Failed and less favorable trials are
retained. No movement coefficient was changed to make a driver succeed.

| Standalone trial / family | Delivery | Time | Key evidence | Cargo |
|---|---|---:|---|---:|
| Depot direct | yes | 8.93 s | 0.017 slip BRRR | 100% |
| Depot road | yes | 11.30 s | 1.24 slip BRRR | 100% |
| Deliberate 1.0 s steering pair | yes | 7.78 s | 64.02 slip BRRR | 100% |
| Deliberate 1.2 / 1.4 / 1.6 s steering pairs | yes | 6.25 / 5.62 / 8.78 s | 91.68 / 124.83 / 163.73 slip BRRR | 100% |
| Overextended 2.0 s steering pair | yes | 10.68 s | 252.27 slip BRRR | 77.7% |
| Relay conservative interior | yes | 19.00 s | 0.73 s longest streak | 100% |
| Relay interior north-straight burst | yes | 21.35 s | 2.28 s longest streak | 100% |
| Relay straight north attempt | no, 70 s limit | — | 0.93 s streak; blocked by existing geometry | 76% |
| Relay premature interior commitment | no, 70 s limit | — | 6.33–6.37 s streak accumulated amid repeated collisions | 0% |
| Relay outer, late/simple setup | yes | 31.47–36.17 s | 3.40–8.77 s streak; substantial impacts | 65.6–78.2% |
| Relay outer, anticipated 27 m/s input target | yes | 32.13–32.57 s | 5.50–6.30 s streak | 92.5–99.8% |
| Works road-following side-pass | yes | 9.25 s | Spread, no Hop; went around end | 100% |
| Works direct across-bar hot Drive | no, 60 s limit | — | stopped at bar under sustained pressure | 76.1% |
| Works direct across-bar early / middle Hop | yes | 8.95 / 8.85 s | deliberate early Spread + supported Hop | 100% |
| Works direct across-bar late Hop | yes | 8.47 s | impact spent Care bonus | 77.3% |
| Works direct across-bar Spread without Hop | yes | 12.22 s | contact/capsule recovery, not a clean crossing | 77.7% |
| Works northern bypass | yes | 23.12 s | no new obstacle encounter | 100% |

The numerical matrix is authoritative for individual trials; the family ranges
above summarize them. The initial pre-matrix probe used the wrong controller
property name and was rejected rather than counted as calibration.

## Why these targets

**Depot 100:** above the straight/road controls and the short 64/92-point steering
experiments, below the clean 125/144/164-point deliberate variants. It asks for
a purposeful drift but not the overextended 252-point contact. No yard furniture
was necessary. The actual contract integration repeats the deliberate maneuver
with its setup included and records the earned receipt.

**Relay 6 seconds:** well above the completed short-route controls, near the
repeatable outer-line runs. The selected anticipated line produces about 6.28 s
at a 27 m/s diagnostic input target with a minor glance (about 96% cargo). This
does not claim a spotless full sweep. Early organization matters: simply holding
Drive late produced larger impacts, while other anticipation choices missed the
streak. The current outside wall already provides tension. No new hazard was
added. An interior driver can farm a streak while repeatedly colliding, but those
trials did not deliver; farming remains a known property of the seed metric.

**Works 85%:** one accepted maximum episode costs 24 condition points without
the liner, 18 with it. Either spends this bonus from full condition; the liner
still helps subsequent delivery condition. A minor glance can retain the bonus.
The service crossing is sampled at 65% of authoritative L6, not copied world
coordinates: 10 m wide, 1.8 m deep, 1.14 m above local ground. One shared box
defines visible structural geometry and collision. An advance marking is 35 m
earlier on L6. Top cover/bands are thin cosmetics. Existing terrain and old
collision are unchanged. Probe exceptions use the existing hard-obstacle pattern.

The feature does **not** require Hop on every legal line. Its end and the northern
bypass remain open. Early standalone "Hop" trials actually skimmed its end;
position traces exposed this, so separate across-bar trials were added. The live
contract test now proves Hop success across the solid and hot-hit recovery to base-only
delivery. A conservative side-pass is an accepted option, not a verification
failure or grounds to fill more of the road.

The direct test crosses toward the bar's left end, not its exact midpoint:
the movie trace is 4.1–4.6 m from the center within the 5 m half-width. The hot
control strikes at about 4.47 m. `works-crossing-proof.json` retains these
projections. This is evidence of clearing the solid, not an exhaustive Hop
margin test across its full width.

## Additive rewards and uncertainty

The old short interior Relay trip paid more per second than the outer challenge.
100 +200 now favors a roughly 33-second successful sweep over a roughly
15–22-second base-only interior trip. Depot 80 +60 makes its short expressive
attempt attractive alongside direct delivery. Works remains 120 +35. These are
small fixed receipts, not an economy model; return travel, failures and player
preferences can outweigh these rough comparisons. No hidden multipliers.

The unchanged 400-Credit liner takes two or three bonus-bearing deliveries or
roughly four mixed base-only deliveries (five Depot base-only repeats). It is
still session-only and affects only accepted cargo bills. Human difficulty,
desire to improve a line, bonus anxiety and payout preference remain unjudged.
