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
file access.

## Frozen packet delivered and independently verified

The complete initial packet was committed and pushed at
`05d55064a1013483b869dba0bc9d2d1906a24b6b`, then attached in the group.
Both Bots independently acknowledged the ZIP, manifest, aggregate and all
28 listed files by size/hash. Examiner additionally compared all 27 original
files against that GitHub commit and confirmed unchanged `game/` ancestry.
Shared extraction: `/workspace/hush-basin-story-room/packet-05d5506/`.

| Artifact | SHA-256 |
| --- | --- |
| `Hush-Basin-Story-Room-05d5506.zip` (112,445 bytes) | `e46d37892d0731bcc815c7251fce3fb4577d0c8733af47118d364ddb433c413d` |
| `manifest.json` | `0baa97baf2ccfbc2135f3cb168554dc1821076dc7b283fe368ae0b5ad9704c7a` |
| `writer_packet.md` | `4b3b4f6fb94001901ce7e9b72897d1c6064e6e25c54ed866b6ae0e5bd21b7bcc` |

The six canon documents and authored source are frozen in this packet. Later
connection-record updates must not silently replace it during a run.

## Actual launch boundary

Producer prepared `/workspace/hush-basin-story-room/runs/rehearsal-20261006-01/`
and a pre-launch branch/PR inventory. Its group-origin launch was refused before
agent creation: “This action needs Auto-review approval, which isn't available
in this conversation. Run it from a direct chat with the assistant.” It reported
an empty launched-agent list: **zero writer turns and zero examiner passes**.

The attempt to send that same launch instruction through the Producer's direct
chat was then rejected by Codex automatic approval review. Stated reason: a
potentially billable Cursor/Opus coding agent has repository access and possible
branch side effects; preparation authorization did not explicitly approve this
live rehearsal. Explicit owner confirmation was requested. The direct-chat
message was not sent; its composer was verified empty afterward. No safeguard
was disabled or routed around.

Thus the room is **prepared and connected**, while the live writer/revision
cycle is **not tested**. Begin actual assignments in the Producer's direct chat
so the native approval path can operate; keep peer discussion/results in the
group. The next step is approval of the bounded rehearsal, not recreating Bots
or rechecking the already-verified packet.

For an initial bounded assignment use the requested **Opus 5.5** explicitly.
Ordinary starting settings are 300k context, high effort, fast off, unless
Charlie chooses otherwise. These are configuration defaults, not new creative
constraints. Do not ask him to pick every routine parameter again.

Still untested: a full Opus draft→review→revision→acceptance run, its exact charged
allowance, and actual writer compliance with artifact-only output. The room
is idle pending the live rehearsal's explicit launch approval. It will not
invent Chapter 4 as a connection test. Existing spending limits remain in force.
