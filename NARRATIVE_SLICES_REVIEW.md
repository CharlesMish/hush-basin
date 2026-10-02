# Narrative Chapters 2 + 3 v0.1 — implementation record

Starting authority: `fix/opening-chapter-ux-v0.1`, exact clean HEAD
`9a559f95c1ec5eea910affd17b52d02eac562476`. Successor:
`experiment/narrative-chapters-2-3-v0-1`. No remote or production action.

## Checkpoint A — Chapter 2

The complete opening continues into Quarry's new threshold, Nell's first tray,
an ordinary Clinic arrival releasing the old threshold, its separate paid
return, and an ordinary Quarry arrival revealing its reuse. Optional later Bea
remark remains local. All authored ticket, dialogue, release slip and receipt
text is in `game/scripts/courier/slices_text.gd`, with the source drafts copied
byte-for-byte into `docs/`.

The successor subclasses the accepted chapter director, HUD, panel and anchors.
Four factory methods are the only existing director changes. Existing fixtures
keep their original scene; one new default scene runs the entire story.
Finite save flags extend the existing atomic-save pattern. `Reset Story` clears
this candidate's story; `user://narrative_chapters_v01.json` is separate from
the owner's older review saves. No narrative component owns vehicle simulation.

Completed deliveries settle before the portrait. Skip reaches the receipt or
offer summary without accepting. The inherited neutral-release barrier guards
every explicit acceptance. Physical installation/reuse happens after departure.

### Inspected adaptations and omissions

- No ordinary soap or chisel job exists. Existing `clinic_thread` (South desk
  kit) and `quarry_haul` (Shelf survey pack) host the ordinary arrivals. Their
  original receipts and optional challenges remain; Clinic appends the exact
  release text. The chisel-specific Bea line is omitted as allowed by the draft.
- The actual Clinic door is a closed decorative door on a raised plinth; Quarry
  has no shed beside the receiving stop. Small open, non-colliding receiving
  bays support the authored threshold/cart/barrow. No road or collider changes.
- No Nell portrait existed in the authoritative source. One temporary standard
  portrait was created and will be reused unchanged in Chapter 3. Bea has one
  temporary portrait. Both are original generated assets, not scraped art.
- Existing cargo condition cannot distinguish a fresh stone chip. That optional
  line is disabled; ordinary delivery never fails because of cargo condition.
- No existing tray receipt exists. The new neutral standard receipt is
  “Tray received in the return crate.” No authored line was rewritten.

The old slab retains grey silhouette, two pale tracks and a dished center. The
new one is pale/flat with a bevel. The reused slab retains its wear and has a
sawn edge, with a barrow wheel aligned to a track. Native normal-camera captures
show these distinctions; recognition and emotional effect remain owner gates.

### Prototype portrait provenance

Generated with the installed imagegen skill using the accepted Ren portrait as
a style reference, then stored as `bea.png` and `nell.png`; imports are limited
to 512px. One state each. The source images are original generated PNGs.

Bea direction: practical Quarry Stores adult woman B, grounded dry welcome,
sturdy grey/ochre workwear and dusty sleeves, tied-back hair, weathered face,
hands, readable at 238px, restrained painted realism/mineral palette/overcast
light/plain dark warm-grey field, distinct from Ren; no text/anime/stock styling.

Nell direction: adult food-hatch woman, practical apron and clay shirt, tied
hair, alert unsentimental neutral dry reserve suitable for service and an
interruption; same style; no seated/finale/angry variants, scene or background
humans. These are coherent placeholders, not final character illustration.

### Checkpoint A evidence

Evidence root: `../Hush-Basin-Chapters-2-3-v0.1-Review/evidence/`.
Exact engine: `4.7.1.stable.official.a13da4feb`, native Metal Forward+.

- Untouched baseline: 882 checks / 36 runs PASS; exact 1,260-tick movement SHA
  `29f1049f8e16ec65d288407c35e6ccae46e87c711bb6b54b134e6158c68b9443`.
- Fresh opening → Chapter 2, same instance: 128 checks PASS headless and Web.
- Chapter 2 native final: 44 checks PASS; normal-camera screenshots inspected.
- Five delivery routes driven through ordinary inputs: 49 checks PASS, no
  resets. Pickup repositioning is a fixture, not a claim of human play.
