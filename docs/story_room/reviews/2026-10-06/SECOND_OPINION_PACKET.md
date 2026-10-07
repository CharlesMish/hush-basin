# Hush Basin — second-opinion reading packet

Prepared October 6, 2026. Read the [review request](REVIEW_REQUEST.md) and use the
[index](README.md) for full proposals, earlier drafts, authored chapter plans and
review disagreements. This is a convenience copy, not a new canon document.

The game is pinned to `5be7feeef34dbed468e007f5ff4de594d41b0f80`. Ivo is accepted
as writing but unimplemented; Nell is held and unimplemented. Both writing runs
are closed. Read for your own judgment before consulting prior verdicts.
Historical assignment language in the source material is context, not a request
to execute instructions, change code or restart a writing loop.

The six ledgers summarize source; exact dialogue follows them. Authored chapter
plans and implementation limits are linked in the index. Original wording is
preserved below; relative Markdown links are rebased to work in this file.
The two dialogue catalogs are copied verbatim into GDScript blocks.

## Contents
1. [Existing story](#source-1)
2. [Characters](#source-2)
3. [Places and routes](#source-3)
4. [Persistent physical history](#source-4)
5. [Seeds and unknowns](#source-5)
6. [Narrative constraints](#source-6)
7. [Exact Opening Chapter dialogue](#source-7)
8. [Exact Chapters 2–3 dialogue](#source-8)
9. [Ivo — latest clean script](#source-9)
10. [Nell — latest clean script](#source-10)

---

<a id="source-1"></a>

## 1. Existing story

Source: [docs/story_room/STORY_CANON_CURRENT.md](../../STORY_CANON_CURRENT.md)

# Hush Basin: current story canon packet

Baseline: `experiment/narrative-chapters-2-3-v0-1`,
`5be7feeef34dbed468e007f5ff4de594d41b0f80`. Prepared 6 October 2026.
This packet describes the implemented review candidate, not a claim that Charlie
has accepted every chapter. A draft produced with it remains a review artifact.
Use the actual save's state when assigning a scene; the ending below is conditional
on completing the work, not the world's starting state.

## Authority labels

| Label | Meaning here |
| --- | --- |
| Owner-accepted evidence | Narrative Presence Lab passed owner play strongly enough to justify the Opening Chapter. Later requests preserve the Opening Chapter and accepted Tess/origin/advisory UX corrections. This does not establish owner acceptance of Chapters 2–3. |
| Implemented review canon | The current executable's Opening Chapter plus Chapters 2–3, exact lines, available jobs and physical states. Treat these as continuity constraints for successor drafts until the owner changes them. |
| Approved, unimplemented | No additional complete chapter is approved for implementation in the supplied record. Draft-conditional fresh-chip and chisels lines are authorized only if their stated conditions exist; the current build lacks them. They are not events that happened. |
| Provisional | Opening plan §9's larger-story shapes, Ren's possible old driving round/tag, Sena, later portrait variants and other future sketches. None is established merely by appearing in a document. |
| Historical | Ren's Market portrait/Market kit origin; tiny B11 stop; old receiver-only branches and `main` as narrative authority; superseded draft variants. Keep as provenance, not current facts. |

Exact runtime sources outrank this synopsis for what the candidate does. Authored
v1.1 drafts govern intended text; inspected deviations are recorded in
[NARRATIVE_SLICES_REVIEW](../../../../NARRATIVE_SLICES_REVIEW.md), not silently repaired
through new writing. A conflict between approved script and implementation is a
finding to report, not permission to invent connective history.

## Working identity and grammar

Hush Basin is a courier game about a small working city. Driving is the game;
people are the reason. Paid, ordinary work gradually changes what places and
people can do. The courier is a mostly silent go-between carrying objects,
notes and awkward news. No courier biography, chosen-one role or relationship
score is established.

The tone is practical, dry and sometimes affectionate. People have their own
preferences and edges. Joyful, committed driving coexists with modest needs;
do not invent emergencies to explain speed. Brief local portrait exchanges are
player-advanced. Tickets, receipts and carried notes do much of the work.
There are five single-state portraits: Ren, Ivo, Tess, Bea and Nell. A face means
that person is present at their own contact point. Anonymous institutions do
not become portrait characters by signing a receipt.

## What happens in the implemented chapters

**Opening: eight authored deliveries.** Anonymous Market dispatch has a week
of mail for Relay because its receiver is down. The courier takes it to Ren at
Relay. Ren has promised Quarry an answer today without telling Ivo. Her last
parts go to his Works bench; the finished receiver returns with his invitation
to tea. Its enlarged dial accommodates her gloves. Ren chooses to visit him
herself. The receiver is installed, Relay works, and its first request is six
pairs of dry socks for Quarry. The courier is paid separately for each leg.

Tess's first day at her own B11 counter follows. Her mended jackets go to Depot,
whose table she borrowed for a year; Clinic's aprons are collected there and
delivered to Clinic; Clinic's repair bag comes back to Tess. Her counter opens,
Depot's apron table clears, and she fits a stitched protective patch to the
craft's existing rigid rear panel. After another paid job, Relay posts Quarry's
tarp request with Ren's “Ivo says” referral. Pickup is at Tess, not Relay. The
patch kit goes to Quarry; the receipt is signed B and invites the courier back.
Optional local Ren/Ivo lines confirm the tea visit after Arc 1 plus other work.

**Chapter 2: new use for an old threshold.** At Quarry, B is introduced as Bea.
The courier carries a pale new threshold and Bea's release slip to Clinic.
The old grey slab's lip catches the service cart. The new stone is delivered
beside the door and installed while the courier is away. Ren's empty tray goes
from Relay to Nell's Market hatch; Nell protects her corner piece and reads an
order's extra-greens note. On an ordinary Clinic delivery, the cart now crosses
the new scuffed threshold and Clinic releases the old one. Its return to Bea is
a separate paid job. While the courier is away, Quarry beds the old stone at
the shed door: lip sawn off, wear and tracks retained, barrow in the old groove.
A later ordinary Quarry delivery hosts that observation. Nell's tray and the
Quarry observation must both be completed before Chapter 3 opens.

The preferred tray-before-Clinic-return order is not an extra hard prerequisite.
The existing Market → Clinic desk-kit and Market → Quarry survey-pack jobs host
those ordinary arrivals. There is no implemented soap or chisels delivery.

**Chapter 3: seven counted legs, two independent threads.** Quarry's grey-brown
sleeve has a sound earlier Tess patch, grit in the lining, and an ambiguous
PLAIN SIDE instruction. Bea suspects the patch; Tess first takes that personally,
then diagnoses the grit. Her attributed completion receipt asks Quarry whether
it has been put down face-first. Bea's answer travels with kneeling pads and
permits relining. Tess keeps the old outer cloth and fits an entire flat red
lining. Its return to Quarry leaves a corrected RED/NEVER DOWN ON ITS FACE card
and the sleeve red-side-up. Bea likes it while still preferring the convenience
of buying new. No compulsory personality conversion occurs.

Meanwhile two Relay → Market tray deliveries occur. The first is ordinary;
the second carries Ren's unsupported promise of an extra meal. Nell has finished
service, refuses, and sends an attributed receipt. On the next suitable Relay
arrival Ren admits she promised before asking and has retracted it. A thread
box carries her question to Tess, explicitly allowing “no.” Tess permits tagged
mending on her shelf and refuses freight/crates in the sitting space. Ren's
first tagged parcel respects that boundary. On a later Relay arrival, Ren reads
a Stop 9 invitation referring to jam and says she had promised to go.

The sleeve return/exchange and Ren's final letter exchange are both required
for chapter completion. Their threads can interleave. Ren's two Relay scenes
are cargo-neutral arrivals, not extra jobs. The extra meal is prose only, never
missing cargo. Ordinary work continues; there is no implemented Chapter 4.

## Established connections; deliberate limits

- Ren and Ivo have a familiar shared history, teased through practical details.
  Tea happened in the authored return lines; romance, kinship and its resolution
  are not established.
- Tess previously worked on a Depot table; Clinic is a regular. The courier's
  work makes her new address function. Ivo is credited with telling Ren about
  the new mender; how he learned about Tess is not specified.
- Bea and Tess have prior repair business. The sleeve's old patch predates the
  opening patch kit. Their personal closeness is unknown.
- Ren routes Nell's trays and requests work from Tess. The north crew's identity,
  the greens customer's identity and Stop 9 correspondent's identity are unknown.
- No universal friendship network, complete freight-round history, northern
  destination, Clinic portrait character or playable tea visit is established.

See [characters](../../CHARACTER_LEDGER.md), [geography](../../WORLD_AND_ROUTE_STORY_MAP.md),
[physical states](../../WORLD_STATE_LEDGER.md), [seeds](../../SEED_PAYOFF_LEDGER.md), and
[directing rules](../../NARRATIVE_RULES.md) before adding facts.

## Source index

- [Opening script](../../../../game/scripts/courier/chapter_text.gd),
  [slice script/dependencies](../../../../game/scripts/courier/slices_text.gd).
- [Opening director](../../../../game/scripts/courier/chapter_director.gd),
  [slice director](../../../../game/scripts/courier/slices_director.gd),
  [save validation](../../../../game/scripts/courier/slices_store.gd).
- [Opening plan](../../../OPENING_CHAPTER_PLAN_V0_1.md),
  [Quarry v1.1](../../../QUARRY_SLICE_V1_1.md),
  [Chapter 3 v1.1](../../../CHAPTER_3_SLICE_V1_1.md).
- [Opening implementation/adaptations](../../../../OPENING_CHAPTER_REVIEW.md),
  [accepted UX correction](../../../../OPENING_CHAPTER_UX_REVIEW.md),
  [recorded validation](../../../../NARRATIVE_SLICES_REVIEW.md).

---

<a id="source-2"></a>

## 2. Characters

Source: [docs/story_room/CHARACTER_LEDGER.md](../../CHARACTER_LEDGER.md)

# Character ledger

Baseline/status labels: [current canon](../../STORY_CANON_CURRENT.md). These are facts
available by the relevant completed scene, not knowledge all characters possess
at a fresh save. “Unknown” means not established, not a claim of ignorance.
Voice observations are guides, not compulsory sentence templates.

## Ren — Relay operator

- **Place/status:** northern Relay receiving desk; implemented local portrait in
  all three chapters. `game/presentation/narrative/ren.png`, one state. Late-30s
  impression, practical coat/cap, gloved hand are art direction, not stated age.
- **Voice/person:** active, self-involving, rueful, prone to committing ahead of
  asking. She can hear a refusal and retract her promise. Neither villain nor
  incompetent comic victim.
- **Connections:** familiar with Ivo; knows his work and accepts his invitation.
  Routes Quarry requests; sends Nell's trays; learns Tess can take tagged mending.
  Has correspondence with unnamed Stop 9; promised a visit.
- **Knows when:** she knows her Quarry deadline before Ivo; the courier brings
  his tea invitation; Nell's attributed receipt informs her refusal scene;
  Tess's receipt establishes the shelf boundary before she routes mending.
- **Not established:** former driving career/old round, family, identity or
  relationship of Stop 9, knowledge of every Quarry/Clinic event. Do not give her
  omniscient dispatch knowledge merely because she operates Relay.
- **End situation/traces:** functioning receiver with large dial; mail/rack;
  respected shelf arrangement; pinned letter awaiting an unimplemented visit.
- **Voice examples:** “Tell him I’ll—no. I’ll go over after close.” / “I've taken
  it back. They were very nice about it, which was worse.” / “Say no if it's no.”
- **Avoid:** repeating overpromise/apology every arc, begging forgiveness,
  permanent guilt, a moral lesson speech, couriered apology errands.

## Ivo — Fabrication

- **Place/status:** Works receiving bench; implemented Opening portrait and
  optional local return. `ivo.png`, one state. Early-50s/broad/silver curls,
  apron and rolled sleeves are prototype art direction.
- **Voice/person:** contained amusement, precise consideration expressed through
  fabrication. Teases Ren through details; lets an object carry the affection.
- **Connections:** established history with Ren and a chair he calls hers. Ren's
  coda note credits him as the source of the Tess referral; no meeting between
  Ivo and Tess is shown or required by that fact.
- **Knows when:** the courier tells him Ren said today; he knows her gloves and
  invites her. His optional return line reports her visit/reorganized shelves.
- **Not established:** romantic/kinship label, hidden grievance, extent of contact
  with Tess, Bea or Nell. There is no implemented Chapter 2/3 Ivo scene.
- **End situation/traces:** receiver leaves Works for Relay. Bench, chair and
  parts crate remain. The crate does not clear in the current prototype; it is
  not a reliable narrative clock or evidence contradicting the spoken visit.
- **Voice examples:** “Ren promised today? She used to book my whole afternoon
  with that word.” / “I made the dial bigger, since she won’t take those gloves
  off.” / “She came by after close. Sat an hour and reorganized my shelves.”
- **Avoid:** pining caricature, exposition machine, mechanic upgrade vendor,
  every concern permanently revolving around Ren.

## Tess — Mending

- **Place/status:** B11 south counter, own address from first meeting; implemented
  Opening/Chapter 3 portrait. `tess.png`, one state. Compact late-20s impression,
  brick coat, tape measure, pinned sleeves, eyeline toward craft: art direction.
- **Voice/person:** sociable, confident, diagnostic, quick to judge a makeshift
  fix; capable of examining what actually failed. Chapter 3 lets her initial
  defensiveness coexist with a correct diagnosis.
- **Connections:** Depot lent her a table for a year; Clinic is a regular;
  courier supplies her new counter and receives a patch; prior Quarry repair
  business; Ren asks permission to route tagged mending.
- **Knows when:** sees the craft's scuffed rear panel; reads Bea's sleeve tag;
  discovers grit; waits for Bea's pads note; reads Ren's request and states a
  boundary. She need not know Nell refused Ren earlier.
- **Not established:** friendship with every customer, origin of Ivo's referral,
  a generic depot service, cloth cargo cover, mechanical performance upgrade.
- **End situation/traces:** open counter; protective craft patch; Quarry sleeve
  relined and returned; MENDING — TAGGED, PLEASE shelf and delivered parcel;
  front space reserved for sitting, not freight.
- **Voice examples:** “Their jackets are mended—call it rent.” / “The seam held.
  That didn't make the lining fit to use.” / “Crates, no. Out front's for sitting.”
- **Avoid:** cute seamstress, mother hen, flirt, driving scold, bad-repair lesson.
  Her earlier sleeve patch is sound. The whole lining is replaced, not her patch.

## Bea / B — Quarry Stores

- **Place/status:** Quarry receiving shed/pallet/bench; B receipt in Opening,
  portrait introduced Chapter 2 and reused Chapter 3. `bea.png`, one state,
  practical dusty workwear; no dialogue age or broader biography established.
- **Voice/person:** dry, observant about material use and wear, offers ordinary
  hospitality without a speech. Can value reuse and still prefer buying new
  when that means less checking. She is not an allegory for repair.
- **Connections:** Quarry crew/Stores; releases work to Clinic; previous Tess
  sleeve repair; invites courier to return. Exact social intimacy is unspecified.
- **Knows when:** requests the old threshold if Clinic releases it; reads Tess's
  receipt and answers that the sleeve was being put on the yard; sees red lining
  on return. She initially suspects patch location; the suspicion is not fact.
- **Not established:** awareness of Ren's Nell promise, personal familiarity with
  Ivo, Clinic staff identities, ability to identify a fresh chip from generic
  cargo condition. The optional chip line is disabled in this build.
- **End situation/traces:** patched tarp, rope hook, reused worn threshold/barrow;
  red-lined sleeve, corrected handling instruction at her bench.
- **Voice examples:** “Hollow between the tracks. That's feet, not the cart.” /
  “It's good. I'd still have bought a new one. Less to check.” / “Crew keeps
  showing me the red side. I've seen the red side.”
- **Avoid:** explaining the threshold's symbolism, secretly testing the courier,
  all-wise thrift evangelist, a new belief substituted for her practical preference.

## Nell — Market hatch

- **Place/status:** Market food hatch at Market contact; distinct from anonymous
  dispatch. Introduced Chapter 2; standard portrait at Chapter 3 interruption;
  no portrait on the first Chapter 3 tray. `nell.png`, one state. Apron, tied hair
  and practical dry reserve are prototype art direction; no seated variant.
- **Voice/person:** notices regular preferences, protects her own portion and
  finished work time. Direct refusal, not a cruelty beat or invitation to fix her.
- **Connections:** regular meal/tray work with Relay; an unnamed customer whose
  greens she has removed for a year. The latter's identity is not supplied.
- **Knows when:** reads the greens note, then learns of Ren's extra-meal promise
  when the next authored interruption occurs. Her receipt tells Relay “No extra.”
- **Not established:** knowledge that Ren later changes how she asks Tess; a
  reconciliation scene, second Nell project, general hostility to courier work.
- **End situation/traces:** return crate persists; meal settings and note are
  visit props, not permanent food or an objective. Service hours are authored
  staging, not a simulated clock.
- **Voice examples:** “Don't look at the corner. That one's mine. I got here
  first.” / “I'd only just sat down.” / “Ren's promised them another? I didn't
  say that. I've finished.”
- **Avoid:** rewarding the player for overriding her no, guilt arc, cartoon
  anger, a mystery or permanent motif behind every corner piece.

## Institutions, seeded correspondents and non-cast

| Voice/reference | Established scope | Do not silently add |
| --- | --- | --- |
| Market dispatch | Anonymous, brisk mail/ordinary-work counter | A named dispatcher or Nell speaking for all Market |
| Depot receiving | Jackets receipt; lent Tess a table; receives ordinary freight | A portrait freight-hand, specific past friendship scene |
| Clinic receiving | Precise apron/threshold/release receipts; regular Tess work | Sena, medical emergency, physician dialogue |
| Quarry Stores “we” | Institutional tickets/receipts; B later introduced as Bea | Bea personally uttering every older receipt unless assigned |
| North crew | Recipient group of Ren's retracted extra-meal promise | A face, playable new stop, or failed meal job |
| Stop 9 correspondent | Wrote quoted jam invitation; identity unspecified | Name, kinship, romance or northern travel chapter |
| Sena / other cast slots | Provisional older sketches only | Current canon, portrait or active job |

Sources: [opening lines](../../../../game/scripts/courier/chapter_text.gd),
[slice lines/notes](../../../../game/scripts/courier/slices_text.gd),
[portrait and adaptation record](../../../../NARRATIVE_SLICES_REVIEW.md),
[opening art/craft record](../../../../OPENING_CHAPTER_REVIEW.md),
[Works physical source](../../../../game/scripts/courier/narrative_anchors.gd).

---

<a id="source-3"></a>

## 3. Places and routes

Source: [docs/story_room/WORLD_AND_ROUTE_STORY_MAP.md](../../WORLD_AND_ROUTE_STORY_MAP.md)

# World and route story map

Baseline/status: [current canon](../../STORY_CANON_CURRENT.md). Coordinates below are
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

Contact dimensions come from [manifest destination pads](../../../../game/world/p1a_world_manifest.json)
and the [chapter's TES override](../../../../game/scripts/courier/chapter_director.gd).
Anchor offsets: [receiver anchors](../../../../game/scripts/courier/narrative_anchors.gd),
[opening anchors](../../../../game/scripts/courier/chapter_anchors.gd),
[slice anchors](../../../../game/scripts/courier/slices_anchors.gd).

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
line clear. See [yard geometry](../../../../game/world/world_polish_v1.json),
[manifest roads/gates](../../../../game/world/p1a_world_manifest.json),
[live neighborhood labels](../../../../game/presentation/neighborhood_v1.json), and
[Works service bar](../../../../game/scripts/courier/mechanics_feature.gd).

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

Source: [base catalog](../../../../game/scripts/courier/alpha_contracts.gd),
[current catalog override](../../../../game/scripts/courier/relay_contracts.gd),
[local work](../../../../game/scripts/courier/chapter_text.gd),
[board construction](../../../../game/scripts/courier/chapter_director.gd),
[slice jobs](../../../../game/scripts/courier/slices_text.gd),
[UX audit](../../../../OPENING_CHAPTER_UX_REVIEW.md).

---

<a id="source-4"></a>

## 4. Persistent physical history

Source: [docs/story_room/WORLD_STATE_LEDGER.md](../../WORLD_STATE_LEDGER.md)

# Persistent world state ledger

Baseline: [current canon](../../STORY_CANON_CURRENT.md). “Implemented” means present
in review source, not that every owner has reached or accepted that state.
Visibility below distinguishes source/capture evidence from untested human
recognition. Narrative anchors use simple non-colliding meshes; they do not
change road topology, physics or camera.

| State/change | Cause | Location | Visible during normal play? | Story significance | Implementation status |
| --- | --- | --- | --- | --- | --- |
| Dead receiver/parts case → mail received | Opening mail delivery | Ren's Relay desk | Local bench/props, no reveal camera | Requests reach their person | Implemented; mail remains after delivery |
| Prepared core/kit → finished oversized-dial receiver → receiver leaves | Kit delivery, then explicit receiver acceptance | Ivo's Works bench | Same local receiver shape later used at Relay | Ivo remembers the gloves | Implemented |
| Receiver arrives → mounts, indicator on, dispatch active | Ren's invitation exchange completed/skipped to handoff | Relay receiving desk | Strong local machine/indicator distinction | A working desk and first request | Implemented; completed consequence persists |
| Quarry socks parcel available → leaves rack | Relay activation, then explicit acceptance | Relay rack | Local parcel | Ordinary first answered need | Implemented; not permanent trophy |
| Chair and occupying crate | Opening staging | Works | Local furniture | Supports “her chair” invitation | Static prototype: crate never clears, even after visit lines |
| Half-unpacked counter → open MENDING sign, hanging work, shelves | Clinic repairs delivered and Tess exchange resolved | B11 | Local frontage/counter | Tess has her own working address | Implemented; Chapter 3 sleeve staging later replaces hanging display |
| Apron stack → empty table | Aprons collected at Depot | Depot receiving | Small nearby table | Old address's outstanding work cleared | Implemented |
| Rear-panel scuffs → stitched protective patch | Tess's final opening exchange | Craft rear starboard inner leaf | Small visible child mesh; owner noticeability unresolved | Tess notices courier's own equipment | Implemented cosmetic only; real rigid surface, no cloth cover, no repair stat |
| Patched tarp over new threshold → folded tarp/bare pallet | Chapter 2 threshold loaded | Quarry Stores pallet | Local pale slab silhouette/patches | Prior patch delivery did work | Implemented; coda's exact tarp-repair moment is not animated |
| Old grey dished threshold, pale tracks, raised lip; cart catching | Initial Chapter 2 receiving state | Clinic bay | Normal-view captures supplied | Specific functional reason for new slab | Implemented; static cart staging, not cart physics |
| New pale flat slab on pad → installed bevel/no lip/scuffs/cart across | Delivery, then departure >90 m from Clinic | Clinic | Normal-view before/after captured; scuffs finer than silhouette | Improvement stays in use | Implemented; installation occurs off-screen |
| Old stone leaned on offcuts → released collection → absent | Installation; ordinary Clinic receipt releases; explicit old-stone pickup | Clinic wall beside receiving | Local prop and concrete release text | Release permission, not unclaimed salvage | Implemented; visual staging can precede legal release |
| Old stone on blocks → bedded doorway, pale sawn edge, old wear/tracks, barrow | Return delivery; departure >90 m from Quarry | Quarry shed | Native normal-camera evidence; human object recognition still a playtest gate | Old object gets another practical use | Implemented; next ordinary Quarry delivery hosts observation, no symbolism sign |
| Return crate | Nell's first tray arrival | Market hatch | Local shelf/crate | Stable routine return place | Implemented and persistent |
| Meal/tin/saucer/order → later busy orders → finished-service plate/fork/note | Authored tray visits | Market hatch | Normal local view; bite/fork/paper marks are fine details | Nell is working, then has finished | Implemented visit states; not permanent meals or simulated time |
| Grey-brown sleeve/old sound patch/PLAIN card → sleeve leaves | Chapter 3 starts, then sleeve accepted | Quarry bench | Bench/card/roll in normal-view captures | Misleading sameness of the two faces | Implemented; patch predates opening kit |
| Unrolled sleeve → held on hook | Sleeve delivered; Tess scene resolves | B11 | Counter/hook visible | Waits for Bea's answer | Implemented; no timer or failed patch |
| Pads/note → relining → folded sleeve with broad red lining | Pads delivery; departure >50 m from B11 | Quarry pickup / Tess counter | Fold exposes full red face | Permission plus practical correction | Implemented; retained old outer cloth, flat new working face |
| Sleeve red-side-up; PLAIN struck, RED above, NEVER DOWN ON ITS FACE | Relined sleeve returned | Quarry bench | Normal-view red/card evidence; recognition remains owner judgement | Corrected handling stays after conversation | Implemented; subsequent optional Bea remark never gates progress |
| Thread box → tagged-mending shelf label | Thread delivery/boundary reply; departure >50 m from B11 | Relay desk / B11 shelf | Local box/label | Tess consented to a specific service | Implemented; label permanent, sitting front remains clear |
| Tagged parcel on labelled shelf | First routed mending delivered | B11 | Local shelf parcel | Ren remembers the boundary | Implemented; no portrait at routine drop |
| Opened Stop 9 letter → pinned letter | Ren's final Chapter 3 exchange | Relay desk | Small local paper asset | An invitation/promise remains unresolved | Implemented; no northern visit or automatic removal in current content |

## State and restart contracts

`user://narrative_chapters_v01.json` atomically stores opening step, seen scenes,
pending handoff, active authored parcel/checkpoint, craft patch/intervening-work
flags, slice completion IDs and physical `installed`, `bedded`, `relined`,
`shelf_label` flags. Older review saves are separate. Reset Story clears this
candidate's complete narrative progression and traces; it is explicit.

An accepted authored parcel resumes at its saved position at rest, preserving
condition and elapsed delivery time. A pending handoff returns to its real local
contact. Declining new work preserves the last delivery/payment/consequence.
Ordinary jobs, credits, liner and mastery retain session-only semantics; do not
promise persistence for a generic ordinary cargo merely because story cargo
persists. New Chapter 3 named ordinary legs are authored persisted parcels.

Three attributed completion receipts post subsequent requester state: Tess's
sleeve reply → Bea's pads/answer; Nell's refusal → Ren's next Relay arrival;
Tess's shelf boundary → Ren's tagged parcel. This is the existing finite
receipt/posting channel, not simulated messaging or a new physical errand.

Sources: [opening anchors](../../../../game/scripts/courier/chapter_anchors.gd),
[receiver anchors](../../../../game/scripts/courier/narrative_anchors.gd),
[slice anchors](../../../../game/scripts/courier/slices_anchors.gd),
[off-screen transitions/resume](../../../../game/scripts/courier/slices_director.gd),
[atomic record/dependencies](../../../../game/scripts/courier/slices_store.gd),
[reviewed limits](../../../../NARRATIVE_SLICES_REVIEW.md).

---

<a id="source-5"></a>

## 5. Seeds and unknowns

Source: [docs/story_room/SEED_PAYOFF_LEDGER.md](../../SEED_PAYOFF_LEDGER.md)

# Seeds, payoffs and ordinary details

Baseline/status: [current canon](../../STORY_CANON_CURRENT.md). An unresolved reference
is not an approved future assignment. “Possible” below marks an opening for
human direction, not promised content. Players may skip/review conversations;
do not require their memory of an optional line as a hard prerequisite.

| Planted detail | Player exposure | Payoff / status | Knowledge boundaries |
| --- | --- | --- | --- |
| Ren says today before asking Ivo | Required opening exchange, skippable | Receiver arc resolved; later premature Nell promise develops the pattern | Ivo learns deadline through courier, not prior telepathy |
| Gloves, enlarged dial, her chair, invitation | Required Works/Relay exchanges and receiver | Tea visit confirmed by optional local return lines; paid off as an old connection | Ren hears invitation through courier; relationship label remains open |
| “Ivo says there's a new mender down south” | Coda ticket | Referral acted on; reveals information moving between acquaintances | Establishes attributed referral, not an Ivo/Tess meeting or everyone's friendship |
| Tess's first order to her own address / courier patch | Required opening arc | Counter opens and craft changes; paid off | Tess sees craft wear; patch is not a performance upgrade or debt |
| Quarry's B signature/invitation | Required coda receipt | Bea introduced in Chapter 2; name seed paid off | B is Bea; no need to turn invitation into a mandatory leisure trip |
| New stone's release slip and old threshold wear | Required cargo docket/Clinic receipt; physical staging | Paid off by legal return and Quarry reuse | Bea asks; Clinic grants release later; courier cannot assume permission |
| Quarry doorway rut / barrow groove | Environmental, expected to be recognizable from normal arrival | Paid off physically by reused threshold | No character needs to explain its symbolism |
| Nell's corner piece / greens note | Chapter 2 exchange; later environmental repetition | Ordinary preference and work boundary; not a future mystery | Unnamed greens customer stays unnamed; do not assume it is Ren or Ivo |
| Sleeve patch and PLAIN handling card | Chapter 3 pickup/tag | Paid off by diagnosis, Bea's answer, red lining and corrected instruction | Bea's suspicion and Tess's first interpretation are beliefs, not causal facts |
| Ren's extra-meal promise / Nell's refusal | Tray ticket, interruption and attributed receipt | Ren retracts promise; paid off, not a new apology arc | Receipt reaches Ren; Nell need not know about Ren's later Tess request |
| “Say no if it's no” / tagged-only boundary | Carried note, Tess dialogue/receipt | First labelled-shelf parcel proves Ren respected it; paid off | Ren receives receipt before routing parcel; Tess has not accepted freight |
| Stop 9 jam letter and “I did say I'd go” | Final Ren exchange; pinned letter | Unresolved invitation. No visit or Chapter 4 written/implemented | Ren knows correspondent; courier hears quoted letter; identity/relationship unknown |
| Ren's old round / working tag | Older Opening §9 sketch only, not planted by current dialogue | Provisional future shape, not unresolved canon | Do not make characters remember it as an established fact |

## Details allowed to remain ordinary

- Socks and the reclaimed kettle: a dry practical request already fulfilled.
- Ivo's hinges; Ren rearranging shelves: two people describing the same visit.
- The corner piece, greens preference, plate and fork: food, work and a pause.
- Rope on its hook, tarp patches, blue thread on pockets, thread spools: useful
  material detail; no coded message, secret identity or compulsory return arc.
- The person who sat on Tess's last box for an hour: a wry example, not a cast slot.
- Freight seals, desk kits, coils and survey packs: ordinary work may remain so.
- Environmental office signs: a place can exist without a portrait or quest.

A writer may propose a meaningful reuse, but the examiner should not demand one.
Selective physical memory is welcome; every repeated noun becoming a plotted
clue is not. The Stop 9 invitation is a real unresolved line, but its eventual
importance and timing still need direction. Do not invent a withheld secret to
make the ending feel more consequential.

Sources: [exact opening text](../../../../game/scripts/courier/chapter_text.gd),
[exact slice text](../../../../game/scripts/courier/slices_text.gd),
[Opening plan §9, explicitly sketches](../../../OPENING_CHAPTER_PLAN_V0_1.md),
[world-state implementation](../../WORLD_STATE_LEDGER.md).

---

<a id="source-6"></a>

## 6. Narrative constraints

Source: [docs/story_room/NARRATIVE_RULES.md](../../NARRATIVE_RULES.md)

# Narrative rules for the story room

Use [current canon](../../STORY_CANON_CURRENT.md) for authority and
[the map](../../WORLD_AND_ROUTE_STORY_MAP.md) for physical truth. These rules combine
established implementation constraints with directing principles Charlie has
adopted for this authoring workflow. New workflow principles guide proposals;
they do not make unwritten events canon.

## Protect the game

1. **Driving is the game; people are the reason.** Most time remains freely
   controlled movement. Geography supplies challenge; story chooses geography.
   A worthwhile leg changes the drive, understanding, physical situation or
   subsequent work. Flag a weak bridge leg with reasons; do not cut approved
   content automatically.
2. **Story delivery accepts any legal route.** Suggestions may offer an enjoyable
   line, never an invented route obligation. Optional mastery can coexist with
   work but never gates story. No timer, pristine-condition requirement,
   relationship penalty or emergency invented to compel speed.
3. **Respect actual cargo and surfaces.** One active parcel is not a general
   inventory. A carried note may travel with it. A threshold is a slab, a sleeve
   is cloth, the craft's patched rear panel is rigid. Do not promise unsupported
   simultaneous cargo, walking, animation, time simulation or new physics.
   Nonzero implementation cost is not automatically a bad idea; label it.
4. **Keep the accepted movement and world.** No tuning, camera, collision, BRRR,
   drift, transform/Hop or city-topology changes as narrative conveniences.
   Native Forward+ and current Web architecture are independent constraints.

## Keep the interaction honest

5. **A face means here.** Ren at Relay, Ivo at Works, Tess at B11, Bea at Quarry,
   Nell at Market hatch. Remote notes/receipts are paper/text, never a portrait
   call. A later remote visual language requires separate explicit design.
6. **Text is immediate and player-advanced.** No forced reading timer/typewriter
   wait, cinematic camera or dialogue during technical driving. Story UI yields
   to controls/essential prompts. Repeats are lighter; review is local.
7. **Advance and Skip never accept work.** Both lead to essential handoff/offer
   context. Accept needs a new explicit input after the neutral-release barrier.
   A completed leg settles separately before the next offer; the receiver has
   its established installation exchange before that delivery settles. No
   replay payment, auto-accept, or declining that undoes earlier work.
8. **Postponement is allowed.** Available jobs persist under their dependencies,
   ordinary work remains, and independent threads stay independent. Resume
   language names actual cargo, place and action; neither percentages nor a
   previous leg's origin. Contacts mark where to stop, not a distant frontage.
9. **Information must travel.** State who knows a fact, when and through which
   witnessed exchange, note or receipt. The finite completion-receipt/request
   channel already carries three Chapter 3 replies. It is not general telepathy
   and does not justify adding a courier leg for every reply.

## Write people, not compliance demonstrations

10. **Characters carry arcs; receipts can carry city voice.** A routine arrival
    can host a meaningful scene. Do not manufacture a trip for a cargo-neutral
    exchange. Returning people can reveal another concern without a new arc.
11. **Development preserves a person.** Ren can retract a promise without becoming
    pathetic; Tess can diagnose beyond her pride without having made a bad patch;
    Bea can reuse one object and still prefer buying another new. A character's
    introductory trait is not their only permissible subject.
12. **Practical before cozy.** This is paid work. Prefer specificity, appetite,
    judgement and ordinary friction over gratitude, flattery and universal wit.
    Protect strong prose as well as economy. Opening-plan rules about grammatical
    person, thank-yous and hot drinks are useful local tone heuristics, not
    machine-enforced quotas across every later chapter.
13. **Connections become denser through work.** Some existing connections are
    revealed; some are created by the courier. Not everyone knows everyone at
    the beginning. Later broad interconnectedness is welcome when earned through
    staged revelation; avoid mechanically completing every pair in the cast.
14. **Ordinary work can remain ordinary.** A second appearance does not create a
    promise of a hidden payoff. Use the seed ledger to distinguish unresolved
    commitments from material texture. Do not turn the city into a conspiracy.
15. **History can remain in places, selectively.** Changed props, handling labels,
    receipts and working arrangements often suffice. Persistent evidence should
    be legible from normal play without a camera cut or explanatory plaque.
    Not every delivery earns permanent geometry or a trophy.

## Review and scope discipline

- Preserve accepted authored words in implementation. For a concrete contradiction,
  report source → proposed/implemented change → reason. A writing assignment may
  propose new wording only within its explicit remit; critique is not authority.
- Keep current, approved-unimplemented, provisional and historical material
  distinguishable. A model's accepted/revised draft does not automatically become
  game canon; only an explicit human-authorized promotion updates these ledgers.
- No new relationship systems, portraits/expressions, campaign or Chapter 4 in
  this preparation task. Future ideas remain proposals with scope and dependencies.
- Do not fail writing on taste alone or mechanically obey every criticism.
  Separate continuity/design blockers, implementation costs and subjective notes.
  Name what works and must survive revision.
- Automated tests can prove state/input behavior, not attachment, pacing,
  recognition, comfort, curiosity or desire to keep driving. Charlie's play and
  unfamiliar-player evidence remain necessary. Tess's jackets leg is the known
  opening pacing hypothesis, not protected proof or an automatic deletion.
- If attachment fails, do not compensate autonomously with more characters,
  backstory, romance or missions. Return evidence and seek direction.

Sources: owner-approved [Opening scope](../../../OPENING_CHAPTER_PLAN_V0_1.md),
[Quarry v1.1](../../../QUARRY_SLICE_V1_1.md),
[Chapter 3 v1.1](../../../CHAPTER_3_SLICE_V1_1.md),
[acceptance/locality code](../../../../game/scripts/courier/chapter_director.gd),
[slice state logic](../../../../game/scripts/courier/slices_director.gd),
[implementation limits](../../../../NARRATIVE_SLICES_REVIEW.md). Social-web and
writer/examiner discipline above also implement Charlie's adopted story-room
brief of 6 October 2026; they do not authorize new story content.

---

<a id="source-7"></a>

## 7. Exact Opening Chapter dialogue

Source: [game/scripts/courier/chapter_text.gd](../../../../game/scripts/courier/chapter_text.gd)

```gdscript
extends RefCounted
## Opening Chapter v0.1 only. No campaign graph or remote portraits.
const ORDER=["relay_mail","relay_stock","relay_receiver","relay_quarry","tess_jackets","tess_aprons","tess_repairs","tess_patches"]
const ORIGINS={"relay_mail":"MRK","relay_stock":"RLY","relay_receiver":"WRK","relay_quarry":"RLY","tess_jackets":"TES","tess_aprons":"DEP","tess_repairs":"CLN","tess_patches":"TES"}
const PLACES={"MRK":"Market","RLY":"Relay","WRK":"Works","QRY":"Quarry Stores","DEP":"Depot","CLN":"Clinic","TES":"South counter"}
const HOME={"market":"MRK","ren_intro":"RLY","works":"WRK","relay":"RLY","quarry_offer":"RLY","tess_intro":"TES","depot":"DEP","clinic":"CLN","tess_final":"TES","coda":"TES","ticket":"RLY","ren_return":"RLY","ivo_return":"WRK"}
const SPEAKER={"ren_intro":"ren","works":"ivo","relay":"ren","quarry_offer":"ren","tess_intro":"tess","tess_final":"tess","coda":"tess","ren_return":"ren","ivo_return":"ivo"}
const OFFERS={"market":"relay_mail","ren_intro":"relay_stock","works":"relay_receiver","quarry_offer":"relay_quarry","tess_intro":"tess_jackets","depot":"tess_aprons","clinic":"tess_repairs","coda":"tess_patches"}
const LINES={
 "market":["For Relay. Their receiver’s down, so it’s all been landing here."],
 "ren_intro":["I’m Ren. That’s a week of requests this desk couldn’t hear.","I told Quarry we’d be answering again today. Ivo’s got the receiver—he doesn’t know I said today.","These are the last parts. Could you run them to Works? And maybe mention the today part."],
 "works":["Ren promised today? She used to book my whole afternoon with that word.","That finishes it. I made the dial bigger, since she won’t take those gloves off.","Tell her I’ll clear off her chair, if she has time for tea."],
 "relay":["Look at that dial. He remembered the gloves. Thanks for bringing this.","Tell him I’ll—no. I’ll go over after close."],
 "quarry_offer":["Six pairs. I’ve got those on the rack. Want the Quarry run?"],
 "tess_intro":["You’re the courier? I’m Tess. First day at my own counter.","Depot lent me a table for a year. Their jackets are mended—call it rent.","Clinic’s aprons are waiting there too. I’m not leaving this counter on day one."],
 "depot":["Jackets received. Yard’s quieter without her."],
 "clinic":["Aprons received. Shorter ties this time—no more catching on the cupboard.","Three for mending. Blue thread marks the torn pockets."],
 "tess_final":["You’ve brought my first order in. Clinic, of course.","Your rear panel’s scuffed along the edge. You take every corner like that?","Pull in. This’ll take a minute."],
 "coda":["Strong thread. And tell them rope isn’t a repair."],
 "ticket":["QUARRY STORES — Tarp’s split again. Strong thread and patches, please. It’s held together with rope.","RELAY — Ivo says there’s a new mender down south. Try Tess. —R."],
 "ren_return":["Went over to Ivo’s. He talked about hinges for an hour."],
 "ivo_return":["She came by after close. Sat an hour and reorganized my shelves."]
}
const TICKET="QUARRY STORES — Tarp’s split again. Strong thread and patches, please. It’s held together with rope.\nRELAY — Ivo says there’s a new mender down south. Try Tess. —R."
const SOCK_TICKET="QUARRY STORES\nSix pairs of dry socks, please. The old ones are drying on the kettle."
const SUMMARIES={
 "market":"Relay mail → Ren · Relay\nA week of requests that couldn’t reach her desk.",
 "ren_intro":"Receiver kit → Ivo · Works\nLast parts for Ren’s receiver.",
 "works":"Receiver kit → Finished receiver\n\nFinished receiver → Ren · Relay\nRestores Relay dispatch. Ivo’s invitation travels with it.",
 "quarry_offer":"Dry socks → Quarry Stores\nRelay’s first answered request.",
 "tess_intro":"Mended jackets → Depot\nThe freight crew’s jackets. Tess’s rent for a borrowed table.",
 "depot":"Clinic’s aprons → Clinic\nFinished before the move; never collected.\nSouth Cut: S0 → DOG or HOP → S1. Any legal route.",
 "clinic":"Clinic repairs → Tess · South counter\nFirst order to her new address.",
 "tess_final":"Tess’s counter is open.\nHer stitched protective patch is fitted to your rear panel.",
 "coda":"Patch kit → Quarry Stores\nStrong thread and patches, from Tess’s counter.",
 "ticket":"Patch kit → Quarry Stores\nPick up at Tess’s counter. No cargo accepted here."
}
const ACCEPT={"market":"Take Relay mail","ren_intro":"Take kit to Works","works":"Take receiver","quarry_offer":"Take Quarry parcel","tess_intro":"Take jackets","depot":"Take aprons","clinic":"Take repair bag","coda":"Take patch kit"}
const DECLINE={"market":"Not now","ren_intro":"Not now","works":"Leave it here","quarry_offer":"Later","tess_intro":"Not now","depot":"Leave them here","clinic":"Later","coda":"Later"}

static func job(id: String) -> Dictionary:
	var c: Dictionary=preload("res://scripts/courier/relay_contracts.gd").outbound()
	var spec: Dictionary={
	 "relay_mail":{"destination":"RLY","name":"Relay mail","base":100,"routes":["-L5","-L4"],"reaction":"Relay mail received."},
	 "relay_stock":{"destination":"WRK","name":"Receiver kit","base":120,"routes":["L4","R0"],"reaction":"Receiver kit received."},
	 "relay_receiver":{"destination":"RLY","name":"Finished receiver","base":140,"routes":["L7","-A2"],"reaction":"Receiver delivered."},
	 "relay_quarry":{"destination":"QRY","name":"Dry socks","base":100,"routes":["-A1","-A0"],"reaction":"Six pairs received. We can have the kettle back."},
	 "tess_jackets":{"destination":"DEP","name":"Mended jackets","base":100,"routes":["-L1"],"reaction":LINES.depot[0]},
	 "tess_aprons":{"destination":"CLN","name":"Clinic’s aprons","base":120,"routes":["S0","DOG","S1"],"reaction":LINES.clinic[0]},
	 "tess_repairs":{"destination":"TES","name":"Clinic repairs","base":100,"routes":[],"reaction":"First order received at Tess’s counter."},
	 "tess_patches":{"destination":"QRY","name":"Patch kit","base":120,"routes":["-L1","-L0","-A0"],"reaction":"Patches received. Rope’s back on its hook. Come out when you’re not working—we’ll put the kettle on. —B."}
	}[id]
	c.merge(spec,true);c.id=id;c.origin=ORIGINS[id];c.place=PLACES[c.destination];c.character="To "+String(c.place);c.objective_text="Paid delivery · no timer or quality gate"
	var exchange: String=OFFERS.find_key(id)
	c.purpose=SUMMARIES[exchange]
	if id=="relay_receiver":c.purpose=c.purpose.get_slice("\n\n",1) # Transformation belongs to the handoff, not the active leg.
	c.dispatch=c.purpose
	return c

static func local_work(hub: String) -> Dictionary:
	var c: Dictionary=preload("res://scripts/courier/relay_contracts.gd").outbound()
	c.id="mending_pickup" if hub=="TES" else "local_"+hub;c.origin=hub
	c.name="Mended work" if hub=="TES" else "Market post pouch"
	c.destination="DEP" if hub=="TES" else "MRK";c.place=PLACES[c.destination];c.character=PLACES[hub]+" → "+c.place
	c.purpose=c.name+" → "+c.place+"\nOrdinary paid work.";c.dispatch=c.purpose;c.reaction="Mended work received." if hub=="TES" else "Post received at Market.";c.routes=[]
	return c

static func pickup_label(c: Dictionary) -> String:
	return "Pickup: "+PLACES[c.origin]+" → "+PLACES[c.destination]
```

---

<a id="source-8"></a>

## 8. Exact Chapters 2–3 dialogue

Source: [game/scripts/courier/slices_text.gd](../../../../game/scripts/courier/slices_text.gd)

```gdscript
extends RefCounted
## Exact v1.1 authored text. UI summaries are kept separate from spoken panels.
const Opening=preload("res://scripts/courier/chapter_text.gd")
const RELEASE="QUARRY STORES · One threshold for Clinic receiving entrance, finished face protected. If Clinic has no further use for the old threshold, please release it to Quarry. —B"
const CLINIC_RECEIPT="Received: one threshold for the receiving entrance. It'll be in before the cart's next round. We've seen B's note."
const CLINIC_RELEASE="Cart's stopped rattling at the door. The old threshold by the wall is released to Quarry; we've no further use for it. Collection posted."
const SLEEVE_TAG="New one to this pattern, please. Plain side to the stone. —B"
const SLEEVE_REPLY="Sleeve received. Grit in the lining; patch is sound. Has it been going down face-first? I can reline and keep the cloth, or make new. Holding it till you say. —T"
const NELL_REPLY="Tray in. No extra. Nobody asked me. —N"
const THREAD_NOTE="Could your shelf take south-end drops when you're busy? Parcels, the odd crate. Say no if it's no. —Ren"
const THREAD_REPLY="Thread received. Shelf: tagged mending yes, freight no. —T"
const PADS_NOTE="Yes, on the yard while we clear the bench. That side isn't marked. Reline it if you like. —B"
const RELINED_TAG="Relined. Cloth's got years in it. Red side to the stone. —T"
const CHAPTER_THREE_JOBS=["tray_one","quarry_sleeve","tray_two","thread_box","kneeling_pads","relined_sleeve","tagged_mending"]
const JOBS={
 "new_threshold":{"origin":"QRY","destination":"CLN","name":"New threshold","sender":"Quarry Stores","ticket":"Collection at Quarry Stores: one stone threshold for Clinic's receiving entrance. Ask for B.","docket":RELEASE,"base":140,"reaction":CLINIC_RECEIPT,"routes":["A0","L0","L1","L2"],"pickup":"bea_first","arrival":""},
 "nell_first_tray":{"origin":"RLY","destination":"MRK","name":"Empty meal tray","sender":"Ren · Relay","ticket":"Empty meal tray to Nell at the Market hatch. Use the return crate below the receiving shelf.","docket":"","base":100,"reaction":"Tray received in the return crate.","routes":["L4","L5"],"pickup":"tray_offer","arrival":"nell_first"},
 "old_threshold":{"origin":"CLN","destination":"QRY","name":"Used threshold","sender":"Clinic Receiving","ticket":"Collection at Clinic's receiving entrance: one used threshold, released to B at Quarry Stores. Heavy.","docket":"","base":140,"reaction":"Used threshold received at Quarry Stores.","routes":["-L2","-L1","-L0","-A0"],"pickup":"old_offer","arrival":"bea_old"},
 "tray_one":{"origin":"RLY","destination":"MRK","name":"Meal tray","sender":"Ren · Relay","ticket":"Nell's tray. Return crate below the shelf.","docket":"","base":100,"reaction":"Tray received in the return crate.","routes":["L4","L5"],"pickup":"tray_one_offer","arrival":"","kind":"budgeted tray"},
 "quarry_sleeve":{"origin":"QRY","destination":"TES","name":"Quarry sleeve","sender":"Quarry Stores","ticket":"Collection at Quarry Stores: one sleeve for Tess at B11.","docket":SLEEVE_TAG,"base":120,"reaction":SLEEVE_REPLY,"routes":["A0","L0","L1"],"pickup":"bea_sleeve","arrival":"tess_sleeve","reply_to":"QRY","kind":"story"},
 "tray_two":{"origin":"RLY","destination":"MRK","name":"Meal tray","sender":"Ren · Relay","ticket":"Nell's tray back to Market. Usual return place. She'll do one more for the north crew. Bring it back up with you.","docket":"","base":100,"reaction":NELL_REPLY,"routes":["L4","L5"],"pickup":"tray_two_offer","arrival":"nell_interruption","reply_to":"RLY","kind":"budgeted tray"},
 "thread_box":{"origin":"RLY","destination":"TES","name":"Thread box","sender":"Ren · Relay","ticket":"Thread for Tess at B11. There's a note in with it.","docket":THREAD_NOTE,"base":100,"reaction":THREAD_REPLY,"routes":["L4","L5"],"pickup":"thread_offer","arrival":"tess_boundary","reply_to":"RLY","kind":"ordinary"},
 "kneeling_pads":{"origin":"QRY","destination":"TES","name":"Two kneeling pads","sender":"Quarry Stores","ticket":"Collection at Quarry Stores: two kneeling pads for Tess at B11. Straps want stitching.","docket":PADS_NOTE,"base":100,"reaction":"Mending received. Two kneeling pads for stitching.","routes":["A0","L0","L1"],"pickup":"pads_offer","arrival":"tess_reline","kind":"ordinary"},
 "relined_sleeve":{"origin":"TES","destination":"QRY","name":"Relined Quarry sleeve","sender":"Tess · B11","ticket":"Collection at B11: Quarry's sleeve, relined. To B at Quarry Stores.","docket":RELINED_TAG,"base":120,"reaction":"Relined sleeve received at Quarry Stores.","routes":["-L1","-L0","-A0"],"pickup":"relined_offer","arrival":"bea_red","kind":"story"},
 "tagged_mending":{"origin":"RLY","destination":"TES","name":"Tagged mending parcel","sender":"Ren · Relay","ticket":"Tess's shelf. Tagged mending only. I asked.","docket":"","base":100,"reaction":"On the shelf, thanks. —T","routes":["L4","L5"],"pickup":"mending_offer","arrival":"","kind":"ordinary"}
}
const SCENES={
 "bea_first":{"home":"QRY","speaker":"bea","offer":"new_threshold","lines":["You'll be the courier. I'm B. Tarp's holding. Those patches'll do.","You've come working. We've put the kettle on anyway.","Finished face on the pad. Let them put the first marks on it.","There's a note for Clinic about the old one. If they've no use for it, we'd like it back. If it comes, don't fuss. Everything's already happened to that one."]},
 "tray_offer":{"home":"RLY","speaker":"","offer":"nell_first_tray","lines":[JOBS.nell_first_tray.ticket]},
 "old_offer":{"home":"CLN","speaker":"","offer":"old_threshold","lines":[JOBS.old_threshold.ticket]},
 "nell_first":{"home":"MRK","speaker":"nell","offer":"","lines":["Don't look at the corner. That one's mine. I got here first.","'Extra greens.' I've been picking the greens off his for a year. He never said a word."]},
 "bea_old":{"home":"QRY","speaker":"bea","offer":"","lines":["Hollow between the tracks. That's feet, not the cart.","Leave it by our door. I've got a place for it."]},
 "bea_groove":{"home":"QRY","speaker":"bea","offer":"","lines":["Barrow found the old groove before I did."]},
 "tray_one_offer":{"home":"RLY","speaker":"","offer":"tray_one","lines":[JOBS.tray_one.ticket]},
 "bea_sleeve":{"home":"QRY","speaker":"bea","offer":"quarry_sleeve","lines":["It's been leaving marks on finished work. That patch sits too near the face for my liking."]},
 "tess_sleeve":{"home":"TES","speaker":"tess","offer":"","paper_panels":1,"paper_heading":"BEA'S TAG · carried with the sleeve","lines":[SLEEVE_TAG,"She wants a new one because mine shows.","Hang on. Grit, right through the lining. And 'plain side to the stone'? They're both plain."]},
 "tray_two_offer":{"home":"RLY","speaker":"","offer":"tray_two","lines":[JOBS.tray_two.ticket]},
 "nell_interruption":{"home":"MRK","speaker":"nell","offer":"","lines":["I'd only just sat down.","Ren's promised them another? I didn't say that. I've finished."]},
 "ren_answer":{"home":"RLY","speaker":"ren","offer":"","lines":["Nell's receipt came in. I told the north crew yes on my way to asking her, and never got to the asking.","I've taken it back. They were very nice about it, which was worse."]},
 "thread_offer":{"home":"RLY","speaker":"","offer":"thread_box","lines":[JOBS.thread_box.ticket]},
 "tess_boundary":{"home":"TES","speaker":"tess","offer":"","paper_panels":1,"paper_heading":"REN'S NOTE · carried in the thread box","lines":[THREAD_NOTE,"Mending, yes. Tag it and it goes on the shelf.","Crates, no. Out front's for sitting. Last box I left there, someone sat on it for an hour."]},
 "pads_offer":{"home":"QRY","speaker":"","offer":"kneeling_pads","lines":[JOBS.kneeling_pads.ticket]},
 "tess_reline":{"home":"TES","speaker":"tess","offer":"","paper_panels":1,"paper_heading":"BEA'S NOTE · carried with the pads","lines":[PADS_NOTE,"The seam held. That didn't make the lining fit to use.","New lining, same cloth, and a face you can spot from the bench."]},
 "relined_offer":{"home":"TES","speaker":"","offer":"relined_sleeve","lines":[JOBS.relined_sleeve.ticket,RELINED_TAG]},
 "bea_red":{"home":"QRY","speaker":"bea","offer":"","lines":["Well. Nobody's going to miss that.","It's good. I'd still have bought a new one. Less to check."]},
 "bea_red_return":{"home":"QRY","speaker":"bea","offer":"","lines":["Crew keeps showing me the red side. I've seen the red side."]},
 "mending_offer":{"home":"RLY","speaker":"","offer":"tagged_mending","lines":[JOBS.tagged_mending.ticket]},
 "ren_letter":{"home":"RLY","speaker":"ren","offer":"","lines":["Stop 9. 'Thank you for the jam. I have jam. Come and eat some of it with me.'","I did say I'd go."]}
}
const HEADINGS={"bea":"BEA · Quarry Stores","nell":"NELL · Market hatch","tess":"TESS · Mending","ren":"REN · Relay operator"}
static func job(id: String) -> Dictionary:
	var c: Dictionary=preload("res://scripts/courier/relay_contracts.gd").outbound()
	c.merge(JOBS[id],true);c.id=id;c.place=Opening.PLACES[c.destination];c.character=c.sender
	c.objective="NONE";c.target=0;c.bonus=0;c.objective_text="Paid delivery · any legal route"
	c.purpose=c.name+" → "+c.place+"\n"+("Release slip travels with the stone." if id=="new_threshold" else "Paid delivery · any legal route.")
	c.dispatch=c.purpose
	return c
static func available(r: Dictionary) -> Array[String]:
	var ids: Array[String]=[]
	if r.step<8:return ids
	var done: Array=r.slices.done
	if not "new_threshold" in done:ids.append("new_threshold")
	elif not "nell_first_tray" in done:ids.append("nell_first_tray")
	if "clinic_release" in done and not "old_threshold" in done:ids.append("old_threshold")
	if chapter_two_complete(r):
		if not "tray_one" in done:ids.append("tray_one")
		elif not "tray_two" in done:ids.append("tray_two")
		if not "quarry_sleeve" in done:ids.append("quarry_sleeve")
		elif not "kneeling_pads" in done:ids.append("kneeling_pads")
		elif r.slices.relined and not "relined_sleeve" in done:ids.append("relined_sleeve")
		if "ren_answer" in done and not "thread_box" in done:ids.append("thread_box")
		elif "thread_box" in done and not "tagged_mending" in done:ids.append("tagged_mending")
	return ids
static func arrival_scene(r: Dictionary,hub: String) -> String:
	if hub!="RLY" or not chapter_two_complete(r):return ""
	if "tray_two" in r.slices.done and not "ren_answer" in r.slices.done and r.pending!="nell_interruption":return "ren_answer"
	if "tagged_mending" in r.slices.done and not "ren_letter" in r.slices.done:return "ren_letter"
	return ""
static func chapter_three_complete(r: Dictionary) -> bool:
	return "relined_sleeve" in r.slices.done and "bea_red" in r.seen and "ren_letter" in r.slices.done
static func chapter_two_complete(r: Dictionary) -> bool:
	return "quarry_later" in r.slices.done and "nell_first_tray" in r.slices.done and not r.pending in ["nell_first","bea_old"]
static func summary(id: String) -> String:
	var scene: Dictionary=SCENES[id]
	if not scene.offer.is_empty():
		var c:=job(scene.offer)
		return Opening.pickup_label(c)+"\n"+c.ticket+("\n\n"+c.docket if not c.docket.is_empty() else "")
	for job_id in JOBS:
		if JOBS[job_id].arrival==id:
			return JOBS[job_id].reaction+("\n\nCarried note\n"+JOBS[job_id].docket if not JOBS[job_id].docket.is_empty() else "")
	return "\n\n".join(scene.lines)
```

---

<a id="source-9"></a>

## 9. Ivo — latest clean script

Source: [docs/story_room/reviews/2026-10-06/ivo/writer/CLEAN_SCRIPT.md](ivo/writer/CLEAN_SCRIPT.md)

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

---

<a id="source-10"></a>

## 10. Nell — latest clean script

Source: [docs/story_room/reviews/2026-10-06/nell/writer/CLEAN_SCRIPT_v3.md](nell/writer/CLEAN_SCRIPT_v3.md)

# CLEAN SCRIPT v3 — Heels for a Corner (PART 1 only, from draft-3.md · PROPOSED, not canon)

**Writer:** Hush Basin Story Writer / native Grok Bot / run nell-wants-20261006-01 / draft-3 final repair  
**Note:** Separately named per Astra. Based on CLEAN_SCRIPT_v2 / draft-2. Does not overwrite CLEAN_SCRIPT.md or CLEAN_SCRIPT_v2.md.

Nell wants to taste someone else's cooking, and she wants only the ends. She wraps her own corner piece, posts it west to Quarry Stores with a hard ask — both heels of their loaf, not the loaf — and when the heels come back she gives a short, uneven verdict at the hatch. Two paid legs, real cargo both ways, no empty return. Bea answers on paper only. Nobody is told how the tasting went.

# PART 1 — PLAYABLE SCRIPT

## 1.1 Order and dependencies

One object-chain. Ordinary work stays on the board under the one-active-parcel rule. None of it is required filler.

| # | Where | What | Kind | Requires |
| --- | --- | --- | --- | --- |
| 1 | Market hatch | Nell, face pickup: **Wrapped corner piece** | Offer; leg 1 | Chapter 3 complete |
| 2 | Quarry Stores | Anonymous receipt of leg 1 (Bea's paper note). Then no-face pickup: **Two loaf heels** | Arrival + offer; leg 2 | Leg 1 delivered and settled |
| 3 | Market hatch | Nell, face arrival of leg 2; she tastes; slice ends | Arrival scene | Leg 2 delivered |

No third portrait. Bea never appears as a face. Ren, Tess, Ivo, Stop 9, greens customer, and romance are untouched.

## 1.2 The two counted legs

Pay is fixed: 100 / 100. No timer, condition gate, or extra challenge objective. Normal parcel/destination objectives still exist (carry this parcel to that place). Any legal route completes. Highlighted routes are advisory only.

| Leg | Pickup → destination | Cargo (one parcel) | Pay | Suggested highlight (advisory) |
| --- | --- | --- | --- | --- |
| 1 | Market hatch → Quarry Stores | One wrapped corner piece, Nell's note inside | 100 | −L1, −L0, −A0 (west street run) |
| 2 | Quarry Stores → Market hatch | Two loaf heels, Bea's note with them | 100 | A0, L0, L1 |

Both legs carry real freight. Leg 2 is offered at Quarry only after leg 1 settles. There is no hidden empty return and no mandatory ordinary job between them.

## 1.3 Text

Format follows existing slices. A scene's first panel is paper where marked. Text in quotation marks is spoken by the portrait. Apostrophes are straight.

### Scene 1 — `nell_heels_offer` · Market hatch · Nell · face pickup (leg 1)

Heading: NELL · Market hatch.

1. "I've looked at my own corner long enough."
2. "I want to know what Quarry's loaf tastes like at the ends."
3. "Both heels. Ends only. Not the loaf."
4. "There's a corner wrapped for them. Note's in with it."

Pickup label: *Pickup: Market hatch → Quarry Stores*

> Collection at Market hatch: one wrapped corner piece for Quarry Stores. Note travels with it. Ask for B.
>
> **Carried note.** Corner piece, mine. Heels off your loaf, both ends, in return. Not the loaf. —N

Buttons: *Accept delivery* / *Not now*.

Advance and Skip land on the offer summary (Nell's ask plus ticket) and never accept. Not now leaves the offer at the Market hatch without cargo or payment. The first introduction panels do not replay as a compulsory fresh conversation on later Market visits after decline; local review of the offer summary / ticket remains available. The player may do any ordinary work, or none, and take the corner on any later Market visit while Chapter 3 remains complete and leg 1 is not done.

**Physical on accept:** the wrapped corner leaves the hatch with the craft. Existing return crate stays. No new prop required at pickup. Standard Nell portrait + text only.

### Leg 1 arrival — Quarry Stores · anonymous receipt, no face

Receipt footer: *Wrapped corner piece delivered · Payment +100 received*

> Corner received. Heels, both ends, for Market. Crew had the middle. —B

That paper note is Bea's whole participation. No portrait, no kettle speech, no clock. The delivery settles once before the next offer appears. In Bea's note, "the middle" means the middle of Quarry's loaf (what the crew kept); it is not Nell's delivered corner piece, and this script does not invent who took her piece.

### Scene 2 — `heels_return_offer` · Quarry Stores · no face · pickup (leg 2)

Offered at Quarry only after leg 1 has settled. Pickup label: *Pickup: Quarry Stores → Market hatch*

> Collection at Quarry Stores: two loaf heels for Nell at the Market hatch. Note travels with them.
>
> **Carried note.** Heels, both ends. Crew had the middle. —B

Buttons: *Accept delivery* / *Not now*.

Not now leaves the heels offer at Quarry. Ordinary work elsewhere is fine. Returning to Quarry later still finds the offer. No perishability, no "crew waiting," no implied timer.

**Physical on accept:** two wrapped heels become the active parcel. Bea's note travels with them. Nell's corner piece stayed at Quarry when leg 1 settled; it does not travel back. Keep the two objects distinct: her inbound corner piece is not the "middle" of Quarry's loaf named in Bea's note.

### Scene 3 — `nell_heels_verdict` · Market hatch · Nell · arrival of leg 2

Receipt footer: *Two loaf heels delivered · Payment +100 received*. Payment lands once, before any panel. Heading: NELL · Market hatch.

1. *(paper, heading "BEA'S NOTE · carried with the heels")* Heels, both ends. Crew had the middle. —B
2. "Both ends. They kept the middle."
3. "Salt's dried into this crust."
4. "I'll keep the crusty heel. Soft stays put."

Summary (after the last panel or after Skip): *Heels received at the Market hatch.* + carried note.

**What the player sees:** standard local Nell portrait + text. Optional static visit props only: reuse existing Market hatch saucer/corner-place and stool language as visit staging approximations (not a bread-heel mesh or food asset; no new art required this writing turn). Visit props, not permanent food. No new mesh, portrait, seated variant, or animation. No animated sitting, chewing, or on-screen human action beyond the ordinary portrait panel.

**End.** She keeps the verdict. Nobody carries it back to Bea. No next offer, promise, receipt channel ping, or cliffhanger. Slice resolved.

## 1.4 Decline / Skip / postpone / quit-resume (honesty pass)

| Player action | What happens |
| --- | --- |
| Decline leg 1 (Not now) | Offer stays at Market hatch. No cargo. No payment. Chapter 3 state unchanged. Ordinary board untouched. First introduction does not compulsory-replay; local review of summary/ticket remains available. |
| Quit during initial offer (before Accept) | Same as decline: no cargo, no pay; offer remains at Market for later Accept without forcing a fresh compulsory intro conversation. |
| Accept leg 1, quit mid-route | Authored parcel persists like Chapter 3 named legs: resume at saved craft position with the wrapped corner still aboard. |
| Deliver leg 1, Skip receipt panels | Pay +100 settles once; Bea's note is in the summary. Leg 2 offer becomes available at Quarry. |
| Decline leg 2 (Not now) | Heels stay offered at Quarry. Leg 1 remains done and paid. No invented trip back to Market required. |
| Accept leg 2, quit mid-route | Heels parcel persists; resume with cargo. |
| Deliver leg 2; quit during final paid-but-pending Nell exchange | Pay +100 already settled once. Pending `nell_heels_verdict` remains. On return to Market, resume the pending local exchange; do not re-pay, re-deliver, or re-open as a fresh offer. |
| Deliver leg 2, Skip Nell panels | Pay +100 settles once; summary carries receipt + Bea's note. Verdict lines may be skipped; situation is still resolved (heels delivered, trade complete). Mark scene resolved/seen; clear pending. No auto-accept of further work. |
| Ordinary work before leg 1, between legs, or after | Always allowed under one-active-parcel. Independent threads stay independent. |
| Postpone indefinitely | Fine. Quarry is not waiting on a clock. Nell's offer does not expire. |

Advance and Skip never accept work. Accept needs a fresh explicit input after the neutral-release barrier. Declining never undoes a settled leg. Settlement of each leg's pay is once-only.

## 1.5 Player-facing resume strings

Exact player-facing copy for each heels-chain state (Astra-supplied; do not paraphrase):

| State | Player-facing string |
| --- | --- |
| Offer | “Nell has a wrapped corner piece for Quarry. Collect it at the Market hatch.” |
| Outbound | “Nell's corner piece is aboard. Deliver it to Quarry Stores.” |
| At Quarry | “Quarry has two loaf heels for Nell. Collect them at Quarry Stores.” |
| Return | “Two loaf heels are aboard. Deliver them to Nell at the Market hatch.” |
| Pending final scene | “Nell has the loaf heels. Speak with her at the Market hatch.” |
| Complete | “Nell's trade is complete. Ordinary paid work is available.” |

Internal resume behavior, once-only pay/seen/pending rules, and named costs remain in the state appendix (§2.5 in the full draft). These six strings are the player-facing resume copy only.

## 1.6 What stays

Nothing permanent is required. Optional visit staging reuses the existing Market hatch saucer/corner/stool language for Scene 3 only as static approximations — that reuse is not the same as already having a bread-heel asset. Return crate unchanged. Quarry gains no new prop. No handling card, shelf label, or bench object. No permanent trophy.
