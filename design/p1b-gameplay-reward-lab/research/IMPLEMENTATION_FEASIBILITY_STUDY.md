# District Zero P1B — Implementation Feasibility Study

Status: `DESIGN/ARCHITECTURE STUDY — NO R7 SOURCE CHANGE`

Read-only baseline:
`District-Zero-P1A-v1.2.8-Vehicle-Integration-R7-Run-1/District-Zero-P1A-v1.2.8-Vehicle-R7-Player`

This study asks for the smallest credible route from the verified R7 player to
a courier-game vertical slice. It does not authorize P1B, alter R7, or treat a
design recommendation as a passed feel gate.

## Executive finding

The courier loop is practical without changing movement, collision, terrain,
camera, routes, or the R7 craft. The world already contains almost all of the
hard spatial machinery the loop needs:

- six exact destination pads (`CLN`, `DEP`, `MRK`, `QRY`, `RLY`, `WRK`);
- 17 bidirectionally usable routes with exact endpoints and baked lengths;
- exact junction and gate polygons;
- genuine route-entry and traversal events;
- a live telemetry signal that does not require consuming the bounded evidence
  queue;
- a controller-owned, physics-resolved impact severity and impact counter;
- reset/fall events;
- route highlighting on the existing map; and
- a render-only 56-mesh vehicle rig with a small, explicit material vocabulary.

The smallest safe product shape is therefore **a new P1B scene and game-layer
sibling around the unchanged R7 craft/world**, not a rewrite of the controller
or world builder. Keep the R7 scene runnable as a regression fixture. A P1B
scene can instantiate the same craft, world, camera, telemetry, and map, then
add a contract session, UI, destination-marker layer, and cosmetics.

There is no blocking geometry deficiency for endpoint contracts. There are
four integration risks that must be solved explicitly before scoring can be
trusted:

1. raw `COLLISION_SAMPLE` events are contact samples, not crash episodes;
2. telemetry inherits the root's always-processing mode and its physics tick is
   therefore unsuitable as billable elapsed time while paused;
3. the diagnostic spawn/reset path can teleport and change the craft spawn,
   so it must be inaccessible in the P1B scene and any active reset must have a
   terminal contract rule; and
4. consuming a UI input event does not stop `CraftController` from polling the
   same held action in physics, so modal close needs a neutral-release latch.

These are tractable integration issues, not reasons to touch movement.

## Evidence-backed inventory

| Existing fact | Safe gameplay use | Important limit |
| --- | --- | --- |
| `P1AWorldData.manifest.destination_pads` has six pads with centers and `inner_flat_radius_m: 8.0` | pickup/drop-off containment and world marker placement | `PAD_*` geometry is the full 13 m blend disc; use the 8 m inner-flat radius for controlled delivery |
| `P1AWorldData.geometry_contains()` | gates, junctions, full pad masks | XZ-only; delivery must separately require support and low tangential speed |
| `P1ATelemetry.event_emitted` | subscribe live to route, gate, reset, Hop, surface, and collision observations | never call `drain_events()` from gameplay; that queue is evidence infrastructure and is capped at 256 |
| `ROUTE_STATE ENTERED/TRAVERSED` | authored-route modifiers and route progress | `TRAVERSED` omits direction; direction must be normalized in a P1B adapter and tested both ways |
| `GATE_CROSSED` includes ID and direction | gate-required contracts | a gate crossing alone does not prove a full route |
| `CraftController.telemetry()` exposes tangential speed, support, form, impact severity/count, Hop count, reset count | settle gate, cargo shock, HUD | it is a current snapshot, not an event ledger |
| `impact_count` increments after the controller's strongest resolved impact and `last_impact_severity` is normalized | one authoritative shock observation per physics step | consecutive increments during one wall-hugging contact must be grouped into one impact episode |
| `reset_performed` plus telemetry `RESET` | deterministic abort and trail clearing | `impact_count` and Hop count reset to zero; observers must reset their baselines too |
| `P1AMap.set_highlighted_routes()` | highlight the accepted contract's authored route | the diagnostic menu also writes highlights; disable its inputs in P1B |
| `VehicleVisualRig` has reserved dynamic energy/nozzle materials | paints on the other material roles | cosmetics must never overwrite Spread/Drive/caution/strike cues |
| existing `SurfaceFeedback3D` uses 128 GPU particles at 30 Hz | establishes that a modest presentation emitter path works | it is not a trail performance budget; dust plus trail must be profiled together |

