extends SceneTree

const EXPECTED_ENGINE_PREFIX := "4.7.1.stable.official.a13da4feb"
const BASELINE_HASHES := {
	"res://scripts/motion_math.gd": "c2ceb0ab0f5bcff7d6a4cf7c2b6e3c7fa1c70b96edee206d00b529d3329ed575",
	"res://scripts/craft_tuning.gd": "c6b82758d7d985d0a16d16a7265a52e2ba2b5a4ec2e608a08ef1d2fa7650acfd",
	"res://resources/default_tuning.tres": "a6d7a6ef66f28a480bc28096c91124e5c93f9b8e7dd32c68296030ce21800459",
}
const SAMPLE_POSES := [0.0, 0.12, 0.25, 0.43, 0.60, 0.75, 0.87, 0.88, 0.94, 1.0]
const POSE_SIGNATURE_SHA256 := "045296bf018b6da5af5d89b37af831fd29eedfe16d8f085f80ba6fb113dfb44b"
const POSE_SIGNATURE_PATHS := [
	"FrontPortRig/BookPivot",
	"FrontPortRig/BookPivot/YawPivot",
	"FrontPortRig/BookPivot/YawPivot/HaunchPivot",
	"FrontPortRig/BookPivot/YawPivot/HaunchPivot/SocketSlide",
	"FrontStarboardRig/BookPivot",
	"FrontStarboardRig/BookPivot/YawPivot",
	"FrontStarboardRig/BookPivot/YawPivot/HaunchPivot",
	"FrontStarboardRig/BookPivot/YawPivot/HaunchPivot/SocketSlide",
	"RearPortRig/BookPivot",
	"RearPortRig/BookPivot/YawPivot",
	"RearPortRig/BookPivot/YawPivot/HaunchPivot",
	"RearPortRig/BookPivot/YawPivot/HaunchPivot/SocketSlide",
	"RearStarboardRig/BookPivot",
	"RearStarboardRig/BookPivot/YawPivot",
	"RearStarboardRig/BookPivot/YawPivot/HaunchPivot",
	"RearStarboardRig/BookPivot/YawPivot/HaunchPivot/SocketSlide",
	"CentralStructure/DriveBay/MovingCan",
]

var failures: Array[String] = []
var spread_envelope := Vector3.ZERO
var drive_envelope := Vector3.ZERO


func _initialize() -> void:
	_run_validation.call_deferred()


func _run_validation() -> void:
	var engine_info := Engine.get_version_info()
	var exact_engine := (
		int(engine_info.get("major", 0)) == 4
		and int(engine_info.get("minor", 0)) == 7
		and int(engine_info.get("patch", 0)) == 1
		and str(engine_info.get("status", "")) == "stable"
		and str(engine_info.get("hash", "")).begins_with("a13da4feb")
	)
	_require(exact_engine, "exact Godot 4.7.1 engine")

	var craft_scene := load("res://scenes/craft.tscn") as PackedScene
	var visual_scene := load("res://scenes/vehicle_visual.tscn") as PackedScene
	_require(craft_scene != null, "craft scene loads")
	_require(visual_scene != null, "visual rig scene loads")
	if craft_scene == null or visual_scene == null:
		_finish()
		return

	var craft := craft_scene.instantiate()
	var rig := visual_scene.instantiate() as VehicleVisualRig
	root.add_child(craft)
	root.add_child(rig)
	_validate_gameplay_contract(craft)
	_validate_rig(rig)
	_validate_preserved_hashes()
	craft.queue_free()
	rig.queue_free()
	_finish()


