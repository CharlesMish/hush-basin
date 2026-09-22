extends SceneTree
class MovieProbe:
 extends "res://tests/mastery_probe.gd"
 func run() -> void:
  var args:=OS.get_cmdline_user_args();route_id=args[args.find("--line")+1]
  review=load("res://review/alpha_loop/alpha_review.tscn").instantiate();add_child(review);await ticks(120)
  game=review.game;job=review.job;gate=job.gate;craft=job.craft
  var cases:={"DEP_style":[0,[]],"RLY_sweep":[1,["-L1","-L0","A1"]],"WRK_way":[2,[]],"THREAD_dogleg":[3,["-L1","S0","DOG","S1"]],"THREAD_hop":[3,["-L1","S0","HOP","S1"]],"HAUL_long":[4,["L2","L3","-A2","-X0"]]}
  await fresh(cases[route_id][0])
  if "--amber" in args:job.trail.trail_style="lantern_amber" # Visual comparison fixture only.
  var points: Array[Vector2]=[job.origin,job.destination]
  if not cases[route_id][1].is_empty():points=Driver.road(gate,cases[route_id][1])
  var result:=await Driver.drive(self,points)
  print("MOVIE_RESULT "+JSON.stringify(result))
  await ticks(90)
  finished.emit(result)
func _initialize() -> void:call_deferred("run")
func run() -> void:
 var probe:=MovieProbe.new();root.add_child(probe)
 var result: Dictionary=await probe.finished
 var args:=OS.get_cmdline_user_args();FileAccess.open(args[args.find("--result")+1],FileAccess.WRITE).store_string(JSON.stringify(result,"  "))
 quit(0 if result.delivered and result.receipt.objective_met else 1)
