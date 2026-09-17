extends "res://scripts/craft_controller.gd"
## Disposable observation hook. The production controller is byte-identical.
var review_pre_move_velocity := Vector3.ZERO
var review_impact_frame := -1

func _apply_strongest_impact(pre_move_velocity: Vector3) -> void:
	review_pre_move_velocity = pre_move_velocity
	review_impact_frame = Engine.get_physics_frames()
	super._apply_strongest_impact(pre_move_velocity)