## Recommended product boundary

### Preserve verbatim

Keep these R7 concerns byte-identical in the first P1B branch:

- `CraftController` physics, input math, collider/probes/cast, reset transform,
  tuning, and movement helpers;
- world manifest, generated route/terrain/solid artifacts, world builder, and
  camera;
- R7 vehicle geometry and transformation choreography; and
- the existing P1A runtime scene as a regression fixture.

The new branch may observe public craft state, subscribe to telemetry, add
presentation-only children/siblings, and provide a separate main scene. A
clean movement comparison must still produce zero delta.

### New main scene, not an invasive root rewrite

Create `scenes/district_zero_p1b.tscn` from the existing scene structure and
retain `scenes/district_zero_p1a.tscn` unchanged. The P1B scene adds:

```text
DistrictZeroP1B
├── existing World / Craft / CameraRig / SurfaceFeedback / Telemetry
├── GameplaySession
├── DestinationMarkers                 # visual only
├── CosmeticTrail                      # visual only
└── UI
    ├── ContractHUD
    ├── InteractionPrompt
    ├── ContractBoard
    ├── ResultPanel
    └── GaragePanel
```

The least fragile root arrangement is a small P1B root adapter that extends
`P1AWorldGate`, calls the inherited setup, then suppresses the owner-review and
diagnostic presentation. It should not duplicate world construction. The
diagnostic actions (`TAB`, bracket selection, diagnostic spawn) must be
intercepted/disabled in this scene so no player path can change the spawn
transform or teleport during a contract.

The original P1A pause panel conflicts visually with gameplay modals because
the inherited root makes it visible whenever the tree is paused. The P1B root
adapter should make pause-panel ownership explicit rather than relying on child
process order to hide it one frame later.

## Small, testable file boundaries

Avoid a framework. Eight runtime scripts, two pure rule modules, two data files,
and one scene are enough for the complete first slice.

| Proposed file | Responsibility | Must not know about |
| --- | --- | --- |
| `gameplay/contract_catalog.gd` | load and validate stable contract records against node/route IDs | UI nodes, player balance, save I/O |
| `gameplay/contract_rules.gd` | pure grade, integrity, payout, unlock, and result calculations | Godot scene tree and input |
| `gameplay/impact_episode_tracker.gd` | pure reducer from impact observations to monotone cargo-damage deltas | credits, routes, UI |
| `gameplay/contract_session.gd` | one attempt state machine; elapsed time, odometer, route/gate/Hop evidence, pickup/drop settle, reset outcome | material mutation and file I/O |
| `gameplay/profile_state.gd` | credits, reputation, owned/equipped cosmetic IDs, idempotent award ledger | nodes and disk paths |
| `gameplay/profile_store.gd` | optional versioned profile read/validate/write with injectable path | scoring decisions |
| `ui/gameplay_ui.gd` | render immutable session/profile view models and emit intentions | scoring math and craft writes |
| `ui/p1b_input_router.gd` | contextual interaction, modal pause ownership, neutral-release resume | payout and integrity math |
| `presentation/destination_marker_layer.gd` | non-colliding pickup/delivery emphasis at existing node centers | contract adjudication |
| `presentation/vehicle_paint_controller.gd` | explicit role registry and cached material copies, excluding energy/nozzle/bore | movement and reward calculation |
| `presentation/cosmetic_trail_3d.gd` | bounded render history, reset/teleport clearing, equipped trail style | collision, route detection, scoring |
| `data/contracts_v1.json` | curated contract IDs, endpoints, authored paths/distances, pars, modifiers | executable code |
| `data/cosmetics_v1.json` | stable IDs, prices, unlock predicates, paint/trail resource paths | arbitrary scripts or shaders |

`contract_rules.gd`, `impact_episode_tracker.gd`, and `profile_state.gd` should
be deterministic reducers with dictionary/value inputs. They can then be tested
headlessly without constructing the world.

## Runtime state machine

Use one explicit state and reject transitions not in this table:

