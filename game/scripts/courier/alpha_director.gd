extends "res://scripts/courier/courier_director.gd"
## Three-job session sibling; inherited movement observation/arrival are intact.
const Catalog = preload("res://scripts/courier/alpha_contracts.gd")
const Session = preload("res://scripts/courier/alpha_session.gd")
const AlphaCargo = preload("res://scripts/courier/alpha_cargo.gd")
const AlphaHud = preload("res://scripts/courier/alpha_hud.gd")
const MarketLantern = preload("res://scripts/courier/market_lantern.gd")
var session=Session.new()
var selected := 0
var contract: Dictionary=Catalog.job(0)
var attempt_id := 0
var board_notice := "Three repeatable jobs. One optional bonus each."

func _initialize() -> void:
	cargo=AlphaCargo.new()
	await super._initialize()
	remove_child(hud);hud.queue_free()
	hud=AlphaHud.new();add_child(hud)
	hud.primary.connect(primary_action)
	hud.secondary.connect(close_dispatch)
	hud.select_job.connect(select_contract)
	hud.purchase.connect(purchase_liner)
	var lantern:=MarketLantern.new()
	lantern.manifest=gate.data.manifest
	gate.world.add_child(lantern)
	print("ALPHA_LOOP_READY three jobs; session credits; accepted v1.1 cargo")

func select_contract(index: int) -> void:
	if state!="DISPATCH":return
	selected=clampi(index,0,Catalog.JOBS.size()-1)
	board_notice="Any legal route counts. Missing the bonus still pays the base."

func purchase_liner() -> void:
	if state!="DISPATCH":return
	if session.buy_liner():board_notice="Cargo liner installed · 25% smaller cargo bills. This session only."
	elif session.liner_owned:board_notice="Cargo liner already installed."
	else:board_notice="Cargo liner costs %d Credits. No debt; keep driving." % Catalog.LINER_PRICE

func _input(event: InputEvent) -> void:
	if initialized and state=="DISPATCH" and event is InputEventKey and event.pressed and not event.echo:
		var code: int=event.physical_keycode if event.physical_keycode!=0 else event.keycode
		if code in [KEY_1,KEY_2,KEY_3]:
			select_contract(code-KEY_1);get_viewport().set_input_as_handled();return
		if code in [KEY_LEFT,KEY_RIGHT]:
			select_contract(posmod(selected+(1 if code==KEY_RIGHT else -1),3));get_viewport().set_input_as_handled();return
		if code==KEY_C:
			purchase_liner();get_viewport().set_input_as_handled();return
	if initialized and state=="DISPATCH" and event is InputEventJoypadButton and event.pressed and event.button_index in [JOY_BUTTON_DPAD_LEFT,JOY_BUTTON_DPAD_RIGHT]:
		select_contract(posmod(selected+(1 if event.button_index==JOY_BUTTON_DPAD_RIGHT else -1),3));get_viewport().set_input_as_handled();return
	super._input(event)

func primary_action() -> void:
	if state=="DISPATCH":
		contract=Catalog.job(selected)
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
	var evidence:={"delivered":delivered,"message":"Delivered" if delivered else message,"condition_units":cargo.condition_units,"elapsed":elapsed,"impact_samples":cargo.impact_samples,"episodes":cargo.episodes,"ignored_samples":cargo.ignored_samples,"brrr":brrr,"longest_streak":longest_streak,"peak_speed":peak_speed,"raw_cargo_loss_units":cargo.raw_total,"protection_saved_units":cargo.saved_total,"committed_cargo_loss_units":cargo.committed_total}
	last_result=session.settle(attempt_id,evidence)
	state="RESULTS"
	get_tree().paused=true
