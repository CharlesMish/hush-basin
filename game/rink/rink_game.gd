extends Node3D
## Hem Loop — a separately launchable Hush Basin time trial.
##
## Reuses the unchanged craft scene, tuning, camera rig, palette, sky and drizzle.
## It writes no save file and changes no shared project settings, so the usual
## story startup and the story saves are untouched.

const Course = preload("res://rink/rink_course.gd")
const Timing = preload("res://rink/rink_timing.gd")
const Builder = preload("res://rink/rink_builder.gd")
const Hud = preload("res://rink/rink_hud.gd")
const Weather = preload("res://rink/rink_weather.gd")
const Story = preload("res://rink/rink_story.gd")
const Overcast = preload("res://scripts/overcast_resources.gd")

const ENTRY_TEXT := "HEM LOOP · DEPOT YARD\nThe freight crew's old turning loop. On wet evenings they race it alone, against the chalkboard.\n\nW  or  Enter   Race the rink\nC   Crew run · Tess is at the Hem\n\nW/S thrust · A/D steer · Shift Drive · Space Hop\nR grid · Esc pause"
const PAUSE_TEXT := "PAUSED\n\nEsc   resume\nR   back to the grid\nT   time trial\nC   crew run"
const HINT_TEXT := "W/S thrust · A/D steer · hold Shift Drive · Space Hop (Spread) · R grid · Esc pause"

@onready var craft: CraftController = $Craft
@onready var camera_rig: StableCameraRig = $CameraRig
@onready var builder: Builder = $Course

var course := Course.new()
var timing := Timing.new()
var hud: Hud
var weather: Weather
var story: Story
var mode := "ENTRY"
var progress_s := 0.0
var lateral := 0.0
var piece := ""
var sim_time := 0.0
var _prev := Vector2.ZERO
var _wrong_way := 0.0
var _hint_cleared := false
var _was_paused := false
var events: Array[Dictionary] = []


func _enter_tree() -> void:
	course.load_course()
	var grid := course.grid_transform(1.3)
	($Craft as Node3D).transform = grid


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	process_physics_priority = 100
	builder.build(course)
	builder.exclude_hard_geometry_from_support(craft)
	_environment()
	weather = Weather.new()
	weather.name = "Drizzle"
	add_child(weather)
	weather.configure(camera_rig.get_node("Camera"), builder.static_meshes(), Vector3(110, 0, -80))
	hud = Hud.new()
	hud.name = "HUD"
	add_child(hud)
	hud.map.configure(course)
	timing.configure(course.gates)
	timing.lap_started.connect(_on_lap_started)
	timing.gate_passed.connect(_on_gate_passed)
	timing.lap_completed.connect(_on_lap_completed)
	timing.lap_refused.connect(_on_lap_refused)
	story = Story.new()
	story.name = "CrewRun"
	add_child(story)
	story.configure(self)
	craft.reset_performed.connect(_on_reset)
	_prev = _flat(craft.global_position)
	var proj := course.project(_prev)
	progress_s = float(proj.s)
	hud.entry_body.text = ENTRY_TEXT
	hud.entry.visible = true
	hud.hint.text = HINT_TEXT
	_refresh_hud()
	print("HEM_LOOP_READY length=%.1f gates=%d" % [course.length, course.gates.size()])


func _environment() -> void:
	var env := Environment.new()
	env.background_mode = Environment.BG_SKY
	env.sky = Overcast.sky()
	env.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	var light: Dictionary = Overcast.config().lighting
	env.ambient_light_color = Overcast.rgb(light.ambient_color)
	env.ambient_light_energy = float(light.ambient_energy)
	env.tonemap_mode = Environment.TONE_MAPPER_FILMIC
	($WorldEnvironment as WorldEnvironment).environment = env
	var sun := $Sun as DirectionalLight3D
	sun.light_color = Overcast.rgb(light.sun_color)
	sun.light_energy = float(light.sun_energy)
	sun.shadow_opacity = float(light.shadow_opacity)
	sun.light_angular_distance = float(light.sun_angular_distance)


static func _flat(v: Vector3) -> Vector2:
	return Vector2(v.x, v.z)


func log_event(kind: String, extra: Dictionary = {}) -> void:
	var row := {"t": snappedf(sim_time, 0.001), "event": kind, "mode": mode}
	row.merge(extra, true)
	events.append(row)
	if events.size() > 600:
		events.pop_front()


# --- modes ---------------------------------------------------------------------

func start_mode(next: String) -> void:
	var previous := mode
	mode = next
	hud.entry.visible = false
	timing.abort("mode")
	if next == "CREW":
		story.begin()
	else:
		story.end()
	if previous != "ENTRY" or next == "CREW":
		_back_to_grid("mode")
	log_event("mode", {"from": previous, "to": next})
	_refresh_hud()


func _back_to_grid(reason: String) -> void:
	craft.reset_craft(reason)


