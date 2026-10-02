extends "res://scripts/courier/relay_director.gd"
const Story=preload("res://scripts/courier/narrative_text.gd")
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
	story_store=preload("res://scripts/courier/narrative_store.gd").new(String(get_tree().get_meta("narrative_test_save","user://narrative_presence_v01.json")))
	var loaded: Dictionary=story_store.load_state();project=story_store
	project_error="" if loaded.ok else String(loaded.error)
	remove_child(hud);hud.queue_free();hud=preload("res://scripts/courier/narrative_hud.gd").new();add_child(hud)
	hud.primary.connect(primary_action);hud.secondary.connect(close_dispatch);hud.select_job.connect(select_contract);hud.purchase.connect(purchase_liner);hud.reset_experiment.connect(reset_experiment);hud.review_conversation.connect(review_local)
	hud.mastery_state=session.mastery
	dialogue=preload("res://scripts/courier/narrative_panel.gd").new();add_child(dialogue)
	dialogue.advance.connect(advance_story);dialogue.back.connect(back_story);dialogue.skip.connect(skip_story);dialogue.accept.connect(accept_offer);dialogue.decline.connect(decline_offer)
	anchors=preload("res://scripts/courier/narrative_anchors.gd").new();gate.world.add_child(anchors);anchors.configure(gate.data)
	apply_project_state();refresh_pool("MRK")
	if loaded.ok:restore_narrative()
	print("NARRATIVE_READY stage=",project.stage()," parcel=",story_store.record.parcel)

func refresh_pool(hub: String) -> void:
	super.refresh_pool(hub)
	if hub=="MRK":board_jobs[0]=Story.job("relay_stock")
	elif hub=="WRK":board_jobs[0]=Story.job("relay_receiver")
	elif hub=="RLY":board_jobs[0]=Story.job("relay_quarry")

func primary_action() -> void:
	if story_store==null:return
	if state=="NARRATIVE":
		if summary:accept_offer()
		else:advance_story()
		return
	if state=="DISPATCH" and not _accepting:
		var id: String=board_jobs[selected].id
		if id=="relay_stock" and project.stage()==0:
			open_story("market",false,"market" in story_store.record.seen);return
		if id=="relay_receiver" and project.stage()==1:
			open_story("works",false,true);return
		if id=="relay_quarry":
			open_story("quarry_offer",false,"quarry_offer" in story_store.record.seen);return
	var accepting_job:=state=="DISPATCH"
	if accepting_job and String(board_jobs[selected].id).begins_with("relay_") and not _restoring:
		var previous: Dictionary=story_store.record.duplicate(true)
		story_store.record.parcel=board_jobs[selected].id
		story_store.record.checkpoint=checkpoint(1000,0)
		if not story_store.commit():
			story_store.record=previous;project_error=story_store.last_error;return
	super.primary_action()
	if accepting_job:update_anchors()

func open_story(id: String,past: bool=false,to_summary: bool=false) -> void:
	conversation=id;panel_index=0;summary=to_summary;reviewing=past;acceptance_armed=false;release_frames=0
	state="NARRATIVE";get_tree().paused=true;craft.clear_pending_hop()
	update_dialogue()

func update_dialogue() -> void:
	dialogue.display(conversation,panel_index,summary,reviewing,receipt_text,acceptance_armed)

func advance_story() -> void:
	if summary:return
	if panel_index+1<Story.LINES[conversation].size():panel_index+=1;update_dialogue()
	else:finish_conversation(false)

func back_story() -> void:
	if not summary:panel_index=maxi(0,panel_index-1);update_dialogue()

func skip_story() -> void:
	if not summary:finish_conversation(true)

func finish_conversation(skipped: bool) -> void:
	if reviewing:
		decline_offer();return
	if not conversation in story_store.record.seen:story_store.record.seen.append(conversation)
	if conversation=="relay":
		# Only now does the existing contribution/payment path install and settle.
		story_store.record.pending="";story_store.record.parcel="";story_store.record.checkpoint={}
		state="ACTIVE";super._finish(true,"Delivered")
		if not project_receipt.get("ok",false):
			dialogue.hide();return
		receipt_text="Receiver delivered · Payment +140 received · Relay dispatch available"
		super.primary_action()
		open_story("quarry_offer",false,skipped or "quarry_offer" in story_store.record.seen)
		update_anchors();return
	if conversation=="works":story_store.record.pending=""
	if not story_store.commit():project_error=story_store.last_error
	summary=true;acceptance_armed=false;release_frames=0;update_dialogue()

