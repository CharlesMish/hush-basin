# Iteration 03 — Pace, Grade, Feedback, and Retry Cadence

Heartbeat started local: `2026-08-26T03:10:47-05:00`

Completed local: `2026-08-26T03:26:00-05:00`

Status: `BOUNDED DESIGN ITERATION — NO PRODUCT CHANGE`

## Decision refined

Select `REFERENCE_RATIO_CONDITION_PACE_GRADE_V1` as the first-slice pace and
grade seed. Pair it with a results cadence that defaults to spatial continuity
and names any optional relocation honestly.

The design has four constraints:

1. time can reward a committed long drift but never turn a valid delivery into
   a routine failure;
2. condition remains more important than speed;
3. grade explains the same evidence that paid, rather than multiplying the
   award again; and
4. replay cannot silently teleport, erase, or repay the completed attempt.

These are deterministic design decisions, not human-calibrated par values or
Godot-runtime proof.

## Active-time authority

Pace uses the session-owned active physics time established in iteration 01:

- start on the first unpaused `ACTIVE` physics tick after the two-frame neutral
  gate;
- include ordinary active driving and the terminal delivery-settle interval;
- freeze during Dispatch, Results, pause, and every neutral-release barrier;
- never catch up wall time on resume; and
- freeze the final value inside the one immutable terminal receipt.

Each contract definition carries one positive, versioned reference time `P`.
The attempt freezes that value at acceptance. Let `r = elapsed / P`.

## Soft pace curve

The pace factor `T` is linear between these anchors:

| Ratio `r` | Pace factor `T` | Meaning |
| ---: | ---: | --- |
| `<= 0.85` | `1.00` | full pace share |
| `1.00` | `0.75` | reference run keeps most of the share |
| `1.25` | `0.40` | deliberate late run still earns some |
| `>= 1.75` | `0.00` | pace share ends; delivery continues |

There is no timeout, failure, debt, or negative multiplier at any ratio. The
curve is continuous, monotone, scale-invariant, and saturated in `[0,1]`.

This replaces the broad study's very long `2.5x` tail. That tail made the
three-line receipt feel nearly constant and obscured the moment pace stopped
paying. A hard cutoff at reference, red countdown, and sudden time cliff are
rejected because they would turn exploratory long drift into anxiety.

### Reference calibration protocol

No absolute C01/C02/C03 reference is frozen from route geometry or an automated
driver.

For each contract and build:

1. Charlie completes two familiarization deliveries that are not measured;
2. record the next five consecutive valid learned completions on the advertised
   line—do not cherry-pick slow or damaged valid runs;
3. require at least three of five to finish at `>=90%` condition, otherwise fix
   cargo/route readability before calibrating time;
4. let `M` be their median active time;
5. propose `P = ceil_to_0.1s(1.10 * M)` and freeze it for that build; and
6. confirm it with five new completions.

C03 must additionally include at least three completed confirmations on each
declared route family. A legitimate route alternative may not be forced below
grade B solely by elapsed time. References never personalize or adapt during a
session.

Human acceptance requires comfortable clean runs to tend A, strong clean runs
to make S possible, early learned runs to remain mostly B/C, and C02's long
sweep to reach A without wall-riding. Failure stops reference calibration; it
does not authorize changing movement, cargo, or a player's personal target.

## Grade is explanation, not currency

The unchanged first-slice payout remains:

```text
Credits = round_half_up(B * (0.50 + 0.35 * integrity + 0.15 * T))
```

Grade uses the same condition and pace evidence:

```text
Q = 100 * (0.70 * integrity + 0.30 * T)

S  Q >= 94, integrity >= 95%, and r <= 0.95   EXCEPTIONAL
A  Q >= 82 and integrity >= 80%                STRONG
B  Q >= 65 and integrity >= 55%                SOLID
C  Q >= 45                                      COMPLETE
D  otherwise                                    ROUGH
```

The condition floors are explicit receipt rules, not hidden deductions. They
prevent a very fast but heavily damaged run from presenting as top-tier cargo
work. Grade never enters money, stock, unlocks, prices, progression, session
best comparison, or contract availability.

At the selected anchors:

