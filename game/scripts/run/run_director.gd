extends Node

const BrrrSeed = preload("res://scripts/run/brrr_seed.gd")
const RunHud = preload("res://scripts/run/run_hud.gd")
const RunMapOverlay = preload("res://scripts/run/run_map_overlay.gd")

enum RunState {
	FREE_ROAM,
	COUNTDOWN,
	LIVE,
	RESULTS,
}

const POST_MOVE_PHYSICS_PRIORITY := 200
const CRAFT_HEIGHT_OFFSET_M := 1.65
const COUNTDOWN_BEAT_SECONDS := 0.6
const COUNTDOWN_BEATS := 3

var state: int = RunState.FREE_ROAM
var gate: P1AWorldGate
var craft: CraftController
var run_start_transform := Transform3D.IDENTITY
var finish_center_xz := Vector2.ZERO
var finish_radius_m := 0.0

var run_time_s := 0.0
var brrr := 0.0
var streak_s := 0.0
var longest_streak_s := 0.0
var drive_seconds := 0.0
var peak_speed := 0.0
var peak_split_degrees := 0.0
var previous_craft_xz := Vector2.ZERO
var last_post_move_craft_xz := Vector2.ZERO

var best_time_s := INF
var best_brrr := 0.0
var last_result: Dictionary = {}
var attempt_serial := 0
var manual_retry_count := 0
var fall_restart_count := 0
var reset_signal_count := 0
var last_reset_signal_reason := ""

var _initialized := false
var _countdown_remaining_s := 0.0
var _hud: CanvasLayer
var _map_overlay: Control


func _ready() -> void:
	# Input remains available while paused so R is still owned by Run. All timed
	# work below explicitly stops while the SceneTree is paused.
	process_mode = Node.PROCESS_MODE_ALWAYS
	process_physics_priority = POST_MOVE_PHYSICS_PRIORITY
	_initialize_after_one_frame()


func _initialize_after_one_frame() -> void:
	await get_tree().process_frame
	if not is_inside_tree():
		return
	gate = get_node_or_null("../DistrictZeroP1A") as P1AWorldGate
	if gate == null or gate.data == null or gate.data.manifest.is_empty():
		push_error("Run v0 requires the initialized District Zero R7 subtree.")
		return
	craft = gate.craft
	if craft == null:
		push_error("Run v0 could not resolve the frozen R7 craft.")
		return
	if not _resolve_run_geometry():
		return
	craft.reset_performed.connect(_on_craft_reset)
	_hud = RunHud.new()
	add_child(_hud)
	_map_overlay = RunMapOverlay.new()
	gate.map.add_child(_map_overlay)
	_map_overlay.configure(finish_center_xz, "RLY")
	_initialized = true
	start_attempt()


func _unhandled_input(event: InputEvent) -> void:
	if not _initialized:
		return
	if event.is_action_pressed("reset"):
		manual_retry_count += 1
		start_attempt()
		get_viewport().set_input_as_handled()
		return
	if (
		state == RunState.RESULTS
		and event is InputEventKey
		and event.pressed
		and not event.echo
		and (event.physical_keycode == KEY_F or event.keycode == KEY_F)
	):
		enter_free_roam()
		get_viewport().set_input_as_handled()


func _physics_process(delta: float) -> void:
	if not _initialized or get_tree().paused:
		return
	if state == RunState.COUNTDOWN:
		_tick_countdown(delta)
	elif state == RunState.LIVE:
		_tick_live(delta)


func start_attempt() -> void:
	if not _initialized:
		return
	# Every manually begun attempt reclaims transient ownership before R7 resets.
	gate.active_tour_id = ""
	var no_routes: Array[String] = []
	gate.map.set_highlighted_routes(no_routes)
	gate.menu_panel.visible = false
	craft.set_spawn_transform(run_start_transform)
	craft.reset_craft("run_retry")
	gate.camera_rig.snap_to_target()
	attempt_serial += 1
	_begin_countdown()


func enter_free_roam() -> void:
	if not _initialized:
		return
	state = RunState.FREE_ROAM
	craft.set_physics_process(true)
	_clear_attempt_metrics()
	_hud.hide_all()


func state_name() -> String:
	return RunState.keys()[state]


func _resolve_run_geometry() -> bool:
	var pads: Dictionary = gate.data.manifest.get("destination_pads", {})
	var qry: Dictionary = pads.get("QRY", {})
	var rly: Dictionary = pads.get("RLY", {})
	var a0: Dictionary = gate.data.routes.get("A0", {})
	var points: Array = a0.get("points_xz_m", [])
	if qry.is_empty() or rly.is_empty() or points.size() < 2:
		push_error("Run v0 requires QRY, RLY, and the first two frozen A0 bake points.")
		return false
	var qry_xz := P1AWorldData.xz(qry.center_xz_m)
	var first := P1AWorldData.xz(points[0])
	var second := P1AWorldData.xz(points[1])
	var tangent := (second - first).normalized()
	if tangent.length_squared() < 0.999:
		push_error("Run v0 could not derive a finite A0 initial tangent.")
		return false
	var yaw := atan2(-tangent.x, -tangent.y)
	var start_position := Vector3(
		qry_xz.x,
		gate.data.terrain_height_at(qry_xz.x, qry_xz.y) + CRAFT_HEIGHT_OFFSET_M,
		qry_xz.y
	)
	run_start_transform = Transform3D(
		Basis.IDENTITY.rotated(Vector3.UP, yaw),
		start_position
	)
	finish_center_xz = P1AWorldData.xz(rly.center_xz_m)
	finish_radius_m = float(rly.outer_blend_radius_m)
	return finish_radius_m > 0.0


