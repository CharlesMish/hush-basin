# District Zero P1B — Paint and Trail Cosmetics Reward Study

Status: `DESIGN STUDY — NO R7 SOURCE CHANGE`

Baseline inspected: `District-Zero-P1A-v1.2.8-Vehicle-R7-Player`

Purpose: identify a small, high-value cosmetic reward set that makes deliveries
feel materially rewarding while remaining entirely presentation-only. This
study does not authorize a progression implementation, does not change Vehicle
R7, and does not treat cosmetics as a substitute for the contract loop.

## Recommendation in one page

The R7 craft is unusually well suited to cosmetic rewards. Its 56 visible mesh
instances already resolve into a small number of shared material roles, and its
Spread-to-Drive transformation exposes different surfaces over time. A good
finish therefore reads as a coordinated livery rather than a flat color swap:
Spread emphasizes the four lift leaves and their bright seams; Drive folds
those surfaces inward, reveals more underlay and joint work, and extends the
moving propulsion can.

The first reward slice should ship:

1. three coordinated paint finishes: **Orchid Static**, **Saltglass**, and
   **Ember Relay**;
2. three independently equippable trails: **Twin Vector**, **Courier Pulse**,
   and **Comet Ledger**;
3. the existing District Standard finish and `TRAIL OFF` as permanent free
   defaults;
4. one free finish choice after the first successful delivery; and
5. enough ordinary earnings to buy one trail after roughly two more clean
   standard deliveries.

That is enough variety to make credits tangible without turning the first
gameplay milestone into a shop project. Paint and trail selection should remain
independent, deterministic, non-random, and free of stat changes.

The strongest trail architecture for the first slice is a tiny render-history
system using two camera-facing `ImmediateMesh` ribbons. It directly celebrates
the game's best emergent pleasure: a long drift produces a long, readable
curving wake even when the craft's heading points elsewhere. A small
`GPUParticles3D` companion can support the third style, but should not be the
foundation for every trail.

## Inspected R7 presentation facts

### Mesh and material inventory

`scenes/vehicle_visual.tscn` contains 56 `MeshInstance3D` nodes under
`VisualRoot` and no physics nodes. Eleven shared material roles account for all
of them:

| Existing role | Meshes | Visible use | Cosmetic disposition |
| --- | ---: | --- | --- |
| `Material_structure` | 8 | keels, bulkheads, shrouds, bay rails | paint channel: frame |
| `Material_shell` | 1 | forward body | paint channel: shell |
| `Material_lift` | 4 | four primary lift leaves | paint channel: lift face |
| `Material_lift_edge` | 4 | four outer vane tips | paint channel: trim |
| `Material_lift_underlay` | 4 | undersides revealed by choreography | paint channel: underlay |
| `Material_panel_seam` | 16 | top and underside vane seams, knuckles | paint channel: trim |
| `Material_joint` | 14 | sockets, hinges, bridges, bay cheeks | derived dark joint finish |
| `Material_can` | 1 | moving axial-drive can | paint channel: drive can |
| `Material_energy` | 2 | forward energy core and fixed drive core | **reserved functional cue** |
| `Material_nozzle` | 1 | moving nozzle ring | **reserved functional cue** |
| `Material_bore` | 1 | dark nozzle interior | fixed; never recolor |

The existing rig dynamically changes the two energy meshes and nozzle ring
through these functional states:

- Spread: orange;
- Drive: cyan;
- hazard caution: amber; and
- strike: red.

Cosmetics must never overwrite these three materials, their state transitions,
or their emission response. Paint may be warm, cool, or red-adjacent elsewhere
on the craft, but the functional cores must remain the brightest, most
saturated local cue and must pass native capture review in all four states.

### Choreography opportunities

- The four primary leaves dominate the Spread silhouette.
- Their darker underlays become more visible during folding.
- Sixteen seam/knuckle pieces create a strong coordinated accent system.
- The moving can travels from local `z=0.47` to approximately `z=0.98` only at
  the late Drive stage.
- The rear of the craft is local positive Z; the desired chase view sees the
  aft bulkhead, moving can, and rear lift rigs.
- The current native captures show the craft at a relatively small on-screen
  size. Broad material-role contrast and trail silhouette matter more than
  tiny decals or texture detail.

