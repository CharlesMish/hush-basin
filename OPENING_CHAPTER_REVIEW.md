# Opening Chapter v0.1 — implementation and owner-review record

The owner reported Narrative Presence Lab as passing strongly enough for this
bounded expansion. That is the starting evidence, not a pass for the new chapter.
The principal question is whether connected character work feels like the
beginning of a real game while leaving the player eager to drive.

## Provenance and scope

Started clean on `feature/narrative-presence-v0.1` at
`d8e921068819a86ca888aaa26d9bfbb9fb8e4476`. Implementation branch:
`feature/opening-chapter-v0.1`. Exact installed engine:
`4.7.1.stable.official.a13da4feb`, native Metal Forward+.

The complete September 25 Opening Chapter Narrative Plan was read before edits.
The owner's explicit request authorizes implementation of sections 2–6 and the
concrete scope in section 13, overriding its “planning only” heading and earlier
lab scope restrictions. Section 9 is not implementation authority. No Bea
portrait, Sena, Market character, relationship system, Chapter 2, campaign,
handling change or production deployment is included.

The accepted narrative scene remains independently runnable. Its files and
existing regression fixtures remain unchanged; the historical lab launcher now
names its old scene explicitly because the default entry is the new chapter.
No main update or external publication is part of this candidate.

## One connected candidate

`PLAY_OPENING_CHAPTER.command` runs one scene, `review/opening_chapter/review.tscn`.
The sequence is Market mail → Ren at Relay → Ivo at Works → receiver at Relay →
Quarry socks → Tess at her south counter → Depot jackets → Clinic aprons →
Tess's repair bag and patch → ordinary paid work → Tess's patch kit → Quarry.
Arc transitions never launch another application or replace the craft/world.

The eight authored cargo legs have no deadline or condition gate. All pay the
fixed delivery base through the existing session ledger. Ordinary paid work and
the original optional challenges remain available at Market. Local institutional
post pouches provide ordinary work at other receiving points; after opening,
Tess offers repeat mended-work pickups to Depot. None adds a named character.

The coda unlocks after Tess's final exchange plus one later completed job. A
reset, cancellation, visit, skipped conversation or repeat settlement does not
count. The optional Ren/Ivo lines unlock after the Quarry socks delivery plus
one other completed job, which can be the jackets delivery. There is no clock or
relationship meter behind either condition.

## Narrative and input architecture

Six small chapter scripts extend the retained courier director, portrait panel,
HUD, atomic project store and visual anchor helpers. `chapter_text.gd` is the
single text/cargo catalog; it is not a branching conversation engine.

Portrait identity is tied to a local interaction ID. The director rejects a
portrait interaction away from that person's own receiving point, including
reviews. Ren appears only at Relay, Ivo only at Works, Tess only at B11. Market,
Depot, Clinic, Quarry and Ren's routed note elsewhere are text-only.

Text appears immediately. Advance, Back, Skip, explicit acceptance and neutral
input release semantics remain. Skip moves to the essential offer/handoff
summary and never accepts. The final advancement event cannot accept the offer
it reveals. Held input must release and two process frames pass before a fresh
acceptance edge. Pointer callbacks obey the same gate. User-visible reading
time is never forced. Reviews and optional return lines never load work or pay.

Mail, kit, jackets and aprons settle/pay before offering the next cargo. The
receiver settles/installs after Ren's exchange. The repair bag pays on delivery;
Tess's patch appears after advancing/skipping her final exchange. Declining a
next offer preserves all earlier deliveries. After the last receipt the player
remains at Quarry and can continue ordinary work.

Conversations open only at the existing settled-arrival gate or a deliberate
stopped interaction. During them the existing paused-tree convention freezes
simulation. The driving HUD keeps a small purpose strip; authored story jobs do
not display an elapsed-time challenge. Controller, tuning, camera, collider,
routes, BRRR, drift, cargo loss and optional challenge formulas are unchanged.

## Exact implemented text

The approved plan's wording is implemented in `game/scripts/courier/chapter_text.gd`.
The only dialogue adaptation is the craft surface noun and its damage description:

> Your rear panel’s scuffed along the edge. You take every corner like that?

This replaces the draft cargo-cover seam, because the accepted craft has no cloth
cover. No other character rewrite was made. The Ren/Ivo receiver and dry-socks
exchanges are preserved. Market uses the anonymous receiver-down lead and the
Relay-mail card. Ren's revised three-panel introduction is at Relay. Depot and
Clinic receipts, Tess's two three-panel exchanges, her one-panel coda, both
optional return lines, the routed Quarry ticket and “—B.” receipt use the plan's
text, with typographic apostrophes. Offer labels and compact summaries are UI.

The implementation text file travels in the source package for exact inspection;
screenshots show the actual layout. Do not give this record to a fresh playtester
before playing.

## B11 validation before modification

Authoritative geometry: B11 is centered at `(40,95)`, footprint `18×14 m`, with a
raised `5.5 m` foundation. The north frontage is the relevant face. Runtime
physics rays found ordinary ground through z=84 and the raised plinth at z=86;
the building itself begins farther back. A stop on the building footprint would
have been misleading.

The new interaction disk is `(40,77)`, radius `4 m`; the modest counter is at
`(40,83)`, below the north frontage. Before adding it, normal-input tests drove
there from Market and Clinic with zero resets. The native before view and a
45-point terrain/collision sample are retained in `evidence/baseline/`.

