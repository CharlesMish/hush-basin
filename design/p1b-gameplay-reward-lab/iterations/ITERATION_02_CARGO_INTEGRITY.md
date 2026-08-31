# Iteration 02 — Cargo Integrity, Collision, and Landing Semantics

Heartbeat started local: `2026-08-26T02:09:47-05:00`

Completed local: `2026-08-26T02:28:00-05:00`

Status: `BOUNDED DESIGN ITERATION — NO PRODUCT CHANGE`

## Decision refined

Select `R7_COUNTER_EPOCH_FORGIVING_PEAK_EPISODE_V1` as the one cargo model for
the three-job proof.

Cargo is an abstract observer of fresh R7 impact observations. It never becomes
a rigid body, movement modifier, per-contact tax, landing surcharge, or drift
meter. All three initial contracts use the same forgiving provisional profile
so route feel—not changing fragility—is the variable under study.

## Exact R7 observation seam

The read-only source establishes these constraints:

- `CraftController` samples support, performs Hop logic, calls
  `move_and_slide()`, then resolves the strongest closing slide collision.
- A closing speed at or below `1.0 m/s` creates no controller impact. A
  qualifying physics step updates sticky `last_impact_*` fields and increments
  `impact_count` at most once.
- `last_impact_severity` does not decay on quiet ticks. It is meaningful only
  when a new `impact_count` increment is observed.
- telemetry's `COLLISION_SAMPLE` may repeat every contact tick, covers only five
  hard-source IDs, and contains post-response velocity. It is evidence, never
  cargo-damage authority.
- reset clears impact and Hop counters to zero, increments monotonic
  `reset_count`, teleports, and emits `reset_performed` synchronously.
- R7 has no landing event. Its support sample is taken before movement and may
  still report support on the tick a Hop begins.

A future P1B observer therefore runs as a sibling at explicit physics priority
`200`, after the craft and existing priority-`100` telemetry. It writes nothing
to either. Acceptance snapshots `reset_count`, `impact_count`, and `hop_count`;
free-roam history cannot leak into cargo.

For every active, unpaused physics sample:

1. a reset epoch change wins and aborts once before cleared counters are read;
2. active sample sequence and finite positive `delta` must advance exactly
   once;
3. unchanged impact count ignores sticky severity entirely;
4. exactly `+1` captures the matching severity snapshot;
5. decrease without reset, jump beyond `+1`, invalid severity, or a missing
   sample stops unscored as `OBSERVER_INVALID`; and
6. the terminal result freezes the ledger permanently.

No collision source or normal is guessed by joining incomplete telemetry. The
absence of source identity makes the time-only grouping deliberately forgiving.

## Peak-episode reducer

State is integer and bounded:

```text
integrity_units = 1000                 # 100.0%, tenths precision
severity_milli = round_half_up(p*1000) # 0.001 precision
quiet_window = 0.250 active seconds
```

Impacts separated by at most `0.250 s` of active, unpaused physics time belong
to one episode. A gap strictly greater than `0.250 s` opens another. Pause
freezes episode age as well as condition.

Within one episode, only a rising peak can charge cargo:

```text
q = clamp((severity_milli - 200) / 800, 0, 1)
target_loss_units = round_half_up(240 * q^1.50)
new_loss = max(0, target_loss_units - already_charged_units)
```

This telescopes: `0.25 -> 0.50 -> 0.75` costs exactly the same as one `0.75`
peak. Holding against one wall cannot scale damage with physics rate or contact
duration.

### Golden seed behavior

| Episode peak | Cargo loss | Condition after one episode |
| ---: | ---: | ---: |
| `0.20` | `0.0%` | `100.0%` |
| `0.25` | `0.4%` | `99.6%` |
| `0.35` | `1.9%` | `98.1%` |
| `0.40` | `3.0%` | `97.0%` |
| `0.50` | `5.5%` | `94.5%` |
| `0.60` | `8.5%` | `91.5%` |
| `0.75` | `13.7%` | `86.3%` |
| `0.80` | `15.6%` | `84.4%` |
| `1.00` | `24.0%` | `76.0%` |

Integrity clamps to `[0,1000]`. Zero condition remains deliverable in this
forgiving proof; it never creates a mid-route deletion.

## Drift, Hop, and landing contract

The only damage inputs are a fresh impact-count increment and its matching
severity. Speed, sideslip, Drive duty, steering, transform, braking, elapsed
time, support transitions, Hop count, paint, and trail never enter the curve.

- A clean long drift with no increment loses exactly `0%`.
- Hop start is condition-neutral.
- A clean landing with no increment, or an increment at/below the calibrated
  dead zone, loses `0%`.
- A poor landing may lose cargo only through the same peak curve as a wall
  strike. There is no second landing rule.
- If a visibly hard landing produces no usable impact observation, stop on an
  observation limitation instead of inventing vertical-speed damage.

Although Hop does not damage cargo, a new `hop_count` increment invalidates the
current unloading sample. This prevents the pre-move support observation on a
Hop-start tick from falsely completing a delivery. The next UI reason is the
ordinary `TOUCH DOWN`, not an impact penalty.

