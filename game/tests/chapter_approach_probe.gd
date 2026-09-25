extends "res://tests/narrative_probe.gd"
func run() -> void:
	get_tree().set_meta("narrative_test_save",save_path);get_tree().set_meta("relay_test_save",save_path+".legacy")
	review=load("res://review/narrative_presence/review.tscn").instantiate();add_child(review);await ticks(120)
	game=review.game;job=review.job;gate=job.gate;craft=job.craft
	for hub in ["MRK","CLN"]:
		await reset_at(job.hub_position(hub))
		# Test-only destination overrides; existing geometry and controls unchanged.
		job.refresh_pool("MRK");job.selected=1;job.state="DISPATCH";job.primary_action();await ticks(8)
		job.destination=Vector2(40,77);job.destination_radius=4
		var path: Array[Vector2]=[job.hub_position(hub),Vector2(40,77)]
		route_id="site_"+hub;await driven(path,route_id)
		await capture(route_id)
		if job.state=="RESULTS":key(KEY_ENTER);await ticks(8)
	finish()
