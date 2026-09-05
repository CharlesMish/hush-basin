# Quiet Surfaces Git checkpoint — 2026-09-05

This checkpoint imports the delivered Quiet Surfaces v1 world onto Run v0
commit `3b245da432b5a20a1606b3a9b2d9559ba409db39`. It includes the three
connected yards, warm overcast/drizzle, Working Neighborhood architecture and
Quiet Surfaces material polish. The owner explicitly authorized updating the
existing public `CharlesMish/hush-basin` repository's `main` without force.
This authorizes this checkpoint publication only; it does not change the
repository's visibility, license or historical acceptance results.

## Source identity and preparation

- Source: `District-Zero-Quiet-Surfaces-V1-Source.zip`, 16,668,580 bytes.
- SHA-256: `73e0c2b29c055c3aa95721a9ab307608a14f57c1893e5a7339e4aaf8dec7548e`.
- ZIP CRC passed; all 412 archived files match the imported checkout byte for
  byte. This delivery record is the only additional source file.
- Before import, `python3 tools/verify_repo.py` passed the clean Run v0
  repository: R7 234/234, Run overlay 9/9, frozen design 65/65.
- Installed engine: `4.7.1.stable.official.a13da4feb`.
- Imported `python3 tools/verify_repo.py`: PASS, 389 preservation checks.
- `python3 tools/verify_world_polish.py --regenerate`: PASS, 670 checks,
  including repeatable generated world bytes and the shipped inventory.
- `python3 tools/verify_quiet_surfaces.py`: PASS, 389 preservation checks.
- Clean `python3 tools/launch.py --prepare-only`: PASS; fresh import and
  parse check with the exact engine.
- Native `godot --path game --resolution 1280x720 --quit-after 180`: exit 0,
  runtime ready, no logged errors; Metal 4.0 / Forward+ / Apple M5.

The import leaves the craft scene, visual scene/rig, controller, motion math,
tuning, probes/collider, camera and Run gameplay byte-identical to Run v0.
The Run map overlay includes the previously authorized shared-projection fix.
Historical manifests, authorities, design records and validators remain intact;
successor checks describe the explicitly changed world and presentation.

## Verification limits retained from the delivery

The final Quiet Surfaces complete suite remains **FAIL**, with 39 command/result
records. Functional checks passed: exact 1,260-tick movement parity, Vehicle R7,
all 12 entrance traversals, Run/paused retry, weather isolation/contact and
terrain geometry/collision identity. The C1 trace SHA-256 is
`29f1049f8e16ec65d288407c35e6ccae46e87c711bb6b54b134e6158c68b9443`.
These are recorded same-host/version results, not cross-platform guarantees.

The unresolved performance result is Market–Clinic in moving pair 1:
17.479 → 20.032 ms p95 (**+14.61%**, above the 10% target). Static median of
25 view p95 values was +0.06%; moving pooled AB was +2.48% and BA was −2.43%.
The pooled results do not cancel the individual workload failure. Both repair
rounds were used, and the earlier complete-2 BA +19.91% failure remains recorded.

The original final moving capture stalled after two routes and eight
Market–Clinic frames, then was stopped with SIGTERM. Its failed record and
partial frames remain in the local delivery. One evidence-only recapture from
unchanged source completed all five clips; performance was not rerun and the
cause of the stall was not established. Publishing does not turn either
failure into a pass. Comfort, visual preference and full-speed shimmer remain
owner judgments.

See [STATUS.md](../STATUS.md) for every final static/moving workload and the
historical repair record. The original source/evidence delivery stays intact
locally in `District-Zero-Quiet-Surfaces-V1-Run-1`; its before/after survey and
raw captures are intentionally outside Git. Source STATUS evidence links refer
to that companion delivery rather than files shipped in this repository.
The companion evidence ZIP SHA-256 is
`0c8f88bbe160dd6c825f71eab68254a1bac2106e05314324ad7445c1356740ca`.

Archives, raw captures, local caches, credentials and the Quarto review archive
are excluded. The proposed native vehicle successor is separate and is not
part of this `main` checkpoint.
