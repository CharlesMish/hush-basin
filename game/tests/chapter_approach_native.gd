extends SceneTree
func _initialize() -> void:call_deferred("run")
func run() -> void:
	var args:=OS.get_cmdline_user_args();var probe=preload("res://tests/chapter_approach_probe.gd").new()
	probe.save_path=args[args.find("--save")+1];root.add_child(probe)
	var result: Dictionary=await probe.finished
	FileAccess.open(args[args.find("--result")+1],FileAccess.WRITE).store_string(JSON.stringify(result,"  "));paused=false;quit(0 if result.status=="PASS" else 1)