This favors coordinated six-channel finishes and rules out spending the first
slice on stickers, tiny markings, micro-patterns, or text.

## Non-negotiable presentation-only boundary

The cosmetic system may:

- duplicate and recolor render materials beneath `VisualRoot`;
- add render-only marker anchors beneath `VisualRoot`;
- read interpolated display transforms, form amount, reset events, and speed
  for presentation timing;
- create non-colliding meshes or particles in a presentation sibling; and
- save/equip cosmetic identifiers when a later save authority exists.

It may not:

- add or alter a collider, probe, cast, collision mask, physics layer, input,
  velocity, force, transform timing, movement coefficient, camera behavior, or
  world geometry;
- write any value back to `CraftController`;
- use a trail as a collision sensor or route detector;
- alter the existing energy/hazard/strike colors;
- change payout, grade, cargo integrity, or contract state based on what is
  equipped; or
- make an expensive cosmetic render path that changes gameplay performance in
  a meaningful way.

The mechanical acceptance test is simple: the same no-input and C1 movement
traces with every cosmetic disabled and enabled must remain byte-identical,
with maximum movement delta `0.0`.

## Proposed paint architecture

### Data model

Use one small typed `Resource`, tentatively `VehiclePaintProfile`, containing:

- stable `id` and display name;
- `frame`, `shell`, `lift`, `underlay`, `trim`, and `drive_can` authoring colors;
- optional low-emission multipliers per role, bounded by a global cap;
- preview sort order and unlock metadata; and
- accessibility tags such as `LIGHT_FINISH`, `DARK_FINISH`, `WARM`, `COOL`,
  and `HIGH_SILHOUETTE_CONTRAST`.

The joint color should be derived from the frame and trim, rather than exposed
as a seventh user-facing swatch:

`joint = frame.lerp(trim, 0.18)`, then darkened slightly in authoring space.

This keeps each finish coherent while preserving the joints' distinct
metallic/roughness role. `Material_bore` remains fixed near-black.

### Runtime binding

A new presentation-only component should own paint application. It can live as
a child of `VehicleVisualRig`, but the craft controller should not know it
exists. At `_ready()` it should:

1. resolve the explicit mesh paths registered for each paint role;
2. duplicate each active `StandardMaterial3D` once;
3. assign the duplicates back as material overrides;
4. retain the scene's metallic and roughness values; and
5. apply only the selected profile's albedo and bounded low-emission tint.

Do not discover roles by fuzzy node names. Use one explicit path registry and a
semantic test proving exactly 53 paint/fixed meshes plus the three reserved
functional-energy meshes account for all 56 visible meshes.

Do not allocate or duplicate materials per frame. A profile change should
reuse the already-owned duplicate resources. The District Standard profile
must reproduce the R7 scene values exactly.

### Emission policy

Several ordinary R7 materials use subtle emission to keep the small model
legible. A paint system should preserve that design language without making
light-colored finishes glow like the functional energy core.

- Frame and joints: very low emission; energy multiplier at or below `0.32`.
- Shell and drive can: low emission; at or below `0.45`.
- Lift faces and underlays: moderate emission; at or below `0.68`.
- Trim/seams: strongest cosmetic emission; at or below `0.75`.
- Functional cores/nozzle: untouched; their dynamic multipliers retain local
  priority up to the existing `1.45` Drive response.

The profile should store authoring colors, not arbitrary shader code. Initial
finishes should use only `StandardMaterial3D`; procedural patterns and custom
shaders are deferred until the simple finishes are proved valuable.

## Palette catalogue

Hex values below are authoring-preview targets, not final acceptance values.
They require native Forward+ capture at Spread, midpoint, and Drive before
selection. `Joint` is derived as described above. Functional energy and bore
colors are never part of a palette.

### Free reference finish

| Finish | Frame | Shell | Lift | Underlay | Trim | Drive can | Role |
| --- | --- | --- | --- | --- | --- | --- | --- |
| District Standard | `#1B2A32` | `#29404D` | `#2EB8AD` | `#176161` | `#4FF7E8` | `#148C9E` | existing R7 identity; always free |

### Twelve candidate reward finishes

