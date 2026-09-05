# Quarto vehicle v1 — native visual successor

The owner requested: “Please continue with building on the existing native rig
then, thank you :)” after reviewing the proposal to retain Hush Basin's palette,
handling, camera and quick transformation while developing Quarto's construction.
This authorizes implementation and local comparison on a dedicated branch from
accepted Hush Basin commit `9fd4c020c374a7a6db441e4cbc20b53919d5a5e4`.

## Bounded change

The two existing playable files permitted to change are
`game/scenes/vehicle_visual.tscn` and `game/scripts/vehicle_visual_rig.gd`.
New native visual mesh data/helpers, reproducible authoring tools, independent
comparison scenes, successor tests, evidence and documentation support them.
Current-task preambles may be added to `README.md`, `AGENTS.md` and
`game/AGENTS.md`, retaining their inherited text unchanged beneath the preamble.
All other baseline tracked files remain byte-identical.

Retain `Craft/VisualRoot`, `VehicleVisualRig`, public `form_amount`,
`set_form_amount(value)` and `set_energy_state(state)`. The existing controller
owns scalar progression, banking and reset. Preserve all eleven material roles
and their source color/metallic/roughness/emission values, plus the original
SPREAD/DRIVE/CAUTION/STRIKE color logic. New geometry is presentation-only and
must contain no physics, collision, probe or gameplay-control descendants.

Develop a long faceted receiving body, four proud sockets, actual paired-leaf
folding, smaller/lower forward versus larger/higher aft folios (legacy/source:
books), a canted folded posture, and a hollow positive-thickness translating can
around a fixed core with a simplified visible receiver/capture relationship.
No part shrinks, disappears or gets replaced during posing. Pose is a pure
function of the existing scalar; interruption and reverse travel are supported.

The Godot derivative retains its original origin, metres, +Y up and −Z forward.
It is not a literal Quarto export. Declare these review budgets before measuring:

| Quantity | Native derivative budget |
| --- | --- |
| SPREAD width | 2.60–2.72 m |
| DRIVE width | at most 1.15 m |
| Endpoint length | 2.25–2.45 m |
| SPREAD height | at most 0.70 m |
| DRIVE height | at most 1.05 m |
| Sampled local vertical extent | within −0.45 to +0.80 m |

The height budget explicitly accommodates the higher rear folding shoulder in
this visual successor. It does not rewrite R7's historical envelope checks or
grant collider/clearance rights. Report measured endpoints and the full sampled
sweep; geometry is corrected to these budgets, not the converse.

## Preserved boundaries

Keep the craft scene, controller, motion math, tuning, camera, collider, three
support probes, hazard cast, input, 0.24 s folding / 0.20 s deployment, world,
weather, surface maps, routes, Run rules and telemetry unchanged. Comparison
scenes are separate entry points; their UI never enters the normal game scene.
Do not transfer Quarto's Babylon proof graph or create a second animation clock
inside the playable rig.

Quarto's frozen MT1-S5HR3R1 and accepted BODY-SHELL-03.1 remain unchanged.
No proof identity, physical registration, structural reservation, cockpit,
contact hardware, utility profession, complete engine or performance claim is
created. **Quarto authority participation: none.** This document authorizes a
Godot presentation successor, not promotion into mechanical authority.

## Verification and review

Before playable edits, `python3 tools/verify_repo.py` passed 389 checks against
the accepted source. Keep all historical inventories, tests and evidence
unchanged. Their vehicle byte/pose bindings are expected to reject the
intentional successor; do not patch their expected hashes into a pass.

Use the new versioned vehicle verifier to check the baseline preservation
boundary, palette, geometry, finite positive-scale transforms, folding,
deterministic direct/reverse/interrupted posing and measured envelopes. Verify
the full native path with the pinned Godot
`4.7.1.stable.official.a13da4feb`, including fresh import, native mesh/pose checks,
matched same-host C1 traces, existing Run/world/entrance fixtures and matched
gameplay-camera captures. Use separate empty evidence outputs and run engine
processes sequentially. Do not install or substitute another engine silently.

Browser geometry previews and offline exported GLBs aid review; they cannot
establish Godot photometry, visual comfort, runtime performance or native passes.
If the pinned engine is unavailable, complete the source and available checks,
record native validation as pending, and provide reproducible native commands.
Owner acceptance is not inferred from automated checks.

The inherited Quiet Surfaces final complete suite remains FAIL, including the
Market–Clinic AB moving p95 +14.61% target miss and the unexplained capture stall.
This task does not reopen that world-performance repair or erase its evidence.
No push, publication or external account action is authorized by this task.
