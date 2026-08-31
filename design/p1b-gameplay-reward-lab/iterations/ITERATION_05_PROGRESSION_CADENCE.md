# Iteration 05 — Credits, Unlock Cadence, and Non-Grindy Progression

Heartbeat started local: `2026-08-26T05:12:18-05:00`

Completed local: `2026-08-26T05:37:00-05:00`

Status: `BOUNDED DESIGN ITERATION — NO PRODUCT CHANGE`

## Decision refined

Select `SESSION_CLEAR_LEDGER_REWARD_BRIDGE_V1`.

The first proof needs only one progression fact: completing C01 makes the
vehicle visibly yours. It does not need a second currency or a locked job
ladder. Gate B therefore remains deliberately smaller than the researched
economy:

- all three proof jobs remain exposed;
- District Standard and Trail Off are permanent free defaults;
- one clearly labeled session Credit balance receives every ordinary receipt;
- the first genuine C01 delivery creates one stable entitlement to choose one
  of the two later-authorized proof paints for free;
- choosing may be deferred by keeping District Standard;
- no Reputation, XP, level, shop, price, paid trail, or save appears in the
  Gate-B proof; and
- app closure resets the prototype economy, so the UI must say exactly:
  `SESSION PROTOTYPE — CREDITS AND FINISHES RESET WHEN THE APP CLOSES`.

This is enough to test whether payout feels connected to expression without
asking a temporary session economy to impersonate durable progression.

## Why Reputation is absent

Reputation currently has no distinct job:

- C01–C03 are already open, so there is no meaningful permission decision;
- grade is display-only and cannot be allowed back into stock or progression;
- repeat-based Reputation creates a second shortest-job farming surface; and
- first-clear-only Reputation is an opaque numerical copy of the exact clear
  facts the game already possesses.

Reconsider a trust track only after at least six authored jobs and two genuinely
machine-enforced contract families exist, and only if players can name an
access decision that exact clear milestones cannot explain. Never add it merely
to lengthen the reward runway.

## Gate-B first-clear issue

The entitlement ID is frozen separately from scoring:

```text
C01_FIRST_CLEAR_PROOF_PAINT_ISSUE
```

Its choice set has its own SHA-256 identity. A valid claim:

1. requires one canonical delivered C01 receipt;
2. accepts exactly one of the two authorized proof paint IDs;
3. adds ownership and optionally equips atomically;
4. costs zero and leaves Credits unchanged; and
5. can happen later in the same session if the player selects Keep Standard.

The same claim replay is a no-op. Reusing the entitlement for the other paint
is `ProgressionConflict`. Abort, reset, invalid observation, grade, integrity,
pace, and current balance cannot create or suppress it.

## Post-Gate-B challenger — exact clear-set stock

Only if Gate B passes and players actually miss a use for Credits, study
`CLEAR_SET_CATALOG_V1` under separate authority:

| Exact distinct-clear predicate | Prospective stock | Seed price |
| --- | --- | ---: |
| `{C01,C02}` plus claimed free issue | the unchosen proof paint | `80` |
| `{C01,C02,C03}` plus trail expansion authority | one selected proof trail | `160` |

These are set predicates over stable contract IDs, not counters. A hundred C01
repeats still produce ordinary Credits but cannot counterfeit C02 or C03.
Grade, condition, pace, route, distance, Session Best, purchase count, and
balance never reveal stock. New future contract IDs cannot satisfy or mutate a
frozen old predicate.

The Gate-B catalog has no reachable purchase command. The post-Gate-B catalog
has a different hash and is a design challenger, not silently active product
scope.

## Price authoring

Prices are offline catalog literals derived from one calibrated global scale:

```text
paint_price = ceil_to_10(R_catalog * 0.8 reward-minutes)
trail_price = ceil_to_10(R_catalog * 1.6 reward-minutes)
```

