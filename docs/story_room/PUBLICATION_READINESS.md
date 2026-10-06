# Current game: review and publication preparation

Prepared October 6, 2026. This document prepares owner review; it is **not
production approval**. No new story or playable-source change was made here.

## Candidate and authority

- Implemented game: `experiment/narrative-chapters-2-3-v0-1` at
  `5be7feeef34dbed468e007f5ff4de594d41b0f80`.
- Story-room preparation branch: `tooling/story-room-v0-1`, initially the same
  HEAD. Later documentation commits do not change the exported game's identity.
- Chapter 2 checkpoint: `31677586809b56ba9993802b33ca3eb1fa6d6828`.
- The contiguous opening, accepted Tess-stop/origin UX corrections, Chapter 2,
  and both interleavable Chapter 3 threads are implemented. Human pacing,
  attachment, recognition, comfort and desire gates remain owner judgments.

Play the isolated [Web review candidate](https://03ea1e54.hush-basin.pages.dev).
Native Forward+ remains the presentation authority. On Charlie's Mac, the
sibling `Hush-Basin-Story-Room-20261006/PLAY_HUSH_BASIN.command` opens the existing
clean extracted owner package. All 593 game-source files in that package match
the new export's input inventory exactly. It remains independent of these
writing-agent documents.

At a desk: **Dispatch → Reset Story** starts all three chapters afresh. Browser
and native saves are separate; prior review saves are preserved. Controls are
in `START_STORY.md` and the adjacent package's `START_HERE.txt`.

The full end-to-end owner duration is **unmeasured**. Reserve about an hour,
longer for exploration; this is a scheduling allowance, not measured content
length. The earlier 20–30-minute target covered the opening, not all chapters.
Useful review checks are postponing work, quitting with cargo aboard, and
returning after consequences have occurred. No emotional-beat walkthrough is
needed before play.

## Immutable export and architecture

The preview contains the new **playable, non-diagnostic**, single-thread release
export. Native project settings remain Forward+; Web remains Compatibility.
There is no threaded-Web, loader, DNS, topology, gameplay or hosting redesign.

| Identity | Value |
| --- | --- |
| Source commit | `5be7feeef34dbed468e007f5ff4de594d41b0f80` |
| Engine | `4.7.1.stable.official.a13da4feb` |
| Build ID | `88d354faf1df2212cc018d257310cf7c9795655dc2095525e8cec1143c4551d3` |
| Shell ID | `d3b640651472e8f77c18f0320adb74a9bafb9335168299ebf45d0111f51eabe7` |
| WASM | 39,513,091 bytes; `35116f68540ac41acf7d71ea457added91b5e960a9cca3e2acc72918eaf01277` |
| PCK | 104,981,556 bytes; `34bf08934e7ad4a86a42c871e303376a9c323ab4735679d76e7fa4ca0f40d023` |
| Nine exported files | 144,829,292 bytes; estimated gzip 26,421,419 bytes |
| Export input inventory SHA-256 | `38a0b52f7a93da3a30c023c0dced58bf4cf4231bbf117670eaf16c794d7a27c7` |

The installed pinned template SHA is
`b7b7d7da29fc6cc2f4934fdd26cc571a40e7af57f716ea3eb7e18da720dae28a`.
The WASM matches it exactly. The inventory digest above hashes canonical JSON
of the 593 filename→SHA-256 entries. `build.json` retains every individual hash.
PCK byte identity across repeated exports is not assumed.

The existing direct-upload Pages project `hush-basin` uses production branch
`production`. This preview uses `candidate-88d354faf1df2212`, a separate
deployment. Its small assets remain on Pages; its WASM/PCK are new immutable keys
under `builds/BUILD_ID/` in private `hush-basin-artifacts`. R2's public development
URL was independently confirmed disabled. The existing same-origin Function
streams the two bodies and retains exact MIME, length and immutable cache policy.

The helper first confirmed that each new key was absent, then uploaded it. No
existing key was overwritten. Both old and new build registries/shells are
retained. Twenty HTTP artifact checks passed: new full bodies, retained small
files/shells, and identity HEAD checks for the old large files.

Production before and after staging was independently read through both
`hush-basin.cmish.dev` and `hush-basin.pages.dev`: the manifests are unchanged.
They still point to historical source `df221870b45de53e4ebb5ea8889b6cf1114054c6`,
build `3ac4997d783741ccd07ff74298302c622fe62300484ef2f55bf3a2153e42b0c0`.
No production promotion occurred.

## Fresh verification

Evidence is outside Git in sibling `Hush-Basin-Story-Room-20261006/evidence/`.
The October 1 implementation results remain historical evidence in
`NARRATIVE_SLICES_REVIEW.md`; the October 6 results below are new runs.

| Fresh check | Observed result |
| --- | --- |
| Retained regressions | 882 checks / 36 logical runs PASS: 769 headless, 97 native opening, 16 native input edges |
| Exact movement trace | 1,260 ticks; original native SHA-256 exact |
| Fresh contiguous opening → 2 → 3 | 275 checks PASS headless; synthetic travel for state/UI coverage |
| Native Forward+ Chapter 2 / Chapter 3 | 56 / 139 checks PASS |
| B11 actual-input approaches | 19 checks PASS from Market, Clinic and Depot |
| Ren-first / sleeve-first | 140 checks each PASS |
| Successor quit/relaunch | 124 checks / 16 independent processes PASS |
| Existing project persistence | 56 checks / 9 processes PASS |
| Atomic store and dependency guards | 45 checks PASS |
| Authored text | 46 exact passages; two previously authorized conditional omissions |
| Scope preservation | 827/835 original files exact; eight existing authorized seams; zero new game changes in this task |
| Browser contiguous / close-reopen | 275 checks PASS; held sleeve and both-complete saves each pass 8 checks after closing/reopening Chromium |
| Playable preview startup and input | PASS: fresh Market start, brief throttle and pause in exact staged build; no captured console errors/warnings across all four browser runs |
| Promotion barriers | 4 tests PASS |
| Preview HTTP identity | 20 artifact checks PASS; both live production manifests unchanged |
| Existing clean native package | ZIP SHA/CRC PASS; all 593 game-source files match fresh export inputs |
| Historical R7 repository inventory (`verify_repo.py`) | FAIL: 11 byte-inventory mismatches / 389 checks; every affected file is exact to starting `5be7fee`, so none was introduced by this task |

The exact native movement SHA is
`29f1049f8e16ec65d288407c35e6ccae46e87c711bb6b54b134e6158c68b9443`.
There is no new controlled performance benchmark. The new full export is
3,264,203 raw bytes (2.31%) larger than the historical production export; this
reflects the already-implemented narrative game, not new content in this task.

Initial environment/tool invocations remain in evidence: the first sandboxed
export could not save Godot editor settings; two native display processes
aborted at startup under the sandbox. The export passed with normal engine
access, and only the two display cases were rerun. A separate manual atomic-store
invocation used a relative log path which Godot resolved under `user://` and
crashed before the test. The corrected absolute-path invocation passed all 45
checks. No game change or assertion relaxation was made for these rechecks.
The legacy R7 inventory is retained as a failure, not relabelled as a current
narrative test. Its full mismatch list and the independent starting-HEAD byte
comparison are in `historical-verify-repo.txt` and
`historical-verify-repo-classification.json` in this pass's evidence.

The preview's normal 1280×720 browser capture visibly starts at Market with the
anonymous Relay-mail lead. The post-input capture shows the craft moved and
paused. These are startup/input observations, not a browser-driven whole-game
playtest. The inherited boxed minimap north-arrow glyph is still visible in Web;
no unrelated UI repair was added. Browser results and captures are in
`browser-fresh/`, with the exact automation in `browser-regression.cjs`.

## Promotion after owner approval

Play the exact preview first. Only after Charlie approves its playability, run
the following from this repository on the current Mac:

```sh
HUSH_NODE=/Users/cmish/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node \
python3 tools/deploy_web.py promote \
  --work ../Hush-Basin-Story-Room-20261006/preview \
  --confirm-playable
```

**This command has not been executed.** The flag is a real operator assertion,
not something an automated critic or test may supply. The helper rejects changed
candidate files, missing preview HTTP evidence, or production that has changed
since staging. If production changes, prepare a new candidate retaining its
current registry; do not bypass that barrier.

After promotion, independently verify the custom domain with a new evidence
label:

```sh
HUSH_NODE=/Users/cmish/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node \
python3 tools/deploy_web.py verify \
  --work ../Hush-Basin-Story-Room-20261006/preview \
  --origin https://hush-basin.cmish.dev --label owner-approved-domain
```

For provenance, the already-executed staging command was `tools/deploy_web.py
preview --work ../Hush-Basin-Story-Room-20261006/preview --export
../Hush-Basin-Story-Room-20261006/evidence/web-playable-final`, with the same
`HUSH_NODE`. Do not run it again against the occupied work directory. The exact
artifact, release registry and promotion inventory are preserved there.

No packages were installed. The current Mac's Homebrew Node fails because an
existing dynamic library is missing. The working bundled Node above and the
already-installed Wrangler 4.131.1 from the earlier feasibility checkout were
used. A local ignored `hosting/cloudflare/node_modules/wrangler` symlink makes
that same package available to the existing helper; both lockfiles are exact.
This local prerequisite is documented rather than altering the hosting helper.

## Limits

There is no new owner approval in these automated results. Portraits and fine
props remain prototypes. Browser/native visual identity, Safari, mobile,
physical gamepad comfort and end-to-end human timing are not certified by this
pass. There is no numeric Web/native movement-parity fixture in the accepted
harness; exact native trace parity and shared unchanged controller source are
the relevant evidence. A separate diagnostic export is local test evidence and
must never be substituted for the playable publication artifact.
