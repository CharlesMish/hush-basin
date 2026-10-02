extends "res://tests/chapter_probe.gd"
func _ready() -> void:
	save_path="user://opening_chapter_web_probe.json"
	if OS.has_feature("web"):
		var search: String=JavaScriptBridge.eval("window.location.search",true)
		for entry in search.trim_prefix("?").split("&"):
			if entry.begins_with("phase="):phase=entry.trim_prefix("phase=")
		if phase.begins_with("inspect_"):save_path+="."+phase.trim_prefix("inspect_")
	super._ready()
func finish() -> void:
	if OS.has_feature("web"):
		JavaScriptBridge.eval("document.title='Chapter "+("FAIL" if checks.values().has(false) else "PASS")+"'",true)
	super.finish()