| Rank | Finish | Frame | Shell | Lift | Underlay | Trim | Drive can | Character and likely reward use |
| ---: | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | **Orchid Static** | `#241D30` | `#5C3E73` | `#9B68C4` | `#452F5A` | `#F0B5EB` | `#714D8F` | Dramatically different from the teal default, strong silhouette contrast, and the cleanest separation from all functional cue colors. Excellent first-choice reward. |
| 2 | **Saltglass** | `#202A34` | `#72869A` | `#AFC6D5` | `#3D5364` | `#F2F5E9` | `#506B7E` | Premium pale technical finish. Reads clearly at the current camera distance without becoming pure white. Strong "earned equipment" feeling. |
| 3 | **Ember Relay** | `#251D1C` | `#633C31` | `#B95D3B` | `#4B2726` | `#F1BA72` | `#7C4132` | Warm copper/ember transformation of the vehicle. Very strong contrast with the district, but needs explicit Spread-orange cue testing. |
| 4 | Moss Circuit | `#1F2925` | `#4A6656` | `#7EAD72` | `#344A3C` | `#D2E38C` | `#526F5C` | Calm mineral green with clear value hierarchy. A good integrity/mastery reward. |
| 5 | Oxide Patina | `#2D2422` | `#65483D` | `#A86642` | `#385D58` | `#9FD1BD` | `#7A5545` | Copper and verdigris pairing makes the underlay reveal especially rewarding. Slightly busier than Ember Relay. |
| 6 | Cobalt Parcel | `#18233A` | `#274F86` | `#3D78C5` | `#203B66` | `#C7D7F3` | `#315A92` | Clean courier blue. Familiar and readable, though less distinctive against the current cool environment and Drive cyan. |
| 7 | Lilac Dawn | `#28243A` | `#655E8A` | `#9F98C5` | `#4A456A` | `#F1C0B7` | `#746D9B` | Softer pastel alternative to Orchid Static; inviting rather than aggressive. |
| 8 | Desert Survey | `#2E2821` | `#806B50` | `#C78D5B` | `#594535` | `#EFE0B2` | `#99704E` | Sand, terracotta, and ivory. Reads like well-used field equipment; suitable for distance/route mastery. |
| 9 | Night Courier | `#111820` | `#273449` | `#3F526B` | `#1A2633` | `#B6C4D2` | `#314257` | Near-black stealth finish with silver seams. Attractive, but requires strict dark-background and shadow legibility checks. |
| 10 | Quarry Rose | `#30262A` | `#76515C` | `#B47784` | `#563945` | `#F0D2C2` | `#8B5C66` | Muted rose/stone palette; distinctive without saturated red that could compete with strike feedback. |
| 11 | Monsoon Steel | `#1D282E` | `#455D67` | `#6E8790` | `#344850` | `#C9D9D8` | `#526D76` | Restrained industrial blue-grey. Cohesive but less emotionally rewarding than Saltglass. |
| 12 | Sunline | `#242522` | `#62592F` | `#C6A73D` | `#4D4425` | `#F4E6A1` | `#786834` | Bold yellow-gold finish. High visibility, but caution-amber separation and gold world-marker confusion make it a later candidate. |

### Initial paint selection: strongest 3

Scoring weights: functional-cue safety 30%, distinct reward identity 25%,
district/background legibility 15%, transformation reveal 15%, accessibility
10%, implementation risk 5%.

| Selection | Study score | Why it earns the slot | Required native falsification |
| --- | ---: | --- | --- |
| Orchid Static | 92/100 | Most distinct from R7 and the world; excellent Spread/Drive reveal; functional orange/cyan/amber/red remain locally salient. | Verify pale trim does not bloom or lose seam detail. |
| Saltglass | 89/100 | Communicates a visibly premium reward even at small screen size; value contrast survives the cool-grey district. | Verify pale leaves remain distinct from bright walls and do not clip. |
| Ember Relay | 85/100 | Supplies the warm option the initial set needs and makes the moving can reveal feel substantial. | Verify Spread-orange energy core remains unmistakable at all three poses and in caution/strike states. |

If Ember Relay fails cue separation, replace it with **Moss Circuit** rather
than weakening the functional cue.

## Proposed trail architecture

### Attachment points

Add render-only `Marker3D` anchors beneath `VisualRoot`; markers contain no
collision and never influence choreography.

