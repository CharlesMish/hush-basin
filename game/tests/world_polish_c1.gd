extends "res://tests/p1a_baseline_runner.gd"
## Same 1260-input C1 fixture, with startup frozen until alignment and samples
## taken explicitly after physics. The inherited recorder is retained unchanged.

class TailFence:
	extends Node
	signal tail
	func _ready() -> void:
		process_physics_priority = 1000
	func _physics_process(_delta: float) -> void:
		tail.emit()

func _run() -> void:
	if not _engine_identity_matches():
		_fail("C1 requires the exact recorded engine")
		return
	_output_path = _parse_output_path()
	var fixture := _build_fixture()
	_craft.set_physics_process(false)
	_camera_rig.set_physics_process(false)
	root.add_child(fixture)
	var fence := TailFence.new()
	root.add_child(fence)
	await process_frame
	_release_all_actions()
	_craft.set_spawn_transform(Transform3D(Basis.IDENTITY, Vector3(0, 1.65, 0)))
	_craft.reset_craft("P1A C1 baseline alignment")
	# look_at preserves the existing scale. Discard the ready-time camera basis
	# (including its floating-point scale residue) before the canonical snap.
	_camera_rig.global_transform = Transform3D.IDENTITY
	_camera_rig.reset_physics_interpolation()
	_camera_rig.snap_to_target()
	var f := FileAccess.open(_output_path, FileAccess.WRITE)
	if f == null:
		_fail("C1 output could not be opened")
		return
	await physics_frame
	_craft.set_physics_process(true)
	_camera_rig.set_physics_process(true)
	for tick in TRACE_TICKS:
		_apply_tick_actions(tick)
		await fence.tail
		f.store_line(JSON.stringify(_sample_trace(tick)))
	f.close()
	_release_all_actions()
	fixture.queue_free()
	fence.queue_free()
	await process_frame
	print("SYNCHRONIZED C1: 1260 ticks")
	quit()
