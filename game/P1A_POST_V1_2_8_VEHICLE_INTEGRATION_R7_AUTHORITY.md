# District Zero P1A — bounded owner-authorized vehicle integration R7

## Trigger

The owner approved integrating the separately completed and validated
`District-Zero-Vehicle-Babylon-Transfer-R1-Polish` presentation asset into the
current Terrain Polish R6 game for play review.

## Narrow authority

R7 may replace only the craft's presentation subtree, add the transferable
`VehicleVisualRig`, and replace the old primitive-vane/core presentation code
in `CraftController` with the minimum calls that provide the same canonical
`fold_amount` and clearance-state cue to that rig.

The transferred visual scene and rig must remain byte-identical to the verified
transfer package. `scenes/craft.tscn` and `scripts/craft_controller.gd` may
match that package only after their gameplay-root, fixed collider, three
support probes, hazard cast, physics code, transform timing, input, movement,
Hop, impact, and reset contracts are proved unchanged from R6.

## Frozen without exception

All movement and tuning; CharacterBody3D settings; collider, probes, hazard
cast, collision layers and masks; transform timing and `fold_amount`; terrain,
world data and geometry; walls and colliders; routes, nodes and spawns; camera;
HUD/map behavior except unambiguous R7 review labeling; lighting, shadows,
tonemapping and fog; telemetry and capture/replay; all visual/ray/runtime
acceptance thresholds; Human World Gate and P1B boundaries remain frozen.

The new visible envelope does not authorize collider changes. The visual rig
may contain only presentation nodes and may never feed geometry, transforms,
contacts, clearance, or state back into simulation.

## Acceptance

- Exact Godot is `4.7.1.stable.official.a13da4feb`, native Forward+.
- Transfer inventory and choreography validator pass from a fresh disposable
  import; the golden pose signature remains
  `045296bf018b6da5af5d89b37af831fd29eedfe16d8f085f80ba6fb113dfb44b`.
- The imported class cache binds `VehicleVisualRig` to its exact script path.
- R6 behavior and terrain tests remain green under an R7-labeled successor.
- C1 compares `1,260` ticks with maximum delta `0.0` and raw-identical traces.
- All runnable inherited runtime vectors remain green.
- Native vehicle endpoint/intermediate captures, `21/21` visuals, `14/14`
  frozen rays, and the `14/14` route/view sweep remain green.
- Fresh player extraction imports, parses, and passes its integration suites.

R7 is an owner-review build, not P1A PASS or Human World Gate authorization.
It does not enter P1B.
