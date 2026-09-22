# Web feasibility v1 decision packet

**Disposition: PAGES_PLUS_LARGE_ASSET_HOST.** The current full game exports and
runs in Chromium without changing any existing playable source. Keep Web as a
routine, provisional regression target while native development resumes. This
is not visual parity, general browser/performance acceptance, or release approval.

## Authority and scope

Starting commit: `df221870b45de53e4ebb5ea8889b6cf1114054c6`.
`git ls-remote origin refs/heads/main` independently returned this exact commit.
Its September 7 checkpoint record documents Charlie's played Quarto approval.
Fresh local clone; branch `feature/web-feasibility-v1`. The old checkout's five
untracked editor UID files were left alone. No older handoff was treated as main.

Read root/nested AGENTS, README, the dated checkpoint, current Quarto and
world/weather/surface authorities, project settings, launch/verification tools,
runtime world-data loaders, presentation/weather implementations and Run/BRRR.
The old root M5 mission is superseded by the owner's current Web request.

All 310 baseline files under `game/` remain byte-identical. This includes native
project settings, Quarto rig/data, controller/tuning, camera, world geometry,
materials/weather, Run/BRRR, minimap, telemetry, fixtures and historical records.
No Web-specific project-setting override proved necessary: the engine's Web
default selects Compatibility while the native default remains Forward+.
This was confirmed in both runtime banners, not inferred from the preset.

Added: `game/export_presets.cfg`, `tools/export_web.py`,
`tools/verify_web_lane.py`, `tools/web_smoke.gd`, this packet, compact structured
results, `docs/WEB_FEASIBILITY_STATUS.md` and `WEB_FEASIBILITY_V1_AUTHORITY.md`.
Root README/AGENTS have new preambles retaining their previous contents.
The historical root STATUS remains byte-identical; Web status is versioned separately.
No existing playable GDScript, scene, asset or project setting was edited.

## Repeatable commands

Run from the repository root, with Python 3.9+ and the already-installed engine:

```sh
python3 tools/verify_web_lane.py
python3 tools/export_web.py --godot /Applications/Godot.app/Contents/MacOS/Godot --output build/web-1
python3 -m http.server 8067 --bind 127.0.0.1 --directory build/web-1/web
```

