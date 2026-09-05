extends SceneTree
## Native presentation checks for the versioned Quarto derivative.
## No old R7 pose signature, authority gate, or gameplay threshold is rewritten.

const EXACT_ENGINE := "4.7.1.stable.official.a13da4feb"
const SOURCE := "res://presentation/quarto_native_v1.json"
const CONTRACT := "res://tests/fixtures/quarto_vehicle_v1_contract.json"
const VISUAL := preload("res://scenes/vehicle_visual.tscn")
const EPS := 0.00001

var checks: Array[Dictionary] = []
var failures: Array[String] = []
var envelopes: Array[Dictionary] = []
var spec: Dictionary = {}
var contract: Dictionary = {}
var result_path := ""


func _initialize() -> void:
	_run.call_deferred()


func _check(id: String, passed: bool, detail: Variant = null) -> void:
	checks.append({"id": id, "pass": passed, "detail": detail})
	if not passed:
		failures.append(id)


func _run() -> void:
	var args := OS.get_cmdline_user_args()
	var at := args.find("--result")
	if at < 0 or at + 1 >= args.size():
		push_error("quarto_vehicle_v1 requires --result <new evidence path>")
		quit(2)
		return
	result_path = args[at + 1]
	if FileAccess.file_exists(result_path):
		push_error("Native Quarto evidence path already exists: " + result_path)
		quit(2)
		return
	_check("EXACT_ENGINE", _engine_identity() == EXACT_ENGINE, _engine_identity())
	if not failures.is_empty():
		_finish()
		return
	var parsed_spec: Variant = JSON.parse_string(FileAccess.get_file_as_string(SOURCE))
	var parsed_contract: Variant = JSON.parse_string(FileAccess.get_file_as_string(CONTRACT))
	_check("JSON_INPUTS", parsed_spec is Dictionary and parsed_contract is Dictionary)
	if not failures.is_empty():
		_finish()
		return
	spec = parsed_spec
	contract = parsed_contract
	var rig := VISUAL.instantiate() as VehicleVisualRig
	var other := VISUAL.instantiate() as VehicleVisualRig
	root.add_child(rig)
	root.add_child(other)
	await process_frame
	_check("PRESENTATION_ONLY_DESCENDANTS", _presentation_only(rig))
	var meshes: Array[MeshInstance3D] = []
	_collect_meshes(rig, meshes)
	_check("NONEMPTY_ACTUAL_GEOMETRY", not meshes.is_empty())
	_validate_mesh_binding(rig, meshes)
	if not failures.is_empty():
		rig.queue_free()
		other.queue_free()
		_finish()
		return
	_validate_samples(rig, meshes)
	_validate_history(rig)
	_validate_energy(rig, other)
	_validate_gameplay_adapter()
	rig.queue_free()
	other.queue_free()
	await process_frame
	_finish()


func _validate_mesh_binding(rig: Node3D, meshes: Array[MeshInstance3D]) -> void:
	var expected_count := 0
	var exact := true
	var complete := true
	for row: Dictionary in spec.nodes:
		var node := rig.get_node_or_null(String(row.path)) as Node3D
		complete = complete and node != null
		if node == null or not row.has("mesh"):
			continue
		expected_count += 1
		var instance := node as MeshInstance3D
		if instance == null or instance.mesh == null:
			exact = false
			continue
		var definition: Dictionary = spec.meshes[String(row.mesh)]
		var actual: PackedVector3Array = instance.mesh.get_faces()
		var indices: Array = definition.indices
		exact = exact and actual.size() == indices.size()
		for i in mini(actual.size(), indices.size()):
			exact = exact and actual[i].distance_to(_vector(definition.vertices[int(indices[i])])) <= EPS
		var material := instance.get_active_material(0) as StandardMaterial3D
		exact = exact and material != null
	_check("ALL_AUTHORED_NODES_EXIST", complete)
	_check("EXACT_NATIVE_MESH_INSTANCE_COUNT", meshes.size() == expected_count, {"native": meshes.size(), "authored": expected_count})
	_check("ACTUAL_TRIANGLES_MATCH_AUTHORED_SURFACES", exact)