At the provisional iteration-04 rate seed `R_catalog = 100 Credits/minute`,
the outputs are `80` and `160`. Once frozen, a catalog never reads player
balance, temporary surplus, grade, route, actual distance, completion count,
or current attempt quality. A later global rate retune creates a new catalog
version and rescales the shelf together; it does not dynamically alter a live
session.

The `80/160` values are cadence evidence, not C01/C02/C03 price authority.
Iteration 04's measured-overhead and wall-pressure falsifiers must be resolved
before any product price is frozen.

## Cadence simulation

The iteration-04 illustrative contracts produce:

| Strategy row | C01 | C02 | C03 | Chain total | After `80` paint | After `160` trail |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| completion floor | `35` | `60` | `85` | `180` | `100` | not yet affordable |
| typical learner | `61` | `105` | `149` | `315` | `235` | `75` remains |
| learned clean | `68` | `116` | `165` | `349` | `269` | `109` remains |
| clean at reference | `66` | `113` | `161` | `340` | `260` | `100` remains |

The floor player who buys the paint has `100` after C03. One ordinary shortest
C01 repeat adds `61`, buys the trail, and leaves `1`. If even that bounded
fourth completion feels like grind, lower the whole shelf only after measured
human cadence; do not add a daily bonus, repeat decay, random grant, or hidden
price adjustment.

The model deliberately allows a choice: save for the trail or buy the second
paint first. It does not manufacture scarcity. Every successful new attempt
still receives its full three-line receipt.

## Atomic profile rules

Progression consumes the canonical iteration-04 receipt and attempt identity;
the UI never manufactures an award.

- `(session_epoch, monotonic_sequence)` still identifies an attempt.
- Exact terminal replay is `DUPLICATE_NOOP`; altered reuse is a ledger conflict.
- A new delivered contract may add one exact clear fact and one first-clear
  entitlement in the same committed transition.
- Purchase requests name purchase ID, item ID, and catalog hash—never a client
  price.
- Locked, unknown, stale, insufficient, or unowned requests leave Credits,
  ownership, equipment, and clears unchanged. A well-formed request ID records
  its terminal outcome, so retry after state changes requires a fresh ID.
- Exact funds may reach zero; purchase replay or an already-owned request
  cannot debit again.
- Equip is free, idempotent, and owned/default-only.
- `available_balance = total_awarded - committed_literal_prices` at all times.
- Continue, retry, ordinary reset, and Results reopen preserve the profile.
- A true new app/session epoch clears balance, award/purchase ledgers, clear
  facts, entitlement state, non-default ownership/equipment, and Session Best
  together. No file is written in this design lab.

## Reward presentation rule

One Results transition may show at most one new reward card, in stable catalog
order. The card states the exact condition, progress, and literal price. It
never auto-purchases, flashes a countdown, hides a grade requirement, or opens
the next job automatically.

Gate B shows only the free C01 issue and the labeled session balance. A future
clear-set shelf must remain a small loadout surface, not a rotating storefront.

## Paint contribution — Open Charter

One original ledger-ink, water-blue, rose-clay finish:

| Role | Color | Emission ceiling |
| --- | --- | ---: |
| Frame | `#151C24` ledger ink | `0.14` |
| Shell | `#3B536B` open-water blue | `0.24` |
| Lift | `#A9877B` weathered rose clay | `0.34` |
| Underlay | `#27403E` deep patina | `0.20` |
| Trim/seams | `#DED2B5` vellum | `0.50` |
| Drive can | `#617681` blue pewter | `0.26` |
| Derived joint target | `#2B3238` | `<=0.18` |

Native metallic/roughness and all functional energy, nozzle, bore, caution,
and strike materials remain unchanged. Once equipped, Open Charter has no
input from Credits, grade, integrity, contract count, or result state.

Reject if native Spread/mid/Drive captures lose four grayscale masses, rose
muddies orange/red cues, blue muddies Drive cyan, trim clips or blooms, bright
or dark backgrounds swallow roles, a reserved material hash changes, or the
movement trace delta is nonzero.

