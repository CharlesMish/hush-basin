# Cloudflare hosting proof v1

Disposition: `SAME_ORIGIN_R2_HOSTING_PROVED`.
Real same-origin R2 delivery, exact artifact identities, cache behavior,
browser startup, reload and retry are verified. The owner confirmed sustained
keyboard holds work normally, closing the last input verification gap. This
completes the bounded hosting proof; it is not a release or production launch.
This successor starts at `5971b494f1dbb3e15aa4e6ac57ac1af2ba80acd8`
(`feature/web-feasibility-v1`). It changes hosting only. The owner authorized a
temporary preview, with no production domain, release, unrelated account
changes, game modifications, package reduction, or alternate-origin shell.

## Exact build

Reuse the accepted `Hush-Basin-Web-Evidence-20260913/final-build/web` export.
Its exporter recorded source commit
`df221870b45de53e4ebb5ea8889b6cf1114054c6`, before the export-tooling successor
was committed. All 311 source hashes in that export manifest, including the Web
preset, still match the accepted successor. No new export or diagnostic entry
is substituted. Godot is `4.7.1.stable.official.a13da4feb`; matching template
SHA-256 is `b7b7d7da29fc6cc2f4934fdd26cc571a40e7af57f716ea3eb7e18da720dae28a`.

The committed `hosting/cloudflare/build-manifest.json` contains all nine
artifact sizes/hashes. Build identity is SHA-256 of its `files` array serialized
as UTF-8 JSON with sorted keys and compact separators:
`3ac4997d783741ccd07ff74298302c622fe62300484ef2f55bf3a2153e42b0c0`.

| File | Bytes | SHA-256 |
| --- | ---: | --- |
| index.wasm | 39,513,091 | `35116f68540ac41acf7d71ea457added91b5e960a9cca3e2acc72918eaf01277` |
| index.pck | 101,717,356 | `7b1859a86a22af0f40a32f27745e9416b47c5538929502cff215a04b79b091f6` |

Complete original export: 141,565,089 bytes. Both large artifacts exceed the
Pages 25 MiB static asset limit. The seven original small assets total 334,642
bytes; they remain unchanged. Staging adds a small manifest and Pages routing,
header, redirect and 404 files. Generated site assets and caches are ignored.
Total staged directory, including Pages control files: 336,988 bytes. Largest
static asset: `index.js`, 279,815 bytes.

## Architecture and cache contract

Small assets live at `/builds/<build-id>/` on Pages. The ordinary generated
loader asks for adjacent `index.wasm` and `index.pck`. `_routes.json` invokes
the Pages Function only for those filenames. The Function accepts only the
recorded build and retrieves `builds/<build-id>/<filename>` through the private
`HUSH_ARTIFACTS` R2 binding. There is no public R2 bucket, CORS configuration,
custom Godot shell, service worker, cross-origin isolation or game fork.

R2 bodies flow directly into Responses as streams. No `.arrayBuffer()`, text
conversion or pack buffering is used. R2's known size becomes Content-Length;
WASM uses `application/wasm`, PCK `application/octet-stream`. `no-transform`
deliberately preserves raw identity and lengths for this proof. Compression
and CDN performance tuning are outside this pass.

Versioned assets use `public, max-age=31536000, immutable, no-transform`.
Never overwrite these R2 keys with different bytes. A different export needs
a different manifest/build ID and URL. `X-Hush-SHA256` and the SHA-derived ETag
declare the manifest identity; independent full HTTP downloads verify that
declaration. Object size mismatches fail closed with 502. Upload integrity is
established by those downloads, not by pretending R2's ETag is SHA-256.

`caches.default` caches complete GET responses with `waitUntil`. A HIT avoids
an R2 read but still invokes the Function. `X-Hush-Cache` reports the actual
cache lookup result; `X-Hush-Cached-At` records the initial response timestamp.
Cloudflare's CF-Cache-Status/Age are recorded separately, without fabricating
them. Queries use the same canonical cache key. Cache contents are local to
the serving data center; this is not a global cache or CDN benchmark.

The deliberately minimal route ignores Range and returns full 200 bodies with
`Accept-Ranges: none`. HEAD returns metadata only. Godot uses full-file GETs.
Partial downloads/resume support are not claimed. Unknown builds return 404;
unsupported methods return 405. No request can select an arbitrary R2 key.

