# Hush Basin Story Examiner

The examiner is a separate Grok role with the same authoritative packet as the
producer. The producer commissions a native Grok writer after a bounded Sonnet
consultation; the examiner assesses that writing for this particular driving
game. Astra makes the editorial call. The examiner does not replace the writer or
implement its recommendations. See the ready-to-paste
`GROK_STORY_EXAMINER_PROMPT.md`.

## Review contract

Focus on the assignment's actual risks and Astra's outstanding notes. These
dimensions guide coverage; brief `clear` entries are enough where no material
issue exists. Do not invent one criticism per category or an exhaustive report
when a short focused check answers the question.

| Dimension | Evidence to examine |
| --- | --- |
| Character fidelity | Distinct voices, plausible change, personality replacement, repeated introductory gimmicks, room for unrelated concerns |
| Relationships | Who knows whom and what; earlier versus newly created links; actual information channels; no telepathy |
| Geography and objects | Real pickup/destination, gates and roads, contact positions, cargo identity/scale, plausible local physical changes |
| Courier-leg necessity | Whether each leg changes the drive, understanding, physical situation or available work; explain weak bridge legs without mechanically deleting them |
| Story and driving | Geographic purpose, legal alternate routes, interruption cost, mastery/time demands, unearned emergency framing |
| Persistent consequences | What remains, where it can be seen, whether a prop/receipt suffices, implementation cost and promises |
| Narrative economy | Exposition, redundant information, universal wit/coziness/gratitude, motif overbuilding; preserve richness that earns its place |
| Social web | Revealed old links and courier-created new ones versus unexplained universal acquaintance; earned later density is welcome |
| Continuity and causality | Prerequisites, interleavings, cargo, chronology, knowledge, postponement, acceptance and restart |
| Feasibility | Existing primitives versus bounded additions versus new systems; do not equate nonzero cost with failure |

## Report

Use `READY`, `READY WITH MINOR NOTES`, `REVISION ADVISED`, or
`BLOCKED BY CONTINUITY/DESIGN`. READY means suitable for human review, not canon.
List:

1. Blocking findings: stable ID; exact beat/line; authority/source; contradiction;
   consequence; smallest repair direction; confidence. Missing information is a
   question, not an invented fact. Mark genuinely undecidable decisions as such.
2. Nonblocking findings grouped by character, continuity, geography, leg
   structure, persistent world, pacing and implementation. Taste stays here.
3. Strongest material: precise passages or structural choices to protect.
4. Proposed continuity-ledger changes, conditional on human acceptance.
5. Only questions that could materially change the revision.
6. Brief coverage of the ten dimensions above and any unverified assumptions.

When Astra explicitly requests a recheck, review the **revision**, its exact hash and the previous findings.
Mark each finding resolved, remaining or withdrawn. Do not keep a false positive
alive to defend your first review. New blockers require evidence; do not restart
the whole aesthetic review. No finding triggers an automatic revision. Stop at
WAITING_FOR_ASTRA after the requested diagnostic; only her concrete direction
authorizes another Grok writer turn.

Optional machine envelope: `verdict`, `artifact_sha256`, `packet_sha256`,
`blocking_findings` (array), `report` (Markdown). A blocker includes `id`, `beat`,
`source`, `problem`, `impact`, `repair`, `confidence`. Store the whole report;
do not reduce it to a numerical quality score. Transport details are in
`LOOP_SPEC.md`.
