extends "res://tests/chapter_probe.gd"
const Slice=preload("res://scripts/courier/slices_text.gd")
var opening_run:=false
var third_after_second:=false
var third_started:=false
func run() -> void:
	review_scene_path="res://review/narrative_slices/review.tscn"
	if phase=="complete":third_after_second=true;opening_run=true;phase="guards";await super.run();return
	if phase=="contiguous":opening_run=true;phase="guards";await super.run();return
	get_tree().set_meta("chapter_test_save",save_path);get_tree().set_meta("relay_test_save",save_path+".legacy")
	review=load(review_scene_path).instantiate();add_child(review);await ticks(120)
	game=review.game;job=review.job;gate=job.gate;craft=job.craft
	checks.initialized=job.story_store!=null and job.anchors!=null
	if phase.begins_with("resume_"):
		checks.restored_without_error=job.project_error.is_empty()
		var sentence: String=job.resume_sentence()
		var names_place:=false
		for place in Chapter.PLACES.values()+["B11","Tess"]:names_place=names_place or sentence.contains(String(place))
		checks.resume_concrete=sentence.length()>20 and not sentence.contains("%") and names_place
		checks.physical_state_restored=job.anchors.clinic_new.visible==job.story_store.record.slices.installed and job.anchors.quarry_bedded.visible==job.story_store.record.slices.bedded
		var s: Dictionary=job.story_store.record.slices
		checks.shelf_restored=job.anchors.mending_label.visible==s.shelf_label
		checks.red_card_restored=job.anchors.red_word.visible==("relined_sleeve" in s.done)
		checks.partial_threads_preserved=Slice.chapter_three_complete(job.story_store.record)==("relined_sleeve" in s.done and "bea_red" in job.story_store.record.seen and "ren_letter" in s.done)
		if phase.contains("held"):checks.held_exact="quarry_sleeve" in s.done and not "kneeling_pads" in s.done and job.anchors.held_sleeve.visible
		if phase.contains("ready"):checks.ready_exact=s.relined and "relined_sleeve" in Slice.available(job.story_store.record)
		if phase.contains("sleeve_only"):checks.sleeve_only_exact="relined_sleeve" in s.done and not "ren_letter" in s.done and not Slice.chapter_three_complete(job.story_store.record)
		if phase.contains("ren_only"):checks.ren_only_exact="ren_letter" in s.done and not "relined_sleeve" in s.done and not Slice.chapter_three_complete(job.story_store.record)
		if phase.contains("both"):checks.both_exact=Slice.chapter_three_complete(job.story_store.record)
		if not job.story_store.record.parcel.is_empty():checks.parcel_restored=job.state=="ACTIVE" and job.contract.id==job.story_store.record.parcel
		if not job.story_store.record.pending.is_empty():checks.pending_local=job.state=="NARRATIVE" and job.nearby_hub()==Slice.SCENES[job.conversation].home
		finish();return
	# Explicit late-opening fixture for bounded slice tests. Contiguous mode does not use it.
	job.story_store.record=job.story_store.fresh_record();job.story_store.record.step=8;job.story_store.record.patch=true;job.story_store.record.after_arc1=true;job.story_store.record.after_arc2=true
	job.story_store.commit();job.story_store.load_state();job.update_anchors()
	if phase=="approaches":
		job.story_store.record.slices.done=["new_threshold","nell_first_tray","clinic_release","old_threshold","quarry_later","tray_one","quarry_sleeve","tray_two","ren_answer","thread_box","kneeling_pads","relined_sleeve","tagged_mending","ren_letter"]
		for flag in ["installed","bedded","relined","shelf_label"]:job.story_store.record.slices[flag]=true
		job.story_store.record.seen=["bea_first","nell_first","bea_old","bea_red","ren_answer","ren_letter"]
		checks.approach_fixture_saved=job.story_store.commit();job.update_anchors();await b11_approaches();finish();return
	if phase in ["sleeve_first","ren_first","interleaved","drive_three"]:
		job.story_store.record.slices.done=["new_threshold","nell_first_tray","clinic_release","old_threshold","quarry_later"]
		job.story_store.record.slices.installed=true;job.story_store.record.slices.bedded=true
		job.story_store.record.seen=["bea_first","nell_first","bea_old"]
		checks.chapter_three_fixture_saved=job.story_store.commit();job.update_anchors();third_started=true;await chapter_three();return
	await chapter_two()