func _validate_samples(rig: VehicleVisualRig, meshes: Array[MeshInstance3D]) -> void:
	rig.set_form_amount(0.0)
	var first_snapshot := _snapshot(rig)
	var areas := _areas(meshes)
	var local_faces := {}
	for mesh in meshes:
		local_faces[String(rig.get_path_to(mesh))] = mesh.mesh.get_faces()
	var core := rig.get_node("CentralStructure/DriveBay/FixedCore") as Node3D
	var can := rig.get_node("CentralStructure/DriveBay/MovingCan") as Node3D
	var core_initial := core.transform
	var can_initial := can.position
	var source_match := true
	var stable_material := true
	var fixed_core := true
	var late_can := true
	var positive := true
	var bilateral := true
	var within_y := true
	var rear_higher := false
	for family in ["Port", "Starboard"]:
		var rear := rig.get_node("Rear%sRig" % family) as Node3D
		var front := rig.get_node("Front%sRig" % family) as Node3D
		rear_higher = rear.position.y > front.position.y
		_check("HIGHER_REAR_STATION_" + family, rear_higher)
	for index in int(contract.sampling.steps) + 1:
		var form := float(index) / float(contract.sampling.steps)
		rig.set_form_amount(form)
		source_match = source_match and _pose_matches_source(rig, form)
		positive = positive and _positive_finite(rig)
		fixed_core = fixed_core and core.transform.is_equal_approx(core_initial)
		if form <= float(contract.can.start_form):
			late_can = late_can and can.position.is_equal_approx(can_initial)
		var current_meshes: Array[MeshInstance3D] = []
		_collect_meshes(rig, current_meshes)
		stable_material = stable_material and current_meshes.size() == meshes.size()
		var current_areas := _areas(meshes)
		for mesh in meshes:
			var path := String(rig.get_path_to(mesh))
			stable_material = stable_material and mesh.is_visible_in_tree()
			stable_material = stable_material and mesh.mesh.get_faces() == local_faces[path]
			stable_material = stable_material and absf(float(current_areas[mesh.get_instance_id()]) - float(areas[mesh.get_instance_id()])) <= EPS
		var envelope := _bounds(rig, meshes)
		envelopes.append({"form_amount": form, "min": _array(envelope.position), "max": _array(envelope.end), "size": _array(envelope.size)})
		within_y = within_y and envelope.position.y >= float(contract.bounds_m.sample_y[0]) - EPS and envelope.end.y <= float(contract.bounds_m.sample_y[1]) + EPS
		for family in ["Front", "Rear"]:
			var port_meshes: Array[MeshInstance3D] = []
			var starboard_meshes: Array[MeshInstance3D] = []
			_collect_meshes(rig.get_node(family + "PortRig"), port_meshes)
			_collect_meshes(rig.get_node(family + "StarboardRig"), starboard_meshes)
			var port := _bounds(rig, port_meshes)
			var starboard := _bounds(rig, starboard_meshes)
			bilateral = bilateral and absf(port.position.x + starboard.end.x) <= EPS and absf(port.end.x + starboard.position.x) <= EPS
			bilateral = bilateral and absf(port.position.y - starboard.position.y) <= EPS and absf(port.end.y - starboard.end.y) <= EPS
			bilateral = bilateral and absf(port.position.z - starboard.position.z) <= EPS and absf(port.end.z - starboard.end.z) <= EPS
			bilateral = bilateral and port.end.x <= starboard.position.x + EPS
	_check("201_NATIVE_POSES_MATCH_AUTHORED_LOCAL_TRANSFORMS", source_match)
	_check("CONSTANT_VISIBLE_TRIANGLES_AND_SURFACE_AREA", stable_material)
	_check("POSITIVE_UNIT_SCALES_FINITE_TRANSFORMS", positive)
	_check("FIXED_CORE_ALL_POSES", fixed_core)
	_check("CAN_STOWED_THROUGH_088", late_can)
	_check("CAN_EXACT_AFT_STROKE", can.position.distance_to(can_initial + Vector3(0, 0, float(contract.can.stroke_m))) <= EPS)
	_check("201_POSE_VERTICAL_ENVELOPE", within_y)
	_check("201_POSE_BILATERAL_SEPARATION", bilateral)
	var spread: Array = envelopes[0].size
	var drive: Array = envelopes[-1].size
	_check("SPREAD_WIDTH", float(spread[0]) >= float(contract.bounds_m.spread_width[0]) - EPS and float(spread[0]) <= float(contract.bounds_m.spread_width[1]) + EPS, spread)
	_check("DRIVE_WIDTH", float(drive[0]) <= float(contract.bounds_m.drive_width_max) + EPS, drive)
	_check("SPREAD_HEIGHT", float(spread[1]) <= float(contract.bounds_m.spread_height_max) + EPS)
	_check("DRIVE_HEIGHT", float(drive[1]) <= float(contract.bounds_m.drive_height_max) + EPS)
	for label in [0, -1]:
		var size: Array = envelopes[label].size
		_check("ENDPOINT_LENGTH_" + str(label), float(size[2]) >= float(contract.bounds_m.endpoint_length[0]) - EPS and float(size[2]) <= float(contract.bounds_m.endpoint_length[1]) + EPS)
	_validate_fold_axes(rig)
	_validate_open_can(rig)
	rig.set_form_amount(0.0)
	_check("FULL_REVERSE_TO_SPREAD", _snapshot_matches(first_snapshot, _snapshot(rig)))


