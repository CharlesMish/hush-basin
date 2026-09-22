# Production Web promotion v1

The owner accepted the same-origin R2 proof and personally confirmed sustained
keyboard holds in that exact exported build. This successor promotes those bytes;
native Forward+ remains authoritative and Web remains a provisional play/regression
target. No game source, renderer, loader, or content has changed.

## Routine deployment

Prerequisites: Python 3.11+, an installed Node 22+ executable, authenticated
Wrangler with this account's Pages/R2 access, and `npm --prefix hosting/cloudflare ci`.
Wrangler is pinned in that directory's lockfile. Set `HUSH_NODE` if the default
Node is unsuitable. Fresh exports require the exact already-installed Godot
`4.7.1.stable.official.a13da4feb` and matching template; the helper does not install
or substitute them. Run from the repository root, using a new work directory.

On the current Mac the working bundled executable is:
`<LOCAL_NODE_EXECUTABLE>`.
Set `HUSH_NODE` to that path for the helper; the system Homebrew Node currently
fails to start because of a missing library. No system runtime was repaired or
upgraded in this task.

```sh
python3 tools/deploy_web.py preview --work /absolute/new/web-candidate
# Open the printed unique preview URL and smoke-test the game.
python3 tools/deploy_web.py promote --work /absolute/new/web-candidate --confirm-playable
```

The first command exports current game source, computes the immutable identity,
checks all source and artifact hashes, checks existing R2 objects before any PUT,
retains previous builds' small files, deploys a preview, and hashes its served
files. To reuse an already verified export, add `--export /absolute/export-output`
(the directory containing `build.json` and `web/`). Only the first-ever production
candidate uses `--bootstrap`. Production is an explicit second operation. There
is no Git-triggered publishing. `--confirm-playable` is an operator assertion to
use only after playing the exact preview.

Promotion refuses missing HTTP evidence, a changed stage, or production that
changed after staging. Fresh edge HTTP 5xx responses receive at most two retries
five seconds apart; successful evidence retains earlier failed attempts. Other
HTTP errors stop immediately. A deployment can exist even if its immediate HTTP
check fails. Inspect the recorded URL and error; do not blindly redeploy or edit
a receipt to bypass checks. Independently recheck a deployed origin with:

```sh
python3 tools/deploy_web.py verify --work /absolute/web-candidate --origin https://hush-basin.cmish.dev --label domain-check-1
```

Use a new label for each check. This command verifies bytes without deploying or
rewriting earlier evidence. Run this single-operator workflow serially;
there is no distributed promotion lock. Keep the work directory as deployment
evidence until the deployment is accepted.

## Architecture and rollback

`hush-basin` is a direct-upload Pages project with production branch `production`.
`hush-basin-artifacts` is a private Standard R2 bucket bound as `HUSH_ARTIFACTS`.
The seven original small files are unchanged. The two large files live at
`builds/BUILD_ID/index.wasm` and `builds/BUILD_ID/index.pck`; the same paths on
Pages are Function routes. The Function returns R2 ReadableStreams, never whole
buffers. The ordinary generated Godot loader resolves both files beside itself.

The root redirects (302) to the current `/builds/BUILD_ID/`. `/production.json`
is a no-store machine-readable current-build pointer and retained build registry.
All build files use `public, max-age=31536000, immutable, no-transform`. Large
responses also include exact length, SHA-256 ETag, MIME, build ID, and a cache
observation header. GET and HEAD are supported. Range is deliberately ignored
and returns the full 200 body with `Accept-Ranges: none`, as in the proof.
No public bucket endpoint or alternate-origin shell is required.

To roll back after another build exists:

```sh
python3 tools/deploy_web.py preview --rollback-build PRIOR_BUILD_ID --work /absolute/new/rollback-candidate
# Smoke-test the printed preview, then:
python3 tools/deploy_web.py promote --work /absolute/new/rollback-candidate --confirm-playable
```

This changes the root pointer while retaining newer and older versioned URLs.
Do not use an old Pages deployment rollback as the routine procedure: its old
registry can omit newer immutable URLs. Never overwrite R2 keys with different
bytes. Existing keys are downloaded and verified; a mismatch aborts. Only an
explicit R2 missing-key response allows upload. No automatic garbage collection
is performed, so retained builds consume storage and small-file deployment count.

## Service assumptions

