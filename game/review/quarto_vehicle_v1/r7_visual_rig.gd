extends Node3D

const SPREAD_ENERGY := Color(1.0, 0.58, 0.16, 1.0)
const DRIVE_ENERGY := Color(0.2, 0.95, 1.0, 1.0)
const CAUTION_ENERGY := Color(1.0, 0.72, 0.12, 1.0)
const STRIKE_ENERGY := Color(1.0, 0.12, 0.08, 1.0)

const FRONT_BOOK_WINDOW := Vector2(0.04, 0.26)
const FRONT_YAW_WINDOW := Vector2(0.26, 0.58)
const FRONT_HAUNCH_WINDOW := Vector2(0.58, 0.80)
const REAR_BOOK_WINDOW := Vector2(0.08, 0.34)
const REAR_YAW_WINDOW := Vector2(0.34, 0.66)
const REAR_HAUNCH_WINDOW := Vector2(0.66, 0.86)
const PROPULSION_WINDOW := Vector2(0.88, 1.00)

const FRONT_BOOK_INWARD := 0.34
const FRONT_SOCKET_INWARD := 0.080
const REAR_BOOK_INWARD := 0.26
const REAR_SOCKET_INWARD := 0.096
const PROPULSION_STROKE := 0.51

var form_amount: float = 0.0
var _energy_state: String = "CLEAR"
var _energy_materials: Array[StandardMaterial3D] = []
var _propulsion_materials: Array[StandardMaterial3D] = []
var _materials_ready := false


func _ready() -> void:
	_prepare_energy_materials()
	set_form_amount(form_amount)


func set_form_amount(value: float) -> void:
	form_amount = clampf(value, 0.0, 1.0)
	_pose_front(-1.0, "FrontPortRig")
	_pose_front(1.0, "FrontStarboardRig")
	_pose_rear(-1.0, "RearPortRig")
	_pose_rear(1.0, "RearStarboardRig")

	var propulsion_t := _stage(PROPULSION_WINDOW.x, PROPULSION_WINDOW.y, form_amount)
	var moving_can := get_node_or_null("CentralStructure/DriveBay/MovingCan") as Node3D
	if moving_can != null:
		moving_can.position = Vector3(0.0, 0.0, 0.47 + PROPULSION_STROKE * propulsion_t)
	_apply_energy()


func set_energy_state(state: String) -> void:
	_energy_state = state
	_prepare_energy_materials()
	_apply_energy()


func _pose_front(side: float, rig_name: String) -> void:
	var rig := get_node_or_null(rig_name) as Node3D
	if rig == null:
		return
	var book := rig.get_node("BookPivot") as Node3D
	var yaw := book.get_node("YawPivot") as Node3D
	var haunch := yaw.get_node("HaunchPivot") as Node3D
	var socket := haunch.get_node("SocketSlide") as Node3D
	var book_t := _stage(FRONT_BOOK_WINDOW.x, FRONT_BOOK_WINDOW.y, form_amount)
	var yaw_t := _stage(FRONT_YAW_WINDOW.x, FRONT_YAW_WINDOW.y, form_amount)
	var haunch_t := _stage(FRONT_HAUNCH_WINDOW.x, FRONT_HAUNCH_WINDOW.y, form_amount)
	var socket_t := _stage(0.70, FRONT_HAUNCH_WINDOW.y, form_amount)
	book.position = Vector3(-side * FRONT_BOOK_INWARD * book_t, 0.0, 0.0)
	book.rotation = Vector3(deg_to_rad(18.0 * book_t), 0.0, 0.0)
	yaw.position = Vector3(0.0, 0.035 * yaw_t, 0.10 * yaw_t)
	yaw.rotation = Vector3(0.0, deg_to_rad(-side * 64.0 * yaw_t), 0.0)
	haunch.rotation = Vector3(deg_to_rad(70.0 * haunch_t), 0.0, 0.0)
	socket.position = Vector3(-side * FRONT_SOCKET_INWARD * socket_t, 0.0, 0.0)


func _pose_rear(side: float, rig_name: String) -> void:
	var rig := get_node_or_null(rig_name) as Node3D
	if rig == null:
		return
	var book := rig.get_node("BookPivot") as Node3D
	var yaw := book.get_node("YawPivot") as Node3D
	var haunch := yaw.get_node("HaunchPivot") as Node3D
	var socket := haunch.get_node("SocketSlide") as Node3D
	var book_t := _stage(REAR_BOOK_WINDOW.x, REAR_BOOK_WINDOW.y, form_amount)
	var yaw_t := _stage(REAR_YAW_WINDOW.x, REAR_YAW_WINDOW.y, form_amount)
	var haunch_t := _stage(REAR_HAUNCH_WINDOW.x, REAR_HAUNCH_WINDOW.y, form_amount)
	var socket_t := _stage(0.76, REAR_HAUNCH_WINDOW.y, form_amount)
	book.position = Vector3(-side * REAR_BOOK_INWARD * book_t, 0.0, 0.0)
	book.rotation = Vector3(deg_to_rad(-24.0 * book_t), 0.0, 0.0)
	yaw.position = Vector3(0.0, 0.045 * yaw_t, 0.05 * yaw_t)
	yaw.rotation = Vector3(0.0, deg_to_rad(-side * 72.0 * yaw_t), 0.0)
	haunch.rotation = Vector3(deg_to_rad(-70.0 * haunch_t), 0.0, 0.0)
	socket.position = Vector3(-side * REAR_SOCKET_INWARD * socket_t, 0.0, 0.0)


func _stage(start: float, finish: float, value: float) -> float:
	var t := clampf((value - start) / maxf(finish - start, 0.0001), 0.0, 1.0)
	return t * t * (3.0 - 2.0 * t)


func _prepare_energy_materials() -> void:
	if _materials_ready:
		return
	for path in [
		"CentralStructure/EnergyCore",
		"CentralStructure/DriveBay/FixedCore",
	]:
		var mesh := get_node_or_null(path) as MeshInstance3D
		if mesh == null:
			continue
		var original := mesh.get_active_material(0)
		if original is StandardMaterial3D:
			var material := (original as StandardMaterial3D).duplicate() as StandardMaterial3D
			mesh.material_override = material
			_energy_materials.append(material)
	for path in [
		"CentralStructure/DriveBay/MovingCan/NozzleRing",
	]:
		var mesh := get_node_or_null(path) as MeshInstance3D
		if mesh == null:
			continue
		var original := mesh.get_active_material(0)
		if original is StandardMaterial3D:
			var material := (original as StandardMaterial3D).duplicate() as StandardMaterial3D
			mesh.material_override = material
			_propulsion_materials.append(material)
	_materials_ready = true


func _apply_energy() -> void:
	_prepare_energy_materials()
	var color := SPREAD_ENERGY.lerp(DRIVE_ENERGY, form_amount)
	if _energy_state == "CAUTION":
		color = CAUTION_ENERGY
	elif _energy_state == "STRIKE":
		color = STRIKE_ENERGY
	for material in _energy_materials:
		material.albedo_color = color
		material.emission = color * 0.58
		material.emission_energy_multiplier = lerpf(0.7, 1.35, form_amount)
	var propulsion_t := _stage(PROPULSION_WINDOW.x, PROPULSION_WINDOW.y, form_amount)
	for material in _propulsion_materials:
		material.albedo_color = color.lerp(Color.WHITE, 0.18)
		material.emission = color * 0.82
		material.emission_energy_multiplier = lerpf(0.22, 1.45, propulsion_t)