func _validate_gameplay_contract(craft: Node) -> void:
	_require(craft is CharacterBody3D, "gameplay root remains CharacterBody3D")
	var collider := craft.get_node_or_null("FixedCollider") as CollisionShape3D
	_require(collider != null, "fixed collider retained")
	if collider != null:
		_require(collider.shape is CapsuleShape3D, "fixed collider remains a capsule")
		if collider.shape is CapsuleShape3D:
			var capsule := collider.shape as CapsuleShape3D
			_require(is_equal_approx(capsule.radius, 0.58), "fixed collider radius unchanged")
			_require(is_equal_approx(capsule.height, 1.9), "fixed collider height unchanged")
		_require(collider.rotation.is_equal_approx(Vector3(1.5708, 0.0, 0.0)), "fixed collider transform unchanged")

	var probe_contracts := {
		"ProbeLeft": Vector3(-0.48, 0.0, 0.52),
		"ProbeRight": Vector3(0.48, 0.0, 0.52),
		"ProbeRear": Vector3(0.0, 0.0, -0.72),
	}
	for probe_name in probe_contracts:
		var probe := craft.get_node_or_null(probe_name) as RayCast3D
		_require(probe != null, "%s retained" % probe_name)
		if probe != null:
			_require(probe.position.is_equal_approx(probe_contracts[probe_name]), "%s position unchanged" % probe_name)
			_require(probe.target_position.is_equal_approx(Vector3(0.0, -3.8, 0.0)), "%s reach unchanged" % probe_name)
			_require(probe.collision_mask == 1 and probe.enabled, "%s collision contract unchanged" % probe_name)

	var hazard := craft.get_node_or_null("HazardPreview") as ShapeCast3D
	_require(hazard != null, "hazard cast retained")
	if hazard != null:
		_require(hazard.shape is SphereShape3D, "hazard cast remains spherical")
		if hazard.shape is SphereShape3D:
			_require(is_equal_approx((hazard.shape as SphereShape3D).radius, 0.48), "hazard radius unchanged")
		_require(hazard.position.is_equal_approx(Vector3(0.0, -0.04, -0.25)), "hazard position unchanged")
		_require(hazard.target_position.is_equal_approx(Vector3(0.0, 0.0, -2.0)), "hazard target unchanged")
		_require(hazard.collision_mask == 1 and hazard.exclude_parent and hazard.enabled, "hazard collision contract unchanged")
	var gameplay_rig := craft.get_node_or_null("VisualRoot") as VehicleVisualRig
	_require(gameplay_rig != null, "gameplay uses shared VehicleVisualRig")
	if gameplay_rig != null:
		craft.set("fold_amount", 0.73)
		craft.call("_update_visuals", 0.0, 1.0 / 60.0)
		_require(is_equal_approx(gameplay_rig.form_amount, 0.73), "CraftController forwards fold_amount to visual rig")


func _validate_rig(rig: VehicleVisualRig) -> void:
	_require(rig != null, "visual root has VehicleVisualRig API")
	if rig == null:
		return
	var pose_signature := _pose_signature(rig)
	print("  Pose choreography SHA-256: %s" % pose_signature)
	if not POSE_SIGNATURE_SHA256.is_empty():
		_require(pose_signature == POSE_SIGNATURE_SHA256, "pose choreography matches the untouched R1 golden signature")
	for path in [
		"FrontPortRig/BookPivot/YawPivot/HaunchPivot/SocketSlide",
		"FrontStarboardRig/BookPivot/YawPivot/HaunchPivot/SocketSlide",
		"RearPortRig/BookPivot/YawPivot/HaunchPivot/SocketSlide",
		"RearStarboardRig/BookPivot/YawPivot/HaunchPivot/SocketSlide",
		"FrontPortRig/RootSocket",
		"FrontPortRig/BookPivot/YawPivot/HaunchPivot/SocketSlide/LeafUnderlay",
		"FrontStarboardRig/RootSocket",
		"FrontStarboardRig/BookPivot/YawPivot/HaunchPivot/SocketSlide/LeafUnderlay",
		"RearPortRig/RootSocket",
		"RearPortRig/BookPivot/YawPivot/HaunchPivot/SocketSlide/LeafUnderlay",
		"RearStarboardRig/RootSocket",
		"RearStarboardRig/BookPivot/YawPivot/HaunchPivot/SocketSlide/LeafUnderlay",
		"CentralStructure/DriveBay/FixedCore",
		"CentralStructure/DriveBay/MovingCan",
		"CentralStructure/DriveBay/MovingCan/CanBody",
		"CentralStructure/DriveBay/MovingCan/NozzleRing",
		"CentralStructure/DriveBay/MovingCan/NozzleBore",
	]:
		_require(rig.get_node_or_null(path) != null, "visual hierarchy contains %s" % path)
	_require(_all_scales_positive(rig), "visual hierarchy keeps positive local scale")

	for pose in SAMPLE_POSES:
		rig.set_form_amount(pose)
		_require(_all_transforms_finite(rig), "pose %.2f is finite" % pose)
		_validate_bilateral_bounds(rig, pose, "FrontPortRig", "FrontStarboardRig")
		_validate_bilateral_bounds(rig, pose, "RearPortRig", "RearStarboardRig")
		_validate_center_separation(rig, pose)

	rig.set_form_amount(0.43)
	var direct_snapshot := _snapshot_transforms(rig)
	rig.set_form_amount(1.0)
	rig.set_form_amount(0.43)
	var replay_snapshot := _snapshot_transforms(rig)
	_require(_snapshots_match(direct_snapshot, replay_snapshot), "direct pose determinism at t=0.43")

	var moving_can := rig.get_node("CentralStructure/DriveBay/MovingCan") as Node3D
	rig.set_form_amount(0.0)
	var can_start := moving_can.position.z
	rig.set_form_amount(0.879)
	_require(is_equal_approx(moving_can.position.z, can_start), "propulsion can remains stowed before t=0.88")
	rig.set_form_amount(0.88)
	_require(is_equal_approx(moving_can.position.z, can_start), "propulsion can is still stowed at t=0.88")
	rig.set_form_amount(1.0)
	_require(is_equal_approx(moving_can.position.z - can_start, 0.51), "propulsion can completes 0.51 m aft stroke")

	var front_yaw := rig.get_node("FrontPortRig/BookPivot/YawPivot") as Node3D
	var rear_yaw := rig.get_node("RearPortRig/BookPivot/YawPivot") as Node3D
	_require(not is_equal_approx(absf(front_yaw.rotation.y), absf(rear_yaw.rotation.y)), "front and rear yaw choreography remain distinct")

	rig.set_form_amount(0.0)
	spread_envelope = _subtree_bounds(rig, rig).size
	rig.set_form_amount(1.0)
	drive_envelope = _subtree_bounds(rig, rig).size
	print("  SPREAD envelope: %.5f W x %.5f H x %.5f L m" % [spread_envelope.x, spread_envelope.y, spread_envelope.z])
	print("  DRIVE envelope:  %.5f W x %.5f H x %.5f L m" % [drive_envelope.x, drive_envelope.y, drive_envelope.z])
	for rig_name in ["FrontPortRig", "FrontStarboardRig", "RearPortRig", "RearStarboardRig"]:
		var mechanism_bounds := _subtree_bounds(rig, rig.get_node(rig_name))
		print("    %s X: %.5f to %.5f" % [rig_name, mechanism_bounds.position.x, mechanism_bounds.end.x])
	_require(spread_envelope.x >= 2.60 and spread_envelope.x <= 2.72, "SPREAD width is within 2.60-2.72 m")
	_require(spread_envelope.y <= 0.56, "SPREAD polish does not increase vehicle height")
	_require(drive_envelope.x >= 0.92 and drive_envelope.x <= 1.15, "DRIVE width is within 0.92-1.15 m")
	_require(drive_envelope.y <= 0.86, "DRIVE polish does not materially increase vehicle height")
	_require(drive_envelope.x < 1.505, "DRIVE is materially narrower than the 1.505 m baseline")
	_require(spread_envelope.z >= 2.25 and spread_envelope.z <= 2.45, "SPREAD length remains near the 1:5 target")
	_require(drive_envelope.z >= 2.25 and drive_envelope.z <= 2.45, "DRIVE length remains near the 1:5 target")


