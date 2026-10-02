extends "res://scripts/courier/chapter_director.gd"
## Two authored slices beside the unchanged opening; no movement ownership.
const Slice=preload("res://scripts/courier/slices_text.gd")
var appended_receipt:=""
func create_story_store() -> RefCounted:return preload("res://scripts/courier/slices_store.gd").new(String(get_tree().get_meta("chapter_test_save","user://narrative_chapters_v01.json")))
func create_story_hud() -> CanvasLayer:return preload("res://scripts/courier/slices_hud.gd").new()
func create_story_panel() -> CanvasLayer:return preload("res://scripts/courier/slices_panel.gd").new()
func create_story_anchors() -> Node3D:return preload("res://scripts/courier/slices_anchors.gd").new()

func refresh_pool(hub: String) -> void:
	super.refresh_pool(hub)
	if story_store==null or story_store.record.step<8:return
	var local: Array[Dictionary]=[]
	for id in Slice.available(story_store.record):
		if Slice.JOBS[id].origin==hub:local.append(Slice.job(id))
	local.append_array(board_jobs);board_jobs=local
func guidance_id() -> String:
	if story_store==null or story_store.record.step<8:return super.guidance_id()
	var here:=nearby_hub()
	if not here.is_empty():return here
	var offers:=Slice.available(story_store.record)
	return Slice.JOBS[offers[0]].origin if not offers.is_empty() else "MRK"
func primary_action() -> void:
	if story_store==null:return
	if state=="NARRATIVE" and conversation in Slice.SCENES:
		if not summary:advance_story()
		elif reviewing or Slice.SCENES[conversation].offer.is_empty():decline_offer()
		else:accept_offer()
		return
	if state=="DISPATCH" and board_jobs[selected].id in Slice.JOBS:
		if not project_error.is_empty():return
		var id: String=board_jobs[selected].id
		if not _accepting:open_story(Slice.JOBS[id].pickup,false,Slice.JOBS[id].pickup in story_store.record.seen);return
		if not _restoring:
			var previous: Dictionary=story_store.record.duplicate(true)
			story_store.record.parcel=id;story_store.record.checkpoint=checkpoint(1000,0)
			if not story_store.commit():story_store.record=previous;project_error=story_store.last_error;return
	var leaving:=state=="RESULTS"
	super.primary_action()
	if leaving:appended_receipt=""
func open_story(id: String,past: bool=false,to_summary: bool=false) -> void:
	if not id in Slice.SCENES:super.open_story(id,past,to_summary);return
	# Even anonymous notices use their real local handoff; a face never travels.
	if nearby_hub()!=Slice.SCENES[id].home:return
	conversation=id;panel_index=0;summary=to_summary;reviewing=past;acceptance_armed=false;release_frames=0
	state="NARRATIVE";get_tree().paused=true;craft.clear_pending_hop();update_dialogue()
func advance_story() -> void:
	if not conversation in Slice.SCENES:super.advance_story();return
	if summary:return
	if panel_index+1<Slice.SCENES[conversation].lines.size():panel_index+=1;update_dialogue()
	else:finish_conversation(false)
func finish_conversation(skipped: bool) -> void:
	if not conversation in Slice.SCENES:super.finish_conversation(skipped);return
	if reviewing:decline_offer();return
	var previous: Dictionary=story_store.record.duplicate(true)
	if not conversation in story_store.record.seen:story_store.record.seen.append(conversation)
	if conversation in ["ren_answer","ren_letter"] and not conversation in story_store.record.slices.done:story_store.record.slices.done.append(conversation)
	story_store.record.pending=""
	if not story_store.commit():story_store.record=previous;project_error=story_store.last_error;return
	summary=true;acceptance_armed=false;release_frames=0;update_anchors();update_dialogue()
func accept_offer() -> void:
	if not conversation in Slice.SCENES:super.accept_offer();return
	if state!="NARRATIVE" or not summary or reviewing or not acceptance_armed:return
	var id: String=Slice.SCENES[conversation].offer
	if not id in Slice.available(story_store.record) or nearby_hub()!=Slice.JOBS[id].origin:return
	dialogue.hide();state="DISPATCH";refresh_pool(Slice.JOBS[id].origin)
	for i in board_jobs.size():
		if board_jobs[i].id==id:selected=i;break
	_accepting=true;primary_action();_accepting=false;receipt_text=""
