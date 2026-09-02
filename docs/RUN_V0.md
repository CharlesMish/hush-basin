# District Zero Run v0

Run v0 is a deliberately small observation layer around the byte-frozen R7
craft and world. It starts one unrestricted run at QRY, finishes at RLY, shows
a clock and the intentionally provisional **BRRR** seed metric, then asks the
owner whether Retry still feels inviting after roughly fifteen minutes.

It is not the P1B courier design, a balance pass, or a claim that BRRR is fair.
There are no checkpoints, route requirements, cargo, Credits, grades, unlocks,
ghosts, saves, or movement changes.

## Launch

The required engine is exactly
`4.7.1.stable.official.a13da4feb`. From the repository root:

```sh
python3 tools/verify_repo.py
./PLAY_RUN_V0.command
```

Or launch the scene explicitly:

```sh
/opt/homebrew/bin/godot --path game res://scenes/district_zero_run.tscn
```

The repository-level launcher performs the same exact-engine, clean-import,
parse, and single-instance checks as the preserved R7 launcher. It does not
change `project.godot` or R7's normal main scene.

Controls are the unchanged R7 controls. `R` starts or retries Run v0 from QRY.
On the results card, `F` returns to ordinary free roam. During the countdown the
craft's physics is frozen; R7's own held-input release lock remains in force, so
your first press after GO is the launch.

The Run input layer stays eligible to consume `R` while paused so the frozen
always-processing craft cannot interpret it as an ordinary manual reset. Its
countdown, clock, BRRR, and finish sampling explicitly stop while paused.

## Finish predicate

```text
Each physics tick while LIVE:
  p0 = craft xz last tick, p1 = craft xz this tick
  finished = segment(p0, p1) intersects disc(center = RLY pad center_xz_m, radius = RLY outer_blend_radius_m = 13.0)
No speed, form, dwell, impact, hop, or y condition.
```

The sole pre-existing safety guard suppresses a segment after the craft has
already crossed R7's fall-reset Y boundary; R7 then performs its ordinary fall
reset on the next craft tick. This is not an added finish-height requirement.

The QRY center, RLY center/radius, terrain height, and initial heading are all
resolved from the frozen manifest and route bake at runtime. The initial yaw is
derived from the first two A0 baked points; it is not copied from a diagnostic
tour or stored as another magic orientation.

## BRRR seed

```text
V_FLOOR = 20.0 m/s        # above Spread cap (17), below Drive soft (25): Spread cannot score, QRY pad cannot score
Each physics tick while LIVE:
  v      = horizontal speed = Vector2(velocity.x, velocity.z).length()
  drive  = craft.regime_name() == "DRIVE"
  split  = angle in degrees between flattened -basis.z and flattened velocity, clamped to [0, 90]
  qualifying = drive and v >= V_FLOOR
  if qualifying:
      streak_s += delta
      rate  = (v - V_FLOOR) * (1.0 + split / 30.0) * (1.0 + min(streak_s, 10.0) / 10.0)
      brrr += rate * delta * 10.0
  else:
      streak_s = 0.0
Impacts are never read. A wall that kills speed below V_FLOOR ends the streak by itself.
```

BRRR deliberately rewards fast, yawed Drive motion and keeps the longest streak
on the results card. Sightseeing/farming before entering the RLY finish disc is
expected evidence in v0, not something the vehicle should be changed to prevent.

## Frozen boundary

Every one of the 234 R7 manifest records remains byte-identical. The overlay
does not modify movement, tuning, camera, collision, Hop, vehicle rig, world
geometry/data, route authorship, diagnostic fixtures, InputMap, telemetry, or
the P1B design lab. It only instances the existing R7 scene and observes it at
physics priority `200`, after the priority-0 craft has completed
`move_and_slide()`.

Every manually started attempt clears transient diagnostic-tour ownership and
map highlights before installing the QRY spawn and invoking the existing R7
reset. If R7 performs a fall reset during LIVE, Run v0 accepts that completed
reset, freezes the craft for its countdown, and never issues a second reset.
A fall during free roam remains ordinary R7 free-roam behavior.
