extends SceneTree
func _initialize() -> void:call_deferred("run")
func run() -> void:
 var args:=OS.get_cmdline_user_args();var out:=args[args.find("--output")+1];DirAccess.make_dir_recursive_absolute(out)
 var before: bool="--before" in args
 var gate: P1AWorldGate
 var game: Node
 if before:
  game=load("res://scenes/district_zero_p1a.tscn").instantiate();root.add_child(game);gate=game
  var lantern:=preload("res://scripts/courier/market_lantern.gd").new();lantern.manifest=gate.data.manifest;gate.world.add_child(lantern)
 else:
  game=load("res://review/alpha_loop/alpha_review.tscn").instantiate();root.add_child(game)
  for i in 5:await process_frame
  gate=game.job.gate;game.job.hud.hide();game.panel.hide()
 gate.get_node("UI").hide()
 var craft:=gate.craft;craft.set_physics_process(false)
 var cfg: Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://presentation/mechanics_range_v1.json")).works
 var points: Array=gate.data.routes.L6.points_xz_m;var end:=int((points.size()-1)*float(cfg.fraction));var target:=P1AWorldData.xz(points[end])
 var views:={"works_approach":P1AWorldData.xz(points[end-140]),"works_warning":P1AWorldData.xz(points[end-95]),"works_close":P1AWorldData.xz(points[end-45]),"depot_yard":Vector2(-10,25),"relay_entry":Vector2(-168,20)}
 for id in views:
  var p: Vector2=views[id];var look:=target if String(id).begins_with("works") else Vector2(-90,65) if id=="depot_yard" else Vector2(-166,-50)
  var d: Vector2=(look-p).normalized()
  craft.global_transform=Transform3D(Basis(Vector3.UP,atan2(-d.x,-d.y)),Vector3(p.x,gate.data.terrain_height_at(p.x,p.y)+1.325,p.y));craft.reset_physics_interpolation();gate.camera_rig.snap_to_target()
  for i in 20:await process_frame
  RenderingServer.force_draw(false);root.get_texture().get_image().save_png(out.path_join(id+".png"))
 quit()
