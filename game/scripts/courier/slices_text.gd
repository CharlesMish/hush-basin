extends RefCounted
## Exact v1.1 authored text. UI summaries are kept separate from spoken panels.
const Opening=preload("res://scripts/courier/chapter_text.gd")
const RELEASE="QUARRY STORES · One threshold for Clinic receiving entrance, finished face protected. If Clinic has no further use for the old threshold, please release it to Quarry. —B"
const CLINIC_RECEIPT="Received: one threshold for the receiving entrance. It'll be in before the cart's next round. We've seen B's note."
const CLINIC_RELEASE="Cart's stopped rattling at the door. The old threshold by the wall is released to Quarry; we've no further use for it. Collection posted."
const JOBS={
 "new_threshold":{"origin":"QRY","destination":"CLN","name":"New threshold","sender":"Quarry Stores","ticket":"Collection at Quarry Stores: one stone threshold for Clinic's receiving entrance. Ask for B.","docket":RELEASE,"base":140,"reaction":CLINIC_RECEIPT,"routes":["A0","L0","L1","L2"],"pickup":"bea_first","arrival":""},
 "nell_first_tray":{"origin":"RLY","destination":"MRK","name":"Empty meal tray","sender":"Ren · Relay","ticket":"Empty meal tray to Nell at the Market hatch. Use the return crate below the receiving shelf.","docket":"","base":100,"reaction":"Tray received in the return crate.","routes":["L4","L5"],"pickup":"tray_offer","arrival":"nell_first"},
 "old_threshold":{"origin":"CLN","destination":"QRY","name":"Used threshold","sender":"Clinic Receiving","ticket":"Collection at Clinic's receiving entrance: one used threshold, released to B at Quarry Stores. Heavy.","docket":"","base":140,"reaction":"Used threshold received at Quarry Stores.","routes":["-L2","-L1","-L0","-A0"],"pickup":"old_offer","arrival":"bea_old"}
}
const SCENES={
 "bea_first":{"home":"QRY","speaker":"bea","offer":"new_threshold","lines":["You'll be the courier. I'm B. Tarp's holding. Those patches'll do.","You've come working. We've put the kettle on anyway.","Finished face on the pad. Let them put the first marks on it.","There's a note for Clinic about the old one. If they've no use for it, we'd like it back. If it comes, don't fuss. Everything's already happened to that one."]},
 "tray_offer":{"home":"RLY","speaker":"","offer":"nell_first_tray","lines":[JOBS.nell_first_tray.ticket]},
 "old_offer":{"home":"CLN","speaker":"","offer":"old_threshold","lines":[JOBS.old_threshold.ticket]},
 "nell_first":{"home":"MRK","speaker":"nell","offer":"","lines":["Don't look at the corner. That one's mine. I got here first.","'Extra greens.' I've been picking the greens off his for a year. He never said a word."]},
 "bea_old":{"home":"QRY","speaker":"bea","offer":"","lines":["Hollow between the tracks. That's feet, not the cart.","Leave it by our door. I've got a place for it."]},
 "bea_groove":{"home":"QRY","speaker":"bea","offer":"","lines":["Barrow found the old groove before I did."]}
}
const HEADINGS={"bea":"BEA · Quarry Stores","nell":"NELL · Market hatch","tess":"TESS · Mending","ren":"REN · Relay operator"}
static func job(id: String) -> Dictionary:
	var c: Dictionary=preload("res://scripts/courier/relay_contracts.gd").outbound()
	c.merge(JOBS[id],true);c.id=id;c.place=Opening.PLACES[c.destination];c.character=c.sender
	c.objective="NONE";c.target=0;c.bonus=0;c.objective_text="Paid delivery · any legal route"
	c.purpose=c.name+" → "+c.place+"\n"+("Release slip travels with the stone." if id=="new_threshold" else "Paid delivery · any legal route.")
	c.dispatch=c.purpose
	return c
static func available(r: Dictionary) -> Array[String]:
	var ids: Array[String]=[]
	if r.step<8:return ids
	var done: Array=r.slices.done
	if not "new_threshold" in done:ids.append("new_threshold")
	elif not "nell_first_tray" in done:ids.append("nell_first_tray")
	if "clinic_release" in done and not "old_threshold" in done:ids.append("old_threshold")
	return ids
static func chapter_two_complete(r: Dictionary) -> bool:
	return "quarry_later" in r.slices.done and "nell_first_tray" in r.slices.done and not r.pending in ["nell_first","bea_old"]
static func summary(id: String) -> String:
	var scene: Dictionary=SCENES[id]
	if not scene.offer.is_empty():
		var c:=job(scene.offer)
		return Opening.pickup_label(c)+"\n"+c.ticket+("\n\n"+c.docket if not c.docket.is_empty() else "")
	return "Exchange complete."
