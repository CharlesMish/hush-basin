extends "res://tests/courier_slice_probe.gd"
## Same real integration in native and Web. Fixture resets are explicitly named;
## the three delivery legs use only ordinary inputs after acceptance.
const Driver=preload("res://tests/mastery_driver.gd")
const Catalog=preload("res://scripts/courier/relay_contracts.gd")
const Precision=preload("res://scripts/courier/challenge_display.gd")
var route_id:=""
var routes: Array=[]
var phase:="full"
var save_path:="user://relay_probe_project_v01.json"
var neutral:=false
var review: Node

func capture(id: String) -> void:
	if capture_dir.is_empty() or DisplayServer.get_name()=="headless":return
	await get_tree().process_frame;await get_tree().process_frame
	RenderingServer.force_draw(false)
	get_viewport().get_texture().get_image().save_png(capture_dir.path_join(id+".png"))

func run() -> void:
	get_tree().set_meta("relay_test_save",save_path)
	get_tree().set_meta("relay_test_control",neutral)
	review=load("res://review/relay_consequence/relay_review.tscn").instantiate();add_child(review)
	await ticks(120)
	game=review.game;job=review.job;gate=job.gate;craft=job.craft
	checks["starts_at_market"]=job.state=="FREE_ROAM" and job.can_dispatch()
	checks["saved_mesh_state"]=job.annex.stage==(0 if neutral else job.project.stage())
	checks["default_trail_no_reward_gate"]=job.trail.trail_style=="standard" and job.session.balance==0
	if phase in ["reset","full"]:
		key(KEY_E);job.reset_experiment();key(KEY_ESCAPE);await ticks(8)
		checks["reset_fresh"]=job.project.stage()==0 and job.annex.stage==0
	if phase=="reset":finish();return
	if phase in ["inspect1","inspect2","inspect0"]:
		var expected:=int(phase.trim_prefix("inspect"))
		checks["reopened_expected_stage"]=job.project.stage()==expected
		checks["reopened_mesh_matches"]=job.annex.stage==(0 if neutral else expected)
		await reset_at(job.hub_position("WRK"));checks["works_pickup_gate"]=job.can_dispatch()==(expected>=1)
		await reset_at(job.hub_position("RLY"));checks["relay_dispatch_gate"]=job.can_dispatch()==(expected==2)
		await capture("reopened_"+phase);finish();return
	if phase in ["full","leg1"]:
		key(KEY_E);await ticks(3)
		checks["market_three_visible"]=job.hud.cards.size()==3 and job.hud.visible_indices.size()==3 and job.board_jobs.size()==6
		await capture("01_market_project_board")
		key(KEY_LEFT);checks["browse_wraps_full_pool"]=job.selected==5
		key(KEY_RIGHT);checks["browse_returns_project"]=job.selected==0
		Input.action_press("throttle");key(KEY_ENTER);await ticks(8)
		checks["accept_neutral_guard"]=job.state=="WAIT_NEUTRAL"
		Input.action_release("throttle");await ticks(8)
		key(KEY_ESCAPE);await get_tree().process_frame
		var clock: float=job.elapsed;var weather=gate.get_node("WarmOvercastWeather");var age: float=weather.active_time
		await ticks(10);checks["pause_clock_weather"]=job.elapsed==clock and weather.active_time==age
		key(KEY_ESCAPE);await ticks(8)
		route_id="WRK_way"
		var path: Array[Vector2]=[job.origin,job.destination]
		await driven(path,"stock_normal_input")
		checks["stock_specific_contribution"]=job.project.stage()==1 and job.project_receipt.changed
		await capture("02_stock_received")
		await continue_here()
		checks["continue_works_pickup"]=job.nearby_hub()=="WRK" and job.can_dispatch()
		if phase=="leg1":finish();return
	if phase in ["full","leg2"]:
		if phase=="leg2":await reset_at(job.hub_position("WRK")) # restart fixture; never writes during drive
		key(KEY_E);await ticks(3)
		checks["works_exact_receiver"]=job.board_hub=="WRK" and job.board_jobs.size()==1 and job.board_jobs[0].id=="relay_receiver"
		await capture("03_works_pickup")
		key(KEY_ENTER);await ticks(8)
		route_id="receiver_leg"
		await driven(Driver.road(gate,["-R0","-L4"]),"receiver_normal_input")
		checks["receiver_activates_dispatch"]=job.project.stage()==2 and job.project.outbound_available()
		checks["receiver_activates_mesh"]=job.annex.stage==(0 if neutral else 2)
		await capture("04_receiver_installed")
		await continue_here()
		checks["continue_relay_dispatch"]=job.nearby_hub()=="RLY" and job.can_dispatch()
		if phase=="leg2":finish();return
	if phase in ["full","outbound"]:
		if phase=="outbound":await reset_at(job.hub_position("RLY"))
		key(KEY_E);await ticks(3)
		checks["relay_outbound_available"]=job.board_hub=="RLY" and job.board_jobs.size()==1 and job.board_jobs[0].id=="relay_return"
		await capture("05_relay_dispatch")
		key(KEY_ENTER);await ticks(8);route_id="relay_outbound"
		await driven(Driver.road(gate,["L4","L5"]),"outbound_normal_input")
		await capture("06_return_received");await continue_here()
		checks["outbound_leaves_at_market"]=job.nearby_hub()=="MRK"
	if phase=="full":await adversarial()
	finish()