func _pose_matches_source(rig: Node3D, form: float) -> bool:
	var expected := {}
	for row: Dictionary in spec.nodes:
		expected[String(row.path)] = {"position": _vector(row.get("position", [0, 0, 0])), "rotation_degrees": _vector(row.get("rotation_degrees", [0, 0, 0]))}
	for row: Dictionary in spec.pose_channels:
		var amount := clampf((form - float(row.start)) / (float(row.end) - float(row.start)), 0.0, 1.0)
		amount = amount * amount * (3.0 - 2.0 * amount)
		var component: int = int(row.component) if row.component is float or row.component is int else {"x": 0, "y": 1, "z": 2}[String(row.component)]
		var value: Vector3 = expected[String(row.path)][String(row.property)]
		value[component] += float(row.travel) * amount
		expected[String(row.path)][String(row.property)] = value
	for path: String in expected:
		var node := rig.get_node_or_null(path) as Node3D
		if node == null:
			return false
		var row: Dictionary = expected[path]
		var basis := Basis.from_euler((row.rotation_degrees as Vector3) * PI / 180.0)
		if not node.position.is_equal_approx(row.position) or not node.basis.is_equal_approx(basis):
			return false
	return true


func _validate_fold_axes(rig: VehicleVisualRig) -> void:
	var half_turns := 0
	for row: Dictionary in spec.pose_channels:
		if not String(row.path).ends_with("/OuterFold"):
			continue
		rig.set_form_amount(0.0)
		var hinge := rig.get_node(String(row.path)) as Node3D
		var initial := hinge.basis
		rig.set_form_amount(1.0)
		var relative := initial.inverse() * hinge.basis
		var expected := Basis(Vector3.FORWARD, PI)
		if relative.is_equal_approx(expected):
			half_turns += 1
	_check("FOUR_ACTUAL_OUTER_LEAF_HALF_TURNS", half_turns == 4, half_turns)


func _validate_open_can(rig: Node3D) -> void:
	var can := rig.get_node("CentralStructure/DriveBay/MovingCan/CanBody") as MeshInstance3D
	var faces := can.mesh.get_faces()
	var inner := INF
	var outer := 0.0
	var zmin := INF
	var zmax := -INF
	for point in faces:
		var radius := Vector2(point.x, point.y).length()
		inner = minf(inner, radius)
		outer = maxf(outer, radius)
		zmin = minf(zmin, point.z)
		zmax = maxf(zmax, point.z)
	_check("ACTUAL_CAN_POSITIVE_WALL_THICKNESS", inner > 0 and outer - inner >= float(contract.can.minimum_wall_m), {"inner_radius": inner, "outer_radius": outer})
	var clear := true
	for ray in 9:
		var offset := Vector2.ZERO if ray == 0 else Vector2.from_angle(float(ray - 1) * PI / 4.0) * inner * 0.8
		var start := Vector3(offset.x, offset.y, zmin - 0.01)
		var finish := Vector3(offset.x, offset.y, zmax + 0.01)
		for i in range(0, faces.size(), 3):
			if Geometry3D.segment_intersects_triangle(start, finish, faces[i], faces[i + 1], faces[i + 2]) != null:
				clear = false
	_check("ACTUAL_CAN_NINE_CLEAR_AXIAL_RAYS", clear)
	var core := rig.get_node("CentralStructure/DriveBay/FixedCore") as MeshInstance3D
	var core_fits := true
	var relative := can.global_transform.affine_inverse() * core.global_transform
	for point in core.mesh.get_faces():
		var local := relative * point
		core_fits = core_fits and Vector2(local.x, local.y).length() < inner - EPS
	_check("FIXED_CORE_INSIDE_OPEN_RADIAL_PASSAGE", core_fits)


