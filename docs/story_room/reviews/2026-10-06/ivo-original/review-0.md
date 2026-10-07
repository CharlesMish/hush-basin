# Review 0: Examiner pass 1 (ivo-slice-20261006-01)

- **Verdict:** READY WITH MINOR NOTES. Suitable for Charlie's review. Not canon, not owner acceptance, and not authority to implement.
- **Artifact:** `draft-0.md`, SHA256 `2931de462b8d88f5edc1120892b93842f9beee9ef5d82dfaa7678fd293307670`. Recomputed: 16800 bytes, 235 lines, 2967 words.
- **Packet:** manifest `0baa97baf2ccfbc2135f3cb168554dc1821076dc7b283fe368ae0b5ad9704c7a`.
- **Source:** tooling `05d55064a1013483b869dba0bc9d2d1906a24b6b`; game `5be7fee` (identical `game/` tree).
- **Method:** read the full draft against CHARACTER_LEDGER (Ivo, Bea), STORY_CANON_CURRENT, WORLD_AND_ROUTE_STORY_MAP, WORLD_STATE_LEDGER, SEED_PAYOFF_LEDGER, NARRATIVE_RULES, HEADINGS in `slices_text.gd`, ordinary `freight_seals` job, and the assignment brief. Route advisories checked against the road table.

## 1. Blocking findings

None.

No evidenced character, continuity, geography, state or game-rule contradiction. The draft stays inside the brief: Ivo-centred, Bea as the one other portrait, anonymous Depot, Chapters 2–3 preserved, Stop 9 untouched, no new portrait/road/system/emergency.

## 2. Nonblocking findings

### Continuity / design (decisions for Charlie, not automatic repairs)

