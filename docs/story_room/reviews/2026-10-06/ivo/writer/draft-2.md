# A Flat He Didn't Make — Ivo narrative-slice PROPOSAL (repair revision 2)

Run `ivo-grok-repair-20261006-01` · writer turn 2 (first of at most two repairs) · draft-2 · writer: Grok Bot
Revises `writer/draft-1.md` (sha256 `21a74821fd6fc5444cb51a4614c33e0c688f16f223a9de4661ce7a962ec63ce3`, untouched) per Astra review `astra/astra-review-draft-1.md` (sha256 `364f1e348a6c5a33b0f63955c2ed978e8a3d6050d7b5d1a684861fd47eaad630`). The keyed R1–R4 response is in `RESPONSE_R1-R4.md`.
Checkout: tooling `05d55064a1013483b869dba0bc9d2d1906a24b6b`; implemented game `5be7feeef34dbed468e007f5ff4de594d41b0f80`.

**Status: PROPOSED. Nothing below is canon or implemented, and Astra has not accepted this revision.** Every name, line, fact and prop is new unless it is quoted from the game.

This slice follows Chapters 2 and 3 (`Slice.chapter_three_complete`). Cast: Ivo and Bea, with Depot receiving left anonymous. Ren, Tess and Nell do not appear and are not mentioned.

**In one paragraph.** For a month, Depot's seal press has been striking half a seal, so the dies go to Ivo. The plain die has worn low on one side. Re-facing it is easy. Knowing when it's flat is the job, and his own bench plate has ordinary wear where he works. Checking against it would only agree with his hand, so he lends the courier his straightedge to take to Quarry. Bea checks offcuts against the edge, picks one from the Clinic stone and sends it back with the edge strapped on top. On that same Works visit, Ivo seats the stone on three feet and checks it. He then re-faces the plain die, checks it against the stone, and the dies go back to Depot. The slice has four counted legs and leaves one lasting trace: a pale stone plate on three feet on Ivo's bench.

---

# PART 1 — PLAYABLE SCRIPT

## 1.1 Order and dependencies

The chain follows one object, so each step opens only after the one before it. Ordinary work stays on the board the whole time under the one-active-parcel rule. None of it is required.

| # | Where | What | Kind | Requires |
| --- | --- | --- | --- | --- |
| 1 | Depot | Pickup, no face: **Seal press dies** | Offer; leg 1 | Chapter 3 complete |
| 2 | Works | Ivo, hosted by leg 1's arrival | Arrival scene | Leg 1 delivered |
| 3 | Works | Pickup, no face: **Steel straightedge** | Offer; leg 2 | Scene 2 resolved |
| 4 | Quarry | Bea, hosted by leg 2's arrival | Arrival scene | Leg 2 delivered |
| 5 | Quarry | Pickup, no face: **Dressed offcut** | Offer; leg 3 | Scene 4 resolved |
| 6 | Works | Ivo, hosted by leg 3's arrival (offcut paid first) | Arrival scene | Leg 3 delivered |
| 7 | Works | Ivo, pickup with face: **Re-faced press dies**. Same visit, straight after Scene 6. | Offer; leg 4 | Scene 6 resolved |
| 8 | Depot | Anonymous receipt, no scene | Leg 4 arrival | Leg 4 delivered |

Scenes 6 and 7 play on one Works visit. The offcut settles and pays first. Ivo seats and checks the stone in Scene 6. When the player advances into Scene 7, its first panel is Ivo's finished note for Depot. That paper panel is the whole time ellipsis: the work has happened by the time the player reads it. There is no wait, timer, departure gate, cutscene or intervening job. The return offer follows as its own Accept / Not now.

## 1.2 The four counted legs

Pay is fixed: 120 / 100 / 140 / 120. No timer, condition gate or objective. Any legal route completes. The highlighted routes are advisory suggestions only, and the implementer may drop either one.

| Leg | Pickup → destination | Cargo (one parcel) | Pay | Suggested highlight (advisory) |
| --- | --- | --- | --- | --- |
| 1 | Depot → Works | Seal press dies (a wrapped pair) | 120 | L1, L6 (service-bar choice stays) |
| 2 | Works → Quarry Stores | Steel straightedge | 100 | Scenic outbound: −R0, −L4, −X0, north gate, past Relay, along the Quarry Shelf. Light cargo, technical line. |
| 3 | Quarry Stores → Works | Dressed offcut with the straightedge strapped on top. Heavy. | 140 | Smoother return: A0, L0, L1, L6 |
| 4 | Works → Depot | Re-faced press dies | 120 | None. The player picks the line. |

