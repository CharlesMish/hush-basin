# World and route story map

Baseline/status: [current canon](STORY_CANON_CURRENT.md). Coordinates below are
world `(x,z)` metres: east is +x, south +z. They locate contacts, not houses that
the craft should touch. Story completion accepts any legal route. Highlighted
roads are fixed advisories, not a shortest-path solver or mandatory itinerary.

## Places and actual stopping points

| Place / contact | What is physically there and who belongs here | Driving and writing cautions |
| --- | --- | --- |
| Market MRK `(0,20)`, radius 8 m | Central dispatch; anonymous opening mail lead; ordinary catalog. Nell's hatch is offset `(6,-7)` from the pad, at `(6,13)`. Persistent return crate, visit-specific food props. | Street hub joining the spine, Depot/Clinic belt and Works way. Market's dispatch is not Nell's food service. Ren no longer appears here. |
| Works WRK `(90,-55)`, radius 8 m | Ivo's fabrication anchor is `(95,-59)`: bench, prepared receiver, chair/crate. Industrial frontage/stacks nearby. | L6 from Market, L7 from East Gate, R0 from North Gate. Retained service bar on L6 gives Spread/Hop or bypass choice. Do not obstruct that line or put Ivo at the wrong building sign. |
| Relay RLY `(0,-210)`, radius 8 m | Ren's desk is `(5,-214)`, receiver/bracket/indicator, rack, mail, later letter. | Controlled northern arrival; L4 spine and both outer approaches. This is not the distant mast at `(0,-285)` and not inland B02's RELAY SERVICE frontage. The mast/annex is background evidence, not the portrait contact. |
| Depot DEP `(-110,75)`, radius 8 m | Freight receiving and apron table at pad offset `(5,-4)`; yards and freight buildings. Tess's borrowed table is past work history. | Western inner belt; S0 enters the South Cut. Open yard supports drifting/settling. Tess is met at B11, never reintroduced here. |
| Clinic CLN `(110,75)`, radius 8 m | Anonymous receiving, new ground-level bay at `(118,81)`, threshold/cart states. Nearby Clinic Services/tower and civic-looking buildings. | Eastern belt and S1. Existing raised decorative Clinic door is not the usable threshold bay. Do not invent a doctor/medical crisis or set delivery inside the tower. |
| B11 / TES / South counter `(40,67)`, radius 9 m | Tess's counter at `(40,83)` in front of north-facing TEA & MENDING frontage. Building center `(40,95)`, raised plinth starts near z=86. Shelves, canopy, later stool/label. | Marker is the practical road-facing stop, not frontage. Approach from Market, Clinic or Depot through Market is tested. Do not return to old `(40,77)`/4 m contact or drive into the plinth. B11 is well north of HOP/DOG; no prop may obstruct either. |
| Quarry QRY `(-245,20)`, radius 8 m | Bea/Stores shed anchor at `(-254,20)` rotated toward the arrival; pallet/tarp, rope/rut, threshold/barrow, sleeve bench/card. | West of town: A0 or long X0 shelf. Not a generic stone-crate destination; actual door-width slabs and wear matter. New bay is presentation-only, not a new traversable building. |

