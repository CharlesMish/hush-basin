# Hush Basin — story second-opinion packet

Two proposed slices, their drafts and reviews, and the story that precedes them.
Prepared for Charlie's independent second opinion on October 6, 2026.
This branch publishes documentation only. Neither proposal is in the game.

## Start here

For one file to give another thread, use the
[second-opinion packet](SECOND_OPINION_PACKET.md): existing story summaries,
exact implemented dialogue, then both latest clean scripts. It deliberately
leaves the detailed editorial verdicts in separate files so the reviewer can
form a view before reading them. The [review request](REVIEW_REQUEST.md) can be
pasted alongside it. Using GitHub's **Raw** view makes the full text easy to copy.

| Proposal | Latest script | Full proposal and implementation notes | Current disposition |
| --- | --- | --- | --- |
| Ivo — *A Flat He Didn't Make* | [Clean script](ivo/writer/CLEAN_SCRIPT.md) | [Draft 2](ivo/writer/draft-2.md) | Accepted as a writing candidate; unimplemented; no owner-play result |
| Nell — *Heels for a Corner* | [Clean script v3](nell/writer/CLEAN_SCRIPT_v3.md) | [Draft 3](nell/writer/draft-3.md) | Held, not editorially accepted; run closed at repair cap; unimplemented |

These are separate proposals after Chapter 3. Nell's brief did not depend on
implementing Ivo. Their order here is review history, not a newly approved
chapter order. A second opinion may disagree with either verdict.

## Story leading up to this

Implemented authority is `5be7feeef34dbed468e007f5ff4de594d41b0f80`:
Opening Chapter with accepted Tess/contact, origin and route-advisory fixes,
followed by Chapters 2 and 3. This publication starts from tooling commit
`1134720153d7006a57655c625feca54ba4d7b054`. Game files and the six canon ledgers
are unchanged.

| Context | Source |
| --- | --- |
| Current story, characters and unknowns | [Canon](../../STORY_CANON_CURRENT.md), [character ledger](../../CHARACTER_LEDGER.md) |
| Physical consequences and possible seeds | [World states](../../WORLD_STATE_LEDGER.md), [seed ledger](../../SEED_PAYOFF_LEDGER.md) |
| Actual contacts and durable constraints | [World/routes](../../WORLD_AND_ROUTE_STORY_MAP.md), [narrative rules](../../NARRATIVE_RULES.md) |
| Opening Chapter authored plan | [Opening plan](../../../OPENING_CHAPTER_PLAN_V0_1.md) |
| Chapter 2 authored script | [Quarry v1.1](../../../QUARRY_SLICE_V1_1.md) |
| Chapter 3 authored script | [Chapter 3 v1.1](../../../CHAPTER_3_SLICE_V1_1.md) |
| Exact implemented dialogue | [Opening catalog](../../../../game/scripts/courier/chapter_text.gd), [Chapters 2–3 catalog](../../../../game/scripts/courier/slices_text.gd) |
| Implementation limits and recorded validation | [Opening review](../../../../OPENING_CHAPTER_REVIEW.md), [UX correction review](../../../../OPENING_CHAPTER_UX_REVIEW.md), [slices review](../../../../NARRATIVE_SLICES_REVIEW.md) |

Plans can contain deferred sketches. They do not establish those sketches as
implemented events. Ledger voice examples are evidence, not mandatory
catchphrases. Use the exact dialogue and implementation reviews when the
distinction matters.

## Drafts and review trail

- [Ivo history](ivo/README.md): Sonnet advice, both Grok drafts, Examiner findings,
  Astra's repair direction and acceptance, plus provenance corrections.
- [Original Ivo proposal](ivo-original/README.md): the earlier Sonnet drafts and
  Examiner response that preceded the Grok repair pilot. Historical, superseded.
- [Nell history](nell/README.md): assignment, Sonnet advice, all three drafts,
  Examiner report, both repair directions, responses and final hold decision.
- [Provenance and publication limits](PROVENANCE.md), including which metadata
  was omitted and which historical labels should not be taken literally.
- [SHA-256 manifest](MANIFEST.json) for this publication, excluding itself.

The [loop specification](../../LOOP_SPEC.md) explains the working arrangement:
Astra directs and makes the editorial call; Grok produces/writes; Sonnet gives
one consultation; the Examiner supplies a focused diagnostic. Reviewer agreement
is not implementation or human acceptance. Both runs are closed; the archived
assignment/repair instructions here are historical context, not live commands.
