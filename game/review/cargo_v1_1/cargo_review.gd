extends Node
## Disposable owner review entry. Ordinary main scene does not load this layer.
const Event = preload("res://review/cargo_v1_1/cargo_event.gd")
var game_scene_path := "res://scenes/district_zero_courier.tscn"
var game: Node
var job: Node
var craft: CraftController
var log_file: FileAccess
var label: Label
var panel: PanelContainer
var initialized := false
var attempt := 0
var elapsed_seen := -1.0
var units_seen := 1000
var counter_seen := 0
var episode_seen := 0
var peak_seen := 0
var severity_peak := 0.0
var last_loss: Dictionary = {}
var last_impact: Dictionary = {}
var log_path := ""
var _pending := PackedStringArray()
var _flush_clock := 0.0

func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	process_physics_priority = 300
	var args := OS.get_cmdline_user_args()
	log_path = args[args.find("--cargo-log")+1] if "--cargo-log" in args else "user://cargo-review-"+str(Time.get_unix_time_from_system()).replace(".","-")+".jsonl"
	log_file = FileAccess.open(log_path,FileAccess.WRITE)
	if log_file==null:
		push_error("Cargo review cannot record evidence: "+log_path)
		get_tree().quit(2)
		return
	write({"event":"session","build":"courier-v1.1-cargo-adjudication","engine":Engine.get_version_info(),"schema":1,"note":"Review-only subclass captures pre_move_velocity argument, then calls unchanged superclass. No movement or response override."})
	game = load(game_scene_path).instantiate()
	craft = game.get_node("DistrictZeroP1A/Craft")
	var tuning := craft.tuning
	craft.set_script(preload("res://review/cargo_v1_1/review_craft.gd"))
	craft.tuning = tuning
	add_child(game)
	await get_tree().process_frame
	await get_tree().process_frame
	job = game.get_node("CourierLayer")
	var canvas := CanvasLayer.new()
	canvas.layer = 50
	add_child(canvas)
	panel = PanelContainer.new()
	panel.position = Vector2(515,18)
	panel.custom_minimum_size = Vector2(460,126)
	panel.mouse_filter = Control.MOUSE_FILTER_IGNORE
	var style := StyleBoxFlat.new()
	style.bg_color = Color(.03,.045,.05,.94)
	style.border_color = Color(.7,.53,.3)
	style.set_border_width_all(1)
	style.content_margin_left = 12
	style.content_margin_right = 12
	style.content_margin_top = 10
	style.content_margin_bottom = 10
	panel.add_theme_stylebox_override("panel",style)
	label = Label.new()
	label.add_theme_font_size_override("font_size",14)
	label.text = "CARGO FEEL v1.1 · RECORDING\nIncoming / closing / post-response speed\nLoss receipts appear here. F2 hides this panel.\nF3 bookmarks a contact for review."
	panel.add_child(label)
	canvas.add_child(panel)
	initialized = true
	print("CARGO_REVIEW_LOG "+ProjectSettings.globalize_path(log_path))

func _input(event: InputEvent) -> void:
	if not initialized or not event is InputEventKey or not event.pressed or event.echo:
		return
	if event.physical_keycode==KEY_F2 or event.keycode==KEY_F2:
		panel.visible = not panel.visible
		get_viewport().set_input_as_handled()
	elif event.physical_keycode==KEY_F3 or event.keycode==KEY_F3:
		write({"event":"owner_bookmark","attempt":attempt,"state":job.state,"active_time":job.elapsed,"current_world_speed":craft.velocity.length(),"last_impact":last_impact,"last_loss":last_loss,"note":"Last impact/loss are historical receipts, not a new charge."})
		_flush_log()
		get_viewport().set_input_as_handled()

func _physics_process(_delta: float) -> void:
	if not initialized or job.state!="ACTIVE" or get_tree().paused:
		return
	var cargo: RefCounted = job.cargo
	if attempt!=cargo.observation_serial:
		attempt = cargo.observation_serial
		units_seen = 1000
		counter_seen = 0
		episode_seen = 0
		peak_seen = 0
		severity_peak = 0
		last_loss = {}
		last_impact = {}
		label.text = "CARGO FEEL v1.1 · PARCEL %d\nRecording fresh contact evidence.\nNo loss charged on this parcel.\nF2 hides this panel · F3 bookmarks a contact." % attempt
		write({"event":"parcel_accepted","attempt":attempt,"active_time":job.elapsed})
	elapsed_seen = job.elapsed
	if cargo.episodes!=episode_seen:
		severity_peak = 0
	if cargo.impact_samples!=counter_seen:
		var contact: Dictionary = cargo.contacts(craft)
		if contact.eligible:
			severity_peak = maxf(severity_peak,craft.last_impact_severity)
		var sample := {"fresh":true,"eligible":contact.eligible,"loss":maxi(0,int(cargo.get("_charged_peak"))- (peak_seen if cargo.episodes==episode_seen else 0)) if contact.eligible else 0}
		var row := Event.record(craft,cargo,sample,units_seen,peak_seen,severity_peak)
		row["event"] = "impact"
		row["attempt"] = attempt
		row["active_time"] = job.elapsed
		row["accepted_loss"] = units_seen>cargo.condition_units
		last_impact = row
		write(row)
		if row.accepted_loss:
			last_loss = row
			label.text = "LAST CARGO LOSS  −%.1f%%   ·   total %.1f%%\n%s · episode %d · impact %d\nIncoming %.2f  /  closing %.2f  /  after %.2f m/s\nSeverity %.3f · episode peak %.3f\nCARGO FEEL v1.1 · F2 hide · F3 bookmark" % [row.incremental_loss_units/10.0,row.cumulative_loss_units/10.0,row.form,row.cargo_episode,row.impact_counter,row.pre_impact_world_speed,row.impact_closing_speed,row.post_response_world_speed,row.impact_severity,row.episode_peak_severity]
	units_seen = cargo.condition_units
	counter_seen = cargo.impact_samples
	episode_seen = cargo.episodes
	peak_seen = cargo.get("_charged_peak")

func write(row: Dictionary) -> void:
	_pending.append(JSON.stringify(row))

func _process(delta: float) -> void:
	_flush_clock += delta
	if _flush_clock>=.25:
		_flush_clock = 0
		_flush_log()

func _flush_log() -> void:
	if log_file==null or _pending.is_empty(): return
	log_file.store_string("\n".join(_pending)+"\n")
	log_file.flush()
	_pending.clear()

func _exit_tree() -> void:
	_flush_log()
