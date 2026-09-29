extends "res://scripts/courier/relay_director.gd"
func _input(event: InputEvent) -> void:
	if event is InputEventKey:
		var code: int=event.physical_keycode if event.physical_keycode else event.keycode
		if code in [KEY_E,KEY_ENTER,KEY_X,KEY_ESCAPE]:
			if event.pressed:_held_story_inputs[code]=true
			else:_held_story_inputs.erase(code)
	elif event is InputEventJoypadButton:
		var code: String="%d:%d" % [event.device,event.button_index]
		if event.pressed:_held_story_inputs[code]=true
		else:_held_story_inputs.erase(code)
	if event is InputEventMouse and state in ["DISPATCH","RESULTS","PAUSED"]:return
	if state!="NARRATIVE":super._input(event);return
	if event is InputEventMouse:return # GUI owns pointer buttons; no gameplay forwarding.
	# Consume both edges and repeats before any inherited gameplay/UI handling.
	get_viewport().set_input_as_handled()
	var fresh: bool=(event is InputEventKey and event.pressed and not event.echo) or (event is InputEventJoypadButton and event.pressed)
	if not fresh:return
	var keycode: int=event.physical_keycode if event is InputEventKey and event.physical_keycode else event.keycode if event is InputEventKey else 0
	var button: int=event.button_index if event is InputEventJoypadButton else -1
	if keycode in [KEY_E,KEY_ENTER] or button==JOY_BUTTON_B:primary_action()
	elif keycode==KEY_LEFT or button==JOY_BUTTON_DPAD_LEFT:back_story()
	elif keycode==KEY_X or button==JOY_BUTTON_Y:skip_story()
	elif keycode==KEY_ESCAPE or button==JOY_BUTTON_BACK:
		if summary or reviewing:decline_offer()
		else:skip_story()

const Story=preload("res://scripts/courier/chapter_text.gd")
const SOUTH=Vector2(40,67)
const SOUTH_RADIUS=9.0
var story_store: RefCounted
var dialogue: CanvasLayer
var anchors: Node3D
var conversation:=""
var panel_index:=0
var summary:=false
var reviewing:=false
var acceptance_armed:=false
var release_frames:=0
var receipt_text:=""
var _accepting:=false
var _restoring:=false
var _last_saved_condition:=-1
var _held_story_inputs: Dictionary={}

func _initialize() -> void:
	await super._initialize()
	story_store=preload("res://scripts/courier/chapter_store.gd").new(String(get_tree().get_meta("chapter_test_save","user://opening_chapter_v01.json")))
	var loaded: Dictionary=story_store.load_state();project=story_store
	project_error="" if loaded.ok else String(loaded.error)
	remove_child(hud);hud.queue_free();hud=preload("res://scripts/courier/chapter_hud.gd").new();add_child(hud)
	hud.primary.connect(primary_action);hud.secondary.connect(close_dispatch);hud.select_job.connect(select_contract);hud.purchase.connect(purchase_liner);hud.reset_experiment.connect(reset_experiment);hud.review_conversation.connect(review_local);hud.return_line.connect(return_local)
	hud.mastery_state=session.mastery
	dialogue=preload("res://scripts/courier/chapter_panel.gd").new();add_child(dialogue)
	dialogue.advance.connect(advance_story);dialogue.back.connect(back_story);dialogue.skip.connect(skip_story);dialogue.accept.connect(accept_offer);dialogue.decline.connect(decline_offer)
	# Local interaction metadata only. No terrain/collision/route data is changed.
	gate.data.manifest.destination_pads["TES"]={"center_xz_m":[SOUTH.x,SOUTH.y],"inner_flat_radius_m":SOUTH_RADIUS}
	anchors=preload("res://scripts/courier/chapter_anchors.gd").new();gate.world.add_child(anchors);anchors.configure_chapter(gate.data,craft)
	apply_project_state();refresh_pool("MRK")
	if loaded.ok:restore_narrative()
	update_anchors();print("OPENING_CHAPTER_READY step=",story_store.record.step)

func nearby_hub() -> String:
	for id in ["MRK","RLY","WRK","DEP","CLN","QRY","TES"]:
		if id=="TES" and story_store==null:continue
		if _xz().distance_to(hub_position(id))<=float(gate.data.manifest.destination_pads[id].inner_flat_radius_m):return id
	return ""