func finish() -> void:
	if opening_run:opening_run=false;phase="contiguous";call_deferred("chapter_two");return
	if third_after_second and not third_started:third_started=true;phase="complete";call_deferred("chapter_three");return
	super.finish()
func chapter_two() -> void:
	checks.opening_complete=job.story_store.record.step==8
	await leave_story();await view_at("CLN");await capture("clinic_old")
	await take("new_threshold")
	checks.release_slip_aboard=job.contract.docket==Slice.RELEASE
	checks.pallet_bare_after_load=not job.anchors.new_stone.visible and job.anchors.folded_tarp.visible
	await deliver("new_threshold")
	checks.stone_paid=job.last_result.delivered and job.last_result.total_credits==140
	checks.clinic_receipt_exact=job.last_result.reaction==Slice.CLINIC_RECEIPT
	checks.no_visible_install=not job.story_store.record.slices.installed and job.anchors.clinic_pad.visible and job.anchors.clinic_old.visible
	snapshot("ch2_delivered");await capture("clinic_new_on_pad")
	await leave_story();await take("nell_first_tray")
	checks.installed_while_away=job.story_store.record.slices.installed
	await deliver("nell_first_tray")
	checks.nell_local_paid_first=job.state=="NARRATIVE" and job.conversation=="nell_first" and job.last_result.total_credits==100 and job.nearby_hub()=="MRK"
	await capture("nell_first");await leave_story()
	checks.return_crate_persists=job.anchors.market_crate.visible
	await take_ordinary("MRK","clinic_thread")
	await deliver("clinic_thread")
	checks.ordinary_receipt_retained=job.last_result.reaction.begins_with("Kit received. The south desk stays open.")
	checks.release_appended=job.last_result.reaction.ends_with(Slice.CLINIC_RELEASE)
	checks.old_job_posted="old_threshold" in Slice.available(job.story_store.record)
	snapshot("ch2_released");await capture("clinic_installed_receipt")
	await leave_story();await view_at("CLN");await capture("clinic_installed")
	await take("old_threshold")
	checks.old_collected_at_wall=job.origin==job.hub_position("CLN") and not job.anchors.clinic_released.visible
	await deliver("old_threshold")
	checks.old_paid_no_pristine=job.last_result.total_credits==140
	checks.no_fabricated_chip=Slice.SCENES.bea_old.lines.size()==2
	checks.bea_return_local=job.conversation=="bea_old" and job.nearby_hub()=="QRY"
	await capture("bea_old");await leave_story();snapshot("ch2_old_returned")
	checks.old_waits_for_departure=not job.story_store.record.slices.bedded and job.anchors.quarry_blocks.visible
	await take_ordinary("MRK","quarry_haul")
	checks.bedded_while_away=job.story_store.record.slices.bedded
	await deliver("quarry_haul")
	checks.ordinary_quarry_receipt_retained=job.last_result.reaction=="The shelf crew can start its round."
	checks.chapter_two_complete=Slice.chapter_two_complete(job.story_store.record)
	await leave_story();await view_at("QRY");await capture("quarry_reused_normal")
	checks.reuse_physical=job.anchors.quarry_bedded.visible and job.anchors.barrow.visible and not job.anchors.rut.visible
	snapshot("ch2_complete")
	finish()