func refresh_navigation() -> void:
	if state=="NARRATIVE" and conversation in Slice.SCENES:
		var empty: Array[String]=[];gate.map.set_highlighted_routes(empty);gate.map.route_caption="Local handoff"
		var home: String=Slice.SCENES[conversation].home;cue.configure(hub_position(home),home);return
	super.refresh_navigation()
func _finish(delivered: bool,message: String) -> void:
	if story_store==null or story_store.record.step<8:super._finish(delivered,message);return
	if not (state=="ACTIVE" or state in ["PAUSED","WAIT_NEUTRAL"] and _resume_state=="ACTIVE"):return
	story_store.delivery_destination=contract.destination
	appended_receipt=""
	if delivered and not contract.id in Slice.JOBS and contract.destination=="CLN" and story_store.record.slices.installed and not "clinic_release" in story_store.record.slices.done:
		appended_receipt=Slice.CLINIC_RELEASE;contract=contract.duplicate(true);contract.reaction+="\n\n"+appended_receipt
	var pending: String=Slice.JOBS[contract.id].arrival if delivered and contract.id in Slice.JOBS else ""
	if delivered and pending.is_empty():pending=Slice.arrival_scene(story_store.record,contract.destination)
	if delivered and contract.id=="nell_first_tray":anchors.meal_visit=true
	if delivered and contract.id in ["tray_one","tray_two"]:anchors.market_visit=contract.id
	settle_delivery(delivered,message,pending)
	if not pending.is_empty() and project_receipt.get("ok",false):
		var paid: String=receipt_text+("\n"+String(contract.reaction) if not contract.id in Slice.JOBS else "")
		super.primary_action();receipt_text=paid;open_story(pending)
func _process(delta: float) -> void:
	super._process(delta)
	if story_store==null or anchors==null or story_store.record.step<8 or get_tree().paused:return
	var previous: Dictionary=story_store.record.duplicate(true);var s: Dictionary=story_store.record.slices
	# Work happens only once the courier has left the receiving neighborhood.
	if "new_threshold" in s.done and not s.installed and _xz().distance_to(hub_position("CLN"))>90:s.installed=true
	if "old_threshold" in s.done and not s.bedded and _xz().distance_to(hub_position("QRY"))>90:s.bedded=true
	if "kneeling_pads" in s.done and not s.relined and _xz().distance_to(hub_position("TES"))>50:s.relined=true
	if "thread_box" in s.done and not s.shelf_label and _xz().distance_to(hub_position("TES"))>50:s.shelf_label=true
	if story_store.record!=previous:
		if not story_store.commit():story_store.record=previous;project_error=story_store.last_error
		update_anchors()
	if anchors.meal_visit and _xz().distance_to(hub_position("MRK"))>50:anchors.meal_visit=false;update_anchors()
	if not anchors.market_visit.is_empty() and _xz().distance_to(hub_position("MRK"))>50:anchors.market_visit="";update_anchors()
	# An unladen visit also counts, once parked with controls released. Active jobs
	# settle first in _finish; passing the desk at driving speed never opens a face.
	if state=="FREE_ROAM" and can_dispatch() and craft.velocity.length()<.5 and inputs_neutral():
		var arrival:=Slice.arrival_scene(story_store.record,nearby_hub())
		if not arrival.is_empty():
			story_store.record.pending=arrival
			if story_store.commit():receipt_text="";open_story(arrival)
			else:story_store.record=previous;project_error=story_store.last_error
