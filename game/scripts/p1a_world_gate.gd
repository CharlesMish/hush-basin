class_name P1AWorldGate
extends Node3D

const BUILD_LABEL := "DISTRICT ZERO · QUIET SURFACES v1"
const DIAGNOSTIC_LABEL := "QUIET SURFACES · LIGHT DRIZZLE · OWNER REVIEW"

@onready var craft: CraftController = $Craft
@onready var camera_rig: StableCameraRig = $CameraRig
@onready var world: P1AWorldBuilder = $World
@onready var telemetry: P1ATelemetry = $Telemetry
@onready var menu_panel: PanelContainer = $UI/MenuPanel
@onready var menu_label: Label = $UI/MenuPanel/MenuContent/MenuLabel
@onready var status_label: Label = $UI/StatusPanel/Status
@onready var debug_panel: PanelContainer = $UI/DebugPanel
@onready var debug_label: Label = $UI/DebugPanel/Debug
@onready var map: P1AMap = $UI/MapPanel/Map
@onready var diagnostic_identity_panel: PanelContainer = $UI/DiagnosticIdentityPanel
@onready var pause_panel: PanelContainer = $UI/PausePanel

var data := P1AWorldData.new()
var selection_index := 1
var active_tour_id := ""
var debug_visible := false
var _last_transform := Transform3D.IDENTITY
var _explicit_reset_in_progress := false


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	if not data.load_all():
		get_tree().quit(2)
		return
	world.build(data)
	preload("res://scripts/world_polish_presentation.gd").new().environment(self, data)
	preload("res://scripts/overcast_resources.gd").environment(self)
	var weather := preload("res://scripts/overcast_weather.gd").new()
	weather.name = "WarmOvercastWeather"
	add_child(weather)
	weather.configure(self)
	world.exclude_hard_geometry_from_support(craft)
	telemetry.configure(data, craft)
	map.configure(data, craft)
	craft.reset_performed.connect(_on_craft_reset)
	_last_transform = craft.global_transform
	menu_panel.visible = false
	debug_panel.visible = false
	pause_panel.visible = false
	(diagnostic_identity_panel.get_node("Label") as Label).text = DIAGNOSTIC_LABEL
	_update_menu()
	_update_status()
	print("P1A_RUNTIME_READY authority=%s routes=%d solids=%d" % [P1AWorldData.AUTHORITY_VERSION, data.routes.size(), data.solids.size()])


func _process(_delta: float) -> void:
	if data == null or craft == null:
		return
	pause_panel.visible = get_tree().paused
	_update_status()
	_last_transform = craft.global_transform


func _unhandled_input(event: InputEvent) -> void:
	if event.is_action_pressed("diagnostic_menu"):
		menu_panel.visible = not menu_panel.visible
		get_viewport().set_input_as_handled()
	elif event.is_action_pressed("debug_overlay"):
		debug_visible = not debug_visible
		debug_panel.visible = debug_visible
		get_viewport().set_input_as_handled()
	elif menu_panel.visible and event.is_action_pressed("diagnostic_prev"):
		_change_selection(-1)
		get_viewport().set_input_as_handled()
	elif menu_panel.visible and event.is_action_pressed("diagnostic_next"):
		_change_selection(1)
		get_viewport().set_input_as_handled()
	elif menu_panel.visible and event.is_action_pressed("diagnostic_spawn"):
		spawn_selected_tour()
		get_viewport().set_input_as_handled()


func _change_selection(direction: int) -> void:
	var order: Array = data.diagnostic.selection_order
	var prior := String(order[selection_index])
	selection_index = posmod(selection_index + direction, order.size())
	var selected := String(order[selection_index])
	telemetry.emit_selection(selected, prior)
	_update_menu()


func spawn_selected_tour() -> void:
	var order: Array = data.diagnostic.selection_order
	var tour_id := String(order[selection_index])
	var tour := _tour_by_id(tour_id)
	if tour.is_empty():
		return
	var spawn := _spawn_transform(tour.spawn_transform)
	var before := craft.global_transform
	craft.set_spawn_transform(spawn)
	craft.reset_craft("diagnostic")
	_apply_initial_mode(String(tour.initial_mode))
	active_tour_id = tour_id
	map.set_highlighted_routes(_routes_for_tour(tour))
	telemetry.emit_reset("DIAGNOSTIC", before, spawn)
	telemetry.emit_spawn(tour_id, String(tour.get("spawn_id", tour_id)), spawn)
	camera_rig.snap_to_target()
	menu_panel.visible = false