func take(id: String) -> void:
	await leave_story();await view_at(Slice.JOBS[id].origin)
	key(KEY_E);await ui_frames()
	var index:=-1
	for i in job.board_jobs.size():
		if job.board_jobs[i].id==id:index=i
	checks[id+"_available"]=index>=0
	if index<0:return
	job.select_contract(index);key(KEY_ENTER);await ui_frames()
	checks[id+"_local"]=job.conversation==Slice.JOBS[id].pickup and job.nearby_hub()==Slice.JOBS[id].origin
	if id=="new_threshold":await capture("bea_pickup")
	var before: int=job.attempt_id
	if id in ["quarry_sleeve","relined_sleeve","thread_box"]:
		while job.panel_index+1<Slice.SCENES[job.conversation].lines.size():key(KEY_ENTER);await ui_frames()
		press(KEY_ENTER);await ui_frames();job.accept_offer();press(KEY_ENTER,true,true)
		checks[id+"_last_advance_no_accept"]=job.summary and not job.acceptance_armed and job.attempt_id==before
		press(KEY_ENTER,false);await ui_frames()
	else:
		press(KEY_X);await ui_frames();job.accept_offer()
		checks[id+"_skip_never_accepts"]=job.summary and job.attempt_id==before
		press(KEY_X,false);await ui_frames()
	checks[id+"_summary_pickup"]=job.dialogue.speech.text.contains(Chapter.pickup_label(Slice.job(id)))
	var done_before: Array=job.story_store.record.slices.done.duplicate()
	key(KEY_ESCAPE);await ui_frames()
	checks[id+"_decline_preserves"]=job.story_store.record.slices.done==done_before and job.story_store.record.parcel.is_empty()
	key(KEY_E);await ui_frames();job.select_contract(index);key(KEY_ENTER);await ui_frames()
	checks[id+"_repeat_summary"]=job.summary
	key(KEY_ENTER);await ui_frames()
	checks[id+"_explicit_accept"]=job.state=="ACTIVE" and job.contract.id==id and job.origin==job.hub_position(Slice.JOBS[id].origin)
	checks[id+"_hud_origin"]=job.hud.purpose_text.text.contains(Chapter.pickup_label(Slice.job(id)))
	checks[id+"_marker"]=job.cue._destination_xz==job.destination and job.cue._destination_label=="To "+Slice.JOBS[id].destination
	if id in Slice.CHAPTER_THREE_JOBS:snapshot("aboard_"+id)
func take_ordinary(hub: String,id: String) -> void:
	await leave_story();await view_at(hub);key(KEY_E);await ui_frames()
	for i in job.board_jobs.size():
		if job.board_jobs[i].id==id:job.select_contract(i);break
	key(KEY_ENTER);await ui_frames();checks[id+"_ordinary_available"]=job.state=="ACTIVE" and job.contract.id==id
func deliver(id: String) -> void:
	if phase in ["drive","drive_three"]:
		var path: Array[Vector2]=Driver.road(gate,job.contract.routes)
		if id in ["quarry_sleeve","kneeling_pads","thread_box","tagged_mending"]:path+=line(job.hub_position("MRK"),job.hub_position("TES"))
		if id=="relined_sleeve":path=line(job.hub_position("TES"),job.hub_position("MRK"))+path
		if id=="relay_window":path=Driver.road(gate,["-L5","-L4"])
		if id=="clinic_thread":path=Driver.road(gate,["L2"])
		if id=="quarry_haul":path=Driver.road(gate,["-L1","-L0","-A0"])
		if path.is_empty():path=line(job._xz(),job.destination)
		var result: Dictionary=await Driver.drive(self,path,true,false);routes.append({"id":id,"result":result});checks[id+"_drive_no_reset"]=result.reset_delta==0 and job.last_result.get("delivered",false)
	else:
		if id in Slice.CHAPTER_THREE_JOBS:job.cargo.condition_units=0;job.elapsed=3600
		place_without_reset(job.destination);await ticks(100)
	await ui_frames();checks[id+"_settled"]=job.last_result.get("delivered",false)
func view_at(hub: String) -> void:
	await reset_at(job.hub_position(hub))
	craft.rotation.y=PI/2 if hub=="QRY" else atan2(-8.0,-6.0) if hub=="CLN" else atan2(-6.0,7.0) if hub=="MRK" else PI if hub=="TES" else 0.0
	gate.camera_rig.snap_to_target();await ticks(10)
func snapshot(suffix: String) -> void:
	job.save_checkpoint();DirAccess.copy_absolute(save_path,save_path+"."+suffix)

