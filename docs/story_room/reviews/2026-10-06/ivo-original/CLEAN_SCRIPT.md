# Clean playable script — A Flat He Didn't Make

Extracted from revision-1.md (PART 1 only). Status: PROPOSED.

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

