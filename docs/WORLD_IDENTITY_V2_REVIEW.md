# World Identity / Detail v2 — owner review

The accepted Quarto game now has an additive district-detail layer across all
14 supporting buildings and six landmark families. This is a local successor,
not a production update. Baseline: `ce48769fd648a44dd0b28c975b8fe4bf78bd3cb1`.

## What changed

- **Quarry:** roof gantries, extraction/grade identifiers and mineral service
  bands. The nearby repair workshop gets northlight hoods and a larger fascia.
- **Depot:** numbered hoist frames on the twins, freight-office identification,
  warehouse roof hoods and warm logistics bands.
- **Relay:** additional mast receivers, a utility-office aerial and cool muted
  service accents. The original mast remains the dominant landmark.
- **Works:** ducts, ventilation banks, stack caps/service ribs and distinct
  fabrication, air-handling and materials-store identifiers.
- **Market:** roof lanterns, awning valances and larger commercial identifiers.
  Existing warm windows and closed service entrances remain.
- **Clinic:** calm roof screens, paired civic fins and softer service bands,
  continuing through the water office and Clinic support building.

Fixed replacement tabs on new fascia panels suggest maintenance without adding
loose props. District colors share the existing warm mineral/steel vocabulary.
Transitions use thin bands on selected existing retaining faces. The long outer
boundary is preserved. No detail is scattered across yards or shortcuts.

There are 296 native primitive instances in eight batches, one band mesh, and
20 native text identifiers. All additions are non-colliding; roof equipment
joins the existing particle-only rain mask. No new textures, shaders, lights,
particles, external assets or dependencies are introduced.

## Preservation and observed native results

All 465 baseline files are byte-identical after removing exactly the one new
builder call from `p1a_world_builder.gd`. Existing terrain, material maps, routes,
classification data, destination positions, architecture/collision, Quarto,
movement, camera, weather, Run/BRRR, Web presets, shell and hosting tools remain
unchanged. The new configuration and generated output have a separate identity.

Fresh baseline import/parse, 25-view survey, vehicle fixture, movement trace and
Web export passed with `4.7.1.stable.official.a13da4feb`. The successor results:

| Check | Observed result |
|---|---|
| Deterministic generation, finite geometry and occupied-plot bounds | Pass |
| Runtime collision graph | All 162 shapes hash-identical |
| Terrain vertices, normals and triangle indices | Hash-identical |
| Movement fixture | Exact 1,260-tick byte parity |
| Quarto native vehicle fixture | 39/39 |
| Run | 54/54 |
| Paused retry | 15/15 |
| World runtime, including all 12 entrance traversals and contact/recovery | 35/35 |
| Weather/reset/pause/map checks | 31/31 |
| Native rain-contact probes: ground, roof, quarry top | 3/3 |
| New runtime detail/preservation checks | 8/8 |

Movement trace SHA256:
`29f1049f8e16ec65d288407c35e6ccae46e87c711bb6b54b134e6158c68b9443`.
Runtime collision graph SHA256:
`60d972c8d68f168c684d411af78946a2624e272f2a60a95c11aecc29a1e90064`.

At 1280×720 Forward+ on Apple M5, median per-view static p95 changed **+1.08%**;
the largest individual static increase was **+3.66%**. Five-route adjacent moving
AB/BA pairs had median changes **−1.36% / +0.43%**; the largest individual moving
increase was **+2.91%**. Every workload met the 10% target. Individual workloads,
both orders and raw moving samples are retained; no unfavorable run was removed.
These are wall-clock frame timings with display/scheduling effects, not isolated
GPU costs or cross-machine guarantees. Static before/after captures were
separated by implementation; moving pairs were adjacent with review UI idle.

## Web regression lane

