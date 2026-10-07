# A Flat He Didn't Make — Ivo narrative-slice PROPOSAL

Run `ivo-slice-20261006-01` · writer turn 2 (revision 1) · writer: Claude Sonnet 5.5 (`claude-sonnet-5-5`)
Revises `draft-0.md` (sha256 `2931de462b8d88f5edc1120892b93842f9beee9ef5d82dfaa7678fd293307670`) after `review-0.md` (sha256 `9e07258020111c1575971f63fa1f75126f27626987690a60afaab00eb936f2ec`, READY WITH MINOR NOTES, no blockers).
**This revision changes no script text, leg, state or implementation claim.** The only edits are this header, review-ID tags on the open decisions in §2.9, and the change record at the end. Scenes 1–7, tickets, notes, receipts and Parts 1–2.1–2.8 are word-for-word the original.
Checkout: tooling `05d55064a1013483b869dba0bc9d2d1906a24b6b`; implemented game `5be7feeef34dbed468e007f5ff4de594d41b0f80`.

**Status: PROPOSED. Nothing below is canon or implemented.** Every name, line, fact and prop here is new unless it is quoted from the game.

Follows: Chapters 2 and 3 complete (`Slice.chapter_three_complete`). Cast: Ivo, Bea. Anonymous: Depot receiving. Ren, Tess and Nell do not appear and are not mentioned.

**In one paragraph.** Depot's seal press has been striking half a seal for a month. Its dies go to Ivo to be re-faced. He can do it in an hour, but he won't trust his own bench plate, which he made and knows is hollow. He wants a flat he didn't make, so he lends the courier his straightedge to carry to Quarry. Bea tests it against her stone and sends back an offcut with instructions for seating it. Ivo checks the stone, works on the dies while the courier is away, and the dies go back to Depot. Four counted legs. One persistent trace: a pale stone plate on three feet on Ivo's bench.

---

# PART 1 — PLAYABLE SCRIPT

## 1.1 Order and dependencies

Each step is open only once the one before it has been delivered, because the chain follows one object. Ordinary work is available the whole time.

| # | Where | What | Kind | Requires |
| --- | --- | --- | --- | --- |
| 1 | Depot | Pickup scene (no face): **Seal press dies** | Offer, counted leg 1 start | Chapter 3 complete |
| 2 | Works | Ivo, hosted by leg 1's arrival | Cargo-neutral scene | Leg 1 delivered |
| 3 | Works | Pickup scene (no face): **Steel straightedge** | Offer, counted leg 2 start | Leg 1 delivered |
| 4 | Quarry | Bea, hosted by leg 2's arrival | Cargo-neutral scene | Leg 2 delivered |
| 5 | Quarry | Pickup scene (no face): **Dressed offcut** | Offer, counted leg 3 start | Leg 2 delivered |
| 6 | Works | Ivo, hosted by leg 3's arrival | Cargo-neutral scene | Leg 3 delivered |
| — | (off-screen) | Ivo re-faces the dies while the courier is away | Physical state change | Leg 3 delivered, then courier >90 m from Works |
| 7 | Works | Ivo pickup scene: **Re-faced press dies** | Offer, counted leg 4 start | Step 6 state change |
| 8 | Depot | Anonymous receipt (no scene) | Leg 4 arrival | Leg 4 delivered |

## 1.2 The four counted legs

Pay is within the existing 100–140 range. No timer, condition gate or objective. Highlighted roads are suggestions only; any legal route completes.

| Leg | Pickup → destination | Cargo (one parcel) | Suggested highlight |
| --- | --- | --- | --- |
| 1 | Depot → Works | Seal press dies (a wrapped pair) · base 120 | L1, L6 (service-bar choice stays) |
| 2 | Works → Quarry Stores | Steel straightedge · base 100 | −R0, −L4, −X0: north gate, past Relay, along the Quarry Shelf. It is light cargo and gets the scenic technical line. |
| 3 | Quarry Stores → Works | Dressed offcut with the straightedge strapped on top (one parcel, like "two kneeling pads") · base 140 · "Heavy." | A0, L0, L1, L6: smooth streets for the stone. |
| 4 | Works → Depot | Re-faced press dies · base 120 | None highlighted. The player picks the line. |

## 1.3 Text

Format follows the existing slices. A scene's first panel is paper (a carried note) where marked. Text in quotation marks is spoken by the portrait. Apostrophes are straight, as in `slices_text.gd`.

### Scene 1 — `dies_offer` · Depot · no face

Pickup label (automatic): *Pickup: Depot → Works*

> Collection at Depot receiving: one pair of seal-press dies, wrapped, for Works.
>
> **Carried note.** DEPOT RECEIVING · Press has struck half a seal for a month. Dies look sound; faces don't meet. Works to re-face and return. We're on the hand stamp meanwhile.

