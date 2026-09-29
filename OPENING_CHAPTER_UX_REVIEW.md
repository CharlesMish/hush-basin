# Opening Chapter — small UX correction, September 29, 2026

Starting branch: `feature/opening-chapter-v0.1`, clean.
Exact starting HEAD: `fd6a7563918f257590906f0b7dae0229273b20a3`.
Correction branch: `fix/opening-chapter-ux-v0.1`.
Final commit/package identity is in the adjacent review folder's `package.json`.

This implements only the owner's Tess-stop, pickup-label and advisory corrections.
No new story, dialogue, portraits, missions, progression or world-detail pass.
The existing chapter save remains compatible; no reset is required.

## Tess contact

| | Before | After |
| --- | --- | --- |
| Stop center (world x,z metres) | (40,77) | (40,67) |
| Usable contact radius | 4 m | 9 m |
| Counter position | (40,83) | Unchanged |
| Roadside test position (40,60) | No interaction; HUD asks for another 17 m | Interaction available |
| World cue | No Tess ground marker | Existing Basin ring style at the stop center |
| Minimap cue | Old stop near frontage | Same center as practical ground stop |

The contact moves ten metres toward the road. Its wall-side edge is now z=76,
ten metres clear of the raised frontage beginning near z=86. The counter,
canopy, furniture, building, foundation and collision remain in place. The new
ring is non-colliding and reuses the existing marker mesh; no camera change.

A fresh 25-point native physics-ray survey found only ground throughout the
proposed approach box. Ordinary-input drives from Market, Clinic and Depot
(west approach via Market) stop and open Tess's actual introduction without
resets or impact events. These validate reachability; Charlie still judges feel.
The enlarged disk clears HOP's operational corridor by **52 m**, DOG's by
**51.184 m**. World geometry and authored route files are byte-identical.

## Pickup and destination audit

Previously the chapter inherited a Market origin coordinate and supplied no
explicit origin in its contract data. Cards mainly named cargo ownership or its
recipient: “Clinic's aprons” did not establish that pickup was at Depot. The
receiver's driving strip also repeated the previous kit transformation heading.

Each contract now carries its actual pickup ID. Acceptance sets the origin from
that pickup; a saved parcel reconstructs it from the same chapter leg. Cards,
offer summaries and the driving purpose strip explicitly show **Pickup: origin
→ destination**. The handoff transformation remains at Works, while the driving
strip shows only the finished receiver and its existing purpose text.

The active minimap marker says **To destination**. Outside a delivery it marks
the local/pickup stop. A Quarry ticket viewed at Relay explicitly names pickup
at **South counter → Quarry Stores**; Relay posting it does not make Relay the
cargo origin. Neither reading it nor Skip accepts work.

## Route audit and decisions

There is no shortest-path selector here. Contracts contain fixed lists of roads
to highlight, and delivery checks only the destination's existing arrival gate.
Two longer advisories are explicit chapter design choices: the receiver returns
via East Gate/East Sweep to vary the round trip, and aprons use the South Cut.
They remain suggestions. No fictional road condition or customer excuse was added.

| Cargo | Actual pickup → destination | Guidance after correction |
| --- | --- | --- |
| Relay mail | Market → Relay | Spine, −L5 / −L4; unchanged |
| Receiver kit | Relay → Works | L4 / R0; unchanged |
| Finished receiver | Works → Relay | L7 / −A2; deliberate alternate return, retained |
| Dry socks | Relay → Quarry Stores | −A1 / −A0; unchanged |
| Mended jackets | South counter → Depot | L1 toward Depot; removed unrelated full L2 segment |
| Clinic's aprons | Depot → Clinic | S0 / DOG / S1; intentional South Cut advisory retained; HOP and inner streets legal |
| Clinic repairs | Clinic → South counter | Destination marker only for the nearby direct approach; removed full Clinic–Market L2 detour |
| Patch kit | South counter → Quarry Stores | L1 / L0 / A0 toward the west; removed unrelated full L2 segment |

The full L2 highlight ran to/from Clinic for Tess's off-road counter, suggesting
the wrong departure or an unnecessary trip through Market. The remaining road
highlights identify road sections, not a turn-by-turn path from the exact craft
position. No navigation/pathfinding system was added.

The audit also reproduced a real stale-state defect: the retained diagnostic
route menu could overwrite the delivery highlight; cancellation/Results could
retain a previous line. Chapter presentation now derives the highlighted roads
from the active contract and clears them during handoffs, decline, free roam and
Results. The map legend says **Suggested · any legal route**, or **Destination ·
any legal route** when no road is suggested. Existing optional challenge offers
retain their own “Optional challenge route” label and rules.

Without a specific owner leg/capture, we cannot identify which of these caused
the reported unexpected route. Both intentional detours and incorrect guidance
were found; they were not given a blanket explanation.

## Files and checks

Six runtime files changed: `chapter_director.gd` (stop, origin, map state),
`chapter_anchors.gd` (fixed counter/ground cue), `chapter_text.gd` (origin and
advisory metadata/current cargo purpose), `chapter_panel.gd` (offer pickup),
`chapter_hud.gd` (card/driving pickup), and `p1a_map.gd` (configurable legend,
historical default unchanged). New `chapter_ux_probe.gd` / `chapter_ux_native.gd`
cover these behaviors; `verify_chapter_ux_preservation.py` checks the bounded diff.
Documentation changes are this review and the current STATUS entry.

All spoken text, offer choices, handoff summaries, mission order, portraits,
controller/tuning, camera, world/route data, cargo/scoring, persistent record
format and consequences remain exact. Acceptance/input code is untouched apart
from recording the actual origin at acceptance. Skip/Accept/review and resume
retain their existing behavior.

The previous chapter's 85-check handoff suite passed before editing. The new
71-check UX audit failed on the old candidate as expected, reproducing the stop,
missing pickup labels and stale guidance. Focused native/headless checks then
passed; native captures prompted one final UI-only cleanup of the stale kit
heading, covered by a new assertion. Final counts and commands are in STATUS
and `../Hush-Basin-Opening-Chapter-UX-v0.1-Review/evidence/`.

Use the corrected review folder's `PLAY_OPENING_CHAPTER.command`. Existing saves
resume normally; Dispatch → Reset Opening Chapter remains available if a fresh
run is wanted. No deployment, push, main update or further narrative expansion.
Stop for owner review.
