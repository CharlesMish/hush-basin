# District Zero P1A — post-v1.2.8 visibility repair R2

## Trigger and correction of the prior diagnosis

The owner’s review of the correct v1.2.8 project showed that the first
visibility repair remained incomplete. A near wall exterior can disappear while
the far interior face remains visible. The shipped builder explicitly makes the
terrain two-sided but leaves all solid materials at Godot’s default back-face
culling mode. The authored wall side triangles have a single winding, so this
is a render-consumer culling defect rather than a shadow, camera, geometry, or
collision defect.

The top HUD also displayed only the inherited world-data authority `v1.2.3`,
which is truthful as world authority but ambiguous as review-build identity.

## Narrow R2 authority

R2 may only:

1. disable render culling on the existing materials for `CORE_WALL`,
   `OUTER_CLOSURE_MASK`, and `OUTER_WALL`, rendering their authored triangles
   from both sides without duplicating or changing geometry; and
2. make the smallest side-face lightening adjustment needed for a newly visible
   wall exterior to retain the unchanged `0.12` obstacle-separation gate; and
3. identify the executable presentation unambiguously as `v1.2.8 VISIBILITY
   R2` while retaining `WORLD v1.2.3` in the visible label.

The first repair’s render-only face values and camera obstruction shortening
remain in force.

## Frozen without exception

Movement, tuning, input, craft collider, support, terrain bytes/colors,
positions, vertices, triangle order/winding, normals, collision, routes, nodes,
spawns, HOP, thresholds, camera FOV/look target/unobstructed frame, lighting,
shadows, background, tonemapping, and every non-target material remain frozen.

This is an owner review successor. It is not P1A PASS, Human World Gate
authorization, or permission to enter P1B.