Buttons: *Accept delivery* / *Not now*. Nothing else is said at Depot.

### Scene 2 — `ivo_dies` · Works · Ivo · arrival of leg 1

Receipt footer: *Seal press dies delivered · Payment +120 received*. Heading: IVO · Fabrication.

1. *(paper, heading "DEPOT'S NOTE · carried with the dies")* Press has struck half a seal for a month. Dies look sound; faces don't meet. Works to re-face and return. We're on the hand stamp meanwhile.
2. "Worn hollow. They meet at the rim and nowhere else."
3. "An hour on a true plate and they'd close. Mine's the trouble. I made it, and it's got a hollow of its own."
4. "Anything I true on it, I'm only agreeing with myself. I want a flat I didn't make. Depot's managed a month. It'll keep."
5. "Quarry dresses stone. I'll send my edge to check it against. It doesn't leave the bench, as a rule. You carried the receiver. I'll trust you with a bar of steel."

Summary (shown after the last panel or after Skip): *Seal dies received at Works.* + Carried note. No offer in this scene; the pickup is separate.

### Scene 3 — `edge_offer` · Works · no face

Pickup label: *Pickup: Works → Quarry Stores*

> Collection at Works: one steel straightedge for Quarry Stores. Ask for whoever dresses the stone.
>
> **Carried note.** Quarry Stores — I need one flat I didn't make: a dressed offcut small enough to carry, true to this edge. If light shows under it anywhere I'd rather go without. Edge comes back with it. —Ivo, Works

### Scene 4 — `bea_edge` · Quarry · Bea · arrival of leg 2

Heading: BEA · Quarry Stores.

1. *(paper, heading "IVO'S NOTE · carried with the straightedge")* Quarry Stores — I need one flat I didn't make: a dressed offcut small enough to carry, true to this edge. If light shows under it anywhere I'd rather go without. Edge comes back with it. —Ivo, Works
2. "He's sent his own edge to check my stone."
3. "Lamp low behind it. That face, light at the left. That one, at the right."
4. "End for end, same both times. Somebody checked this twice."
5. "This one's clear to both ends. Offcut from the Clinic stone, same lift."

Summary: *Straightedge received at Quarry Stores.* + Carried note.

### Scene 5 — `offcut_offer` · Quarry · no face

Pickup label: *Pickup: Quarry Stores → Works*

> Collection at Quarry Stores: one dressed offcut for Ivo at Works, his straightedge strapped on top. Heavy.
>
> **Carried note.** Offcut from the Clinic stone. Edge strapped on top. Three feet under it, not a bench: on four it rocks, on a bench it takes the bench's shape. —B

### Scene 6 — `ivo_stone` · Works · Ivo · arrival of leg 3

1. *(paper, heading "BEA'S NOTE · carried with the offcut")* Offcut from the Clinic stone. Edge strapped on top. Three feet under it, not a bench: on four it rocks, on a bench it takes the bench's shape. —B
2. "Three feet. I'd have laid it on the bench."
3. "Edge on, lamp behind. Not a hair. End for end. Not a hair."
4. "Now mine. There. You could read by that."
5. "Years I've worked to that plate. Come back after you've been somewhere. This takes what it takes."

Summary: *Offcut and straightedge received at Works.* + Carried note.

**What the player sees:** the pale slab is on the bench on three small feet, with the dies on it. There is no wait screen. The player simply drives away.

### Scene 7 — `faced_offer` · Works · Ivo · pickup

Opens from the dispatch board once Ivo has finished (see §1.4). Short pickup scene with a face, like Bea's first two. Heading: IVO · Fabrication.

1. "Done. Hold them face to face. No, you'd want the lamp. Take my word."
2. "I could keep going. It stops being for Depot about here."
3. "Nobody there will lay an edge on them. They'll just stop getting half a seal."

Pickup label: *Pickup: Works → Depot*

> Collection at Works: one pair of seal-press dies, re-faced, for Depot receiving.
>
> **Carried note.** DEPOT RECEIVING — Re-faced and checked to a dressed stone. They'll seat flat; the press should strike whole. —Ivo, Works

### Leg 4 arrival — Depot · anonymous receipt, no scene

Ordinary receipt panel: *Re-faced press dies delivered · Payment +120 received*

> Dies received. First seal struck whole, edge to edge. Press is back in use.

That is the end. Nobody tells Ivo or Bea. There is no next offer, no promise and no cliffhanger.

## 1.4 Physical states

