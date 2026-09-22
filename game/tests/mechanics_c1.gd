extends "res://tests/alpha_c1.gd"
func _build_fixture() -> Node3D:
 var fixture:=super._build_fixture()
 var trail:=preload("res://scripts/courier/slip_trail.gd").new();trail.craft=_craft;fixture.add_child(trail)
 return fixture
