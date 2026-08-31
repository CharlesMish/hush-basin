# Iteration 07 — Cosmetic Desirability, Trail Legibility, and Reward Surface

Heartbeat started local: `2026-08-26T07:13:48-05:00`

Completed local: `2026-08-26T07:34:00-05:00`

Status: `BOUNDED DESIGN ITERATION — NO PRODUCT CHANGE`

## Decision refined

Select `RECEIPT_FIRST_SESSION_REWARD_SURFACE_V1`.

The reward screen remains a delivery receipt. Cosmetics are optional and one
shallow action away. They do not delay the next drive, reinterpret the award,
or turn the Gate-B proof into a shop.

The exact hierarchy is:

1. the immutable committed receipt;
2. at most one nonmodal reward card;
3. `CONTINUE AT <DESTINATION>` as the default action;
4. an optional free finish drawer; and
5. only in a separately authorized post-Gate-B build, an optional shallow
   paid loadout.

Every reward surface repeats:

```text
SESSION PROTOTYPE — CREDITS AND FINISHES RESET WHEN THE APP CLOSES
```

Gate B also labels its otherwise decorative balance:

```text
SESSION CREDITS · NO SHOP IN THIS PROOF
```

This is intentionally candid. Session Credits prove that a completed drive
can create legible value; the one free C01 finish proves that value can cross
back into presentation. Gate B does not imply persistence or ask Charlie to
grind a currency that cannot yet be spent.

## Receipt-first Results

```text
DELIVERED · GRADE A
96 CREDITS                         BALANCE AFTER DELIVERY 164

DELIVERY                                             +50
CONDITION 92% · 1 EPISODE                            +32
PACE 1:42 · REF 1:35                                 +14

NEW SESSION BEST RECEIPT
SESSION PROTOTYPE — CREDITS AND FINISHES RESET WHEN THE APP CLOSES

[ CONTINUE AT DEP ]       [ FINISHES ]       [ RESTART AT MRK ]*
Run details >
```

`RESTART AT <ORIGIN>` remains absent unless its separate relocation authority
passes. Distance, route, Hops, form duty, and impact detail remain collapsed
because they do not pay. Grade remains an explanation of condition and pace;
it never multiplies the three-line award.

The receipt is rendered from one canonical committed record. Its Delivery,
Condition, and Pace lines must sum exactly to the displayed Credits. A later
cosmetic purchase may change `CURRENT SESSION BALANCE`; it cannot rewrite the
historical `BALANCE AFTER DELIVERY`.

No count-up animation gates input. Continue is readable and actionable as soon
as the valid terminal record is present.

## One-card ceremony

One Results transition can present at most one card in this stable order:

1. the newly created C01 free finish issue;
2. the conditionally revealed paid paint; or
3. the conditionally revealed paid trail.

The card never steals focus, auto-opens a drawer, expires, or grants an item.
Its event identity is bound to the committing attempt and card/item identity.
Reopening the same result cannot replay the ceremony. A pending entitlement
remains available in the free finish drawer without manufacturing a new card
after an abort, repeat, or unrelated result.

The Gate-B card is exactly:

```text
FREE FINISH CHOICE READY
C01 FIRST CLEAR · FREE · SESSION ONLY
[ VIEW FINISHES ]
```

Opening, previewing, claiming, keeping Standard, closing, and continuing each
require a distinct fresh edge. One physical press can cross only one state
boundary.

## Gate-B finish drawer

Gate B exposes one paused, free-only drawer:

```text
FINISHES · SESSION PROTOTYPE

District Standard                         OWNED · EQUIPPED
Proof Paint A                             FREE ISSUE
Proof Paint B                             FREE ISSUE
Trail Off                                 ALWAYS FREE

FINISH ONLY — NO HANDLING, CARGO, OR PAYOUT EFFECT
```

There are no prices, paid commands, locked trail silhouettes, rarity labels,
sales, countdowns, Reputation, or future-stock tease. Before the free choice
is claimed, the drawer shows exactly District Standard, the two authorized
proof paints, and Trail Off. After claim, the unchosen paint disappears from
the Gate-B drawer rather than pretending to be purchasable.

`KEEP DISTRICT STANDARD — CHOOSE LATER THIS SESSION` closes the drawer without
consuming the issue. `CLAIM & EQUIP` atomically consumes the exact entitlement,
adds and equips one authorized paint, and debits zero Credits. It returns to
the same immutable receipt with Continue focused.

The preferred preview is the actual render-only R7 visual rig cycling Spread,
midpoint, and Drive. It must contain no controller, collider, input, route,
cargo, payout, or physics node. If that preview cannot be built behavior-
neutrally, omit it: seeing the equipped finish on Continue is more honest than
a misleading swatch.

