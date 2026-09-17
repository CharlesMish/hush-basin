# Web shell presentation v1

Baseline: `c683f189afe44af127629d0cfa4b6873d27e6113`.
Branch: `feature/web-shell-presentation-v1`.
The owner confirmed production hosting works and requested a bounded Web shell
presentation correction. Proof-resource cleanup is outside this successor.

The accepted build remains
`3ac4997d783741ccd07ff74298302c622fe62300484ef2f55bf3a2153e42b0c0`, exported from
`df221870b45de53e4ebb5ea8889b6cf1114054c6`. No fresh export was made. All nine
original files, including generated HTML, remain unchanged under `/builds/ID/`.
Native Forward+, the game, world, HUD, handling, and 1280×720 composition are
unchanged. WASM/PCK keep their exact private R2 keys and served SHA-256 identities.

## Presentation seam

The existing template used `canvasResizePolicy: 1`. Inspection of the exact
exported loader showed its CSS dimensions are desired dimensions divided by
device pixel ratio. That left the 1280×720 backing canvas displayed at 640×360
CSS pixels in the Retina Chromium capture.

The derived shell supplies explicit canvas width/height 1280/720 and
`canvasResizePolicy: 0`. CSS independently fits the largest 16:9 rectangle inside
the viewport and centers it on both axes. No DPR division, backing-buffer resize,
scene/HUD relayout, cropping, or stretching occurs. Dynamic viewport-height units
are used where supported, with ordinary viewport units as fallback.

The small Fullscreen button calls the browser API directly from its click gesture
and returns focus to the canvas. There is no F-key or other gameplay-key shortcut.
There is no global Escape handler. Escape retains browser fullscreen exit and
the existing game pause behavior; Chromium may also pause when exiting. Escape
again resumes normally. The Exit fullscreen button changes only presentation,
preserving the current pause state. No input is synthesized and no pause/game
state is manipulated. Unsupported browsers hide
the button and keep fitted windowed presentation. Audio initialization, loader,
worklets, and game files are unchanged.

