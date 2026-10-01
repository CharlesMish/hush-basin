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
