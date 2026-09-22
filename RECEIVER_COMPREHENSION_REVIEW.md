# Ren's receiver — bounded framing candidate

Starting state: `15934a53fad1eea23327d2bcab21e4bd62e58b97`, the owner-played
Relay consequence build. All 744 inventory entries match; the September 21
00:21 owner session identifies that build. Exact Godot 4.7.1 is unchanged.

Only the two existing project jobs' presentation changes. Stable prototype
identities are **Ivo, Works fabricator** and **Ren, Relay dispatch contact**.

| Moment | New framing |
|---|---|
| Market card | Receiver kit goes to Ivo; he makes the receiver Ren needs to open local dispatch. |
| Works stopped handoff | Ivo · Works. **Receiver kit → Finished receiver**. “I assembled your kit into Ren's finished receiver. Take it to Ren at Relay; they'll install it to open local dispatch.” |
| Works pickup | Ivo offers the **Finished receiver**; collection is still explicitly accepted. |
| Drive | Persistent strip: **Finished receiver → Ren, Relay / Opens local dispatch**. It remains beyond the old four-second flavor window. |
| Relay stopped handoff | Ren · Relay. **Finished receiver → Installed at Relay**. “Your receiver is installed. We can dispatch from Relay now. I have a Market return pouch if you'd like the next delivery.” |
| Continue | Remain at Relay; a restrained prompt offers Ren's return pouch. Opening/browsing is not acceptance and starts no clock. |

The stopped project receipts emphasize contact, cargo transformation and two
short causal lines, with one Continue button. Payment, condition and time remain
compact. Full BRRR/impact evidence remains in the frozen receipt and F3 diagnostic
logs; ordinary challenge results keep their existing full presentation.

A small original native UI schematic draws the receiver's actual paired-panel
parts and palette from the unchanged annex definition. The installed form adds
that definition's mount. This provides visual correspondence without adding a
cargo prop, changing the rig, or modifying the Relay world object.

Unchanged: job IDs, payouts, objectives, routes/endpoints, director/state machine,
acceptance/arrival/Continue behavior, save format/path, project flags, annex world
geometry, dispatch availability, vehicle, camera, cargo, trail, weather and BRRR.
The existing shared save is deliberately retained. A completed owner save stays
completed until **Reset Project Experiment** is explicitly confirmed. Repeated
deliveries say “repeat” or “spare”; they do not imply another installation.
Failed storage never claims fabrication or installation. Neutral-control copy
and its untransformed world remain available through the old launch option.

Only six pre-existing files change: `game/project.godot` (display identity),
`game/review/relay_consequence/relay_review.gd` (log identity),
`game/scripts/courier/relay_contracts.gd` (copy),
`game/scripts/courier/relay_hud.gd` (presentation), `tools/play_relay.py` (title),
and `tools/relay_web_smoke.gd` (new presentation assertions). The new schematic,
test wrappers and these review documents are additive. There is no new save field,
route, contact beyond Ivo/Ren, dialogue system, campaign or gameplay retuning.

Native screenshots were inspected at 1280×720. One compact-layout adjustment
removed an intermediate full-stat receipt layout that inflated the handoff card.
There is no forced camera reveal. The inherited east-approach visibility limit
of Relay's mast remains; this pass does not move it.

Owner gate: after one play, can Charlie explain what Works did, what he carried
to Relay and why Relay changed, in his own words? Automated correctness and
clear screenshots cannot pass that gate. If the explanation remains unclear,
the framing remains insufficient.

No main update, push or deployment. See `RECEIVER_PLAY_CARD.md`; the adjacent
review packet contains exact results and before/after captures.