func chapter_three() -> void:
	checks.seven_counted_legs=Slice.CHAPTER_THREE_JOBS.size()==7
	checks.no_prop_colliders=job.anchors.find_children("*","CollisionObject3D",true,false).is_empty()
	checks.tess_stop_preserved=job.hub_position("TES")==Vector2(40,67) and gate.data.manifest.destination_pads.TES.inner_flat_radius_m==9
	checks.two_start_jobs=Slice.available(job.story_store.record).has("tray_one") and Slice.available(job.story_store.record).has("quarry_sleeve")
	await leave_story();await view_at("QRY");await capture("initial_sleeve_normal")
	if phase=="ren_first":
		await ren_start();await ren_arrival("ren_answer");await thread_delivery();await mending_delivery();await ren_arrival("ren_letter")
		snapshot("ren_only");checks.ren_alone_not_complete=not Slice.chapter_three_complete(job.story_store.record)
		checks.sleeve_still_available="quarry_sleeve" in Slice.available(job.story_store.record)
		await sleeve_start();await pads_delivery();await sleeve_return()
	elif phase=="sleeve_first":
		await sleeve_start();await pads_delivery();await sleeve_return()
		snapshot("sleeve_only");checks.sleeve_alone_not_complete=not Slice.chapter_three_complete(job.story_store.record)
		checks.trays_still_available="tray_one" in Slice.available(job.story_store.record)
		await ren_start();await ren_arrival("ren_answer");await thread_delivery();await mending_delivery();await ren_arrival("ren_letter")
	else:
		await take("tray_one");await deliver("tray_one");checks.tray_one_no_portrait=job.state=="RESULTS";await leave_story()
		await sleeve_start()
		await tray_two();await ren_arrival("ren_answer");await thread_delivery();await pads_delivery();await sleeve_return()
		snapshot("sleeve_only");checks.sleeve_alone_not_complete=not Slice.chapter_three_complete(job.story_store.record)
		await mending_delivery();await ren_arrival("ren_letter")
	checks.both_threads_complete=Slice.chapter_three_complete(job.story_store.record)
	checks.no_eighth_story_leg=Slice.available(job.story_store.record).is_empty()
	await view_at("QRY");await capture("corrected_card_normal")
	await view_at("TES");await capture("b11_shelf_normal")
	await view_at("RLY");await capture("relay_letter_normal")
	snapshot("both")
	var paid: int=job.session.balance;var attempts: int=job.attempt_id
	key(KEY_E);await ui_frames();job.review_local();await ui_frames();key(KEY_X);await ui_frames()
	checks.review_no_pay=job.session.balance==paid and job.attempt_id==attempts
	await leave_story();await take_ordinary("MRK","quarry_haul");await deliver("quarry_haul");await leave_story()
	key(KEY_E);await ui_frames();checks.optional_bea_available=job.return_id()=="bea_red_return"
	job.return_local();await ui_frames();checks.optional_bea_local=job.state=="NARRATIVE" and job.nearby_hub()=="QRY"
	await leave_story();key(KEY_E);await ui_frames();checks.optional_once=job.return_id()!="bea_red_return"
	await leave_story();await view_at("MRK");key(KEY_E);await ui_frames();job.reset_experiment();await ui_frames()
	checks.reset_all_story=job.story_store.record==job.story_store.fresh_record() and not job.anchors.red_word.visible and not job.anchors.mending_label.visible and not job.anchors.quarry_bedded.visible
	finish()
func scene_check(id: String) -> void:
	checks[id+"_local_paid"]=job.conversation==id and job.nearby_hub()==Slice.SCENES[id].home and job.last_result.get("delivered",false) and job.story_store.record.parcel.is_empty()
	if Slice.SCENES[id].get("paper_panels",0)>0:
		checks[id+"_paper_no_remote_face"]=not job.dialogue.portrait.visible and job.dialogue.speech.text==Slice.SCENES[id].lines[0]
		await capture(id+"_note");key(KEY_ENTER);await ui_frames()
	checks[id+"_face_here"]=job.dialogue.portrait.visible and job.nearby_hub()==Slice.SCENES[id].home
	await capture(id)
	var paid: int=job.session.balance;var attempts: int=job.attempt_id
	key(KEY_X);await ui_frames()
	checks[id+"_skip_settled"]=job.summary and job.story_store.record.parcel.is_empty() and job.session.balance==paid and job.attempt_id==attempts
	checks[id+"_reply_present"]=job.dialogue.speech.text.contains(Slice.summary(id))
	await capture(id+"_receipt");await leave_story()
func sleeve_start() -> void:
	await take("quarry_sleeve");await deliver("quarry_sleeve")
	checks.sleeve_attributed_reply=job.last_result.reaction==Slice.SLEEVE_REPLY
	await scene_check("tess_sleeve")
	checks.sleeve_reply_posts_pads="kneeling_pads" in Slice.available(job.story_store.record) and job.anchors.held_sleeve.visible
	snapshot("held");await view_at("TES");await capture("sleeve_held_normal")
func pads_delivery() -> void:
	await take("kneeling_pads");await deliver("kneeling_pads");await scene_check("tess_reline")
	checks.reline_waits_for_departure=not job.story_store.record.slices.relined
	snapshot("pads_answer")
	await view_at("MRK");checks.relined_while_away=job.story_store.record.slices.relined
	snapshot("ready");await view_at("TES");await capture("red_lining_normal")