- Three independent process restarts (delivered, released, returned): 4 checks
  each PASS. Concrete resume and physical flags preserved.
- Web compatibility diagnostic: 128 checks PASS, no captured warnings/errors.
  This diagnostic predates the final slab orientation/readability-only edits;
  the native final run includes them. Final integrated export will recheck all.

Commands: `python3 tools/verify_slices.py --output <new-evidence-folder>` with
`--phase contiguous`, `--phase drive`, `--native`, or `--resume <snapshot>
--phase resume_<stage>` as applicable. Every run saves its exact command.
Historical full suite: `python3 tools/verify_opening_chapter.py --output
<new-evidence-folder> --native`. Local Web: `tools/export_web.py --slices-smoke`.

No attachment, comfort, desire, timing or recognition owner gate is claimed.

## Checkpoint B — Chapter 3

Checkpoint A was committed as `31677586809b56ba9993802b33ca3eb1fa6d6828`
before Chapter 3 implementation began. Checkpoint B and final HEAD are recorded
in the adjacent owner package's `package.json` and director report.

Seven finite paid legs implement the draft. Tray 1 and tray 2 are budgeted tray
jobs; sleeve outward/return are story jobs; thread, pads and tagged mending are
ordinary deliveries carrying required context. No matching ordinary Relay→B11
or Quarry→B11 jobs existed, so these three are posted through the existing local
dispatch catalog. They have ordinary pay and no mastery, condition or time gate.
Other ordinary jobs remain available throughout.

The sleeve and Ren branches have independent prerequisites. The sleeve branch
ends after its return and Bea's exchange; Ren's ends after the letter exchange.
`chapter_three_complete` requires both. No Chapter 4 content is implemented.

### Replies and arrival encounters

The established completion-receipt/project-posting path carries all three
replies, with their exact signatures and a visible “Receipt to” heading:

| Completion | Requester state it posts |
| --- | --- |
| Tess receives sleeve; exact grit/patch/holding receipt | Quarry posts Bea's pads and answer |
| Nell receives second tray; exact refusal receipt | Ren's answer on the next Relay arrival |
| Tess receives thread; exact tagged-mending/freight boundary | Relay posts tagged mending |

Ren's answer and letter have no courier job IDs or reward. They attach after
an ordinary Relay delivery settles, or to an unladen Relay visit once parked
below 0.5 m/s with released controls. Neither opens during active driving.
The tests use the unchanged ordinary `relay_window` coil delivery as their host.
The extra meal is ticket prose only: active cargo and objective are the tray.

Remote notes use anonymous paper panels before the local recipient's portrait.
Skip exposes the exact note plus attributed receipt at the summary; a fresh
input is always required to accept a new job. Optional local review cannot pay
or advance progress. Existing opening dialogue and portraits remain unchanged.

### Physical traces and persistence

- The original sleeve is grey-brown on both faces, with a sound earlier patch,
  grit and a tag. It unrolls at Tess's handoff, then hangs behind the counter.
- Relining waits for departure from the B11 neighborhood (50 m, enough for a
  normal Market visit). The folded sleeve exposes a broad red canvas face. The
  old outer cloth and its patch remain underneath; the working face has no ridge.
- The returned sleeve rests red-side-up. Quarry's physical card strikes PLAIN,
  adds RED above, and adds NEVER DOWN ON ITS FACE. The optional later Bea line
  needs an ordinary Quarry arrival and never gates completion.
- B11's MENDING — TAGGED, PLEASE label appears while away after the boundary
  exchange. The parcel rests on that shelf. Front space stays clear except for
  the stool; the accepted stop remains (40,67), radius 9 m.
- Market's visit-only service props and partially lowered hatch use the same
  stool. No human model or animated background pose. Return crate persists.
- The letter is pinned after Ren's last line. The northern address is not a
  playable destination. All authored optional cosmetics were implemented as
  simple primitives; fine paper markings and the fork/bite are small details.

The finite atomic record adds `relined` and `shelf_label`; checkpoint A records
migrate by adding those false flags, without inventing progress. Concrete resume
text names the current parcel/destination or available work at its real pickup.
Both unfinished leads are available at dispatch; driving shows one short lead.
Clean reset clears all three chapters and visual flags while preserving older
review saves and existing session-reward semantics.

