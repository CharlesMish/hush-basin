# Hush Basin — World Identity / Detail v2

This is an isolated presentation successor for Charlie's review. It includes
the accepted Quarto game, Quiet Surfaces world, warm overcast preset and current
Web export/hosting/shell architecture. It has not been deployed or pushed.

Use the existing `PLAY_FULL_GAME.command` launcher, or run
`python3 tools/launch.py` from this directory. Exact installed Godot
`4.7.1.stable.official.a13da4feb` is required. Existing controls are unchanged.

The old README, STATUS and authorities are historical records, retained exactly.
The current narrow authority is `WORLD_IDENTITY_DETAIL_V2_AUTHORITY.md`.
See `docs/WORLD_IDENTITY_V2_REVIEW.md` for this delivery's results and playtest.

Authoring lives in `game/presentation/world_identity_detail_v2.json`.
`python3 tools/generate_world_identity_v2.py` expands fixed roof/facade modules;
`python3 tools/verify_world_identity_v2.py` checks repeatability, occupied plot
bounds and preservation against the accepted 465-file inventory, including in
an unpacked ZIP. Existing historical validators are deliberately not rewritten.

The only existing product-file edit is one additive world-builder call. The
new detail root has no physics nodes. Existing collision, terrain, classifications,
destinations, movement, camera, Quarto, weather and Run are preserved. Presentation
identity is `world-identity-detail-v2`; geometry identity remains `world-polish-v1`.

No new texture, shader, light, particle, dependency or gameplay system is added.
Production deployment is a separate owner decision. The source includes the
unchanged Web tools for continuity; do not run deployment commands for review.