Only a strictly positive curve increment produces `CARGO MOVING — STABILIZE`
and breaks settle. A recorded zero-loss contact does not flicker unloading.

## Calibration boundary

The exact values above are coherent seeds, not human feel authority. A later
exact-engine capture may vary one field at a time only within:

| Parameter | Bounded study range |
| --- | ---: |
| Dead zone | `0.18–0.23` severity |
| Maximum episode loss | `20–28%` |
| Exponent | `1.35–1.70` |
| Quiet window | `0.20–0.30 s` active time |

The clean class must include long Drive drift, ordinary turning/braking,
supported Hop and landing, and ordinary rough-route travel. The error class
must include a light brush, controlled glance, poor landing, direct strike,
and sustained wall pressure.

Stop rather than tune around any of these:

- any clean class loses cargo;
- a recognizable controlled strike never separates above the dead zone;
- observer priority misses or jumps counters;
- one wall contact repeatedly splits into separate charges;
- distinct incidents are routinely merged closely enough to feel dishonest;
- `30/60/120 Hz` representations differ by one integrity unit;
- landing is charged by impact plus another rule;
- reset can preserve payout eligibility; or
- the HUD makes the owner avoid the established long drift or lowers ordinary
  route speed by roughly `15%` or more.

If the time-only episode rule cannot separate the native maneuvers, the next
step is a separately authorized behavior-neutral, source-bound observation
record—not a route-specific filter or R7 movement edit.

## Paint contribution — Kiln Manifest

An original high-integrity commendation finish inspired by fired ceramic and
inspection marks, without implying mechanical protection:

| Role | Color | Emission multiplier |
| --- | --- | ---: |
| Frame | `#211F24` carbon | `0.20` |
| Shell | `#5E5855` basalt taupe | `0.28` |
| Lift | `#C8BDAB` warm ceramic | `0.44` |
| Underlay | `#3C3849` graphite violet | `0.36` |
| Trim/seams | `#AA9AD1` inspection violet | `0.60` |
| Drive can | `#686171` plum gunmetal | `0.32` |
| Derived joint target | `#35313E` | `<=0.28` |

Energy, nozzle, bore, metallic behavior, roughness, and state cues remain fixed.
Reward copy may say `earned for an intact delivery`; it must never say
`protective`, `reinforced`, or `damage resistant`.

Reject if the pale lift disappears against walls, trim blooms, grayscale role
separation fails, functional orange/cyan/amber/red cues lose priority, or a
player expects an integrity buff. It remains research-only pending native pose
and cue review.

## Trail contribution — Manifest Stitch

Alternating parcel-seam kite marks trace the craft's completed path without
communicating cargo condition:

- one preallocated `MultiMeshInstance3D`, maximum 16 solid marks;
- fixed spine history, alternating `+/-0.145 m` port/starboard;
- each mark `0.055 x 0.120 m`, path-tangent aligned;
- `1.05 m` world-distance spacing, maximum `18 m`, `0.52 s` history;
- violet `#B8A7DD` and cool silver `#B4BCC3`;
- invisible through `5 m/s`, full by `14 m/s`, head alpha `<=0.48`, tail zero;
- depth test on; depth write, shadow, GI, lights, collision, and gameplay query
  off;
- fixed storage, no per-frame node/resource allocation, and all ordinary trail
  reset/pause/teleport guards; and
- reduced motion: `0.24 s`, at most 7 marks, `1.60 m` spacing, alpha `<=0.26`.

Reject it if it resembles route guidance, lane paint, dropped cargo, debris, or
an integrity meter; aliases at Drive speed; shows through walls; leaves a
teleport streak; exceeds the existing frame budget; or needs greater density to
read. It remains deferred until the three-job feel gate requests a trail.

Visual mockup: `concepts/ITERATION_02_KILN_MANIFEST_STITCH.svg`  
SHA-256: `9ebe3ce2bdf2ec82aee3a24a7aa5dd69e1e1c7167468614953d0feff0b8f7380`

## Deterministic evidence

Command:

```text
PYTHONPATH=tools python3 -B tools/test_iteration_02_cargo.py \
  --report analysis/ITERATION_02_CARGO_REPORT.json
```

Result: `64/64 PASS`.

Report SHA-256:
`7cab0aea8e894afc038d6476186103cebe832e3ff190ce0e8b8e25deda50b096`

The report covers every severity milli for monotonicity and cap behavior,
sticky snapshots, fresh counter epochs, sub-dead-zone contact, rising/falling
peaks, exact quiet-window boundaries, separate incidents, pause/resume,
Hop/landing semantics, reset precedence, post-terminal immutability, invalid
observations, integrity clamp, and rate-equivalent wall pressure.

The same generated report was byte-identical across two executions. These pure
vectors do not prove native impact separation, visual fairness, cargo anxiety,
or exact Godot process ordering.

R7 source/player bytes remain untouched.