func driven(path: Array[Vector2],id: String) -> void:
	var r: Dictionary=await Driver.drive(self,path)
	routes.append({"id":id,"result":r})
	checks[id]=r.delivered and r.reset_delta==0
	print("RELAY_ROUTE ",id," ",r.delivered)

func continue_here() -> void:
	var pose:=craft.global_transform;var velocity:=craft.velocity;var balance: int=job.session.balance
	job._finish(true,"duplicate")
	checks["duplicate_%s" % route_id]=job.session.balance==balance
	key(KEY_R);checks["results_reset_%s" % route_id]=job.session.balance==balance and craft.global_transform==pose
	key(KEY_ENTER)
	checks["continue_exact_%s" % route_id]=craft.global_transform==pose and craft.velocity==velocity
	await ticks(8)

func adversarial() -> void:
	for index in 6:
		await reset_at(job.origin);key(KEY_E);job.select_contract(index);key(KEY_ENTER);await ticks(8)
		job.cargo.condition_units=0;job.elapsed=3600
		var before: int=job.session.balance
		place_without_reset(job.destination);await ticks(90)
		checks["zero_base_%d" % index]=job.last_result.get("delivered",false) and job.last_result.condition_units==0 and not job.last_result.objective_met and job.last_result.total_credits==job.contract.base and job.session.balance==before+int(job.contract.base)
		if index==0:checks["completed_project_replay_no_advance"]=not job.project_receipt.changed and job.project.stage()==2
		if index==1:checks["basic_has_no_mastery"]=job.last_result.objective=="NONE" and not job.session.mastery.status("freight_seals").mastered
		key(KEY_ENTER);await ticks(8)
	# Explicit zero-condition receiver replay still valid; it cannot install twice.
	await reset_at(job.hub_position("WRK"));key(KEY_E);key(KEY_ENTER);await ticks(8)
	job.cargo.condition_units=0;place_without_reset(job.destination);await ticks(90)
	checks["zero_receiver_delivers_without_destroyed_fiction"]=job.last_result.get("delivered",false) and not job.project_receipt.changed
	key(KEY_ENTER);await ticks(8)
	await reset_at(job.origin);key(KEY_E);var balance: int=job.session.balance;key(KEY_C)
	checks["liner_purchase_unchanged"]=job.session.liner_owned and job.session.balance==balance-400
	key(KEY_ENTER);await ticks(8);key(KEY_ESCAPE);balance=job.session.balance;key(KEY_R)
	checks["paused_retry_no_project_or_credit"]=job.state=="RESULTS" and not job.last_result.delivered and job.project.stage()==2 and job.session.balance==balance
	key(KEY_ENTER);await ticks(8)
	checks["weather_reset_viable"]=gate.get_node("WarmOvercastWeather").rain.emitting
	checks["maximum_precision_not_false_success"]=Precision.maximum_time(10.001)=="10.01" and Precision.maximum_time(10.0)=="10.00"
	checks["minimum_precision_not_false_success"]=Precision.minimum_duration(3.499)=="3.49"
	checks["mastery_only_four_authored"]=not job.session.mastery.reward_unlocked()
	key(KEY_F3)

func finish() -> void:
	var good:=true
	for value in checks.values():good=good and value
	var result:={"status":"PASS" if good else "FAIL","phase":phase,"neutral":neutral,"project":job.project.snapshot(),"checks":checks,"routes":routes,"pid":OS.get_process_id()}
	print("RELAY_SMOKE_RESULT "+JSON.stringify(result));finished.emit(result)