| State | Entry | Valid exits |
| --- | --- | --- |
| `FREE_ROAM` | launch, result dismissal, or abort acknowledgement | `BOARD_OPEN` when supported and settled inside a destination's 8 m inner pad |
| `BOARD_OPEN` | contextual interact at a pad | `FREE_ROAM` on cancel; `ACTIVE` on valid contract accept |
| `ACTIVE` | accepted contract snapshot and attempt ID are frozen | `DELIVERY_SETTLE` while inside target pad under settle limits; `ABORTED` on manual/fall reset; remain active on ordinary impact |
| `DELIVERY_SETTLE` | supported, within inner pad, below speed limit | `ACTIVE` immediately if any condition breaks; `RESULTS` after the continuous settle duration |
| `RESULTS` | one immutable result and one idempotent reward commit | `FREE_ROAM` on continue, optionally opening the destination's board afterward |
| `ABORTED` | active reset or unrecoverable validity failure | `FREE_ROAM` after acknowledgement; no payout or reputation |

The initial slice does not need a countdown, cargo rigid body, fail timer, or
loading animation. Accepting at rest is the start. The player can choose any
physical path unless the selected contract explicitly registers a gate or
route requirement.

### Pickup and delivery tests

Use the manifest's pad center plus its `inner_flat_radius_m` rather than adding
new physics areas. A valid pickup interaction requires:

- XZ distance to pad center no greater than 8 m;
- at least two valid support probes;
- finite measured height;
- tangential speed at or below the pickup threshold; and
- an explicit interaction press.

A valid delivery sample uses the same spatial/support checks and its own low
speed threshold. It must remain valid for a continuous settle interval. Exit,
speed rise, loss of support, pause, or non-finite state resets the settle timer.
Pause must neither advance nor reset an otherwise valid settle streak.

This prevents airborne fly-through completion and avoids accidentally
completing on the 8–13 m terrain blend around a pad.

## Safely deriving route direction and requirements

The current telemetry proves genuine route entry and traversal, but its public
event omits `origin_node` and `destination_node`. Do not infer direction from
velocity heading; drifting makes heading an unreliable course indicator.

The P1B adapter can recover direction without changing R7:

1. on `ROUTE_STATE:ENTERED`, read the route's `from_node` and `to_node`;
2. compare the event's exact `entry_crossing_xz_m` with those two node centers
   and register the nearer endpoint as the attempt-local origin;
3. on the matching `TRAVERSED`, accept only the opposite endpoint, which is
   already implied by P1A's traversal rule; and
4. emit an internal immutable tuple
   `(route_id, origin_node, destination_node, entry_tick)`.

Test every registered route in both directions. Reject a route record if the
entry point is not unambiguously closer to one endpoint. This is safer than
reimplementing P1A's route-envelope winner or calling its underscore-prefixed
helpers.

For an eventual telemetry cleanup, adding origin/destination fields to the
observational payload would be useful, but it is **not required** for the first
P1B slice and must never become permission to alter route logic.

Endpoint-only jobs naturally collapse to shortest paths. Authored HOP, `DOG`,
`A1`, `A2`, or `X0` jobs must therefore freeze an ordered route requirement or
a gate requirement and price the authored distance. The runtime should collect
traversals; it should not recalculate a route price from where the player
actually drove.

## Cargo integrity: use impact episodes, not contact counts

### Why raw collision telemetry is unsafe

`P1ATelemetry._observe_collisions()` emits at most one sample per hard source
**per physics tick**. Hugging one wall can consequently produce many samples.
The list is also intentionally limited to five P1A hard-authority sources and
does not cover every building or terrain impact. Counting those events as
damage would punish wall contact according to frame duration, miss other real
shocks, and create an obvious integrity exploit/inconsistency.

The controller already makes the better mechanical observation. After
`move_and_slide()`, it computes the strongest closing impact, applies the
existing response, increments `impact_count`, and exposes normalized
`last_impact_severity`, closing speed, loss, retention, and whether the craft
was in Drive. P1B should observe this snapshot at a physics priority later than
the controller. It must not write any controller value.

### Minimum episode reducer

At contract acceptance, snapshot `impact_count`. Each later increment yields
one observation containing attempt-local physics step, severity, closing speed,
and Drive state. Group observations separated by no more than a short,
preregistered quiet window into one impact episode.

Apply cargo damage from the **peak severity of the episode**, not its sample
count. To provide immediate feedback without double charging, make damage
monotone:

```text
new_damage = damage_curve(new_peak_severity)
apply max(0, new_damage - damage_already_applied_for_this_episode)
```