func _begin_countdown() -> void:
	craft.set_physics_process(false)
	_clear_attempt_metrics()
	state = RunState.COUNTDOWN
	_countdown_remaining_s = COUNTDOWN_BEAT_SECONDS * float(COUNTDOWN_BEATS)
	previous_craft_xz = _craft_xz()
	last_post_move_craft_xz = previous_craft_xz
	_hud.show_countdown(str(COUNTDOWN_BEATS))


func _tick_countdown(delta: float) -> void:
	_countdown_remaining_s = maxf(0.0, _countdown_remaining_s - delta)
	if _countdown_remaining_s > 0.0:
		var beat := clampi(
			ceili(_countdown_remaining_s / COUNTDOWN_BEAT_SECONDS),
			1,
			COUNTDOWN_BEATS
		)
		_hud.show_countdown(str(beat))
		return
	# Enabling at priority 200 means the craft's priority-0 callback cannot run
	# until the next physics frame; the first LIVE delta is therefore post-move.
	previous_craft_xz = _craft_xz()
	last_post_move_craft_xz = previous_craft_xz
	state = RunState.LIVE
	craft.set_physics_process(true)
	_hud.show_countdown("GO")


func _tick_live(delta: float) -> void:
	var current_xz := _craft_xz()
	last_post_move_craft_xz = current_xz
	# R7 will perform its own reset at the start of the next craft tick. Do not
	# score or finish a below-boundary segment in the interim.
	if craft.global_position.y < craft.tuning.fall_reset_y:
		previous_craft_xz = current_xz
		return
	run_time_s += delta
	var sample: Dictionary = BrrrSeed.step(
		craft.velocity,
		-craft.global_basis.z,
		craft.regime_name() == "DRIVE",
		delta,
		brrr,
		streak_s
	)
	brrr = float(sample.brrr)
	streak_s = float(sample.streak_s)
	longest_streak_s = maxf(longest_streak_s, streak_s)
	peak_speed = maxf(peak_speed, float(sample.speed))
	peak_split_degrees = maxf(peak_split_degrees, float(sample.split_degrees))
	if craft.regime_name() == "DRIVE":
		drive_seconds += delta
	if segment_intersects_disc(
		previous_craft_xz,
		current_xz,
		finish_center_xz,
		finish_radius_m
	):
		_finish_attempt()
		return
	previous_craft_xz = current_xz
	_hud.show_live(run_time_s, brrr, streak_s)


func _finish_attempt() -> void:
	craft.set_physics_process(false)
	state = RunState.RESULTS
	best_time_s = minf(best_time_s, run_time_s)
	best_brrr = maxf(best_brrr, brrr)
	last_result = {
		"time_s": run_time_s,
		"best_time_s": best_time_s,
		"brrr": brrr,
		"best_brrr": best_brrr,
		"drive_seconds": drive_seconds,
		"peak_speed": peak_speed,
		"peak_split_degrees": peak_split_degrees,
		"longest_streak_s": longest_streak_s,
		"impacts": craft.impact_count,
	}
	_hud.show_results(last_result)


func _on_craft_reset(_count: int, reason: String) -> void:
	reset_signal_count += 1
	last_reset_signal_reason = reason
	if reason == "run_retry":
		return
	if reason == "diagnostic":
		enter_free_roam()
		return
	if reason.begins_with("fell below") and state == RunState.LIVE:
		# R7 has already teleported, zeroed velocity, restored Spread, locked held
		# input, and emitted this signal. A second reset here would be incorrect.
		fall_restart_count += 1
		attempt_serial += 1
		gate.camera_rig.snap_to_target()
		_begin_countdown()


func _clear_attempt_metrics() -> void:
	run_time_s = 0.0
	brrr = 0.0
	streak_s = 0.0
	longest_streak_s = 0.0
	drive_seconds = 0.0
	peak_speed = 0.0
	peak_split_degrees = 0.0
	last_result = {}


func _craft_xz() -> Vector2:
	return Vector2(craft.global_position.x, craft.global_position.z)


static func segment_intersects_disc(
	segment_start: Vector2,
	segment_end: Vector2,
	disc_center: Vector2,
	disc_radius: float
) -> bool:
	if disc_radius < 0.0:
		return false
	var segment := segment_end - segment_start
	var length_squared := segment.length_squared()
	if length_squared <= 0.000000000001:
		return segment_start.distance_squared_to(disc_center) <= disc_radius * disc_radius
	var projection := clampf(
		(disc_center - segment_start).dot(segment) / length_squared,
		0.0,
		1.0
	)
	var closest := segment_start + segment * projection
	return closest.distance_squared_to(disc_center) <= disc_radius * disc_radius
