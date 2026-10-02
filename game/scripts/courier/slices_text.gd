extends RefCounted
## Exact v1.1 authored text. UI summaries are kept separate from spoken panels.
const Opening=preload("res://scripts/courier/chapter_text.gd")
const RELEASE="QUARRY STORES · One threshold for Clinic receiving entrance, finished face protected. If Clinic has no further use for the old threshold, please release it to Quarry. —B"
const CLINIC_RECEIPT="Received: one threshold for the receiving entrance. It'll be in before the cart's next round. We've seen B's note."
const CLINIC_RELEASE="Cart's stopped rattling at the door. The old threshold by the wall is released to Quarry; we've no further use for it. Collection posted."
const SLEEVE_TAG="New one to this pattern, please. Plain side to the stone. —B"
const SLEEVE_REPLY="Sleeve received. Grit in the lining; patch is sound. Has it been going down face-first? I can reline and keep the cloth, or make new. Holding it till you say. —T"
const NELL_REPLY="Tray in. No extra. Nobody asked me. —N"
const THREAD_NOTE="Could your shelf take south-end drops when you're busy? Parcels, the odd crate. Say no if it's no. —Ren"
const THREAD_REPLY="Thread received. Shelf: tagged mending yes, freight no. —T"
const PADS_NOTE="Yes, on the yard while we clear the bench. That side isn't marked. Reline it if you like. —B"
const RELINED_TAG="Relined. Cloth's got years in it. Red side to the stone. —T"
const CHAPTER_THREE_JOBS=["tray_one","quarry_sleeve","tray_two","thread_box","kneeling_pads","relined_sleeve","tagged_mending"]
const JOBS={
 "new_threshold":{"origin":"QRY","destination":"CLN","name":"New threshold","sender":"Quarry Stores","ticket":"Collection at Quarry Stores: one stone threshold for Clinic's receiving entrance. Ask for B.","docket":RELEASE,"base":140,"reaction":CLINIC_RECEIPT,"routes":["A0","L0","L1","L2"],"pickup":"bea_first","arrival":""},
 "nell_first_tray":{"origin":"RLY","destination":"MRK","name":"Empty meal tray","sender":"Ren · Relay","ticket":"Empty meal tray to Nell at the Market hatch. Use the return crate below the receiving shelf.","docket":"","base":100,"reaction":"Tray received in the return crate.","routes":["L4","L5"],"pickup":"tray_offer","arrival":"nell_first"},
 "old_threshold":{"origin":"CLN","destination":"QRY","name":"Used threshold","sender":"Clinic Receiving","ticket":"Collection at Clinic's receiving entrance: one used threshold, released to B at Quarry Stores. Heavy.","docket":"","base":140,"reaction":"Used threshold received at Quarry Stores.","routes":["-L2","-L1","-L0","-A0"],"pickup":"old_offer","arrival":"bea_old"},
 "tray_one":{"origin":"RLY","destination":"MRK","name":"Meal tray","sender":"Ren · Relay","ticket":"Nell's tray. Return crate below the shelf.","docket":"","base":100,"reaction":"Tray received in the return crate.","routes":["L4","L5"],"pickup":"tray_one_offer","arrival":"","kind":"budgeted tray"},
 "quarry_sleeve":{"origin":"QRY","destination":"TES","name":"Quarry sleeve","sender":"Quarry Stores","ticket":"Collection at Quarry Stores: one sleeve for Tess at B11.","docket":SLEEVE_TAG,"base":120,"reaction":SLEEVE_REPLY,"routes":["A0","L0","L1"],"pickup":"bea_sleeve","arrival":"tess_sleeve","reply_to":"QRY","kind":"story"},
 "tray_two":{"origin":"RLY","destination":"MRK","name":"Meal tray","sender":"Ren · Relay","ticket":"Nell's tray back to Market. Usual return place. She'll do one more for the north crew. Bring it back up with you.","docket":"","base":100,"reaction":NELL_REPLY,"routes":["L4","L5"],"pickup":"tray_two_offer","arrival":"nell_interruption","reply_to":"RLY","kind":"budgeted tray"},
 "thread_box":{"origin":"RLY","destination":"TES","name":"Thread box","sender":"Ren · Relay","ticket":"Thread for Tess at B11. There's a note in with it.","docket":THREAD_NOTE,"base":100,"reaction":THREAD_REPLY,"routes":["L4","L5"],"pickup":"thread_offer","arrival":"tess_boundary","reply_to":"RLY","kind":"ordinary"},
 "kneeling_pads":{"origin":"QRY","destination":"TES","name":"Two kneeling pads","sender":"Quarry Stores","ticket":"Collection at Quarry Stores: two kneeling pads for Tess at B11. Straps want stitching.","docket":PADS_NOTE,"base":100,"reaction":"Mending received. Two kneeling pads for stitching.","routes":["A0","L0","L1"],"pickup":"pads_offer","arrival":"tess_reline","kind":"ordinary"},
 "relined_sleeve":{"origin":"TES","destination":"QRY","name":"Relined Quarry sleeve","sender":"Tess · B11","ticket":"Collection at B11: Quarry's sleeve, relined. To B at Quarry Stores.","docket":RELINED_TAG,"base":120,"reaction":"Relined sleeve received at Quarry Stores.","routes":["-L1","-L0","-A0"],"pickup":"relined_offer","arrival":"bea_red","kind":"story"},
 "tagged_mending":{"origin":"RLY","destination":"TES","name":"Tagged mending parcel","sender":"Ren · Relay","ticket":"Tess's shelf. Tagged mending only. I asked.","docket":"","base":100,"reaction":"On the shelf, thanks. —T","routes":["L4","L5"],"pickup":"mending_offer","arrival":"","kind":"ordinary"}
}
const SCENES={
 "bea_first":{"home":"QRY","speaker":"bea","offer":"new_threshold","lines":["You'll be the courier. I'm B. Tarp's holding. Those patches'll do.","You've come working. We've put the kettle on anyway.","Finished face on the pad. Let them put the first marks on it.","There's a note for Clinic about the old one. If they've no use for it, we'd like it back. If it comes, don't fuss. Everything's already happened to that one."]},
 "tray_offer":{"home":"RLY","speaker":"","offer":"nell_first_tray","lines":[JOBS.nell_first_tray.ticket]},
 "old_offer":{"home":"CLN","speaker":"","offer":"old_threshold","lines":[JOBS.old_threshold.ticket]},
 "nell_first":{"home":"MRK","speaker":"nell","offer":"","lines":["Don't look at the corner. That one's mine. I got here first.","'Extra greens.' I've been picking the greens off his for a year. He never said a word."]},
 "bea_old":{"home":"QRY","speaker":"bea","offer":"","lines":["Hollow between the tracks. That's feet, not the cart.","Leave it by our door. I've got a place for it."]},
 "bea_groove":{"home":"QRY","speaker":"bea","offer":"","lines":["Barrow found the old groove before I did."]},
 "tray_one_offer":{"home":"RLY","speaker":"","offer":"tray_one","lines":[JOBS.tray_one.ticket]},
 "bea_sleeve":{"home":"QRY","speaker":"bea","offer":"quarry_sleeve","lines":["It's been leaving marks on finished work. That patch sits too near the face for my liking."]},
 "tess_sleeve":{"home":"TES","speaker":"tess","offer":"","paper_panels":1,"paper_heading":"BEA'S TAG · carried with the sleeve","lines":[SLEEVE_TAG,"She wants a new one because mine shows.","Hang on. Grit, right through the lining. And 'plain side to the stone'? They're both plain."]},
 "tray_two_offer":{"home":"RLY","speaker":"","offer":"tray_two","lines":[JOBS.tray_two.ticket]},
 "nell_interruption":{"home":"MRK","speaker":"nell","offer":"","lines":["I'd only just sat down.","Ren's promised them another? I didn't say that. I've finished."]},
 "ren_answer":{"home":"RLY","speaker":"ren","offer":"","lines":["Nell's receipt came in. I told the north crew yes on my way to asking her, and never got to the asking.","I've taken it back. They were very nice about it, which was worse."]},
 "thread_offer":{"home":"RLY","speaker":"","offer":"thread_box","lines":[JOBS.thread_box.ticket]},
 "tess_boundary":{"home":"TES","speaker":"tess","offer":"","paper_panels":1,"paper_heading":"REN'S NOTE · carried in the thread box","lines":[THREAD_NOTE,"Mending, yes. Tag it and it goes on the shelf.","Crates, no. Out front's for sitting. Last box I left there, someone sat on it for an hour."]},
 "pads_offer":{"home":"QRY","speaker":"","offer":"kneeling_pads","lines":[JOBS.kneeling_pads.ticket]},
 "tess_reline":{"home":"TES","speaker":"tess","offer":"","paper_panels":1,"paper_heading":"BEA'S NOTE · carried with the pads","lines":[PADS_NOTE,"The seam held. That didn't make the lining fit to use.","New lining, same cloth, and a face you can spot from the bench."]},
 "relined_offer":{"home":"TES","speaker":"","offer":"relined_sleeve","lines":[JOBS.relined_sleeve.ticket,RELINED_TAG]},
 "bea_red":{"home":"QRY","speaker":"bea","offer":"","lines":["Well. Nobody's going to miss that.","It's good. I'd still have bought a new one. Less to check."]},
 "bea_red_return":{"home":"QRY","speaker":"bea","offer":"","lines":["Crew keeps showing me the red side. I've seen the red side."]},
 "mending_offer":{"home":"RLY","speaker":"","offer":"tagged_mending","lines":[JOBS.tagged_mending.ticket]},
 "ren_letter":{"home":"RLY","speaker":"ren","offer":"","lines":["Stop 9. 'Thank you for the jam. I have jam. Come and eat some of it with me.'","I did say I'd go."]}
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
	if chapter_two_complete(r):
		if not "tray_one" in done:ids.append("tray_one")
		elif not "tray_two" in done:ids.append("tray_two")
		if not "quarry_sleeve" in done:ids.append("quarry_sleeve")
		elif not "kneeling_pads" in done:ids.append("kneeling_pads")
		elif r.slices.relined and not "relined_sleeve" in done:ids.append("relined_sleeve")
		if "ren_answer" in done and not "thread_box" in done:ids.append("thread_box")
		elif "thread_box" in done and not "tagged_mending" in done:ids.append("tagged_mending")
	return ids
static func arrival_scene(r: Dictionary,hub: String) -> String:
	if hub!="RLY" or not chapter_two_complete(r):return ""
	if "tray_two" in r.slices.done and not "ren_answer" in r.slices.done and r.pending!="nell_interruption":return "ren_answer"
	if "tagged_mending" in r.slices.done and not "ren_letter" in r.slices.done:return "ren_letter"
	return ""
static func chapter_three_complete(r: Dictionary) -> bool:
	return "relined_sleeve" in r.slices.done and "bea_red" in r.seen and "ren_letter" in r.slices.done
static func chapter_two_complete(r: Dictionary) -> bool:
	return "quarry_later" in r.slices.done and "nell_first_tray" in r.slices.done and not r.pending in ["nell_first","bea_old"]
static func summary(id: String) -> String:
	var scene: Dictionary=SCENES[id]
	if not scene.offer.is_empty():
		var c:=job(scene.offer)
		return Opening.pickup_label(c)+"\n"+c.ticket+("\n\n"+c.docket if not c.docket.is_empty() else "")
	for job_id in JOBS:
		if JOBS[job_id].arrival==id:
			return JOBS[job_id].reaction+("\n\nCarried note\n"+JOBS[job_id].docket if not JOBS[job_id].docket.is_empty() else "")
	return "\n\n".join(scene.lines)
