extends "res://tests/cargo_review_c1.gd"
class AlphaObserver:
	extends Node
	var craft: CraftController
	var cargo=preload("res://scripts/courier/alpha_cargo.gd").new()
	func _ready() -> void:
		process_physics_priority=250
		cargo.protected="--protected" in OS.get_cmdline_user_args()
		craft.reset_performed.connect(func(_count,_reason):cargo.begin(craft))
		cargo.begin(craft)
	func _physics_process(delta: float) -> void:
		if craft.is_physics_processing():assert(cargo.sample(craft,delta).valid)
func _build_fixture() -> Node3D:
	var fixture:=super._build_fixture()
	var observer:=AlphaObserver.new();observer.craft=_craft;fixture.add_child(observer)
	return fixture