Initial fixed anchors:

| Anchor | Suggested local position | Purpose |
| --- | --- | --- |
| `TrailPort` | `(-0.24, -0.04, 1.16)` | left rail just aft of the fixed central structure |
| `TrailStarboard` | `(0.24, -0.04, 1.16)` | right rail just aft of the fixed central structure |
| `TrailSpine` | `(0.00, 0.00, 1.36)` | single-center ribbon or particle origin, aft of the fully extended nozzle |

These anchors are intentionally attached to the fixed central structure, not
the folding vane tips. They stay coherent throughout transformation and cannot
intersect wildly during the midpoint pose. Four dynamic vane-tip anchors can
be studied later for `Vane Echo`.

### Recommended history-ribbon core

Create a presentation sibling such as `CosmeticTrail3D` in the district scene.
It holds a read-only path to the craft and the anchor nodes. It must never be
queried by gameplay code.

At render time:

1. sample `Marker3D.get_global_transform_interpolated()` at a bounded 30 Hz or
   after at least `0.30 m` of travel;
2. retain at most 32 samples per anchor and at most `0.75 s` of history;
3. generate two small camera-facing triangle strips in one or two
   `ImmediateMesh` surfaces;
4. taper width and alpha toward the oldest sample;
5. keep depth testing enabled so trails disappear correctly behind walls; and
6. disable shadows, GI contribution, collision, lights, and depth writing.

Godot documents `ImmediateMesh` as suitable for simple geometry that changes
often. Two 32-sample strips are tiny: at most 128 strip vertices before any
style-specific subdivision. The visual is a historical render trace, not a
physics trajectory prediction.

Call `get_global_transform_interpolated()` once during initialization, before
any interpolation reset can occur. Connect `CraftController.reset_performed`
to clear history. Also clear on a one-frame anchor displacement greater than
`8 m`, on scene change, and when the craft is invalid. These guards prevent the
classic teleport-to-spawn streak.

### Segmented and particle companions

- Segmented styles can reuse the same history but omit strip spans according
  to cumulative world distance. Distance segmentation is preferable to rapid
  time flashing: it looks animated while moving and cannot strobe when idle.
- Sparse particles should use one `GPUParticles3D` with `local_coords=false`,
  `fixed_fps=30`, a fixed seed, no collision, and no more than 64 particles.
  In Forward+, `emit_particle()` can place deterministic cosmetic motes at the
  current interpolated anchor.
- Godot's built-in `GPUParticles3D.trail_enabled` plus `RibbonTrailMesh` is
  compatible with Forward+, but it is better reserved for a later experiment.
  It trails individual particles rather than directly representing the craft's
  sampled path, requires `use_particle_trails` on the draw material, and is a
  less transparent foundation for reset and drift-history behavior.

### Trail profile data

`VehicleTrailProfile` should contain only presentation fields:

- stable `id`, display name, architecture enum;
- one or two colors;
- width, history seconds, sample spacing, alpha curve;
- segment length/gap or particle count/lifetime;
- minimum fade-in speed and full-visibility speed;
- preview order and unlock metadata; and
- reduced-motion substitutions.

Every public numeric field must be range-checked. Equipping a malformed profile
falls back to `TRAIL OFF`, never to an unbounded effect.

## Eight trail concepts

