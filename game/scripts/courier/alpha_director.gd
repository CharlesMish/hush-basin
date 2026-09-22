extends "res://scripts/courier/courier_director.gd"
## Five-job session sibling; inherited movement observation/arrival are intact.
const Catalog = preload("res://scripts/courier/alpha_contracts.gd")
const Session = preload("res://scripts/courier/mastery_session.gd")
const AlphaCargo = preload("res://scripts/courier/alpha_cargo.gd")
const AlphaHud = preload("res://scripts/courier/mastery_dispatch_hud.gd")
const MarketLantern = preload("res://scripts/courier/market_lantern.gd")
var session=Session.new()
var selected := 0
var contract: Dictionary=Catalog.job(0)
var attempt_id := 0
var slip_brrr := 0.0
var lines=preload("res://scripts/courier/line_evidence.gd").new()
var execution=preload("res://scripts/courier/route_execution.gd").new()
var trail: MeshInstance3D
var board_notice := "Any legal delivery pays base. First optional success earns that job's mastery seal."

func _initialize() -> void:
	cargo=AlphaCargo.new()
	await super._initialize()
	remove_child(hud);hud.queue_free()
	hud=AlphaHud.new();add_child(hud)
	hud.primary.connect(primary_action)
	hud.secondary.connect(close_dispatch)
	hud.select_job.connect(select_contract)
	hud.purchase.connect(purchase_liner)
	hud.cosmetic.connect(choose_trail)
	hud.mastery_state=session.mastery
	var lantern:=MarketLantern.new()
	lantern.manifest=gate.data.manifest
	gate.world.add_child(lantern)
	var feature:=preload("res://scripts/courier/mechanics_feature.gd").new()
	feature.gate=gate;gate.world.add_child(feature)
	trail=preload("res://scripts/courier/slip_trail.gd").new();trail.craft=craft;gate.add_child(trail)
	lines.configure(gate.data)
	execution.configure(gate.data)
	print("MASTERY_ALPHA_READY five open jobs; first mastery; session reward; accepted v1.1 cargo")

func select_contract(index: int) -> void:
	if state!="DISPATCH":return
	selected=clampi(index,0,Catalog.JOBS.size()-1)
	board_notice="Any legal delivery pays base. First optional success earns that job's mastery seal."

func choose_trail() -> void:
	if state!="DISPATCH":return
	if not session.mastery.reward_owned:
		if not session.buy_trail():return
		board_notice="Lantern amber owned and equipped. Trail feedback works exactly as before."
	else:
		var next: String="standard" if session.mastery.trail_style=="lantern_amber" else "lantern_amber"
		session.set_trail_style(next)
		board_notice="Trail: "+("standard teal" if next=="standard" else "Lantern amber")+". Free to switch."
	trail.trail_style=session.mastery.trail_style

func purchase_liner() -> void:
	if state!="DISPATCH":return
	if session.buy_liner():board_notice="Cargo liner installed · 25% smaller cargo bills. This session only."
	elif session.liner_owned:board_notice="Cargo liner already installed."
	else:board_notice="Cargo liner costs %d Credits. No debt; keep driving." % Catalog.LINER_PRICE

func _input(event: InputEvent) -> void:
	if initialized and state=="DISPATCH" and event is InputEventKey and event.pressed and not event.echo:
		var code: int=event.physical_keycode if event.physical_keycode!=0 else event.keycode
		if code in [KEY_1,KEY_2,KEY_3,KEY_4,KEY_5]:
			select_contract(code-KEY_1);get_viewport().set_input_as_handled();return
		if code in [KEY_LEFT,KEY_RIGHT]:
			select_contract(posmod(selected+(1 if code==KEY_RIGHT else -1),Catalog.JOBS.size()));get_viewport().set_input_as_handled();return
		if code==KEY_C:
			purchase_liner();get_viewport().set_input_as_handled();return
		if code==KEY_T:
			choose_trail();get_viewport().set_input_as_handled();return
	if initialized and state=="DISPATCH" and event is InputEventJoypadButton and event.pressed and event.button_index in [JOY_BUTTON_DPAD_LEFT,JOY_BUTTON_DPAD_RIGHT]:
		select_contract(posmod(selected+(1 if event.button_index==JOY_BUTTON_DPAD_RIGHT else -1),Catalog.JOBS.size()));get_viewport().set_input_as_handled();return
	super._input(event)

func primary_action() -> void:
	if state=="DISPATCH":
		slip_brrr=0.0
		lines.begin(craft)
		contract=Catalog.job(selected)
		execution.begin(contract.objective,craft.global_position)
		var pad: Dictionary=gate.data.manifest.destination_pads[contract.destination]
		destination=P1AWorldData.xz(pad.center_xz_m)
		destination_radius=float(pad.inner_flat_radius_m)
		cargo.protected=session.liner_owned
		attempt_id=session.accept(contract)
		var advisory: Array[String]=[]
		for route in contract.routes:advisory.append(route)
		gate.map.set_highlighted_routes(advisory)
	var previous:=state
	super.primary_action()
	if previous=="RESULTS":
		var no_routes: Array[String]=[]
		gate.map.set_highlighted_routes(no_routes)

func _process(delta: float) -> void:
	super._process(delta)
	if not initialized:return
	var active: bool=state=="ACTIVE" or (state in ["PAUSED","WAIT_NEUTRAL"] and _resume_state=="ACTIVE")
	cue.configure(destination if active else origin,String(contract.destination) if active else "MRK")

func _finish(delivered: bool, message: String) -> void:
	if not (state=="ACTIVE" or (state in ["PAUSED","WAIT_NEUTRAL"] and _resume_state=="ACTIVE")):return
	var evidence:={"delivered":delivered,"message":"Delivered" if delivered else message,"condition_units":cargo.condition_units,"elapsed":elapsed,"impact_samples":cargo.impact_samples,"episodes":cargo.episodes,"ignored_samples":cargo.ignored_samples,"brrr":brrr,"longest_streak":longest_streak,"peak_speed":peak_speed,"raw_cargo_loss_units":cargo.raw_total,"protection_saved_units":cargo.saved_total,"committed_cargo_loss_units":cargo.committed_total,"slip_brrr":slip_brrr,"reaction":contract.reaction,"objective_target":contract.target}
	evidence.merge(lines.snapshot,true)
	evidence.merge(execution.snapshot,true)
	last_result=session.settle(attempt_id,evidence)
	hud.mastery_receipt=session.mastery_receipt(attempt_id)
	state="RESULTS"
	get_tree().paused=true

func _physics_process(delta: float) -> void:
	if initialized and not get_tree().paused and state=="ACTIVE":
		# Decompose the unchanged metric's earned increment. This is its existing
		# slip contribution, not a replacement BRRR formula or universal multiplier.
		lines.sample(craft,delta)
		execution.sample(craft,delta)
		var observed:=Brrr.step(craft.velocity,-craft.global_basis.z,craft.regime_name()=="DRIVE",delta,brrr,streak)
		var split: float=observed.split_degrees
		slip_brrr+=(float(observed.brrr)-brrr)*split/(30.0+split)
	super._physics_process(delta)