func restore_narrative() -> void:
	var r: Dictionary=story_store.record
	if not r.parcel in Slice.JOBS and not r.pending in Slice.SCENES:super.restore_narrative();return
	if r.parcel in Slice.JOBS:
		var cp: Dictionary=r.checkpoint.duplicate(true)
		refresh_pool(Slice.JOBS[r.parcel].origin)
		for i in board_jobs.size():
			if board_jobs[i].id==r.parcel:selected=i;break
		state="DISPATCH";_restoring=true;_accepting=true;primary_action();_accepting=false;_restoring=false
		state="FREE_ROAM";craft.set_spawn_transform(Transform3D(Basis(Vector3.UP,float(cp.yaw)),Vector3(cp.x,cp.y,cp.z)));craft.reset_craft("story_resume");cargo.begin(craft);cargo.condition_units=int(cp.condition);elapsed=float(cp.elapsed);gate.camera_rig.snap_to_target();_wait_for_neutral("ACTIVE")
	if r.pending in Slice.SCENES:
		var p:=hub_position(Slice.SCENES[r.pending].home);state="FREE_ROAM"
		craft.set_spawn_transform(Transform3D(Basis.IDENTITY,Vector3(p.x,gate.data.terrain_height_at(p.x,p.y)+1.65,p.y)));craft.reset_craft("story_resume");gate.camera_rig.snap_to_target()
		receipt_text="" if r.pending in ["ren_answer","ren_letter"] else "Delivery already received and paid";open_story(r.pending)
func resume_sentence() -> String:
	if story_store.record.step<8:return super.resume_sentence()
	var r: Dictionary=story_store.record;var s: Dictionary=r.slices
	if r.parcel in Slice.JOBS:
		var c:=Slice.job(r.parcel);return c.name+" aboard. Deliver to "+c.place+"."
	if Slice.chapter_two_complete(r):return chapter_three_resume()
	if not "new_threshold" in s.done:return "Quarry Stores has Clinic's new threshold ready. Ask for B."
	if "clinic_release" in s.done and not "old_threshold" in s.done:return "Clinic released the old threshold. Collect it by the receiving entrance for Bea."
	if not "nell_first_tray" in s.done:return "Clinic received the new threshold. Ren has an empty tray for Nell at Relay."
	if not "clinic_release" in s.done:return "Clinic received the threshold. Its ordinary desk-kit delivery is available at Market."
	if not "quarry_later" in s.done:return "The old threshold is at Quarry. Market has ordinary Quarry work when you want it."
	return "The Basin's desks still have ordinary paid work."
func chapter_three_resume() -> String:
	var r: Dictionary=story_store.record;var done: Array=r.slices.done
	if Slice.chapter_three_complete(r):return "Quarry's sleeve is back. Tess's tagged-mending shelf is working. Ordinary paid work continues."
	var sleeve:="Quarry has a sleeve for Tess. Collect it at Quarry Stores."
	if "quarry_sleeve" in done:sleeve="Tess holds the sleeve. Collect Bea's answer with the pads at Quarry."
	if "kneeling_pads" in done:sleeve="Tess has Bea's answer and is relining the sleeve while you're away."
	if r.slices.relined:sleeve="Tess has relined Quarry's sleeve. Collect it at B11."
	if "relined_sleeve" in done:sleeve=""
	var ren:="Ren has Nell's tray ready at Relay."
	if "tray_one" in done:ren="Ren has another tray for Nell at Relay."
	if "tray_two" in done:ren="Nell's receipt reached Relay. Ren will speak on your next Relay arrival."
	if "ren_answer" in done:ren="Ren has a thread box with a question for Tess. Collect it at Relay."
	if "thread_box" in done:ren="Tess's reply reached Relay. Ren has tagged mending for B11."
	if "tagged_mending" in done:ren="The tagged mending is on Tess's shelf. Ren has a letter at Relay."
	if "ren_letter" in done:ren=""
	return sleeve+("\n" if not sleeve.is_empty() and not ren.is_empty() else "")+ren
func local_review() -> String:
	if story_store!=null:
		for i in range(story_store.record.seen.size()-1,-1,-1):
			var id: String=story_store.record.seen[i]
			if id in Slice.SCENES and Slice.SCENES[id].home==board_hub:return id
	return super.local_review()
func return_id() -> String:
	if story_store!=null and board_hub=="QRY" and "red_return" in story_store.record.slices.done and not "bea_red_return" in story_store.record.seen:return "bea_red_return"
	if story_store!=null and board_hub=="QRY" and "groove_return" in story_store.record.slices.done and not "bea_groove" in story_store.record.seen:return "bea_groove"
	return super.return_id()
func reset_experiment() -> void:
	super.reset_experiment()
	if story_store!=null:board_notice="Story reset. Earlier review saves are preserved.";appended_receipt="";anchors.meal_visit=false;anchors.market_visit="";update_anchors()