func _unhandled_input(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed and not event.echo:
		var key := (event as InputEventKey).physical_keycode
		if mode == "ENTRY":
			if key in [KEY_ENTER, KEY_KP_ENTER]:
				start_mode("RACE")
				get_viewport().set_input_as_handled()
			elif key == KEY_C:
				start_mode("CREW")
				get_viewport().set_input_as_handled()
			return
		if get_tree().paused:
			if key == KEY_T:
				get_tree().paused = false
				start_mode("RACE")
			elif key == KEY_C:
				get_tree().paused = false
				start_mode("CREW")
	elif event is InputEventJoypadButton and event.pressed and mode == "ENTRY":
		var button := (event as InputEventJoypadButton).button_index
		if button == JOY_BUTTON_START:
			start_mode("RACE")
		elif button == JOY_BUTTON_BACK:
			start_mode("CREW")


func _on_reset(_count: int, reason: String) -> void:
	timing.abort(reason)
	_prev = _flat(craft.global_position)
	progress_s = float(course.project(_prev).s)
	_wrong_way = 0.0
	weather.restart()
	if story != null:
		story.on_reset(reason)
	log_event("reset", {"reason": reason})


# --- simulation observer --------------------------------------------------------

func _physics_process(delta: float) -> void:
	if get_tree().paused:
		return
	sim_time += delta
	if mode == "ENTRY" and Input.get_action_strength("throttle") > 0.2:
		start_mode("RACE")
	var curr := _flat(craft.global_position)
	if mode != "ENTRY":
		timing.step(_prev, curr, delta)
	var proj := course.project(curr, progress_s)
	if float(proj.distance) > 30.0:
		proj = course.project(curr)
	progress_s = float(proj.s)
	lateral = float(proj.lateral)
	piece = String(proj.id)
	_update_wrong_way(delta)
	if mode == "CREW":
		story.physics(delta, curr, proj)
	_prev = curr


func _update_wrong_way(delta: float) -> void:
	var pose := course.pose_at(progress_s)
	var along := _flat(craft.velocity).dot(pose.f)
	if along < -3.0:
		_wrong_way += delta
	else:
		_wrong_way = maxf(0.0, _wrong_way - delta * 2.0)
	if _wrong_way > 1.0 and mode != "ENTRY":
		hud.flash("WRONG WAY", Hud.AMBER, 0.4)


func _process(_delta: float) -> void:
	var paused := get_tree().paused
	if paused != _was_paused:
		_was_paused = paused
		hud.pause_panel.visible = paused and mode != "ENTRY"
		hud.pause_body.text = PAUSE_TEXT
	hud.tick(sim_time)
	_refresh_hud()


func _refresh_hud() -> void:
	if hud == null:
		return
	var tel := craft.telemetry()
	hud.set_form("%s   %d m/s" % [String(tel.regime), int(round(float(tel.speed)))])
	hud.map.set_craft(_flat(craft.global_position), _flat(-craft.global_transform.basis.z))
	if story != null:
		hud.map.marks = story.map_marks()
	var lines := "Last %s    Best %s" % [
		Timing.format_time(timing.laps[-1].time) if not timing.laps.is_empty() else "-:--.--",
		Timing.format_time(timing.best_time)]
	lines += "\nValid laps %d" % timing.laps.size()
	if not timing.refused.is_empty():
		lines += "  ·  not counted %d" % timing.refused.size()
	var title := "HEM LOOP · TIME TRIAL"
	if mode == "CREW":
		title = "HEM LOOP · CREW RUN"
		lines = story.status_line() + "\n" + lines
	var clock_text := Timing.format_time(timing.current_time()) if timing.lap_active else "0:00.00"
	hud.set_lap(title, clock_text, lines)
	if not timing.lap_active and mode != "ENTRY" and not hud.story_visible():
		hud.hint.text = "Clock starts at the line · " + HINT_TEXT
	elif _hint_cleared:
		hud.hint.text = ""
	else:
		hud.hint.text = HINT_TEXT


# --- timing events ----------------------------------------------------------------

func _on_lap_started(_time: float) -> void:
	log_event("lap_started")
	if mode == "CREW":
		story.on_line()


func _gate_name(index: int) -> String:
	return String(course.gates[index].name)


func _on_gate_passed(index: int, split: float, delta: float, has_delta: bool) -> void:
	log_event("gate", {"gate": course.gates[index].id, "split": snappedf(split, 0.001)})
	if has_delta:
		hud.flash("%s  %s" % [_gate_name(index), Timing.format_delta(delta)], Hud.GOOD if delta <= 0.0 else Hud.BAD, 2.0)
	else:
		hud.flash("%s  %s" % [_gate_name(index), Timing.format_time(split)], Hud.PALE, 1.6)


func _on_lap_completed(record: Dictionary) -> void:
	log_event("lap", {"lap": record.lap, "time": snappedf(record.time, 0.001), "best": record.best})
	_hint_cleared = true
	var sectors := []
	for i in record.sectors.size():
		sectors.append("%s%.2f" % ["★" if record.sector_best[i] and record.had_best else "", record.sectors[i]])
	var head := "LAP %d   %s" % [record.lap, Timing.format_time(record.time)]
	var tint := Hud.PALE
	if record.best and record.had_best:
		head += "   NEW BEST  " + Timing.format_delta(record.delta)
		tint = Hud.GOOD
	elif record.best:
		head += "   first valid lap"
		tint = Hud.GOOD
	else:
		head += "   " + Timing.format_delta(record.delta)
		tint = Hud.BAD if record.delta > 0.0 else Hud.GOOD
	hud.show_result(head + "\nYard %s · Hem %s · Crane & Dock %s · Gate %s" % sectors, tint, 5.0)
	_update_board()


func _on_lap_refused(missed: Array, passed_any: bool) -> void:
	log_event("lap_refused", {"missed": missed.map(func(i): return course.gates[i].id), "passed_any": passed_any})
	if passed_any:
		var names := missed.map(func(i): return _gate_name(i))
		hud.show_result("Lap not counted — missed %s" % ", ".join(names), Hud.BAD, 4.0)
	else:
		hud.flash("Clock restarted at the line", Hud.AMBER, 1.8)


func _update_board() -> void:
	var text := "HEM LOOP · TONIGHT\nBest  %s" % Timing.format_time(timing.best_time)
	var recent := timing.laps.slice(maxi(0, timing.laps.size() - 3))
	recent.reverse()
	for lap in recent:
		text += "\nLap %d  %s" % [lap.lap, Timing.format_time(lap.time)]
	builder.set_chalkboard(text)