## Conditional shallow loadout

This is a registered challenger, not Gate-B authority.

Only a distinct `POST_GATE_B_CLEAR_SET` catalog may expose:

- the unchosen native-approved proof paint after exact clears `{C01,C02}` and
  a claimed free issue, literal price `80`; and
- one separately native/performance-approved trail after exact clears
  `{C01,C02,C03}`, literal price `160`.

Stock is a visible exact set. Grade, condition, pace, Credits, repetition,
future contract IDs, Session Best, route, actual distance, and Reputation
cannot substitute for a required clear.

A paid card says `NOW AVAILABLE TO BUY`, never `EARNED`. A purchase happens
only inside Loadout through an explicit `BUY & EQUIP · <literal price>` action.
The reducer—not the UI—owns catalog identity, price, funds, entitlement,
ownership, and equipment. A request carries the session epoch, monotonic
purchase identity, item ID, and exact catalog hash; there is no client price.

The successful debit, ownership grant, and same-slot equip are atomic. Exact
replay is a no-op. Altered reuse is a conflict. A failed request keeps its
terminal identity and cannot become successful later merely because funds or
stock changed. Defaults and already-owned items equip for free.

Illustrative already-verified cadence remains:

| Path | C01+C02+C03 ordinary Credits | After 80 paint + 160 trail |
| --- | ---: | ---: |
| completion floors | `180` | needs one bounded repeat after buying paint |
| typical learner | `315` | `75` remain |
| learned-clean | `349` | `109` remain |

These examples demonstrate affordability, not price authority. The shelf
remains conditional on measured native cadence, owner desire for a Credit use,
and session-loss comprehension. If the player asks for saving before more
stock, save outranks the shelf.

## Input and state contract

```text
RESULTS
  -- fresh View Finishes --> ISSUE_DRAWER or LOADOUT_DRAWER
  -- fresh Continue --> WAITING_FOR_NEUTRAL(next=FREE_ROAM)

DRAWER
  -- fresh Preview --> presentation-only preview
  -- fresh Claim/Buy/Equip --> one reducer transaction
  -- fresh Back --> RESULTS

WAITING_FOR_NEUTRAL
  -- all aliases neutral for two complete always-process samples --> FREE_ROAM
```

Results, either drawer, and the neutral gate consume reset and every gameplay
alias. Modal time does not advance active time, delivery settle, cargo,
odometer, or the craft. Continue preserves the exact reached transform and
velocity; it does not relocate, auto-open Dispatch, or allocate an attempt.

Session reset coherently clears balance, award and purchase ledgers, clear
facts, pending issue, nondefault ownership/equipment, cards, and Session Best.
Stale prior-epoch actions fail.

## Paint contribution — Vesper Ceramic

One original fixed finish with a neutral-violet body and warm ceramic reveal:

| Role | Authoring color | Emission ceiling |
| --- | --- | ---: |
| Frame | `#161A20` ink graphite | `0.12` |
| Shell | `#57485E` smoked aubergine | `0.22` |
| Lift | `#C4AF99` warm ceramic | `0.34` |
| Underlay | `#263A3C` tide-black | `0.18` |
| Trim/seams | `#D7CDD9` pearl lilac | `0.48` |
| Drive can | `#727A83` blue nickel | `0.24` |
| Derived joint target | `#2D2D34` | `<=0.16` |

Approximate linear-sRGB luminances across the six primary roles are `0.0101`,
`0.0747`, `0.4470`, `0.0376`, `0.6312`, and `0.1914`. This is desk evidence
for four clear value masses, not a native pass.

Metallic/roughness and all energy, nozzle, bore, CLEAR, CAUTION, and STRIKE
materials stay fixed. Vesper Ceramic has no runtime input from contract,
condition, pace, grade, balance, reward, route, speed, form, or cue state.

Reject it if matched native captures show fewer than four readable grayscale
masses, lift/trim washout, horizon silhouette loss, functional-cue confusion,
any ceiling violation, reserved-material change, per-frame material/resource
allocation, nonzero movement delta, or owner judgment that it is not visibly
reward-like in both Spread and Drive.

Vesper Ceramic is a researched reserve. It is not silently one of the two
Gate-B proof paints.

## Trail contribution — Tide Script

One camera-facing ribbon follows only the craft's actual interpolated past
path. A soft world-distance width rhythm celebrates long drift without timing,
scoring, or guiding it.

- one persistent two-sided unshaded `ImmediateMesh` surface;
- two vertices per sample, at most `20` samples / `40` vertices / `38`
  triangles;
