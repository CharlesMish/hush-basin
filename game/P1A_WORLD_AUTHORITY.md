# District Zero P1A v1.2.5 — instrumented human feasibility capture authority

## 1. Sole decision

The v1.2.4J automated A1 gate is consumed and closed as `STOP/RETHINK — AUTOMATED A1 GATE`. Autonomous V4–V7 controller development is retired. No V8, v1.2.4K, parameter family, movement retune, route change, threshold change, or world correction is authorized.

The replacement evidence stage is:

`INSTRUMENTED HUMAN FEASIBILITY CAPTURE → DETERMINISTIC INPUT REPLAY`

This stage is accepted because the fast-route hard checks were intended to establish the existence of a valid player-input trajectory under frozen physics. An autonomous follower was only a proxy for that existential claim. A human-generated witness trace plus deterministic replay tests the claim directly while retaining every objective threshold.

This is an informed developer/director feasibility stage. It is not naive discovery and is not the later qualitative Human World Gate.

## 2. Frozen authority

The following remain byte- and meaning-frozen:

- world-data authority `v1.2.3` and all 19 formal frozen movement/world files;
- all 41 selected project/world files until Codex adds behavior-neutral test instrumentation outside the protected set;
- selected HOP `HB_TOP_1240MM@0.0`;
- every route, node, baked centerline, terrain, mask, solid, collider, spawn, camera, tuning value, and presentation asset;
- A1/A2/X0 route direction, canonical initial state, termination, route-entry/traversal semantics, collision semantics, and telemetry semantics;
- speed floor `18 m/s`;
- A1 fast distance `64.372840 m`, genuine traversal `190.291358 m`, lateral maximum `11.0 m`;
- A2 fast distance `88.456389 m`, genuine traversal `289.825556 m`, lateral maximum `11.0 m`;
- X0 fast distance `99.976210 m`, genuine traversal `342.304838 m`, lateral maximum `8.0 m`;
- zero non-Hop hard collisions and zero fall/reset;
- selected C1 maximum delta `0.0` and the complete 40-vector authority;
- Human World Gate and P1B boundaries.

No epsilon may convert a measured crossing beyond a lateral maximum into a pass. Existing `+0.000001 m` computational comparison treatment remains the only numerical guard.

## 3. v1.2.4J evidence adjudication

The embedded evidence at `227f3aa338040f02487fea189c03a3158f97af7df9b864c8324e4b1d6685ac30` verifies `225/225 PASS`, exact engine `4.7.1.stable.official.a13da4feb`, and a byte-identical `1796/1796` executed source copy.

J proves only that its preregistered V7 family did not satisfy A1. All P/L/H sensitivity axes changed commands and trajectories. All seven selection candidates executed valid `FAIL/1` gameplay, entered A1, emitted contiguous projection evidence, had zero hard collisions and zero post-result events, then crossed the unchanged lateral maximum before `TRAVERSED`.

J does not prove human impossibility, authorize threshold relaxation, or establish a movement/world defect. The closest candidate, `V7_P36_L30_H20`, reached chainage `186.663088 m` before failing at lateral distance `11.001759 m`; it still had outward lateral velocity and predicted further departure. It remains a valid controller failure, not a tolerance pass.

The machine-readable verification is `evidence/v1_2_5_j_executed_evidence_verification.json`.

## 4. Objective claim and evidence boundary

The feasibility stage may establish only:

> From each frozen canonical A1, A2, and X0 initial state, at least one sequence of normal player inputs satisfies every frozen route metric, and that sequence reproduces under the same exact engine and project bytes.

It may not establish fun, clarity, comfort, learnability, naive route discovery, or final World Gate acceptance. Human judgment cannot override a failed metric.

## 5. Codex implementation contract

Codex shall implement only behavior-neutral capture/replay instrumentation described by `tests/fixtures/human_capture_implementation_contract.json` and the schemas in `tests/fixtures/`.

The implementation may:

- set the canonical spawn transform, zero velocity, frozen DRIVE initial state, and route candidate reset before physics tick zero;
- disable physics during the ready countdown;
- sample existing player inputs;
- emit files, status UI, and evidence;
- inject recorded normalized inputs during replay before the craft physics tick.

It may not generate steering or braking commands, assist aim, display an ideal line or live lateral/chainage coaching, change gameplay state after tick zero except through normal recorded input, or write movement/world data.

Instrumentation must be inactive during C1 and unrelated vectors. C1 must remain maximum delta `0.0`.

## 6. Per-route human protocol

Execute routes in the fixed order `A1 → A2 → X0`.

For each route:

