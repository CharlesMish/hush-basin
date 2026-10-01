extends "res://tests/narrative_probe.gd"
const Chapter=preload("res://scripts/courier/chapter_text.gd")
var review_scene_path:="res://review/opening_chapter/review.tscn"
func run() -> void:
	get_tree().set_meta("chapter_test_save",save_path);get_tree().set_meta("relay_test_save",save_path+".legacy")
	review=load(review_scene_path).instantiate();add_child(review);await ticks(120)
	game=review.game;job=review.job;gate=job.gate;craft=job.craft
	checks["chapter_initialized"]=job.story_store!=null and job.anchors!=null
	if job.story_store==null:finish();return
	checks["native_forward_or_web"]=RenderingServer.get_current_rendering_method()==("gl_compatibility" if OS.has_feature("web") else "forward_plus") if DisplayServer.get_name()!="headless" else true
	if phase.begins_with("inspect_"):
		var expected:=phase.trim_prefix("inspect_")
		checks["resume_step"]=job.story_store.record.step==int(expected.split("_")[0])
		checks["patch_matches"]=job.anchors.patch.visible==job.story_store.record.patch
		checks["resume_concrete"]=job.resume_sentence().length()>25 and not job.resume_sentence().contains("%")
		checks["loaded_without_error"]=job.project_error.is_empty()
		if not job.story_store.record.pending.is_empty():checks["pending_restored_local"]=job.state=="NARRATIVE" and job.conversation==job.story_store.record.pending and job.nearby_hub()==Chapter.HOME[job.conversation]
		elif not job.story_store.record.parcel.is_empty():checks["parcel_restored"]=job.state=="ACTIVE" and job.contract.id==job.story_store.record.parcel and job.cargo.condition_units==int(job.story_store.record.checkpoint.condition)
		await capture(phase);finish();return
	key(KEY_E);job.reset_experiment();key(KEY_ESCAPE);await ui_frames()
	checks["fresh_one_chapter"]=job.story_store.record.step==0 and not job.story_store.record.patch and job.story_store.record.seen.is_empty()
	save_stage("0_fresh")
	if phase=="fresh":finish();return
	if phase=="visuals":await chapter_visuals();finish();return
	if phase=="edges":await chapter_edges();finish();return
	for step in 8:
		var id: String=Chapter.ORDER[step];var hub: String=Chapter.ORIGINS[id]
		if step==7:
			checks["coda_waits_for_other_job"]=not job.coda_available()
			# A real separate paid pickup, settled at Depot; synthetic travel in guards phase.
			await leave_story();await relocate("TES")
			key(KEY_E);job.refresh_pool("TES");job.selected=0;key(KEY_ENTER);await ui_frames()
			checks["ordinary_mending_unlocked"]=job.contract.id=="mending_pickup" and job.state=="ACTIVE"
			await travel(line(job._xz(),job.hub_position("MRK"))+Driver.road(gate,["-L1"]),"ordinary_after_arc2")
			key(KEY_ENTER);await ui_frames();checks["coda_after_other_delivery"]=job.coda_available()
		if not (job.state=="NARRATIVE" and Chapter.OFFERS.get(job.conversation,"")==id):
			await leave_story()
			if job._xz().distance_to(job.hub_position(hub))>3:await relocate(hub)
			key(KEY_E);await ticks(3);job.refresh_pool(hub);key(KEY_ENTER);await ticks(3)
		checks[id+"_local_face"]=job.state=="NARRATIVE" and job.nearby_hub()==Chapter.HOME[job.conversation] and job.dialogue.portrait.visible==(job.conversation in Chapter.SPEAKER)
		await capture(id+"_dialogue")
		if id in ["tess_jackets","tess_patches"]:checks[id+"_no_stale_receipt"]=job.receipt_text.is_empty()
		var pose:=craft.global_transform;var fold:=craft.fold_amount
		Input.action_press("throttle");await ticks(3);Driver.release()
		checks[id+"_paused_vehicle"]=craft.global_transform==pose and craft.fold_amount==fold
		var attempts: int=job.attempt_id
		# One real held Skip edge must not arm or accept, even through a callback.
		if not job.summary:
			press(KEY_X);await ui_frames();job.accept_offer()
			checks[id+"_skip_guard"]=job.summary and not job.acceptance_armed and job.attempt_id==attempts
			press(KEY_X,false);await ui_frames()
		else:checks[id+"_summary_no_auto_accept"]=job.story_store.record.parcel.is_empty() and job.attempt_id==attempts
		key(KEY_ESCAPE);await ui_frames()
		checks[id+"_decline_preserves"]=job.story_store.record.step==step and job.story_store.record.parcel.is_empty()
		key(KEY_E);key(KEY_ENTER);await ui_frames()
		checks[id+"_no_reintroduced"]=job.summary
		key(KEY_ENTER);await ui_frames()
		checks[id+"_explicit_accept"]=job.state=="ACTIVE" and job.contract.id==id and job.attempt_id==attempts+1
		save_stage(str(step)+"_aboard")
		if phase=="guards":job.cargo.condition_units=0;job.elapsed=3600
		await travel(chapter_path(id),id)
		if id=="relay_receiver":
			checks["receiver_waits_exchange"]=job.story_store.record.step==2 and not job.anchors.installed.visible
			key(KEY_ENTER);await ticks(2);checks["invitation_handoff"]=job.dialogue.caption.text=="You pass on Ivo’s invitation."
			await capture("relay_invitation");save_stage("2_pending");key(KEY_X);await ui_frames()
			checks["relay_skip_no_accept"]=job.story_store.record.step==3 and job.anchors.installed.visible and job.attempt_id==attempts+1 and job.story_store.record.parcel.is_empty()
		else:checks[id+"_settled"]=job.story_store.record.step==step+1 and job.project_error.is_empty()
		if id=="tess_repairs":
			await capture("tess_final");save_stage("7_pending")
			key(KEY_ENTER);await capture("tess_surface_line");key(KEY_X);await ui_frames()
			checks["patch_after_exchange"]=job.story_store.record.patch and job.anchors.patch.visible and not job.anchors.scuff.visible
			checks["counter_and_depot_consequences"]=job.anchors.hanging.visible and not job.anchors.apron_stack.visible
		if step==3:checks["returns_not_early"]=not job.story_store.record.after_arc1
		if step==4:checks["returns_after_other_job"]=job.story_store.record.after_arc1
		await capture(id+"_receipt");save_stage(str(step+1)+"_received")
		var balance: int=job.session.balance;job._finish(true,"duplicate")
		checks[id+"_once_only_pay"]=job.session.balance==balance
	await leave_story();checks["ends_at_quarry"]=job.nearby_hub()=="QRY" and job.story_store.record.step==8
	for hub in ["WRK","RLY"]:
		# Optional-return guard fixtures begin after the contiguous chapter finishes.
		await reset_at(job.hub_position(hub));key(KEY_E);await ticks(3);var balance: int=job.session.balance;var id: String=job.return_id();job.return_local();await ticks(2)
		checks[hub+"_optional_return_local"]=job.state=="NARRATIVE" and job.conversation==id and job.dialogue.portrait.visible
		await capture(hub+"_return");key(KEY_ENTER);await ui_frames();key(KEY_E)
		checks[hub+"_return_once"]=job.return_id().is_empty() and job.session.balance==balance
		job.review_local();await ticks(2);key(KEY_X);await ui_frames()
		checks[hub+"_review_no_pay"]=job.session.balance==balance and job.story_store.record.step==8
	save_stage("8_done");finish()

