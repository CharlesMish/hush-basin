# District Zero P1A — Polish R5 owner review

Double-click `PLAY_DISTRICT_ZERO_POLISH_R5.command` to play the polished
standalone project with the existing exact Godot 4.7.1 installation.

This pass changes presentation only. It provides a quieter default HUD, a
clear route-selection panel, an explicit pause card, active-route emphasis on
the minimap, a restrained procedural horizon, and compact ring-style route
markers. Movement, craft behavior, collision, world geometry, routes, camera,
lighting, shadows, and acceptance thresholds are unchanged.

The launcher prevents two copies of this same project from starting at once.
If Godot itself crashes, close every remaining Godot window/process before
launching again. A stale launch lock is removed automatically when no prior
launcher process remains. Generated `.godot` data is disposable; the launcher
does not delete it automatically.

The terrain's jagged color ribbons were reviewed but deliberately left alone.
They are authored terrain-class boundaries, not the invisible-wall defect, and
smoothing them safely would require a separately bounded render-color study.

This is an owner-review build, not P1A PASS or Human World Gate authorization.
Human attempts in automated verification: 0. P1B remains frozen.