## Reproduction

From the repository root, with Node >=22 and Python 3 available:

```sh
npm --prefix hosting/cloudflare ci
python3 tools/stage_cloudflare_proof.py /absolute/path/to/final-build/web
cd hosting/cloudflare
npx wrangler login --scopes account:read user:read workers:write pages:write
```

Staging intentionally refuses an existing `site` directory. Archive/remove only
that generated directory before rerunning. Wrangler is pinned to 4.131.1 with
its lockfile (MIT OR Apache-2.0); this is a development dependency only.

For this proof, new resource names are both `hush-basin-r2-proof-20260914`.
Check they do not already contain unrelated work before creation. R2 must be
enabled on the account; its subscription enrollment is an owner action.

```sh
npx wrangler r2 bucket create hush-basin-r2-proof-20260914
npx wrangler pages project create hush-basin-r2-proof-20260914 --production-branch reserved-production --compatibility-date 2026-09-14
```

Upload the two exact files, replacing only the local export directory:

```sh
HUSH_BUILD=3ac4997d783741ccd07ff74298302c622fe62300484ef2f55bf3a2153e42b0c0
HUSH_EXPORT=/absolute/path/to/final-build/web
npx wrangler r2 object put "hush-basin-r2-proof-20260914/builds/$HUSH_BUILD/index.wasm" --remote --file "$HUSH_EXPORT/index.wasm" --content-type application/wasm --cache-control 'public, max-age=31536000, immutable, no-transform'
npx wrangler r2 object put "hush-basin-r2-proof-20260914/builds/$HUSH_BUILD/index.pck" --remote --file "$HUSH_EXPORT/index.pck" --content-type application/octet-stream --cache-control 'public, max-age=31536000, immutable, no-transform'
npm run deploy:preview
```

Use the unique deployment URL returned by Wrangler. `hosting-proof` differs
from reserved-production, so it is a preview deployment. No domain is attached.
The root redirects to the version directory. Preview pages carry noindex
headers, but the URL is publicly reachable; this is not authentication.

From the repository root, download two complete loads plus a Range probe and
preserve exact response headers and bodies outside product source:

```sh
python3 tools/verify_cloudflare_http.py https://DEPLOYMENT.pages.dev --output /absolute/new/evidence/edge-http
```

For local integration, replace `--remote` on the two object uploads with
`--local`, then run `npm run dev -- --port 8071`. This uses only the local R2
emulator. The same HTTP verifier accepts `http://localhost:8071`. Local results
are not edge evidence.

On this machine the system Homebrew Node is broken (missing simdjson dylib).
The working Node is
`<LOCAL_NODE_EXECUTABLE>`.
Prepend its containing directory to PATH; npm's CLI is available at
`/opt/homebrew/lib/node_modules/npm/bin/npm-cli.js`. Wrangler can also be invoked
with that Node and `hosting/cloudflare/node_modules/wrangler/bin/wrangler.js`.
No system Node or Godot installation was changed.

## Deployed resources

Account: `REDACTED_ACCOUNT_ID`.

- Pages project: `hush-basin-r2-proof-20260914`.
- R2 bucket: `hush-basin-r2-proof-20260914`, Standard, WNAM, created
  `2026-09-14T02:53:25.331Z`. Public access through r2.dev is disabled.
- Deployment: `27ea1fea-f95f-4551-8670-01333118a991`, **Preview** environment,
  branch `hosting-proof`. Reserved production branch: `reserved-production`.
- Deployed source: `74b7f5adc16d4d75ad436ebdae7dbd18d7f67152`.
  Hosting implementation first committed as
  `82d4575a1686f51497d5116f48b7662b6ac734f4`; only evidence docs differ between them.
- Unique test URL: <https://27ea1fea.hush-basin-r2-proof-20260914.pages.dev/>.
  Alias: <https://hosting-proof.hush-basin-r2-proof-20260914.pages.dev/>.
- Exact immutable R2 keys:
  `builds/3ac4997d783741ccd07ff74298302c622fe62300484ef2f55bf3a2153e42b0c0/index.wasm`
  and
  `builds/3ac4997d783741ccd07ff74298302c622fe62300484ef2f55bf3a2153e42b0c0/index.pck`.