func coda_available() -> bool:return story_store!=null and story_store.record.step==7 and story_store.record.after_arc2 and story_store.record.patch
func offer_id() -> String:
	if story_store==null or story_store.record.step>=8:return ""
	if story_store.record.step==7 and not coda_available():return ""
	return Story.ORDER[int(story_store.record.step)]
func refresh_pool(hub: String) -> void:
	if story_store==null:super.refresh_pool(hub);return
	board_hub=hub;selected=0;board_jobs.clear();board_notice=""
	var id:=offer_id()
	if not id.is_empty() and Story.ORIGINS[id]==hub:board_jobs.append(Story.job(id))
	if hub=="RLY" and coda_available():
		var ticket: Dictionary=Story.local_work("TES");ticket.merge({"id":"chapter_ticket","name":"Quarry request","destination":"QRY","place":"Quarry Stores","base":0,"purpose":"Patch kit → Quarry Stores. Pick up at Tess’s counter.","character":"Relay-posted request · view ticket"},true);board_jobs.append(ticket)
	if hub=="MRK":
		for i in 5:
			var c: Dictionary=Catalog.ordinary(i);c.origin=hub;board_jobs.append(c)
	elif hub!="TES" or story_store.record.patch:board_jobs.append(Story.local_work(hub))
	# Before the arc unlock, Tess has no remotely spoken introduction or fake job.
	if board_jobs.is_empty():
		var closed: Dictionary=Story.local_work(hub);closed.merge({"id":"chapter_closed","name":"Counter","base":0,"purpose":"Tess is unpacking. Ordinary paid work is available at Market.","character":"No parcel ready"},true);board_jobs.append(closed)

func guidance_id() -> String:
	var local:=nearby_hub()
	if not local.is_empty():return local
	if story_store==null:return "MRK"
	var id:=offer_id()
	return Story.ORIGINS[id] if not id.is_empty() else "MRK"
func primary_action() -> void:
	if story_store==null:return
	if state=="NARRATIVE":
		if summary:
			if reviewing or not conversation in Story.OFFERS:decline_offer()
			else:accept_offer()
		else:advance_story()
		return
	if state=="DISPATCH" and not _accepting:
		if not project_error.is_empty():return
		var id: String=board_jobs[selected].id
		if id=="chapter_ticket":open_story("ticket");return
		if id=="chapter_closed":return
		if id in Story.ORDER:
			var exchange: String=Story.OFFERS.find_key(id)
			open_story(exchange,false,exchange in story_store.record.seen);return
	if state=="DISPATCH" and not _restoring:
		if not project_error.is_empty():return
		var id: String=board_jobs[selected].id
		if id in Story.ORDER:
			var previous: Dictionary=story_store.record.duplicate(true)
			story_store.record.parcel=id;story_store.record.checkpoint=checkpoint(1000,0)
			if not story_store.commit():story_store.record=previous;project_error=story_store.last_error;return
	var leaving_receipt:=state=="RESULTS"
	if state=="DISPATCH":
		# Acceptance and restore both know the actual pickup, never the old Market default.
		origin=hub_position(board_jobs[selected].origin)
		origin_radius=float(gate.data.manifest.destination_pads[board_jobs[selected].origin].inner_flat_radius_m)
	super.primary_action()
	if leaving_receipt:receipt_text=""
	update_anchors()

func open_story(id: String,past: bool=false,to_summary: bool=false) -> void:
	# A face means here, including reviews and optional return lines.
	if id in Story.SPEAKER and nearby_hub()!=Story.HOME[id]:return
	conversation=id;panel_index=0;summary=to_summary;reviewing=past;acceptance_armed=false;release_frames=0
	if to_summary and not past and not id in story_store.record.seen:
		story_store.record.seen.append(id)
		if story_store.record.pending==id:story_store.record.pending=""
		if not story_store.commit():project_error=story_store.last_error
	state="NARRATIVE";get_tree().paused=true;craft.clear_pending_hop();update_dialogue()
func update_dialogue() -> void:dialogue.display(conversation,panel_index,summary,reviewing,receipt_text,acceptance_armed)
func advance_story() -> void:
	if summary:return
	if panel_index+1<Story.LINES[conversation].size():panel_index+=1;update_dialogue()
	else:finish_conversation(false)
