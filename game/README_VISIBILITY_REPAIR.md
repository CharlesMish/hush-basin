# District Zero P1A v1.2.8 — Visibility R3 review build

This isolated R3 successor corrects the remaining scope defect confirmed by
the owner's review of R2:

- authored wall top, side, and bottom faces now receive distinct render-only
  values, making the top edge and wall volume readable; and
- all nineteen collidable solid families render their existing triangles from
  both sides, so no one-sided visual can disappear while its collision remains;
  and
- the chase camera is shortened toward the craft when world collision blocks
  their line of sight, preventing a wall from filling the foreground while the
  craft appears through an edge or aperture.

The HUD now says `v1.2.8 VISIBILITY R3 · WORLD v1.2.3`: the first part identifies
this executable review build, while the second accurately preserves the frozen
world-data authority.

No wall, terrain, collision, route, movement, tuning, camera FOV, or
unobstructed camera frame changed.

## Open the review build

Use the project in this directory with the already-installed exact engine:

```text
/opt/homebrew/bin/godot --editor --path <THIS_DIRECTORY>
```

Run the project normally, use `TAB` for the diagnostic list, and drive near the
walls that produced the supplied screenshots. This is an owner review build;
it is not P1A PASS or authorization for the Human World Gate.

## Automated result

- exact Godot: `4.7.1.stable.official.a13da4feb`;
- visibility behavior checks: `39/39 PASS`, including all `19/19` solid
  render/collision pairs;
- native acceptance metrics: `21/21 PASS`;
- newly visible left-wall separation: `0.1241901353` against unchanged `0.12`;
- native rays: `14/14 PASS`, zero mismatches;
- all 14 registered diagnostic starts captured successfully;
- inherited R1 semantics: `65/65 PASS`;
- v1.2.8 semantics: `45/45 PASS`;
- C1: `1,260/1,260` ticks, raw traces identical, maximum delta `0.0`.

The complete commands, logs, JSON results, and PNG sweep are in the paired
validation-evidence package.
