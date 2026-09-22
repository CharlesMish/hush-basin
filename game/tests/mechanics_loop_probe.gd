extends "res://tests/courier_slice_probe.gd"
const Catalog=preload("res://scripts/courier/alpha_contracts.gd")
const Ledger=preload("res://scripts/courier/alpha_session.gd")
const AlphaCargo=preload("res://scripts/courier/alpha_cargo.gd")
const Driver=preload("res://tests/mechanics_input_driver.gd")
var route_id:=""
var routes: Array=[]
var review: Node
func capture(id: String) -> void:
	if capture_dir.is_empty() or DisplayServer.get_name()=="headless":return
	await get_tree().process_frame
	await get_tree().process_frame
	RenderingServer.force_draw(false)
	get_viewport().get_texture().get_image().save_png(capture_dir.path_join(id+".png"))
func fresh(index: int) -> void:
	if job.state=="RESULTS":key(KEY_ENTER);await ticks(8)
	if job.state=="ACTIVE":job._finish(false,"Diagnostic cancel");key(KEY_ENTER);await ticks(8)
	await reset_at(job.origin)
	key(KEY_E)
	key(KEY_1+index)
	key(KEY_ENTER)
	await ticks(8)
func evidence(met: bool) -> Dictionary:
	return {"delivered":true,"condition_units":1000 if met else 0,"elapsed":10.0 if met else 3600.0,"longest_streak":12.0 if met else 0.0,"slip_brrr":300.0 if met else 0.0,"brrr":999999.0,"episodes":100}
func unit_checks() -> void:
	var ledger:=Ledger.new()
	for i in 3:
		for met in [false,true]:
			var c:=Catalog.job(i)
			var id:=ledger.accept(c)
			var before:=ledger.balance
			var r:=ledger.settle(id,evidence(met))
			checks["receipt_%d_%s_exact" % [i,met]]=r.total_credits==int(c.base)+(int(c.bonus) if met else 0) and r.objective_met==met and r.is_read_only()
			ledger.settle(id,evidence(not met))
			checks["receipt_%d_%s_idempotent" % [i,met]]=ledger.balance==before+r.total_credits
	checks["unknown_receipt_cannot_pay"]=ledger.settle(999,evidence(true)).is_empty()
	var failed:=evidence(true);failed.delivered=false
	var failed_id:=ledger.accept(Catalog.job(0));var before:=ledger.balance
	checks["cancellation_zero"]=ledger.settle(failed_id,failed).total_credits==0 and ledger.balance==before
	var fresh_ledger:=Ledger.new()
	checks["new_session_empty"]=fresh_ledger.balance==0 and not fresh_ledger.liner_owned
	checks["no_credit_purchase"]=not fresh_ledger.buy_liner()
	for i in 5:fresh_ledger.settle(fresh_ledger.accept(Catalog.job(0)),evidence(false))
	checks["five_depot_base_deliveries_afford_liner"]=fresh_ledger.balance==Catalog.LINER_PRICE and fresh_ledger.buy_liner() and fresh_ledger.balance==0
	checks["purchase_once"]=not fresh_ledger.buy_liner() and fresh_ledger.balance==0
	var raw:=AlphaCargo.new();var protected:=AlphaCargo.new();protected.protected=true
	for i in 8:
		raw.reduce(.3,false,0,false);protected.reduce(.3,false,0,false)
		var a:=raw.reduce(1.0/60,true,1,true);var b:=protected.reduce(1.0/60,true,1,true)
		checks["protection_episode_%d" % i]=b<=a or raw.condition_units==0
		checks["protection_receipt_%d" % i]=protected.loss_receipt.raw_capped_loss_units-protected.loss_receipt.protection_actual_reduction_units==b and b==protected.loss_receipt.committed_loss_units
	checks["protected_zero_possible"]=protected.condition_units==0
	checks["unprotected_original_max"]=raw.loss_receipt.raw_episode_loss_units==240
	checks["liner_modest"]=protected.loss_receipt.protection_nominal_reduction_units==60