## 1.3 Text

The format follows the existing slices. A scene's first panel is paper (a carried or written note) where marked. Text in quotation marks is spoken by the portrait. Apostrophes are straight.

### Scene 1 — `dies_offer` · Depot · no face

Pickup label: *Pickup: Depot → Works*

> Collection at Depot receiving: one pair of seal-press dies, wrapped, for Works.
>
> **Carried note.** DEPOT RECEIVING · Press has struck half a seal for a month. Works to look the dies over and send them back. We're on the hand stamp meanwhile.

Buttons: *Accept delivery* / *Not now*.

### Scene 2 — `ivo_dies` · Works · Ivo · arrival of leg 1

Receipt footer: *Seal press dies delivered · Payment +120 received*. Heading: IVO · Fabrication.

1. *(paper, heading "DEPOT'S NOTE · carried with the dies")* DEPOT RECEIVING · Press has struck half a seal for a month. Works to look the dies over and send them back. We're on the hand stamp meanwhile.
2. "Lettered die's fine. The plain one's worn low on one side. Press closes and only half the seal takes."
3. "Re-facing it is the easy part. Knowing when it's flat is the job. My plate's worn where I work. Ordinary wear. Fine for ordinary iron. Not for this."
4. "Anything I check on it, I'm only agreeing with myself. I want a flat I didn't make. Depot's managed a month. It'll keep."
5. "Quarry dresses stone. I'll send my edge to check it against. It doesn't leave the bench, as a rule. You carried the receiver. I'll trust you with a bar of steel."

Summary (after the last panel or after Skip): *Seal dies received at Works.* + carried note. This scene has no offer. The pickup is separate.

### Scene 3 — `edge_offer` · Works · no face

Pickup label: *Pickup: Works → Quarry Stores*

> Collection at Works: one steel straightedge for Quarry Stores. Ask for B.
>
> **Carried note.** Quarry Stores — I need one flat I didn't make: a dressed offcut small enough to carry, true to this edge. If light shows under it anywhere I'd rather go without. Edge comes back with it. —Ivo, Works

### Scene 4 — `bea_edge` · Quarry · Bea · arrival of leg 2

Receipt footer: *Steel straightedge delivered · Payment +100 received*. Heading: BEA · Quarry Stores.

1. *(paper, heading "IVO'S NOTE · carried with the straightedge")* Quarry Stores — I need one flat I didn't make: a dressed offcut small enough to carry, true to this edge. If light shows under it anywhere I'd rather go without. Edge comes back with it. —Ivo, Works
2. "He's sent his own edge to check my stone."
3. "Edge across, lamp low behind. That one shows light under the middle. Not that."
4. "This one. Along, across, corner to corner. No light."
5. "Offcut from the Clinic stone. That'll do him. His edge goes home on top of it."

Summary: *Straightedge received at Quarry Stores.* + carried note.

### Scene 5 — `offcut_offer` · Quarry · no face

Pickup label: *Pickup: Quarry Stores → Works*

> Collection at Quarry Stores: one dressed offcut for Ivo at Works, his straightedge strapped on top. Heavy.
>
> **Carried note.** Offcut from the Clinic stone. No light under your edge, along, across or corner to corner. Edge strapped on top. —B

### Scene 6 — `ivo_stone` · Works · Ivo · arrival of leg 3

Receipt footer: *Dressed offcut delivered · Payment +140 received*. The payment lands before any panel. Heading: IVO · Fabrication.

1. *(paper, heading "BEA'S NOTE · carried with the offcut")* Offcut from the Clinic stone. No light under your edge, along, across or corner to corner. Edge strapped on top. —B
2. "Off the bench. Three feet under it."
3. "Edge on, lamp behind. Not a hair."
4. "Now mine. There. You could read by that."
5. "Nothing gets worked on this. It only tells me when to stop."

Summary: *Offcut and straightedge received at Works.* + carried note.

**What the player sees:** the pale slab is on the bench on three small feet, and the plain die lies on it. Resolving the scene (by the last panel or Skip) hands straight on to Scene 7 at the same contact. The player doesn't drive anywhere first.

### Scene 7 — `ivo_done` · Works · Ivo · pickup with face (leg 4 offer)

This is a pickup scene with a face, the same shape as Bea's pickups. Its first panel is paper. Heading: IVO · Fabrication.

1. *(paper, heading "IVO'S NOTE · for Depot, with the dies")* DEPOT RECEIVING — Plain die re-faced and checked to a dressed stone. Lettered die untouched. The press should strike whole. —Ivo, Works
2. "Done. Sat it on the stone, lamp behind. No light under it."
3. "I could keep going. It stops being for Depot about here."
4. "Nobody there will lay an edge on them. They'll just stop getting half a seal."