References checked: [Godot shell configuration](https://docs.godotengine.org/en/stable/tutorials/platform/web/html5_shell_classref.html)
and [Fullscreen API](https://developer.mozilla.org/en-US/docs/Web/API/Fullscreen_API).
Godot's documentation notes incomplete 4.7 updates, so the exact exported loader
was inspected as well as the observed runtime.

## Immutable shell identity and repeatability

`tools/web_shell.py` derives one HTML file from the validated original. It adds a
same-origin `<base href="/builds/ID/">`, CSS and fullscreen logic. Original JS,
WASM, PCK, worklets and icons still load from their original paths. The shell's
SHA-256 is its own ID under `/shells/SHELL_ID/index.html`. Root redirects to this
presentation URL. `/production.json` retains the unchanged current build ID and
adds `current_shell_id` and a hash/size registry of retained shells.

`tools/deploy_web.py` stages, retains, and verifies these small shell files in
addition to the original build files. Future export/preview/promotion commands
from the production runbook automatically include the fitted shell. Both old
build URLs and old shell URLs remain immutable. Rolling a game build back through
the helper uses the current shell implementation with the selected old game.
For a shell-only rollback, revert the CSS/JS/rendering changes in source and
preview/promote the same accepted export; the derived prior shell ID is reused.

## Verification

All original artifact hashes and the added shell hash are checked through the
preview and production origins. Raw evidence resides in sibling
`Hush-Basin-Web-Shell-Evidence-20260914/`.

Chromium observed canvas geometry before promotion:

| Browser viewport | Displayed canvas | Offset (x,y) | Backing canvas |
|---|---|---|---|
| 1280×720 | 1280×720 | 0,0 | 1280×720 |
| 1600×1000 | 1600×900 | 0,50 | 1280×720 |
| 1800×900 | 1600×900 | 100,0 | 1280×720 |
| 1000×900 | 1000×562.5 | 0,168.75 | 1280×720 |

The first preview's attempted Escape interception was unreliable and was not promoted. Its
same-origin PCK also returned an initial transient 404 immediately after deployment;
full recheck passed. A second timing guard also failed to consistently isolate
that gesture. The final version removes both attempts and preserves native key
handling, with explicit fullscreen control only on the button. Historical failed
tests remain evidence, not passes. Browser and production results follow below.

## Production result

Live at [hush-basin.cmish.dev](https://hush-basin.cmish.dev/), deployed from
`263fd4e760772e2cb55d427b174a20fb508dd2f5` to
`https://2a16c942.hush-basin.pages.dev`. Final preview:
`https://4f73c07e.hush-basin.pages.dev`.

Shell SHA-256/ID:
`3e7bf4a9dca342df0487b66b530f7ba8efe978b0b04efccdbe9133ad18dbc99d`.
The single added HTML page is 8,269 bytes. Its immutable URL is
`/shells/3e7bf4a9dca342df0487b66b530f7ba8efe978b0b04efccdbe9133ad18dbc99d/`.
Open the site root for the new presentation; previously bookmarked `/builds/`
URLs intentionally retain the original immutable generated shell.

All ten full-file hash comparisons passed on the final preview, production
deployment, and custom domain: nine original files plus the presentation HTML.
The first immediate PCK requests on preview v3 and production returned 404;
independent full rechecks passed, preserving the failed attempt logs. No R2
objects were uploaded or modified in this pass: existing bytes were retrieved
and verified, and only small Pages files were deployed.

| Production artifact | Bytes | SHA-256 |
|---|---:|---|
| WASM | 39,513,091 | `35116f68540ac41acf7d71ea457added91b5e960a9cca3e2acc72918eaf01277` |
| PCK | 101,717,356 | `7b1859a86a22af0f40a32f27745e9416b47c5538929502cff215a04b79b091f6` |

The shell, WASM, and PCK all retained the explicit immutable/no-transform cache
policy. Correct MIME and Content-Length were present. Both large responses
reported X-Hush-Cache HIT, Age 4543, and outer CF-Cache-Status DYNAMIC in the
custom-domain sample. No CDN speed claim is made.

Chromium reached the exact Godot 4.7.1 WebGL 2 Compatibility runtime and
`P1A_RUNTIME_READY authority=world-polish-v1 routes=17 solids=19`. Full Quarto,
city/weather/minimap and HUD composition are visible. Final fullscreen button
entry/exit left the game live and returned focus to canvas; R then produced the
countdown. Reload through the custom domain reached the same build and runtime.
Production resize to 1000×900 produced the same centered 1000×562.5 display and
1280×720 backing buffer. No console errors were observed. Audio files and startup
code are unchanged; no independent audible listening test is claimed.

Safari is installed and was selected for native macOS testing. Three control/read
attempts were blocked by its automation guard reporting ongoing user interaction;
no Safari result or screenshot is claimed. The owner was asked to leave Safari
idle for that check, with no response received during this pass. Chromium checks
and the production correction are complete; native Safari verification remains
an explicit limitation. No browser preference or security setting was changed.

The four deployment-barrier tests pass. `game/` has an empty diff against the
baseline and all 311 accepted export source hashes match. The legacy repository
verifier remains FAIL (389 checks): the existing production `.gitignore` update
and two historical Quarto visual files differ from its older frozen inventory.
No fixture or historical failure was rewritten to obtain a pass.

Exact source files changed in this successor:

- `hosting/production/shell.css`: aspect-preserving fitting and small button style.
- `hosting/production/shell.js`: gesture-driven fullscreen and canvas focus.
- `tools/web_shell.py`: reproducible, separately hashed HTML derivative.
- `tools/deploy_web.py`: stage/retain/verify the shell and choose the root entry.
- `AGENTS.md`: current bounded authority.
- `docs/WEB_SHELL_PRESENTATION_V1.md`: this decision and verification record.
