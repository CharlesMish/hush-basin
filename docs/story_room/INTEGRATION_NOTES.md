# Grok Bot / Cursor integration notes

Verified October 6, 2026. This is a preparation record, not evidence that a live
writing loop has run. During the command-line/document inspection, no Bot,
Cloud Agent, paid model request, worker, routine, new dependency, or external
configuration was created. Subsequent native Bot setup is recorded separately;
no Opus writer was called during this research phase.

## Recommended connection

Use two named Grok Bots in one **Hush Basin Story Room** group:

1. **Story Producer** owns the assignment and delegates prose to an explicitly
   selected Opus agent through Charlie's Cursor account. It preserves the Opus
   output and sends the exact draft to the Examiner.
2. **Story Examiner** reviews that draft independently and returns findings to
   the Producer. It does not replace the writer or turn taste into a blocker.

Use native Bot messages for handoffs and shared files for the exact draft,
review and revision. This is supported by the product: Bots can retain separate
roles, send asynchronous messages that wake each other, and participate in a
group of two to six Bots. A group handoff is currently text-only, so hand off a
shared file path and digest; send images directly when inspection is necessary.
There is no need to build a new message server for this experiment.
[Bot roles](https://docs.x.ai/grok-bot/bots),
[Messaging and groups](https://docs.x.ai/grok-bot/chat-and-collaboration).

The Grok Bot computer is shared by this account's Bots, including its
`/workspace` files and sign-ins. Keep each run in a distinct project directory;
only the Producer advances its stage record. Separate Bot identities are
editorial roles, not filesystem isolation. The local Mac checkout and the Bot
cloud computer are different machines.
[Computer and apps](https://docs.x.ai/grok-bot/computer-and-apps).

A third Grok Bot is optional: add a continuity librarian only if two-role
handoffs actually become cumbersome. It should not become another prose critic
or another mandatory revision pass. Astra's periodic integration review remains
separate from the per-assignment loop.

## Opus through Cursor: supported path and remaining check

Grok Bot supports delegation to Cursor Cloud Agents. That is the first route to
try from the Producer, using the existing Cursor account and native delegation
tools. Team controls can disable that capability. The delegation target must
report the selected model; a Grok Bot itself has no model picker and cannot be
made Opus by putting an Opus name in its description.
[Delegation controls](https://docs.x.ai/grok-bot/teams-and-enterprises),
[Bot model setting](https://docs.x.ai/grok-bot/settings-and-notifications).

**At the research stage these were unverified:** available Opus version/model ID,
native delegation's model-selection controls, authentication validity, repository
access from that computer, and the exact usage allowance charged. Subsequent
live results are recorded in `CONNECTION_STATUS.md`; it supersedes this initial
unknown list. Do not invent
an `opus-5.5` ID, use Auto, fall back to another writer, or substitute a direct
Anthropic API key without Charlie choosing that change.

Cursor's Cloud Agent API supports an explicit `model.id`, with currently valid
values discoverable through `GET /v1/models`. It also supports a repository
`startingRef`. That is evidence of a supported Cursor path, not a requirement
to install an SDK or add a bespoke API adapter. The Bot's actual native tools
should be inspected first. If those tools cannot set/confirm the requested
model, report the narrow mismatch before launching writing work.
[Cloud Agent API](https://cursor.com/docs/cloud-agent/api/endpoints).

Cursor documents Cloud Agents as charging for the selected model at API rates;
Grok Bot has its own weekly allowance and possible on-demand usage on the Cursor
account. These statements do not prove that delegated Opus consumes the precise
pool Charlie means. Check the account's usage presentation for the selected
route. Preserve existing spending settings; preparation does not authorize
enabling on-demand, raising limits, or buying usage.
[Cloud Agent billing](https://cursor.com/docs/cloud-agent),
[Grok Bot usage](https://cursor.com/help/grok-bot/plans).

Cloud Agents normally work on repository branches and may push for handoff.
For this writing experiment require artifact-only output, no PR/commit/push,
and no game edits; explicitly disable automatic PR creation if the transport
exposes it. Supply the pinned review ref, never an implicit `main` default.
Review outputs do not become canon because an automated examiner accepts them.

## Local inspection: what is actually installed

| Observation | Result |
| --- | --- |
| Desktop apps | `Grok Bot.app` and `Cursor.app` are installed in `/Applications` |
| Grok Build binary | `~/.grok/bin/grok` resolves to `grok-1.0.30-macos-aarch64` |
| Version | `grok 1.0.30 (04b7ffed98c6) [stable]` |
| Generic `agent` command | `~/.local/bin/agent` links to **Grok Build**, not Cursor CLI |
| Cursor CLI | `cursor-agent` was not found on PATH or the standard checked paths; the app's editor launcher exists |
| Worker support | Installed `grok cursor-worker` supports `start`, `stop`, `status` |
| Worker status | Read-only status returned no running leader for this environment |
| Worker configuration | No `cursor_worker` section or worker directories configured in the inspected Grok config |
| Local peer messaging flag | `features.active_agent_messages` is unset |
| Authentication | A Grok auth file exists; its contents and validity were not inspected |

Do not invoke bare `agent --model ...` on this Mac expecting Cursor: it currently
starts a different product. No symlinks, credentials or user settings were
changed. The desktop app's own current Bot roster/session has not been inspected
as part of these command-line checks.

### Why `cursor-worker` is not the primary setup step

Installed help and bundled documentation say that `grok cursor-worker start`
registers a local leader as a private worker so Cursor Cloud Agents can execute
against this machine. It accepts repository directories and a concurrency cap.
It does not itself select Opus, create the durable Bot team, or establish which
billing pool is used. No local worker is necessary for a story-only cloud room
unless Charlie specifically wants execution against this Mac's files.

Read-only command used:

```sh
~/.grok/bin/grok cursor-worker status --json
```

Observed result: `no running leader for this environment`. We did not run the
suggested start command. Local source of this interpretation:
`~/.grok/docs/user-guide/26-config-reference.md`, section `cursor_worker`, plus
the installed `cursor-worker start --help` output.

### Grok Build is a possible fallback, not an equivalent Bot team

Installed Grok Build supports headless prompts, named agent profiles, resumable
subagents, and ACP. Its bundled `16-subagents.md` documents
`send_subagent_message`, disabled by default and gated by
`features.active_agent_messages`. It has hierarchy restrictions, including a
child directly under the root being unable to message that root. Therefore do
not describe the unconfigured CLI as already providing the user's persistent,
mutually communicating Bot room.

Cursor separately documents a subscription-backed CLI with explicit model
selection and model discovery. A genuine Cursor CLI could be used if native
delegation cannot meet the requirement, but it is not verified installed here
and should not be confused with Grok's executable alias. Do not install it or
overwrite `agent` merely for preparation.
[Cursor CLI](https://cursor.com/docs/cli/overview),
[Cursor CLI parameters](https://cursor.com/docs/cli/reference/parameters),
[Cursor CLI announcement](https://cursor.com/blog/cli).

## Readiness checklist for the first real assignment

This is the execution checklist, not a request to redo completed setup. Consult
`CONNECTION_STATUS.md` first and skip checks already verified there:

1. In the actual Grok Bot account, identify/create the Producer and Examiner,
   record their IDs, and put them in one group. Confirm a handoff can wake the
   other Bot and both can read the same run artifact.
2. Inspect available Cursor delegation and model-selection tools. Record the
   exact Opus ID and the authenticated Cursor route. If unavailable, stop at
   that integration boundary rather than silently substituting a model.
3. Verify the repository packet at its pinned revision and the account's usage
   route. Use only the existing authorized allowance and spending settings.
4. Record one bounded assignment, expected outputs and stop conditions before
   spending writer calls. The first trial should be explicitly noncanonical;
   this preparation task does not authorize Chapter 4.
5. Draft → independent critique → one Opus revision → acceptance check. Permit
   one additional revision only for unresolved factual/design blockers, then
   stop with the evidence. Do not schedule a recurring loop yet.
6. Keep the original draft, each review, model/session IDs, and the final
   candidate. Inspect the completed run before calling the integration proven.

The protocol and prompts can be ready before these live account checks pass.
The report must distinguish **prepared**, **connected**, and **tested**.
