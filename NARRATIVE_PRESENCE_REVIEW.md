# Narrative Presence Lab v0.1 — implementation record

Owner play is pending. Correct dialogue, state transitions, or name recall do not
establish attachment. Stop here for Charlie's playtest; do not add another arc or
character in response to a weak result.

## Authority and provenance

Starting local branch: `review/rens-receiver-v0.1`.
Starting HEAD: `1afd28a253a3dbc0387cd3f339e5a56ab29dabf4`, clean before Godot import.
Its publication record identifies candidate
`6570619b7bff67140bec03039942585208b5a8be` as the playable source.
Implementation branch: `feature/narrative-presence-v0.1`.
Runtime implementation commit: `891d911e4108d7e937d8cc62a30f12a604035dff`.
No main update, push, deployment or external account action.

The owner's Narrative Presence request supersedes the historical M5, world,
vehicle and Web-only scope restrictions for the explicitly requested narrative
slice. The v0.2 bible and complete editorial review were read before source edits.
The owner's exact approved script overrides their alternative wording. Neither
attachment is authority for the deferred character/campaign proposals.

The untouched current candidate passed its 57-check native comprehension and
integration fixture with the exact installed
`4.7.1.stable.official.a13da4feb`, Metal Forward+ on Apple M5. Baseline evidence
also includes the 1,260-tick movement trace and original dialogue captures.
Historical checksum validators retain their expected successor/publication
mismatches; their frozen expectations were not rewritten.

## Architecture and unchanged systems

`narrative_director.gd` extends the existing Relay director. It intercepts only
the finite story offers, first handoffs, review, resume and reset. The existing
arrival observer, Cargo, session acceptance/settlement ledger, optional
challenges, BRRR, drift, controls, movement, camera, collision and city data are
unchanged. The historical Relay scene remains independently runnable.

`narrative_text.gd` owns the exact lines, short summaries and three story cargo
definitions. `narrative_panel.gd` is a single stopped UI panel with two portrait
resources and Advance/Back/Skip/Accept/Decline signals. It contains no game rules.
`narrative_hud.gd` retains the three-card board and ordinary challenge HUD, adds
local review/reset, concrete resume language, and the short Quarry receipt.

Conversations use the existing paused-tree convention. They open only from a
deliberate stopped interaction or the existing settled-delivery gate. Text is
immediate; there is no typewriter, reading timer or auto-advance. Driving shows
only the compact cargo purpose strip and essential controls/receiving prompt.

Every final line/Skip enters a summary with acceptance disabled. The director
tracks actual key/button release events and requires two neutral process frames
before a fresh acceptance edge. It consumes story input before inherited
gameplay handling. Pointer input reaches GUI buttons; acceptance callbacks obey
the same guard. Skipping Relay applies the handoff, then shows the unaccepted
Quarry summary. Past-exchange review has no acceptance or payment side effects.

Works pays/completes leg one before its conversation/offer. Relay holds leg two
at the settled handoff until the conversation is advanced or skipped, then uses
the existing once-only payment/contribution path. Only after that can the Quarry
ticket appear. Ordinary replays do not replay introductions or reinstall anything.

## Exact dialogue

**Market — REN · Relay operator**

1. I’m Ren, from Relay. I told Quarry we’d be taking requests today.
2. The last parts just came in. Ivo’s got the receiver core. He doesn’t know I said today.
3. Could you run these to Works? And maybe mention the today part.

**Take kit to Works / Not now**. Receiver kit → Ivo · Works.
Last parts for Ren’s receiver.

**Works — IVO · Fabrication**

1. Ren promised today? She used to book my whole afternoon with that word.
2. That finishes it. I made the dial bigger, since she won’t take those gloves off.
3. Tell her I’ll clear off her chair, if she has time for tea.

Receiver kit → Finished receiver. **Take receiver / Leave it here**.
Finished receiver → Ren · Relay. Restores Relay dispatch.

**Relay — REN · Relay operator**

1. Look at that dial. He remembered the gloves. Thanks for bringing this.
2. Tell him I’ll—no. I’ll go over after close.

Immediately above panel two: **You pass on Ivo’s invitation.**
Then install, light the indicator, pay, and activate local dispatch.

**QUARRY STORES**

Six pairs of dry socks, please. The old ones are drying on the kettle.

Ren: Six pairs. I’ve got those on the rack. Want the Quarry run?

**Take Quarry parcel / Later**.

**Quarry receipt**

Six pairs received. We can have the kettle back.

The character dialogue is 114 whitespace-delimited words; the anonymous receipt
adds nine. The ticket, captions and offer summaries are unspoken UI. No duration
is enforced and no claim is made about human reading time.

## Portrait assets

`game/presentation/narrative/ren.png` and `ivo.png` are original temporary
illustrations generated with the built-in imagegen tool, one state each. No
scraped character art, third character or expression system. Their Godot import
settings limit runtime textures to 512 pixels, displayed at roughly 238 pixels
wide. Replacing these two resources replaces the portraits without code changes.