## Trail contribution — Open Fold

One two-tone center-creased `ImmediateMesh` sheet along only the craft's actual
interpolated past path:

- one persistent `ImmediateMesh` resource with at most one surface at a time;
- three vertices per sample, at most 27 samples / 81 vertices / 104 triangles;
- sample at most `30 Hz` or every `0.35 m`;
- at most `0.50 s` and `15 m` of history;
- width tapers from `0.072 m` at the head to `0.018 m` at the tail;
- port `#D7CCAD`, starboard `#829AA5`, meeting at a quiet center crease;
- alpha `<=0.32`, monotonically to exactly zero;
- depth test on; depth write, shadows, GI, lights, collision, RNG, prediction,
  and gameplay queries off; fixed/preallocated CPU history and material; zero
  per-frame node, material, or resource-object creation; and
- pause freezes; reset, restart, scene/profile change, invalid craft, generic
  clear, or a one-frame displacement `>8 m` clears before rendering.

Reduced motion flattens the fold, uses a fixed `0.028 m` width, at most 12
samples / `0.20 s`, and alpha `<=0.16`. Trail Off remains permanent and free.

Reject if Open Fold resembles a route or ideal line, appears ahead, survives
relocation, crosses walls, obscures road/craft/UI, aliases at Drive speed,
occupies `>=3%` of the viewport, exceeds `0.25 ms` median or `0.55 ms` p95,
grows in a ten-minute soak, or changes movement.

Visual mockup: `concepts/ITERATION_05_OPEN_CHARTER_OPEN_FOLD.svg`  
SHA-256: `cbeb64dfc602ca41b2cbdcebf5f44bf77058194b138c089d3c384938f02b773f`

## Deterministic evidence

Command:

```text
PYTHONPATH=tools python3 -B tools/test_iteration_05_progression.py \
  --report analysis/ITERATION_05_PROGRESSION_REPORT.json
```

Result: `142/142 PASS WITH POST-GATE-B AND NATIVE FALSIFIERS REMAINING`.

Report SHA-256:
`847492dcf043636761c0a39ab2369b5f6ef708590ef670e680a0d39ba21e500d`

The vectors cover price quantization/identity, exact catalog binding, forged
phase/price/receipt rejection, absence of Reputation/grade fields, proof-phase
purchase blocking, abort/terminal/issue semantics, full-value repeats, claim
conflicts, exact clear-set permutations, future-ID non-substitution,
quality-invariant stock, 100-repeat breadth attack, four cadence rows,
exact/one-below purchase boundaries, terminal purchase-request identities,
stale/forged/double purchase handling, balance conservation, free equip, and
coherent distinct-epoch session reset.

This is pure reducer and arithmetic evidence—not Godot UI, durable ownership,
native reward desirability, measured earning cadence, or authorization to build
the post-Gate-B shelf.

## Human and native falsifiers

Stop or defer progression expansion if any is true:

1. the C01 free issue is not visibly meaningful in both Spread and Drive;
2. it interrupts the result enough to weaken the desire to continue driving;
3. labeled session Credits feel deceptive or pointless before persistence;
4. the three-job chain does not make the player want another job or retry;
5. a paid paint is not affordable by two ordinary distinct clears after scale
   calibration;
6. a first trail remains unaffordable after the chain plus at most one ordinary
   shortest repeat;
7. shortest-job or wall-pressure play wins measured Credits/minute;
8. buying the paint makes the trail feel withheld rather than chosen;
9. a repeat, grade, or future contract silently advances an exact clear gate;
10. any duplicate, stale catalog, insufficient purchase, reset, or reopen
    changes balance or ownership twice;
11. session-only loss surprises the player; durable save then outranks more
    stock; or
12. Open Charter/Open Fold harms functional cues, occlusion, performance, or
    movement equivalence.

No product file was changed. R7 remains read-only.
