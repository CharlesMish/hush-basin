# Hush Basin — Quarto native vehicle v1

This candidate develops the existing native `VehicleVisualRig` into a more
recognizable Quarto derivative while retaining Hush Basin's material palette and
gameplay. The normal game automatically uses the revised visual scene through
its existing `Craft/VisualRoot` instance. There is no controller adapter or new
animation clock.

Source baseline: `9fd4c020c374a7a6db441e4cbc20b53919d5a5e4`, Quiet Surfaces v1.
Task branch: `feature/quarto-native-vehicle-v1`.
Scope: [QUARTO_VEHICLE_V1_AUTHORITY.md](../QUARTO_VEHICLE_V1_AUTHORITY.md).
Status: **candidate; native Godot validation and owner acceptance pending**.
The pinned engine was not available in the implementation environment. No
substitute engine was installed or used, and browser images are not native proof.

## What changed

Each of the four folios (legacy/source: books) now contains an inner and outer
leaf. The outer leaf folds underneath through a real hinge before yaw, cant and
terminal seating. The former early whole-leaf compaction translation is removed.
The smaller forward pair sits lower; the larger rear pair forms a higher folded
shoulder. Material remains present at every pose, including reverse travel.

The central body is longer and faceted, with an open stern and four receiving
pockets. The folios remain proud of those pockets. A positive-thickness hollow
can moves around a fixed core, with a separate receiver and four simplified
capture jaws. This is construction language for a game asset, not a complete
engine or a physical mechanism certificate.

The eleven original material blocks and amber/cyan, caution and strike cues
remain. Controller, craft scene, motion math, tuning, camera, collider, support
probes, hazard cast, input, world, weather, routes, Run logic and telemetry are
unchanged. Folding still takes 0.24 s; deployment still takes 0.20 s.

## Review in Godot

Use the existing exact `4.7.1.stable.official.a13da4feb` executable. Set
`GODOT_BIN` to its path or pass `--godot /path/to/godot` to these tools.

```sh
python3 tools/launch_quarto_vehicle.py --view compare
python3 tools/launch_quarto_vehicle.py --view studio
python3 tools/launch_quarto_vehicle.py --view game
```

`compare` opens the unchanged Run world and camera with a separate visual
comparison overlay. F6 or its buttons switch the visible original/candidate.
Both receive the current form and energy state; the comparison reference follows
the controller-owned visual bank. This view is for judging appearance during
play, not measuring performance: both rigs exist while one is hidden.

`studio` supplies a scrubber, original/candidate switch, forward/reverse endpoint
controls, slow or game cadence, three camera views and all energy states. Space
reverses travel; right-drag orbits, wheel zooms and Escape exits. Its lighting is
a separate neutral review setup. The Game angle preset reproduces the stationary
unobstructed camera geometry, not the world's dynamic camera collision behavior.

`game` launches the normal game with the candidate alone. The normal project
entry point, HUD and review labeling inside inherited source are unchanged;
the separate comparison scene clearly identifies this candidate.

## Source and portability

These four files form the native visual asset and must travel together:

- `game/scenes/vehicle_visual.tscn`
- `game/scripts/vehicle_visual_rig.gd`
- `game/scripts/quarto_mesh_library.gd`
- `game/presentation/quarto_native_v1.json`

The scene contains the explicit hierarchy and the inherited native materials.
The helper builds immutable ArrayMeshes once from explicit vertices, normals and
indices. Per-frame work only poses the authored channels and updates energy
materials. The JSON is also the input to the provisional browser viewer and
static GLB exporter; it is not an independently remodeled approximation.

Author geometry in `game/tools/build_quarto_native_v1.py`, then regenerate:

```sh
python3 game/tools/build_quarto_native_v1.py
```

Generation writes only the new canonical JSON and native scene. It preserves
the scene's eleven material blocks verbatim. Retain the JSON in any game export;
the rig loads it through `FileAccess`, as the existing world does with its data.
Coordinates remain metres, +Y up and −Z forward, at the original gameplay origin.

The comparison reference is copied from the baseline scene/rig. Only the copied
scene's script path and copied script's global class declaration change to avoid
a resource/class collision. Reversing those two namespace edits reproduces the
baseline bytes exactly. Historical originals remain at the baseline Git commit.

## Verification

The original preservation verifier passed all 389 checks before playable edits.
The successor has its own independent verifier and baseline binding; historical
inventories and expected poses are not rewritten.

