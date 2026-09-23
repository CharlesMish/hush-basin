extends "res://tests/relay_probe.gd"
## Real input boundaries and normal-input legs; synthetic placements are named.
func press(code: Key,down: bool=true,echo: bool=false) -> void:
	var event:=InputEventKey.new();event.physical_keycode=code;event.keycode=code;event.pressed=down;event.echo=echo;get_viewport().push_input(event)

func run() -> void:
	get_tree().set_meta("narrative_test_save",save_path)
	get_tree().set_meta("relay_test_save",save_path+".legacy")
	review=load("res://review/narrative_presence/review.tscn").instantiate();add_child(review)
	await ticks(120);game=review.game;job=review.job;gate=job.gate;craft=job.craft
	checks["native_forward_plus_or_web_compatibility"]=RenderingServer.get_current_rendering_method()==("gl_compatibility" if OS.has_feature("web") else "forward_plus") if DisplayServer.get_name()!="headless" else true
	if phase=="edges":await edge_cases();finish();return
	if phase=="anchors":await anchor_captures();finish();return
	if phase.begins_with("inspect_"):
		var expected:=phase.trim_prefix("inspect_")
		checks["resume_"+expected]=job.story_store.record.parcel==expected if expected.begins_with("relay_") else job.story_store.record.pending==expected if expected in ["works","relay"] else job.project.stage()==2 and job.story_store.record.quarry_done if expected=="done" else job.project.stage()==int(expected)
		checks["concrete_resume"]=not job.resume_sentence().contains("%") and job.resume_sentence().length()>25
		checks["derived_anchors"]=job.anchors.installed.visible==(job.project.stage()==2)
		if expected.begins_with("relay_"):
			checks["restored_active_parcel"]=job.state=="ACTIVE" and job.contract.id==expected and job.cargo.condition_units==int(job.story_store.record.checkpoint.condition)
		if expected in ["works","relay"]:checks["restored_pending_exchange"]=job.state=="NARRATIVE" and job.conversation==expected
		await capture(phase);finish();return
	if phase=="full" or phase=="fresh":
		key(KEY_E);job.reset_experiment();key(KEY_ESCAPE);await ticks(8)
		checks["fresh_reset"]=job.project.stage()==0 and job.story_store.record.seen.is_empty() and job.story_store.record.parcel.is_empty()
		save_stage("0")
	if phase=="fresh":finish();return
	key(KEY_E);await ticks(4);key(KEY_ENTER);await ticks(3)
	checks["market_stopped_explicit_intro"]=job.state=="NARRATIVE" and job.conversation=="market" and job.attempt_id==0 and get_tree().paused
	await capture("market_dialogue")
	var pose:=craft.global_transform;var fold:=craft.fold_amount;var age: float=gate.get_node("WarmOvercastWeather").active_time
	Input.action_press("throttle");Input.action_press("transform");await ticks(6)
	checks["dialogue_freezes_vehicle_and_weather"]=craft.global_transform==pose and craft.fold_amount==fold and gate.get_node("WarmOvercastWeather").active_time==age
	Driver.release();key(KEY_ENTER);key(KEY_LEFT)
	checks["back_reviews_current_line"]=job.panel_index==0
	key(KEY_ENTER);key(KEY_ENTER);press(KEY_ENTER);await ticks(8)
	checks["last_advance_cannot_accept_held"]=job.summary and job.attempt_id==0 and not job.acceptance_armed
	press(KEY_ENTER,true,true);job.accept_offer()
	checks["echo_and_callback_cannot_accept_held"]=job.attempt_id==0
	press(KEY_ENTER,false);await ticks(4);key(KEY_ESCAPE);await ticks(6)
	checks["decline_does_not_load_kit"]=job.state=="FREE_ROAM" and job.story_store.record.parcel.is_empty()
	key(KEY_E);key(KEY_ENTER);await ticks(4)
	checks["intro_not_repeated"]=job.summary
	key(KEY_ENTER);await ticks(8)
	checks["explicit_accept_loads_kit"]=job.state=="ACTIVE" and job.contract.id=="relay_stock"
	save_stage("relay_stock")
	if phase=="aboard_kit":job.save_checkpoint();finish();return
	route_id="WRK_way";var path: Array[Vector2]=[job.origin,job.destination];await narrative_drive(path,"kit_drive")
	checks["works_paid_before_offer"]=job.session.balance==120 and job.project.stage()==1 and job.state=="NARRATIVE"
	await capture("works_dialogue")
	save_stage("works")
	if phase=="pending_works":finish();return
	var paid: int=job.session.balance;key(KEY_X);await ticks(4)
	checks["works_skip_never_accepts"]=job.summary and job.story_store.record.parcel.is_empty() and job.attempt_id==1
	await capture("works_handoff_offer");key(KEY_ESCAPE);await ticks(6)
	checks["works_decline_keeps_paid_leg"]=job.session.balance==paid and job.project.stage()==1 and job.can_dispatch()
	save_stage("1")
	if phase=="ready_receiver":finish();return
	key(KEY_E);job.review_local();await ticks(2);key(KEY_X);await ticks(6)
	checks["review_has_no_accept_or_payment"]=job.session.balance==paid and job.story_store.record.parcel.is_empty()
	key(KEY_E);key(KEY_ENTER);await ticks(4);key(KEY_ENTER);await ticks(8)
	checks["receiver_loaded_separately"]=job.state=="ACTIVE" and job.contract.id=="relay_receiver"
	save_stage("relay_receiver")
	if phase=="aboard_receiver":job.save_checkpoint();finish();return
	route_id="receiver_leg";await narrative_drive(Driver.road(gate,["-R0","-L4"]),"receiver_drive")
	checks["relay_not_active_before_exchange"]=job.project.stage()==1 and job.session.balance==120 and not job.anchors.installed.visible
	await capture("relay_dialogue");key(KEY_ENTER);await ticks(2)
	checks["invitation_adjacent_to_reply"]=job.dialogue.caption.text=="You pass on Ivo’s invitation." and job.panel_index==1
	await capture("relay_invitation")
	save_stage("relay")
	if phase=="pending_relay":job.save_checkpoint();finish();return
	key(KEY_ENTER);await ticks(4)
	checks["installation_after_exchange"]=job.project.stage()==2 and job.session.balance==260 and job.anchors.installed.visible and job.anchors.indicator.visible
	checks["quarry_request_after_activation"]=job.conversation=="quarry_offer" and job.dialogue.caption.text.contains("dry socks") and job.story_store.record.parcel.is_empty()
	await capture("relay_first_request");key(KEY_X);await ticks(4);key(KEY_ESCAPE);await ticks(6)
	checks["quarry_decline_keeps_relay"]=job.project.stage()==2 and job.session.balance==260 and job.story_store.record.parcel.is_empty()
	checks["relay_resume_has_only_current_parcel"]=not job.hud.readout.text.contains("return pouch") and job.hud.readout.text.contains("dry socks")
	save_stage("2")
	if phase=="relay_active":finish();return
	key(KEY_E);key(KEY_ENTER);await ticks(4);key(KEY_ENTER);await ticks(8)
	checks["quarry_explicit_accept"]=job.state=="ACTIVE" and job.contract.id=="relay_quarry" and job.contract.destination=="QRY"
	save_stage("relay_quarry")
	if phase=="aboard_socks":job.save_checkpoint();finish();return
	route_id="quarry_narrative";await narrative_drive(Driver.road(gate,["-A1","-A0"]),"quarry_drive")
	checks["quarry_receipt_and_pay"]=job.state=="RESULTS" and job.last_result.get("reaction","")==preload("res://scripts/courier/narrative_text.gd").RECEIPT and job.session.balance==360
	pose=craft.global_transform;var velocity:=craft.velocity
	job._finish(true,"duplicate");checks["duplicate_does_not_pay"]=job.session.balance==360
	await capture("quarry_receipt");key(KEY_ENTER)
	checks["quarry_continue_exact_pose"]=craft.global_transform==pose and craft.velocity==velocity
	await ticks(6);checks["player_remains_at_quarry"]=job._xz().distance_to(job.hub_position("QRY"))<8
	save_stage("done")
	finish()

