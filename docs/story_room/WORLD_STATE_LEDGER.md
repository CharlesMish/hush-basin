# Persistent world state ledger

Baseline: [current canon](STORY_CANON_CURRENT.md). “Implemented” means present
in review source, not that every owner has reached or accepted that state.
Visibility below distinguishes source/capture evidence from untested human
recognition. Narrative anchors use simple non-colliding meshes; they do not
change road topology, physics or camera.

| State/change | Cause | Location | Visible during normal play? | Story significance | Implementation status |
| --- | --- | --- | --- | --- | --- |
| Dead receiver/parts case → mail received | Opening mail delivery | Ren's Relay desk | Local bench/props, no reveal camera | Requests reach their person | Implemented; mail remains after delivery |
| Prepared core/kit → finished oversized-dial receiver → receiver leaves | Kit delivery, then explicit receiver acceptance | Ivo's Works bench | Same local receiver shape later used at Relay | Ivo remembers the gloves | Implemented |
| Receiver arrives → mounts, indicator on, dispatch active | Ren's invitation exchange completed/skipped to handoff | Relay receiving desk | Strong local machine/indicator distinction | A working desk and first request | Implemented; completed consequence persists |
| Quarry socks parcel available → leaves rack | Relay activation, then explicit acceptance | Relay rack | Local parcel | Ordinary first answered need | Implemented; not permanent trophy |
| Chair and occupying crate | Opening staging | Works | Local furniture | Supports “her chair” invitation | Static prototype: crate never clears, even after visit lines |
| Half-unpacked counter → open MENDING sign, hanging work, shelves | Clinic repairs delivered and Tess exchange resolved | B11 | Local frontage/counter | Tess has her own working address | Implemented; Chapter 3 sleeve staging later replaces hanging display |
| Apron stack → empty table | Aprons collected at Depot | Depot receiving | Small nearby table | Old address's outstanding work cleared | Implemented |
| Rear-panel scuffs → stitched protective patch | Tess's final opening exchange | Craft rear starboard inner leaf | Small visible child mesh; owner noticeability unresolved | Tess notices courier's own equipment | Implemented cosmetic only; real rigid surface, no cloth cover, no repair stat |
| Patched tarp over new threshold → folded tarp/bare pallet | Chapter 2 threshold loaded | Quarry Stores pallet | Local pale slab silhouette/patches | Prior patch delivery did work | Implemented; coda's exact tarp-repair moment is not animated |
| Old grey dished threshold, pale tracks, raised lip; cart catching | Initial Chapter 2 receiving state | Clinic bay | Normal-view captures supplied | Specific functional reason for new slab | Implemented; static cart staging, not cart physics |
| New pale flat slab on pad → installed bevel/no lip/scuffs/cart across | Delivery, then departure >90 m from Clinic | Clinic | Normal-view before/after captured; scuffs finer than silhouette | Improvement stays in use | Implemented; installation occurs off-screen |
| Old stone leaned on offcuts → released collection → absent | Installation; ordinary Clinic receipt releases; explicit old-stone pickup | Clinic wall beside receiving | Local prop and concrete release text | Release permission, not unclaimed salvage | Implemented; visual staging can precede legal release |
| Old stone on blocks → bedded doorway, pale sawn edge, old wear/tracks, barrow | Return delivery; departure >90 m from Quarry | Quarry shed | Native normal-camera evidence; human object recognition still a playtest gate | Old object gets another practical use | Implemented; next ordinary Quarry delivery hosts observation, no symbolism sign |
| Return crate | Nell's first tray arrival | Market hatch | Local shelf/crate | Stable routine return place | Implemented and persistent |
| Meal/tin/saucer/order → later busy orders → finished-service plate/fork/note | Authored tray visits | Market hatch | Normal local view; bite/fork/paper marks are fine details | Nell is working, then has finished | Implemented visit states; not permanent meals or simulated time |
| Grey-brown sleeve/old sound patch/PLAIN card → sleeve leaves | Chapter 3 starts, then sleeve accepted | Quarry bench | Bench/card/roll in normal-view captures | Misleading sameness of the two faces | Implemented; patch predates opening kit |
| Unrolled sleeve → held on hook | Sleeve delivered; Tess scene resolves | B11 | Counter/hook visible | Waits for Bea's answer | Implemented; no timer or failed patch |
| Pads/note → relining → folded sleeve with broad red lining | Pads delivery; departure >50 m from B11 | Quarry pickup / Tess counter | Fold exposes full red face | Permission plus practical correction | Implemented; retained old outer cloth, flat new working face |
| Sleeve red-side-up; PLAIN struck, RED above, NEVER DOWN ON ITS FACE | Relined sleeve returned | Quarry bench | Normal-view red/card evidence; recognition remains owner judgement | Corrected handling stays after conversation | Implemented; subsequent optional Bea remark never gates progress |
| Thread box → tagged-mending shelf label | Thread delivery/boundary reply; departure >50 m from B11 | Relay desk / B11 shelf | Local box/label | Tess consented to a specific service | Implemented; label permanent, sitting front remains clear |
| Tagged parcel on labelled shelf | First routed mending delivered | B11 | Local shelf parcel | Ren remembers the boundary | Implemented; no portrait at routine drop |
| Opened Stop 9 letter → pinned letter | Ren's final Chapter 3 exchange | Relay desk | Small local paper asset | An invitation/promise remains unresolved | Implemented; no northern visit or automatic removal in current content |

## State and restart contracts

`user://narrative_chapters_v01.json` atomically stores opening step, seen scenes,
pending handoff, active authored parcel/checkpoint, craft patch/intervening-work
flags, slice completion IDs and physical `installed`, `bedded`, `relined`,
`shelf_label` flags. Older review saves are separate. Reset Story clears this
candidate's complete narrative progression and traces; it is explicit.

An accepted authored parcel resumes at its saved position at rest, preserving
condition and elapsed delivery time. A pending handoff returns to its real local
contact. Declining new work preserves the last delivery/payment/consequence.
Ordinary jobs, credits, liner and mastery retain session-only semantics; do not
promise persistence for a generic ordinary cargo merely because story cargo
persists. New Chapter 3 named ordinary legs are authored persisted parcels.

Three attributed completion receipts post subsequent requester state: Tess's
sleeve reply → Bea's pads/answer; Nell's refusal → Ren's next Relay arrival;
Tess's shelf boundary → Ren's tagged parcel. This is the existing finite
receipt/posting channel, not simulated messaging or a new physical errand.

Sources: [opening anchors](../../game/scripts/courier/chapter_anchors.gd),
[receiver anchors](../../game/scripts/courier/narrative_anchors.gd),
[slice anchors](../../game/scripts/courier/slices_anchors.gd),
[off-screen transitions/resume](../../game/scripts/courier/slices_director.gd),
[atomic record/dependencies](../../game/scripts/courier/slices_store.gd),
[reviewed limits](../../NARRATIVE_SLICES_REVIEW.md).
