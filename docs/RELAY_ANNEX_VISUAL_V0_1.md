# Relay annex presentation lane

This isolated lane starts at played Mastery Alpha handoff
`66b4c228264d6c2966a8af68243898fc21c6573d`. The owner's Persistent Consequence
commission authorizes one finite Relay presentation change, preserving roads,
collision, terrain, camera and weather. The root integration owns project copy,
the two delivery needs, persistence and Dispatch; this node reads only stage.

`relay_annex.gd` is a native `Node3D`: add it to the world, call
`configure(gate.data)`, then `set_stage(0/1/2)`. Its anchor comes from the existing
`RLY_MAST` landmark and its bounds are checked against that owner's existing
Working Neighborhood plot. `relay_annex_v0_1.json` contains every authored part,
palette and dimension. It is not a general construction or project framework.

- **0:** no visible geometry; the old mast remains unchanged.
- **1:** fitted receiving frame, mounting returns and brackets, 10 box instances.
- **2:** the same frame carries two broad receiver panels, steady warm status
  strips and a physical `RELAY DISPATCH` header, 24 box instances total.

There are three native box MultiMesh batches and one Label3D. No new textures,
shaders, lights, particles, collision bodies or dynamic animation. The equipment
occupies world bounds x `[-4.475,4.475]`, y `[12.61,22.24]`, z
`[-285.45,-281.65]`, wholly within the mast's existing 10 × 10 m occupied plot.
All scales are positive and transforms finite. The original mast top remains
32 m, its aerial reaches 34.2 m, and both remain unchanged.

The stage batches join the existing particle-only heightfield mask (layer 2).
When stage changes, integration must refresh that static heightfield. Installed
Godot 4.7.1's class has no `force_update()` method: set `update_mode` to
`UPDATE_MODE_ALWAYS` for a rendered frame, then restore `UPDATE_MODE_WHEN_MOVED`.
This refresh changes particle contact only, not weather settings or body physics.

## Evidence and limitation

Fresh native Forward+ 1280 × 720 baseline captures were made before implementing
the lane. Matched stage 1 and 2 views reuse ordinary gameplay-camera transforms:
the south road, Relay pad, western approach and eastern approach. No cinematic
camera or forced reveal is used. Source engine version is
`4.7.1.stable.official.a13da4feb`.

The paired panels create a readable wider silhouette at the pad and from the
south/west. The header's words are not reliably legible at speed from 75+ m;
silhouette and material change carry the effect. The intermediate empty frame is
deliberately quieter than the completed installation.

**The eastern sweep arrival can miss the entire mast.** Its travel heading faces
west/southwest while the mast stands 75 m north of the delivery pad, outside that
camera view. The captures retain this unfavorable view. A player who arrives
from the east and immediately departs without turning may not notice the change.
Whether the current physical consequence is noticed naturally remains a human
gate; this lane does not claim it passes.

`game/tests/relay_annex_visual_probe.gd`: 31/31 checks pass, including loaded
authoritative data, finite positive transforms, occupied bounds, three-batch
limit, stage transitions and reversal, reset-to-zero, idempotent reconfiguration,
native materials, precipitation layer, and absence of physics/lights/particles.
The probe is run headless; native matched captures establish visible behavior.
The sandboxed import emitted the known macOS certificate/editor-settings warning;
it had no script parse errors. Native capture runs exited cleanly.

Evidence lives outside source in `evidence/relay-visual-lane/`: baseline-road,
stage1, stage2, `probe.json`, `api.log`, and `relay-stages-contactsheet.png`.
Contact sheet columns: unchanged / fitted mount / operational. Rows: south
approach / Relay pad / west approach / east approach. The earlier `baseline/`
folder contains exploratory views beyond the pad and is not the matched survey.
