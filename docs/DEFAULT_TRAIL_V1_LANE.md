# Default trail v1 — separate presentation lane

Starting state: Charlie's played Mastery Alpha handoff
`66b4c228264d6c2966a8af68243898fc21c6573d`. This isolated lane follows the
Persistent Consequence v0.1 commission only for baseline trail presentation.
Relay project state, Dispatch, rewards and saving are outside this lane. The
lead removes the former cosmetic-purchase gating separately.

The existing trail showed two broad, hard-edged pale bands during a drift. It
also computed each segment's side vector independently, and could join samples
across a short interval in which it emitted no trail. The successor uses one
shared frame at each sample, feathers each ribbon from its center to transparent
edges, and tapers/fades its older end. New emission after a slow/unfolded interval
starts a separate tail. Wall contact and relocation clear history; reset clears
history, mesh and observer state. Pause remains pausable.

The default keeps the accepted teal/pale warm palette. Ordinary qualifying fast
Drive emits thin, faint ribbons; the unchanged genuine-drift predicate drives the
wider/brighter response. No correction grace or scoring tolerance is added.
Past drift light fades in its original world positions rather than following
the craft. The original central propulsion particle trail is unchanged.

`game/presentation/default_trail_v1.json` holds appearance/lifetime dimensions.
`trail_ribbon_profile.gd` derives visual frames only. Existing
`mastery_trail_palette.gd` remains RGB-only, so future appearances can share the
same functional width/alpha response. No trail catalog, currency or project
dependency is introduced here.

Resource bound: 18 history samples, one ImmediateMesh surface and one native
StandardMaterial3D. At most 408 triangle vertices, up from 204. There are no new
textures, shaders, lights, particles, collisions or render passes. Sampling stays
30 Hz; mesh aging now redraws every physics tick for smooth fade. This small CPU
increase still requires the integrated native/Web cost lane; movie render
statistics are not a performance verdict.

## Observed lane verification

Engine: `4.7.1.stable.official.a13da4feb`.

- `--headless --script res://tests/default_trail_probe.gd -- --result <path>`:
  13/13. Finite/bounded curved geometry, tail fade, stronger genuine-drift
  response, exact shared seam positions, transparent edges, one bounded surface,
  separated gaps, safe empty geometry and clearing.
- `--headless --script res://tests/mechanics_c1.gd -- --output <path>`:
  all 1,260 JSONL ticks exactly equal the accepted handoff trace. SHA256
  `29f1049f8e16ec65d288407c35e6ccae46e87c711bb6b54b134e6158c68b9443`.
- Matched native Forward+ `mastery_movie.gd --line DEP_style` captures:
  1280 × 720, 30 FPS, 766 frames each. The complete result dictionaries and all
  39 sampled route records are identical: delivery 20.45 s, longest genuine
  drift 3.783333 s, BRRR 2047.2972999, zero impacts, cargo 100%.
- Inspected matched ordinary-camera straight/drift stills. The hard ribbon edges
  are gone; the original center propulsion particles remain visible. Comfort,
  attractiveness and feedback clarity remain owner judgments.
- Frozen controller, tuning, motion math, camera, Quarto, BRRR and line predicate
  sources are untouched by this lane. No native scene or gameplay is changed.

Evidence lives outside source under `evidence/trail-lane/`: paired MP4s, matched
stills, result/trace JSON, geometry probe, movement parity and engine logs.
The initial probe inspected a near-expired center vertex whose native alpha was
quantized to zero; the assertion now inspects a visible mid-tail vertex. An
initial check command used a relative engine log path and crashed while Godot
tried to create that path beneath `user://`; rerunning with an absolute log path
completed. Headless import also reported denied global editor-settings writes
and a macOS certificate warning. Native captures completed without script errors.

The old Depot challenge used for this visual comparison is a retained harness,
not endorsement of its mastery design. The lead's basic-job cleanup is separate.
Web rendering and integrated preservation/cost checks are required before handoff.
