# Consultation-led Grok writing, v0.2

Owner direction, October 6, 2026: Claude usage is comparatively scarce. Astra
directs the work and makes editorial calls; Grok does drafting and repairs.
This supersedes the previous Opus/Sonnet-writer loop. Its run records remain
historical evidence; the implemented game and six canon ledgers are unchanged.

```text
Charlie / Astra: bounded brief and editorial decisions
  → Grok Producer → Sonnet 5.5: one short consultation
                  → Grok Writer: full draft or revision
                  → Grok Examiner: focused diagnostic evidence
  → WAITING_FOR_ASTRA: actual script, consultation, findings, provenance
  → Astra: accept for owner review, direct a specific Grok repair, or stop
```

## Roles and economy

- Producer commissions, verifies artifacts and keeps the run record. It does
  not write a substitute script or certify its own work.
- Sonnet consults. Default: one turn, at most 600 words, `claude-sonnet-5-5`,
  300k context, high effort through the existing Cursor account. Continue a
  relevant session when practical. No automatic second call or Opus escalation.
- A distinct native Grok Writer owns prose and repair responses. Report actual
  route/identity; a Cursor-hosted Grok model is not assumed to draw the same
  allowance as Grok Bot. Verify the route before substituting it.
- Examiner supplies focused independent evidence; it cannot order another
  writer turn or turn READY into Astra acceptance.
- Astra reads the actual artifact and makes the delegated editorial decision.
  Charlie retains project direction and playtest judgment. Editorial acceptance
  does not authorize implementation, canon promotion or deployment.

Normal proposal details within the brief belong to the writer/director. Small
new institutional facts need not become separate owner questions. Distinguish
proposals from established history. Unknown does not mean false; unwitnessed
events are not inherently dishonest. Escalate actual scope changes or consequential
unresolved choices, not every noun or line.

## Bounded sequence

1. Freeze assignment, canon manifest, implemented commit and input hashes.
   Reuse existing Bots; do not recreate the room for each run.
2. Start Cursor consultation from Producer's direct chat, preserving native
   approval. Groups cannot supply that approval. Existing account/spending
   settings only: no new keys, providers, installations or limit changes.
3. Preserve Sonnet's advice. Give it, the brief and packet to Grok Writer.
   Advice does not require mechanical compliance; reasoned disagreement is valid.
4. Grok returns playable writing first, a concise state/cost appendix, and keyed
   findings responses. Source/game/canon/saves/Git stay read-only. Preserve input
   and every revision as separate artifacts.
5. Default to one focused Examiner pass on the director's questions and concrete
   source/flow issues. Protect good writing; no numerical scores or compulsory
   criticism per category.
6. Package the actual files and enter `WAITING_FOR_ASTRA`. No automatic revision,
   acceptance, next chapter or scheduled continuation.
7. Astra may direct at most two further Grok repair turns in this bounded run.
   Fix identified issues; accept good work without inventing an edit. At the cap,
   keep disagreements visible and stop.

Default cap: **one Sonnet consultation turn; one Grok draft/revision plus at most
two Astra-directed Grok repair turns**. Further Examiner checks need a specific
direction. These are role instructions and an auditable ledger, not a hard
billing limiter. Report usage/cost/pool data only when actually exposed.

## Communication and artifacts

Use the existing Story Room, native direct peer messages and hosted files. A
native Writer Bot may share Producer's filesystem; a Cursor consultant has a
different machine. Require final file references for native Cursor transfer,
copy into the shared run and verify hashes. A path on one machine does not prove
a file exists on another.

Producer owns `run.json`: run/assignment/packet IDs and hashes, exact source/game
refs, actual writer/consultant routes and identities/settings, stage, counts,
artifact paths/hashes and disposition. Handoffs name the run, exact artifact/hash,
request and next owner. A duplicate must not start another agent. Inspect
ambiguous launches before retrying.

Retain assignment, consultation, draft, focused report, Astra review/decision,
each revision and response. Final bundle contains a clean script, full proposal,
disagreements, proposed additions and provenance. Inspect Git activity from
repository-capable agents.

There is no verified automatic Grok→Codex wake-up bridge. During an actively
supervised run Astra reads the files and replies. Otherwise the room waits for
Charlie/Astra to bring or inspect the bundle. Never impersonate Astra or claim
an unread artifact was reviewed. No monitor is created implicitly.

## Review standard

Check the player's actual sequence: cargo at every stage, declining, repeated
panels, forced empty travel, what the normal camera shows, knowledge channels,
and concrete resume states. Verify the practical mechanism without adding a
lecture. Human feel, attachment and pacing remain playtest questions.

The six ledgers remain the baseline. Accepted writing is distinct from implemented
game state. Periodic wider review still uses
`ASTRA_CONTINUITY_INTEGRATOR_PROMPT.md` alongside this per-run oversight.
