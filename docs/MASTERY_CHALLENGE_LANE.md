# Mastery alpha — challenge lane findings

Isolated branch `lab/mastery-challenges`, starting exactly at accepted V1.1
`39d098c52b028db3d2b2ca0c41c7c71de89b8791`. This is a lane prototype for lead
review, not an independently integrated game. The current owner commission
authorizes the bounded audit. Historical authorities and all existing source
files remain unchanged in this lane.

The owner accepts the five-job toy and geographic direction. In particular,
Thread and Haul matter because they use previously neglected city. Straight
Drive is enjoyable traversal; the owner does not consider its mere use a skill
challenge. This audit preserves that distinction without changing global BRRR
or the accepted V1.1 drift qualification.

## Five-contract recommendation

| Contract | V1.1 optional objective | Recommendation | Reason |
|---|---|---|---|
| Depot / Freight seals | 3.5 s continuous drift, Drive, 22+ m/s, 15–75° slip | Keep; call it Drift Chain / STYLE | Already distinguishes shaped drift from straight BRRR. No new correctness defect or owner evidence warrants changing the predicate. |
| Relay / Longline coil | 170 m clean Drive, 24+ m/s, <=45° slip | SWEEP: complete the named West Sweep section within 10 s | Rewards executing an actual curved road at pace, not accumulating a mode's distance anywhere. |
| Works / Bench instruments | Arrive with >=85% cargo | Keep CARE | Existing service bar, early unfold/Hop and legal bypasses already create cargo-risk decisions. Minor glances can remain compatible with cargo success. |
| Clinic / South desk kit | Clean west-to-east South Cut crossing in Spread | Keep THREAD | Although form is named, it applies to an actual technical feature with Hop/dogleg choice, rather than being a global Spread timer. Owner evidence accepts its geographic role. |
| Quarry / Shelf survey pack | Drive160 m / Spread40 m / Drive90 m accumulated globally | HAUL: use East Sweep, then cross Quarry Shelf without wall contact | Requires learning a long route and controlling its technical part. The observer no longer asks for mode meters; choose the useful form for the road. |

All five base contracts should remain available. No distinct additional contract
tier was validated here. Locking accepted Thread/Haul behind arbitrary stamp
counts would remove useful geographic variety. Prefer mastery stamps and the
other lane's tiny reward prototype over inventing an untested sixth job or tier.

## Optional section semantics

`route_execution.gd` is a separate observer. Configure from `P1AWorldData`, call
`begin(objective, craft.global_position)` on acceptance, then `sample(craft,dt)`
only during active, unpaused delivery. Merge its primitive snapshot into the
frozen receipt before settlement. It never writes craft, collision, cargo, BRRR,
camera or world state. It uses the accepted cargo contact classifier's
`wall_touch`, never raw controller counter increments from support contact.
The courier lifecycle must still cancel/reset this observer on retry, fall reset
and diagnostic relocation. Spatial discontinuity checks cannot detect a reset
back to the exact same position; the lead should explicitly test a half-earned
Haul followed by that lifecycle transition. The observer does not own reset logic.

SWEEP follows A1 west-to-north. Its timed section begins after the existing GW
junction radius (38 m along the route), and ends before the existing RLY
junction radius (46 m before the route end). The roughly 238 m section contains
the existing 72 m bends. The corridor is A1's authoritative 17 m operational
half-width. The entry band is 8 m deep along the road, allowing normal frame
sampling without a tiny gate. The whole courier delivery clock is separate.

Enter that road band to start the optional section clock. Leaving the road
cancels only that attempt; return to its beginning to try again. A slower
completed section records its time but does not earn the optional objective.
There is no delivery timeout. This is Express, not contact purity: a minor
glance may still pass if the whole section is completed within the reference.
Do not label it a "clean Sweep." BRRR and mode do not enter the predicate.