func back_story() -> void:
	if not summary:panel_index=maxi(0,panel_index-1);update_dialogue()
func skip_story() -> void:
	if not summary:finish_conversation(true)
func finish_conversation(skipped: bool) -> void:
	if reviewing:decline_offer();return
	var previous: Dictionary=story_store.record.duplicate(true)
	if not conversation in story_store.record.seen:story_store.record.seen.append(conversation)
	if conversation=="relay":
		state="ACTIVE";settle_delivery(true,"Delivered","quarry_offer")
		if project_receipt.get("ok",false):
			super.primary_action();open_story("quarry_offer",false,skipped or "quarry_offer" in story_store.record.seen)
		return
	story_store.record.pending=""
	if conversation=="tess_final":story_store.record.patch=true
	if not story_store.commit():story_store.record=previous;project_error=story_store.last_error;return
	if conversation in ["ren_return","ivo_return"]:decline_offer();return
	summary=true;acceptance_armed=false;release_frames=0;update_anchors();update_dialogue()
func accept_offer() -> void:
	if state!="NARRATIVE" or not summary or reviewing or not acceptance_armed or not conversation in Story.OFFERS:return
	var id: String=Story.OFFERS[conversation]
	if id!=offer_id() or nearby_hub()!=Story.ORIGINS[id]:return
	dialogue.hide();state="DISPATCH";refresh_pool(Story.ORIGINS[id])
	_accepting=true;primary_action();_accepting=false;receipt_text=""
func decline_offer() -> void:
	if state!="NARRATIVE":return
	dialogue.hide();receipt_text="";_wait_for_neutral("FREE_ROAM")
func local_review() -> String:
	var ids: Array={"MRK":["market"],"RLY":["relay","ren_intro"],"WRK":["works"],"TES":["tess_final","tess_intro"],"DEP":["depot"],"CLN":["clinic"]}.get(board_hub,[])
	for id in ids:
		if id in story_store.record.seen:return id
	return ""
func review_local() -> void:
	if state=="DISPATCH" and not local_review().is_empty():open_story(local_review(),true)
func return_id() -> String:
	if story_store==null or not story_store.record.after_arc1:return ""
	var id: String={"RLY":"ren_return","WRK":"ivo_return"}.get(board_hub,"")
	return "" if id in story_store.record.seen else id
func return_local() -> void:
	if state=="DISPATCH" and not return_id().is_empty():open_story(return_id())

func _process(delta: float) -> void:
	super._process(delta)
	if story_store==null or dialogue==null:return
	refresh_navigation()
	if state=="NARRATIVE" and summary and not acceptance_armed:
		release_frames=release_frames+1 if inputs_neutral() and _held_story_inputs.is_empty() else 0
		if release_frames>=2:acceptance_armed=true;update_dialogue()
	if state=="ACTIVE" and not story_store.record.parcel.is_empty() and cargo.condition_units!=_last_saved_condition:
		save_checkpoint();_last_saved_condition=cargo.condition_units

func refresh_navigation() -> void:
	var active: bool=state=="ACTIVE" or state in ["PAUSED","WAIT_NEUTRAL"] and _resume_state=="ACTIVE"
	var advisory: Array[String]=[]
	if active:
		for route in contract.routes:advisory.append(String(route).trim_prefix("-"))
	# The retained diagnostic menu can write this map too. The current chapter state
	# owns its guidance, including clearing an old line during a handoff or decline.
	if gate.map.highlighted_route_ids!=advisory:gate.map.set_highlighted_routes(advisory)
	gate.map.route_caption=("Suggested · any legal route" if contract.objective=="NONE" else "Optional challenge route") if active and not advisory.is_empty() else "Destination · any legal route" if active else "Pickup / local stop"
	if active:cue.configure(destination,"To "+String(contract.destination))
	elif state=="NARRATIVE":cue.configure(hub_position(Story.HOME[conversation]),Story.HOME[conversation])
	else:
		var id:=guidance_id();cue.configure(hub_position(id),"Stop "+id)