func _validate_bilateral_bounds(rig: Node3D, pose: float, port_path: String, starboard_path: String) -> void:
	var port_bounds := _subtree_bounds(rig, rig.get_node(port_path))
	var starboard_bounds := _subtree_bounds(rig, rig.get_node(starboard_path))
	var tolerance := 0.001
	_require(absf(port_bounds.position.x + starboard_bounds.end.x) <= tolerance, "%s mirrored outer X at %.2f" % [port_path, pose])
	_require(absf(port_bounds.end.x + starboard_bounds.position.x) <= tolerance, "%s mirrored inner X at %.2f" % [port_path, pose])
	_require(absf(port_bounds.position.y - starboard_bounds.position.y) <= tolerance, "%s mirrored low Y at %.2f" % [port_path, pose])
	_require(absf(port_bounds.end.y - starboard_bounds.end.y) <= tolerance, "%s mirrored high Y at %.2f" % [port_path, pose])
	_require(absf(port_bounds.position.z - starboard_bounds.position.z) <= tolerance, "%s mirrored front Z at %.2f" % [port_path, pose])
	_require(absf(port_bounds.end.z - starboard_bounds.end.z) <= tolerance, "%s mirrored aft Z at %.2f" % [port_path, pose])


func _validate_center_separation(rig: Node3D, pose: float) -> void:
	for pair in [
		["FrontPortRig", "FrontStarboardRig"],
		["RearPortRig", "RearStarboardRig"],
	]:
		var port_bounds := _subtree_bounds(rig, rig.get_node(pair[0]))
		var starboard_bounds := _subtree_bounds(rig, rig.get_node(pair[1]))
		var separated := port_bounds.end.x <= starboard_bounds.position.x + 0.002
		if not separated:
			print("  overlap sample %s %.2f: port %.5f / starboard %.5f" % [pair[0], pose, port_bounds.end.x, starboard_bounds.position.x])
		_require(separated, "%s bilateral assemblies do not cross at %.2f" % [pair[0], pose])


