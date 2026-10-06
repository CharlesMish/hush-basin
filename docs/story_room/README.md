# Hush Basin Story Room v0.1

**Two communicating Grok Bots; one Opus writer through Cursor.** Producer
directs Opus, Examiner independently critiques, and Opus revises with room to
disagree. The default loop stops after one revision and acceptance check; at
most one further revision may address genuine blockers. Charlie directs and
accepts. Astra periodically integrates accepted work across the wider game.

This packet is production preparation, not a new chapter. Its implemented game
authority is `5be7feeef34dbed468e007f5ff4de594d41b0f80`, comprising the Opening
Chapter, accepted Tess/origin/advisory fixes, and Chapters 2 + 3. Their source
branch is `experiment/narrative-chapters-2-3-v0-1`; this tooling successor starts
there. No gameplay, dialogue, handling or world geometry changes are included.

## Use the room

Read `CONNECTION_STATUS.md` for the Bots actually created and verified, the
packet revision they received, and remaining live checks. Do not create
duplicates when the named Bots already exist. `INTEGRATION_NOTES.md` records
platform research; installed command-line tools alone are not a connected room.

1. Put both Bots in **Hush Basin Story Room** and give them the same frozen
   packet. Use `GROUP_KICKOFF_PROMPT.md` if setting up another account.
2. Give Producer a bounded assignment using `OPUS_SCENE_DRAFT_TEMPLATE.md`.
   Nothing here authorizes writing Chapter 4 automatically.
3. Inspect the final artifacts and disagreements. A model's READY verdict is
   not your acceptance and never authorizes implementation or deployment.

For a portable bundle, from repository root:

```sh
python3 tools/package_story_room.py --output /absolute/new/hush-basin-story-room.zip
```

The ZIP includes one aggregated writer packet, individual reference documents,
role prompts, the two exact dialogue catalogs and named authored plans/reviews,
and a per-file hash manifest. Other code links refer to the pinned repository;
the bundle is not a complete game checkout. Unzip into the
Grok hosted workspace; a local Mac path is not automatically accessible there.
Pin the tooling commit as well as the separate implemented-game commit. Future
updates create a new snapshot rather than changing a packet during a live run.

## Compact writer packet

Read the synopsis first; consult the tables when relevant. These are summaries
with source references, not authority to silently fix design ambiguities.

| Document | Purpose |
| --- | --- |
| [Current canon](STORY_CANON_CURRENT.md) | Identity, current chapters, established facts and explicit unknowns |
| [Characters](CHARACTER_LEDGER.md) | Voice examples, local presence, knowledge limits, relationships, current state |
| [World and routes](WORLD_AND_ROUTE_STORY_MAP.md) | Actual contacts, roads/gates, ordinary jobs and routing pitfalls |
| [World states](WORLD_STATE_LEDGER.md) | Authored physical consequences versus current visible implementation |
| [Seeds and ordinary details](SEED_PAYOFF_LEDGER.md) | Open/paid-off/provisional seeds; details allowed to stay ordinary |
| [Narrative rules](NARRATIVE_RULES.md) | Durable game constraints and directing principles |

## Roles and loop

- [Producer prompt](GROK_PRODUCER_PROMPT.md)
- [Examiner specification](GROK_STORY_EXAMINER_SPEC.md) and
  [ready-to-paste prompt](GROK_STORY_EXAMINER_PROMPT.md)
- [Opus draft](OPUS_SCENE_DRAFT_TEMPLATE.md) and
  [revision](OPUS_REVISION_TEMPLATE.md) templates
- [Finite loop and communication contract](LOOP_SPEC.md)
- [Periodic Astra integration prompt](ASTRA_CONTINUITY_INTEGRATOR_PROMPT.md)

## Play and publication

Use [publication readiness](PUBLICATION_READINESS.md) for current test results,
preview URL, one native launcher, reset instructions and the exact unexecuted
production promotion step. The story room is independent of the playable game.
No new writing assignment is needed to play the complete candidate.

## Decisions still belonging to people

The current implementation is a review candidate; automated tests don't prove
attachment, pacing or desire to drive. Some future sketches remain provisional,
and the ledgers intentionally do not fill in Stop 9's identity or other unknown
relationships. A canon table can make a character too rigid if every voice
example becomes a mandatory catchphrase. The examiner should protect surprise,
ordinary life and earned change while citing actual contradictions precisely.
Neither bots agreeing nor an exhaustive checklist establishes good writing.
