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

This preflight was observed in the account's authenticated Bot UI. The public
platform documentation is linked separately in `INTEGRATION_NOTES.md`. The
subsequent owner-approved live rehearsal is recorded below. No new story was
generated.

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

Charlie subsequently gave explicit permission for that exact bounded rehearsal.
The instruction was sent successfully in Producer's direct chat at 01:23 CT on
October 6. Producer first checked that the refused group attempt had created no
agent, then launched one agent through normal native approval. No further
approval card was needed. Begin future assignments in Producer's direct chat;
keep peer discussion/results in the group. Do not recreate the existing Bots.

For an initial bounded assignment use the requested **Opus 5.5** explicitly.
Ordinary starting settings are 300k context, high effort, fast off, unless
Charlie chooses otherwise. These are configuration defaults, not new creative
constraints. Do not ask him to pick every routine parameter again.

## Completed live rehearsal

Run `rehearsal-20261006-01` completed with **one agent, two writer turns, two
Examiner passes and one revision**. Producer and Examiner both reported idle;
the writer was finished and unwatched, with no schedule or next assignment.
The result verifies this bounded facts/transport loop, not story-writing quality
or unattended operation.

| Provenance | Observed result |
| --- | --- |
| Agent | `bc-92d0b21c-f906-5502-b841-e7cf92473bed` ([Cursor record](https://cursor.com/agents/bc-92d0b21c-f906-5502-b841-e7cf92473bed)) |
| Explicit launch selection | `claude-opus-5-5`, context `300k`, effort `high`, fast `false`; accepted without a reported substitution |
| Model verification limit | Writer self-reports Claude Opus 5.5; platform status does not echo model/settings, and the writer cannot independently observe those settings |
| Frozen source | `05d55064a1013483b869dba0bc9d2d1906a24b6b`; game still `5be7feeef34dbed468e007f5ff4de594d41b0f80` |
| Continuation | Same agent, second run `run-4fadf51c-7809-4855-be5f-517f04e8e5e5` |
| Review | READY WITH MINOR NOTES → READY; three citation/completeness notes resolved |
| Writer Git state | Transcript contains exact starting HEAD and empty porcelain status after both turns; all edits target external artifact files |
| Remote activity | Producer reports no new branch/PR or writer commit; the tooling branch's pre-launch `d005361` addendum is accounted for separately |
| Billing | Exact charged pool/plan, cost, tokens and remaining allowance remain unexposed; existing account/spending settings retained |

The first draft was 241 words; the revision was 275. Examiner caught a line
reference error and requested stronger route citations and the complete tray
sequence. Opus also corrected the review's mistaken `objective_text`/`objective`
supporting detail; Examiner explicitly withdrew that detail. An independent
local source audit confirmed the final five facts and the justified correction.
No new canon or ledger changes resulted.

| Retained file | SHA-256 |
| --- | --- |
| `draft-0.md` | `cc5c27a4a6ba6b3bb7865cdb7e1de0a9c41ef43539515921e2fa27521ba7eb44` |
| `review-0.md` | `0d686b74ee83753436a3618e9a958a8cfa3eebcb50f3cd725f3a5fba4ce2178d` |
| `revision-1.md` | `11fc3ac42a4b9ad88ae33a4603dcf2041f885e5dd615788df0e30193bbf1b72a` |
| `findings-response-1.md` | `d6cde51f998ff49f42fd923196ff42a6b35eeb3beaa23893882e4804c27443f3` |
| `acceptance-1.md` | `2acfe6ca570a4c355d50bf0e6d1cae87b14e59ee38487759505229987427389c` |

Writer artifacts originated under
`/opt/cursor/artifacts/hb-rehearsal-20261006-01/`, were transferred natively to
`/workspace/cloud-agent-artifacts/bc-92d0b21c-f906-5502-b841-e7cf92473bed/hb-rehearsal-20261006-01/`,
then copied into the shared run. Producer verified hashes before each Examiner
handoff. Both drafts, both reports, findings response, ledger and returned
transcripts were downloaded through the app as
`hb-rehearsal-20261006-01-evidence.zip` (109,835 bytes), SHA-256
`3a2eadcc040927572f9cbd5ad6e2ec0ee99808fa3b19a800cb52491814f1b5b0`.

Local evidence lives in sibling `Hush-Basin-Story-Room-20261006/`, with safe
extraction under `rehearsal-evidence/runs/rehearsal-20261006-01/`. Local checks
independently verified ZIP hash/CRC, all five ledger artifact hashes/sizes,
assignment and frozen-manifest hashes, and writer command/edit results. The
43 returned tool results show reads and three external artifact files only;
both final Git checks are clean. The Producer ledger uses approximate launch
timestamps; the app's visible timestamps place successful launch at 01:23 and
final delivery at 01:29 CT. Original evidence is preserved unchanged.

Existing spending limits remain in force. The general loop's turn caps remain
instructions and an auditable ledger, not a hard billing limiter. The next
creative assignment needs Charlie's bounded brief; no Chapter 4 is inferred.