Contact dimensions come from [manifest destination pads](../../game/world/p1a_world_manifest.json)
and the [chapter's TES override](../../game/scripts/courier/chapter_director.gd).
Anchor offsets: [receiver anchors](../../game/scripts/courier/narrative_anchors.gd),
[opening anchors](../../game/scripts/courier/chapter_anchors.gd),
[slice anchors](../../game/scripts/courier/slices_anchors.gd).

## Road graph writers may rely on

These are named road connections, not the complete navigable surface. Directions
are canonical data directions; `-ID` in a job advisory means traverse in reverse.
Mode character describes the road, not a story requirement.

| Road | Connection | Character |
| --- | --- | --- |
| A0 | Quarry → West Gate GW | Broad west arterial; Drive commitment |
| A1 | GW → Relay | West Sweep; sustained wide bending approach |
| A2 | Relay → East Gate GE | Longer East Sweep; broad committed outer arc |
| L0 | GW → Depot | Inner Market-way approach |
| L1 | Depot → Market | Inner street, tighter direction changes |
| L2 | Market → Clinic | Inner street, tighter direction changes |
| L3 | Clinic → GE | Eastern inner approach |
| L4 | Relay → North Gate GN | Straight northern spine segment |
| L5 | GN → Market | Bending inner spine segment |
| L6 | Market → Works | Works way, service-bar choice retained |
| L7 | Works → GE | Eastern Works connection |
| R0 | GN → Works | Rough drain / technical Spread ground |
| S0 | Depot → HJW `(-45,135)` | Western South Cut approach |
| HOP | HJW → HJE `(45,135)` | Straight technical Spread/Hop option across low bar |
| DOG | HJW → HJE | Longer dogleg dipping south to z=170; valid alternative to HOP |
| S1 | HJE → Clinic | Eastern South Cut approach |
| X0 | Quarry → Relay | Long outside Quarry Shelf, around the northwest; mixed commitment/technical edges |

Actual gate apertures are only GW `(-170,35)`, GN `(0,-130)`, GE `(170,35)`.
**B14 bears a SOUTH GATE sign, but there is no southern gate node/aperture or
exit in the authored route graph.** HJW/HJE are internal junctions, not gates.
The southern Cut is not an exit from the city. Do not invent a road from that
sign. Water Office B08, Pump House B05, Works Office B04 and other labels are
environmental institutions without new characters or playable contacts.

Three preserved open-yard regions—Quarry–Depot, Relay–Works and Market–Clinic—
also permit driving choices. Use current collision/world inspection for a
specific off-road route; the road table alone cannot prove an arbitrary straight
line clear. See [yard geometry](../../game/world/world_polish_v1.json),
[manifest roads/gates](../../game/world/p1a_world_manifest.json),
[live neighborhood labels](../../game/presentation/neighborhood_v1.json), and
[Works service bar](../../game/scripts/courier/mechanics_feature.gd).

## Current cargo origins and route semantics

- Opening: Market→Relay mail; Relay→Works kit; Works→Relay receiver;
  Relay→Quarry socks; **B11→Depot jackets**; **Depot→Clinic aprons**;
  Clinic→B11 repairs; **B11→Quarry patches**, although Relay posts its ticket.
- Chapter 2: Quarry→Clinic new threshold; Relay→Market first tray;
  Clinic→Quarry old threshold. Ordinary Clinic and Quarry arrivals host the
  release/reuse observations; neither observation creates a new bespoke parcel.
- Chapter 3: Relay→Market tray 1; Quarry→B11 sleeve; Relay→Market tray 2;
  Relay→B11 thread; Quarry→B11 pads; B11→Quarry relined sleeve;
  Relay→B11 tagged mending. The two Ren arrival scenes have no cargo leg.

Receiver's L7/−A2 return and aprons' S0/DOG/S1 advice intentionally vary the
driving. HOP/inner streets remain legal. B11 short local approaches need the
destination marker, not a fictional full road to its front door. Chapter 2's
threshold default highlights the street route A0/L0/L1/L2; a South Cut alternative
is permitted, not secretly required. Chapter 3 Relay→B11 jobs highlight L4/L5
toward Market and leave the final local approach to the destination cue.
No new road condition was invented to rationalize these choices.

## Ordinary jobs actually implemented

Market posts these five jobs in addition to available authored work. Optional
challenge conditions affect their existing rewards, not access to story.

| ID / cargo | Pickup → destination | Optional challenge retained |
| --- | --- | --- |
| `freight_seals` / Freight seals | Market → Depot | None in current relay catalog (older STYLE version superseded) |
| `relay_window` / Longline coil | Market → Relay | West Sweep express section |
| `works_instruments` / Bench instruments | Market → Works | Cargo-care target |
| `clinic_thread` / South desk kit | Market → Clinic | Clean South Cut in Spread, Hop or dogleg |
| `quarry_haul` / Shelf survey pack | Market → Quarry | East Sweep northbound, then Quarry Shelf |

Other non-Market contacts provide an ordinary Market post pouch. Once Tess's
patch/opening is complete, B11 provides `mending_pickup` to Depot instead.
The generic local pouch at Relay is not gated on receiver installation in the
current board code. Receiver activation remains the authored story/visual
payoff and gates its story sequence; do not claim it locks every ordinary desk
job. This is a prototype scope limitation, not new fiction about the receiver.
Chapter 3 thread/pads/tagged-mending are **finite required ordinary deliveries**
added through local dispatch; they are not pre-existing infinite services or
optional filler. No ordinary soap/chisel route exists. Tests use `clinic_thread`
and `quarry_haul` as Chapter 2 hosts and `relay_window` for Ren arrivals.

Source: [base catalog](../../game/scripts/courier/alpha_contracts.gd),
[current catalog override](../../game/scripts/courier/relay_contracts.gd),
[local work](../../game/scripts/courier/chapter_text.gd),
[board construction](../../game/scripts/courier/chapter_director.gd),
[slice jobs](../../game/scripts/courier/slices_text.gd),
[UX audit](../../OPENING_CHAPTER_UX_REVIEW.md).