This gives immediate feedback on the first strike, adds only the difference if
the same contact becomes worse, and makes a sustained wall-hug independent of
how many physics frames it lasts. Pure drifting with no impact increment causes
zero damage. Mild support contacts below the damage curve's dead zone also
cause zero damage.

The quiet-window length and damage curve are tuning questions, not movement
changes. They require synthetic streams plus human wall/glance/landing trials.
If controller impact increments prove noisy on ordinary rough driving, stop and
calibrate the cargo dead zone; do not filter by route or silently change the
controller response.

### Collision-specific blockers to prove before tuning

- Pause while touching a wall: confirm whether the last slide collision remains
  observable while always-processing telemetry continues. The game layer must
  ignore gameplay observations while paused regardless.
- Two colliders in one physics step: controller authority is the strongest
  impact only; cargo must not invent two shocks from telemetry samples.
- Repeated thrust into one wall: verify the episode quiet window produces one
  peak-based damage charge.
- Wall separation and a genuine second hit: verify the second episode opens.
- Rough landing: measure controller severity before selecting a dead zone.
- Reset in an open episode: active reset aborts, clears the reducer, and awards
  nothing.

## Reset and anti-teleport semantics

For the first slice, the safest rule is simple:

- reset in `FREE_ROAM`: ordinary R7 reset;
- manual or fall reset in `ACTIVE`/`DELIVERY_SETTLE`: **abort the attempt, no
  credits, no reputation, no result grade**;
- reset from a gameplay modal: modal closes into an abort acknowledgement;
- reset never rewinds time, restores integrity, changes a contract origin, or
  retains route-requirement progress.

This is stricter but substantially clearer than trying to price a teleport.
An abandon/recovery system can be designed later. The diagnostic menu and
diagnostic spawn actions must be unreachable in the P1B scene; otherwise the
existing `set_spawn_transform()` path can permanently redirect subsequent R
resets and invalidate all contract evidence.

Every attempt gets a monotonically increasing session `attempt_id`. Terminal
handling is idempotent: a duplicate event, repeated settle sample, result-panel
input repeat, or scene notification cannot award twice.

## Time, distance, and pause ownership

Do not use `P1ATelemetry.physics_tick` differences as delivery time. The root
sets `PROCESS_MODE_ALWAYS`, telemetry inherits that mode, and telemetry has no
pause early-return. Its counter can therefore continue while gameplay is
paused. The session should accumulate its own physics `delta` only while state
is `ACTIVE` or `DELIVERY_SETTLE` and the tree is not paused.

Similarly, the attempt odometer should sum finite, continuous XZ craft-position
deltas once per active physics step. It is an outcome statistic and efficiency
input only. Contract price comes from the frozen authored distance. An active
reset aborts before the teleport delta can enter the odometer.

Never consume or clear telemetry's 256-event queue. Connect to
`event_emitted`, reduce only events relevant to the active attempt, and keep a
small attempt-owned ledger.

## Modal input and runtime-menu robustness

The contract board and result panel should pause the scene tree and be owned by
an always-processing input/UI coordinator. There is one non-obvious Godot input
trap: `set_input_as_handled()` prevents later unhandled callbacks, but it does
not make a held action disappear from `Input.is_action_pressed()` or
`get_action_strength()`. The craft polls those APIs every physics step.

Therefore closing any modal must enter `WAITING_FOR_NEUTRAL`, keep gameplay
paused, and resume only when throttle, brake, steer, transform, Hop, accept, and
cancel are all released. This is especially important if gamepad A is both UI
accept and the craft's transform action. Without the latch, accepting a job can
launch directly into Drive and dismissing results can arm an unintended Hop or
form change.

Use a contextual `interact` action (`E` plus one currently unused gamepad
button) and normal Godot UI navigation while paused. Do not use W/S for board
selection unless the neutral latch covers their release. Modal ownership must
also suppress the inherited generic pause panel so overlays do not stack.

## Results, rewards, and idempotence

At successful settle completion:

1. freeze an immutable `AttemptSummary` (contract identity hash, elapsed,
   odometer, integrity, impact episodes, traversals, gates, Hops, resets=0);
2. run the pure evaluator exactly once;
3. produce an immutable `RunResult` with an explicit component breakdown;
4. apply its credit/reputation award to `ProfileState` using `attempt_id` as an
   idempotency key; and
5. show the already-committed result.

