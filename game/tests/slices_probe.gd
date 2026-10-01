extends "res://tests/chapter_probe.gd"
const Slice=preload("res://scripts/courier/slices_text.gd")
var opening_run:=false
func run() -> void:
	review_scene_path="res://review/narrative_slices/review.tscn"
	if phase=="contiguous":opening_run=true;phase="guards";await super.run();return
	get_tree().set_meta("chapter_test_save",save_path);get_tree().set_meta("relay_test_save",save_path+".legacy")
	review=load(review_scene_path).instantiate();add_child(review);await ticks(120)
	game=review.game;job=review.job;gate=job.gate;craft=job.craft
	checks.initialized=job.story_store!=null and job.anchors!=null
	if phase.begins_with("resume_"):
		checks.restored_without_error=job.project_error.is_empty()
		checks.resume_concrete=job.resume_sentence().length()>35 and not job.resume_sentence().contains("%")
		checks.physical_state_restored=job.anchors.clinic_new.visible==job.story_store.record.slices.installed and job.anchors.quarry_bedded.visible==job.story_store.record.slices.bedded
		if not job.story_store.record.parcel.is_empty():checks.parcel_restored=job.state=="ACTIVE" and job.contract.id==job.story_store.record.parcel
		if not job.story_store.record.pending.is_empty():checks.pending_local=job.state=="NARRATIVE" and job.nearby_hub()==Slice.SCENES[job.conversation].home
		finish();return
	# Explicit late-opening fixture for bounded slice tests. Contiguous mode does not use it.
	job.story_store.record=job.story_store.fresh_record();job.story_store.record.step=8;job.story_store.record.patch=true;job.story_store.record.after_arc1=true;job.story_store.record.after_arc2=true
	job.story_store.commit();job.story_store.load_state();job.update_anchors()
	await chapter_two()
func finish() -> void:
	if opening_run:opening_run=false;phase="contiguous";call_deferred("chapter_two");return
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
	press(KEY_X);await ui_frames();job.accept_offer()
	checks[id+"_skip_never_accepts"]=job.summary and job.attempt_id==before
	press(KEY_X,false);await ui_frames()
	checks[id+"_summary_pickup"]=job.dialogue.speech.text.contains(Chapter.pickup_label(Slice.job(id)))
	key(KEY_ENTER);await ui_frames()
	checks[id+"_explicit_accept"]=job.state=="ACTIVE" and job.contract.id==id and job.origin==job.hub_position(Slice.JOBS[id].origin)
func take_ordinary(hub: String,id: String) -> void:
	await leave_story();await view_at(hub);key(KEY_E);await ui_frames()
	for i in job.board_jobs.size():
		if job.board_jobs[i].id==id:job.select_contract(i);break
	key(KEY_ENTER);await ui_frames();checks[id+"_ordinary_available"]=job.state=="ACTIVE" and job.contract.id==id
func deliver(id: String) -> void:
	if phase=="drive":
		var path: Array[Vector2]=Driver.road(gate,job.contract.routes)
		if id=="clinic_thread":path=Driver.road(gate,["L2"])
		if id=="quarry_haul":path=Driver.road(gate,["-L1","-L0","-A0"])
		if path.is_empty():path=line(job._xz(),job.destination)
		var result: Dictionary=await Driver.drive(self,path,true,false);routes.append({"id":id,"result":result});checks[id+"_drive_no_reset"]=result.reset_delta==0 and job.last_result.get("delivered",false)
	else:
		place_without_reset(job.destination);await ticks(100)
	await ui_frames();checks[id+"_settled"]=job.last_result.get("delivered",false)
func view_at(hub: String) -> void:
	await reset_at(job.hub_position(hub))
	craft.rotation.y=PI/2 if hub=="QRY" else atan2(-8.0,-6.0) if hub=="CLN" else atan2(-6.0,7.0) if hub=="MRK" else PI if hub=="TES" else 0.0
	gate.camera_rig.snap_to_target();await ticks(10)
func snapshot(suffix: String) -> void:
	job.save_checkpoint();DirAccess.copy_absolute(save_path,save_path+"."+suffix)