func leave_story() -> void:
	if job.state=="NARRATIVE":
		if not job.summary:key(KEY_X);await ui_frames()
		key(KEY_ESCAPE);await ui_frames()
	if job.state=="RESULTS":key(KEY_ENTER);await ui_frames()
	if job.state=="DISPATCH":key(KEY_ESCAPE);await ui_frames()
func relocate(hub: String) -> void:
	if phase=="guards":await reset_at(job.hub_position(hub));return
	var path: Array[Vector2]=[]
	if job.nearby_hub()=="QRY":path=Driver.road(gate,["A0","L0","L1"])
	elif job.nearby_hub()=="DEP":path=Driver.road(gate,["L1"])
	else:path=[job._xz()]
	path.append_array(line(path[-1],job.hub_position(hub)))
	route_id="reposition_"+hub
	var r: Dictionary=await preload("res://tests/chapter_driver.gd").drive(self,path,true,true)
	routes.append({"id":route_id,"result":r});checks[route_id+str(routes.size())]=r.arrived_home and r.reset_delta==0
func line(a: Vector2,b: Vector2) -> Array[Vector2]:
	var points: Array[Vector2]=[];var count:=maxi(1,ceili(a.distance_to(b)/.25))
	for i in count+1:points.append(a.lerp(b,float(i)/count))
	return points
func chapter_path(id: String) -> Array[Vector2]:
	match id:
		"relay_mail":return Driver.road(gate,["-L5","-L4"])
		"relay_stock":return Driver.road(gate,["L4","R0"])
		"relay_receiver":return Driver.road(gate,["L7","-A2"])
		"relay_quarry":return Driver.road(gate,["-A1","-A0"])
		"tess_aprons":return Driver.road(gate,["S0","DOG","S1"])
		"tess_jackets":return line(job._xz(),job.hub_position("MRK"))+Driver.road(gate,["-L1"])
		"tess_patches":return line(job._xz(),job.hub_position("MRK"))+Driver.road(gate,["-L1","-L0","-A0"])
		_:return [job._xz(),job.destination]