func accept_offer() -> void:
	if state!="NARRATIVE" or not summary or reviewing or not acceptance_armed:return
	var hub: String={"market":"MRK","works":"WRK","quarry_offer":"RLY"}[conversation]
	dialogue.hide();state="DISPATCH";refresh_pool(hub)
	_accepting=true;primary_action();_accepting=false;receipt_text=""

func decline_offer() -> void:
	if state!="NARRATIVE":return
	dialogue.hide();receipt_text="";_wait_for_neutral("FREE_ROAM")

func review_local() -> void:
	if state!="DISPATCH":return
	var id: String={"MRK":"market","WRK":"works","RLY":"relay"}[board_hub]
	if id in story_store.record.seen:open_story(id,true)

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

func _process(delta: float) -> void:
	super._process(delta)
	if story_store==null or dialogue==null:return
	if state=="NARRATIVE":cue.configure(hub_position("MRK" if conversation=="market" else "WRK" if conversation=="works" else "RLY"),"MRK" if conversation=="market" else "WRK" if conversation=="works" else "RLY")
	if state=="NARRATIVE" and summary and not acceptance_armed:
		# Two neutral process frames after transition; never arm in the final edge.
		release_frames=release_frames+1 if inputs_neutral() and _held_story_inputs.is_empty() else 0
		if release_frames>=2:acceptance_armed=true;update_dialogue()
	if state=="ACTIVE" and not story_store.record.parcel.is_empty() and cargo.condition_units!=_last_saved_condition:
		save_checkpoint();_last_saved_condition=cargo.condition_units

func _finish(delivered: bool,message: String) -> void:
	if story_store==null:super._finish(delivered,message);return
	if not (state=="ACTIVE" or (state in ["PAUSED","WAIT_NEUTRAL"] and _resume_state=="ACTIVE")):return
	if delivered and contract.id=="relay_receiver" and project.stage()==1:
		story_store.record.pending="relay";save_checkpoint();update_anchors();open_story("relay");return
	var first_works: bool=delivered and contract.id=="relay_stock" and project.stage()==0
	story_store.record.parcel="";story_store.record.checkpoint={}
	if first_works:story_store.record.pending="works"
	if delivered and contract.id=="relay_quarry":story_store.record.quarry_done=true
	super._finish(delivered,message)
	if not story_store.commit():project_error=story_store.last_error
	update_anchors()
	if first_works and project_receipt.get("ok",false):
		receipt_text="Receiver kit delivered · Payment +120 received"
		super.primary_action();open_story("works")

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
		refresh_pool("MRK" if r.parcel=="relay_stock" else "WRK" if r.parcel=="relay_receiver" else "RLY")
		state="DISPATCH";_restoring=true;_accepting=true;primary_action();_accepting=false;_restoring=false
		if not cp.is_empty():
			# Resume is a new launch, never a runtime motion correction.
			var pose:=Transform3D(Basis(Vector3.UP,float(cp.yaw)),Vector3(cp.x,cp.y,cp.z))
			state="FREE_ROAM"
			craft.set_spawn_transform(pose);craft.reset_craft("narrative_resume");cargo.begin(craft);cargo.condition_units=int(cp.condition);elapsed=float(cp.elapsed);gate.camera_rig.snap_to_target()
			_wait_for_neutral("ACTIVE")
		if r.pending=="relay":open_story("relay")
	elif r.pending=="works":
		var p:=hub_position("WRK");var pose:=Transform3D(Basis.IDENTITY,Vector3(p.x,gate.data.terrain_height_at(p.x,p.y)+1.65,p.y))
		craft.set_spawn_transform(pose);craft.reset_craft("narrative_resume");gate.camera_rig.snap_to_target();receipt_text="Receiver kit already delivered and paid";open_story("works")
	update_anchors()

func resume_sentence() -> String:
	match String(story_store.record.parcel):
		"relay_stock":return "Ren’s receiver kit is aboard. Deliver it to Ivo at Works."
		"relay_receiver":return "Ren’s receiver is aboard. Deliver it to Relay."
		"relay_quarry":return "Six pairs of dry socks are aboard. Deliver them to Quarry Stores."
	if project.stage()==1:return "Ivo finished Ren’s receiver. Collect it at Works."
	if project.stage()==2:return "Relay is working. Quarry received the dry socks." if story_store.record.quarry_done else "Relay is working. Ren has dry socks ready for Quarry."
	return "Ren is at Market with the last receiver parts."

func update_anchors() -> void:
	if anchors!=null:anchors.update_state(project.stage(),String(story_store.record.parcel),bool(story_store.record.quarry_done),String(story_store.record.pending))

func reset_experiment() -> void:
	super.reset_experiment()
	if story_store!=null:update_anchors();receipt_text="";board_notice="Narrative experiment reset. Session rewards are unchanged."