func sleeve_return() -> void:
	await take("relined_sleeve");checks.tag_carried=job.contract.docket==Slice.RELINED_TAG
	await deliver("relined_sleeve");await scene_check("bea_red")
	checks.corrected_card_and_red=job.anchors.red_word.visible and job.anchors.strike.visible and job.anchors.never_line.visible and job.anchors.sleeve_red.visible
func ren_start() -> void:
	await take("tray_one");await deliver("tray_one")
	checks.tray_one_no_portrait=job.state=="RESULTS" and job.anchors.busy_orders.visible and job.anchors.corner_saucer.visible
	await capture("market_busy_normal");await leave_story();await tray_two()
func tray_two() -> void:
	await take("tray_two")
	checks.tray_only_objective=job.contract.name=="Meal tray" and not job.contract.purpose.contains("meal") and job.contract.objective=="NONE"
	await deliver("tray_two");checks.nell_attributed_reply=job.last_result.reaction==Slice.NELL_REPLY
	await scene_check("nell_interruption");checks.nell_reply_posts_ren=Slice.arrival_scene(job.story_store.record,"RLY")=="ren_answer"
	await view_at("MRK");await capture("nell_hatch_normal")
func ren_arrival(id: String) -> void:
	await take_ordinary("MRK","relay_window");await deliver("relay_window")
	checks[id+"_ordinary_host"]=job.last_result.reaction=="The mast crew has what it needs." and job.story_store.record.pending==id
	await scene_check(id)
	checks[id+"_cargo_neutral"]=job.story_store.record.parcel.is_empty() and id in job.story_store.record.slices.done
	checks[id+"_no_replay"]=Slice.arrival_scene(job.story_store.record,"RLY").is_empty()
func thread_delivery() -> void:
	await take("thread_box");await deliver("thread_box")
	checks.boundary_reply_exact=job.last_result.reaction==Slice.THREAD_REPLY
	await scene_check("tess_boundary")
	checks.boundary_reply_posts_mending="tagged_mending" in Slice.available(job.story_store.record)
func mending_delivery() -> void:
	await take("tagged_mending");await deliver("tagged_mending")
	checks.mending_no_portrait=job.state=="RESULTS" and job.last_result.reaction=="On the shelf, thanks. —T"
	checks.mending_on_labelled_shelf=job.anchors.routed_parcel.visible and job.anchors.mending_label.visible
	await leave_story()
func b11_approaches() -> void:
	checks.no_added_collision=job.anchors.find_children("*","CollisionObject3D",true,false).is_empty()
	var ground_ok:=true
	for z in [58,61,67,73,76]:
		for x in [31,35,40,45,49]:
			var query:=PhysicsRayQueryParameters3D.create(Vector3(x,20,z),Vector3(x,-5,z));query.exclude=[craft.get_rid()]
			var hit: Dictionary=craft.get_world_3d().direct_space_state.intersect_ray(query)
			ground_ok=ground_ok and not hit.is_empty() and absf(hit.position.y-gate.data.terrain_height_at(x,z))<.2
	checks.stop_ground_clear=ground_ok
	for hub in ["MRK","CLN","DEP"]:
		await leave_story();await view_at(hub)
		var path: Array[Vector2]=line(job._xz(),Vector2(40,64))
		if hub=="DEP":path=Driver.road(gate,["L1"])+line(job.hub_position("MRK"),Vector2(40,64))
		var impacts: int=craft.impact_count
		var result: Dictionary=await preload("res://tests/chapter_driver.gd").drive(self,path,true,true);routes.append({"id":hub+"_Tess","result":result})
		checks[hub+"_comfort"]=result.arrived_home and result.reset_delta==0 and job.can_dispatch() and job.nearby_hub()=="TES"
		checks[hub+"_no_scrape"]=craft.impact_count==impacts
		checks[hub+"_road_facing"]=craft.global_position.z<72
		checks[hub+"_stop_marker"]=job.cue._destination_xz==Vector2(40,67)
		await capture(hub+"_approach");key(KEY_E);await ui_frames()
		checks[hub+"_usable_counter"]=job.state=="DISPATCH" and job.board_hub=="TES"
	await leave_story();await view_at("TES");await capture("b11_shelf_final_normal")
