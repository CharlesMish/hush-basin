# Hem Loop rink v0.1 — design and verification record

A separately launchable Hush Basin experiment: one dedicated racing circuit for
a solo time trial, plus one short story encounter on the same circuit where how
you drive matters to someone. Built November 5, 2026 in a cloud session.

## Provenance and boundaries

- Base: `review/story-ground-20261001` (draft PR #3) at
  `a9d7aceffb07fe6326bfa6021645d4a6d43c7755`, the recorded checkpoint `a9d7ace`.
  Experiment branch: `claude/hush-basin-racing-rink-3bifsv`, which starts
  exactly at that commit. Nothing was merged, and nothing was deployed.
- Engine: the official Godot `4.7.1.stable.official.a13da4feb` Linux x86_64
  build and export templates from `godotengine/godot-builds`, SHA-512-checked
  against the release's `SHA512-SUMS.txt`. The extracted
  `web_nothreads_release.zip` matches the repository's pinned SHA-256
  `b7b7d7da…dae28a`. The cloud container has no GPU: physics and logic ran
  headless; images came from the Compatibility (OpenGL/llvmpipe) renderer under
  Xvfb and from SwiftShader WebGL in headless Chromium. Forward+ and real-GPU
  frame rates were not exercised.
- No existing file is modified except a prepended section in `AGENTS.md` and
  `game/AGENTS.md`. `project.godot` still starts the story with its own user
  directory; the rink writes no file at all, so story saves cannot be touched.
  `tools/verify_rink.py` checks all of this against the base commit.
- The rink instances the unchanged `scenes/craft.tscn` (controller, colliders,
  probes, Quarto visual rig), `resources/default_tuning.tres`, and
  `scripts/camera_rig.gd`. It reuses the Basin palette
  (`world/world_polish_v1.json`) and the warm-overcast sky, light and drizzle
  (`presentation/warm_overcast_v1.json`). Handling and camera are exactly the
  game's; only the ground is new.

## Place and purpose

**The Hem Loop, Depot yard.** Depot is where Tess sewed on a borrowed table for
a year ("Yard's quieter without her"), and Depot's yard is where the game's own
notes already put deliberate fast Drive drifts. The rink is the freight crew's
old turning loop behind the sheds, ringed by low sandstone walls with the
Basin's teal band. On wet evenings the crew race it alone, against a chalkboard
at the start line, which shows tonight's best lap in the world as you set it.
The big bend is called the Hem; the crew run explains why.

## The lap (782 m, counter-clockwise)

| Piece | Shape | Width | What it asks |
|---|---|---|---|
| Yard Straight | 205 m | 24 m | Drive to ~33 m/s. Start/finish gantry 58 m in, grid 36 m behind it. |
| **The Hem** | 200° left, R 66 m | 38 m (17 in / 21 out) | The signature bend. Scrub at the 150/100/50 boards, then a long sideways Drive drift. Outer 12 m is a banked, turned-up edge (2.4 m rise). |
| Hem exit | 36 m | 13 in / 19 out | Wide outside so a drift can run out. |
| The Points | 20° right, R 110 m | 24 m | The flick back the other way. |
| Long Siding | 127 m | 24 m | Drive; the yellow crane frames the next corner. |
| **Crane Corner** | 90° left, R 24 m | 26 m | Unfold to Spread. Inside it, a 0.5 m loading dock behind a 1 m red **HOP** buffer: Spread + Hop and cut the corner. |
| Dock Lane | 45 m | 22 m | Back into Drive. |
| The Gate | 90° left, R 40 m | 29 m | Drift onto the straight; the gantry is visible across the infield. |

The centreline lives in `game/rink/hem_loop_course.json` (straights and arcs,
plus widths, gates, dock, bank and story anchors).
`python3 tools/rink_layout.py --check` confirms closure: 0.5 mm, 360°.

Readability: a checkered line under a "HEM LOOP / DEPOT YARD · RACE THIS WAY"
gantry, a grid box, amber ground chevrons after the grid and before each major
corner, brake boards, edge lines, the painted name THE HEM on the bend's inner
wall, an amber skim stripe at the foot of the Hem's outer wall, a minimap with
gates, and a WRONG WAY warning.

## Shaped around what the craft already does

I measured the handling first (headless, real controller) and shaped the
corners around those facts, rather than the reverse:

- **Drive has almost no lateral authority at top speed.** Thrust tapers from
  29 m/s² at 25 m/s to zero at 35 m/s, and the nose turns at most 0.44 rad/s.
  At 33 m/s, full lock barely bends the path. A held full-lock Drive drift
  settles at about 27–30 m/s on a 61–68 m radius with 30–70° of slip. That is
  the ridiculous sideways line, so the Hem's radius is 66 m.
- **Walls do not carry Drive round a bend.** The craft is a floating
  `CharacterBody3D`, and its velocity is not slid along walls, so on a curved
  wall it keeps pointing into the wall. Every tick then registers a small
  impact, and Drive loses up to 82% of its speed per full-severity hit. Light,
  shallow skims are cheap; leaning on a curved wall is not. So the Hem's
  outside is a **berm instead of a wall**: on the bank, the craft's existing
  slope-following hover turns gravity into inward pull, up to ~6.7 m/s² near
  the top. The u² profile has zero slope where it starts, and at its steepest
  (~22°) it still leaves the Drive collider ~0.18 m of clearance.
- **Spread is the precision form.** It turns at 1.9 rad/s, brakes at 19 m/s²,
  loses at most 18% of its speed on an impact, and is the only form that can
  Hop. It runs about 14–17 m/s. So the tight inside line, Crane Corner and the
  dock belong to Spread.

Hem drift envelope with simple, human-style inputs (no feedback steering;
`tests/rink_hem_sweep.gd`), before and after the bank:

| Input pattern into the Hem | Flat outer wall | Banked outer edge |
|---|---|---|
| Full lock + throttle, no scrub | 9.48 s · 4 hard hits · min 5.5 m/s | 9.47 s · 0 hits · min 22.3 m/s |
| Brake 0.8 s from the 100 board | 22.0 s · 7 hits | 8.80 s · 0 hits |
| Brake 1.0 s from the 50 board | 10.2 s · 5 hits | 9.48 s · 0 hits |
| Spread flick 0.25 s at the 50 board | 21.6 s · 6 hits | 8.60 s · 0 hits |
| Spread flick 0.40 s at the 50 board | 8.10 s · 0 hits | 7.90 s · 0 hits · 84° slip, min 29.6 m/s |

The first lap is survivable, and a better entry is worth about 1.5 s. Earlier
geometry passes, each found by driving the bot and reading the traces: the Hem
grew from R 58 to R 66 and its outside from 17 to 21 m; the Hem exit stopped
narrowing into the drift; the Points eased from R 70 to R 110; and the lamp
posts and crane legs moved back where the chase camera swings outside the wall.

## Time trial

- From the title card, W or Enter (or the stick forward) starts racing in the
  same keypress. The craft sits on the grid; the clock starts at the line, and
  every lap after that is a flying lap.
- Ordered gates: line → Hem apex → Long Siding → Dock Lane → line. A lap counts
  only when every checkpoint was crossed forward, in order.
- Forgiving validation: each gate spans wall to wall plus 4 m. Backward
  crossings are ignored and never cancel progress. Every forward line crossing
  restarts the clock, so doubling back over the line can restart a lap but can
  never earn one. A refused lap names the checkpoint it missed. Crossing times
  are interpolated inside the 60 Hz physics step.
- R puts you back on the grid for a fresh attempt; the abandoned lap is
  discarded without counting as a refusal. Esc pauses; T/C switch modes.
- HUD: running clock, last and best, valid and not-counted laps, split deltas
  against your best at each checkpoint, and a lap banner with four sector times
  (★ marks a sector best). Tonight's best also appears on the chalkboard.
  Session best only; nothing is saved.
- One-time tips, at most once per session: after a hard Drive strike entering
  the Hem, and after striking the dock buffer.

## Crew run: "the Hem"

Tess's borrowed table stood on the inside of this bend for the year she sewed
at Depot. The night run is short one mended jacket. Tess is back at her old
spot, leaning over the inside wall at the apex with it held out.

- **What you do differently, and why.** The fast solo line rides wide in
  Drive. To take a jacket from someone's hand without stopping, you unfold
  early and brush the inside wall in Spread. The bot's inside line is ~5 s
  slower across the two sectors that span the Hem (24.4 s vs 19.3 s): it's the
  line you would never take for time.
- **What responds to what actually happened.** You catch the jacket if the
  craft passes within 3.4 m of her hand (centre within ~5 m of the wall):

  | What happened | Visible from the craft | Who answers |
  |---|---|---|
  | Pass the apex wide | Tess still holding it, pulsing amber ring, chalk marks along the inside line | Tess: "Too wide…", then two further, firmer hints |
  | Catch in Spread, first pass / later pass | Jacket strapped on your rear deck; her empty arm lifts | Tess: "That's it. First time, too." / "There. Go on, they're waiting." |
  | Catch crawling (< 7 m/s) or folded in Drive | Same | Tess: "You can keep moving, you know…" / "Folded, at that speed? Show-off." |
  | Wall hits while carrying (severity ≥ 0.15) | Grey scuffs appear on the jacket | Crew at the line: "Bit of wall on the sleeve…" / "…half the yard wall back on it." |
  | Deliver clean, first pass / after misses | Night driver at the line is now wearing it | Crew: "First pass, and not a mark on it. Ta." / "Took a few goes. Not a mark on it, though." |
  | Next pass of the Hem afterwards | — | Tess, about the jacket's condition |

  Then the crew say why the bend has its name: "Her table sat on the inside of
  that bend for a year." / "You took your mending off her tight, or went round
  again." / "That's why it's the Hem."
- Lines are one short sentence each, shown in a strip at the top of the screen
  with Tess's existing portrait. They never pause play.
- A friend can ignore all of it: the title card defaults to the plain time
  trial, and T returns to it from pause.

## Play it

- Web, the easiest: `hem_loop_web.zip` (built by
  `python3 tools/export_rink_web.py --output <new dir> --zip`). Unzip it and run
  `PLAY_IN_BROWSER.command` or `python3 serve_hem_loop.py`; a browser opens at
  `http://127.0.0.1:8765/`. It is a single-thread build, so no special headers
  are needed. ~45 MB unpacked, of which the stock engine WASM is 39.5 MB and the
  game pack 4.8 MB.
- Native: `python3 tools/play_rink.py`, `PLAY_RINK.command`, or directly
  `godot --path game res://rink/rink.tscn`. Add `--compatibility` to the
  launcher to match the Web renderer.
- Controls and a "try these two things" card: `HEM_LOOP_PLAY_CARD.md`.

## Verification (what was run)

All commands run from the repository root with `GODOT_BIN` set to the exact
engine. Results below are from the final commit unless noted.

Engine `4.7.1.stable.official.a13da4feb`, Linux x86_64, this cloud container.

| What | Command | Result |
|---|---|---|
| Untouched base, before any change | `python3 tools/verify_story_fine_ground.py`; `python3 tools/verify_slices.py --phase complete --output <dir>` | 899/899 static PASS; contiguous story 275/275 PASS |
| Base preservation, scope, startup, saves, closure | `python3 tools/verify_rink.py` | 10/10 PASS (every base file byte-identical except the prepended AGENTS sections) |
| Rink suite, headless native | `godot --headless --fixed-fps 60 --path game --script res://tests/rink_suite.gd -- --result <file>` | **63/63 PASS** |
| Story on this branch | `python3 tools/verify_rink.py --native --evidence <dir>` | rink suite PASS + contiguous story **275/275 PASS** (same count as the base) |
| Rink suite inside the exported Web build | `python3 tools/export_rink_web.py --smoke --output <dir>`, then Chromium on `?draw=0` | 58/58 PASS at `a12ff6c` in headless Chromium (SwiftShader WebGL2; 13.7 min; no console errors); the clean-delivery scenario added afterwards: BROWSER_CLEAN |
| Playable Web build in Chromium | `python3 tools/export_rink_web.py --zip --output <dir>` | Loads in ~3–5 s, no console errors; title card, W to race, Shift Drive, Esc pause, C crew run all respond |
| Hem input sweep | `godot --headless ... --script res://tests/rink_hem_sweep.gd` | 7 simple input patterns, 0 hard hits with the bank (table above) |

What the suite drives (all through ordinary input actions):

- **Consecutive valid laps:** 3 flying laps in a row, 34.96 / 35.08 / 35.05 s.
  Checkpoints arrive in order every lap, the best is the minimum, sectors sum to
  the lap, and the chalkboard shows the best.
- **Doubling back over the finish:** cross the line, stop, turn round, cross it
  backwards, turn round, cross forwards. No lap is awarded; the refusal lists
  all three checkpoints; the clock restarts; the next full lap counts (35.85 s).
- **Skipped checkpoint:** a labelled test-only jump across the Hem infield
  (the walls make a real cut impossible). The lap is refused, the HUD says
  "missed the Hem", and the next lap is valid.
- **Retry:** R mid-lap puts you back on the grid with the clock at 0:00.00. The
  lap is discarded rather than refused, and the next attempt is a valid 34.96 s.
- **Story hit:** inside line, caught on the first pass in Spread at 14.2 m/s,
  3.2 m from her hand; jacket visible on the craft, Tess's hand empty; delivered
  at the line; the night driver now wears it.
- **Story miss, then hit:** the fast wide line sails past (miss recorded; Tess
  still holding it; ring and chalk shown; "Too wide…" spoken). The next lap on
  the inside line catches on attempt 2, and the crew's answer acknowledges the
  retries or the scuffs.
- **Scuffs:** deliberately hitting a wall while carrying marks the jacket, and
  the crew comments on the wall.
- **Clean delivery:** careful Spread line home. 0 scuffs; "First pass, and not
  a mark on it. Ta."; the three-line reveal; and on the next Hem pass Tess says
  "Clean all the way round. Now I've seen everything."
- **Entry and modes:** W starts racing in the same keypress and the craft is
  moving within half a second; C on the title card or after Esc starts the crew
  run; T returns to the plain time trial.

Bot reference laps (relative, not human pace):

| Line | Lap | Yard→Hem apex | Hem apex→Siding | Siding→Dock | Dock→Line |
|---|---|---|---|---|---|
| Spread flick + Drive drift | 34.96 s | 9.37 | 9.96 | 8.10 | 7.65 |
| Same + **dock Hop** | **32.63 s** | 9.36 | 9.97 | **6.86** | 6.48 |
| Crew-run inside line | 40.45 s | 12.51 | 11.88 | 8.78 | 7.28 |
| Lazy Spread on the centreline | 57.19 s | 18.73 | 17.66 | 10.24 | 10.58 |

The browser and native runs produced the same lap times to about 10⁻⁵ s, the
same impact counts and the same story outcomes on this host pair. That is
agreement on one machine, not a cross-platform determinism claim.

## What still needs hands on the controls

- **Feel.** Every lap here was driven by a test bot pressing ordinary inputs
  (`tests/rink_bot.gd`: no pose or velocity writes, except the one labelled
  infield-cut fixture). The bot is a mediocre driver that scrubs walls a human
  wouldn't. Lap times show relative line value, not human pace. Whether the Hem
  drift is satisfying, whether the berm feels like a gift or a crutch, and
  whether the dock hop is discoverable on lap 1 are owner questions.
- **Readability at speed.** Brake boards, chevrons and Tess's silhouette were
  checked in still frames only, not at full frame rate on a real display.
- **Performance.** Desktop GPU frame time, phone/touch play, gamepad feel and
  Forward+ were not measured. Software rendering here manages ~2 fps, which
  says nothing about a real machine.
- **Story tone.** The lines are new. Tess's voice follows the existing chapters,
  and the night crew are unnamed Depot voices, as in the opening. They are
  short by design; whether they land is yours to judge.
- **Out of scope:** AI opponents, a second track, progression, saved bests, and
  any link from the main game into the rink.

## Files

- `game/rink/` — scene, course data, builder, timing, HUD, minimap, drizzle,
  crew run and its text.
- `game/tests/rink_*` — input bot, racing-line plans, checks suite (headless
  and browser), Hem sweep, capture tool.
- `tools/export_rink_web.py`, `tools/play_rink.py`, `tools/rink_layout.py`,
  `tools/verify_rink.py`, `PLAY_RINK.command`, `HEM_LOOP_PLAY_CARD.md`.
