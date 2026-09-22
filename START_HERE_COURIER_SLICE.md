# Hush Basin — first courier slice

This is an owner-review candidate based on accepted World Identity / Detail v2
(`0e995643c36d32e4ce03ef0d1b3b390949080480`). It contains one Market → Depot job.
No production deployment, economy, permanent progression or additional contracts.

## Play

On this Mac, double-click **PLAY_COURIER_SLICE.command** (or run
`python3 tools/launch.py`). The existing launcher requires the already-installed
Godot `4.7.1.stable.official.a13da4feb`. Alternatively open `game/project.godot`
in that exact engine and run the project. Native rendering remains Forward+.

You start in free roam on Market's existing inner pad. Press **E / Enter** or
gamepad **B** to open Dispatch, then accept. Release controls to resume.
Drive any legal route to the orange **DEP** minimap cue. Settle on Depot's inner
pad below 6 m/s for half a second. Continue leaves you where you arrived.

W/S drive/brake; A/D steer; Shift changes form; Space Hop. The existing gamepad
movement bindings are unchanged. Esc pauses; R resets. Resetting, falling or a
diagnostic relocation returns the active parcel without recording a delivery.
R also works while paused. Results and Dispatch wait for neutral controls before
releasing the craft. You can drive back to Market and take the same job again.

**PLAY_RUN_V0.command** still launches the unchanged QRY → RLY arcade Run.

## What to judge

1. Take the direct yard shortcut, then try a more expressive route. Does the
   parcel add excitement or anxiety?
2. Drift, transform, Hop and brake normally. Did anything that felt legitimate
   damage the parcel? If so, note the location and action.
3. Try a deliberate wall strike and then deliver anyway. Does the condition
   change seem fair and understandable?
4. Does the controlled Depot arrival feel satisfying? After Results, do you
   want another job?
5. Did Dispatch, HUD, Results or the neutral-input release interrupt flow?

There is no time limit, pace grade or Credit reward. BRRR, longest streak and
peak speed are expressive evidence, independent of cargo condition. Zero
condition still delivers. The direct shortcut is intentionally very short;
this slice asks whether one parcel improves the existing toy, not whether it
already supplies a full game's worth of content.

## Verification and scope

See **COURIER_VERIFICATION.md** for exact results, limitations and commands, and
**COURIER_SLICE_V1_AUTHORITY.md** for the narrow successor authority. The retained
P1B study remains research only. Historical records and validators are retained;
their old source-hash freezes are not silently rewritten.

The adjacent owner-review packet contains native screenshots, a short
normal-input delivery clip, Web screenshots, complete JSON results and logs.
Human cargo fairness, comfort, physical gamepad feel and replay desire remain
open gates for Charlie.
