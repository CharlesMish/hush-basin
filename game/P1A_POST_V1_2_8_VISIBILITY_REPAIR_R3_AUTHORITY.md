# District Zero P1A — post-v1.2.8 visibility repair R3

## Trigger and correction of R2 scope

Owner review of the R2 executable proved that an apparently invisible solid
could still stop the craft. R2 correctly diagnosed a render/collision culling
mismatch, but applied its correction to only three named wall families. The
same builder creates nineteen solid render meshes and nineteen colliding
`StaticBody3D` peers. The remaining sixteen render materials retained Godot's
one-sided default while their collision remained closed or explicitly
two-sided. This allowed a craft-facing surface to disappear even though the
corresponding collision stayed active.

## Narrow R3 authority

R3 may only:

1. set `BaseMaterial3D.CULL_DISABLED` on the existing material of every solid
   created by `_build_solids`, matching the already two-sided/closed collision
   contract without adding or changing geometry;
2. add a structural regression proving that all nineteen solid visual/body
   pairs exist, contain collision shapes, and use two-sided rendering; and
3. identify the executable presentation unambiguously as `v1.2.8 VISIBILITY
   R3` while retaining `WORLD v1.2.3` in the visible label.

R1's render-only face tones and camera obstruction shortening remain in force.
R2's bounded `WALL_SIDE_LIGHTEN = 0.18` selection remains in force. R3 does not
authorize another presentation or contrast adjustment.

## Frozen without exception

Movement, tuning, input, craft collider, support, terrain bytes/colors,
positions, vertices, triangle order/winding, normals, collision shapes or
masks, routes, nodes, spawns, HOP behavior or dimensions, gameplay and visual
thresholds, camera FOV/look target/unobstructed frame, lighting, shadows,
background, tonemapping, and all material properties other than solid render
culling remain frozen.

This is an owner review successor. It is not P1A PASS, Human World Gate
authorization, or permission to enter P1B.
