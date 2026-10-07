# RESPONSE R1–R4 — draft-2 (writer turn 2, ivo-grok-repair-20261006-01)

Review: `astra/astra-review-draft-1.md` (sha256 `364f1e348a6c5a33b0f63955c2ed978e8a3d6050d7b5d1a684861fd47eaad630`), with R1–R4 implemented as editorial decisions. Input `draft-1.md` (sha256 `21a74821fd6fc5444cb51a4614c33e0c688f16f223a9de4661ce7a962ec63ce3`) is untouched. Status: PROPOSED. Astra has not accepted this revision. No Sonnet consult.

## R1 — Compulsory readiness delivery removed
- There are four required deliveries. The bench sequence now finishes on the **same Works visit** as the offcut. Scene 6 (`ivo_stone`) settles and pays the offcut (+140) first, then Ivo seats and checks the stone. Scene 7 (`ivo_done`) follows at the same contact. It is a face pickup whose first panel is Ivo's finished note for Depot, and that paper panel is the time ellipsis. The return offer follows as its own Accept / Not now.
- There is no wait, timer, cutscene, departure gate, new system or fifth job. Ordinary work is never asked for and stays optional.
- **Deleted:** the `faced` flag, "I'll have the dies when you've settled another job…", the readiness paragraph, the readiness job, the intervening-job resume line and the 5→6 save migration.
- **Skip** lands on Scene 7's offer summary (pickup label, ticket and Ivo's finished-work note) without accepting. **Quitting** during Scene 6 reopens the pending exchange at Works, which then hands on to Scene 7. Quitting during Scene 7, or choosing Not now, leaves the offer open and Scene 7 presents again at Works.
- Availability: `dies_return` opens once `flat_offcut` is done and `pending != "ivo_stone"`. Save needs only four done IDs plus dependency rules.

## R2 — Physical account simplified
- One plain counter-die is re-faced and the lettered die is untouched, consistently across Ivo's line, his note and the appendix. Depot's note no longer diagnoses; Ivo does ("The plain one's worn low on one side… only half the seal takes").
- Removed: "flat faces don't meet", "Hold them face to face", "clear to both ends", "second rocks on the bar", the end-for-end proof, and "Somebody checked this twice". The maintained edge is simply trusted.
- Bea now checks the stone against the borrowed edge in plain terms ("That one shows light under the middle. Not that." / "This one. Along, across, corner to corner. No light."), picks the Clinic offcut and sends it back with the edge on top. There is no lecture.

## R3 — The soft-lift / seating-wet mechanism deleted
- That mechanism is gone from the script, notes and appendix. Bea's note no longer carries any seating instruction. Ivo seats the stone himself ("Off the bench. Three feet under it.").
- The new plate is a clean checking reference only: "Nothing gets worked on this. It only tells me when to stop." Scene 2 makes the same split: "Re-facing it is the easy part. Knowing when it's flat is the job." How Ivo does the re-facing is left unspecified.
- Appendix §2.7 adds a short source check: Seals.com Bulldog plain/recessed/raised interchangeable dies, Starrett on inspecting and resurfacing worn plates and on defined support points, and Kemet on checking the lap against a known flat or straightedge. It closes with a plain list of what remains fiction or inference (Depot's press, the lettered/plain pairing, one-sided wear giving half a seal, a dressed offcut being flat enough, lamp-and-edge as the check).

## R4 — Dialogue economy
- Removed "Years on that plate. Ordinary wear." Ordinary wear is now stated once, in Ivo's voice, in Scene 2.
- **Protected and present:** lending his edge ("It doesn't leave the bench, as a rule."), "You carried the receiver.", "It'll keep.", and "I could keep going. It stops being for Depot about here." (Scene 7). "Nobody there will lay an edge on them…" is also retained.
- Pay is **fixed at 120 / 100 / 140 / 120**, and the owner question is removed. The other owner questions are dropped too: whether to keep "You carried the receiver", and the soft-lift question.
- The scenic outbound (leg 2) and smoother return (leg 3) highlights are kept and labelled advisory; the implementer may drop either.
- The "smallest honest count" and "unwitnessed delivery is an invented fact" claims are gone. Four legs is stated as our chosen bounded proposal. There is no new scene, relationship or character. The A1–A4 disposition layers were dropped from the draft, and the appendix is smaller.
