# Mechanics Range V1.1 calibration

Parent: accepted V1 `0fb521fa8d881abcc595a3e2d19787f2ba25c4d6`.
No controller, cargo curve/grouping, BRRR formula, world or collider edits.
No geometry additions. The existing Works service bar remains as in V1.

## Evidence and interpretation

The old broad BRRR streak admits fast straight Drive. A stricter sibling observer
now requires Drive, speed ≥22 m/s and slip from 15° through 75°. At exactly 60 Hz,
only qualifying samples add time. Straight samples cannot extend a combo; wall
contact clears unfinished evidence. Best completed evidence stays earned.

An important instrumentation finding: the controller's raw impact counter can
advance on ordinary terrain/support contact. Treating every counter increment as
a failed line incorrectly rejected Shelf travel. The observer therefore uses the
unchanged cargo contact classifier's wall-contact evidence, including sustained
pressure. It does not reinterpret or modify controller telemetry or cargo loss.
F3 retains raw cargo evidence and adds a bounded 64-transition combo history.

Final reproducible calibration uses `range_v11_calibration.gd`; complete-game
drives use `range_v11_probe.gd` and the ordinary-input `range_v11_driver.gd`.
The former declares initial heading before driving; the latter organizes that
heading through normal Spread steering/braking and includes setup in active time.
Neither changes craft position/velocity during a driving trial. Synthetic
endpoint/contact tests are separately labelled and do not count as route runs.

Depot straight: 8.93 s, 100% cargo, zero drift combo despite 202 BRRR. Three clean
shaped variants produced 3.10, 3.78 and 4.40 s qualifying drift in 17.10, 19.15 and
21.12 s. Choose **3.5 s**, between an incomplete shape and two successful variants.
The 15° floor excludes the straight run's 5.24° peak. Actual correction gaps in
sampled shapes were 1.42–1.58 s, not one-frame steering noise; no grace was added
to conceal them. The owner's 10.8 s observation was not used as the target.

Relay interior: 19.00 s, 16.7 m best clean Drive. Outer variants produced 144.9,
149.4 and 180.6 m; the last was clean and took 32.23 s. Choose **170 m** at ≥24 m/s,
≤45° slip. This asks for one organized line instead of banking broad BRRR through
a wall. It is deliberately not a route-exclusive or anti-farming system.

Works retains **85% condition**. Complete-game clean early-unfold/Hop and rough
legal bypass examples succeed; hot contact/recovery delivers with about 76% and
misses. Accepted cargo/protection remain untouched. A competent clean bypass can
still earn Care, so this is a mode-choice demonstration rather than forced Hop.

Thread uses authoritative HJW/HJE and the union of existing HOP/DOG route bounds,
with a 9 m margin and 15 m entry/exit radii. The optional west-to-east crossing
requires Spread and no wall contact. Direct Clinic delivery misses. The southern
dogleg sample takes 48.37 s with 100% cargo; complete-game Hop also clears cleanly.
The broader corridor avoids camera-hostile precision. It may remain too gentle
for Charlie: the question is whether South Cut merits learning, not whether an
automated driver can be made to fail arbitrarily.

Haul uses existing Clinic–East Sweep–Quarry Shelf routes, roughly a whole-district
journey. Choose **160 m clean Drive / 40 m moving Spread / 90 m clean Drive**.
The first sweep yields 234.2 m; Shelf affords a shorter second opportunity
(108.4 m observed before the phase target was applied). The selected run takes
79.67 s with 98.6% cargo. A 21.50 s shortcut earns no phases. Neighboring steering
look-ahead variants do not all finish the second leg: this is retained as a real
weakness, not discarded evidence. Automated separation is established; the
second leg's human readability and tolerance need review. We did not keep tuning
the observer until every automated path won.

## Rewards and limits

V1 → V1.1: Depot slip BRRR 100 → strict drift 3.5 s (80+60 unchanged);
Relay broad BRRR streak 6 s → clean Drive 170 m (100+200 unchanged);
Works 85% Care (120+35 unchanged). New Thread 100+300; new Haul 140+420.
New totals roughly compensate the observed longer runs without a general economy:
Thread ~400/50 s, Haul ~560/81 s, versus their short base-only alternatives.
Exact totals are additive, authored and session-only. No repeat penalty.

The existing large release spaces stay empty on purpose. No additional yard
furniture, topology edits or cosmetic progression was necessary. Five jobs only.
All historical validators/manifests remain intact; the V1.1 inventory explicitly
binds the six changed existing files instead of rewriting old expectations.

## Complete-game native route matrix

All rows delivered using ordinary inputs with zero resets. Full JSON also records
impact samples, distance, phases and payouts. Return-to-Market driving is an
additional passing check, not a delivery.

| Route | Time s | Drive / Spread s | Cargo | Bonus | Drift s | Clean Drive m | BRRR | Episodes |
|---|---:|---:|---:|---|---:|---:|---:|---:|
| DEP_direct | 9.23 | 2.8 / 6.4 | 100.0% | no | 0.00 | 55.2 | 190.4 | 0 |
| DEP_style | 20.48 | 11.3 / 9.2 | 100.0% | yes | 3.78 | 109.4 | 2047.3 | 0 |
| RLY_spine | 21.75 | 2.6 / 19.1 | 100.0% | no | 0.00 | 11.5 | 42.2 | 0 |
| WRK_way | 9.88 | 2.5 / 7.4 | 100.0% | yes | 0.00 | 45.7 | 165.6 | 0 |
| WRK_sidepass | 12.12 | 0.9 / 11.2 | 78.1% | no | 0.00 | 0.0 | 1.8 | 1 |
| WRK_hot_recovery | 11.53 | 4.1 / 7.4 | 76.1% | no | 0.00 | 62.8 | 236.4 | 1 |
| DEP_road | 12.52 | 2.0 / 10.5 | 100.0% | no | 0.00 | 14.4 | 55.2 | 0 |
| RLY_sweep | 33.70 | 11.3 / 22.4 | 100.0% | yes | 5.63 | 180.6 | 2237.4 | 1 |
| WRK_rough_alternate | 40.10 | 0.0 / 40.1 | 100.0% | yes | 0.00 | 0.0 | 0.0 | 0 |
| THREAD_easy | 10.12 | 2.6 / 7.5 | 100.0% | no | 0.00 | 55.1 | 230.2 | 0 |
| THREAD_dogleg | 49.87 | 0.0 / 49.9 | 100.0% | yes | 0.00 | 0.0 | 0.0 | 0 |
| THREAD_hop | 47.05 | 0.0 / 47.0 | 100.0% | yes | 0.00 | 0.0 | 0.0 | 0 |
| HAUL_easy | 22.87 | 5.0 / 17.8 | 100.0% | no | 0.18 | 19.8 | 140.8 | 0 |
| HAUL_long | 81.18 | 19.9 / 61.3 | 98.6% | yes | 12.88 | 234.2 | 3758.9 | 2 |
