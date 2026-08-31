# District Zero P1A v1.2.4I-R1 adjudication ledger

| Item | Disposition | Evidence / operative repair |
|---|---|---|
| Blocker evidence ZIP identity | ACCEPT | SHA-256 `a1910e236dc9d45cebf5d000bbe5ea3e1b8bdf985355e69abc9937c72e3d44cd`; root inventory `6/6 PASS`. |
| Static verifier process | ACCEPT AS PASSING | Return code `0`; stdout is one valid pretty-formatted JSON object with `status: PASS`, `error_count: 0`, and `anti_duplication_gate: PASS`. |
| Original I terminal gate result | ACCEPT AS HARNESS BLOCKER | `BLOCKED/NOT TESTABLE` at `STATIC_VERIFIER`; `verifier_result: null` despite a valid complete document. |
| Failure class | `TEST_HARNESS` | `COMPLETE PRETTY-PRINTED VERIFIER JSON PARSED AS INDEPENDENT LINES`. |
| Static authority / V6 / Godot / world / movement failure | REJECT | No exact-engine project stage or V6 gameplay ran; the verifier itself was green. |
| Parser repair | AUTHORIZE | Replace per-line interpretation with whole-document `json.loads`, then require object, process `0`, status `PASS`, and integer `error_count: 0`. |
| Verifier output formatting | PRESERVE | Pretty-formatted output remains valid; do not force the verifier onto one line. |
| Sendoff CLI | CORRECT | Document actual `--evidence-dir` and `--standalone-evidence-zip`; retire unsupported `--output-root`. |
| V6 authority | FROZEN | `v1.2.4I`, 12 candidates, 36 static records; no redesign or execution. |
| World / movement / HOP / thresholds | FROZEN | No change authorized. |
| Human World Gate / P1B | LOCKED | Human `NOT PERFORMED`; P1B frozen. |
