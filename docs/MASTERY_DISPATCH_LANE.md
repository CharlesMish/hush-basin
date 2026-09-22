# Compact Dispatch lane — isolated presentation prototype

Baseline: accepted Mechanics Range V1.1 commit
`39d098c52b028db3d2b2ca0c41c7c71de89b8791`.

Direct owner evidence is preserved verbatim:
“The five-card Dispatch presentation is getting visually busy.”
“The owner wants more variety over time, but does not want Market to become a giant quest-center menu.”

This lane adds a new HUD adapter and isolated UI fixture. It does not replace
the accepted HUD/director, change a contract or settle a receipt. The lead chooses
whether to integrate it. No new assets, fonts, runtime dependencies or external
actions are involved.

## Alternatives reviewed

| Alternative | Benefit | Cost | Decision |
| --- | --- | --- | --- |
| Fixed pages, first three then remaining two | Stable card positions; familiar grouping | A second page has an empty slot; page/selection are separate states; the final jobs can look like a separate or locked tier | Rejected for this five-job pool |
| Three neighboring cards, selected contract centered | Only one selection state; one press reveals the next job; all five remain equally browsable | Selection moves the cards; wraparound shows Quarry beside Depot | Implemented as the isolated adapter |

The board shows real contract numbers, including cards reached by wrapping.
Left/Right and D-pad browse as before; mouse arrows emit the same `select_job`
signal. Keys 1–5 retain absolute contract selection. This is browsing, not a
rotation, availability timer or artificial scarcity system.

## Before / prototype

The baseline puts all five multiline cards in a two-column grid in a
1120 × 610 panel. The prototype shows three cards in one row, selected in the
middle, inside a requested 1032 × 492 panel. Godot containers can grow to fit
minimum content; the fixture checks the measured panel remains within 1280 × 720.

Each card separates destination/number, short name, challenge archetype and route
character, fixed delivery/optional reward, and mastery status. Only the selected
card's exact objective and route description appear below the row. A delivered
job without its optional challenge reads “Delivered · mastery to earn”; a first
optional completion earns one seal, and mastered jobs remain replayable.

The small status line shows session Credits and mastered count. One reward row
explains the approved line-seal + service-seal unlock for a single Lantern amber
trail tint, then shows purchase, then the two-way equipped toggle. This row has
one action, not a store. The existing cargo-liner action remains separate.

Results preserve the fixed additive receipt and run evidence. A small first-time
mastery/unlock line is placed above it. A repeat should show the earned mastery
without awarding another stamp; a failed optional objective still says delivery
counts. Continue remains the existing signal and cannot move the craft.

## Integration contract

Swap only the director's HUD preload to
`res://scripts/courier/mastery_dispatch_hud.gd`, retaining existing four signals:
`primary`, `secondary`, `select_job(index)` and `purchase`.

Assign `hud.mastery_state = session.mastery` once after construction. On Results,
assign `hud.mastery_receipt = session.mastery_receipt(attempt_id)` before refresh;
clear it when accepting the next job. The adapter expects:

- `status(job_id) -> {delivered: bool, mastered: bool}`;
- `mastery_count() -> int`;
- `reward_unlocked() -> bool`, `reward_owned: bool`, `trail_style: String`;
- receipt event `{first_mastery: bool, unlocks: Array[String]}`.

Connect the new `cosmetic` signal to one director action: call `session.buy_trail()`
when unowned/unlocked, otherwise toggle `standard` / `lantern_amber` through
`session.set_trail_style()`. The HUD changes no currency or mastery itself. The
prototype's visible price is 200 Credits, agreed with the progression lane.

The adapter's `objective_progress()` now handles the challenge lane's SWEEP and
geographic HAUL through `job.execution.snapshot`. SWEEP always labels its clock
as a **section** clock, starting after West Gate; the 10-second reference is not
the full delivery time. Finishing over reference still says delivery pays.
HAUL names East Sweep and the clean Quarry Shelf crossing, with no mode or time
requirement. A broken Shelf crossing directs a retry from the Relay end.
`route_complete` means optional-objective success, not merely reaching a section
exit. All STYLE, CARE and THREAD progress delegates to the unchanged old HUD.

The board reads exact objective text and fixed rewards from the catalog; this
lane does not reinterpret or recalibrate them. The shorthand name STYLE is
displayed as DRIFT CHAIN only, matching accepted V1.1 semantics.

## Verification observed

Exact installed engine: `4.7.1.stable.official.a13da4feb`.
Historical `tools/verify_repo.py` reports its already-known three R7 inventory
differences (`.gitignore`, vehicle scene and vehicle rig). Those historical
expectations were not changed. This is not a new R7 pass claim.

Headless `--check-only` parses the adapter. Running
`--script res://tests/mastery_dispatch_probe.gd` passes 120 checks: three slots for
all five selections, selected-center/wrapped-neighbor invariants, measured card
text widths, board viewport bounds, neighbor click selection, distinct
delivered/mastered labels, single cosmetic state transitions, Results viewport
bounds, first-seal/unlock and additive receipt text, pause hiding Results mastery
text, SWEEP section-clock success/miss/retry states, geographic HAUL phases and
clean-crossing retry, and preserved STYLE/CARE/THREAD text. Mock state is confined
to this test. The test creates no world or
craft and proves no gameplay behavior or visual preference.

The headless process emitted the macOS system-CA warning while obtaining local
certificates; the fixture used no network service and all checks completed.
Headless editor import generated the two new script UIDs and completed without
script errors. Saving global editor settings was denied by the filesystem
sandbox; this does not affect the project import or fixture. Newly generated
UIDs for unrelated pre-existing V1.1 scripts are excluded from this lane commit.
Native capture/visual inspection is reserved for the lead's scheduled window.
No native window or browser was started independently by this lane.

For a native fixture capture, run exact Godot at `game/` with
`--script res://tests/mastery_dispatch_probe.gd -- --captures /absolute/new/dir`.
It captures initial browsing, Quarry selection, earned mastery and first-unlock
Results, then exits. The lead should also inspect the integrated board over the
actual Market camera. Human comprehension and comfort remain owner gates.