- **R0-N1: Depot seal press is a new institutional fact.** The ordinary Market→Depot `freight_seals` job already moves seal blanks. A press that stamps them at Depot is a small, coherent invention, and the draft already marks it as unresolved decision §2.9.1. Leave it for Charlie. Do not treat it as a silent established fact.
- **R0-N2: Leg 1 is the weakest bridge, as the writer says.** Depot→Works carries the problem to Ivo. It earns the drive mainly by changing understanding (Ivo's want) rather than geography or physical situation. Under NARRATIVE_RULES §1 that is a flag, not a cut. Four legs is the honest smallest chain if the dies must be witnessed. Alternatives (unwitnessed delivery; starting mid-problem) invent worse facts. Keep unless Charlie prefers a three-leg reshaping.
- **R0-N3: Star geometry.** All four legs touch Works. Variety comes from Depot/Quarry endpoints and from the deliberately different suggested lines (leg 2 technical northern shelf; leg 3 street arterial for heavy stone; leg 4 unhighlighted). Acceptable for a Works-centred slice; call it out in human review so nobody mistakes it for city-wide coverage.

### Geography / routes

- **R0-N4: Leg 2 advisory (−R0, −L4, −X0) is legal.** Works→GN (−R0), GN→Relay (−L4), Relay→Quarry (−X0) matches the road table. Leg 3 (A0, L0, L1, L6) is the street path Quarry→GW→Depot→Market→Works. Both are suggestions only; any legal route still completes. The optional drop of R0/X0 if edges prove unfriendly (§2.9.6) is fine.
- No invented roads, districts or southern-gate misuse.

### Character / information

- **R0-N5 (taste, not blocker): Scene 3 ticket says “Ask for whoever dresses the stone.”** The courier already knows Bea from Chapters 2–3. The caution is understandable (Ivo may not name her), but the ticket is slightly coy for the player. Soft alternative: “Ask for B at Quarry Stores.” Preference only.
- Information channels (§2.2) are clean. Notes travel with cargo. No telepathy. No reply trip for the first whole seal (player-only receipt). Ivo↔Bea stay notes-and-tool acquaintances, which matches Bea's ledger (“personal familiarity with Ivo” not established).

### Implementation / feasibility

- **R0-N6:** Save-validation migration (`slices` key count, new `faced` boolean, chapter-3 gate) is correctly named as the largest risk. Props as four boxes + optional dies boxes, no collision/camera change, is honest and modest. Unverified playtest question (whether the pale plate reads at normal arrival) is correctly left open.
- `HEADINGS` lacking `ivo` is verified at `slices_text.gd:50`. `ivo.png` exists. One-line heading addition is real and small.

### Scope / must-not checklist

Preserved: Opening and Chapters 2–3 consequences; receiver/Tess shelf/Clinic and Quarry threshold/red sleeve left alone; Ren overpromise pattern not revived; sleeve patch not reopened as failed; Tess not turned into freight; Nell refusal untouched; no new portrait, biography dump, romance label, road, progression system, mechanical upgrade or compulsory emergency. “It'll keep” keeps Depot's inconvenience ordinary.

## 3. Strongest material to protect

- **Scene 2, panels 2–5.** Ivo's present-tense want is fabrication-native: he will not true dies on a plate he made and knows is hollow. “Anything I true on it, I'm only agreeing with myself. I want a flat I didn't make.” That is a new side of him that does not replace the person we met, and it does not orbit Ren.
- **“Depot's managed a month. It'll keep.”** Keeps stakes practical and refuses emergency framing.
- **Lending the edge / “You carried the receiver.”** Trust earned through prior work, without a biography dump or Ren-centred apology.
- **Scene 4, Bea's lamp tests.** Dry, material, specific. “End for end, same both times. Somebody checked this twice.” / “This one's clear to both ends. Offcut from the Clinic stone, same lift.” Reuses Chapter 2 stone work as ordinary leftover, not a new mystery.
- **Bea's seating note and Scene 6.** “Three feet under it, not a bench.” Ivo's “Three feet. I'd have laid it on the bench.” then the lamp check against his own hollow plate (“You could read by that.”) is the earned character beat of the slice.
- **Scene 7.** “I could keep going. It stops being for Depot about here.” / “Nobody there will lay an edge on them.” Precision and appetite without a lesson speech.
- **Ending discipline.** Anonymous Depot receipt; nobody tells Ivo or Bea; no next-assignment promise. Curiosity stays in the plate on the bench.
- **Self-critique in §2.8.** Naming leg 1 as the weakest bridge and star geometry honestly is the right posture for this room.

Do not thin Scene 2's technical talk into generic warmth. If anything feels dense, the writer's own cut target (Scene 2 panel 3) is the least damaging; prefer keeping it.

## 4. Proposed continuity-ledger changes (conditional on Charlie)

Agree with §2.6 as proposals only:

1. Depot owns/operates a seal press whose dies can be re-faced at Works (ties to existing freight-seal blanks job).
2. Ivo's bench plate is his make and had a hollow; he keeps a straightedge he does not normally lend; he prefers checking against a flat he did not make.
3. Bea can test steel against stone; respects a twice-checked edge.
4. Clinic-stone offcut becomes a three-footed plate on Ivo's bench.
5. Ivo and Bea remain note-and-tool acquaintances; no meeting shown.

## 5. Questions that could materially change a revision

Only Charlie's choices from §2.9, reframed:

1. May Depot own a seal press?
2. Keep four legs, or reshape to drop/repurpose leg 1 or 4?
3. Accept the plate-on-three-feet prop (dies prop optional)?
4. Keep “You carried the receiver”?
5. Keep the R0/X0 highlight on leg 2?

None of these is an evidenced continuity blocker. No examiner-forced rewrite is required for acceptance of this draft as a proposal.

## 6. Coverage

| Dimension | Assessment |
| --- | --- |
| Character fidelity | **Clear / strong.** Ivo has his own want, judgement and stopping point. Bea stays dry and material. Neither becomes an exposition machine or Ren satellite. |
| Relationships | **Clear.** New connection is earned through witnessed notes and a tool. No backfilled friendship. |
| Geography and objects | **Clear.** Contacts and cargo scale fit. Routes are legal advisories. Offcut + strapped edge as one parcel matches pads precedent. |
| Courier-leg necessity | **Mostly clear.** Legs 2–3 are strong; leg 4 closes paid work; leg 1 is the weak but honest bridge (R0-N2). |
| Story and driving | **Clear.** Any-legal-route; no hop obligation; service-bar choice retained on L6; deliberate variety in suggested lines; interruption is voluntary departure for the >90 m work flag. |
| Persistent consequences | **Clear.** One modest permanent plate; dies temporary; Depot press change is receipt-only. Cost labeled. |
| Narrative economy | **Clear.** Player-facing panels are short. Appendix length is for implementers, not padding play. No universal wit/coziness. |
| Social web | **Clear.** Cast limited to Ivo + Bea + anonymous Depot. |
| Continuity and causality | **Clear.** Gate on `chapter_three_complete`; sequential chain; pending/resume named; no optional-return dependency. |
| Feasibility | **Clear.** Reuses existing primitives; largest risk (save migration) named honestly. |

**Unverified:** static source only; no live playtest of plate readability or R0/X0 feel. Billing unknown to Examiner.

## Disposition

Send the complete report to the **same** writer agent for revision turn 2. A revision that preserves the strong scenes and only adjusts what Charlie or the writer choose among R0-N1…N5 / §2.9 is appropriate. An explicit no-change artifact is also acceptable if the writer judges the notes as human-decision items rather than draft defects. Do not invent a problem to justify edits.
