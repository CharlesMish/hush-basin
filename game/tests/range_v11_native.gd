extends SceneTree
func _initialize() -> void:call_deferred("run")
func run() -> void:
	var args:=OS.get_cmdline_user_args()
	var out:=args[args.find("--result")+1]
	var probe:=preload("res://tests/range_v11_probe.gd").new()
	if "--captures" in args:
		probe.capture_dir=args[args.find("--captures")+1]
		DirAccess.make_dir_recursive_absolute(probe.capture_dir)
	probe.clip_frames="--clip" in args
	root.add_child(probe)
	var result: Dictionary=await probe.finished
	FileAccess.open(out,FileAccess.WRITE).store_string(JSON.stringify(result,"  "))
	paused=false;probe.queue_free();await process_frame
	quit(0 if result.status=="PASS" else 1)