func save_stage(id: String) -> void:
	job.save_checkpoint()
	DirAccess.copy_absolute(save_path,save_path+"."+id)

func pointer(button: Button,down: bool) -> void:
	var event:=InputEventMouseButton.new();event.button_index=MOUSE_BUTTON_LEFT;event.pressed=down;event.position=button.get_global_rect().get_center();get_viewport().push_input(event,true)

func joy(button: int,down: bool) -> void:
	var event:=InputEventJoypadButton.new();event.button_index=button;event.pressed=down;get_viewport().push_input(event)

func edge_cases() -> void:
	key(KEY_E);job.reset_experiment();await ticks(4)
	print("EDGE board ",job.state," rect ",job.hud.accept_button.get_global_rect()," viewport ",get_viewport().get_visible_rect())
	pointer(job.hud.accept_button,true);pointer(job.hud.accept_button,false);await ticks(4)
	print("EDGE after pointer ",job.state," attempt ",job.attempt_id)
	checks["pointer_opens_story"]=job.state=="NARRATIVE"
	pointer(job.dialogue.skip_button,true);pointer(job.dialogue.skip_button,false);await ticks(4)
	checks["pointer_skip_no_accept"]=job.summary and job.attempt_id==0
	pointer(job.dialogue.decline_button,true);pointer(job.dialogue.decline_button,false);await ticks(6)
	checks["pointer_decline_no_accept"]=job.state=="FREE_ROAM" and job.attempt_id==0
	key(KEY_E);await ticks(2);pointer(job.hud.reward,true);pointer(job.hud.reward,false);await ticks(3)
	checks["pointer_reset_confirmation"]=job.hud.reset_dialog.visible
	key(KEY_ESCAPE);await ticks(3);checks["reset_cancel_preserves_seen"]=not job.hud.reset_dialog.visible and "market" in job.story_store.record.seen
	# Synthetic confirmed reset, then real gamepad button edges through the UI.
	job.reset_experiment();key(KEY_ENTER);await ticks(2)
	print("EDGE before joy ",job.state," summary ",job.summary," attempt ",job.attempt_id)
	joy(JOY_BUTTON_Y,true);await ticks(6)
	print("EDGE joy held ",job.state," summary ",job.summary," armed ",job.acceptance_armed," held ",job._held_story_inputs)
	checks["gamepad_skip_held_blocks_accept"]=job.summary and not job.acceptance_armed and job.attempt_id==0
	joy(JOY_BUTTON_B,true);joy(JOY_BUTTON_B,false);checks["gamepad_accept_while_skip_held_rejected"]=job.attempt_id==0
	joy(JOY_BUTTON_Y,false);await ticks(4);joy(JOY_BUTTON_B,true);joy(JOY_BUTTON_B,false);await ticks(8)
	checks["gamepad_fresh_accept"]=job.state=="ACTIVE" and job.attempt_id==1
	# Synthetic settled endpoints isolate the skip/receipt transaction, not routes.
	job.cargo.condition_units=0;place_without_reset(job.destination);await ticks(90)
	checks["zero_condition_story_delivery"]=job.project.stage()==1 and job.session.balance==120
	key(KEY_X);await ticks(4);key(KEY_ENTER);await ticks(8)
	place_without_reset(job.destination);await ticks(90)
	checks["relay_skip_fixture_waits_for_exchange"]=job.project.stage()==1 and job.state=="NARRATIVE"
	key(KEY_X);await ticks(4)
	checks["relay_skip_installs_but_never_accepts"]=job.project.stage()==2 and job.session.balance==260 and job.summary and job.attempt_id==2 and job.story_store.record.parcel.is_empty()
	key(KEY_ESCAPE);await ticks(6);key(KEY_E);job.review_local();await ticks(3);key(KEY_X);await ticks(6)
	checks["relay_review_cannot_reinstall_or_pay"]=job.project.stage()==2 and job.session.balance==260 and job.attempt_id==2

func anchor_captures() -> void:
	for id in ["WRK","RLY"]:
		var p: Vector2=job.hub_position(id)+Vector2(-4,5) if id=="WRK" else job.hub_position(id)+Vector2(0,6)
		await reset_at(p)
		craft.rotation.y=-.65 if id=="WRK" else 0.0;gate.camera_rig.snap_to_target();get_tree().paused=true
		job.set_process(false);gate.set_process(false);gate.pause_panel.hide();job.hud.hide();job.dialogue.hide();job.cue.hide()
		job.anchors.hide();await capture(id+"_before_anchors")
		job.anchors.show();job.anchors.update_state(0 if id=="WRK" else 1,"",false)
		await capture(id+"_incoming_or_bracket")
		job.anchors.update_state(1 if id=="WRK" else 2,"",false)
		await capture(id+"_finished_or_installed")
		get_tree().paused=false;job.set_process(true);gate.set_process(true);job.hud.show()
	checks["anchor_capture_fixture"]=true

func narrative_drive(path: Array[Vector2],id: String) -> void:
	var r: Dictionary=await Driver.drive(self,path)
	routes.append({"id":id,"result":r})
	checks[id]=job.state in ["NARRATIVE","RESULTS"] and r.reset_delta==0