The completed source/data run passed **449/449 checks**, including a 201-pose
surface screen with zero main-leaf pair defects and zero main-leaf contacts with
the tested central body, receiver and socket meshes. The eight principal leaves
are closed convex solids. Scene/JSON bindings and all eleven original material
blocks match. These are authored-geometry measurements, not Godot observations:

| Pose | Width | Height | Length |
| --- | --- | --- | --- |
| SPREAD | 2.660 m | 0.602 m | 2.300 m |
| DRIVE | 1.05134 m | 0.81548 m | 2.405 m |

The sampled local Y extent is −0.30043 to +0.60048 m. Maximum sampled width is
2.66701 m during folding. DRIVE is within the agreed 1.15 m limit; it sits about
1.3 mm above the older reference's preferred 1.05 m upper target.

Fresh disposable regeneration reproduced the scene and JSON byte-for-byte.
Seven final browser views completed without JavaScript errors. The responsive
viewer was checked at 700 and 390 px. Three final static GLBs passed 17,196 world
vertex comparisons and 8,808 outward-winding checks, with maximum vertex error
below 0.000000030 m. These interchange/browser checks do not establish native
photometry or gameplay. The native preflight returned **BLOCKED: no matching
engine found**, and ran zero native commands.

Development evidence retains the earlier oversized-frame height/length miss,
the body/socket sweep intersections, the bevel repair, and narrow-browser
framing correction. Geometry was repaired without relaxing the declared bounds
or altering folio motion. Independent code review also led to physics-tick
synchronization of the world comparison and one-time editor mesh initialization.
Native parsing and editor appearance still require the pinned-engine check.

The final [structured result](QUARTO_VEHICLE_V1_RESULT.json) binds the delivered
source and records the exact validation scope and limitations.

```sh
python3 tools/verify_quarto_vehicle.py --evidence /absolute/new/static-evidence
python3 tools/verify_quarto_vehicle.py --native --evidence /absolute/new/native-evidence
```

Use a new evidence directory for every run. Native mode requires the exact
engine and stages separate baseline and successor projects. An optional
`--baseline /absolute/clean/baseline` works when the recorded Git commit is not
available. That baseline must match the original 413-file binding.

Static checks are independent source/data checks. Native checks are required to
establish actual Godot parsing, mesh/pose fidelity, direct/reverse/interrupted
posing, independent warning materials, same-host matched 1,260-tick C1 movement,
Run/reset behavior, current world/entrance checks and gameplay-camera captures.
The inherited R7 camera probe is reused only for framing/capture observations;
it does not re-certify R7's historical vehicle pose.

The historical `tools/verify_repo.py` intentionally retains its Quiet Surfaces
vehicle-byte bindings. It should reject the two changed visual files on this
candidate. Use the versioned successor verifier for the declared new asset;
do not update old checksums to disguise that intentional difference.

For an immediate geometry inspection without Godot, see
[the browser preview instructions](../tools/quarto_preview/README.md). It uses
an already installed Babylon core and requires no new package. Its static GLBs
carry mesh/pose/material snapshots only; they do not contain the native rig or
establish a Godot round-trip result.

## Handoff boundaries

Changed baseline files: the visual scene/rig and current-task preambles in root
README/AGENTS and `game/AGENTS.md`. Additions: mesh authoring/data/helper, copied
comparison reference, studio/world comparison scenes/scripts, pinned-engine
launcher, successor fixture/verifiers, browser preview/export tools, this handoff
and the scope document. Refer to the branch diff for the exact file inventory.

Evidence consulted: Quarto's current state, nomenclature, frozen MT1-S5HR3R1
closure, BODY-SHELL-03.1 pocket correction, the prior Hush Basin reference and
palette bridge; Hush Basin's R7 integration contract, current presentation
authorities, delivery/status records, camera/controller/rig and existing tests.
New source/geometry/preview verification records are reported with the delivery.

**Authority participation: none.** Quarto's frozen mechanism, identifiers,
geometry, proof semantics and accepted shell are unchanged. No physical
registration, clearance right or structural reservation is created in either
project by this visual asset.

Remaining unknowns include native import/runtime, actual game lighting/readability,
gamepad feel and performance until the pinned-engine review is run. Sampled
geometry checks have an explicitly bounded scope; they are not manufacturing
or general collision authority. Quiet Surfaces' inherited complete suite remains
FAIL, including its Market–Clinic AB p95 +14.61% target miss and unexplained
capture stall. This vehicle candidate does not turn those results into passes.
