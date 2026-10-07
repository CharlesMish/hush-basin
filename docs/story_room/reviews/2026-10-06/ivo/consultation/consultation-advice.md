> Publication note: operational identifiers were omitted from metadata only; editorial/advisory wording is unchanged. See MANIFEST.json for source and published hashes.

# Sonnet consultation advice — ivo-grok-repair-20261006-01

- **Agent:** [operational identifier omitted for publication]
- **Model:** claude-sonnet-5-5 (300k, high reasoning_effort)
- **Kind:** one advisory turn only; not a draft
- **Source checkout:** 05d5506 (read-only claimed)
- **Archived:** 2026-10-06

---

**Advisory for the Grok Writer. This is advice, not a draft or a script.** I read the brief and `input-revision-1.md`, whose hash matches `bc9344c4…a7a0`. I checked the checkout at `05d5506` and edited nothing.

## A1 — Competence

- **Direction:** Make Ivo's problem the job, not his ignorance.
  - Scene 2: his plate is hollow from years of work, "plates wear where you work," the way the dies did. He is working beyond his usual standard, because press dies set against a plate he made would only agree with his own hand.
  - Scene 6: Bea's note carries one stone-specific fact in place of "three feet." For example, this lift is soft and takes grit. Ivo answers as a professional, e.g. "Soft. Then oil, and the grit stays off it."
- **Risk:** Any stone fact is new lore, so keep it to one fact.
- **Don't touch:** "Anything I true on it, I'm only agreeing with myself. I want a flat I didn't make." Also leave Bea's dryness and "same lift."

## A2 — Player flow

- **Direction:** Replace the >90 m flag with a readiness event, `faced`, set when any counted delivery settles after the offcut arrives.
  - Scene 6 ends with Ivo saying plainly that he'll have the dies when the courier has been back from another delivery.
  - The Works→Market pouch qualifies, and so does any other paid job.
  - The dies are offered at the next Works arrival, and the player can decline.
  - Resume sentence: "Ivo is re-facing Depot's dies. He'll have them after your next delivery."
  - Save: `faced` is persisted.
- **Risk:** One further paid delivery is required. Say so openly and don't call it optional. It is real paid work, not a naked out-and-back.
- **Fallback if that is too heavy:** Cut the wait entirely. Ivo finishes in-scene and Scene 7 follows on the same visit. That removes the `faced` flag and the save migration.
- **Don't touch:** the one-parcel rule and the any-route rule.

## A3 — Physical clarity

- **Direction:** Make the comparison legible. Bea's lamp beat becomes spoken results on the offcuts, not pointing at faces ("first has light under the middle, second rocks, this one's clear"). Keep the flip, since it tells her stone error from steel error.
- **Re-faced part:** The flat counter-die or anvil face is lapped. The engraved die is checked and left alone. A hollowed counter-die presses the lead unevenly, which gives a half-struck seal. Scene 2 ("meet at the rim") and the Depot ticket must match this.
- **Risk:** The press mechanism is invented. The source has no press, so keep it to one sentence and lecture nothing.
- **Don't touch:** "Somebody checked this twice" in spirit, and the lamp-against-his-plate payoff.

## A4 — Factual hygiene

- **"Blanks":** `alpha_contracts.gd:8` has `"name":"Freight seals"`, dispatch "Fresh seals for the freight office.", and reaction "Seals counted. The next load can leave." `relay_contracts.gd:14` repeats "Fresh seals for the freight office. Take any line you like." Neither says blanks.
  - "Seals counted" implies finished seals arrive at Depot, so my "blanks" claim contradicts the source.
  - Delete the blanks parenthetical in §2.6 and §2.9.1. Make the press strike Depot's own lead load tags, separate from Market's seals.
- **Ivo and Bea:**
  - `CHARACTER_LEDGER.md:44` says Ivo's "extent of contact with Tess, Bea or Nell" is not established.
  - `CHARACTER_LEDGER.md:92-93` says Bea's "personal familiarity with Ivo" is not established.
  - Both are unknown, not "never met." So revise §2.6 ("No meeting is shown") to "familiarity unspecified; none shown or required."
  - The ticket "Ask for whoever dresses the stone" (line 75) reads as ignorance. Neutralise it, e.g. "Ask for B."
  - I withdraw my R0-N5 dispute, which rested on never-met.
- **One active parcel:** Line 191 ("takes the dies, then does an ordinary Market job first") violates it. Reword: ordinary work before accepting, or after settling.
- **Other claims to make consistent:**
  - Dies sitting on the bench from leg 1 until pickup.
  - "While you're away" in §1.4, §2.3 and Scene 6.
  - "It'll keep" and the hand stamp.
  - The Depot receipt "struck whole."

## Protect

- Ivo lending his edge ("You carried the receiver…").
- "Depot's managed a month. It'll keep."
- Bea's lamp tests and "Offcut from the Clinic stone, same lift."
- Scene 7: "I could keep going. It stops being for Depot about here." and "Nobody there will lay an edge on them."
- The anonymous Depot receipt ending, with nobody told.
