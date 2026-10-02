extends "res://tests/chapter_probe.gd"
## Explicit synthetic leg fixtures; approach lane uses ordinary vehicle input.
func run() -> void:
	get_tree().set_meta("chapter_test_save",save_path);get_tree().set_meta("relay_test_save",save_path+".legacy")
	review=load("res://review/opening_chapter/review.tscn").instantiate();add_child(review);await ticks(120)
	game=review.game;job=review.job;gate=job.gate;craft=job.craft
	if phase=="approaches":await approaches();finish();return
	await stage(4,Vector2(40,60));craft.rotation.y=PI;gate.camera_rig.snap_to_target();await ticks(90)
	checks.comfortable_roadside_stop=job.can_dispatch() and job.nearby_hub()=="TES"
	checks.marker_targets_stop=job.cue._destination_xz==job.hub_position("TES")
	await capture("tess_contact")
	var ground_ok:=true
	for z in [58,61,67,73,76]:
		for x in [31,35,40,45,49]:
			var query:=PhysicsRayQueryParameters3D.create(Vector3(x,20,z),Vector3(x,-5,z));query.exclude=[craft.get_rid()]
			var hit: Dictionary=craft.get_world_3d().direct_space_state.intersect_ray(query)
			ground_ok=ground_ok and not hit.is_empty() and absf(hit.position.y-gate.data.terrain_height_at(x,z))<.2
	checks.proposed_stop_is_clear_ground=ground_ok
	for step in 8:
		var id: String=Chapter.ORDER[step];var hub: String=Chapter.ORIGINS[id]
		await stage(step,job.hub_position(hub));key(KEY_E);await ui_frames()
		var from_to: String=Chapter.PLACES[hub]+" → "+Chapter.PLACES[Chapter.job(id).destination]
		checks[id+"_card_pickup"]=job.hud.objective_detail.text.contains("Pickup: "+from_to)
		key(KEY_ENTER);await ui_frames();key(KEY_X);await ui_frames()
		checks[id+"_summary_pickup"]=job.dialogue.speech.text.contains("Pickup: "+from_to)
		key(KEY_ENTER);await ui_frames()
		checks[id+"_accepted_origin"]=job.origin==job.hub_position(hub) and job.contract.get("origin","")==hub
		checks[id+"_hud_origin"]=job.hud.purpose_text.text.contains(from_to)
		if id=="relay_receiver":checks.receiver_hud_has_only_current_cargo=not job.hud.purpose_text.text.contains("Receiver kit") and job.hud.purpose_text.text.contains("Restores Relay dispatch")
		checks[id+"_destination_marker"]=job.cue._destination_xz==job.destination and job.cue._destination_label=="To "+String(job.contract.destination)
		var expected: Array[String]=[]
		for route in job.contract.routes:expected.append(String(route).trim_prefix("-"))
		checks[id+"_active_advisory"]=gate.map.highlighted_route_ids==expected
		if id=="tess_repairs":checks.no_clinic_market_detour=expected.is_empty()
		if id in ["tess_jackets","tess_patches"]:checks[id+"_no_false_clinic_origin"]=not "L2" in expected
		# Opening the retained diagnostic route menu must not replace delivery guidance.
		gate._change_selection(1);await ui_frames()
		checks[id+"_no_diagnostic_route_leak"]=gate.map.highlighted_route_ids==expected
		if id in ["relay_receiver","tess_aprons","tess_repairs"]:await capture(id+"_active")
		job._finish(false,"UX fixture cancel");await ui_frames()
		checks[id+"_no_stale_route_after_cancel"]=gate.map.highlighted_route_ids.is_empty()
		key(KEY_ENTER);await ui_frames()
	await stage(7,job.hub_position("RLY"));key(KEY_E);await ui_frames()
	checks.remote_ticket_names_tess_pickup=job.hud.objective_detail.text.contains("Pickup: South counter → Quarry Stores")
	finish()

func stage(step: int,at: Vector2) -> void:
	job.state="FREE_ROAM";job.dialogue.hide();get_tree().paused=false
	job.story_store.record=job.story_store.fresh_record();job.story_store.record.step=step
	job.story_store.record.patch=step>=7;job.story_store.record.after_arc1=step>=5;job.story_store.record.after_arc2=step>=7
	job.story_store.commit();job.story_store.load_state();job.update_anchors()
	await reset_at(at);await ui_frames()

func approaches() -> void:
	for hub in ["MRK","CLN","DEP"]:
		await stage(4,job.hub_position(hub))
		var path: Array[Vector2]=line(job._xz(),Vector2(40,64))
		if hub=="DEP":path=Driver.road(gate,["L1"])+line(job.hub_position("MRK"),Vector2(40,64))
		var impacts: int=craft.impact_count
		var result: Dictionary=await preload("res://tests/chapter_driver.gd").drive(self,path,true,true)
		routes.append({"id":hub+"_to_Tess","result":result})
		checks[hub+"_comfortable_arrival"]=result.arrived_home and result.reset_delta==0 and job.can_dispatch()
		checks[hub+"_no_scrape"]=craft.impact_count==impacts
		checks[hub+"_clear_of_frontage"]=craft.global_position.z<72
		key(KEY_E);await ui_frames();key(KEY_ENTER);await ui_frames()
		checks[hub+"_actual_tess_interaction"]=job.state=="NARRATIVE" and job.conversation=="tess_intro"
		await capture(hub+"_approach")