| Rank | Trail | Architecture | Visual behavior | Reward strength | Main risk |
| ---: | --- | --- | --- | --- | --- |
| 1 | **Twin Vector** | two continuous history ribbons | Two narrow ice/teal rails trace the true drift path for about `0.62 s`, tapering smoothly to zero. | Directly celebrates the game's long-drift identity; readable but restrained. | Must depth-occlude correctly and clear on reset. |
| 2 | **Courier Pulse** | two distance-segmented history ribbons | Violet-pearl dashes: roughly `0.80 m` visible, `0.45 m` gap, with a soft head-to-tail fade rather than flashing. | Visibly different from Twin Vector while sharing safe machinery. | Segment cadence must not alias or shimmer at high speed. |
| 3 | **Comet Ledger** | one short center ribbon plus fixed-seed motes | A warm-white spine with sparse gold motes peeling away over `0.55 s`. | Feels premium and alive without hiding the road. | Motes must remain distinct from existing grey ground spray and gold node markers. |
| 4 | Prism Fork | two gradient ribbons | Port and starboard use related but distinct hues which converge to pearl at the tail. | Strong screenshot appeal; good high-tier credit sink. | Gradient transparency sorting and color overload. |
| 5 | Echo Chevron | `MultiMesh` history markers | Small translucent chevrons are placed every `1.1 m` and fade through 18 instances. | A graphic, courier-like alternative with clear rhythm. | Orientation around sharp curves and all-or-none MultiMesh culling. |
| 6 | Vane Echo | four short history ribbons from vane tips | Each of the four folding leaves writes a `0.30 s` tracer, making transformation briefly fan the trail. | Makes the vehicle choreography itself collectible. | Four traces become busy and can look broken during folding; later only. |
| 7 | Dust Constellation | fixed-seed billboard motes | Cool star-like dots linger in world space and gently shrink, without a solid ribbon. | Low-obstruction, whimsical option. | Too close to surface spray; potentially weak at the current camera distance. |
| 8 | Slipstream Gates | sparse ring/arc instances | A soft ring or paired arc is left every `3.5 m` along the course and fades over `0.8 s`. | Dramatic mastery reward and clear speed perception. | May read as world checkpoints or a mechanic; defer until contracts establish their own visual language. |

### Initial trail selection: strongest 3

| Selection | Study score | Initial profile target | Why it earns the slot |
| --- | ---: | --- | --- |
| Twin Vector | 94/100 | 2 rails, `0.055 m` width each, `0.62 s`, 32 samples, head alpha `0.58` | Best expression of long drifting; simplest reset semantics; one bounded system. |
| Courier Pulse | 89/100 | 2 rails, `0.065 m`, `0.72 s`, distance gaps, head alpha `0.62` | A genuinely different reward using the same verified path core; no rapid flashing. |
| Comet Ledger | 84/100 | 1 ribbon, `0.075 m`, `0.48 s`, plus <=48 motes at <=`0.42` alpha | Supplies a particle option and a warmer premium fantasy without requiring a second large system. |

If Comet Ledger cannot remain distinct from ground spray in native captures,
substitute **Echo Chevron**. Do not increase particle brightness or count until
it becomes visible; choose the clearer architecture instead.

## Legibility and accessibility contract

### Functional cue protection

- Functional energy core/nozzle materials remain unchanged under every finish.
- Caution and strike must remain recognizable against all paint/trail pairs.
- A trail may not turn red or amber in response to collision; that vocabulary
  belongs to the vehicle's functional cue.
- Trail brightness must not visually exceed the nozzle ring at full Drive.
- Trails are occluded by solid geometry. `no_depth_test` is forbidden.

### Motion and photosensitivity

- Always provide `TRAIL OFF` and a reduced-motion trail intensity option.
- No high-contrast time strobe. Any pulse must be a smooth fade or a
  world-distance pattern.
- Keep repeated contrast changes well below three full on/off cycles per
  second; the initial set does not need any full on/off cycling.
- Reduced-motion mode caps history at `0.28 s`, disables motes, and reduces
  alpha by at least 40%.
- Pause freezes the effect; it does not continue simulating behind a menu.

### Color and shape

- Paint names and shop icons must not be distinguishable only by color text.
- Each trail style must retain a pattern distinction in grayscale: continuous,
  segmented, or mote-assisted.
- Review every paint in Spread/mid/Drive against bright walls, ordinary road,
  dark terrain shadow, and the near-black horizon.
- Review cue states in simulated common color-vision-deficiency views, but use
  native human review rather than treating simulation as a pass.
- A high-contrast accessibility override may strengthen the fixed functional
  core outline, but it must be a global presentation setting, not a purchased
  advantage.

### Screen-space restraint

At native 1280x720:

- the two initial ribbons together should occupy less than 5% of the viewport
  in ordinary straight Drive;
- head alpha should stay at or below `0.65` and tail alpha reach exactly zero;
- world-space width should stay at or below `0.075 m` per rail in the first
  slice;
- ordinary trail history should remain below `20 m` at the existing Drive
  equilibrium; and
- trails must never obscure the craft, minimap, dispatch target, pickup zone,
  or delivery-zone border.

## Performance budget