The UI must never recompute money. A result should expose base distance value,
time band, integrity band, small capped efficiency/requirement modifiers, final
grade, credits, reputation, and newly unlocked items. Integer credits and
explicit rounding at one final step avoid platform-dependent presentation
drift.

Reject these farming paths in tests:

- repeated delivery-zone samples;
- opening/closing results repeatedly;
- retrying or reloading a completed attempt ID;
- driving extra loops to inflate distance payout;
- accepting away from the registered origin;
- diagnostic spawn/reset after accept;
- completing at the outer pad blend or while airborne; and
- traversing a required route in the wrong direction.

## Cosmetics and performance boundary

### Paint

Paint is low risk if the controller never knows it exists. Resolve explicit
mesh paths by material role, make one cached `StandardMaterial3D` copy per
paint role, and assign those copies to the registered meshes. Never recolor
`Material_energy`, `Material_nozzle`, or `Material_bore`; the first two carry
Spread/Drive/caution/strike state and the bore must remain dark. Do not allocate
materials per frame or discover paint roles by fuzzy names.

### Trail

The first trail should be one bounded render-history implementation, not three
different effect systems. Two camera-facing ribbons sampled at 30 Hz, at most
32 samples per anchor, and at most 0.75 s of history are a credible starting
budget. Styles should vary palette, width, segmentation, and fade on that same
core. A small particle companion may be used by one style only after profiling.

The trail must:

- live outside the craft physics subtree;
- sample interpolated presentation transforms only;
- clear on `reset_performed`, attempt teleport, scene change, or an impossible
  one-frame anchor displacement;
- stop sampling while paused;
- cast no shadows, contribute no GI, have no collision, and keep depth testing;
- use a hard vertex/sample cap; and
- never feed a history point back to gameplay.

R7 already emits up to 128 surface-feedback particles. Test trail plus maximum
surface spray together at native `1280×720` Forward+, not on an empty pad. A
particle count alone is not performance proof. Record CPU frame time, GPU frame
time, physics-step health, and allocation growth during a 120-second fast
drift, then repeat with trail off. The acceptance goal should be an explicit
small frame-time delta and zero movement-trace delta, finalized only on the
target Mac.

## Save path: design now, ship after loop acceptance

The current lab correctly defers durable saving until the reward cadence is
fun. Still, `ProfileState` should use stable IDs and a versioned serializable
shape from day one so persistence is not a rewrite.

Recommended initial schema:

```text
schema_version
credits
reputation
owned_paint_ids
owned_trail_ids
equipped_paint_id
equipped_trail_id
completed_contract_ids / best_grade_by_contract
recent_awarded_attempt_ids   # bounded idempotency ledger
```

First gameplay review can use an in-memory store and label progression as
session-only. After the loop/economy is approved, `ProfileStore` may write a
validated JSON document under `user://` using a temporary file, flush/close,
then replace the primary while retaining one last-known-good backup. Invalid,
unknown, duplicate, negative, or unbounded values must be rejected or clamped
by the schema validator; unknown cosmetic IDs fall back to District Standard
and trail off.

Tests must inject a temporary absolute store path. Never let headless tests
touch the owner's real `user://` profile. Saving should occur on a committed
award, purchase, equip change, and orderly quit—not every frame.

The save file is not an anti-cheat boundary. Its purpose is crash recovery and
stable ownership, not cryptographic trust.

## Deterministic verification plan

### Pure rule suite

- all legal and illegal state transitions;
- settle streak exact-boundary, break, pause, unsupported, non-finite, and
  outer-blend cases;
- time bands and final rounding at every boundary;
- integrity damage curve at dead-zone/full-loss boundaries;
- impact grouping: long wall contact, rising peak, quiet separation, second
  impact, simultaneous observations, and reset;
- payout independent of actual odometer except the explicitly capped
  efficiency component;
- ordered route requirements in both directions and wrong-way rejection;
- one terminal result and one award per attempt ID;
- unlock and purchase exact-credit boundaries;
- invalid catalog/profile records; and
- canonical serialization round trips.

### Headless integration suite

- P1B scene imports/parses on exact Godot;
- origin prompt appears only when spatial/support/speed conditions are true;
- modal pause plus neutral-release latch for keyboard and gamepad;
- accepted contract freezes identity, route list, par, and price;
- active timer excludes modal/pause time;
- manual and fall resets abort with zero award;
- diagnostic actions cannot open/spawn in P1B;
- route traversal adapter proves every route both directions;
- map highlights only the current authored routes and clears terminally;
- result repeat cannot double-award;
- session profile purchase/equip validation;
- trail clears on reset/teleport and stays bounded; and
- gameplay runs with the telemetry queue already full, proving live signal use.

