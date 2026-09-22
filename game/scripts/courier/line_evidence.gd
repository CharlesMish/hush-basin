extends RefCounted
## Observes motion only. Never writes the craft, BRRR, cargo or physics state.
const Brrr=preload("res://scripts/run/brrr_seed.gd")
const CargoContacts=preload("res://scripts/courier/cargo_observer.gd")
var cfg: Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://presentation/mechanics_range_v1_1.json"))
var drift_s:=0.0
var best_drift_s:=0.0
var grace_s:=0.0
var qualifying:=false
var reason:="idle"
var clean_drive_m:=0.0
var best_drive_m:=0.0
var haul_phase:=0
var transfer_m:=0.0
var second_leg_m:=0.0
var thread_active:=false
var thread_complete:=false
var thread_west:=Vector2.ZERO
var thread_east:=Vector2.ZERO
var thread_bounds:=Rect2()
var last_position:=Vector3.ZERO
var last_impacts:=0
var initialized:=false
var drive_s:=0.0
var spread_s:=0.0
var total_m:=0.0
var breaks:=0
var snapshot: Dictionary={}
var transitions: Array=[]
var sample_time:=0.0
func configure(data: P1AWorldData) -> void:
 thread_west=P1AWorldData.xz(data.manifest.nodes.HJW.xz_m)
 thread_east=P1AWorldData.xz(data.manifest.nodes.HJE.xz_m)
 thread_bounds=Rect2(thread_west,Vector2.ZERO)
 for route in ["HOP","DOG"]:
  for p in data.routes[route].points_xz_m:thread_bounds=thread_bounds.expand(P1AWorldData.xz(p))
 thread_bounds=thread_bounds.grow(float(cfg.thread.corridor_margin_m))
func begin(craft: CraftController) -> void:
 drift_s=0;best_drift_s=0;grace_s=0;clean_drive_m=0;best_drive_m=0
 haul_phase=0;transfer_m=0;second_leg_m=0;thread_active=false;thread_complete=false
 drive_s=0;spread_s=0;total_m=0;breaks=0;qualifying=false;reason="ready"
 last_position=craft.global_position;last_impacts=craft.impact_count;initialized=true
 transitions.clear();sample_time=0;snapshot={}
func sample(craft: CraftController,delta: float) -> Dictionary:
 if not initialized:begin(craft)
 var observed:=Brrr.step(craft.velocity,-craft.global_basis.z,craft.regime_name()=="DRIVE",delta,0,0)
 var moved:=Vector2(craft.global_position.x-last_position.x,craft.global_position.z-last_position.z).length()
 var fresh_controller_impact:=craft.impact_count>last_impacts
 # Raw counters include support contact. Use the accepted obstacle classifier;
 # sustained wall pressure breaks a line even without a fresh severity report.
 var contact:=CargoContacts.contacts(craft)
 var impact: bool=contact.wall_touch
 var discontinuity:=moved>maxf(3.0,float(observed.speed)*delta*3.0)
 last_position=craft.global_position;last_impacts=craft.impact_count
 var result:=step(delta,observed.speed,observed.split_degrees,craft.regime_name()=="DRIVE",impact,discontinuity,moved,Vector2(last_position.x,last_position.z))
 result.merge({"controller_impact_fresh":fresh_controller_impact,"controller_impact_count":craft.impact_count,"eligible_impact":fresh_controller_impact and contact.eligible,"wall_touch":contact.wall_touch})
 return result
func step(dt: float,speed: float,slip: float,drive: bool,impact: bool,discontinuity: bool,moved: float,p: Vector2) -> Dictionary:
 var prior_reason:=reason
 sample_time+=dt
 if drive:drive_s+=dt
 else:spread_s+=dt
 var distance:=0.0 if discontinuity else moved
 total_m+=distance
 var hard_break:=impact or discontinuity or not drive or speed<float(cfg.drift.speed_mps) or slip>float(cfg.drift.slip_max_deg)
 qualifying=not hard_break and slip>=float(cfg.drift.slip_min_deg)
 var previous:=drift_s
 if hard_break:
  drift_s=0;grace_s=0;reason="impact" if impact else "relocation" if discontinuity else "Spread" if not drive else "speed" if speed<float(cfg.drift.speed_mps) else "line lost"
 elif qualifying:
  drift_s+=dt;grace_s=0;reason="drift";best_drift_s=maxf(best_drift_s,drift_s)
 else:
  grace_s+=dt;reason="correction" if grace_s<=float(cfg.drift.grace_s) and drift_s>0 else "straight"
  if grace_s>float(cfg.drift.grace_s):drift_s=0
 if previous>0 and drift_s==0:breaks+=1
 var clean:=drive and speed>=float(cfg.commit.speed_mps) and slip<=float(cfg.commit.slip_max_deg) and not impact and not discontinuity
 clean_drive_m=clean_drive_m+distance if clean else 0.0
 best_drive_m=maxf(best_drive_m,clean_drive_m)
 # Two distinct clean Drive legs separated by moving Spread, not two fragments
 # of one broken streak. Each leg and transfer is explicitly visible in the HUD.
 if impact or discontinuity:
  # Finished legs stay earned; a contact never joins unfinished fragments.
  transfer_m=0;second_leg_m=0
 if haul_phase==0 and clean_drive_m>=float(cfg.haul.first_leg_m):haul_phase=1
 elif haul_phase==1:
  if not drive and speed>=float(cfg.haul.spread_min_mps):transfer_m+=distance
  if drive and transfer_m<float(cfg.haul.transfer_m):transfer_m=0
  if transfer_m>=float(cfg.haul.transfer_m):haul_phase=2;second_leg_m=0
 elif haul_phase==2:
  second_leg_m=second_leg_m+distance if clean else 0.0
  if second_leg_m>=float(cfg.haul.second_leg_m):haul_phase=3
 # Optional South feature crossing. Delivery has no route requirement.
 if not thread_complete:
  if impact or discontinuity or drive or not thread_bounds.has_point(p):thread_active=false
  elif p.distance_to(thread_west)<=float(cfg.thread.approach_radius_m):thread_active=true
  if thread_active and p.distance_to(thread_east)<=float(cfg.thread.exit_radius_m):thread_complete=true
 snapshot={"drift_s":drift_s,"best_drift_s":best_drift_s,"qualifying":qualifying,"reason":reason,"grace_s":grace_s,"speed":speed,"slip":slip,"drive":drive,"impact":impact,"breaks":breaks,"clean_drive_m":clean_drive_m,"best_drive_m":best_drive_m,"haul_phase":haul_phase,"transfer_m":transfer_m,"second_leg_m":second_leg_m,"thread_active":thread_active,"thread_complete":thread_complete,"drive_s":drive_s,"spread_s":spread_s,"distance_m":total_m}
 if reason!=prior_reason or (previous>0 and drift_s==0):
  transitions.append({"time":sample_time,"from":prior_reason,"to":reason,"ended_combo_s":previous if drift_s==0 else 0.0,"evidence":snapshot.duplicate()})
  if transitions.size()>64:transitions.pop_front()
 return snapshot