| Example | Integrity | `r` | `T` | `Q` | Grade |
| --- | ---: | ---: | ---: | ---: | --- |
| Exceptional clean | `98%` | `0.90` | `0.917` | `96.1` | S |
| Clean at reference | `95%` | `1.00` | `0.750` | `89.0` | A |
| Ordinary learner | `90%` | `1.25` | `0.400` | `75.0` | B |
| Pristine long drift | `100%` | `1.50` | `0.200` | `76.0` | B |
| Fast, damaged | `75%` | `0.85` | `1.000` | `82.5` | B by condition floor |
| Damaged, no pace | `55%` | `1.75` | `0.000` | `38.5` | D |

A clean reference run is deliberately A rather than an automatic S.

## HUD and result language

The active HUD derives time and label from the same fixed active-time value:

```text
PACE 01:23 · FULL BONUS OPEN
PACE 01:49 · BONUS EASING
PACE 02:18 · BONUS ENDED · DELIVERY CONTINUES
```

Never show `LATE`, `FAILED`, a red countdown, projected Credits, a live grade,
or a live personal-best delta. Each pace-state boundary may make one restrained
nonmodal cue; arrival/settle feedback retains priority.

The result has one explanatory hierarchy:

```text
DELIVERED · GRADE A
96 CREDITS                         BALANCE 164
DELIVERY                                +50
CONDITION 92% · 1 EPISODE               +32
PACE 1:42 · REF 1:35                    +14
NEW SESSION BEST RECEIPT
[ CONTINUE AT DEP ]       [ RESTART AT MRK ]
Run details >
```

The three integer lines are reconciled by stable largest remainder and must
sum exactly to the single atomically awarded total. This changes no payout
weight; it prevents a one-Credit explanatory mismatch. Distance, Hops, form
duty, route observations, and impact detail are collapsed receipt facts because
they do not pay. An unlock preview, when real, is the only conditional panel.

The terminal headline stays `DELIVERED` even when pace earns zero or condition
is poor. `COMPROMISED CARGO` may qualify that success, never contradict it.

## Session best

Use `SESSION BEST RECEIPT`, not an ambiguous fastest-time `PB`. It is keyed by
the frozen contract-definition and scoring-version hashes and compares only
completed ordinary receipts:

1. higher ordinary Credits;
2. then higher displayed integrity unit;
3. then lower displayed elapsed tenth; and
4. exact tie keeps the earlier result.

First-clear and unlock grants are excluded. The only callouts are `FIRST
SESSION RESULT`, `NEW SESSION BEST RECEIPT`, and `MATCHED SESSION BEST RECEIPT`.
Abort cannot create or erase a best. A retry never rolls back the prior receipt,
award, or best.

## Continue and explicit restart

`CONTINUE AT <DESTINATION>` is the default focused action. After the ordinary
neutral gate it resumes free roam at the exact reached transform and velocity,
sets the destination as the future recovery anchor, and does not auto-open the
next Dispatch.

There is no honest instant `Retry` from the destination without relocation.
The optional secondary action is therefore named `RESTART AT <ORIGIN>` and its
focus help says `Relocates craft · completed reward remains`.

This option is conditional on explicit P1B relocation authority and exact-engine
proof. If authorized, it runs while terminal and paused, clears transient cargo,
observer, navigation, and trail history, performs exactly one reason-tagged R7
reset to the frozen origin, then exits through the neutral gate into free roam
with the board closed. The player must make a fresh Dispatch/Accept to create a
new attempt. It never crosses one press into driving.

At contract acceptance, a future wrapper must set the current contract origin
as the R7 recovery anchor. Active/fall reset then wins the terminal race,
returns to the correct origin, awards zero, and presents one durable line:

```text
DELIVERY ABORTED · CRAFT RESET · NO CREDITS
```

On Continue, the destination becomes the next free-roam recovery anchor without
moving the craft. If this behavior-neutral anchor transaction is not separately
authorized and proved, omit `RESTART AT ...` and keep C02/C03 blocked rather
than pretending their reset/retry cadence works from the historical MRK anchor.

Generic Retry, automatic next-job offer, automatic relocation, results-bound
`R`, and an acknowledgement modal are rejected.

## Paint contribution — Reprise Alloy

One original cool mineral retry-themed finish, fixed and presentation-only:

| Role | Color | Emission multiplier |
| --- | --- | ---: |
| Frame | `#171A29` midnight indigo | `0.18` |
| Shell | `#434A68` slate violet | `0.28` |
| Lift | `#A7ACC7` weathered periwinkle | `0.42` |
| Underlay | `#332B42` blackberry graphite | `0.30` |
| Trim/seams | `#DDD2E5` porcelain lilac | `0.58` |
| Drive can | `#615A7A` muted iris steel | `0.30` |
| Derived joint target | `#343344` | `<=0.24` |

Existing roughness, metallic values, energy, nozzle, bore, caution, and strike
cues stay fixed. The palette never reacts to time, grade, cargo, payout, or
retry count. Reject it if native Spread/mid/Drive captures lose grayscale role
separation, pale parts wash into walls, trim blooms, dark parts vanish into the
horizon, or any functional cue loses priority.

## Trail contribution — Second Draft

Two asymmetric current-path-only ribbons make a quiet editorial pair without
ever depicting the prior run:

- camera-facing `ImmediateMesh` history strips from the existing presentation
  spine only;
- primary `#B9C3D8`, `0.052 m`, `0.50 s`, at most 26 samples, alpha `<=0.42`;
- secondary `#D4C0DC`, `0.028 m`, `0.34 s`, at most 18 samples, alpha `<=0.34`;
- fixed offsets `-0.065/+0.065 m`, sample at most `30 Hz` or each `0.30 m`,
  retained distance at most `18 m`, and 88 total strip vertices;
- tails reach zero alpha; speed visibility only suppresses idle clutter;
- depth test on; depth write, shadow, GI, lights, collision, gameplay query,
  time strobing, and forward projection off;
- pause freezes it; reset/restart/terminal/scene change/invalid craft or one
  frame over `8 m` clears both histories; and
- reduced motion uses only the primary for `0.22 s`, at most 12 samples,
  `0.036 m`, alpha `<=0.20`; Trail Off remains permanent.

Reject if either ribbon reads as a ghost, ideal line, time split, or route
guide; survives relocation; crosses walls; aliases at Drive speed; obscures
road/craft; exceeds `0.35 ms` median / `0.75 ms` p95 added-frame study budgets;
or changes any movement trace. It remains deferred beyond the three-job feel
gate.

Visual mockup: `concepts/ITERATION_03_REPRISE_ALLOY_SECOND_DRAFT.svg`  
SHA-256: `bd428b62f9fcb17d1f4f9cecae496c16094c0fa6bd6c64d9cac3057b29131cf1`

## Deterministic evidence

Command:

```text
PYTHONPATH=tools python3 -B tools/test_iteration_03_pace_grade.py \
  --report analysis/ITERATION_03_PACE_GRADE_REPORT.json
```

Result: `83/83 PASS`.

Report SHA-256:
`221693c6f61a3b04c19674480fac2bf2187a516f6742f93416455affbcfbc141`

The vectors cover every curve anchor, interpolation, one-tick continuity,
global monotonicity/bounds, scale invariance, invalid observations, exact HUD
copy, nine grade scenarios and every condition gate, grade/payout independence,
exact-sum receipts, calibration median/rounding/clean-evidence gates, session
best ordering, one award, neutral-gated Continue, authorized explicit restart,
and active-reset idempotence.

The report was regenerated byte-identically. These pure checks do not establish
fair human reference times, native UI comprehension, relocation feel, paint
legibility, trail occlusion, or exact Godot input/reset ordering.

## Human falsifiers

Stop before expanding the slice if any is true:

1. after two receipts Charlie cannot explain delivery + condition + pace in
   about five seconds;
2. `BONUS EASING/ENDED` reads as failure or suppresses the enjoyable long drift;
3. a comfortable clean reference run does not tend A, or S feels routine;
4. a legitimate C03 alternative is capped below B by time alone;
5. the visible component lines differ from the award by one Credit;
6. Continue changes position, auto-opens a board, or leaks a held input;
7. Restart surprises once, carries attempt state, duplicates an award, or
   starts driving without fresh Dispatch/Accept;
8. a C02/C03 active reset returns to the wrong origin or makes the player stop
   retrying;
9. `SESSION BEST RECEIPT` is still interpreted as fastest-only; or
10. reset and delivery on one tick show any mixed terminal presentation.

No product file was changed. R7 remains read-only.