Only these two objects were uploaded. No production deployment, custom domain,
Git integration, public R2 URL or unrelated Cloudflare property was changed.
The owner enabled R2 after the initial API code 10042 prerequisite was reported;
that earlier blocked attempt remains recorded in Git history.

## Real HTTP and cache evidence

All nine original files matched their exported SHA-256 and byte counts across
two HTTP loads. Both large files also matched on full-body Range probes. These
are real HTTPS requests to the unique deployment URL, not the local emulator.
The browser loaded before the HTTP verifier, warming the serving cache.

| Artifact/request | Status | Content-Type | Content-Length | CF-Cache-Status | Age | X-Hush-Cache |
| --- | ---: | --- | ---: | --- | ---: | --- |
| WASM, first HTTP verification load | 200 | application/wasm | 39513091 | HIT | 111 | HIT |
| WASM, second HTTP verification load | 200 | application/wasm | 39513091 | HIT | 120 | HIT |
| PCK, first HTTP verification load | 200 | application/octet-stream | 101717356 | HIT | 91 | HIT |
| PCK, second HTTP verification load | 200 | application/octet-stream | 101717356 | HIT | 98 | HIT |

All four responses had no Content-Encoding and
`Cache-Control: public, max-age=31536000, immutable, no-transform`.
CF-Ray identified DFW. Initial cache timestamps retained across these reads:
PCK `2026-09-14T02:56:24.134Z`, WASM `2026-09-14T02:56:24.441Z`.
This establishes real edge cache hits, not a guarantee of retention or hits
from other locations. The initial browser MISS headers were not captured.

The same cache policy and exact lengths were present for small static assets;
HTML was `text/html; charset=utf-8`, JS/worklets `application/javascript`, icons
`image/png`. Their responses did not expose CF-Cache-Status or Age, so no static
cache-hit claim is made from those headers. Pages canonicalizes `index.html`
to the directory URL; the final HTML bytes still match exactly.

Range `bytes=0-15` was deliberately ignored: both files returned 200, complete
bodies, correct hashes and `Accept-Ranges: none`. Metadata-only HEAD returned
200 with the full file length and zero body bytes. POST returned 405 and an
unknown build returned 404, through the real edge as well as locally.

The first Python request with urllib's default user agent returned 403,
Cloudflare error 1010. The browser and curl succeeded. Identifying the helper
as `Hush-Basin-Hosting-Proof/1.0` returned 200, and the entire verification then
passed. The helper now sends that explicit identifier. No Cloudflare security
setting was disabled or changed.

Observed full-download durations (one client/network, already cached): PCK
3.613 s then 5.377 s; WASM 1.860 s then 1.288 s. These variable single-location
samples do not establish CDN performance. Raw bodies are intentionally served
without compression for this identity proof; package reduction was not attempted.

Full request/response headers, downloaded bodies and hashes are in the sibling
`Hush-Basin-Cloudflare-Evidence-20260914/edge-http-identified-client/` directory.

## Browser evidence

The ordinary generated page loaded in the Codex in-app browser. Console:

```text
Godot Engine v4.7.1.stable.official.a13da4feb
OpenGL API OpenGL ES 3.0 (WebGL 2.0 (OpenGL ES 3.0 Chromium)) - Compatibility - Using Device: WebKit - WebKit WebGL
Build configuration: Emscripten 4.0.20, single-threaded, no GDExtension support.
P1A_RUNTIME_READY authority=world-polish-v1 routes=17 solids=19
```

The Quarto craft, city, cloud cover, drizzle, minimap, Run countdown and elapsed
timer, BRRR and streak HUD rendered. Escape paused the simulation and displayed
the pause overlay. Reload restarted the exact runtime and reached ready again
with the world and active HUD. No startup/runtime errors were captured on either
load. The preserved canvas renders in the top-left part of this browser's
viewport; this proof makes no new layout or art-parity changes.

Browser console and reload capture are in
`Hush-Basin-Cloudflare-Evidence-20260914/browser/`. Browser automation supplies
key taps, not sustained holds. After the W/Shift/release/R check request, the
owner reported: “I have confirmed that all the holds are working normally”.
That is owner-observed confirmation of W and Shift Drive/Spread behavior,
separate from the automated checks. The agent then independently tapped R and
observed the craft at spawn in Spread, zero speed, and the new countdown at 3,
confirming retry. No player-driven finish, gamepad, Safari, broad performance
or owner-feel acceptance is claimed by this proof.