func _subtree_bounds(root_node: Node3D, subtree: Node) -> AABB:
	var minimum := Vector3(INF, INF, INF)
	var maximum := Vector3(-INF, -INF, -INF)
	var meshes: Array[MeshInstance3D] = []
	_collect_meshes(subtree, meshes)
	for mesh_instance in meshes:
		if mesh_instance.mesh == null:
			continue
		var relative := root_node.global_transform.affine_inverse() * mesh_instance.global_transform
		var local_bounds := mesh_instance.mesh.get_aabb()
		for corner_index in 8:
			var corner := Vector3(
				local_bounds.position.x + local_bounds.size.x * float(corner_index & 1),
				local_bounds.position.y + local_bounds.size.y * float((corner_index >> 1) & 1),
				local_bounds.position.z + local_bounds.size.z * float((corner_index >> 2) & 1)
			)
			var point := relative * corner
			minimum = minimum.min(point)
			maximum = maximum.max(point)
	return AABB(minimum, maximum - minimum)


func _collect_meshes(node: Node, output: Array[MeshInstance3D]) -> void:
	if node is MeshInstance3D:
		output.append(node as MeshInstance3D)
	for child in node.get_children():
		_collect_meshes(child, output)


func _snapshot_transforms(root_node: Node) -> Dictionary:
	var result := {}
	_snapshot_recursive(root_node, root_node, result)
	return result


func _snapshot_recursive(root_node: Node, node: Node, output: Dictionary) -> void:
	if node is Node3D:
		output[str(root_node.get_path_to(node))] = (node as Node3D).transform
	for child in node.get_children():
		_snapshot_recursive(root_node, child, output)


func _snapshots_match(left: Dictionary, right: Dictionary) -> bool:
	if left.size() != right.size():
		return false
	for path in left:
		if not right.has(path) or not (left[path] as Transform3D).is_equal_approx(right[path] as Transform3D):
			return false
	return true


func _pose_signature(rig: VehicleVisualRig) -> String:
	var context := HashingContext.new()
	context.start(HashingContext.HASH_SHA256)
	for pose in SAMPLE_POSES:
		rig.set_form_amount(pose)
		context.update(("pose=%.9f\n" % pose).to_utf8_buffer())
		for path in POSE_SIGNATURE_PATHS:
			var node := rig.get_node(path) as Node3D
			var transform := node.transform
			var values := [
				transform.basis.x.x, transform.basis.x.y, transform.basis.x.z,
				transform.basis.y.x, transform.basis.y.y, transform.basis.y.z,
				transform.basis.z.x, transform.basis.z.y, transform.basis.z.z,
				transform.origin.x, transform.origin.y, transform.origin.z,
			]
			var line := "%s=" % path
			for value in values:
				line += "%.9f," % value
			context.update((line + "\n").to_utf8_buffer())
	return context.finish().hex_encode()


func _all_transforms_finite(node: Node) -> bool:
	if node is Node3D:
		var transform := (node as Node3D).transform
		if not _vector_finite(transform.origin):
			return false
		if not _vector_finite(transform.basis.x) or not _vector_finite(transform.basis.y) or not _vector_finite(transform.basis.z):
			return false
	for child in node.get_children():
		if not _all_transforms_finite(child):
			return false
	return true


func _all_scales_positive(node: Node) -> bool:
	if node is Node3D:
		var local_scale := (node as Node3D).scale
		if local_scale.x <= 0.0 or local_scale.y <= 0.0 or local_scale.z <= 0.0:
			return false
	for child in node.get_children():
		if not _all_scales_positive(child):
			return false
	return true


func _vector_finite(value: Vector3) -> bool:
	return is_finite(value.x) and is_finite(value.y) and is_finite(value.z)


func _validate_preserved_hashes() -> void:
	for path in BASELINE_HASHES:
		_require(_sha256(path) == BASELINE_HASHES[path], "%s remains byte-identical to baseline" % path)


func _sha256(path: String) -> String:
	var file := FileAccess.open(path, FileAccess.READ)
	if file == null:
		return ""
	var context := HashingContext.new()
	context.start(HashingContext.HASH_SHA256)
	while file.get_position() < file.get_length():
		context.update(file.get_buffer(mini(65536, file.get_length() - file.get_position())))
	return context.finish().hex_encode()


func _require(condition: bool, description: String) -> void:
	if not condition:
		failures.append(description)


func _finish() -> void:
	if failures.is_empty():
		print("BABYLON_TRANSFER_VALIDATION:PASS")
		quit(0)
		return
	for failure in failures:
		push_error("BABYLON_TRANSFER_VALIDATION:FAIL:%s" % failure)
	quit(1)
