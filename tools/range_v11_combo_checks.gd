extends SceneTree
## Explicit replay of the reported exploit shape; no game/controller writes.
const Lines=preload("res://scripts/courier/line_evidence.gd")
const Catalog=preload("res://scripts/courier/alpha_contracts.gd")
func samples(line: RefCounted,count: int,slip: float,wall: bool=false) -> void:
 for i in count:line.step(1.0/60,30,slip,true,wall,false,.5,Vector2(500,500))
func _initialize() -> void:
 var checks: Dictionary={};var line:=Lines.new()
 samples(line,180,25);samples(line,600,0)
 checks["three_second_drift_then_ten_second_straight_misses"]=not Catalog.objective_met(Catalog.job(0),line.snapshot)
 checks["straight_adds_no_drift_seconds"]=is_equal_approx(line.best_drift_s,3.0)
 line=Lines.new();samples(line,180,25);samples(line,1,25,true);samples(line,600,0)
 checks["wall_then_straight_cannot_finish_partial_combo"]=not Catalog.objective_met(Catalog.job(0),line.snapshot) and line.drift_s==0
 line=Lines.new();samples(line,120,25);samples(line,1,0);samples(line,120,25)
 checks["two_drift_fragments_do_not_add"]=not Catalog.objective_met(Catalog.job(0),line.snapshot) and is_equal_approx(line.best_drift_s,2.0)
 line=Lines.new();samples(line,240,25)
 checks["continuous_four_seconds_succeeds"]=Catalog.objective_met(Catalog.job(0),line.snapshot)
 var good:=true
 for value in checks.values():good=good and value
 var result:={"status":"PASS" if good else "FAIL","checks":checks}
 var args:=OS.get_cmdline_user_args();FileAccess.open(args[args.find("--result")+1],FileAccess.WRITE).store_string(JSON.stringify(result,"  "))
 print("COMBO_EXPLOIT_REPLAY "+JSON.stringify(result));quit(0 if good else 1)