Pages Functions use Workers request quotas and the Cache API is local to a
Cloudflare data center. A warm local sample does not prove global CDN performance.
R2 Standard storage and operations are metered, with account-wide free allowances;
R2 egress is free. No paid Workers upgrade or account subscription change is part
of this promotion. Budget/usage depends on aggregate account traffic and retained
build count. See [Pages Functions pricing](https://developers.cloudflare.com/pages/functions/pricing/),
[R2 pricing](https://developers.cloudflare.com/r2/pricing/), and
[Cache API behavior](https://developers.cloudflare.com/workers/runtime-apis/cache/).

Cloudflare's [Pages custom-domain workflow](https://developers.cloudflare.com/pages/configuration/custom-domains/)
registers the domain with Pages before creating its CNAME. Only
`hush-basin.cmish.dev` is authorized here.

## Verification record

Starting hosting-proof commit: `c33ff6e0624c3a281df28795caad6a3ac1f47727`.
Branch: `feature/production-web-promotion-v1`. Deployed infrastructure commit:
`7176214901fc383edf38826c0114f9b56c00b141`. The subsequent helper-only recovery
command and evidence documentation do not change the deployed Function or game.

Export source: `df221870b45de53e4ebb5ea8889b6cf1114054c6`, with accepted Web
tooling successor `5971b494f1dbb3e15aa4e6ac57ac1af2ba80acd8`. All 311 export
source hashes match. The exact accepted export was reused, with no fresh export.

Build ID: `3ac4997d783741ccd07ff74298302c622fe62300484ef2f55bf3a2153e42b0c0`.

| Artifact | Bytes | SHA-256 |
|---|---:|---|
| index.wasm | 39,513,091 | `35116f68540ac41acf7d71ea457added91b5e960a9cca3e2acc72918eaf01277` |
| index.pck | 101,717,356 | `7b1859a86a22af0f40a32f27745e9416b47c5538929502cff215a04b79b091f6` |

Both R2 keys use `builds/BUILD_ID/` followed by the filename above. The complete
nine-file export is 141,565,089 bytes; seven small original files total 334,642
bytes. No generated game artifacts or caches are committed to source.

Verified preview: `https://68bae21b.hush-basin.pages.dev`.
Production deployment: `https://0f1d6589.hush-basin.pages.dev`.
Production origin: `https://hush-basin.cmish.dev/`.
R2: Standard, WNAM, public r2.dev disabled. The new bucket's inventory metrics
initially reported zero despite successful full object GETs; these delayed
metrics are not used as artifact-presence evidence.

HTTP verification independently passed all nine full bodies on the final preview,
the unique production deployment, and the stable Pages origin. Through the custom
domain, 20 full-body comparisons passed (all nine twice, then both large files
with Range). The release manifest also matched exactly through the custom domain.
TLS 1.3 validated normally against the trusted certificate for `cmish.dev` and
`*.cmish.dev`. Root returned 302 to the same accepted immutable build path.

| Custom-domain observation (DFW) | PCK | WASM |
|---|---|---|
| Status | 200 | 200 |
| Content-Type | application/octet-stream | application/wasm |
| Content-Length | 101717356 | 39513091 |
| Content-Encoding | absent | absent |
| First cache observation | X-Hush-Cache MISS, no Age | X-Hush-Cache MISS, no Age |
| Second cache observation | X-Hush-Cache HIT, Age 5 | X-Hush-Cache HIT, Age 14 |
| CF-Cache-Status | DYNAMIC | DYNAMIC |
| Range bytes=0-15 | full 200, Age 20 | full 200, Age 24 |

Large responses carried the exact immutable policy above. On this custom domain,
the outer CF-Cache-Status remained DYNAMIC while the Function's Cache API showed
HIT and increasing Age. Do not mislabel that outer header as HIT. The second PCK
sample took longer than the first; these are correctness/cache observations, not
evidence of a CDN speed improvement or global performance.

Initial failures retained: empty project 522 before bootstrap, one first-preview
small-file 522, and a first production PCK 404 immediately after deployment.
Subsequent full verification passed without changing the production route or
game bytes. The initial promotion invocation therefore failed its HTTP check;
the later independent unique-origin and stable-origin checks establish success.

Full raw evidence is in sibling `Hush-Basin-Production-Evidence-20260914/`.
The compact final record is `PRODUCTION_WEB_V1_RESULT.json`.

The custom-domain browser reported the exact engine and Compatibility renderer,
single-threaded Emscripten configuration, and `P1A_RUNTIME_READY` with 17 routes
and 19 solids. Captures show Quarto, city, drizzle, minimap, running time and BRRR
HUD. R produced the retry countdown, Escape paused, and an actual reload reached
the same runtime/build again without observed console errors. The original
640×360 game canvas inside the 1280×720 browser capture remains unchanged.

Current disposition: `AWAITING_PRODUCTION_CONTROLS_CONFIRMATION`. The owner has
already accepted sustained holds on the identical proof artifact. A final W/A/D,
held Shift Drive/release to Spread, and R confirmation through the new custom
domain was requested; it has not yet been received. Browser automation here only
sends short key presses. Do not label this outstanding owner observation passed.
Proof resources remain intact pending that last check. No account-level R2
subscription or unrelated resource was altered.

After that check passes, the only disposable resources eligible for cleanup are
Pages project and R2 bucket `hush-basin-r2-proof-20260914`, with these two keys:
`builds/3ac4997d783741ccd07ff74298302c622fe62300484ef2f55bf3a2153e42b0c0/index.wasm`
and the same prefix with `index.pck`. Use the pinned Wrangler to delete those
specific objects and then the bucket/project. Never empty unknown objects to
force bucket deletion. Retain all proof documents and evidence.

The helper's four promotion barrier tests pass. The current Quarto source verifier
reports 449 checks with two wrapper failures (`PRESERVED:.gitignore` and
`PRESERVED_WRAPPER_SUFFIX:README.md`) caused by the authorized production ignore
and README edits. Its game checks did not fail; the full game diff is empty and
all 311 accepted export source hashes match. The fixture was not rewritten.

Historical native failures remain failures: the legacy repository verifier has
two known Quarto inventory mismatches and the native Quarry–Depot traverse is not
repaired by hosting. Prior feasibility art, gamepad, browser sizing, and performance
limitations remain. No mobile or global performance claim is made.