- sample only after both `1/30 s` and `0.30 m`;
- retain at most `0.54 s` and `18 m`;
- full width `0.040–0.066 m` over a fixed `4.80 m` spatial wavelength;
- pearl steel `#CBD6DA` and muted violet `#A995BF` edges;
- head alpha `<=0.36`, monotonically reaching exactly `0` at the tail;
- invisible through `5 m/s`, full by `14 m/s`;
- one private unsaved chord counter unavailable to gameplay/economy;
- depth test on; depth write, shadows, GI, lights, collision, prediction, RNG,
  gameplay queries, and post-warm-up object allocation off; and
- pause freezes history/phase; every reset, restart, scene/profile/equip/session
  change, invalid or nonfinite state, timestamp regression, generic clear, or
  one-frame displacement `>8 m` clears before rendering.

Reduced motion removes width modulation and uses at most `8` samples, `0.18 s`,
`4 m`, fixed `0.026 m` width, pearl only, and alpha `<=0.14`. Trail Off remains
permanent and free.

Reject Tide Script for forward projection, wall-through pixels, a relocation
streak, aliasing at `14/25/33.13/40 m/s`, timer or route interpretation,
craft/road/UI obstruction, viewport occupancy `>=2.5%`, added cost above
`0.20 ms` median or `0.45 ms` p95, state/resource growth in a ten-minute soak,
post-warm-up allocation, reduced-motion failure, or nonzero movement delta.

Tide Script is a researched reserve. Gate B still has no trail.

## Cosmetic convergence rule

No mockup, color arithmetic, name, or automated score may create stock.
Candidate stages are:

1. `DESK_QUALIFIED` — exact profile and static bounds;
2. `NATIVE_ELIGIBLE` — no reserved-cue/gameplay/physics/state violation;
3. `NATIVE_PASSED` — complete native captures, movement equivalence,
   occlusion/reset, reduced motion, and performance hard gates;
4. `OWNER_RANKED` — blinded native desirability review; and
5. `FINALIST` — selected only from stages 3+4.

Hard gates are non-compensable. Beauty cannot offset cue ambiguity,
wall-through rendering, discomfort, movement delta, or performance failure.

The iteration-08 desk-evidence shortlist is:

| Paint finalists | Paint reserve | Trail finalists | Trail reserves |
| --- | --- | --- | --- |
| Orchid Static | Vesper Ceramic | Twin Vector | One Wake |
| Saltglass | Vesper Ceramic | Courier Pulse | Tide Script |
| Ember Relay | Moss Circuit if warm cues conflict | Comet Ledger | One Wake if gold/ground-spray conflicts |

The final three paints require fourteen matched `1280×720` native captures:
Spread/mid/Drive against bright and dark contexts plus orange/cyan/amber/red
cues against both. The final trails use identical native clips for straight
Drive, long drift, braking, Hop/landing, wall occlusion, pause, reset,
relocation, reduced motion, and maximum surface-spray soak.

Owner pairwise review hides names, prices, rarity, and unlock copy. A paint
must look worth choosing in both Spread and Drive. A trail must express actual
long-drift motion without reading as a route or ideal line.

## Deterministic evidence

Command:

```text
PYTHONPATH=tools python3 -B tools/test_iteration_07_reward_surface.py \
  --report analysis/ITERATION_07_REWARD_SURFACE_REPORT.json
```

Result:

```text
112/112 PASS WITH NATIVE AND OWNER COSMETIC GATES REMAINING
```

The pure vectors cover:

- strict cosmetic evidence cardinality, finite numeric fields, movement delta,
  wall occlusion, reduced motion, performance, resource growth, and owner
  evidence boundaries;
- immutable receipt arithmetic, terminal and SHA identity;
- one-time reward-card event identity, deferred entitlement access, a blocked
  Gate-B paid action, and late free-issue claim;
- Gate-B free-only card inventory with no locked/paid tease;
- fresh edges, modal reset consumption, and two-frame neutral release;
- atomic free claim, exact paid purchase, replay/conflict, shortfall, equip, and
  historical-receipt preservation;
- exact clear-set/literal-price presentation without grade, route, distance,
  or Reputation inputs; and
- explicit no-product/no-Human-World-Gate status.

These are design-model tests. No Godot scene, native paint, native trail,
player preference, or product gameplay was executed.

## Stop boundary

- R7 source/player: byte-preserved and read-only.
- Product gameplay: not implemented.
- Gate-B paid shop/trail: not authorized.
- Human World Gate: not performed.
- P1B implementation: not started.
