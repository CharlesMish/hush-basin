extends RefCounted
## Review evidence only. No values from this record feed movement or cargo.
static func record(craft: CraftController, cargo: RefCounted, sample: Dictionary, before_units: int, prior_peak: int, episode_severity: float) -> Dictionary:
	var pre: Vector3 = craft.get("review_pre_move_velocity")
	var contacts: Array = []
	for i in craft.get_slide_collision_count():
		var hit := craft.get_slide_collision(i)
		var n := hit.get_normal()
		contacts.append({"source":String(hit.get_collider().get_meta("source_geometry_id","")),"normal":[n.x,n.y,n.z],"normal_closing_mps":maxf(0,-pre.dot(n))})
	var frame := Engine.get_physics_frames()
	var row := {"physics_frame":frame,"pre_impact_world_speed":pre.length(),"pre_impact_world_velocity":[pre.x,pre.y,pre.z],"pre_speed_source":"captured unchanged superclass pre_move_velocity argument","same_physics_frame":craft.get("review_impact_frame")==frame,"post_response_world_speed":craft.velocity.length(),"impact_closing_speed":craft.last_impact_closing_speed,"impact_severity":craft.last_impact_severity,"impact_in_drive":craft.last_impact_in_drive,"form":"DRIVE" if craft.last_impact_in_drive else "SPREAD","fold_amount":craft.fold_amount,"impact_counter":craft.impact_count,"cargo_episode":cargo.episodes,"episode_prior_peak_units":prior_peak,"episode_peak_units":cargo.get("_charged_peak"),"episode_peak_severity":episode_severity,"incremental_loss_units":before_units-cargo.condition_units,"requested_increment_units":sample.loss,"cumulative_loss_units":1000-cargo.condition_units,"condition_units":cargo.condition_units,"eligible":sample.get("eligible",false),"fresh":sample.get("fresh",false),"contacts":contacts}
	row["realized_world_speed"] = craft.get_real_velocity().length()
	var moved := craft.get_position_delta()
	row["position_delta"] = [moved.x,moved.y,moved.z]
	row["condition_before_units"] = before_units
	row["controller_episode_peak_severity"] = episode_severity
	var entry: Variant = cargo.get("entry_severity")
	if entry != null:
		row["episode_peak_severity"] = entry
		row["billing_policy"] = "contact-entry-only"
	else:
		row["billing_policy"] = "v1-rising-peak"
	return row
