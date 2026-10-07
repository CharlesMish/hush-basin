# CLEAN SCRIPT — A Flat He Didn't Make (PART 1 only, from draft-2.md · PROPOSED, not canon)

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
