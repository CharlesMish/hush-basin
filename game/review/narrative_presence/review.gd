extends "res://review/relay_consequence/relay_review.gd"
func _init() -> void:
	game_scene_path="res://scenes/narrative_presence.tscn"
func write(row: Dictionary) -> void:
	row["narrative_candidate"]="v0.1"
	super.write(row)
