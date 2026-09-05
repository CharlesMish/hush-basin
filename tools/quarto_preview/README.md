# Quarto geometry preview

This local review tool reads the same `game/presentation/quarto_native_v1.json`
as the native Godot rig. Mesh vertices, normals, hierarchy, authored transforms
and scalar motion channels are consumed directly. Godot's default YXZ Euler
rotation order is retained. Triangle winding changes from Godot clockwise to
counterclockwise for the right-handed browser/interchange representation.

The Babylon renderer approximates the native materials. It does not reproduce
Godot lighting, weather, shadows, collisions, follow-camera dynamics or handling,
and is not native validation or MT1 authority evidence. The Game camera button
uses the current tuning values for a stationary, unobstructed frame; the ground
is a neutral review plane, not the Hush Basin map. Normal-speed playback uses the
existing fold/deploy durations; slow playback is for inspecting construction.

No engine or package installation occurs. Supply an existing Babylon core:

```sh
python3 tools/quarto_preview/serve.py \
  --babylon-root /home/cmish/MECHA/MT1/node_modules/@babylonjs/core
```

Open `http://127.0.0.1:5192`. The server binds only to loopback and exposes the
preview files, canonical data, camera settings and the selected engine directory.
Scrub, orbit, compare endpoints, inspect from the stern and try the warning colors.
No game files are modified by the preview.

Static interchange snapshots can be written to a new directory:

```sh
python3 tools/quarto_preview/export_glb.py --output /tmp/quarto-native-v1-glb-review
python3 tools/quarto_preview/verify_exports.py --exports /tmp/quarto-native-v1-glb-review
```

The three GLBs retain the native hierarchy at Spread, midpoint and Drive, with
embedded geometry/materials and no external dependencies. They contain no
controller, collision, native script, gameplay state or animation tracks. Their
JSON export report verifies container structure. The companion verifier compares
every exported world vertex against independently composed native YXZ transforms
and checks triangle winding against outward normals. Native Godot round-trip and
visual comparison remain required. Existing export directories are never overwritten.