The unchanged pinned single-thread export lane succeeded. Baseline and successor
each passed the existing 13-check Chromium diagnostic smoke, including countdown,
both Quarto forms, minimap, pause, paused retry, synthetic finish crossing,
results, free roam and retry clearing. This synthetic finish is not a human-driven
completion claim. The original fitted shell is reused locally without edits.

| Raw artifact size | Before | After | Change |
|---|---:|---:|---:|
| Web PCK | 101,717,356 bytes | 101,862,156 bytes | +144,800 / +0.142% |
| Complete nine-file export | 141,565,089 bytes | 141,709,889 bytes | +144,800 / +0.102% |

The fitted HTML shell is a separate derivative, outside those nine-file totals.
The engine WASM remains the pinned template. PCK byte identity is not claimed
between repeat exports. Local browser timing results and raw samples accompany
the review packet in `WEB_RESULTS.json`.

Both adjacent Chromium AB/BA pairs passed without console/page runtime errors.
Idle RAF p95 changed **−0.57% / −3.28%**; sustained W+Shift+A p95 changed
**+1.16% / 0.00%**. The canvas remained 1280×720 in the unchanged fitted shell.
Each workload lasted 20 seconds; all individual frame samples are retained.
Browser RAF and native frame measurements are separate observations, not
interchangeable performance metrics.

## Remaining limits and historical failures

The lower Relay approach remains sparse, and the unchanged player camera crops
some tall roof details at close range. Long outer walls and broad yards still
carry less local storytelling than the occupied blocks. Small lettering is not
expected to be readable at full Drive speed; silhouettes and accent rhythm do
most of the work. Thin roof rails and signs deserve Charlie's temporal-shimmer
check, especially in Web. No claim of continuous human comfort testing is made.

Web Compatibility remains brighter than native. Safari, physical gamepad,
actual background-tab suspension and Web particle contact are not certified in
this pass. Native contact probes cover three retained surfaces; new equipment's
rain-mask participation is checked, not every individual drop/roof intersection.

Historical validators are preserved and their failures are explicit:

- Old Quarto static suite: baseline **447/449**, successor **446/449**. Baseline
  failures are the previously accepted `.gitignore` and README wrapper changes;
  the successor adds the explicitly authorized world-builder hook difference.
  The other 446 checks pass. Current native Quarto checks pass separately.
- Old export-only Web preservation gate: baseline **6/6**, successor **5/6**,
  with only the new world-builder hook reported changed. The narrow successor
  inventory guard replaces that expectation; the old gate is not edited.
- Quiet Surfaces' historical Market–Clinic **+14.61% p95** failure, prior capture
  interruption and intermittent non-contact entrance short traces remain
  historical findings. Today's successful traversals do not resolve their cause.

The initial close review caught overlapping Depot identifiers, corrected before
complete verification by mounting numbers on the hoists. Two new evidence-camera
starts initially sat inside old plinths; the recorded correction uses existing
DEP/CLN pads. Those initial views remain in the evidence. No product change was
needed for the camera correction. No post-complete product repair rounds used.

## Charlie's 8-minute playtest

Launch `PLAY_FULL_GAME.command`. Keep your usual driving style.

1. Take Quarry → Depot in Drive. Notice whether gantries and hoist numbers make
   those places distinct before you slow down.
2. Cross Relay → Works. Look for the utility aerial, stack group and roof plant;
   say whether Relay needs a stronger lower-level cue next time.
3. Loop Market → Clinic in both forms. Look for commercial versus civic rhythm,
   and whether the extra bands and signage feel maintained or too systematic.
4. Sweep past the buildings at full speed, brake beside a service frontage, and
   take a favorite shortcut. Check open space, distraction and shimmering edges.
5. Retry a Run, pause/retry once, then return to free roam. Try the local Web
   candidate separately if useful; the hosted production version is unchanged.

The owner decisions are: **Do places feel more purposeful and memorable? Does
anything distract from driving? Which single approach still feels unfinished?**
No courier/gameplay implementation follows automatically from this review.