func run() -> void:
	unit_checks()
	review=load("res://review/alpha_loop/alpha_review.tscn").instantiate()
	add_child(review)
	await ticks(120)
	game=review.game;job=review.job;gate=job.gate;craft=job.craft
	checks["market_home"]=job.state=="FREE_ROAM" and job.can_dispatch() and job.session.balance==0
	checks["three_distinct_destinations"]=Catalog.JOBS.size()==3 and Catalog.JOBS[0].destination=="DEP" and Catalog.JOBS[1].destination=="RLY" and Catalog.JOBS[2].destination=="WRK"
	checks["three_single_incentives"]=Catalog.JOBS[0].objective=="STYLE" and Catalog.JOBS[1].objective=="COMMIT" and Catalog.JOBS[2].objective=="CARE"
	await capture("01_market_home")
	key(KEY_E);await ticks(3);await capture("02_dispatch")
	checks["dispatch_pauses"]=get_tree().paused and job.state=="DISPATCH"
	key(KEY_2);checks["board_select"]=job.selected==1
	key(KEY_1);Input.action_press("throttle");key(KEY_ENTER);await ticks(10)
	checks["accept_neutral_input_guard"]=job.state=="WAIT_NEUTRAL"
	Input.action_release("throttle");await ticks(8)
	var clock: float=job.elapsed
	key(KEY_ESCAPE);await get_tree().process_frame
	var weather: Node=gate.get_node("WarmOvercastWeather")
	var age: float=weather.active_time
	await ticks(20)
	checks["pause_clock_weather"]=job.elapsed==clock and weather.active_time==age
	key(KEY_ESCAPE);await ticks(8)
	var direct: Array[Vector2]=[job.origin,job.destination]
	route_id="DEP_direct"
	var driven:=await Driver.drive(self,direct)
	routes.append({"id":route_id,"result":driven})
	checks["depot_driven"]=driven.delivered and driven.reset_delta==0
	await capture("03_depot_results")
	if job.state=="ACTIVE":job._finish(false,"Diagnostic drive incomplete")
	var pose:=craft.global_transform;var velocity:=craft.velocity;var balance: int=job.session.balance
	job._finish(true,"Duplicate")
	checks["terminal_no_double_commit"]=job.session.balance==balance
	key(KEY_R)
	checks["results_retry_cannot_commit"]=job.session.balance==balance and job.state=="RESULTS" and craft.global_transform==pose
	key(KEY_ENTER)
	checks["continue_exact_pose_velocity"]=craft.global_transform==pose and craft.velocity==velocity
	await ticks(8)
	checks["continue_stays_destination"]=job.state=="FREE_ROAM" and job._xz().distance_to(job.destination)<8
	await capture("04_depot_return_cue")
	var home_path: Array[Vector2]=[job._xz(),job.origin]
	route_id="DEP_home"
	var home_run:=await Driver.drive(self,home_path,false,true)
	routes.append({"id":route_id,"result":home_run})
	checks["drive_home_no_teleport"]=home_run.arrived_home and home_run.reset_delta==0 and job.can_dispatch()
	key(KEY_E)
	checks["home_reopens_board"]=job.state=="DISPATCH" and job.session.balance==balance
	await capture("04b_home_board")
	key(KEY_ESCAPE);await ticks(8)
	for item in [[0,"DEP_style",["-L1"],false],[1,"RLY_spine",["-L5","-L4"],false],[2,"WRK_way",["L6"],false],[2,"WRK_sidepass",["L6"],false],[2,"WRK_hot_recovery",["L6"],false],[0,"DEP_road",["-L1"],false],[1,"RLY_sweep",["-L1","-L0","A1"],false],[2,"WRK_rough_alternate",["-L5","R0"],true]]:
		await fresh(item[0]);route_id=item[1]
		var path:=Driver.road(gate,item[2])
		if route_id in ["DEP_style","WRK_way","WRK_hot_recovery"]:path=[job.origin,job.destination]
		driven=await Driver.drive(self,path,item[3])
		routes.append({"id":route_id,"result":driven})
		checks[route_id+"_driven"]=driven.delivered and driven.reset_delta==0
		await capture("results_"+route_id)
	# Deliberate synthetic endpoint cases separate predicates from route driving.
	for i in 3:
		await fresh(i)
		checks["accept_%d_at_market" % i]=job.state=="ACTIVE" and job._xz().distance_to(job.origin)<1
		job.elapsed=3600;job.longest_streak=0;job.slip_brrr=0;job.cargo.condition_units=0
		before_balance=job.session.balance
		place_without_reset(job.destination)
		await ticks(90)
		checks["zero_and_all_bonus_missed_%d" % i]=job.last_result.get("delivered",false) and job.last_result.condition_units==0 and not job.last_result.objective_met and job.last_result.total_credits==Catalog.JOBS[i].base and job.session.balance==before_balance+int(Catalog.JOBS[i].base)
		key(KEY_ENTER);await ticks(8)
		checks["continue_%d_at_destination" % i]=job._xz().distance_to(job.destination)<8
	await reset_at(job.origin);key(KEY_E)
	checks["earnings_afford_purchase"]=job.session.balance>=Catalog.LINER_PRICE
	before_balance=job.session.balance
	key(KEY_C)
	checks["board_purchase_exact"]=job.session.liner_owned and job.session.balance==before_balance-Catalog.LINER_PRICE
	key(KEY_C)
	checks["board_no_double_purchase"]=job.session.balance==before_balance-Catalog.LINER_PRICE
	await capture("05_liner_owned")
	key(KEY_3);key(KEY_ENTER);await ticks(8)
	checks["protected_next_parcel"]=job.cargo.protected
	# Explicit fixture placement at the new service bar; unchanged controller/cargo handles contact.
	var crossing:=gate.world.get_node("WorksServiceCrossing")
	craft.global_transform=Transform3D(Basis(Vector3.UP,atan2(-crossing.forward.x,-crossing.forward.z)),crossing.center-crossing.forward*8+Vector3.UP*1.4);craft.velocity=crossing.forward*16;craft.reset_physics_interpolation();gate.camera_rig.snap_to_target()
	await ticks(120)
	checks["protected_world_impact_receipt"]=not review.last_loss.is_empty() and review.last_loss.has("protection_receipt") and review.last_loss.protection_receipt.protection_actual_reduction_units>0
	key(KEY_F3);key(KEY_F2);await capture("06_protected_receipt")
	var saved: float=job.cargo.saved_total
	checks["protection_commits_condition_only"]=job.cargo.committed_total==1000-job.cargo.condition_units and saved>0
	key(KEY_ESCAPE);before_balance=job.session.balance;var resets:=craft.reset_count;key(KEY_R)
	checks["paused_retry_no_payout"]=job.state=="RESULTS" and not job.last_result.delivered and job.session.balance==before_balance and craft.reset_count==resets+1
	key(KEY_ENTER);await ticks(10)
	checks["weather_restarts"]=weather.rain.emitting and not weather.reset_pending
	await fresh(0);before_balance=job.session.balance;craft.global_position.y=craft.tuning.fall_reset_y-10;await ticks(4)
	checks["fall_no_payout"]=job.state=="RESULTS" and not job.last_result.delivered and job.session.balance==before_balance
	await fresh(1);before_balance=job.session.balance;gate.spawn_selected_tour()
	checks["diagnostic_no_payout"]=job.state=="RESULTS" and not job.last_result.delivered and job.session.balance==before_balance
	checks["depot_naive_no_style"]=not routes[0].result.receipt.objective_met
	for row in routes:
		if row.id in ["DEP_style","RLY_sweep","WRK_way"]:checks[row.id+"_bonus"]=row.result.receipt.get("objective_met",false)
		if row.id=="WRK_hot_recovery":checks["hot_works_delivers_base_only"]=row.result.delivered and not row.result.receipt.get("objective_met",true)
		if row.id=="RLY_spine":checks["interior_no_commit"]=not row.result.receipt.get("objective_met",true)
	checks["trail_bounded"]=job.trail.history.size()<=18 and not has_physics(job.trail)
	job.trail.clear();checks["trail_clears"]=job.trail.history.is_empty()
	checks["landmark_no_physics"]=not has_physics(gate.world.get_node("MarketHomeLantern"))
	var good:=true
	for value in checks.values():good=good and value
	var result:={"status":"PASS" if good else "FAIL","checks":checks,"routes":routes,"note":"Normal-input routes plus explicitly synthetic endpoint/reset/contact predicates. Human loop/feel remains owner review."}
	print("MECHANICS_SMOKE_RESULT "+JSON.stringify(result));finished.emit(result)
var before_balance := 0
func has_physics(node: Node) -> bool:
	if node is CollisionObject3D or node is CollisionShape3D:return true
	for child in node.get_children():
		if has_physics(child):return true
	return false