The current game already uses one 128-particle `SurfaceFeedback3D` spray. The
trail budget should remain visibly smaller than that system.

- Ribbon styles: maximum two draw surfaces, 32 samples per anchor, and 128
  base strip vertices total.
- Particle-assisted style: maximum 64 allocated particles; initial target 48.
- No particle collision, subemitters, lights, shadows, GI, or preprocess.
- One material allocation per role/style at initialization; zero per-frame
  node or material creation.
- Fixed-size bounded history arrays; no unbounded point list.
- A conservative custom/visibility AABB that covers the maximum trail length
  without causing premature popping.
- Changing `amount_ratio` is not counted as a performance optimization because
  Godot allocates/processes the configured amount; configure the actual small
  amount instead.
- Target on the validation Mac: added median frame cost <=`0.35 ms`, added p95
  <=`0.75 ms` during a sustained full-speed drift at 1280x720. These are study
  budgets, not claims until profiled.
- Every style must pass a ten-minute wall-adjacent drift/free-roam soak with no
  growing node count, resource count, history length, or console output.

## Reward and unlock structure

The cosmetics should make delivery earnings feel valuable without requiring a
grind economy. Use relative prices until the payout study selects real credit
numbers.

Let `S` mean the net payout of one ordinary successful standard contract at a
respectable but imperfect result.

| Reward beat | Availability | Suggested price | Intended feeling |
| --- | --- | ---: | --- |
| District Standard + Trail Off | start | free | trusted baseline; no penalty for opting out |
| First-finish choice: Orchid, Saltglass, or Ember | first completed familiarization | one choice free | the first delivery visibly changes the vehicle immediately |
| Remaining two first-wave paints | after familiarization | `0.8S` each | each clean delivery can buy meaningful expression |
| Twin Vector | after first successful standard delivery | `1.6S` | a clear near-term aspiration |
| Courier Pulse | after two successful contracts | `1.9S` | a second style rather than a recolor |
| Comet Ledger | after one grade-A or high-integrity result | `2.2S` | mastery opens stock, but credits still purchase it |
| Secondary paint catalogue | route/reputation milestones | `0.9S–1.5S` | continued variety without power creep |
| Later prestige variants | district mastery only | undecided | long-term recognition, not part of first slice |

Principles:

- Unlocking stock and purchasing are separate: reputation/achievements reveal
  options; credits acquire them.
- The first free choice prevents the economy from feeling withholding.
- A merely completed delivery must make progress; perfect play accelerates
  choice but is not required for basic expression.
- No random drops, loot boxes, rotating stock, duplicate unlocks, or hidden
  rarity odds.
- Do not bundle mechanical performance with a cosmetic. A paint or trail never
  changes speed, braking, integrity tolerance, payout, or route availability.
- Paint and trail equip independently so six assets create twelve immediately
  meaningful combinations before accounting for the default.

### Results-screen reward choreography

The acquisition moment is part of making credits feel worthwhile:

1. settle time, integrity, distance/efficiency, and grade;
2. show credits earned and the updated total;
3. if stock unlocked, reveal exactly one clear card after the score settles;
4. offer `EQUIP NOW`, `PREVIEW`, and `CONTINUE`;
5. if credits are just short, state the exact remaining amount without selling
   or pressuring; and
6. on equip, show the actual R7 vehicle rotating through Spread, midpoint, and
   Drive so the underlay/can reveal is visible.

For the first slice, a lightweight `SubViewport` preview may instantiate only
`vehicle_visual.tscn`, not the craft controller or world. If that is too much
UI work, `EQUIP NOW` followed by the real world vehicle is preferable to a
static color square. The model transformation is the reward.

## Verification plan for an implementation milestone

### Static and semantic checks

1. R7 material-role registry resolves every expected path exactly once.
2. Exactly 56 mesh instances are accounted for.
3. The three functional energy/nozzle meshes and bore are rejected from paint
   mutation.
4. No cosmetic scene contains `CollisionObject3D`, `CollisionShape3D`,
   `RayCast3D`, `ShapeCast3D`, `NavigationObstacle3D`, or physics-writing code.
5. Profile bounds reject excessive width, history, alpha, particle count, and
   emission.
6. Cosmetic selection cannot enter contract grade, payout, integrity, route,
   movement, or input calculations.