Prompt for Ren: one original square prototype dialogue bust, late-30s woman,
lean angular silhouette, slightly weathered expressive face, cropped dark hair
under a low angular cap, muted teal worn work coat, clearly visible leather
gloved hand holding a plain docket, rueful amused half-smile, task-oriented
eyeline to viewer's right. Broad readable painted shapes, mineral steel/brick/
plaster colors, overcast light, plain dark warm-gray backdrop. No text, logos,
anime/RPG-stock styling, fantasy embellishment or facial variants.

Prompt for Ivo: one original square prototype dialogue bust, early-50s man,
broad rounded silhouette, short silver curls, open attentive face, contained
amusement and approachable warmth, direct eyeline. Rolled sleeves and practical
ochre canvas apron over gray shirt. Matching broad painted shapes, worn fabric,
mineral palette, overcast light and dark warm-gray backdrop. No text, logos,
generic anime/RPG styling, fantasy tools or facial variants.

These are richer than the geometric world presentation. That stylistic contrast
and the single-expression limit may influence attachment and must be considered
when interpreting the test.

## Minimum physical anchors

`narrative_anchors.gd` adds only native meshes and two plaques at the existing
receiving pads: Works `(90,-55)` and northern Relay `(0,-210)`, each offset
`(+5,-4)` metres. No collision, route edits, world-data regeneration, camera
reveal, human models, audio or dynamic lights.

Works: a practical bench with a lit strip, incoming parts/core, the finished teal
receiver with a large brass dial, and a nearby chair occupied by a parts crate.
The chair stays occupied throughout this first test; no later tea-scene payoff.

Relay: work surface, bracket, indicator, small rack and outbound parcel. The
receiver is the same construction as Works. It rests forward on the surface
during Ren's exchange, then moves into the bracket and lights its indicator.
The parcel appears only after activation and leaves when accepted. The prior
distant annex consequence remains intact but is no longer the sole local payoff.

The anchors intentionally remain simple, small and non-colliding. Visibility
varies with the player's approach. This is not a full Works/Relay design pass.

## Persistence and reset

The existing project store and `relay_annex_project_v01.json` remain unchanged.
The narrative store uses `narrative_presence_v01.json` in the same existing user
data directory. On first launch only, it reads the older two completion flags
and imports them without modifying the older file. An existing completed owner
save therefore needs the explicit reset for a fresh narrative test.

One validated, atomically replaced document contains the same two project flags,
seen conversations, pending handoff, story parcel/checkpoint and Quarry receipt
flag. It saves on acceptance, contribution, conversation completion, cargo change
and normal close/suspend. Invalid storage is reported; it is never silently
discarded. Reset Narrative Experiment confirms and resets the full new document.
Old saves, ordinary challenges, session Credits/liner/mastery retain their prior
semantics. Session rewards still reset on exit.

Concrete resume states:

- Fresh: Ren is at Market with the last receiver parts.
- Kit aboard: Ren’s receiver kit is aboard. Deliver it to Ivo at Works.
- Works complete: Ivo finished Ren’s receiver. Collect it at Works.
- Receiver aboard: Ren’s receiver is aboard. Deliver it to Relay.
- Relay active: Relay is working. Ren has dry socks ready for Quarry.
- Socks aboard: Six pairs of dry socks are aboard. Deliver them to Quarry Stores.
- Complete: Relay is working. Quarry received the dry socks.

Interrupted Works/Relay handoffs reopen their short exchange; finished
introductions do not automatically replay. Active story cargo resumes at the
saved position in Spread at rest, retaining condition and elapsed delivery time.
It does not preserve instantaneous velocity or session driving statistics.
This occurs only at application launch. No runtime movement correction is added.
Ordinary challenge runs retain their existing session-only behavior.

Browser persistence depends on its local filesystem/IndexedDB synchronization.
An immediate forced process kill before that synchronization is not an atomic
cloud-save guarantee. No cloud services or analytics were added.
Eight fresh native processes verified saved arc stages (37 checks). Nine actual
browser tab close/reopen cycles verified saved states (41 checks); a full browser
process kill was not tested. The raw Web shell retains its high-DPI canvas sizing
limit and occasional arrow-glyph differences; native Forward+ is the visual
review authority.

## Playtest boundaries

Use only START_NARRATIVE.md and the launcher before playing. The implementation
record and screenshots are reviewer evidence, not an emotional walkthrough.
Charlie already knows the script; prior knowledge, prototype portrait/world
contrast, anchor readability and the known earlier city performance limitations
can contaminate this test. Physical gamepad, comfort, causal comprehension,
character distinction, perceived relationship, attachment, voluntary reading
time and continued desire to drive remain owner-only and unpassed.

If the two still feel interchangeable, or conversations make work tedious, stop
and return that evidence. Do not add prose, romance, backstory, cast or quests.

Exact commands, final counts, artifact sizes and package validation are recorded
in STATUS.md and the adjacent review evidence directory.
