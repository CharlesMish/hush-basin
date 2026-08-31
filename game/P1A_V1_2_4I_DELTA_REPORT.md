# District Zero P1A v1.2.4I delta report

This successor was compiled from completed v1.2.4H exact-engine evidence. It does not reissue H.

- V5 selection is historical completed evidence: 3/3 valid gameplay FAIL, no candidate selected.
- Active successor identity: `DZP1A_DECEL_CONSTRAINED_THRUST_VECTOR_V1` / `ROUTE_FOLLOWER_INPUT_CONTROLLER_V6_DECEL_CONSTRAINED_THRUST_VECTOR_CONTAINED`.
- Structural change: V5's fixed turning-throttle floor under full brake is replaced by a conservative longitudinal-thrust projection constraint that preserves preregistered minimum net deceleration.
- DOE: 12 preregistered candidates (3×2×2), first A1 pass freezes.
- Added per-tick speed-prediction and slowdown-health telemetry; material speed rise during sustained slowdown is a fail-fast defect.
- Frozen world/movement, selected HOP, routes/spawns/thresholds, C1, suite, Human World Gate, and P1B are unchanged.
- Exact-engine v1.2.4I execution: `NOT PERFORMED` in this director rebuild.

## Machine identities

- V6 candidate registry SHA-256: `460897a34caa0e57fe7ce8222593accab26f28b4ad34ccd3e56910db53c3f391`
- H→I delta manifest: `evidence/v1_2_4i_h_to_i_delta_manifest.json` (126 records)
