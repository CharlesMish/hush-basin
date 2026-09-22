extends "res://scripts/courier/courier_director.gd"
## A finite Relay experiment beside the unchanged driving/arrival observer.
const Catalog=preload("res://scripts/courier/relay_contracts.gd")
const Project=preload("res://scripts/courier/relay_project.gd")
var session=preload("res://scripts/courier/relay_session.gd").new()
var project=Project.new()
var neutral_control:=false
var selected:=0
var board_jobs: Array[Dictionary]=[]
var board_hub:="MRK"
var contract: Dictionary=Catalog.ordinary(0)
var attempt_id:=0
var slip_brrr:=0.0
var lines=preload("res://scripts/courier/line_evidence.gd").new()
var execution=preload("res://scripts/courier/route_execution.gd").new()
var trail: MeshInstance3D
var annex: Node3D
var board_notice:=""
var project_receipt: Dictionary={}
var project_error:=""
var _weather_revision:=0

func _initialize() -> void:
	cargo=preload("res://scripts/courier/alpha_cargo.gd").new()
	await super._initialize()
	# Diagnostic scenes inject an isolated save; normal launches use only user://.
	if get_tree().has_meta("relay_test_save"):project=Project.new(String(get_tree().get_meta("relay_test_save")))
	neutral_control="--relay-control" in OS.get_cmdline_user_args()
	if get_tree().has_meta("relay_test_control"):neutral_control=bool(get_tree().get_meta("relay_test_control"))
	var loaded: Dictionary=project.load_state()
	if not loaded.ok:project_error=String(loaded.error)
	remove_child(hud);hud.queue_free()
	hud=preload("res://scripts/courier/relay_hud.gd").new();add_child(hud)
	hud.primary.connect(primary_action);hud.secondary.connect(close_dispatch)
	hud.select_job.connect(select_contract);hud.purchase.connect(purchase_liner)
	hud.reset_experiment.connect(reset_experiment)
	hud.mastery_state=session.mastery
	var lantern:=preload("res://scripts/courier/market_lantern.gd").new()
	lantern.manifest=gate.data.manifest;gate.world.add_child(lantern)
	var feature:=preload("res://scripts/courier/mechanics_feature.gd").new()
	feature.gate=gate;gate.world.add_child(feature)
	trail=preload("res://scripts/courier/slip_trail.gd").new();trail.craft=craft;gate.add_child(trail)
	annex=preload("res://scripts/courier/relay_annex.gd").new()
	gate.world.add_child(annex);annex.configure(gate.data)
	apply_project_state()
	lines.configure(gate.data);execution.configure(gate.data)
	refresh_pool("MRK")
	print("RELAY_CONSEQUENCE_READY stage=",project.stage()," neutral=",neutral_control," source=66b4c228")

func apply_project_state() -> void:
	annex.set_stage(0 if neutral_control else project.stage())
	# One bounded refresh after the static roof silhouettes change. Particle-only.
	_weather_revision+=1
	var revision:=_weather_revision
	var floor_node: GPUParticlesCollisionHeightField3D=gate.get_node("WarmOvercastWeather").rain_collision
	floor_node.update_mode=GPUParticlesCollisionHeightField3D.UPDATE_MODE_ALWAYS
	await get_tree().process_frame
	await get_tree().process_frame
	if revision==_weather_revision:floor_node.update_mode=GPUParticlesCollisionHeightField3D.UPDATE_MODE_WHEN_MOVED

func hub_position(id: String) -> Vector2:
	return P1AWorldData.xz(gate.data.manifest.destination_pads[id].center_xz_m)

func nearby_hub() -> String:
	# Exactly these three authored points; this is not an arbitrary pickup system.
	for id in ["MRK","WRK","RLY"]:
		if id=="WRK" and project.stage()<1:continue
		if id=="RLY" and not project.outbound_available():continue
		var pad: Dictionary=gate.data.manifest.destination_pads[id]
		if _xz().distance_to(hub_position(id))<=float(pad.inner_flat_radius_m):return id
	return ""

func can_dispatch() -> bool:
	return not nearby_hub().is_empty() and _supported() and craft.velocity.length()<=Rules.DISPATCH_SPEED

func refresh_pool(hub: String) -> void:
	board_hub=hub;selected=0;board_jobs.clear()
	if hub=="MRK":
		board_jobs.append(Catalog.project_job(0,neutral_control))
		for i in 5:board_jobs.append(Catalog.ordinary(i))
	elif hub=="WRK":board_jobs.append(Catalog.project_job(1,neutral_control))
	elif hub=="RLY":board_jobs.append(Catalog.outbound(neutral_control))
	board_notice=""

func select_contract(index: int) -> void:
	if state=="DISPATCH":selected=posmod(index,board_jobs.size())

func purchase_liner() -> void:
	if state!="DISPATCH":return
	if session.buy_liner():board_notice="Cargo liner fitted · 25% less cargo loss. This session only."
	elif session.liner_owned:board_notice="Cargo liner already fitted."
	else:board_notice="Cargo liner costs 400 Credits."

