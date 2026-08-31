# District Zero P1A v1.2.4J — evidence adjudication and resolution ledger

## Input verification

| Item | Verified result |
|---|---|
| I-R1 evidence transport | `ea0338dd1735760f91352e7ecf752d83b61e96216d034e2f3708754a47da2c54` |
| Root evidence inventory | `242/242 PASS`; all nested inventories pass |
| Executed-source copy | `1498/1498 byte-identical` |
| Gate result | `FAIL`; `FAST_ROUTE_GATE`; `TEST_DRIVER` |
| Exact engine | `4.7.1.stable.official.a13da4feb` |
| Executed V6 registry | `460897a34caa0e57fe7ce8222593accab26f28b4ad34ccd3e56910db53c3f391` |
| V6 execution | `12/12 valid gameplay FAIL`; no candidate selected |
| Downstream locks | A1 confirmation, A2, X0, C1, 40-suite, Human World Gate, P1B not reached |

## Required adjudications

| Finding | Disposition | Evidence | Operative resolution |
|---|---|---|---|
| S08/S10 identity | **ACCEPT** | All six pairs have identical command and dynamics streams after excluding labels, S-dependent desired/cap fields, and slowdown bookkeeping. | S is a dead V6 axis. V7 requires runtime command-and-trajectory sensitivity for every axis before selection. |
| Closest deviations near 11 m | **REJECT as tolerance issue** | Best terminal deviations were `11.002896 m` and `11.003646 m`, but traces still carried ~4.64–5.00 m/s outward lateral velocity, ~62° course error, and ~16.7–17.2 m predicted deviation. | Keep the exact `11 m` limit and fail-fast rule. No epsilon. |
| Fast-distance room | **ACCEPT** | Six distinct trajectories banked roughly 95–100 m versus required `64.372840 m`. | Earlier decisive slowing is contract-compatible; thresholds remain unchanged. |
| Speed plan/braking timing | **ACCEPT** | Curvature/lateral request saturated near chainage 87.2–87.6 m at ~20.3–20.7 m/s, while the speed planner used a permissive lateral budget. | V7 tests earlier planning via P and L axes and a more conservative backward envelope. |
| Phase switching/ineffective braking | **ACCEPT** | Traces show repeated brake/non-brake switching; D30 produced roughly twice the switching of D20/D25 without monotonic containment improvement. | V7 uses a persistent `BRAKE_COMMIT` phase with minimum duration and release hysteresis. |
| Lateral-capture authority | **ACCEPT** | During V6 braking, throttle was capped to ~0.05–0.09, starving transverse thrust while requested acceleration/body lead were saturated. | V7 separates full brake/yaw (`throttle=0`) from brake-free `CAPTURE_THRUST`, never simultaneous brake+throttle. |
| Automated proxy disproportionality | **REJECT at this stage** | The defect is localized and mechanistically identified; a normal-input-only correction remains bounded and falsifiable. | Authorize one final V7 family. Family exhaustion ends `STOP/RETHINK — AUTOMATED A1 GATE`; no automatic successor. |
| World/movement incompatibility | **NOT ESTABLISHED** | V6 evidence tests the follower, not human playability; no collision and ample fast distance were achieved. | Preserve all world/movement authority. Do not unlock Human World Gate. |

## Six distinct V6 trajectories

Chainage and speed are shown as `chainage / speed`.

| Representative | First braking | First lateral saturation | First recovery | First 5 m deviation | Terminal state |
|---|---|---|---|---|---|
| `V6_D20_R35_S08` | ch 71.990 / 20.258 m/s | ch 87.350 / 20.573 m/s | ch 91.080 / 20.395 m/s | ch 111.180 / 16.245 m/s | ch 124.391; 12.687 m/s; dev 11.072956 m; lateral 5.435 m/s; course 61.6°; predicted 17.777 m |
| `V6_D20_R45_S08` | ch 71.990 / 20.258 m/s | ch 87.350 / 20.573 m/s | ch 93.439 / 20.463 m/s | ch 111.441 / 16.763 m/s | ch 124.522; 13.318 m/s; dev 11.091187 m; lateral 5.788 m/s; course 61.8°; predicted 18.230 m |
| `V6_D25_R35_S08` | ch 71.540 / 20.347 m/s | ch 87.565 / 20.713 m/s | ch 91.302 / 20.450 m/s | ch 110.880 / 15.803 m/s | ch 123.906; 11.581 m/s; dev 11.082331 m; lateral 5.097 m/s; course 62.1°; predicted 17.369 m |
| `V6_D25_R45_S08` | ch 71.540 / 20.347 m/s | ch 87.565 / 20.713 m/s | ch 93.320 / 20.538 m/s | ch 111.142 / 16.337 m/s | ch 123.985; 12.305 m/s; dev 11.035620 m; lateral 5.449 m/s; course 62.3°; predicted 17.757 m |
| `V6_D30_R35_S08` | ch 44.024 / 22.647 m/s | ch 87.505 / 20.289 m/s | ch 91.243 / 20.469 m/s | ch 110.762 / 15.199 m/s | ch 123.207; 10.347 m/s; dev 11.002895 m; lateral 4.644 m/s; course 61.9°; predicted 16.731 m |
| `V6_D30_R45_S08` | ch 44.024 / 22.647 m/s | ch 87.505 / 20.289 m/s | ch 93.260 / 20.516 m/s | ch 111.052 / 15.748 m/s | ch 123.382; 11.113 m/s; dev 11.003646 m; lateral 5.003 m/s; course 62.9°; predicted 17.174 m |

## Director outcome

**Outcome A — genuine v1.2.4J successor.** The evidence supports exactly one bounded phase-separated, input-only experiment. v1.2.4I-R1 is consumed historical evidence and is not repackaged as active authority.
