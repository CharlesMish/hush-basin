# Source Provenance

## Playable source

The `game/` directory was constructed from the verified District Zero Vehicle
Integration R7 owner-review player by copying exactly every path named in
`VEHICLE_R7_SHA256SUMS.txt`, then copying the inventory itself.

- Inventory records: `234`
- Inventory SHA-256:
  `e178f1d4b50518107dbbba0e4bc3eb0c22b41baefce029ecc704c2f6d7fe130c`
- Copied game files including inventory: `235`
- Copied game bytes: `80,612,548`
- Largest file: `world/generated/planar_triangulations.json`
  (`34,063,508` bytes)
- Required engine: `4.7.1.stable.official.a13da4feb`

The original playable directory was not modified. Its `.godot/` cache and
three manifest-external editor-generated test UIDs were not copied.

## Design source

The `design/p1b-gameplay-reward-lab/` directory is a clean copy of the frozen
P1B Gameplay & Reward Design Lab with Python cache files excluded.

- Substantive files: `65`
- Canonical tree SHA-256:
  `150cfe8dcf9829595cfecbfbf7929f138da4d26efd42c6392eb91c8caf0ffe55`
- Bytes: `2,328,104`
- Nightly status: `COMPLETE_FROZEN`
- Aggregate pure checks reported by the lab: `844/844 PASS`
- Product implementation: `NOT STARTED`

The canonical tree hash is SHA-256 over the UTF-8 concatenation of sorted
records in the form `<file_sha256><two spaces><relative_path><newline>`.

## Repository wrapper

Root documentation, Git metadata, and the two portable Python helpers are new
repository-only files. They do not run inside the Godot simulation and do not
change the R7 source inventory.

No third-party runtime packages, addons, models, textures, fonts, music, or
network services were introduced. No credentials or secrets were found in the
prepared snapshot.

The exact historical game snapshot retains a small number of old local-path
and owner-name references. Keep the first remote private. A later public-source
successor may sanitize those records only through an explicit, versioned
privacy release rather than silently changing the R7 evidence.
