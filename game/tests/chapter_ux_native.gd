extends SceneTree
func _initialize() -> void:call_deferred("run")
func run() -> void:
	var args:=OS.get_cmdline_user_args();var probe=preload("res://tests/chapter_ux_probe.gd").new()
	probe.save_path=args[args.find("--save")+1]
	if "--phase" in args:probe.phase=args[args.find("--phase")+1]
	if "--captures" in args:probe.capture_dir=args[args.find("--captures")+1];DirAccess.make_dir_recursive_absolute(probe.capture_dir)
	root.add_child(probe);var result: Dictionary=await probe.finished
	FileAccess.open(args[args.find("--result")+1],FileAccess.WRITE).store_string(JSON.stringify(result,"  "))
	paused=false;probe.queue_free();await process_frame;quit(0 if result.status=="PASS" else 1)