func reset_active_segment(reason: String = "MANUAL") -> void:
	var before := craft.global_transform
	_explicit_reset_in_progress = true
	craft.reset_craft(reason.to_lower())
	_explicit_reset_in_progress = false
	var tour := _tour_by_id(active_tour_id)
	if not tour.is_empty():
		_apply_initial_mode(String(tour.initial_mode))
	telemetry.emit_reset(reason, before, craft.global_transform)
	camera_rig.snap_to_target()


func _on_craft_reset(_count: int, reason: String) -> void:
	# Diagnostic resets are emitted by spawn_selected_tour with the exact tour payload.
	if reason == "diagnostic" or _explicit_reset_in_progress:
		return
	var normalized := "FALL" if reason.begins_with("fell below") else "MANUAL"
	var tour := _tour_by_id(active_tour_id)
	if not tour.is_empty():
		_apply_initial_mode(String(tour.initial_mode))
	telemetry.emit_reset(normalized, _last_transform, craft.global_transform)


func _apply_initial_mode(mode: String) -> void:
	craft.fold_amount = 1.0 if mode == "DRIVE" else 0.0


func _update_menu() -> void:
	if data.diagnostic.is_empty():
		return
	var order: Array = data.diagnostic.selection_order
	var lines := PackedStringArray(["DIAGNOSTIC SEGMENTS", "[ / ] select  ·  ENTER start  ·  TAB close", ""])
	for index in order.size():
		var tour := _tour_by_id(String(order[index]))
		var marker := "▶" if index == selection_index else " "
		lines.append("%s %s" % [marker, String(tour.display_label)])
	menu_label.text = "\n".join(lines)
	var selected_tour := _tour_by_id(String(order[selection_index]))
	map.set_highlighted_routes(_routes_for_tour(selected_tour))


func _update_status() -> void:
	if craft == null:
		return
	var sample := craft.telemetry()
	status_label.text = "%s\n%s  //  %5.1f m/s  //  %s\nW/S thrust & brake  ·  A/D steer  ·  SHIFT Drive  ·  SPACE Hop\nTAB routes  ·  R reset  ·  F1 details  ·  ESC pause" % [
		BUILD_LABEL,
		String(sample.regime),
		float(sample.tangential_speed),
		"PAUSED" if get_tree().paused else "LIVE",
	]
	if debug_visible:
		var point := Vector2(craft.global_position.x, craft.global_position.z)
		debug_label.text = "tick %d\npos  %.2f  %.2f  %.2f\nclass  %s\nprobe  %d  height %.3f\nroute  %s\nevents  %d  dropped %d" % [
			telemetry.physics_tick,
			craft.global_position.x, craft.global_position.y, craft.global_position.z,
			telemetry.classify(point),
			int(sample.probe_hits), float(sample.measured_height),
			telemetry.current_route_id if not telemetry.current_route_id.is_empty() else "—",
			telemetry.events.size(), telemetry.dropped_count,
		]


func _routes_for_tour(tour: Dictionary) -> Array[String]:
	var route_ids: Array[String] = []
	var coverage = tour.get("covers_for_human_prompting_only")
	if coverage is Array:
		for value in coverage:
			var route_id := String(value)
			if data.routes.has(route_id):
				route_ids.append(route_id)
	var spawn_record: Dictionary = tour.get("spawn_transform", {})
	var spawn_source: Dictionary = spawn_record.get("source", {})
	var source_route := String(spawn_source.get("route", spawn_source.get("toward_route", "")))
	if data.routes.has(source_route) and source_route not in route_ids:
		route_ids.append(source_route)
	return route_ids


func _tour_by_id(tour_id: String) -> Dictionary:
	for value in data.diagnostic.get("tours", []):
		var tour: Dictionary = value
		if String(tour.id) == tour_id:
			return tour
	return {}


static func _spawn_transform(record: Dictionary) -> Transform3D:
	var position: Array = record.position_xyz_m
	var transform := Transform3D(Basis.IDENTITY.rotated(Vector3.UP, float(record.yaw_rad)), Vector3(float(position[0]), float(position[1]), float(position[2])))
	return transform
