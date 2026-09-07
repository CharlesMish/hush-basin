# Quarto full-game checkpoint — September 7, 2026

Charlie played the imported full game, enjoyed it and explicitly requested
updating GitHub main. This checkpoint promotes the Quarto-derived vehicle from
`0b0cc10efac414a25578468adcc4519f98206ba2`, based on Quiet Surfaces
`9fd4c020c374a7a6db441e4cbc20b53919d5a5e4`, together with two locally verified
test-runner corrections. The complete city, weather, camera, movement, collider,
probes and Run rules remain unchanged. This is a working checkpoint with more
work planned, not a claim of finished-game or performance acceptance.

## Native verification completed before publication

Exact installed Godot: `4.7.1.stable.official.a13da4feb`, native Forward+,
1280 × 720, Apple M5 / Metal 4.0. No substitute engine or dependency installed.

- 449 source/data checks and 22 native execution/result records passed.
- 39 native vehicle checks across 201 poses, including direct/reversed/interrupted posing.
- Exact 1,260-tick baseline/successor movement equality. Both trace SHA-256 values:
  `29f1049f8e16ec65d288407c35e6ccae46e87c711bb6b54b134e6158c68b9443`.
- Run: 54 checks; paused retry: 15; baseline and candidate world: 35 each,
  including all twelve entrance traversals in each version.
- Three matched before/after gameplay-camera views; 18 additional full-game,
  F6 comparison and studio smoke checks.
- Packaged import freshly extracted: 575 inventory entries, exact-engine
  preparation and a native 180-frame launch passed.

The full verified import archive is `District-Zero-Quarto-Full-Game-20260907.zip`,
SHA-256 `688dc002275f5b5f1c245857823c0b17e3d52e808a14add17d58f4962a91639f`.
Its raw captures and execution evidence remain in the local import delivery;
archives, raw captures, caches and credentials are excluded from Git.

Reproduce the versioned suite from a Git checkout with the baseline commit:

```sh
python3 tools/verify_quarto_vehicle.py --native --evidence /absolute/new/evidence
```

## Verifier correction and failures retained

The initial native test used `Mesh.get_faces()`, whose triangle-helper readback
rounded coordinates by up to 0.0000762924 m on this exact engine. Direct render
vertex/index arrays matched all 89 authored meshes exactly. The test now expands
those arrays; its 0.00001 m tolerance and all playable geometry remain unchanged.
The runner adds a matched baseline world traversal and absolute per-command logs.

The initial Market–Clinic entrance 1 Spread traversal stopped at 41.01384 m of
47.16991 m, without contacts or resets. Baseline and candidate passed all twelve
entrances in the complete rerun without gameplay/fixture changes. The earlier
failure remains unreproduced, with cause unestablished. A separate diagnostic
startup crashed with relative paths and passed with absolute paths; no engine
root cause is claimed. Bounded editor parse logs retain the exit warning
`Scan thread aborted...`. One bounded verifier repair round was used.

Quiet Surfaces' earlier Market–Clinic +14.61% p95 miss and capture interruption
remain historical failures. Candidate performance has not been certified. The
separate comparison overlay partly covers the minimap and holds both rigs, so
use the normal game for ordinary play and performance measurement.

Spread measures 2.660 × 0.602 × 2.300 m; Drive 1.05134 × 0.81548 × 2.405 m.
These satisfy this Quarto branch's declared budgets, not the preceding local
native candidate's tighter height cap. The collider did not grow. Charlie's
positive play feedback authorizes this checkpoint; it does not mark every
formal comfort, physical-gamepad, shimmer or performance gate passed.

Historical authorities, manifests and the earlier native-pending branch handoff
are retained unchanged. This dated record adds the later native observations
and owner publication decision without rewriting that history.
