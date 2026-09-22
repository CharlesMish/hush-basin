extends "res://tests/mechanics_c1.gd"
## The same 1,260 movement ticks with the owned palette selected.
func _build_fixture() -> Node3D:
	var fixture:=super._build_fixture()
	for child in fixture.get_children():
		if child.get_script()==preload("res://scripts/courier/slip_trail.gd"):
			child.trail_style="lantern_amber"
	return fixture
