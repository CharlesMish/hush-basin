# District Zero P1A v1.2.5 — instrumented feasibility capture card

**Evidence class:** informed developer/director physical-feasibility evidence. This is not the qualitative Human World Gate and cannot support naive discovery claims.

## Before Charlie plays

Codex must provide a visible build labeled `DISTRICT ZERO · P1A FEASIBILITY CAPTURE · v1.2.5`, prove exact Godot `4.7.1.stable.official.a13da4feb`, import and parse the disposable project, pass the implementation verifier, and demonstrate C1 maximum delta `0.0` with capture/replay instrumentation inactive.

No prior human trace is required. Charlie has not installed or played the current map.

The capture UI may show only route name, phase, three-second ready countdown, attempt number, elapsed time, recording state, and final attempt result. It must not show chainage, lateral error, fast-distance progress, desired speed, an ideal line, or steering/braking advice.

## Controls

Use the normal craft controls: `W` throttle, `S` brake, `A/D` steering, and hold `Shift` for DRIVE. Hop, reset, pause, debug, and diagnostic controls invalidate a recorded attempt. `F10` may be a capture-only abort and is recorded as a failed attempt.

## Exact route sequence

For each route in order A1, A2, X0:

1. Up to five minutes of clearly labeled non-evidentiary familiarization; end early when ready.
2. Up to five recorded attempts from the exact canonical spawn/state.
3. Retain and checksum every attempt, including aborts and failures.
4. Select the first full pass automatically; never cherry-pick a later better attempt.
5. Replay that exact normalized input trace three times; Charlie supplies no replay input.
6. Continue only if all three replays independently pass and satisfy the deterministic contract.

## Hard pass rules

| Route | Fast speed | Minimum fast distance | Genuine traversal | Maximum lateral distance | Hard collisions / fall-reset |
|---|---:|---:|---:|---:|---:|
| A1 | 18 m/s | 64.372840 m | 190.291358 m | 11.0 m | 0 / 0 |
| A2 | 18 m/s | 88.456389 m | 289.825556 m | 11.0 m | 0 / 0 |
| X0 | 18 m/s | 99.976210 m | 342.304838 m | 8.0 m | 0 / 0 |

A measured lateral crossing is a failure. Human judgment cannot waive any hard metric.

## Evidence retained per attempt

The session retains exact argv, exact engine and project identity, normalized `input_trace.json`, full `telemetry.json`, canonical quantized `state_trace.json`, attempt result, stdout, stderr, engine log, and detached checksums. Hashes are never embedded inside the bytes they identify.

## End states

- First capture plus three replays pass: advance to the next route.
- Five attempts without a capture pass, or any replay mismatch: `HUMAN FEASIBILITY NOT ESTABLISHED — <route>`; stop and package all evidence.
- All three routes pass capture/replay: Codex runs selected C1 and the complete 40-vector suite. The qualitative Human World Gate remains locked until `40/40 PASS` and is not conducted by this workflow.
