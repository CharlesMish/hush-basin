extends SceneTree
## Isolated HUD fixture. No craft, geometry, receipts or gameplay are modified.
const Hud = preload("res://scripts/courier/mastery_dispatch_hud.gd")
const Catalog = preload("res://scripts/courier/alpha_contracts.gd")

class MockMastery extends RefCounted:
	var states: Dictionary = {}
	var reward_owned := false
	var trail_style := "standard"
	func status(job_id: String) -> Dictionary:return states.get(job_id,{"delivered":false,"mastered":false})
	func mastery_count() -> int:
		var total := 0
		for state in states.values():total += int(state.get("mastered",false))
		return total
	func reward_unlocked() -> bool:return mastery_count()>=2

class MockJob extends Node:
	var state := "DISPATCH"
	var selected := 0
	var board_notice := ""
	var session = preload("res://scripts/courier/alpha_session.gd").new()
	var last_result: Dictionary = {}
	var contract: Dictionary = Catalog.job(0)
	var execution = MockExecution.new()
	var lines = preload("res://scripts/courier/line_evidence.gd").new()

class MockExecution extends RefCounted:
	var snapshot: Dictionary = {}

var checks: Array[Dictionary] = []
var captures := ""

func _initialize() -> void:call_deferred("run")

func run() -> void:
	root.size = Vector2i(1280,720)
	var args := OS.get_cmdline_user_args()
	if args.has("--captures"):captures=args[args.find("--captures")+1];DirAccess.make_dir_recursive_absolute(captures)
	var hud := Hud.new()
	var job := MockJob.new()
	var mastery := MockMastery.new()
	root.add_child(job)
	root.add_child(hud)
	hud.mastery_state = mastery
	hud.select_job.connect(func(index: int):job.selected=index)
	job.session.balance = 260
	for selected in Catalog.JOBS.size():
		job.selected = selected
		hud.refresh(job)
		await process_frame
		await process_frame
		record("three_visible_%d" % selected,hud.cards.size()==3 and hud.visible_indices.size()==3)
		record("selection_centered_%d" % selected,hud.visible_indices[1]==selected)
		record("neighbors_wrap_%d" % selected,hud.visible_indices==[posmod(selected-1,5),selected,posmod(selected+1,5)])
		record("board_in_view_%d" % selected,_in_view(hud.board))
		for slot in 3:
			for field in hud.card_labels[slot]:
				var l: Label = hud.card_labels[slot][field]
				var width: float=l.get_theme_font("font").get_string_size(l.text,HORIZONTAL_ALIGNMENT_LEFT,-1,l.get_theme_font_size("font_size")).x
				record("text_fits_%d_%d_%s" % [selected,slot,field],width<=l.size.x+.1,{"text":l.text,"text_width":width,"available_width":l.size.x})
		if selected==0:await capture("dispatch_initial")
		if selected==4:await capture("dispatch_quarry")
	job.selected = 0
	hud.refresh(job)
	hud.cards[0].pressed.emit()
	record("left_neighbor_click_wrap",job.selected==4)
	hud.refresh(job)
	hud.cards[2].pressed.emit()
	record("right_neighbor_click_wrap",job.selected==0)
	mastery.states.freight_seals = {"delivered":true,"mastered":true}
	mastery.states.works_instruments = {"delivered":true,"mastered":false}
	job.selected = 1
	hud.refresh(job)
	await process_frame
	record("mastered_distinct",hud.card_labels[0].stamp.text.contains("Mastered"))
	record("delivered_distinct",hud.card_labels[2].stamp.text.contains("Delivered"))
	record("locked_cosmetic_disabled",hud.reward.disabled)
	mastery.states.clinic_thread = {"delivered":true,"mastered":true}
	hud.refresh(job)
	record("earned_cosmetic_available",not hud.reward.disabled and hud.reward.text.contains("200 Credits"))
	await capture("dispatch_mastery")
	mastery.reward_owned = true
	mastery.trail_style = "lantern_amber"
	hud.refresh(job)
	record("one_cosmetic_toggle",hud.reward.text.contains("switch to Standard") and not hud.reward.disabled)
	job.state = "RESULTS"
	job.last_result = {"delivered":true,"job_id":"clinic_thread","job_name":"South desk kit","place":"Clinic","condition_units":976,"elapsed":51.24,"objective":"THREAD","objective_met":true,"base_credits":100,"bonus_credits":300,"total_credits":400,"session_balance":800,"brrr":381,"longest_streak":5.61,"best_drift_s":3.84,"peak_speed":32.1,"episodes":1,"liner_owned":false,"reaction":"Kit received. The south desk stays open."}
	hud.mastery_receipt = {"first_mastery":true,"unlocks":["Lantern amber trail"]}
	hud.refresh(job)
	await process_frame
	await process_frame
	record("result_in_view",_in_view(hud.card),{"size":str(hud.card.size)})
	record("new_mastery_receipt",hud.mastery_result.text.contains("NEW MASTERY SEAL") and hud.mastery_result.text.contains("Unlocked"))
	record("result_retains_receipt",hud.body.text.contains("DELIVERY +100") and hud.body.text.contains("OPTIONAL +300") and hud.body.text.contains("SESSION 800"))
	await capture("results_mastery")
	job.state = "PAUSED"
	hud.refresh(job)
	record("pause_hides_mastery_receipt",not hud.mastery_result.visible)
	job.contract = {"objective":"SWEEP","target":10.0,"bonus":200}
	job.execution.snapshot = {"route_active":false,"route_complete":false,"best_sweep_s":-1.0,"route_reason":"ready"}
	record("sweep_ready_section_start",hud.objective_progress(job).contains("10.0 s section") and hud.objective_progress(job).contains("after West Gate"))
	job.execution.snapshot = {"route_active":true,"route_complete":false,"route_elapsed_s":6.4}
	record("sweep_active_section_clock",hud.objective_progress(job).contains("section 6.4 / 10.0 s"))
	job.execution.snapshot = {"route_active":false,"route_complete":false,"best_sweep_s":12.4,"route_reason":"over reference"}
	record("sweep_missed_still_delivers",hud.objective_progress(job).contains("12.40 / 10.0 s") and hud.objective_progress(job).contains("delivery still pays") and not hud.objective_progress(job).contains("earned"))
	job.execution.snapshot = {"route_active":false,"route_complete":true,"best_sweep_s":9.4,"route_reason":"complete"}
	record("sweep_earned_only_success",hud.objective_progress(job).contains("9.40 / 10.0 s · earned"))
	job.execution.snapshot = {"route_active":false,"route_complete":false,"route_reason":"left road"}
	record("sweep_retry_start_clear",hud.objective_progress(job).contains("retry from West Gate"))
	job.contract = {"objective":"HAUL","bonus":420}
	job.execution.snapshot = {"route_phase":0,"route_active":false,"route_complete":false}
	record("haul_ready_places_not_mode",hud.objective_progress(job).contains("East Sweep, then clean Quarry Shelf") and not hud.objective_progress(job).contains("Drive"))
	job.execution.snapshot = {"route_phase":0,"route_active":true,"route_complete":false}
	record("haul_east_active",hud.objective_progress(job).contains("East Sweep in progress"))
	job.execution.snapshot = {"route_phase":1,"route_active":false,"route_complete":false,"route_reason":"Shelf ready"}
	record("haul_transition_clear",hud.objective_progress(job).contains("enter Shelf from Relay"))
	job.execution.snapshot = {"route_phase":1,"route_active":true,"route_complete":false}
	record("haul_shelf_clean",hud.objective_progress(job).contains("keep crossing clean"))
	job.execution.snapshot = {"route_phase":1,"route_active":false,"route_complete":false,"route_reason":"Shelf contact"}
	record("haul_contact_retry",hud.objective_progress(job).contains("Shelf contact · retry from Relay end"))
	job.execution.snapshot = {"route_phase":2,"route_active":false,"route_complete":true,"route_reason":"complete"}
	record("haul_completed_geography",hud.objective_progress(job).contains("East Sweep + clean Shelf earned"))
	job.contract = Catalog.job(0)
	var inherited_hud = hud.get_script().get_base_script().new()
	record("style_preserved",hud.objective_progress(job)==inherited_hud.objective_progress(job))
	inherited_hud.free()
	job.contract = Catalog.job(2)
	record("care_preserved",hud.objective_progress(job).contains("arrive with at least 85%"))
	job.contract = Catalog.job(3)
	record("thread_preserved",hud.objective_progress(job).contains("South Cut · Spread, Hop or dogleg"))
	var failures := checks.filter(func(c: Dictionary):return not c.pass)
	var result := {"status":"PASS" if failures.is_empty() else "FAIL","checks":checks.size(),"failures":failures,"all_checks":checks}
	print("MASTERY_DISPATCH_PROBE "+JSON.stringify(result))
	if args.has("--result"):
		var file := FileAccess.open(args[args.find("--result")+1],FileAccess.WRITE)
		file.store_string(JSON.stringify(result,"  "))
	quit(0 if failures.is_empty() else 1)

func record(name: String, passed: bool, evidence: Dictionary={}) -> void:
	checks.append({"name":name,"pass":passed,"evidence":evidence})

func _in_view(control: Control) -> bool:
	var r := control.get_global_rect()
	return r.position.x>=0 and r.position.y>=0 and r.end.x<=1280 and r.end.y<=720

func capture(name: String) -> void:
	if captures.is_empty():return
	await process_frame
	await RenderingServer.frame_post_draw
	root.get_texture().get_image().save_png(captures.path_join(name+".png"))