func _input(event: InputEvent) -> void:
	if initialized and hud.get("reset_dialog")!=null and hud.reset_dialog.visible:return
	if initialized and state=="DISPATCH" and event is InputEventKey and event.pressed and not event.echo:
		var code: int=event.physical_keycode if event.physical_keycode else event.keycode
		if code in [KEY_LEFT,KEY_RIGHT]:select_contract(selected+(1 if code==KEY_RIGHT else -1));get_viewport().set_input_as_handled();return
		if code>=KEY_1 and code<=KEY_9:
			if code-KEY_1<board_jobs.size():select_contract(code-KEY_1)
			get_viewport().set_input_as_handled();return
		if code==KEY_C:purchase_liner();get_viewport().set_input_as_handled();return
	if initialized and state=="DISPATCH" and event is InputEventJoypadButton and event.pressed and event.button_index in [JOY_BUTTON_DPAD_LEFT,JOY_BUTTON_DPAD_RIGHT]:
		select_contract(selected+(1 if event.button_index==JOY_BUTTON_DPAD_RIGHT else -1));get_viewport().set_input_as_handled();return
	super._input(event)

func primary_action() -> void:
	if state=="FREE_ROAM" and can_dispatch():refresh_pool(nearby_hub())
	if state=="DISPATCH":
		contract=board_jobs[selected].duplicate(true)
		# Old challenge metrics remain observers even on ordinary/project work.
		slip_brrr=0;lines.begin(craft);execution.begin(contract.objective,craft.global_position)
		var pad: Dictionary=gate.data.manifest.destination_pads[contract.destination]
		destination=P1AWorldData.xz(pad.center_xz_m);destination_radius=float(pad.inner_flat_radius_m)
		cargo.protected=session.liner_owned;attempt_id=session.accept(contract)
		project_receipt={}
		var advisory: Array[String]=[]
		for route in contract.routes:advisory.append(String(route).trim_prefix("-"))
		gate.map.set_highlighted_routes(advisory)
	var previous:=state
	super.primary_action()
	if previous=="RESULTS":
		var empty: Array[String]=[];gate.map.set_highlighted_routes(empty)

func guidance_id() -> String:
	var local:=nearby_hub()
	if not local.is_empty():return local
	return "WRK" if project.stage()==1 else "MRK"

func _process(delta: float) -> void:
	super._process(delta)
	if not initialized or annex==null:return
	var active: bool=state=="ACTIVE" or (state in ["PAUSED","WAIT_NEUTRAL"] and _resume_state=="ACTIVE")
	var id: String=String(contract.destination) if active else guidance_id()
	cue.configure(destination if active else hub_position(id),id)

func _finish(delivered: bool, message: String) -> void:
	if not (state=="ACTIVE" or (state in ["PAUSED","WAIT_NEUTRAL"] and _resume_state=="ACTIVE")):return
	var evidence:={"delivered":delivered,"message":"Delivered" if delivered else message,"condition_units":cargo.condition_units,"elapsed":elapsed,"impact_samples":cargo.impact_samples,"episodes":cargo.episodes,"ignored_samples":cargo.ignored_samples,"brrr":brrr,"longest_streak":longest_streak,"peak_speed":peak_speed,"raw_cargo_loss_units":cargo.raw_total,"protection_saved_units":cargo.saved_total,"committed_cargo_loss_units":cargo.committed_total,"slip_brrr":slip_brrr,"reaction":contract.reaction,"objective_target":contract.target}
	evidence.merge(lines.snapshot,true);evidence.merge(execution.snapshot,true)
	last_result=session.settle(attempt_id,evidence)
	hud.mastery_receipt=session.mastery_receipt(attempt_id)
	project_receipt=project.contribute(String(contract.id),delivered)
	if not project_receipt.ok:project_error=String(project_receipt.error)
	else:project_error=""
	apply_project_state()
	state="RESULTS";get_tree().paused=true
	print("RELAY_DELIVERY ",JSON.stringify({"receipt":last_result,"contribution":project_receipt,"project":project.snapshot()}))

func reset_experiment() -> void:
	# UI confirmation is explicit. Never cancel an active parcel via this path.
	if state!="DISPATCH":return
	var result: Dictionary=project.reset_project()
	if not result.ok:project_error=String(result.error);return
	project_error="";apply_project_state()
	board_notice="Project reset. Both needs and Relay Dispatch are reset; session Credits are unchanged."
	if board_hub!="MRK":close_dispatch()

func _physics_process(delta: float) -> void:
	if initialized and not get_tree().paused and state=="ACTIVE":
		lines.sample(craft,delta);execution.sample(craft,delta)
		var observed:=Brrr.step(craft.velocity,-craft.global_basis.z,craft.regime_name()=="DRIVE",delta,brrr,streak)
		var split: float=observed.split_degrees
		slip_brrr+=(float(observed.brrr)-brrr)*split/(30.0+split)
	super._physics_process(delta)