HAUL first follows A2 in reverse, from the GE junction edge (34 m) to the RLY
junction edge (46 m), inside its existing 17 m operational half-width. It then
follows X0 in reverse from the RLY junction edge (46 m) to the QRY edge (26 m),
inside its existing 12 m operational half-width. The East approach is geographic;
only the Shelf stage requires no wall contact. Mode and elapsed time do not
qualify it. A Shelf wall touch or road departure ends that attempt, even if the
contact caused no cargo loss. This is deliberately stricter than Care and must
be stated to the player. Earned East approach remains; return to the Shelf
entrance to retry. Completed objectives remain earned for that parcel.

Junction trims and corridor widths come directly from the current manifest;
no copied magic world coordinates or new geometry are introduced. Paths use a
4 m sampling of the fixed baked centerlines. Minimum curvature radius is42 m;
sampled chord error stays below0.05 m. The full city remains physically open.
These route requirements affect optional evidence only; shortcuts still deliver
and must still pay base at any cargo condition.

Suggested labels: `SWEEP · West Gate → Relay · 10 s section`, and
`HAUL · East Sweep → clean Quarry Shelf · choose your form`. A restrained entry
cue may help the lead's gameplay-camera review; this lane adds no furniture.
SWEEP entry is A1 arc38 m; Shelf entry is reverse X0 arc46 m. The existing world
data supplies the positions if a cue is warranted.

## Reproducible calibration

Exact installed Godot `4.7.1.stable.official.a13da4feb`, headless,60 Hz physics.
`mastery_challenge_calibration.gd` extends the retained ordinary-input study.
Initial pose is declared before each sample. After the initial reset, it uses
only throttle, brake, steering, transform and Hop inputs. It does not move or
retune the craft during a run. This is automation evidence, not a human feel pass.

The lane ran21 observer-equipped drives, including four exact repeats. Every
one delivered; failed optional attempts are retained. Full traces include mode,
BRRR, strict drift, raw impacts, cargo episodes and route observer evidence.

| Sweep input | Full delivery s | Section s | Optional | Cargo |
|---|---:|---:|---|---:|
| Interior shortcut |19.00|not entered|no|100%|
| Ordinary conservative sweep |34.55|12.40|no|100%|
| All Spread sweep |54.63|24.17|no|100%|
| Deliberate18 m/s sweep |37.37|13.00|no|100%|
| Deliberate21 m/s sweep |35.15|11.30|no|100%|
| Deliberate24 m/s sweep |33.42|10.00|yes|100%|
| Deliberate27 m/s sweep |32.27|9.00|yes|100%|

Ten seconds is chosen between the observed organized fast examples and the
slower/conservative examples. It is not copied from an external review, global
Drive time or owner drift duration. The24 and27 m/s variants repeated with exact
trace/result equality on this engine/platform. The fastest variant includes a
wall episode with zero cargo loss; it remains valid Express evidence, not a
clean-contact claim. The24 m/s variant is contact-free. The final owner target
may still need calibration after human play.

| Haul input | Delivery s | Cargo | Optional | Finding |
|---|---:|---:|---|---|
| Short west route |21.50|100%|no|Never enters East/Shelf challenge. |
| V1.1 accepted mixed recipe |79.65|98.6%|no|Its100 m Drive lookahead persists into Spread; Shelf contact invalidates this new criterion. Historical success remains truthful for V1.1. |
| Hot uninterrupted Drive |61.02|96.3%|no|Delivers quickly but contacts the first Shelf bend. |
| Unfolded, still using100 m lookahead,8/9/10 m/s |97.57 /91.48 /86.98|99.6 /99.2 /98.6%|no|Changing form alone does not fix a poorly shaped line. All failures retained. |
| Mixed, technical12 m Shelf lookahead |88.00|100%|yes|Drive on East Sweep, controlled Spread on Shelf. |
| Mixed, technical16 m Shelf lookahead |87.72|100%|yes|Independent nearby control recipe also clean. |
| Mixed, technical20 m Shelf lookahead |87.45|100%|yes|Third nearby clean variant; no single optimized recipe gate. |
| All Spread |117.63|100%|yes|Slower but deliberate clean traversal is valid. No hidden mode/time requirement. |

