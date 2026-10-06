# Two Grok Bots, one Opus writer

Use Grok Bot's native peer messages, group chat, shared hosted filesystem and
Cursor delegation. No new service, API key, daemon, subscription or messaging
framework is required by this specification. The transport's account controls
still apply. `INTEGRATION_NOTES.md` distinguishes verified capabilities from
account-specific unknowns; `CONNECTION_STATUS.md` records the actual setup.

```text
Charlie: bounded assignment
  └─ Grok Story Producer ── Cursor: explicit Opus ── draft
           ↕ shared group / direct messages            │
     Grok Story Examiner ◀──── exact draft artifact ───┘
           │ findings + strongest material
           └─ Producer ── same Opus agent ── revision
                               │
                  Examiner acceptance pass
                               │
                  human review / stop
```

The two Grok roles can speak directly. They share one outcome and immutable
artifacts, with one owner per stage. Opus remains the writer. A third Grok
feasibility reader is optional for a concrete question; it shares the packet
and group but has no extra writer/revision budget or casting vote. Start with
two. Astra's periodic integration role remains outside the automatic loop.

## Before the first assignment

1. Freeze one packet/repository revision and one bounded assignment. Both Bots
   acknowledge the same hash, game commit and scope. A Bot's remembered lore is
   not authority. An intentionally new canon decision must be explicit.
2. Verify native Cursor delegation can select the requested Opus model and start
   at an exact repository commit. Use the live discovered model ID, never Auto
   or a potentially ambiguous alias. Record exact model settings and agent ID.
3. Use the existing signed-in Cursor route. Do not substitute a direct provider
   API if unavailable. Billing attribution/allowance must be described truthfully;
   a model list establishes availability, not its remaining allowance.
4. Set the agent's output folder to a new review directory. Repeat no game/canon
   edits, commits, push, PR or deployment in each delegated assignment. Native
   Cloud Agent checkout/branch provisioning is infrastructure, not permission
   to create source commits. There is no verified hard no-push tool switch;
   inspect its returned diff/activity and reject unauthorized mutations.

Suggested hosted run: `/workspace/hush-basin-story-room/runs/<unique-run-id>/`.
Do not reuse the Mac checkout path on the hosted computer. The shared file
protocol is simply files plus native messages, not a filesystem security sandbox.

The delegated Cursor agent has another filesystem. Give it an output directory
outside its repository checkout, and require its final response to reference
the exact files for native artifact transfer. Producer copies those returned
artifacts into the Grok shared run, records both paths and verifies their hashes.
Examiner reads the **copied** artifact; a shared-looking absolute path on the
writer's computer is not evidence it exists on the Grok computer.

## Artifacts and message contract

Producer owns `run.json`: run ID, exact assignment path/hash, packet manifest
hash, implemented game commit, stage, actual delegated model/settings/agent ID,
writer delegation/resume count, examiner pass count, revision count, and final
disposition. Create it before drafting; write updates atomically. The examiner
owns each report. Neither overwrites earlier artifacts.

Keep `assignment.md`, the packet snapshot, `draft-0.md`, `review-0.md`,
`revision-1.md`, `acceptance-1.md`, and if justified `revision-2.md` /
`acceptance-2.md`. Keep Opus's findings response and full returned transcript.
Record usage/token totals only if reported by the provider; do not estimate them
as observations. Ledger deltas stay proposed files outside the canon packet.

Each handoff names: run ID, unique message ID, stage, sender/recipient, packet
hash, artifact path/hash, concrete request and next owner. Acknowledge the
artifact hash once. A duplicate message must not launch another writer. A stale
hash/stage is rejected with a factual reply. Missing files or hash mismatches
pause that run until resolved; do not evaluate a nearby similarly named draft.
Everyone can read the shared conversation. Factual clarification messages are
welcome; avoid a self-sustaining acknowledgement loop.

## Finite control flow

```python
# Protocol pseudocode executed by the Producer, not a background daemon.
assert bounded_assignment and matching_packet_acknowledgements
draft = opus.draft(assignment, packet)       # one delegated agent
critique = examiner.review(draft, packet)   # separate Bot
revision = opus.followup(draft, critique)   # same agent/model; revision 1
acceptance = examiner.check(revision, critique, packet)
if acceptance.has_evidenced_remaining_blockers:
    revision = opus.followup(revision, acceptance)  # revision 2, final
    acceptance = examiner.check(revision, acceptance, packet)
stop_and_handoff_to_charlie(revision, acceptance, disagreements, provenance)
```

One draft, one normal revision, at most one extra revision. Maximum three writer
turns and three examiner passes. A resolved first report may make revision 1 a
reasoned no-change response; do not invent edits. A second revision is allowed
only for evidenced unresolved blockers, never a taste note or numerical score.
Fundamental ambiguity or a required scope expansion stops early for direction.

READY/READY WITH MINOR NOTES/REVISION ADVISED are human-review dispositions;
none automatically changes canon. Remaining blockers after revision 2 become
`NEEDS_HUMAN_DIRECTION`. All terminal states are idle. No timed routines or
automatic next assignments. User interruption wins. An interrupted/uncertain
writer launch is inspected before retrying; do not duplicate an expensive task.

These limits are role instructions and a reviewable run ledger, **not an
enforced billing limiter**. No custom execution wrapper is needed to experiment.
If Bots demonstrably ignore the limits, stop and add narrowly justified runtime
enforcement before leaving them unattended.

## Pilot and periodic review

The setup handshake is not a prose-quality test. A first writing assignment
should be a specifically bounded, noncanonical exercise chosen by Charlie;
do not invent Chapter 4 to test the connection. Check that the model really is
Opus, the examiner protects strong work, disagreements remain visible, the
revision returns to the same packet, and the room stops at its cap.

After a substantial accepted arc or several accepted scenes, use
`ASTRA_CONTINUITY_INTEGRATOR_PROMPT.md`. Human acceptance records travel with
that batch. Only a subsequent authorized implementation task changes the game.
