# Relay — Dispatch Annex · owner review

Double-click `PLAY_RELAY.command`. Exact installed Godot 4.7.1 is used.
W/S thrust/brake, A/D steer, hold Shift for Drive, Space for supported Hop,
E/Enter opens/accepts Dispatch, left/right browses, Esc pauses, R recovers.
F3 bookmarks a surprising contact; F2 shows the retained cargo evidence.

1. At Market, read **Receiver mounting stock**. Deliver it to Works.
2. Close and reopen the game. The fitted Relay bracket and Works pickup should
   remain. The craft starts at Market; use normal driving to return to Works.
3. At Works, accept **Assembled receiver** and deliver it to Relay.
4. Continue where you arrived. Open Relay Dispatch and take the **Market return
   pouch**. Return by any legal route. Close/reopen again if useful.

Only the two needs are saved. Credits, cargo liner and the four remaining
challenge seals reset on exit. Zero-condition cargo still delivers. Completed
needs can be replayed for the displayed ordinary Credit payment, without further
contribution. Freight seals is a basic Depot delivery with no mastery slot.
The polished default trail is immediately available and has no purchase gate.

**Replay from fresh:** any open Dispatch → **Reset Project Experiment…** →
confirm. It clears both needs, the Relay equipment states and Relay Dispatch;
it leaves the current session's Credits/liner/mastery intact. No save-file hunt.

Tell Astra what you noticed without consulting this card: what Relay needed,
what physically changed, whether reopening made it feel remembered, and whether
departing from Relay made another delivery appealing. Did the project feel like
specific work, a chore/indicator, or simply a convenient second board? Was the
brief Relay voice more interesting than the physical consequence? Does the
default trail feel finished and communicate genuine drift?

Known visibility limit: an east-sweep arrival faces away from Relay's existing
mast. There is no forced camera reveal. Failure to notice the change is useful
evidence against this presentation, not something to dismiss.

Optional research control (not required): `python3 tools/play_relay.py --control`.
Reset in Dispatch before a fresh tester starts. This uses the same legs, payments,
completion flags and eventual outbound board, but neutral shipment copy and no
Relay transformation. Use separate fresh testers if possible; switching variants
shares the same experiment save. Browser storage is local to its origin/profile;
clearing it removes the experiment. Nothing is deployed to production.
