# District Zero P1A v1.2.4I-R1 delta report

This packet is a behavior-neutral repair of the original `v1.2.4I` gate harness. It does not create a new V6 authority.

- Added whole-document static-verifier JSON parsing and strict PASS/error-count/process validation.
- Added semantic regression cases using the exact captured pretty verifier stdout.
- Added anti-repeat verifier checks that reject the old per-line parser.
- Corrected the Codex command to use `--evidence-dir` and `--standalone-evidence-zip`, mechanically checked against wrapper `--help`.
- Embedded the cleaned original-I blocker evidence and its transport SHA-256.
- Added `harness_repair_revision: v1.2.4I-R1` while retaining `execution_overlay_authority_version: v1.2.4I`.
- Preserved all V6 candidates, static plans, runtime runner, fixtures, gameplay/world/movement bytes, selected HOP, and downstream locks.

The machine-readable I→I-R1 delta manifest is `evidence/v1_2_4i_r1_i_to_i_r1_delta_manifest.json`.
