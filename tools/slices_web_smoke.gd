extends "res://tests/slices_probe.gd"
func _ready() -> void:
	save_path="user://narrative_slices_web_probe.json"
	if OS.has_feature("web"):
		var search: String=JavaScriptBridge.eval("window.location.search",true)
		for entry in search.trim_prefix("?").split("&"):
			if entry.begins_with("phase="):phase=entry.trim_prefix("phase=")
			if entry.begins_with("snapshot="):save_path+="."+entry.trim_prefix("snapshot=")
	super._ready()
func finish() -> void:
	if OS.has_feature("web") and not opening_run:JavaScriptBridge.eval("document.title='Narrative slices "+("FAIL" if checks.values().has(false) else "PASS")+"'",true)
	super.finish()
