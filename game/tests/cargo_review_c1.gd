extends "res://tests/courier_observed_c1.gd"
func _build_fixture() -> Node3D:
	var fixture := super._build_fixture()
	var tuning := _craft.tuning
	_craft.set_script(preload("res://review/cargo_v1_1/review_craft.gd"))
	_craft.tuning = tuning
	return fixture
