# Web feasibility v1 — observed status, September 13, 2026

Current main baseline: `df221870b45de53e4ebb5ea8889b6cf1114054c6`.
Local successor branch: `feature/web-feasibility-v1`.
Decision: `PAGES_PLUS_LARGE_ASSET_HOST`; provisional routine Web regression lane.
No gameplay/world/presentation edits or publication. See
[the full packet](docs/WEB_FEASIBILITY_V1.md) for limitations and pending gates.

Commands below ran from `Hush-Basin-Web-Feasibility-20260913/` unless absolute.
Evidence paths beginning `../` are outside the source checkout.

| Exact command | Observed result |
| --- | --- |
| `git ls-remote origin refs/heads/main` | Exact baseline hash above; initial sandbox DNS failure, successful network-permitted read |
| `/Applications/Godot.app/Contents/MacOS/Godot --version` | `4.7.1.stable.official.a13da4feb` |
| `python3 tools/verify_repo.py` | 389 checks, expected two Quarto vehicle mismatches; retained FAIL |
| `python3 tools/verify_quarto_vehicle.py --native --evidence ../Hush-Basin-Web-Evidence-20260913/baseline` | 449 static PASS; native display processes aborted -6 under sandbox; suite FAIL |
| `python3 tools/verify_quarto_vehicle.py --native --evidence ../Hush-Basin-Web-Evidence-20260913/baseline-native-display` | 449 static PASS; native Run/Quarto/paused-retry/C1/captures PASS; current-world QUARRY_DEPOT Spread entrance miss; suite FAIL |
| `python3 tools/export_web.py --output ../Hush-Basin-Web-Evidence-20260913/export-1` | Full game exported; sandbox editor-settings errors retained; first browser build playable |
| `python3 tools/export_web.py --output ../Hush-Basin-Web-Evidence-20260913/export-2` | Fresh export with display permissions, no error lines, same output sizes |
| `python3 tools/export_web.py --smoke --output ../Hush-Basin-Web-Evidence-20260913/smoke-1` | Separate diagnostic export; browser 13/13 PASS |
| `python3 tools/export_web.py --output ../Hush-Basin-Web-Evidence-20260913/final-build` | Final full-game export, no error lines, 141,565,089 raw bytes |
| `python3 tools/verify_web_lane.py` | Six checks PASS; 310 baseline game files unchanged |
| `python3 tools/verify_quarto_vehicle.py --evidence ../Hush-Basin-Web-Evidence-20260913/final-static` | 449 static PASS; native not rerun because playable source remained identical |
| `python3 tools/export_web.py --template /tmp/hush-missing-web-template.zip --output ../Hush-Basin-Web-Evidence-20260913/should-not-exist` | Rejected missing template before output creation |
| `python3 -m http.server 8067 --bind 127.0.0.1 --directory ../Hush-Basin-Web-Evidence-20260913/export-1/web` | Loopback-only full-game test server |
| `python3 -m http.server 8069 --bind 127.0.0.1 --directory ../Hush-Basin-Web-Evidence-20260913` | Loopback-only evidence/diagnostic build test server |

Browser drivers used installed Chromium 151.0.7922.34 through the bundled Node
runtime at `/Users/cmish/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node`.
For example, the measured run command was that executable followed by
`/tmp/hush-web-perf.cjs`; full input smoke used `/tmp/hush-web-browser.cjs`, and
the explicit 13-check fixture used `/tmp/hush-web-smoke-browser.cjs`.
Copies of these drivers and the local asset server are retained under sibling
evidence `method/`. No browser packages or engines were installed.

The system `/opt/homebrew/bin/node` failed on a missing simdjson library, so the
already-bundled Node was used. Native display and browser tests required sandbox
escalation; no automatic approval rejection occurred. No settings/game changes
were made to hide environmental failures.

First exploratory browser `--script` and custom-main-loop attempts produced no
valid fixture result. Both are retained separately, not counted as passes.
Two absolute alternate-origin loader attempts timed out after initiating large
asset requests; cause unestablished. Tab attempts produced no visibility events;
real hidden-tab suspension remains unverified. Physical gamepad absent; Safari
not tested. The historical and fresh native failures remain open.

Later revalidation must use new output/evidence directories. Do not overwrite
these observations or infer a human acceptance gate from them.


The historical root STATUS.md is preserved byte-for-byte. A documentation-stage
Quarto check rejected a temporary STATUS preamble; the new Web status was moved
to this separate versioned file and the old document restored. That failed
intermediate check remains in final-docs-static/.