func _validate_history(rig: VehicleVisualRig) -> void:
	var independent := {}
	for amount: float in contract.sampling.interruption_poses:
		rig.set_form_amount(0.0)
		rig.set_form_amount(amount)
		independent[amount] = _snapshot(rig)
	var direct_reverse := true
	var interrupted := true
	var amounts: Array = contract.sampling.interruption_poses.duplicate()
	amounts.reverse()
	for amount: float in amounts:
		rig.set_form_amount(amount)
		direct_reverse = direct_reverse and _snapshot_matches(independent[amount], _snapshot(rig))
		rig.set_form_amount(0.731)
		rig.set_form_amount(0.099)
		rig.set_form_amount(0.947)
		rig.set_form_amount(amount)
		interrupted = interrupted and _snapshot_matches(independent[amount], _snapshot(rig))
	_check("DIRECT_REVERSE_HISTORY_EQUIVALENCE", direct_reverse)
	_check("INTERRUPTED_TRANSITION_EQUIVALENCE", interrupted)
	rig.set_form_amount(-2.0)
	_check("LOW_INPUT_CLAMP", rig.form_amount == 0.0 and _snapshot_matches(independent[0.0], _snapshot(rig)))
	rig.set_form_amount(2.0)
	_check("HIGH_INPUT_CLAMP", rig.form_amount == 1.0 and _snapshot_matches(independent[1.0], _snapshot(rig)))


func _validate_energy(rig: VehicleVisualRig, other: VehicleVisualRig) -> void:
	var paths := ["CentralStructure/EnergyCore", "CentralStructure/DriveBay/FixedCore", "CentralStructure/DriveBay/MovingCan/NozzleRing"]
	other.set_form_amount(0.0)
	other.set_energy_state("CLEAR")
	var other_colors := {}
	var independent := true
	for path: String in paths:
		var a := (rig.get_node(path) as MeshInstance3D).get_active_material(0) as StandardMaterial3D
		var b := (other.get_node(path) as MeshInstance3D).get_active_material(0) as StandardMaterial3D
		independent = independent and a != b
		other_colors[path] = b.albedo_color
	var correct_colors := true
	var no_motion_feedback := true
	for form in [0.0, 0.5, 1.0]:
		rig.set_form_amount(form)
		var before := _snapshot(rig)
		for state in ["CLEAR", "CAUTION", "STRIKE", "CLEAR"]:
			rig.set_energy_state(state)
			var expected := Color(1.0, 0.58, 0.16).lerp(Color(0.2, 0.95, 1.0), form)
			if state == "CAUTION":
				expected = Color(1.0, 0.72, 0.12)
			elif state == "STRIKE":
				expected = Color(1.0, 0.12, 0.08)
			for path: String in paths:
				var material := (rig.get_node(path) as MeshInstance3D).get_active_material(0) as StandardMaterial3D
				var nozzle := path.ends_with("NozzleRing")
				correct_colors = correct_colors and material.emission_enabled
				var albedo := expected.lerp(Color.WHITE, 0.18) if nozzle else expected
				correct_colors = correct_colors and material.albedo_color.is_equal_approx(albedo)
				var emission := expected * (0.82 if nozzle else 0.58)
				correct_colors = correct_colors and Vector3(material.emission.r, material.emission.g, material.emission.b).is_equal_approx(Vector3(emission.r, emission.g, emission.b))
				var amount := clampf((form - 0.88) / 0.12, 0.0, 1.0)
				amount = amount * amount * (3.0 - 2.0 * amount)
				var strength := lerpf(0.22, 1.45, amount) if nozzle else lerpf(0.7, 1.35, form)
				correct_colors = correct_colors and is_equal_approx(material.emission_energy_multiplier, strength)
			no_motion_feedback = no_motion_feedback and _snapshot_matches(before, _snapshot(rig))
	for path: String in paths:
		var material := (other.get_node(path) as MeshInstance3D).get_active_material(0) as StandardMaterial3D
		independent = independent and material.albedo_color.is_equal_approx(other_colors[path])
	_check("RIG_INSTANCE_MATERIAL_ISOLATION", independent)
	_check("EXACT_RUNTIME_ENERGY_CUES", correct_colors)
	_check("ENERGY_STATE_DOES_NOT_MOVE_GEOMETRY", no_motion_feedback)


