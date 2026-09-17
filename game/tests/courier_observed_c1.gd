extends "res://tests/world_polish_c1.gd"
## Same historical input fixture/recorder with the real cargo observer attached.
class Observer:
	extends Node
	var craft: CraftController
	var cargo = preload("res://scripts/courier/cargo_observer.gd").new()
	func _ready() -> void:
		process_physics_priority = 200
		craft.reset_performed.connect(func(_count, _reason): cargo.begin(craft))
		cargo.begin(craft)
	func _physics_process(delta: float) -> void:
		if craft.is_physics_processing():
			var result: Dictionary = cargo.sample(craft,delta)
			assert(result.valid,"C1 cargo observation discontinuity")

func _build_fixture() -> Node3D:
	var fixture := super._build_fixture()
	var observer := Observer.new()
	observer.craft = _craft
	fixture.add_child(observer)
	return fixture