| State | Trigger | Where seen | Persistence |
| --- | --- | --- | --- |
| Dies, dull, lying on Ivo's bench | Leg 1 delivered | Works bench, normal arrival view | Until leg 4 is accepted |
| Pale stone plate on three small feet, the dies on it | Leg 3 delivered | Same | **Permanent.** The plate stays after the dies leave. |
| "Re-faced" offer appears at Works | Leg 3 delivered, then courier >90 m from Works (same departure rule as Clinic installation and Quarry bedding) | Dispatch board; resume sentence | Until accepted |
| Dies gone from bench | Leg 4 accepted | Works bench | — |
| Depot press striking whole | Leg 4 delivered | Receipt text only | No Depot prop |

Quarry gets no trace. The straightedge returns to Ivo inside leg 3, so there is no Quarry prop either.

New physical state at the stopping point: a pale stone plate on three feet on Ivo's Works bench. No availability change beyond that; nothing new unlocks.

## 1.5 Cargo-neutral vs counted

- **Counted paid legs: 4.** Dies to Works. Straightedge to Quarry. Offcut to Works. Re-faced dies to Depot.
- **Cargo-neutral:** Scene 2, Scene 4 and Scene 6 are hosted by those legs' own arrivals. Scene 7 is part of a pickup. No extra trips exist for conversation.

---

# PART 2 — IMPLEMENTATION APPENDIX

## 2.1 Availability

- Gate: `chapter_three_complete(r)`, which needs `relined_sleeve` done, `bea_red` seen and `ren_letter` done. It does **not** need `ivo_return` or any other optional line.
- Chain, same `elif` style as `Slice.available`: `press_dies`; then `ivo_edge` once `press_dies` is done; then `flat_offcut` once `ivo_edge` is done; then `faced_dies` once `flat_offcut` is done and the new boolean `faced` is true.
- The offer must be accepted at its own origin (`nearby_hub()==origin`), after the neutral-release barrier. Advance and Skip never accept.
- Each arrival scene is recorded as `pending` after settlement and is reopened at the real contact if the game is closed mid-scene. A job's next offer is not shown until that arrival scene has been resolved.
- Ordinary Works, Depot and Quarry jobs stay on the board throughout. Only one slice offer exists at a time.
- Reset Story clears everything.

## 2.2 Who learns what, and how

| Fact | Learner | Channel |
| --- | --- | --- |
| Depot's press strikes half a seal; the dies' faces don't meet | Ivo | Depot's note carried with the dies |
| Ivo wants a flat he didn't make; he is lending his edge | Bea | Ivo's note carried with the straightedge, plus the edge itself |
| Bea's stone passes his edge; how to seat it | Ivo | Bea's note carried with the offcut |
| Dies re-faced and checked to a stone | Depot | Ivo's note carried with the dies |
| First seal was whole | Player only | Depot's receipt text |

No receipt in this slice posts a new request, so the existing finite receipt-to-request channel is not used. There are no reply trips: nothing tells Ivo how the seal came out and nothing tells Bea what the stone did.

Ivo and Bea know each other only through these two notes, a tool and a stone. The draft does not claim friendship.

## 2.3 Postponement and resume

Resume sentences use the existing wording style, naming actual cargo, place and action:

- Slice not started: "Depot has seal-press dies for Works. Collect them at Depot."
- Dies aboard (quit and relaunch): "Seal press dies aboard. Deliver to Works." The existing checkpoint restores the position at rest.
- Dies delivered, straightedge not accepted: "Ivo has a straightedge for Quarry Stores. Collect it at Works." The payment already landed. Declining never undoes it.
- Straightedge delivered, offcut not accepted: "Quarry Stores has a dressed offcut for Ivo. Collect it at Quarry."
- Offcut delivered, courier still near Works: "Ivo is re-facing Depot's dies while you're away."
- After departing >90 m: "Ivo has re-faced Depot's dies. Collect them at Works."
- Complete: "Depot's press is striking whole again. Ivo's stone plate is on his bench. Ordinary paid work continues."

Example. A player takes the dies, then does an ordinary Market job first. Nothing is lost and no clock runs. A player who skips Scene 2 still gets the full offer context at Scene 3: the pickup summary carries Ivo's note, and Scene 6's summary carries Bea's seating instruction.

## 2.4 Rule checks

- **Portrait locality.** Ivo only at Works, Bea only at Quarry. Depot is an institution and has no face.
- **Player-advanced, Skip.** All panels advance on input. Skip lands on the summary that holds the note and the offer.
- **One active parcel.** Straightedge and offcut are a single named parcel, as with the kneeling pads. Nothing is carried alongside a second cargo.
- **Any legal route.** Highlights are suggestions only. The suggested legs 2 and 3 take deliberately different lines. The implementer may drop the −R0/−X0 highlight if the technical edges prove unfriendly.
- **No emergency.** Depot is on a hand stamp. That is an inconvenience, not an emergency, and Ivo says so himself: "It'll keep."
- **Face vocabulary.** "Face" appears only for die faces and the stone's dressed surface. No handling instruction, no PLAIN/RED echo. Bea's seating rule is the only instruction.