### Final validation

| Check | Observed result |
| --- | --- |
| Retained native/headless suites | 882 checks / 36 runs PASS |
| Exact native movement | Original 1,260-tick SHA remains exact |
| Fresh opening→2→3, one instance | 275 checks PASS; synthetic travel for state/UI coverage |
| Native Chapter 2 / Chapter 3 integration | 44 / 139 checks PASS |
| Driven Chapter 2 / Chapter 3 deliveries | 49 / 148 checks PASS; no route resets |
| Ren-first and sleeve-first | 140 checks each PASS; the unfinished branch remains available |
| B11 ordinary-input approaches | 19 checks PASS from Market, Clinic, Depot; no impacts/resets; 25 ground samples clear |
| New atomic store / dependency validation | 45 checks PASS |
| Separate-process slice resumes | 124 checks / 16 processes PASS |
| Retained project persistence | 56 checks / 9 processes PASS |
| Exact authored text | 46 of 48 blockquoted passages exact; only the two authorized conditional omissions above |
| Web complete story | 275 checks PASS; no captured warnings/errors |
| Web close/reopen | Held sleeve and both-complete snapshots: 8 checks each PASS; no captured warnings/errors |
| Clean extracted native launch | Exact-engine import/parse PASS; isolated fresh-save native launch 7 checks PASS |
| Source scope | 827 of 835 starting files byte-identical; eight named wrapper/seam/document exceptions |

The native trace SHA is
`29f1049f8e16ec65d288407c35e6ccae46e87c711bb6b54b134e6158c68b9443`.
There is no numeric Web/native movement-parity fixture in the authoritative
harness; no cross-platform bit identity is claimed. Web uses the same preserved
controller source and Compatibility renderer; native remains Forward+.

Final package runtime files match the clean-extraction launch exactly. The Web
diagnostic uses those same runtime files; the later test-only resume predicate
fix does not change the game. Source manifests retain per-file hashes.

Development evidence retains a failed first departure-radius test, corrected
before the successful thread-order runs. A first approach fixture accidentally
used the legacy driver's “any nearby desk” arrival rule; the final approach run
uses the accepted coordinate-target driver. Resume test heuristics initially
rejected a short concrete sentence and omitted Market/South counter from their
place list; final checks cover the actual place catalog. These were test issues,
not lost save data. Original failed evidence is retained, not relabelled PASS.

Final Web diagnostic is 144,832,516 raw bytes / 26,423,283 estimated gzip bytes:
+790,955 raw (+0.55%) / +620,283 gzip (+2.40%) versus accepted opening UX.
No hosting change. No controlled performance benchmark was added; the regression
runs and captures are not a frame-rate or human comfort claim.

Additional reproducible commands:

```sh
python3 tools/verify_slices.py --phase complete --output <new-folder>
python3 tools/verify_slices.py --phase ren_first --output <new-folder>
python3 tools/verify_slices.py --phase sleeve_first --output <new-folder>
python3 tools/verify_slices.py --phase drive_three --output <new-folder>
python3 tools/verify_slices.py --phase approaches --native --output <new-folder>
python3 tools/verify_slices_restarts.py --evidence <evidence-root> --name <new-name>
python3 tools/verify_slices_text.py
python3 tools/verify_slices_preservation.py
python3 tools/package_story.py --output <new-zip> --extract <new-directory>
```

### Remaining implementation choices and test limits

No authored dialogue, ticket, note or mandatory receipt was rewritten. Standard
neutral receipts were supplied for the new tray, used-threshold, relined-sleeve
and pads jobs, where the draft requests an ordinary receipt but supplies none.
Their exact strings remain visible in the small text catalog. Notes occupy an
extra anonymous panel to preserve the existing portrait/locality grammar.

The new bays and large, readable handling cards are deliberately spare prototype
staging. New/old slabs, sleeve, scuffs, patch, labels and meal props are original
code geometry with no new collision. The cart/barrow are static staged props,
as permitted by the source; there is no animated installation or forced camera.

Potential test contamination: two new temporary portraits, coarse object art,
explicit resume leads and required paper panels may affect attachment/readability
or interruption cost. Tests establish state and presentation function, not
whether the people and work remain compelling. No autonomous story expansion
should follow a weak owner result. Stop for Charlie's playtest.