func _validate_gameplay_adapter() -> void:
	var scene := load("res://scenes/craft.tscn") as PackedScene
	var craft := scene.instantiate() as CraftController
	root.add_child(craft)
	# Node can enable an overridden physics callback while entering the tree.
	craft.set_physics_process(false)
	_check("ADAPTER_FIXTURE_PHYSICS_FROZEN", not craft.is_physics_processing())
	var rig := craft.get_node("VisualRoot") as VehicleVisualRig
	var before := craft.transform
	var velocity := craft.velocity
	craft.fold_amount = 0.73
	craft.call("_update_visuals", 0.0, 1.0 / 60.0)
	_check("UNCHANGED_GAMEPLAY_ADAPTER_FORWARDS_FORM", rig != null and is_equal_approx(rig.form_amount, 0.73))
	_check("VISUAL_UPDATE_NO_BODY_STATE_WRITE", craft.transform == before and craft.velocity == velocity)
	var collider := craft.get_node("FixedCollider") as CollisionShape3D
	var capsule := collider.shape as CapsuleShape3D
	_check("ORIGINAL_FIXED_CAPSULE", capsule != null and is_equal_approx(capsule.radius, 0.58) and is_equal_approx(capsule.height, 1.9) and collider.rotation.is_equal_approx(Vector3(1.5708, 0, 0)))
	craft.queue_free()


func _presentation_only(node: Node) -> bool:
	if node is CollisionObject3D or node is CollisionShape3D or node is RayCast3D or node is ShapeCast3D:
		return false
	for child in node.get_children():
		if not _presentation_only(child):
			return false
	return true


func _positive_finite(node: Node) -> bool:
	if node is Node3D:
		var spatial := node as Node3D
		if not spatial.transform.is_finite() or not spatial.scale.is_equal_approx(Vector3.ONE):
			return false
	for child in node.get_children():
		if not _positive_finite(child):
			return false
	return true


func _snapshot(node: Node, prefix := "") -> Dictionary:
	var output := {}
	if node is Node3D:
		output[prefix] = (node as Node3D).transform
	for child in node.get_children():
		output.merge(_snapshot(child, prefix + "/" + String(child.name)))
	return output


func _snapshot_matches(a: Dictionary, b: Dictionary) -> bool:
	if a.size() != b.size():
		return false
	for key in a:
		if not b.has(key) or not (a[key] as Transform3D).is_equal_approx(b[key]):
			return false
	return true


func _areas(meshes: Array[MeshInstance3D]) -> Dictionary:
	var output := {}
	for mesh in meshes:
		var area := 0.0
		var faces := mesh.mesh.get_faces()
		for i in range(0, faces.size(), 3):
			var a := mesh.global_transform * faces[i]
			var b := mesh.global_transform * faces[i + 1]
			var c := mesh.global_transform * faces[i + 2]
			area += (b - a).cross(c - a).length() * 0.5
		output[mesh.get_instance_id()] = area
	return output


func _bounds(rig: Node3D, meshes: Array[MeshInstance3D]) -> AABB:
	var minimum := Vector3(INF, INF, INF)
	var maximum := Vector3(-INF, -INF, -INF)
	for mesh in meshes:
		var relative := rig.global_transform.affine_inverse() * mesh.global_transform
		for point in mesh.mesh.get_faces():
			var value := relative * point
			minimum = minimum.min(value)
			maximum = maximum.max(value)
	return AABB(minimum, maximum - minimum)


func _collect_meshes(node: Node, output: Array[MeshInstance3D]) -> void:
	if node is MeshInstance3D:
		output.append(node as MeshInstance3D)
	for child in node.get_children():
		_collect_meshes(child, output)


func _vector(values: Array) -> Vector3:
	return Vector3(float(values[0]), float(values[1]), float(values[2]))


func _array(value: Vector3) -> Array:
	return [value.x, value.y, value.z]


func _engine_identity() -> String:
	var value := Engine.get_version_info()
	return "%d.%d.%d.%s.%s.%s" % [int(value.major), int(value.minor), int(value.patch), String(value.status), String(value.build), String(value.hash).substr(0, 9)]


func _finish() -> void:
	var result := {"schema": "hush_basin.quarto_vehicle_v1.native.v1", "status": "PASS" if failures.is_empty() else "FAIL", "engine": _engine_identity(), "authority_participation": "none", "checks": checks, "failures": failures, "actual_mesh_envelopes": envelopes, "scope": "Actual native geometry is bound to the authored triangle data and 201 pose transforms checked independently by Python. Native API, reversal, area, material isolation, open bore and gameplay adapter checks are included. No frozen proof authority or human acceptance is claimed."}
	var output := FileAccess.open(result_path, FileAccess.WRITE)
	if output == null:
		push_error("Cannot write native Quarto evidence: " + result_path)
		quit(2)
		return
	output.store_string(JSON.stringify(result, "  ") + "\n")
	output.close()
	print("QUARTO_VEHICLE_V1_NATIVE ", result.status, " checks=", checks.size(), " failures=", failures)
	quit(0 if failures.is_empty() else 1)
