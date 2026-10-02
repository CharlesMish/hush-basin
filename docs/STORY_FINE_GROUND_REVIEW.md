# Story + Fine Ground review — October 2, 2026

The owner requested an isolated draft PR combining Claude's bounded ground
improvement with the latest narrative candidate. This successor authorizes the
terrain material, detail assets and filtering below, plus their tests and docs.
It preserves all narrative, gameplay, camera, world and production behavior.
No main merge, deployment, DNS or credential change is authorized.

## Exact provenance

- Story: `5be7feeef34dbed468e007f5ff4de594d41b0f80`, local
  `experiment/narrative-chapters-2-3-v0-1`; unchanged since the preflight.
- Claude ground: `8b44ea296aac79bdd2c7211aaeeabe213d43aa42`.
- Inspected Claude branch head: `23d100320855cf47a232f8f026d47322129c2004`,
  `claude/fine-ground-v1`; the later commit adds MSAA and debanding.
- Ground tile SHA-256:
  `f40d01df01303565d4ced87b81760cfbea95648bad34d61cabc2c5e607f14632`.

## Integration boundary

Carry over Claude's original generated 256×256 RGBA tile and exact terrain
shader, including the 3 m and rotated 11.3 m layers and 28–85 m distance fade.
The 2048×2048 albedo/roughness maps and terrain UVs remain byte-identical.
Set the same 16× anisotropic filter ceiling for the shader's anisotropic samplers.
Keep the story's main scene, saves, detail-v2 world presentation and all prose.

The branch's SSAO, fog, MSAA and debanding are excluded from this ground-only
integration. They change scene-wide appearance and cost independently of the
341 KiB detail texture. Their source remains on Claude's untouched branch.

The PNG is imported as **Keep**, so native and Web packs retain the exact bytes
needed by `FileAccess` and `load_png_from_buffer`. Claude's `.gdignore` approach
is unsuitable for the story exporter, which excludes hidden files and would
normally import/remap the PNG. The generator now writes the Keep sidecar. The
PNG itself and the shader are unchanged. On decode failure the loader reports
an error and the world falls back to its existing material; it does not crash.

## Verification

Run `python3 tools/verify_story_fine_ground.py --regenerate` for preservation,
bounded wiring, deterministic asset, seam statistics and budgets. Add
`--native --evidence /absolute/new/directory` for matched exact-engine native
geometry/collision/UV checks, motion, material checks and registered captures.
This verifier is bound to the story commit, not historical main. Historical
fixtures and inventories are preserved and may reject intended successors.

The inherited full story flow is
`python3 tools/verify_slices.py --phase complete --output /absolute/new/directory`.
Run the retained opening/cargo/vehicle suites with
`python3 tools/verify_opening_chapter.py --output /absolute/new/directory`.
Export the existing single-thread Web diagnostic with
`python3 tools/export_web.py --slices-smoke --output /absolute/new/directory`;
verify actual browser results and the raw tile's presence in the pack.

Review close, normal, distant, oblique and moving views. The tile uses four
terrain texture samples instead of two; a small asset is not a zero-cost shader.
Desktop timing and small-window Compatibility rendering do not establish
physical-phone performance or touch playability. Human comfort and visual
preference remain owner review questions.

## Recorded results — October 2, 2026

The story baseline is newer than every published narrative branch. Its clean
local checkout matched the owner's Chapters 2+3 source package across all 872
packaged tracked files. The new branch descends directly from that checkpoint;
no narrative commit was reconstructed or rewritten. The draft PR targets
`review/rens-receiver-v0.1`, the latest published story ancestor, and therefore
also carries the existing, previously local narrative commits. Review the final
ground commit against `5be7fee` for the bounded terrain change.

On Godot `4.7.1.stable.official.a13da4feb`, Apple M5:

- Story-bound preservation, shader/tile identity, budgets and deterministic
  regeneration: **902 checks PASS**.
- Matched native Forward+ verification: **19 command/result records PASS**,
  including terrain, collision, UV and node identity, 13 ground runtime checks,
  vehicle 39, Run 54, retry 15, and world/entrances 35.
- Baseline and successor movement traces are identical over **1,260 ticks**:
  `29f1049f8e16ec65d288407c35e6ccae46e87c711bb6b54b134e6158c68b9443`.
- Retained opening/cargo/story suite: **769 checks PASS** over 33 reporting
  fixtures plus the movement run (34 commands, all exit 0).
- Complete opening → Chapter 2 → both Chapter 3 threads: **275 checks PASS**
  headlessly and in the actual single-thread Web export at both 1280×720 and
  844×390 browser viewports; no captured browser errors.
- Authored text: **46 exact passages**, with the same two authorized omissions.
  Every story file remains byte-identical to the selected checkpoint.
- Historical `verify_repo.py`: the same **11 failures / 389 checks** as the
  untouched story baseline. Its historical inventory was not rewritten.

The exported PCK contains the exact original detail PNG bytes. Matched Web
exports total 144,832,628 → 145,094,868 raw bytes (+262,240), and 26,423,187 →
26,671,123 estimated gzip bytes (+247,936). These are complete diagnostic
exports, not deployed or playable release artifacts.

## Visual and resource assessment

Matched native views cover the normal player camera, close Market and Quarry,
medium Market, Clinic, distant basin and five cross-tile positions. A 14.4 m
camera traversal was sampled every ten rendered frames. Inspected images show
restrained grain and relief near the player, without obvious hard tile seams
or a conspicuous repeating grid. The distant basin retains its palette; macro
edges become a little sharper with anisotropic filtering. Sampled screenshots
do not establish full-rate shimmer, comfort or aesthetic acceptance.

Wrap-edge mean channel steps are 44.613 (U) and 42.066 (V), below the ordinary
interior-neighbour mean of 55.580. This checks texture continuity, not whether a
human can eventually notice repetition. The two rotated scales reduce obvious
alignment but remain periodic textures.

The original 2048×2048 maps remain 1,879,142 bytes on disk and 27,962,025 decoded
bytes with mipmaps. The new tile is 234,015 bytes on disk and **349,524 decoded
bytes (341.3 KiB)** with mipmaps: **+1.25%** ground texture payload. This is a
format-derived allocation size, not a verified GPU-residency reading; the
Metal memory monitor returned invalid near-uint64 values and was discarded.

There are four terrain samples per fragment instead of two, plus normal math
and higher anisotropic filtering. The distance fade removes visible grain but
does not skip those texture lookups. Meshes, primitives and draw calls match
at every tested view. In sequential, uncapped desktop runs with 45 warmup and
120 measured frames per view, median-of-view frame intervals were:

| Renderer / window | Story | Ground successor |
| --- | ---: | ---: |
| Metal Forward+ / 1280×720 | 8.217 ms | 8.228 ms |
| OpenGL Compatibility / 844×390 | 1.694 ms | 1.731 ms |

These frame intervals include CPU, scheduling and desktop activity; they are
not isolated GPU measurements or a stable performance budget. Small landscape
Compatibility captures render correctly, but no physical phone, thermal,
battery or touch-playability test was available. Both baseline and successor
Compatibility runs report the same two 349,524-byte texture-leak messages at
shutdown. No new script/shader error appeared; this is not a clean-shutdown
claim. Native Forward+ captures had no logged errors or warnings.

The before/after gallery, exact image hashes, sampled traversal and detailed
measurements are delivered separately to the owner's Library. Run
`python3 tools/launch.py` from this checkout for the unchanged story review
entry with the new ground. Owner play and visual preference remain pending.
