extends SceneTree
## Headless launcher for the Hem Loop checks (tests/rink_checks.gd).
## godot --headless --fixed-fps 60 --path game --script res://tests/rink_suite.gd -- --result <file.json> [--only a,b]


func _initialize() -> void:
	var checks: Node = load("res://tests/rink_checks.gd").new()
	checks.name = "RinkChecks"
	root.add_child.call_deferred(checks)
