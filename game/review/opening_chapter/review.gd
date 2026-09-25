extends "res://review/relay_consequence/relay_review.gd"
func _init() -> void:game_scene_path="res://scenes/opening_chapter.tscn"
func write(row: Dictionary) -> void:
	row["opening_chapter_candidate"]="v0.1";super.write(row)
