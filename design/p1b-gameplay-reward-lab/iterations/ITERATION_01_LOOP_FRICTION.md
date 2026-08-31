# Iteration 01 — Moment-to-Moment Contract Loop

Heartbeat started local: `2026-08-26T01:08:47-05:00`

Completed local: `2026-08-26T01:22:52-05:00`

Status: `BOUNDED DESIGN ITERATION — NO PRODUCT CHANGE`

## Decision refined

Select `TRANSACTIONAL_NEUTRAL_GATE_V1` for proof.

Every contract modal exit crosses one paused neutral-release barrier, and every
attempt ends through one post-controller terminal arbiter. This removes hidden
time, held-input leaks, and competing delivery/reset outcomes without adding a
new driving mechanic.

### Low-friction gesture contract

After familiarization:

- start a job with one Dispatch press and one fresh Accept press;
- finish automatically through controlled settle and one Continue press;
- never add a second pickup hold, loading countdown, unload button, abort OK
  modal, or automatic next-board opening.

One press creates one consequence. An opener press can never also accept, and a
held result input can never also resume the craft.

### Exact transition contract

```text
FREE_ROAM
  -> BOARD_OPEN (fresh E at an eligible origin)
  -> WAITING_FOR_NEUTRAL(next=ACTIVE)
  -> ACTIVE on the next physics tick
  -> DELIVERY_SETTLE while every arrival predicate remains true
  -> terminal transaction
  -> RESULTS
  -> WAITING_FOR_NEUTRAL(next=FREE_ROAM)
  -> FREE_ROAM at the reached destination

ACTIVE / DELIVERY_SETTLE
  -> ABORTED when an actual R7 reset occurs
```

Board, pause, and results exits remain paused until all gameplay and UI aliases
are below their deadzones for two consecutive always-process frames. The gate
includes throttle, brake, both steer directions/axis, transform, Hop, reset,
pause, interact, accept, and cancel. Only then is unpause deferred; the next
ordinary physics tick enters the resume target and contributes exactly its own
`delta`.

The two-frame proof seed costs roughly `33 ms` at 60 Hz, is invisible beside a
human button release, and rejects a one-frame neutral glitch. It remains a
test parameter, not movement authority.

R7 already has a private release lock for its own pause/focus path, but a new
gameplay modal would not automatically invoke it. The P1B input router therefore
owns the modal gate without writing R7's private state.

### Dispatch eligibility

A prompt is advisory. The interact edge revalidates the authoritative sample:

- correct origin pad and XZ distance `<= 8.0 m`;
- at least two support probes;
- finite, nonnegative measured height;
- tangential speed `<= 4.0 m/s` initial seed; and
- fresh interact edge.

Opening Dispatch only opens the board. Acceptance requires a later fresh edge.
Reset is UI-owned and consumed while Board, Pause, Waiting, or Results is
paused; it cannot teleport R7 or mutate a terminal attempt there.

### Delivery feedback and settle

Use exactly one highest-priority message:

1. `REACH <DESTINATION>` — outside/nonfinite;
2. `TOUCH DOWN` — insufficient support;
3. `CARGO MOVING — STABILIZE` — this tick added cargo loss;
4. `SLOW · current / 6.0 m/s` — inside and supported but too fast;
5. `UNLOADING n%` — every predicate valid.

Only a positive cargo-loss increment breaks settle. A zero-loss brush may be
recorded on the receipt but does not flicker the unload bar. Pause preserves
settle without advancing it. Radius exit, support loss, speed excess, or cargo
loss resets progress with no extra penalty.

### Terminal order

For each active physics tick after R7 movement:

1. actual reset/abort claim;
2. impact reduction and cargo-loss update;
3. destination predicates;
4. elapsed/settle increment;
5. success threshold; and
6. if successful, latch terminal, freeze summary, evaluate once, apply award
   once by attempt ID, clear navigation/cargo, then reveal immutable Results.

Reset wins a same-tick delivery race. One attempt ID owns at most one terminal,
one result record, and one Credit-ledger entry.

## Paint contribution — Handoff Bloom

An original mineral-and-lilac courier finish whose transformation reveals a
darker internal color story:

| Role | Color |
| --- | --- |
| Frame | `#17251F` deep pine |
| Shell | `#436A56` mineral green |
| Lift | `#A7B897` lichen |
| Underlay | `#29243A` ink plum |
| Trim/seams | `#D7B8EB` courier lilac |
| Drive can | `#665877` muted violet steel |
| Derived joint target | `#32313A` |

Existing roughness/metallic behavior remains. Functional energy, nozzle, and
bore are never recolored. Reject the finish if pale lifts wash into bright
walls, lilac trim blooms, or orange/cyan/amber/red state cues lose salience.

This is a researched candidate, not one of the two authorized proof finalists.

## Trail contribution — Handoff Braid

Two bounded camera-facing history ribbons weave toward and away from each other
by cumulative world distance while tracing the craft's real interpolated path:

- port `#BDA3E6`; starboard `#C5D8B4`;
- `0.040 m` width, head alpha `<= 0.48`, tail alpha exactly zero;
- `0.56 s`, at most 28 samples per rail, at most 30 Hz or `0.30 m` spacing;
- weave amplitude `0.030 m`, wavelength `3.20 m`;
- fade begins `5 m/s`, full at `14 m/s`;
- depth test on; depth write, shadow, GI, lights, and collision off;
- reset, scene switch, invalid craft, or `>8 m` one-frame displacement clears;
- reduced motion: straight rails, `0.26 s`, alpha `<=0.28`, no weave.

Reject it if crossings shimmer, read as navigation, show through walls, obscure
the road/craft, retain a teleport streak, exceed the existing trail study
budget, or cause any movement-trace delta. It remains deferred concept research
until the delivery-loop owner gate requests a trail.

Visual mockup: `concepts/ITERATION_01_HANDOFF_BLOOM_BRAID.svg`  
SHA-256: `632dc2998882b24d705ef9536b1534f0386f82ad3f383e5da204a6b9da40dfa8`

## Deterministic evidence

Command:

```text
PYTHONPATH=tools python3 -B tools/test_iteration_01_loop.py \
  --report analysis/ITERATION_01_TRANSITION_REPORT.json
```

Result: `41/41 PASS`.

Report SHA-256:
`fd9724c9ac310d55b5fc391f84dfceb761407462ef0ef819aac33188641dab3e`

The pure vectors cover inclusive pad/speed boundaries, stale eligibility,
nonfinite/support rejection, unique feedback precedence, fresh input edges,
two-frame neutral release, physics-owned timing, pause preservation, no catch-up
delta, zero-loss contact, damaging-impact reset, exact 30-tick settle, atomic
award, reset/success race, modal reset suppression, and Results exit.

These checks prove only the design model. They do not prove Godot input order,
native UI comprehension, the `6 m/s / 0.50 s` feel, or R7 runtime behavior.

## Stop conditions carried forward

Stop the future P1B integration if any of these occurs:

- one physical press crosses two state boundaries;
- any held craft action leaks through a modal resume;
- modal/pause time changes timer, settle, odometer, or cargo;
- a reset/success race creates two terminals;
- one attempt changes the balance more than once;
- a fly-through, airborne sample, or outer-blend sample delivers;
- settle feedback shows zero or multiple reasons; or
- the familiar loop exceeds two start gestures and one finish gesture.

R7 source/player bytes remain untouched.
