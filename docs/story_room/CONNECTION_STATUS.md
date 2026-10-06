# Native story-room connection — October 6, 2026

Setup has moved beyond prompt files. The signed-in Grok Bot desktop app now has
two newly created Bots, **Hush Basin Story Producer** and **Hush Basin Story
Examiner**, in a group named **Hush Basin Story Room**. Existing unrelated Bots
were left alone. No scheduled routines, worker, new credentials or spending
settings were created/changed.

The Producer was given an explicit read-only delegation preflight. Its visible
report says it performed a live model-list query, repository search and lookup
of the pinned game commit. Observed report:

| Capability | Result |
| --- | --- |
| Requested writer | `Claude Opus 5.5`, exact discovered ID `claude-opus-5-5` |
| Selection | Explicit model ID/settings supported; omitted selection falls back to Auto, so do not omit |
| Relevant settings | Context 300k or 1m; effort low through max; fast on/off |
| Repository | Connected access to `CharlesMish/hush-basin`; exact `5be7fee…` commit found |
| Starting ref | Repository URL plus branch or exact commit supported |
| Continuation | Follow-up to the same agent ID, retaining its model unless overridden |
| Return | Full transcript and final-referenced files copied to the Bot computer; artifact-folder listing supported |
| Account route | Native signed-in Cursor delegation; no separate provider API key needed |
| Billing | Tool does not expose exact pool attribution, remaining allowance or per-run cost; not verified |
| Git boundary | No verified hard no-push switch; artifact-only instructions and result inspection remain necessary |

This is a report observed in the account's authenticated Bot UI, not an Opus
execution test. The public platform documentation is linked separately in
`INTEGRATION_NOTES.md`. No writer model has been launched during setup, and no
new story has been generated.

Both Bots posted `HB_ROOM_GROUP_READY` in the shared group, with the correct
distinct roles. A separate shared-file/direct-message roundtrip then succeeded:
Producer created `/workspace/hush-basin-story-room/setup/peer-check-20261006.json`,
sent its path/hash directly, Examiner read and independently hashed it, and
Producer acknowledged the direct reply in the group. Both reported SHA-256
`55e57a5a8512aef3fda2c2f6f4e9129644719e0552c8e6e00707d0e2c28016a5`.
The file's marker and exact game commit matched. They then went idle, as asked.
This verifies group participation, direct bidirectional messaging and shared
file access. It does not yet verify the full canon packet or writer transfer.

For an initial bounded assignment use the requested **Opus 5.5** explicitly.
Ordinary starting settings are 300k context, high effort, fast off, unless
Charlie chooses otherwise. These are configuration defaults, not new creative
constraints. Do not ask him to pick every routine parameter again.

Still untested: a full Opus draft→review→revision→acceptance run, its exact charged
allowance, and actual writer compliance with artifact-only output. The room
waits for Charlie's bounded noncanonical pilot assignment; it will not invent
Chapter 4 as a connection test. Existing spending limits remain in force.
