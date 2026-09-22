extends SceneTree
const Lines=preload("res://scripts/courier/line_evidence.gd")
const Catalog=preload("res://scripts/courier/alpha_contracts.gd")
const Ledger=preload("res://scripts/courier/alpha_session.gd")
var checks: Dictionary={}
func run_for(line: RefCounted,n: int,speed: float=30,slip: float=25,drive: bool=true,wall: bool=false) -> void:
 for i in n:line.step(1.0/60,speed,slip,drive,wall,false,speed/60,Vector2(500,500))
func _initialize() -> void:call_deferred("run")
func run() -> void:
 var l:=Lines.new();run_for(l,1200,30,0)
 checks["straight_drive_zero_drift"]=l.best_drift_s==0
 checks["straight_can_still_be_clean_commitment"]=l.best_drive_m>=170
 l=Lines.new();run_for(l,240)
 checks["sustained_real_slip_qualifies"]=l.best_drift_s>3.99
 var before: float=l.drift_s;run_for(l,6,30,0)
 checks["straight_correction_breaks_without_grace"]=l.drift_s==0 and not l.qualifying
 run_for(l,30)
 checks["correction_starts_fresh_combo"]=is_equal_approx(l.drift_s,.5)
 run_for(l,12,30,0)
 checks["long_straight_breaks_combo"]=l.drift_s==0
 run_for(l,60)
 checks["later_drift_starts_new_combo"]=is_equal_approx(l.drift_s,1)
 run_for(l,1,30,25,true,true);run_for(l,120,30,0)
 checks["wall_then_straight_cannot_extend"]=l.drift_s==0
 run_for(l,120,30,25,true,true)
 checks["sustained_wall_pressure_never_qualifies"]=l.drift_s==0 and l.clean_drive_m==0
 for label in ["slow","Spread","backward"]:
  l=Lines.new();run_for(l,120);run_for(l,1,15 if label=="slow" else 30,85 if label=="backward" else 25,label!="Spread")
  checks[label+"_breaks_immediately"]=l.drift_s==0
 l=Lines.new();run_for(l,180,30,25);run_for(l,1,30,25,true,true);run_for(l,180,30,0)
 checks["commit_fragments_not_joined"]=l.best_drive_m<100 and l.clean_drive_m<100
 l=Lines.new();run_for(l,120);l.step(1.0/60,30,25,true,false,true,40,Vector2(500,500))
 checks["relocation_does_not_score"]=l.drift_s==0 and l.clean_drive_m==0
 l=Lines.new();run_for(l,340,30,10);run_for(l,60,10,0,false)
 checks["short_transfer_not_enough"]=l.haul_phase==1
 run_for(l,60,30,10);checks["Drive_cannot_finish_transfer"]=l.haul_phase==1 and l.transfer_m==0
 run_for(l,250,10,0,false);checks["moving_Spread_transfer"]=l.haul_phase==2
 run_for(l,140,30,10);run_for(l,1,30,10,true,true);run_for(l,140,30,10)
 checks["second_leg_fragments_not_joined"]=l.haul_phase==2
 run_for(l,60,30,10);checks["whole_second_leg_finishes"]=l.haul_phase==3
 var ledger:=Ledger.new()
 for i in Catalog.JOBS.size():
  var c:=Catalog.job(i);var no:={"delivered":true,"condition_units":0,"best_drift_s":0,"best_drive_m":0,"thread_complete":false,"haul_phase":0,"route_complete":false,"best_sweep_s":-1,"route_phase":0}
  var yes:={"delivered":true,"condition_units":1000,"best_drift_s":9,"best_drive_m":500,"thread_complete":true,"haul_phase":3,"route_complete":true,"best_sweep_s":9,"route_phase":2}
  for met in [false,true]:
   var id:=ledger.accept(c);var r:=ledger.settle(id,yes if met else no);var balance: int=ledger.balance
   checks["job_%d_%s_payment" % [i,met]]=r.total_credits==int(c.base)+(int(c.bonus) if met else 0) and r.objective_met==met
   ledger.settle(id,yes);checks["job_%d_%s_once" % [i,met]]=ledger.balance==balance
 checks["five_jobs_only"]=Catalog.JOBS.size()==5
 checks["legacy_drive_counter_no_sweep_reward"]=not Catalog.objective_met(Catalog.job(1),{"best_drive_m":100000})
 checks["legacy_mode_sequence_no_haul_reward"]=not Catalog.objective_met(Catalog.job(4),{"haul_phase":3})
 var good:=true
 for value in checks.values():good=good and value
 var result:={"status":"PASS" if good else "FAIL","checks":checks}
 var args:=OS.get_cmdline_user_args();FileAccess.open(args[args.find("--result")+1],FileAccess.WRITE).store_string(JSON.stringify(result,"  "))
 print("MASTERY_PREDICATES "+JSON.stringify(result));quit(0 if good else 1)
