# District Zero P1A v1.2.5 — gate-rethink adjudication ledger

| Question | Disposition | Evidence | Resolution |
|---|---|---|---|
| Did J execute correctly? | **ACCEPT** | Evidence ZIP `227f3aa338040f02487fea189c03a3158f97af7df9b864c8324e4b1d6685ac30`; root `225/225 PASS`; exact Godot; executed source `1796/1796` byte-identical. | Consume J as completed historical evidence. |
| Did V7 sensitivity bind? | **ACCEPT** | P, L, and H each changed commands and vehicle trajectory before the hard boundary. | The J stop is not caused by a dead experimental axis. |
| Did the V7 family pass A1? | **REJECT** | Seven selection candidates executed valid `FAIL/1` and crossed the unchanged limit before `TRAVERSED`. | Retire autonomous V4–V7 development; no V8 or new autonomous family is authorized. |
| Was `V7_P36_L30_H20` a tolerance pass? | **REJECT** | It reached chainage `186.663088 m` but lateral distance `11.001759 m`, with outward lateral velocity and predicted further departure. | Preserve exact `11 m`; record it as the closest-to-full-pass controller failure. |
| Does J prove human impossibility? | **REJECT** | J exercised autonomous controller logic, not a human input witness. | Physical playability remains unproven. |
| Is movement/world failure established? | **REJECT** | No human witness or replay trace exists, and J had no world, collision, reset, engine, or harness blocker. | Preserve all frozen gameplay/world authority. |
| What was the automated gate intended to prove? | **ADJUDICATED** | A1/A2/X0 hard requirements define existence of a valid normal-input route traversal; autonomous controller identity is not a product requirement. | Replace the proxy with instrumented human witness capture and deterministic replay. |
| Does human capture weaken hard checks? | **REJECT** | Capture and each replay pass only through the unchanged runtime-vector metrics. | No epsilon relaxation, metric waiver, or qualitative override. |
| Is capture the final Human World Gate? | **REJECT** | It establishes objective physical feasibility only. | Keep the qualitative World Gate separately locked. |
| Is an existing human trace required now? | **REJECT** | Charlie has not installed or played the map. This turn authorizes the workflow before evidence exists. | `human_trace_required_as_input = false`; Codex implementation/preflight comes first. |
| Failure after five attempts or replay mismatch | **REVISE CLASSIFICATION** | Absence of a bounded witness does not isolate the cause. | `HUMAN FEASIBILITY NOT ESTABLISHED — <route>`; preserve every attempt and return for explicit director choice. |
| P1B | **FROZEN** | Outside P1A scope. | No P1B implementation or design. |
