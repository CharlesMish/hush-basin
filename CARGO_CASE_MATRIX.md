# Observed cargo case matrix

Same flat support, same vertical wall, exact Godot 4.7.1 on this Mac. Every contact case starts with fresh cargo. Angles are velocity relative to the wall normal (0° = head-on). Initial velocities are controlled test conditions, including retained speeds above Spread cruise; movement/response remain unchanged.

Incoming/closing/severity columns show the first fresh controller impact. “—” means no above-threshold impact was reported, not an invented speed of zero. Loss columns are actual cumulative case losses. Repeated-contact rows contain three impacts; their 72% is three 24% entries.

| Case | Incoming m/s | Closing m/s | Severity | v1 loss | v1.1 loss | Episodes v1 → v1.1 |
|---|---:|---:|---:|---:|---:|---:|
| Spread_0.5_mps_0_deg | — | — | — | 0.0% | 0.0% | 0 → 0 |
| Spread_2.0_mps_0_deg | 1.959 | 1.959 | 0.113 | 0.0% | 0.0% | 1 → 1 |
| Spread_6.0_mps_0_deg | 5.938 | 5.938 | 0.581 | 7.9% | 7.9% | 1 → 1 |
| Spread_12.0_mps_0_deg | 11.877 | 11.877 | 1.000 | 24.0% | 24.0% | 1 → 1 |
| Spread_24.0_mps_0_deg | 23.753 | 23.753 | 1.000 | 24.0% | 24.0% | 1 → 1 |
| Spread_0.5_mps_60_deg | — | — | — | 0.0% | 0.0% | 0 → 0 |
| Spread_2.0_mps_60_deg | — | — | — | 0.0% | 0.0% | 0 → 0 |
| Spread_6.0_mps_60_deg | 5.877 | 2.939 | 0.143 | 0.0% | 0.0% | 1 → 1 |
| Spread_12.0_mps_60_deg | 11.755 | 5.877 | 0.359 | 2.1% | 2.1% | 1 → 1 |
| Spread_24.0_mps_60_deg | 23.509 | 11.755 | 0.625 | 9.3% | 9.3% | 1 → 1 |
| Spread_0.5_mps_85_deg | — | — | — | 0.0% | 0.0% | 0 → 0 |
| Spread_2.0_mps_85_deg | — | — | — | 0.0% | 0.0% | 0 → 0 |
| Spread_6.0_mps_85_deg | — | — | — | 0.0% | 0.0% | 0 → 0 |
| Spread_12.0_mps_85_deg | 11.634 | 1.014 | 0.001 | 0.0% | 0.0% | 1 → 1 |
| Spread_24.0_mps_85_deg | 23.267 | 2.028 | 0.038 | 0.0% | 0.0% | 1 → 1 |
| Spread_8.0_mps_0_deg | 7.836 | 7.836 | 0.804 | 15.7% | 15.7% | 1 → 1 |
| Spread_9.0_mps_0_deg | 8.907 | 8.907 | 0.930 | 20.9% | 20.9% | 1 → 1 |
| Spread_9.3_mps_0_deg | 9.204 | 9.204 | 0.965 | 22.4% | 22.4% | 1 → 1 |
| pressure_false_start_20.0 | 14.174 | 14.174 | 1.000 | 24.0% | 24.0% | 1 → 1 |
| pressure_false_start_1.5 | 1.454 | 1.454 | 0.053 | 1.4% | 0.0% | 1 → 1 |
| repeat_false_30_ticks | 11.877 | 11.877 | 1.000 | 72.0% | 72.0% | 3 → 3 |
| repeat_false_6_ticks | 11.877 | 11.877 | 1.000 | 24.0% | 72.0% | 1 → 3 |
| Drive_0.5_mps_0_deg | — | — | — | 0.0% | 0.0% | 0 → 0 |
| Drive_2.0_mps_0_deg | 1.995 | 1.995 | 0.117 | 0.0% | 0.0% | 1 → 1 |
| Drive_6.0_mps_0_deg | 5.992 | 5.992 | 0.587 | 8.1% | 8.1% | 1 → 1 |
| Drive_12.0_mps_0_deg | 11.984 | 11.984 | 1.000 | 24.0% | 24.0% | 1 → 1 |
| Drive_24.0_mps_0_deg | 23.968 | 23.968 | 1.000 | 24.0% | 24.0% | 1 → 1 |
| Drive_0.5_mps_60_deg | — | — | — | 0.0% | 0.0% | 0 → 0 |
| Drive_2.0_mps_60_deg | — | — | — | 0.0% | 0.0% | 0 → 0 |
| Drive_6.0_mps_60_deg | 5.984 | 2.992 | 0.146 | 0.0% | 0.0% | 1 → 1 |
| Drive_12.0_mps_60_deg | 11.984 | 5.992 | 0.367 | 2.3% | 2.3% | 1 → 1 |
| Drive_24.0_mps_60_deg | 23.968 | 11.984 | 0.625 | 9.3% | 9.3% | 1 → 1 |
| Drive_0.5_mps_85_deg | — | — | — | 0.0% | 0.0% | 0 → 0 |
| Drive_2.0_mps_85_deg | — | — | — | 0.0% | 0.0% | 0 → 0 |
| Drive_6.0_mps_85_deg | — | — | — | 0.0% | 0.0% | 0 → 0 |
| Drive_12.0_mps_85_deg | 11.952 | 1.042 | 0.002 | 0.0% | 0.0% | 1 → 1 |
| Drive_24.0_mps_85_deg | 23.904 | 2.083 | 0.040 | 0.0% | 0.0% | 1 → 1 |
| Drive_8.0_mps_0_deg | 7.989 | 7.989 | 0.822 | 16.5% | 16.5% | 1 → 1 |
| Drive_9.0_mps_0_deg | 8.988 | 8.988 | 0.940 | 21.4% | 21.4% | 1 → 1 |
| Drive_9.3_mps_0_deg | 9.275 | 9.275 | 0.974 | 22.8% | 22.8% | 1 → 1 |
| pressure_true_start_20.0 | 30.195 | 30.195 | 1.000 | 24.0% | 24.0% | 1 → 1 |
| pressure_true_start_1.5 | 1.928 | 1.928 | 0.109 | 0.0% | 0.0% | 1 → 1 |
| repeat_true_30_ticks | 11.984 | 11.984 | 1.000 | 72.0% | 72.0% | 3 → 3 |
| repeat_true_6_ticks | 11.984 | 11.984 | 1.000 | 24.0% | 72.0% | 1 → 3 |
| drift | — | — | — | 0.0% | 0.0% | 0 → 0 |
| braking | — | — | — | 0.0% | 0.0% | 0 → 0 |
| transform | — | — | — | 0.0% | 0.0% | 0 → 0 |
| supported_hop | — | — | — | 0.0% | 0.0% | 0 → 0 |
| normal_travel | — | — | — | 0.0% | 0.0% | 0 → 0 |
| stale_after_strike | — | — | — | 0.0% | 0.0% | 0 → 0 |

v1 meets 89/92 successor criteria; the three failures are low-speed Spread pressure escalation and rapid separated hits in each form. v1.1 meets 92/92. Clean drift, braking, transformation, supported Hop/landing, normal travel and stale-telemetry controls all lose zero.

The ordinary damage curve is unchanged. “Near-stop Spread caused 22%” remains unadjudicated as an owner incident because it was not recorded. Controlled fresh 2 m/s head-on entries lose zero; 9.3 m/s nominal head-on entries reproduce about 22%.