## 2.5 Implementation cost (honest)

No new system. This reuses the existing job, scene, `pending`, paper-panel, checkpoint and departure-flag primitives.

- **Text/data.** Four `JOBS`, seven `SCENES` and three reaction strings. `HEADINGS` has no `ivo` entry (`slices_text.gd` lists bea, nell, tess and ren only), so a one-line addition is needed. `ivo.png` already exists.
- **Save validation (largest risk).** `slices_store.gd` whitelists done IDs, requires exact `slices` sizes of 3 or 5, and encodes dependency rules. This needs four new done IDs, one new boolean `faced`, a 5→6 key migration like the earlier 3→5 one, and four dependency rules. Validation also needs to require that chapter 3 is complete.
- **Director.** An `available()` branch, a `faced` flag set in `_process` on the same >90 m pattern as `installed`/`bedded`, and extended `resume_sentence` / `chapter_three_resume`.
- **Props.** The plate is four boxes (slab plus three feet), placed on the Works bench via the existing `works` anchor root. It shows when `flat_offcut` is done. The dies are about two boxes, shown from `press_dies` done until `faced_dies` is accepted. No collision, camera or physics change.
- **Unverified.** Whether a pale slab on the Works bench reads at the normal arrival view is a playtest question. If it doesn't, the fallback is a lamp or a slightly larger plate. Nothing else depends on it.

## 2.6 Proposed canon additions (conditional on Charlie)

- Depot presses its own freight seals, using dies. (The ordinary Market→Depot "freight seals" job supplies the blanks.)
- Ivo's bench plate is his own make and had a hollow. He keeps a steel straightedge he doesn't normally lend. His private standard is to check against a flat he didn't make.
- Bea can test steel against stone, and respects a tool that has been checked twice.
- A pale offcut from the Clinic stone is now a plate on three feet on Ivo's bench.
- Ivo and Bea are acquaintances through notes only. No meeting is shown.

## 2.7 Deliberately left alone

Ren, Tess, Nell and Stop 9. The chair and its crate. Ivo's hinges. `ivo_return`. The sleeve patch. Nell's refusal. No new portrait, road, district, upgrade or progression. The kettle, rope and corner details stay ordinary.

## 2.8 Weak points

- **Leg 1 is the weakest bridge.** It carries the problem to Ivo. Without it, the dies would need an unwitnessed delivery or another carrier, which is an invented fact. Four legs is the smallest honest count. Dropping the stone loop leaves a private bench errand; dropping the dies leaves no stake.
- **Star geometry.** All four legs touch Works. Variety comes from the Depot/Quarry endpoints and from the deliberately different suggested lines, not from new places.
- **Technical talk.** "Flat" and "light under the edge" carry the idea. If the Examiner finds it too much, cut panel 3 of Scene 2 first.

## 2.9 Unresolved decisions

1. May Depot own a seal press? It is a small invented fact about an existing institution. *(Review R0-N1: Charlie's decision.)*
2. Are four legs acceptable, or should leg 1 or 4 be reworked? *(R0-N2, R0-N3: Charlie's decision. Note that all four legs touch Works; this is a Works-centred slice, not city-wide coverage.)*
3. Is the plate-on-three-feet prop acceptable, with the dies prop optional? *(R0-N6.)*
4. Pay values (120 / 100 / 140 / 120) are placeholders.
5. Keep "You carried the receiver" in Scene 2? It acknowledges the courier's earlier work without citing condition.
6. Should the R0/X0 highlight on leg 2 stay, or should leg 2 also have no highlight? *(R0-N4 confirms the roads are legal.)*

---

# CHANGE RECORD (revision 1)

| ID | Disposition | Note |
| --- | --- | --- |
| R0-N1 | Needs human direction | Depot seal press stays marked as an invented fact (§2.6, §2.9.1). |
| R0-N2 | Needs human direction | Leg 1 kept. No smaller chain exists without inventing an unwitnessed delivery. |
| R0-N3 | Adopted as a review flag | Star geometry is stated in §2.8 and now in §2.9.2. No change to the design. |
| R0-N4 | No change needed | Routes confirmed legal. Highlights stay suggestions. |
| R0-N5 | Disputed | Scene 3 ticket keeps "Ask for whoever dresses the stone." See `findings-response-1.md`. |
| R0-N6 | No change needed | Costs and the open playtest question are already stated in §2.5. |

New canon claims: none beyond §2.6 in the original. State changes: none beyond §1.4 in the original.