### Preservation and native checks

- all frozen movement/world/tuning/camera files compare byte-for-byte with R7;
- existing R7 verification and runtime vectors remain green;
- C1 movement traces remain raw-identical / maximum delta `0.0`;
- cosmetics on/off produce the same movement trace;
- three paints in Spread/midpoint/Drive plus caution/strike native captures;
- three trails at rest, ordinary travel, sustained drift, reset, pause, and
  wall occlusion;
- native 120-second worst-case trail+surface-spray performance capture; and
- human review of pickup clarity, settle patience, impact fairness, reward
  cadence, and whether long drift remains joyful rather than punished.

## Phased implementation estimate

These are focused engineering-day ranges for the current unusually rigorous
verification standard, not elapsed calendar promises. Human tuning cycles are
separate.

| Phase | Deliverable | Estimate | Gate |
| --- | --- | ---: | --- |
| 0 | immutable R7 comparison, new P1B scene/root, exact-engine import and baseline harness | 0.5–1 day | R7 checks and C1 green before gameplay |
| 1 | contract/catalog/profile value objects, pure state/evaluator/impact tests, curated 3-job fixture | 1–2 days | all boundary tables executable |
| 2 | pad interaction, board, active HUD, timer/odometer, map highlighting, settle/results, reset abort | 2–3 days | one endpoint contract repeatably playable |
| 3 | impact episode integration and two cargo profiles; route-direction adapter and authored HOP/long-route job | 1.5–2.5 days | drift false-positive and wall episode evidence green |
| 4 | session credits/reputation, small garage, purchase/equip, three paints | 1.5–2.5 days | no duplicate awards; native cue captures green |
| 5 | one bounded trail core plus three styles and worst-case profiling | 2–3 days | explicit performance and zero-delta movement gates |
| 6 | durable save/backup/migration after economy approval | 1–2 days | corrupt/truncated/unknown-ID recovery green |
| 7 | full regression, native captures, packaging, owner playtest card | 2–3 days | stop for human gameplay/reward gate |

Practical totals:

- **first playable contract loop, session-only rewards, no trails:** about
  5–8 focused days;
- **credible vertical slice with route jobs, cargo, results, three paints and
  three trail styles:** about 10–15 focused days; and
- **same slice with durable saves and full release-style evidence:** about
  12–18 focused days.

Expect at least two owner playtest/tuning cycles after the first playable loop.
Payout numbers, settle duration, cargo dead zone, and trail readability cannot
be truthfully finalized from static analysis.

## Recommended first implementation cut

Do not build the shop, save file, and three trails before proving delivery is
fun. The strongest first cut is:

1. new P1B scene around byte-identical movement/world source;
2. three curated contracts: one short local, one medium route-learning job, and
   one longer Drive-commitment job;
3. abstract integrity driven by peak-based impact episodes;
4. controlled 8 m inner-pad delivery settle;
5. explicit results with session credits/reputation;
6. District Standard plus one reward paint as proof of the reward bridge; and
7. a playtest stop.

After that gate, add the complete three-paint/three-trail launch set and only
then durable saving. This ordering tests the main game rather than asking
cosmetics to conceal an unproven loop.

## Truthful blockers and open human questions

No current blocker requires changing movement or world geometry. Before cargo
tuning is accepted, however, exact-engine evidence must answer:

- Does `impact_count` remain quiet during ordinary long drift and rough-route
  travel?
- What episode quiet window makes a wall scrape read as one mistake while two
  real crashes remain two mistakes?
- How low can delivery speed be before settling feels like parking rather than
  momentum control?
- Does an active reset abort feel clear and fair?
- Can route-required jobs be understood from map highlighting without arrows
  or excessive HUD text?
- Do the paint/trail rewards remain legible without competing with hazard
  energy cues or harming performance?
- Does the first trail arrive soon enough to make credits feel meaningful, but
  late enough that the player understands the base craft?

If paused-on-contact observation, impact noise, or gamepad modal release fails
its focused proof, stop and repair the **P1B observer/input layer**. Do not tune
around it by changing collision, movement, routes, or the R7 controller.