1. Offer at most `300 s` of clearly labeled non-evidentiary familiarization. It may end early. Once recorded attempts begin, familiarization for that route is over.
2. Start every recorded attempt from the exact runtime-vector spawn, zero initial velocity, DRIVE fold state, and fixed `1/60 s` timestep.
3. Disable physics during a three-second ready countdown. Begin input capture at the first enabled physics tick.
4. Allow at most five recorded attempts. Retain and checksum every attempt.
5. Select the first attempt in chronological order that fully passes. Do not select a later “better” trace.
6. If none passes, stop `HUMAN FEASIBILITY NOT ESTABLISHED — <route>` and preserve all attempts.

During an eligible attempt the only gameplay actions are `throttle`, `brake`, `steer_left`, `steer_right`, and held `transform`. Hop, reset, pause, debug, diagnostics, and menu actions invalidate the attempt. A manual capture abort is a retained failure.

No live chainage, lateral error, fast-distance accumulation, desired speed, ideal line, or control suggestion may be shown during recorded attempts.

## 7. Per-tick capture

At the start of each physics tick, capture normalized input as integers:

- `throttle_u16 = round(clamp(throttle,0,1) × 65535)`;
- `brake_u16 = round(clamp(brake,0,1) × 65535)`;
- `steer_i16 = round(clamp(steer_right−steer_left,−1,1) × 32767)`;
- `transform_pressed`;
- `hop_pressed`.

After the same physics tick, record engine identity, vector/physics tick, position, velocity, yaw, fold, surface, collision/reset events, route projection, chainage, lateral distance, speed, and accumulated fast distance. Input and telemetry tick sequences must be contiguous.

The canonical `input_trace.json` and quantized `state_trace.json` follow `tests/fixtures/human_trace_serialization_contract.json`; their hashes are detached and never self-referential. Full-precision `telemetry.json` remains raw evidence. Every attempt directory carries the exact artifact set in the implementation contract and its own `SHA256SUMS.txt`.

## 8. Attempt evaluation

Fail immediately and retain evidence on:

- lateral distance above the route maximum plus `0.000001 m`;
- any non-Hop hard collision;
- fall or reset;
- prohibited action or loss of DRIVE transform hold;
- timeout or manual abort;
- missing/noncontiguous input or telemetry.

A capture passes only after a genuine requested-route `ENTERED` followed by genuine requested-route `TRAVERSED`, the required genuine distance and fast distance, zero collision/reset, and all other unchanged vector thresholds.

## 9. Deterministic replay

Replay the selected raw input trace three times under exact Godot `4.7.1.stable.official.a13da4feb`, the same imported project bytes, the same canonical initial state, and fixed `1/60 s` physics. Ignore live user input during replay.

Each replay must independently pass the route metrics. It must also match the capture in termination tick and route/collision/reset/surface event sequence. The canonical quantized state-trace SHA-256 must match, using the quantization and raw-delta limits in `human_feasibility_protocol.json`.

A replay mismatch is a failure; human capture success alone is not sufficient.

## 10. Complete locked sequence

`A1 capture/replay → A2 capture/replay → X0 capture/replay → C1 max delta 0.0 → complete 40-vector suite → authorize but do not conduct Human World Gate → stop before P1B`

The complete suite retains 40 vectors. Its A1/A2/X0 vectors consume the three selected trace records through `NORMALIZED_INPUT_TRACE_REPLAY_V1`; the other 37 remain unchanged.

A route failure cannot be hidden by another route’s success. No new autonomous controller generation is authorized.

## 11. Outcomes

- `READY FOR HUMAN FEASIBILITY CAPTURE`: Codex implementation/import/parse/C1-inactive checks are green; no human attempt has yet been claimed.
- `HUMAN FEASIBILITY NOT ESTABLISHED — A1/A2/X0`: the route exhausted five attempts or replay failed. Preserve evidence and return for explicit director choice among geometry, movement, contract, or route-thesis revision. Do not automatically call this a world failure.
- `BLOCKED/NOT TESTABLE`: required files, exact engine, identity, instrumentation, trace, telemetry, or replay evidence is absent or invalid.
- `FEASIBILITY GATE PASS`: all three capture/replay gates, C1, and the 40-vector suite pass. This authorizes—but does not perform—the later qualitative Human World Gate.

## 12. Evidence policy and frozen P1B boundary

Charlie’s session is `INFORMED_DEVELOPER_DIRECTOR_FEASIBILITY_EVIDENCE`. It cannot support naive comprehension or first-discovery claims and cannot be reused as the final Human World Gate record.

No publishing, deployment, push, PR, external contact, account change, Human World Gate execution, or P1B work is authorized.
