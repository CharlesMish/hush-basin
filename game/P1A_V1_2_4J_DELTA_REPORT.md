# District Zero P1A v1.2.4J — concise successor delta

## Old → new

| Authority | v1.2.4I-R1 | v1.2.4J |
|---|---|---|
| Runtime status | V6 `12/12` executed FAIL; no selection | V6 consumed; V7 `NOT PERFORMED` |
| Algorithm | `DZP1A_DECEL_CONSTRAINED_THRUST_VECTOR_V1` | `DZP1A_PHASE_SEPARATED_BRAKE_CAPTURE_V1` |
| Controller | V6 decel-constrained simultaneous brake/thrust | V7 persistent phase-separated brake then capture thrust |
| Candidate authority | 12 V6 candidates, six trajectories | 4 sensitivity probes + at most 7 selection candidates |
| A1 budget | 12 selection executions | 12 total: 4 sensitivity + ≤7 selection + 1 confirmation |
| Exhaustion outcome | `FAIL — TEST_DRIVER` | `STOP/RETHINK — AUTOMATED A1 GATE`; no automatic controller generation |

## V7 preregistered authority

| Order | Candidate | Stage | Preview P | Plan lateral budget L | Release hysteresis H | Selection eligible |
|---:|---|---|---:|---:|---:|---|
| 1 | `V7_SENS_BASE_P36_L40_H10` | `AXIS_SENSITIVITY` | 36 m | 4.0 m/s² | 1.0 m/s | no |
| 2 | `V7_SENS_P52_L40_H10` | `AXIS_SENSITIVITY` | 52 m | 4.0 m/s² | 1.0 m/s | no |
| 3 | `V7_SENS_P36_L30_H10` | `AXIS_SENSITIVITY` | 36 m | 3.0 m/s² | 1.0 m/s | no |
| 4 | `V7_SENS_P36_L40_H20` | `AXIS_SENSITIVITY` | 36 m | 4.0 m/s² | 2.0 m/s | no |
| 5 | `V7_P52_L30_H20` | `BOUNDED_SELECTION` | 52 m | 3.0 m/s² | 2.0 m/s | yes |
| 6 | `V7_P52_L30_H10` | `BOUNDED_SELECTION` | 52 m | 3.0 m/s² | 1.0 m/s | yes |
| 7 | `V7_P36_L30_H20` | `BOUNDED_SELECTION` | 36 m | 3.0 m/s² | 2.0 m/s | yes |
| 8 | `V7_P36_L30_H10` | `BOUNDED_SELECTION` | 36 m | 3.0 m/s² | 1.0 m/s | yes |
| 9 | `V7_P52_L40_H20` | `BOUNDED_SELECTION` | 52 m | 4.0 m/s² | 2.0 m/s | yes |
| 10 | `V7_P52_L40_H10` | `BOUNDED_SELECTION` | 52 m | 4.0 m/s² | 1.0 m/s | yes |
| 11 | `V7_P36_L40_H20` | `BOUNDED_SELECTION` | 36 m | 4.0 m/s² | 2.0 m/s | yes |

P/L/H are valid axes only if the exact-engine sensitivity stage shows both a command difference and a trajectory difference before the hard boundary. Labels or bookkeeping alone do not count.

## Frozen boundary

World-data authority `v1.2.3`, `HB_TOP_1240MM@0.0`, all 19 formal frozen files, all 41 selected project/world files, routes, spawns, A1/A2/X0 thresholds, C1, 40-suite, Human World Gate, and P1B remain unchanged.

The machine-readable complete file delta is `evidence/v1_2_4j_i_r1_to_j_delta_manifest.json`.

## Director-turn static and packaging verification

The following checks are required against the final bytes and are rerun at the packet root and a fresh extraction:

- original v1.2.4I-R1 `PACKET_SHA256SUMS.txt`: `1,497/1,497 PASS`;
- supplied I-R1 evidence transport SHA-256 and root inventory: exact match, `242/242 PASS`; all 40 nested inventories pass;
- P0 substantive tree: `147/147 PASS`;
- selected project/world preservation: `41/41 byte-identical`;
- formal frozen movement/world subset: `19/19 byte-identical`;
- V6 raw-evidence recomputation: 12 candidates, six distinct trajectories, six S08/S10 pair-identity proofs;
- V7 authority: 11 preregistered records, 33 static route-plan records, 9/9 semantic cases;
- route bake: 17 routes, 11,252 points, compact SHA-256 `f26283b6cd314ba1d27aebea0bf80d82fbf2426ee5f22b610b38c273fec73330`;
- final packet checksum inventory: every file except root `PACKET_SHA256SUMS.txt`;
- strengthened verifier and anti-duplication gate: required `PASS`, zero errors;
- Python AST/JSON parsing, ZIP CRC, duplicate-entry, and forbidden-metadata scans: required `PASS`;
- root versus fresh extraction: required byte-identical.

No exact-engine v1.2.4J gameplay or human testing is performed in this director turn.