## Local and preservation verification

- Hosting implementation commit: `82d4575a1686f51497d5116f48b7662b6ac734f4`.
- Wrangler authentication succeeded after restarting an expired local OAuth
  callback. The account is `REDACTED_ACCOUNT_ID`.
- All nine staged original artifact hashes and sizes match; no large artifact
  is included in Pages static assets.
- Local Wrangler Pages/Miniflare compiled the Function and bound local R2.
  All 20 full HTTP bodies (first, second, two Range probes) match the manifest.
  Both large files returned correct MIME and Content-Length, no Content-Encoding.
  Local first GETs were MISS; second GETs were HIT with emulator CF-Cache-Status
  HIT and Age 0. This is explicitly emulator behavior, not Cloudflare edge proof.
  Two HEAD checks returned correct metadata and zero body bytes; POST returned
  405 and an unknown build returned 404. Evidence is in the sibling
  `Hush-Basin-Cloudflare-Evidence-20260914/local-http/` directory.
- `python3 tools/verify_web_lane.py`: PASS, all 310 native checkpoint files
  unchanged. All 311 recorded export source hashes also match.
- `python3 tools/verify_quarto_vehicle.py --evidence ../Hush-Basin-Cloudflare-Evidence-20260914/static`:
  449 checks PASS. No native runtime rerun for a hosting-only change.
- Required historical `python3 tools/verify_repo.py`: 389 checks, FAIL for
  `game/scenes/vehicle_visual.tscn` and `game/scripts/vehicle_visual_rig.gd`,
  the two already documented Quarto differences. History remains unchanged;
  the earlier native Quarry Depot traverse failure also remains a failure.

## Cost assumptions

This proof uses R2 Standard, about 0.142 GB of large-object storage, two initial
PUTs, and GETs/HEADs on cache misses. Standard includes 10 GB-month, 1 million
Class A operations and 10 million Class B operations monthly. Beyond included
usage: $0.015/GB-month, $4.50/million A, $0.36/million B (billing-unit rounding
applies). R2 egress is free. Account-wide usage determines actual charges.
R2 enrollment is a renewing usage-billed subscription even when amount due now
is $0. Pages Functions consume Workers requests; static asset requests do not.
Cache hits still execute this Function. Workers Free, if used, has a shared
100,000 request/day allowance; existing account usage counts against it. No
Workers plan upgrade was made or required in this proof. Account-wide billing
was not audited. No CDN speed or operational production readiness is claimed.

Primary references checked September 14, 2026:
[Pages R2 bindings](https://developers.cloudflare.com/pages/functions/bindings/#r2-buckets),
[Pages Wrangler configuration](https://developers.cloudflare.com/pages/functions/wrangler-configuration/),
[R2 streaming API](https://developers.cloudflare.com/r2/api/workers/workers-api-reference/),
[Cache API](https://developers.cloudflare.com/workers/runtime-apis/cache/),
[Pages limits](https://developers.cloudflare.com/pages/platform/limits/),
[R2 pricing](https://developers.cloudflare.com/r2/pricing/),
[Pages Functions pricing](https://developers.cloudflare.com/pages/functions/pricing/).

## Cleanup (only these proof resources)

After reviewing the proof, from `hosting/cloudflare`:

```sh
npx wrangler pages project delete hush-basin-r2-proof-20260914
HUSH_BUILD=3ac4997d783741ccd07ff74298302c622fe62300484ef2f55bf3a2153e42b0c0
npx wrangler r2 object delete "hush-basin-r2-proof-20260914/builds/$HUSH_BUILD/index.wasm" --remote
npx wrangler r2 object delete "hush-basin-r2-proof-20260914/builds/$HUSH_BUILD/index.pck" --remote
npx wrangler r2 bucket delete hush-basin-r2-proof-20260914
```

Do not remove the account's R2 subscription if other work subsequently uses it.
If it was enabled only for this proof, the owner can cancel through Cloudflare
Billing Subscriptions after resource cleanup. `npx wrangler logout` removes the
local Wrangler login when desired. Generated `site/`, local `.wrangler/`, and
`node_modules/` are disposable; external evidence should be retained for audit.
