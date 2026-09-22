# Hush Basin — current experimental review candidate

This branch is **Ren's Receiver comprehension v0.1**, from exact local playable
candidate `6570619b7bff67140bec03039942585208b5a8be`. It includes the newer city,
Quarto vehicle, five-job mechanics range, three-visible-card Dispatch, cargo v1.1,
session rewards, Relay consequence experiment and default drift/trail polish.
It supersedes `main` and `review/courier-alpha-v0.2` as **design-review context**;
neither those branches nor production hosting was updated. This is an experiment,
not a finished release. Charlie enjoyed the prior connected Relay deliveries;
this latest comprehension pass is still awaiting his playtest.

## Launch and controls

Use installed Godot **4.7.1.stable.official.a13da4feb** and Python 3.10+.
From the repository root run `python3 tools/play_relay.py`, or double-click
`PLAY_RELAY.command` on macOS. Set `GODOT_BIN` if the engine is elsewhere.
The launcher prepares imports; it does not install software. The project is
`game/project.godot`. Native Forward+ remains authoritative; the retained Web
export/hosting tools are a separate regression lane, not a deployment request.

- W/S: thrust/brake. A/D: steer.
- Hold Shift: **Drive**, faster and more committed, with weaker steering/braking.
  Release: **Spread**, more maneuverable with greater clearance.
- Space: supported **Hop** in Spread; it trades forward speed for lift.
- E/Enter: nearby Dispatch; left/right: browse; Enter: accept/continue.
- Escape: pause/close; R: reset or retry. F2: cargo receipts; F3: diagnostic bookmark.

BRRR is the existing broad expressive-driving metric. The trail gives restrained
traversal feedback and stronger feedback for meaningful slip. A qualifying drift
chain is stricter than BRRR: straight fast Drive is not itself a shaped drift.
Scoring, movement and challenge rules are unchanged by this publication.

## Current loop

Market is the principal home/browse hub. Three cards are visible at once; the
whole available pool is deliberately browsable. The five ordinary jobs reach
Depot, Relay, Works, Clinic and Quarry. Depot is now basic delivery, **without a
mastery objective**. The other bonuses ask for West Sweep execution, cargo care,
South Cut technical traversal, or East Sweep then Quarry Shelf respectively.
Any legal route can deliver; missing a bonus or reaching zero cargo condition
never invalidates delivery. Continue leaves the craft at the reached destination.

Credits pay fixed base plus the stated optional bonus, without hidden BRRR
multipliers. Credits, the one cargo-protection liner and challenge mastery seals
are session-only. The liner reduces cargo loss only; it does not change handling.
The polished default trail is available immediately, not withheld as an unlock.

## Relay: one finite remembered consequence

Market's **Receiver kit** goes to **Ivo at Works**, who fabricates the **Finished
receiver**. A separate acceptance collects it for **Ren at Relay**. Installation
visibly activates Relay's annex and makes its outbound **Market return pouch**
available. That offer does not autoaccept or start a timer. Project jobs contribute
on valid delivery regardless of cargo/bonus/mastery; unrelated freight cannot
substitute. Replays do not pretend to build the annex again.

Only the two named project-completion flags persist locally; the world state and
Relay Dispatch availability derive from them. Market Dispatch's confirmed
**Reset Project Experiment** replays the chain. This shares the existing Relay
experiment save with older local candidates. Optional research control:
`python3 tools/play_relay.py --control` retains legs/pay/outbound convenience but
removes named framing and annex transformation; it shares the same save.

## What to review

The design question is broader than whether Ivo/Ren's latest copy is clear:
**does expressive courier work, learned routes and a place remembering a delivery
create a motivating repeatable game around this vehicle?** Consider job variety,
challenge versus traversal, board flow, return journeys, rewards and whether
Relay's consequence matters beyond another convenient pickup. Do not assume a
successful implementation proves motivation. Specifically, the owner should be
able to explain what Works did, what reached Relay and why Relay changed.

Start with [Relay integration](RELAY_CONSEQUENCE_REVIEW.md),
[current comprehension changes](RECEIVER_COMPREHENSION_REVIEW.md),
[recorded verification](RECEIVER_VERIFICATION.md), and the live
[catalog](game/scripts/courier/relay_contracts.gd) /
[director](game/scripts/courier/relay_director.gd).
Historical authorities and P1B studies are evidence, not blanket implementation
permission. No development, rebalance or deployment was part of this publication.

Publication provenance and exact documentation-only differences are in
[`docs/REVIEW_PUBLICATION.json`](docs/REVIEW_PUBLICATION.json). Local paths were
redacted; original historical hash manifests/results were retained, not rewritten
to suggest that old baseline-only verifiers apply to this successor. Raw captures,
logs, exports, saves and archives remain local. Source-required authored/baked
world data, textures and import *settings* remain; generated import caches do not.