Pickup label: *Pickup: Works → Depot*

> Collection at Works: Depot's seal-press dies, re-faced, for Depot receiving.
>
> **Carried note.** DEPOT RECEIVING — Plain die re-faced and checked to a dressed stone. Lettered die untouched. The press should strike whole. —Ivo, Works

Buttons: *Accept delivery* / *Not now*. Advance and Skip land on this offer summary (finished work plus offer) and never accept. Not now leaves the offer at Works. The player can do any ordinary work, or none, and collect the dies on any later Works visit.

### Leg 4 arrival — Depot · anonymous receipt, no scene

Receipt: *Re-faced press dies delivered · Payment +120 received*

> Dies received. First seal struck whole, edge to edge. Press is back in use.

That is the end. Nobody tells Ivo or Bea. There is no next offer, promise or cliffhanger.

## 1.4 What stays

A pale stone plate on three feet stays on Ivo's Works bench permanently. The dies lie on the bench from leg 1 and leave when leg 4 is accepted. Quarry and Depot get no prop.

---

# PART 2 — COMPACT APPENDIX

## 2.1 Availability and state

- **Gate:** `chapter_three_complete(r)`. It does not need `ivo_return` or any optional line.
- **Chain** (same `elif` style as `Slice.available`): `press_dies`. Then `ivo_edge` once `press_dies` is done. Then `flat_offcut` once `ivo_edge` is done. Then `dies_return` once `flat_offcut` is done **and** `r.pending != "ivo_stone"`. No new boolean and no departure flag.
- **Same-visit handoff:** once Scene 6 resolves, `dies_return` is available at Works. Its pickup scene `ivo_done` then presents at the current contact like any face pickup. Acceptance still needs the origin (`nearby_hub()==origin`), the neutral-release barrier and a fresh Accept input.
- **Quit/relaunch:** quitting during Scene 6 leaves `pending = "ivo_stone"`. That pending exchange reopens at the Works contact and then hands on to Scene 7. Quitting during Scene 7, or choosing Not now, leaves the offer open. Scene 7 presents again at the Works contact, as a lighter repeat.
- **Save:** whitelist four new done IDs (`press_dies`, `ivo_edge`, `flat_offcut`, `dies_return`) and add dependency rules for them, including chapter 3 complete. No new flag means no slices-key migration is expected. Confirm this against `slices_store.gd` size checks. Reset Story clears everything.
- **Ordinary work:** Works, Depot, Market and Quarry jobs stay on the board throughout, one active parcel at a time. Ordinary work can happen before a slice offer is accepted or after the current parcel settles, never alongside it. Nothing in the slice asks for it.

## 2.2 Resume sentences

- Not started: "Depot has seal-press dies for Works. Collect them at Depot."
- Dies aboard: "Seal press dies aboard. Deliver to Works."
- Dies delivered: "Ivo has a straightedge for Quarry Stores. Collect it at Works."
- Straightedge delivered: "Quarry Stores has a dressed offcut for Ivo. Collect it at Quarry."
- Offcut aboard: "Dressed offcut aboard. Deliver to Works."
- Offcut delivered, Scene 6 pending: the existing pending-handoff wording returns the player to the Works contact.
- Scene 6 resolved, dies not accepted: "Ivo has re-faced Depot's dies. Collect them at Works."
- Re-faced dies aboard: "Re-faced press dies aboard. Deliver to Depot."
- Complete: "Depot's press is striking whole again. Ivo's stone plate is on his bench. Ordinary paid work continues."

## 2.3 Physical states

| State | Trigger | Where | Persistence |
| --- | --- | --- | --- |
| Dies on Ivo's bench | Leg 1 delivered | Works bench | Until leg 4 accepted |
| Pale stone plate on three small feet, plain die on it | Leg 3 delivered | Works bench | **Permanent** |
| Dies gone | Leg 4 accepted | Works bench | — |
| Press striking whole | Leg 4 delivered | Receipt text only | No Depot prop |

## 2.4 Who learns what

| Fact | Learner | Channel |
| --- | --- | --- |
| The press strikes half a seal | Ivo | Depot's note with the dies |
| Ivo wants a flat he didn't make and lends his edge | Bea | Ivo's note plus the edge |
| Which offcut passed and how it was checked | Ivo | Bea's note with the offcut |
| Plain die re-faced and checked to a stone | Depot | Ivo's note with the dies |
| First seal was whole | Player only | Depot's receipt |