Minimum clearance from the contact disk to the established operational corridor
is **47 m for HOP** and **46.215 m for DOG**, computed from the authoritative
baked polylines and their operational half-widths. Added furniture has no
collision shapes. The default aprons advisory uses S0 → DOG → S1; HOP and inner
streets remain legal. The complete normal-input chapter traverses the South Cut.

The live native labels were `TEA & REPAIRS`; `TEA & MENDING` appeared in a separate
unused presentation dataset. This candidate explicitly replaces only B11's two
live label texts with TEA & MENDING and brightens the MENDING portion when open.
It does not silently substitute or regenerate the city presentation dataset.

## Physical consequences and craft treatment

Relay retains the same accepted receiver construction and installation. Before
the first visit its indicator is dead, the parts case waits on the counter and
the delivered mail bundle appears there. Ren is met at that same counter.

B11 starts with jackets and a half-unpacked crate. After the repair bag arrives,
the unpacking crate is gone, finished work hangs, the MENDING sign is lit, and
separate incoming/outgoing shelves remain. Depot has a small apron table which
clears when the aprons are collected. These are sparse, non-colliding additions;
the receiving geometry and camera are unchanged. TEA has no dialogue.

Inspection found rigid body/shell surfaces and eight folding leaves, not a cloth
cargo cover or cargo strap. The chosen surface is the existing rear starboard
inner leaf (`VisualRoot/RearStarboardRig/SocketSlide/YawPivot/HaunchPivot/InnerLeaf`).
Its top is at local y=.028; the patch occupies .23×.27 m within its flat top.
A few fine scuff marks are visible before Tess's exchange. A muted cloth-colored
protective patch with brick-colored stitch marks covers them afterward.

The patch is a small child mesh, following the existing leaf's authored transform.
It changes no original vertex, rig channel, collider, material, animation timing,
controller field or mechanic. It is a protective surface repair, not a claim
that Tess welds the craft. It remains visible after reset/relaunch until the
chapter itself is explicitly reset. No repair statistic or upgrade is awarded.

## Tess portrait

One original temporary portrait, `game/presentation/narrative/tess.png`, generated
with the built-in imagegen tool. Ren's existing image was a style reference only.
The prompt requested a late-20s compact, assured mender in a brick-red practical
coat, tape measure, pinned-back sleeves and practical hands, looking down out of
frame toward the craft with mild amusement. Restrained painted realism, worn
cloth, mineral colors, overcast light, plain warm-gray background; no text,
logos, anime stock styling, flirtation, craft depiction or additional characters.
It imports at at most 512 pixels and displays at the existing portrait size.
Ren and Ivo's assets remain unchanged. No expression system was added.

## Persistence and reset

`user://opening_chapter_v01.json` is separate from both earlier experiments.
First launch is fresh; no old completion flags are imported. One validated,
atomically replaced record contains chapter step, seen exchanges, pending
handoff, active authored cargo/checkpoint, patch and the two intervening-job flags.
Earlier lab saves are never modified or reset. Corruption is visible and blocks
progress until explicit reset. Failed writes preserve the prior document.

Active authored cargo resumes at its saved position, in Spread at rest, with
condition and elapsed delivery time. Pending handoffs reopen at their actual
local point. Finished introductions stay finished. Ordinary contracts, Credits,
liner and mastery keep the existing session-only semantics. The save captures
acceptance, contribution, conversation completion, cargo-condition changes and
normal application close/suspend. It is not a cloud save or crash-proof browser
process-kill guarantee.

Resume language names concrete work: mail at Market; receiver parts at Relay;
finished receiver at Works; socks at Relay; Tess opening at B11; aprons at Depot;
repair bag at Clinic; Tess's open counter; the routed Quarry request; or the final
patch receipt. Aboard cargo is named with its actual destination. No percentage
or abstract project-completion label is the primary resume information.

Reset Opening Chapter confirms, clears the entire chapter and patch, and leaves
the player where they are. The first parcel waits at Market. It does not reset
the owner's older lab or session rewards.

## Pacing hypothesis and contamination

**Tess's jackets leg is intentionally retained and is the suspected pacing weak
point.** It is a playtest hypothesis, not protected content. The current geometry
supports it, so there was no technical reason to cut it. Watch for impatience
there and on Relay ↔ Works. If the chapter feels padded, report that evidence;
do not expand the cast or prose to compensate.

A scripted normal-input run recorded approximately five minutes of driving
samples, including required repositioning and the intervening job. It is an
expert route-following fixture with rapid dialogue advancement. It does not
establish a 20–30-minute human experience. No travel or dialogue was padded to
reach a target. Measure actual first-play duration, reading, exploration and
continued desire to drive separately.

Potential contamination: Charlie knows the earlier script and approved plan;
the richer portraits contrast with the geometric world; the patch is small;
counter noticeability depends on approach; inherited city performance and Web
presentation limits remain. The small scuff marks are authored starting wear,
not damage inferred from this play session; Tess's line is not a driving grade.
A player unfamiliar with the scripts is particularly
valuable. No owner/new-player attachment, pacing, location comprehension,
physical-gamepad or comfort gate is inferred from automated checks.

Verification, final commit, exact commands and package identity are recorded in
STATUS.md and the adjacent review evidence. Stop for owner review.
