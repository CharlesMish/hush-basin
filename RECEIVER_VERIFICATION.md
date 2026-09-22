# Ren's receiver — observed checks

Baseline `15934a53fad1eea23327d2bcab21e4bd62e58b97` → runtime
`0640058201c1559b0e4f1621e3a0f7efe8b80ce8`.
Godot `4.7.1.stable.official.a13da4feb`, native Forward+ at 1280×720.

- Baseline inventory: all 744 delivered source files match owner-played state.
  Baseline fresh import/parse/180-frame smoke passed.
- Preservation: 738 existing source files unchanged. The six allowed changes
  are copy, HUD, build/log identity and diagnostic selection. Job IDs, endpoints,
  routes, payments and objective fields compare exactly. Director, save code,
  annex geometry/config, controls, cargo, camera, trail and BRRR are byte-identical.
- Movement: exact 1,260-tick trace matches the accepted same-engine/platform
  baseline, SHA256 `29f1049f8e16ec65d288407c35e6ccae46e87c711bb6b54b134e6158c68b9443`.
- Retained integration: 44/44. All three normal-input route traces match the
  played baseline exactly: stock 11.067 s, receiver 19.867 s, outbound 22.000 s.
- Final native presentation + integration: 57/57. Includes both contact names,
  explicit cargo transformation, purpose visible beyond five seconds, matching
  installed schematic, stopped handoffs, once-only payment, zero-condition
  delivery, no false fabrication on save failure and an unaccepted outbound offer
  whose clock/attempt remain unchanged while browsing.
- Web presentation + integration: 57/57 in Chromium at 1280×720, no script/page
  errors. Separate playable export smoke also passes launch, board, modal,
  driving input, pause and F2/F3. Pinned Web template/WASM unchanged.
- Save store: 56/56 across nine processes. Existing two flags, format and shared
  user-data path remain unchanged. No migration or new persistent field.
- Retained native Run v0: 54/54.

Fresh native screenshots of Market, Ivo's handoff, Works pickup, the driving
purpose strip, Ren's handoff and outbound offer were inspected. Before images in
the packet are retained captures of the exact played baseline. One pre-final
layout adjustment prevents the old full-stat receipt from inflating the compact
handoff. No gameplay repair or retuning was performed.

Playable Web PCK: 102,963,448 → 102,988,172 bytes (+24,724, about 0.024%).
Complete export: 142,811,183 → 142,835,899 bytes (+24,716, about 0.017%).
No new imported assets, textures, shaders, lights or world meshes. This small
copy/UI pass did not repeat the previous AB/BA GPU/frame-time study; no new
performance-improvement claim is made.

Exact command output, JSON results, export manifests, hashes and captures are in
the adjacent evidence folder. The source ZIP excludes caches, logs, test saves,
exports and evidence collections. Its fresh extraction/import/180-frame smoke
is recorded in `evidence/delivery.json` after packaging.

Human comprehension is not passed by these checks. Charlie must explain the
chain after one play; if he cannot, the framing is still insufficient. The
inherited east-approach mast visibility limit remains. No main update, push or
production deployment.