The12 and16 m Shelf variants repeat exactly in this lane. These are diagnostic
driver lookahead parameters, never gameplay tuning. Existing route geometry
produces the consequence: fast Drive is efficient on East Sweep; on Shelf,
unfolding and actually steering to the tighter line succeeds. Mere form choice
with the old broad steering plan fails. A skilled human may find a clean Drive
Shelf line and should earn the same mastery.

Final fixed input recipes live in `game/tests/fixtures/mastery_route_trials.json`,
`mastery_haul_refinements.json` and `mastery_route_repeats.json`. For the lead's
native clips use `RLY_committed_27` (or24 for contact-free), and
`HAUL_read_shelf_12` or16. Their route arrays and phase boundaries are explicit.
The full-game review driver can reuse the same plan fields and must continue to
organize its initial pose through ordinary controls as in V1.1.

## Verification and retained evidence

`mastery_route_predicates.gd`:23/23 checks. Includes authoritative gate derivation,
timed reference boundary, route departure/retry, reversed traversal, diagnostic
relocation, direct-road exclusion, incomplete Shelf fragments, clean retry and
absence of hidden mode/time requirements. These are pure observer tests;
they are not counted as driven route samples.

`python3 tools/verify_range_v11.py`: PASS,612 retained inventory entries and
zero unexpected changes. No tracked baseline file is edited in this lane.
Godot import reports sandbox-prohibited editor-settings persistence and the
system-CA warning; scripts compile and runs complete. No install/dependency added.

Evidence beneath the common candidate `evidence/` directory:
`challenge-routes-1/`, `challenge-routes-2/`, `challenge-routes-3/` preserve every
row and full trace; `challenge-route-matrix.json` and `.md` summarize21 runs;
`challenge-repeats.json` records exact repeats; `challenge-predicates.json`
records23 checks; `challenge-v11-preservation.json` records inventory preservation.
The earlier unchanged-observer `challenge-explore/` and initial parse failure
logs are retained as exploratory evidence, not relabeled final passes.

Canonical command shape, with absolute candidate paths as used in the lane:

```sh
/Applications/Godot.app/Contents/MacOS/Godot --headless --fixed-fps 60 \
  --path "$LAB/game" --script res://tests/mastery_challenge_calibration.gd \
  --log-file "$EVIDENCE/challenge-routes-1.log" -- \
  --plans "$LAB/game/tests/fixtures/mastery_route_trials.json" \
  --output "$EVIDENCE/challenge-routes-1"
```

Root paths and exact commands are recorded in
`evidence/challenge-lane-commands.json`. The lead must independently review and
integrate, then run full native/Web, preservation and performance gates. This
lane does not claim those integration passes or human mastery/comfort.

## Rejected and unresolved

- Raising global Drive distance/time does not fix the semantic issue; rejected.
- Making Relay or Haul another drift challenge loses variety; rejected.
- Haul's100 m Drive lookahead in Spread is a diagnostic driver mistake, not
  a movement defect. The failed recipes remain evidence; no craft tuning change.
- No extra contract tier is justified by these runs; do not invent a gate just
  to spend mastery stamps. Progression lane can test a small cosmetic instead.
- No new collision furniture is needed to create these two decisions.
- Named section boundaries require clear HUD/approach explanation. If the entry
  feels invisible, the lead should prefer a restrained cue over hidden generosity.
- Shelf is contact-free even when cargo would forgive a glance. Charlie should
  explicitly judge whether that distinction feels worthwhile or brittle.
- Automation demonstrates separation. It cannot prove the10 s human Express
  target, chosen line's enjoyment or reward motivation.
