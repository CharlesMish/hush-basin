# District Zero P1A v1.2.7 — bounded presentation calibration authority

**Active status:** `READY FOR CODEX — BOUNDED PRESENTATION CALIBRATION`

This packet converts only the two remaining v1.2.6 native visual failures into a finite exact-engine calibration study. It is not a world redesign, movement/tuning change, autonomous-controller turn, Human World Gate, or P1B authority.

## Immutable executed basis

The sole implementation base is the supplied v1.2.6 source transport identity `e59647e98f119405614718c5c20193dec25565ca2b186c25e083edbfd282bac8`. The authoritative executed result is the supplied Run-1 evidence transport identity `13b024c56932e0b83b858ca6453b66dbd84b28b556ebcb38611ddc8d30277437` with exact Godot `4.7.1.stable.official.a13da4feb`.

Accepted Run-1 facts are preserved: C1 1,260 ticks / maximum delta 0.0; render-only two-sided terrain repair retained; canonical render-normal correction retained; 14/14 ray classifications PASS; 19/21 native visual checks PASS; launcher smoke NOT REACHED; prepared human session NOT CREATED; zero human attempts consumed.

The only failed checks are the left outer-closure shadow-on minimum (`0.06987974055145937 < 0.075`) and the right obstacle separation (`0.03155527517161516 < 0.12`). With the left adjacent ground fixed, the closure measured-Y interval is `0.075 <= Y <= 0.0791557292161208`, balanced target `0.0770778646080604`. With right ground fixed, the wall must measure at least `0.3065906688528181`.

## Frozen authority

Movement, tuning, camera, geometry, collision, routes, terrain data, terrain colors, masks, HOP, capture/replay semantics, gameplay thresholds, input, world topology, global lighting, background, tonemapping, shadows, render normals, and every other solid material are frozen. All 21 native visual thresholds and all 14 ray expectations remain unchanged. The successful v1.2.6 two-sided terrain consumer correction and canonical render-normal correction are preserved.

Candidate-time presentation changes are permitted only for `OUTER_CLOSURE_MASK` and `CORE_WALL` in `scripts/p1a_world_builder.gd`. The first family is hue-preserving RGB albedo scaling. The sole preregistered second-stage family, available only if albedo has no robust local pass, is material-local low emission while normal per-pixel shading remains enabled. Unlit materials and global/environment changes are forbidden.

## Deterministic study

`tests/fixtures/v1_2_7_calibration_registry.json` is normative for domains, quantization, execution caps, margin rules, combined guard grid, and tie-breaks. `tools/run_v1_2_7_calibration.py` must operate in disposable copies and retain each evaluated candidate's exact parameters, material-source hash, engine identity, command, stdout/stderr, four native PNGs, raw patch metrics, 21-check result, and ray result.

Calibrate the two materials independently first. Then evaluate the selected pair together and the preregistered 3×3 guard grid. Candidate engine launches are capped at 82. Do not request a new director turn because an early candidate fails.

The final eligible set requires all 21 original visual checks and all 14 ray classifications. Prefer the registered interior region around the outer-closure balanced measured target; enforce the registered right-wall numerical margin where feasible; then minimize literal presentation delta from v1.2.6 with the registered deterministic tie-breaks.

If no authorized albedo or single fallback family yields an eligible combined candidate within valid channels and the cap, terminate exactly `NO_PRESENTATION_ONLY_INTERVAL`. Do not lower/delete a threshold or expand scope.

## Finalization after selection

Materialize the selected literal values into the actual source. Candidate-only copies/overrides are not part of the human build. Regenerate the v1.2.7 selected-presentation record, checksums, verifier expectations, and status. Then, under the exact engine, rerun the combined native visual gate, all 14 rays, strengthened static/preservation verifier, and C1 against the preserved v1.2.6 runtime baseline; C1 requires 1,260 ticks and maximum delta 0.0.

Only after those pass, run the mandatory 75-second one-click A1 launcher smoke. A smoke failure stops without human testing. If smoke passes, create the prepared A1 human session in the same execution with zero attempts consumed. The Human World Gate is still not performed and P1B remains frozen.

## Clean room

Original project code and built-in primitive/procedural presentation only. No external packages, plugins, models, textures, fonts, audio, third-party game material, Xgame material, publishing, deployment, pushing, PRs, contact, or external-account changes.