Open [the local game](http://127.0.0.1:8067/) in Chromium. Keep a 1280×720 canvas;
the inherited HUD uses fixed offsets. The preset uses project-sized canvas
policy, single-thread release, no extensions, no PWA/service worker or isolation
headers. Desktop texture compression is selected; mobile-browser support is not
certified. Do not launch the HTML through `file://`.

The engine must report `4.7.1.stable.official.a13da4feb`. The helper resolves the
existing engine using the repository launcher. It requires
`web_nothreads_release.zip` in the standard `4.7.1.stable` template folder, or
`--template /absolute/path/web_nothreads_release.zip`. Its SHA-256 must be
`b7b7d7da29fc6cc2f4934fdd26cc571a40e7af57f716ea3eb7e18da720dae28a`.
The exported WASM is checked against that ZIP's WASM. No engine/template download
or substitution occurs. The browser independently reported that same engine
identity and Emscripten 4.0.20, single-threaded, no GDExtension support.

The helper stages current source into a disposable directory, imports, exports,
rejects error logs, verifies source stayed unchanged and writes `build.json`
beside `web/`. That manifest records commands, input hashes, output hashes,
inventory, sizes and hosting disposition. Outputs must be new directories and
outside `game/`; all local caches remain disposable. Existing Git ignore rules
exclude `build/`, exports, logs, archives and caches. Only `web/` is a future
serving artifact; `build.json` and logs are evidence, not site content.

Explicit include filters preserve runtime-loaded world JSON/BIN, presentation
JSON (including Quarto), and diagnostic fixture JSON. Resource export includes
the dynamically loaded native surface images. No game splitting or art reduction
was performed. The conservative first package still contains test resources;
future package pruning is not required to establish this lane.

Repeated fresh exports have identical sizes and identical WASM, JS, HTML and
image hashes. PCK hashes differ. This is a reproducible process, **not a claim of
bit-identical PCKs**; pack-level nondeterminism has not been isolated. Address
immutable hosted artifacts by the actual output hash/build manifest, not an
assumption that a source commit always implies one binary hash.

Optional, separately labeled diagnostic build:

```sh
python3 tools/export_web.py --smoke --output build/web-smoke-1
python3 -m http.server 8068 --bind 127.0.0.1 --directory build/web-smoke-1/web
```

Open it and look for `WEB_SMOKE_RESULT` with `status: PASS` and all 13 checks true
in the browser console. This disposable entry instantiates the unchanged full
game. It is not the playable artifact and is marked `diagnostic_entry` in its
manifest. It directly exercises synthetic finish crossing, results freeze,
free-roam return, countdown, retry, paused retry, clock pause, Quarto endpoint
API posing, minimap presence and world load. Native tests remain separate:

```sh
python3 tools/verify_quarto_vehicle.py --native --evidence /absolute/new/native-evidence
```

Run native display tests sequentially and keep other GPU workloads idle. The
old `verify_repo.py` is intentionally still expected to reject the two Quarto
vehicle files; never update historical checksums to make it pass.

## Measured full-game artifact

| File | Raw bytes | MiB |
| --- | ---: | ---: |
| index.wasm | 39,513,091 | 37.68 |
| index.pck | 101,717,356 | 97.01 |
| index.js | 279,815 | 0.267 |
| index.html | 5,469 | 0.005 |
| index.audio.worklet.js | 7,298 | 0.007 |
| index.audio.position.worklet.js | 2,973 | 0.003 |
| index.png | 21,443 | 0.020 |
| index.icon.png | 5,700 | 0.005 |
| index.apple-touch-icon.png | 11,944 | 0.011 |
| **Total** | **141,565,089** | **135.01** |

The first browser load recorded 141,537,405 response-body bytes for requested
subresources and 141,538,905 Resource Timing transfer bytes (five requests;
navigation HTML is excluded by that API query). The server used identity
encoding. All-file gzip estimates are about 24,557,816 bytes / 23.42 MiB; they
are offline estimates, not measured CDN transfers. PCK compresses to about
13.73 MiB and WASM to 9.59 MiB. Compression does not make the raw files eligible
for ordinary direct Pages asset upload. No transfer-optimized artifacts were
committed or deployed.

## Verification and retained failures

- Legacy verifier: 389 checks, FAIL only for the two expected historical
  Quarto vehicle-byte mismatches, both before and after wrapper changes.
- Quarto source/data: 449/449 PASS before work and after tooling changes.
- Fresh native suite: exact Metal 4.0 Forward+, Apple M5. Quarto 39 PASS;
  Run 54 PASS; paused retry 15 PASS; both C1 traces exactly equal for 1,260 ticks,
  SHA-256 `29f1049f8e16ec65d288407c35e6ccae46e87c711bb6b54b134e6158c68b9443`.
  Both three-pose capture sets passed. Quiet Surfaces comparison world passed.
- **Current checkpoint world traversal: FAIL**, `INPUT_TRAVERSE:QUARRY_DEPOT:0:false`.
  Spread progressed 45.635086 m of 53.851646 m in 600 ticks; no contacts,
  impacts, resets or unsupported ticks. Cause unestablished. The complete fresh
  native suite therefore remains FAIL. No gameplay repair or threshold change.
- Initial sandboxed native display processes aborted with code -6; headless
  checks ran, with certificate/editor-settings permission errors retained.
  A separate display-enabled run produced the observations above. It does not
  erase the first attempt. Initial sandbox export also retained editor-settings
  errors; later display-permitted exports had no `ERROR:` lines.
- Web preservation check: six checks PASS, all 310 baseline game files exact.
  Missing-template negative check rejected before creating an output directory.
- Full game: Chromium startup/runtime logs contained no engine or JS errors;
  runtime reported 17 routes, 19 source solids and world-polish-v1 authority.
- Separate Web smoke: **13/13 PASS**, using the unchanged full-game APIs.
  Synthetic finish is not proof of a player completing the route.
- Earlier browser attempts to invoke retained SceneTree fixtures via `--script`
  ran the normal game without results. Alternate custom-main-loop fixture packs
  reported no main scene. Neither attempt is a fixture pass; the successful
  Node-scene smoke supersedes this diagnostic approach only.

The historical Market–Clinic p95 +14.61% miss, capture interruption and September
7 unreproduced entrance failure remain history, with their original meanings.
No human comfort, physical-gamepad, world, desire or performance gate was passed.

## Browser observations and compatibility classification

Chromium 151.0.7922.34, macOS Apple M5, ANGLE Metal, WebGL 2 Compatibility,
1280×720, device scale 1, no cross-origin isolation. Two foreground 20-second
requestAnimationFrame samples with native Godot stopped:

| Workload | Mean ms | p95 ms | Maximum ms |
| --- | ---: | ---: | ---: |
| Idle at QRY | 16.67 | 17.70 | 18.70 |
| W + Shift + A sustained Drive/turn | 16.71 | 18.40 | 50.10 |

About 60 fps. Local world-ready log arrived in 2.54 seconds in this observation;
this is not a cold-WAN startup benchmark. RAF cadence is not GPU frame time or a
native/Web matched performance ratio. No low-end, long-session, memory-pressure,
full-city route, mobile or Safari/WebKit certification was performed.

**A — Structural blockers:** none observed during the bounded full-game keyboard
sample and diagnostic smoke. Broader traversal/long-session coverage remains
open, particularly given the fresh native entrance failure. Hosting directly
on Pages is structurally blocked by both large assets.

**B — Presentation differences:** Web architecture and cyan emission appear
brighter/more saturated than the native capture; material/lighting parity is not
established. City, terrain, Quarto geometry and cloudy panorama remain visible.
Drizzle is visible, but particle floor/contact parity was not certified. Two HUD
direction arrows render as missing glyph boxes; text, timers and minimap remain
readable. These were left for a bounded future presentation decision, with no
Compatibility art redesign. Godot documents a different Compatibility lighting
path and built-in Web renderer default:
[4.7 project settings](https://docs.godotengine.org/en/4.7/classes/class_projectsettings.html).

**C — Ordinary future polish:** inherited city/art preferences, handling/comfort,
BRRR's provisional balance/farming behavior and earlier native performance
issues are not established Web regressions and were not changed here.

Keyboard: W thrust, S brake, A/D steer, hold Shift Drive, release to Spread,
Space supported Hop, R retry, Escape pause, F on results free roam, Tab diagnostic
locations, F1 details. Browser captures show Drive at 33.0 m/s with BRRR rising,
Spread/Hop input, pause clock holding and paused retry/countdown recovery.
Keyboard controls require canvas focus. The synthetic smoke separately verifies
finish/results and return to free roam; an end-to-end player-driven finish is
still untested in Web.

No physical gamepad was exposed by `navigator.getGamepads()`. Existing mappings
are unchanged: left stick throttle/brake/steer, button 0 transform, 3 Hop,
2 retry, 6 pause. Actual mapping/feel requires a device. Godot notes activation
by a button press, browser mapping differences and secure-context requirements.
Escape pause works and the smoke confirms the clock stops while paused.
Automated background experiments produced no document visibility events, so
they do not prove hidden-tab suspension; the clock continued while merely
unfocused. Explicitly pause before leaving the game until real tab/resume and
held-key behavior are checked. See
[Godot Web limitations](https://docs.godotengine.org/en/stable/tutorials/export/exporting_for_web.html).

## Hosting decision; no deployment performed

Pages' current limit is **25 MiB = 26,214,400 bytes per asset**. Both measured
large files exceed it. Cloudflare explicitly recommends R2 for larger files:
[Pages limits](https://developers.cloudflare.com/pages/platform/limits/).

The small candidate architecture is a Pages front door at the eventual
`hush-basin.cmish.dev`, plus versioned immutable WASM/PCK objects in R2. Keep the
engine JS/audio helpers and pack from one build together. Serve WASM as
`application/wasm`, PCK as `application/octet-stream`, correct content lengths,
and compression with matching Content-Encoding when configured. Validate the
actual served bytes and cache behavior before any release. No game split or
threaded-Web/COOP/COEP requirement was demonstrated.

Two implementation options remain reviewable:

1. Same-origin large-asset paths streamed from an R2 binding through a small
   Pages Function/Worker. Preserve the ordinary Godot file layout and loader;
   stream bodies instead of buffering a 97 MiB PCK in worker memory. This avoids
   cross-origin loader plumbing. Deployment/runtime/cache behavior is untested.
2. A custom Godot shell with immutable alternate engine/pack URLs and CORS from
   an R2 custom-domain origin. Godot's documented `executable`, `mainPack`,
   `init`, `preloadFile(url, virtualPath)` and `start` APIs provide the seams:
   [shell API](https://docs.godotengine.org/en/stable/tutorials/platform/web/html5_shell_classref.html).
   Keep browser fetch URLs separate from the virtual pack filename when using
   the lower-level API. The exact generated loader was inspected.

The simple absolute `executable`/`mainPack` override was attempted on two local
ports. WASM/PCK requests were initiated but no responses/world-ready result
arrived before the bounded timeout; the second server was separately reachable
by curl. No engine/JS error identified a cause. **Alternate-origin loading is
not yet validated**, so do not treat the custom-shell option as deployment-ready.
A same-origin streamed route is the conservative first hosting implementation
to validate. This task deliberately adds neither infrastructure nor a shell
whose success has not been demonstrated.

For direct browser reads, configure R2 CORS for the exact front-door origin and
GET/HEAD as needed; custom-domain caching must also preserve those headers.
Use a production custom domain rather than treating the development r2.dev URL
as the deployment design. Sources:
[R2 CORS](https://developers.cloudflare.com/r2/buckets/cors/) and
[public buckets](https://developers.cloudflare.com/r2/buckets/public-buckets/).

## Remaining gates and recommendation

Retain this lane for routine export, startup/input and separate smoke regression.
Native Forward+ remains authoritative for intended presentation and handling.
Resume development without a game fork or broad Web redesign. Before calling
Web a supported release target, resolve the native traversal result, complete a
browser-driven Run finish, check real tab/key recovery and a physical gamepad,
review weather/text/lighting differences, test another browser and weaker device,
and validate the chosen immutable-asset hosting path. These are explicit pending
checks, not automatic failures or permission to begin the next successor.

Raw evidence and captures are kept outside Git in the sibling directory
`Hush-Basin-Web-Evidence-20260913/`; compact results are in
`WEB_FEASIBILITY_V1_RESULT.json`. Useful captures: `browser-1/startup.png`,
`browser-1/drive.png`, `browser-1/paused.png`, `browser-1/paused-later.png`,
`browser-1/paused-retry.png`, `browser-1/retry-live.png`, and native
`baseline-native-display/successor-camera-poses/vehicle-r7-spread-world.png`.
Native/Web pictures are qualitative observations, not a pixel-matched parity test.