Nothing tells Ivo how the seal came out or tells Bea what the stone did. The receipt-to-request channel is not used. Current canon (`CHARACTER_LEDGER`) leaves Ivo/Bea familiarity unspecified, and none is shown or required.

## 2.5 Rule checks (short)

Faces appear only at home: Ivo at Works, Bea at Quarry. Depot has no face. All panels are player-advanced. Skip lands on the summary, and on Scene 7 that is the finished-work and offer summary, so Skip never accepts. Straightedge plus offcut is one parcel, like the "two kneeling pads". Any legal route completes. There is no emergency: "It'll keep." There is no fifth job, timer or gate.

## 2.6 Implementation cost

No new system is needed. The slice reuses the existing job, scene, `pending`, paper-panel, checkpoint and done-ID primitives.

- **Text/data:** four `JOBS` and seven `SCENES`. `HEADINGS` needs an `ivo` entry (`IVO · Fabrication`); `ivo.png` already exists.
- **Build checks:** first, whether a face pickup scene with `paper_panels:1` (Scene 7) composes as cleanly as the existing face pickups and the paper-first arrival scenes. Second, whether the next pickup scene presents at the same contact straight after an arrival scene resolves. If it needs one board tap, that is acceptable: it is still the same visit with no driving.
- **Props:** the plate is four boxes (a slab plus three feet) on the `works` anchor, shown from `flat_offcut` onward. The dies are about two boxes. No collision, camera or physics change. Whether the slab reads at the normal arrival view needs a playtest; the fallback is a lamp or a slightly larger plate.

## 2.7 Source check and what stays fiction (R3)

- **Press part:** Bulldog seal presses take two interchangeable ½" dies held by a set screw, sold *plain* (blank), *recessed* (for lead) or *raised* (for aluminum) ([seals.com/5-bulldog-seal-press](https://seals.com/5-bulldog-seal-press/); [replacement dies](https://seals.com/replacement-dies-for-the-5-bulldog-seal-press/)). So a press with a replaceable die pair that includes a plain die is credible.
- **Reference and wear:** Starrett asks for frequent inspection of plates in shop use. A worn plate "can be transferred to work involving less accuracy or ... resurfaced" ([Starrett catalog p.411](https://www.starrett.com/dms/flipbooks/Cat-33/inc/html/411.html)). Starrett specifies defined support points, three or four per ASME B89.3.7 ([Starrett granite note](https://www.starrett.com/news-events/what-you-need-to-know-about-precision-granite-inspection-products)). Ivo's "three feet" is the simple version of this.
- **Checking vs. working:** Kemet treats the lapping plate (the working surface) as something that wears and is itself checked against a known flat or a straightedge ([Kemet lapping-plate flatness](https://www.kemet.co.uk/blog/lapping/lapping-plate-flatness-maintenance-procedures)). The draft follows that split: the stone only checks, and Ivo does the re-facing his own way, unspecified.
- **Still fiction or inference:** Depot owning a press; one lettered die paired with one plain die (the sources show plain dies as an option, not this pairing); one-sided wear giving "half a seal"; a dressed quarry offcut being flat enough to check against (real reference plates are lapped and graded); and lamp-behind-straightedge as the check. That last one is ordinary shop practice, but no measurement is claimed.

## 2.8 Proposed canon additions (conditional on Charlie / Astra)

- Depot owns a small seal press for its own tags and seals. This is separate from the ordinary Market → Depot **Freight seals** job, which delivers finished seals.
- The press has one lettered die and one plain die. The plain die wore low on one side and is re-faced; the lettered die is left untouched.
- Ivo's bench plate has ordinary wear where he works. He keeps a straightedge he doesn't normally lend.
- A pale offcut from the Clinic stone is now a checking plate on three feet on Ivo's bench.

## 2.9 Weak points

- **Leg 1 is the weakest bridge.** It carries the problem to Ivo. The dies could arrive off-screen instead. Four witnessed legs is our chosen bounded proposal, not the only possible design.
- **Star geometry.** All four legs touch Works. Variety comes from the Depot and Quarry endpoints and the advisory scenic and smooth lines.
- **Ellipsis.** The only time skip is one paper panel. If playtest finds it abrupt, the fallback stays inside existing grammar: one more Ivo line in Scene 6. Never a wait.

Deliberately left alone: Ren, Tess, Nell, Stop 9, the chair and crate, Ivo's hinges, `ivo_return`, the sleeve patch and Nell's refusal. The slice adds no portrait, road, district, upgrade or progression.
