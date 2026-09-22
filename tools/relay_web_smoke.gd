extends "res://tests/receiver_comprehension_probe.gd"
## Same integration, with phases selected only in this diagnostic export.
func _ready() -> void:
	if OS.has_feature("web"):
		var search: String=JavaScriptBridge.eval("window.location.search",true)
		for entry in search.trim_prefix("?").split("&"):
			if entry.begins_with("phase="):phase=entry.trim_prefix("phase=")
			if entry=="control=1":neutral=true
	super._ready()