7. Reset, scene switch, invalid craft, and displacement guard all clear trail
   history.
8. Palette and trail identifiers are stable and deterministic.

### Exact-engine and native checks

1. Exact Godot remains `4.7.1.stable.official.a13da4feb`, Forward+.
2. C1 remains 1,260 raw-identical ticks with maximum movement delta `0.0` for
   default, each paint, and each trail.
3. Capture all three initial paints at Spread, midpoint, and Drive.
4. Capture all three trails during straight Drive, a long drift, braking,
   Hop/landing, wall occlusion, pause, and reset.
5. Exercise CLEAR, CAUTION, and STRIKE against every initial paint/trail pair.
6. Require no first-frame/teleport streak, no wall-through rendering, and no
   retained trail after reset.
7. Run inherited `21/21` native visuals, `14/14` rays, and route/view sweep
   unchanged.
8. Profile each style alone and with existing surface spray active.
9. Soak at sustained speed and wall-adjacent drifting while checking memory,
   resource count, node count, logs, and frame-time tails.
10. Owner review decides beauty, reward desirability, motion comfort, and the
    final three-plus-three set. Automation cannot claim those gates.

## Bounded implementation order

1. Add profile resources and a material-role resolver in a new successor copy.
2. Implement District Standard as an exact visual no-op and prove material
   accounting.
3. Implement the three selected paint profiles and native pose captures.
4. Add fixed render-only trail anchors.
5. Implement the bounded history core and Twin Vector.
6. Derive Courier Pulse from the same history.
7. Add the small fixed-seed particle companion for Comet Ledger.
8. Add trail-off/reduced-motion controls and reset guards.
9. Add a temporary preview/equip lab with no currency or save dependency.
10. Run the complete presentation, movement-equivalence, performance, and soak
    gates.
11. Let Charlie select/reject the exact three-plus-three before wiring prices
    into the contract economy.

This sequence prevents economic implementation from locking in cosmetics that
look weak in the actual chase camera.

## Deliberately deferred

- speed, braking, hover, integrity, or cargo upgrades;
- texture skins, decals, logos, user-imported art, and UV-dependent designs;
- animated custom paint shaders, iridescence, camouflage, or transparency;
- trail color pickers and arbitrary RGB sliders;
- vane-tip trails, rings that resemble checkpoints, and full-screen effects;
- random rarity, seasonal rotation, premium currency, or storefront pressure;
- NPC-visible cosmetics, multiplayer replication, photo mode, and sharing;
- persistent saves until the gameplay slice proves what must be persisted.

## Technical references

- Local R7 sources inspected read-only:
  `scenes/vehicle_visual.tscn`, `scripts/vehicle_visual_rig.gd`,
  `scenes/craft.tscn`, `scripts/craft_controller.gd`, and
  `scripts/surface_feedback_3d.gd`.
- Godot 4.7 `GPUParticles3D` documents `local_coords`, fixed FPS, fixed seeds,
  `emit_particle()`, trail support, and visibility AABBs:
  <https://docs.godotengine.org/en/4.7/classes/class_gpuparticles3d.html>
- Godot 4.7 `RibbonTrailMesh`:
  <https://docs.godotengine.org/en/4.7/classes/class_ribbontrailmesh.html>
- Godot 4.7 particle-trail setup:
  <https://docs.godotengine.org/en/4.7/tutorials/3d/particles/trails.html>
- Godot 4.7 `Node3D.get_global_transform_interpolated()` and reset-streak
  guidance:
  <https://docs.godotengine.org/en/4.7/classes/class_node3d.html>
- `ImmediateMesh` is intended for small geometry that changes frequently:
  <https://docs.godotengine.org/en/4.7/classes/class_immediatemesh.html>

## Final study decision

Proceed with a small **three paints + three trails** presentation lab before
building a large catalogue. The first set should be broad in identity rather
than broad in quantity:

- Paint: **Orchid Static / Saltglass / Ember Relay**.
- Trail: **Twin Vector / Courier Pulse / Comet Ledger**.

Together they create warm, cool, and violet finish choices plus continuous,
segmented, and particle-assisted wake choices. They make the R7 transformation
and the player's long drifts visible as rewards, while keeping the functional
energy cue, physics, routes, camera, and contract balance untouched.
