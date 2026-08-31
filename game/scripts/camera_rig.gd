class_name StableCameraRig
extends Node3D

const OBSTRUCTION_COLLISION_MASK := 1
const OBSTRUCTION_CLEARANCE_M := 0.45
const OBSTRUCTION_MIN_DISTANCE_M := 0.35

@export var target_path: NodePath
@export var tuning: CraftTuning

@onready var _target: CraftController = get_node(target_path) as CraftController
@onready var _camera: Camera3D = $Camera
var _last_reset_count: int = -1


func _ready() -> void:
	if _target == null or tuning == null:
		push_error("StableCameraRig requires a craft target and tuning resource.")
		return
	snap_to_target()


func _physics_process(delta: float) -> void:
	if _target == null or tuning == null:
		return
	if _target.reset_count != _last_reset_count:
		snap_to_target()
		return
	var frame := _desired_frame()
	var response := 1.0 - exp(-tuning.camera_response * delta)
	var smoothed_position := global_position.lerp(frame.position, response)
	global_position = _resolve_obstructed_position(frame.pivot, smoothed_position)
	look_at(frame.look_target, Vector3.UP)
	var target_fov := tuning.spread_camera_fov + tuning.drive_fov_increase * _target.fold_amount
	_camera.fov = lerpf(_camera.fov, target_fov, response)


func snap_to_target() -> void:
	var frame := _desired_frame()
	global_position = _resolve_obstructed_position(frame.pivot, frame.position)
	look_at(frame.look_target, Vector3.UP)
	_camera.fov = tuning.spread_camera_fov + tuning.drive_fov_increase * _target.fold_amount
	_last_reset_count = _target.reset_count
	reset_physics_interpolation()


func _desired_frame() -> Dictionary:
	var forward := -_target.global_transform.basis.z
	forward.y = 0.0
	forward = MotionMath.safe_normalize(forward, Vector3.FORWARD)
	var camera_position := _target.global_position
	camera_position -= forward * tuning.camera_distance
	camera_position += Vector3.UP * tuning.camera_height
	var look_target := _target.global_position
	look_target += forward * tuning.camera_look_ahead
	look_target += Vector3.UP * tuning.camera_look_height
	var pivot := _target.global_position + Vector3.UP * tuning.camera_look_height
	return {"position": camera_position, "look_target": look_target, "pivot": pivot}


func _resolve_obstructed_position(pivot: Vector3, desired_position: Vector3) -> Vector3:
	if not is_inside_tree() or get_world_3d() == null:
		return desired_position
	var offset := desired_position - pivot
	var desired_distance := offset.length()
	if desired_distance <= OBSTRUCTION_MIN_DISTANCE_M:
		return desired_position
	var query := PhysicsRayQueryParameters3D.create(pivot, desired_position)
	query.collision_mask = OBSTRUCTION_COLLISION_MASK
	query.collide_with_areas = false
	query.hit_back_faces = true
	query.hit_from_inside = true
	if _target != null:
		query.exclude = [_target.get_rid()]
	var hit := get_world_3d().direct_space_state.intersect_ray(query)
	if hit.is_empty():
		return desired_position
	var hit_position: Vector3 = hit.position
	var safe_distance := clampf(
		pivot.distance_to(hit_position) - OBSTRUCTION_CLEARANCE_M,
		OBSTRUCTION_MIN_DISTANCE_M,
		desired_distance
	)
	return pivot + offset / desired_distance * safe_distance