func _finish(delivered: bool,message: String) -> void:
	if story_store==null:super._finish(delivered,message);return
	if not (state=="ACTIVE" or state in ["PAUSED","WAIT_NEUTRAL"] and _resume_state=="ACTIVE"):return
	if delivered and contract.id=="relay_receiver" and story_store.record.step==2:
		story_store.record.pending="relay";save_checkpoint();update_anchors();open_story("relay");return
	var pending: String={"relay_mail":"ren_intro","relay_stock":"works","tess_jackets":"depot","tess_aprons":"clinic","tess_repairs":"tess_final"}.get(contract.id,"") if delivered else ""
	settle_delivery(delivered,message,pending)
	if not pending.is_empty() and project_receipt.get("ok",false):super.primary_action();open_story(pending)
func settle_delivery(delivered: bool,message: String,pending: String) -> void:
	var previous: Dictionary=story_store.record.duplicate(true)
	story_store.record.parcel="";story_store.record.checkpoint={};story_store.record.pending=pending
	super._finish(delivered,message)
	if not project_receipt.get("ok",false):story_store.record=previous
	elif not delivered and not story_store.commit():project_error=story_store.last_error
	receipt_text="%s delivered · Payment +%d received" % [contract.name,contract.base] if delivered else "Parcel returned"
	update_anchors()

func checkpoint(condition: int=-1,seconds: float=-1) -> Dictionary:
	return {"x":craft.global_position.x,"y":craft.global_position.y,"z":craft.global_position.z,"yaw":craft.rotation.y,"condition":cargo.condition_units if condition<0 else condition,"elapsed":elapsed if seconds<0 else seconds}
func save_checkpoint() -> void:
	if story_store==null or story_store.record.parcel.is_empty():return
	story_store.record.checkpoint=checkpoint()
	if not story_store.commit():project_error=story_store.last_error
func _notification(what: int) -> void:
	if what==NOTIFICATION_WM_CLOSE_REQUEST or what==NOTIFICATION_APPLICATION_PAUSED:save_checkpoint()
func restore_narrative() -> void:
	var r: Dictionary=story_store.record
	if not r.parcel.is_empty():
		var cp: Dictionary=r.checkpoint.duplicate(true)
		refresh_pool(Story.ORIGINS[r.parcel]);state="DISPATCH";_restoring=true;_accepting=true;primary_action();_accepting=false;_restoring=false
		state="FREE_ROAM";craft.set_spawn_transform(Transform3D(Basis(Vector3.UP,float(cp.yaw)),Vector3(cp.x,cp.y,cp.z)));craft.reset_craft("chapter_resume");cargo.begin(craft);cargo.condition_units=int(cp.condition);elapsed=float(cp.elapsed);gate.camera_rig.snap_to_target();_wait_for_neutral("ACTIVE")
	if not r.pending.is_empty():
		var p:=hub_position(Story.HOME[r.pending]);state="FREE_ROAM"
		craft.set_spawn_transform(Transform3D(Basis.IDENTITY,Vector3(p.x,gate.data.terrain_height_at(p.x,p.y)+1.65,p.y)));craft.reset_craft("chapter_resume");gate.camera_rig.snap_to_target()
		if r.pending=="relay":cargo.begin(craft);cargo.condition_units=int(r.checkpoint.condition)
		receipt_text="Delivery already received and paid" if r.pending!="relay" else "Receiver ready for handoff"
		open_story(r.pending)
func resume_sentence() -> String:
	var r: Dictionary=story_store.record
	if not r.parcel.is_empty():
		var c:=Story.job(r.parcel);return c.name+" aboard. Deliver to "+c.place+"."
	return ["Relay mail is waiting at Market for Ren.","Ren has the last receiver parts at Relay.","Ivo finished Ren’s receiver. Collect it at Works.","Relay is working. Ren has dry socks ready for Quarry.","Tess is opening her own counter at B11, south of Market.","Clinic’s aprons are ready to collect at Depot.","Clinic has a repair bag for Tess’s new counter.","Relay has a Quarry request. Pick up at Tess’s counter." if coda_available() else "Tess’s counter is open. Ordinary paid work is available.","Quarry received Tess’s patches. Paid work and the Basin remain open."][int(r.step)]
func update_anchors() -> void:
	if anchors!=null:anchors.update_chapter(story_store.record)
func reset_experiment() -> void:
	super.reset_experiment()
	if story_store!=null:
		update_anchors();receipt_text="";refresh_pool("MRK" if state=="DISPATCH" else board_hub);board_notice="Opening Chapter reset. Earlier lab saves are preserved."