func travel(path: Array[Vector2],id: String) -> void:
	if phase=="guards":place_without_reset(job.destination);await ticks(90)
	else:
		route_id="WRK_way" if id=="relay_stock" else id
		await narrative_drive(path,id+"_drive")
func chapter_visuals() -> void:
	for hub in ["TES","RLY","DEP"]:
		await reset_at(job.hub_position(hub));craft.rotation.y=PI if hub=="TES" else 0.0;gate.camera_rig.snap_to_target()
		get_tree().paused=true;job.set_process(false);gate.set_process(false);gate.pause_panel.hide();job.hud.hide();job.dialogue.hide();job.cue.hide()
		var r: Dictionary=job.story_store.record.duplicate(true)
		job.anchors.update_chapter(r);await capture(hub+"_before")
		r.step=7;r.patch=true;job.anchors.update_chapter(r);await capture(hub+"_after")
		get_tree().paused=false;job.set_process(true);gate.set_process(true);job.hud.show()
	checks["visual_fixture"]=true

func ui_frames() -> void:
	# UI release gates count process frames, not physics catch-up ticks.
	for i in 6:await get_tree().process_frame

func chapter_edges() -> void:
	key(KEY_E);await ui_frames();job.open_story("ren_intro")
	checks.face_rejected_away_from_home=job.state=="DISPATCH"
	pointer(job.hud.accept_button,true);pointer(job.hud.accept_button,false);await ui_frames()
	checks.pointer_market_anonymous=job.state=="NARRATIVE" and not job.dialogue.portrait.visible
	press(KEY_ENTER);await ui_frames();job.accept_offer();press(KEY_ENTER,true,true)
	checks.final_advance_held_cannot_accept=job.summary and not job.acceptance_armed and job.attempt_id==0
	press(KEY_ENTER,false);await ui_frames();pointer(job.dialogue.decline_button,true);pointer(job.dialogue.decline_button,false);await ui_frames()
	checks.pointer_decline_no_accept=job.state=="FREE_ROAM" and job.attempt_id==0
	key(KEY_E);await ui_frames();pointer(job.hud.reward,true);pointer(job.hud.reward,false);await ui_frames()
	checks.reset_confirmation=job.hud.reset_dialog.visible
	key(KEY_ESCAPE);await ui_frames();checks.reset_cancel_preserves="market" in job.story_store.record.seen
	job.reset_experiment();key(KEY_ENTER);await ui_frames()
	joy(JOY_BUTTON_Y,true);await ui_frames();joy(JOY_BUTTON_B,true);joy(JOY_BUTTON_B,false)
	checks.gamepad_skip_never_accepts=job.summary and not job.acceptance_armed and job.attempt_id==0
	joy(JOY_BUTTON_Y,false);await ui_frames();joy(JOY_BUTTON_B,true);joy(JOY_BUTTON_B,false);await ui_frames()
	checks.gamepad_fresh_accept=job.state=="ACTIVE" and job.contract.id=="relay_mail"
	key(KEY_ESCAPE);key(KEY_R);await ui_frames()
	checks.clean_active_reset=job.state=="RESULTS" and not job.last_result.delivered and job.story_store.record.step==0 and job.story_store.record.parcel.is_empty()
	key(KEY_ENTER);await ui_frames()
	# Explicit synthetic late-state ticket fixture; no route or owner-play claim.
	job.story_store.record.step=7;job.story_store.record.patch=true;job.story_store.record.after_arc1=true;job.story_store.record.after_arc2=true;job.story_store.commit();job.story_store.load_state();job.update_anchors()
	await reset_at(job.hub_position("RLY"));key(KEY_E);key(KEY_ENTER);await ui_frames()
	checks.relay_ticket_text_only=job.state=="NARRATIVE" and job.conversation=="ticket" and not job.dialogue.portrait.visible
	key(KEY_X);await ui_frames();key(KEY_ENTER);await ui_frames()
	checks.ticket_never_loads_remote_parcel=job.state=="FREE_ROAM" and job.story_store.record.parcel.is_empty()
	await reset_at(job.hub_position("TES"));key(KEY_E);key(KEY_ENTER);await ui_frames()
	checks.tess_coda_local=job.state=="NARRATIVE" and job.conversation=="coda" and job.dialogue.portrait.visible and job.dialogue.caption.text.contains("—R.")
	key(KEY_X);await ui_frames();pointer(job.dialogue.accept_button,true);pointer(job.dialogue.accept_button,false);await ui_frames()
	checks.pointer_explicit_pickup=job.state=="ACTIVE" and job.contract.id=="tess_patches"
