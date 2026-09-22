extends "res://tests/alpha_route_study.gd"
## Review-only input scripts. Reset/placement only before a run; never while driving.
var plans: Array=[]
func run() -> void:
 var args:=OS.get_cmdline_user_args()
 out=args[args.find("--output")+1];DirAccess.make_dir_recursive_absolute(out)
 plans=JSON.parse_string(FileAccess.get_file_as_string(args[args.find("--plans")+1]))
 gate=load("res://scenes/district_zero_p1a.tscn").instantiate();root.add_child(gate)
 fence=Fence.new();root.add_child(fence);await process_frame
 craft=gate.craft;gate.get_node("UI").hide();gate.telemetry.set_physics_process(false)
 if "--geometry" in args:
  var feature=load("res://scripts/courier/mechanics_feature.gd").new();feature.gate=gate;gate.world.add_child(feature)
 for plan in plans:await sample(plan)
 FileAccess.open(out.path_join("matrix.json"),FileAccess.WRITE).store_string(JSON.stringify(records,"  "))
 release();quit()
func sample(plan: Dictionary) -> void:
 var points: Array[Vector2]=[]
 if plan.has("routes"):points=road(plan.routes)
 else:
  for p in plan.points:points.append(Vector2(p[0],p[1]))
 release()
 var start:=points[0];var direction: Vector2=(points[1]-start).normalized()
 craft.set_spawn_transform(Transform3D(Basis(Vector3.UP,atan2(-direction.x,-direction.y)),Vector3(start.x,gate.data.terrain_height_at(start.x,start.y)+1.65,start.y)))
 craft.reset_craft("mechanics_calibration_initial_condition");gate.camera_rig.snap_to_target();await ticks(90)
 var cargo:=Cargo.new();cargo.begin(craft)
 var index:=0;var brrr:=0.0;var streak:=0.0;var longest:=0.0;var slip_points:=0.0;var peak_split:=0.0;var settled:=0.0;var completed:=false;var trace: Array=[];var seconds:=0.0;var initial_resets:=craft.reset_count;var latch:=false
 for tick in int(plan.get("ticks",4200)):
  var p:=Vector2(craft.global_position.x,craft.global_position.z);var speed:=Vector2(craft.velocity.x,craft.velocity.z).length()
  if points.size()>2:
   var best:=INF
   for i in range(index,mini(index+240,points.size())):
    var d:=p.distance_squared_to(points[i])
    if d<best:best=d;index=i
  var effective_look:=float(plan.get("look",12)) if latch else 12.0
  var ahead:=mini(index+int((effective_look+speed*float(plan.get("anticipation",.5)))/.25),points.size()-1)
  var target:=points[ahead] if points.size()>2 else points[-1]
  var wanted:=atan2(-(target-p).x,-(target-p).y)
  var error:=wrapf(wanted-craft.rotation.y,-PI,PI)
  var remain:=p.distance_to(points[-1])
  var bend:=0.0
  if points.size()>2:
   var far:=mini(index+168,points.size()-1)
   bend=absf(wrapf(atan2(-(points[far]-p).x,-(points[far]-p).y)-wanted,-PI,PI))
  var drive_form:=remain>60 and absf(error)<.14 and bend<.10
  if plan.get("committed",false):
   if index>=int(plan.get("drive_index",0)) and absf(error)<.2:latch=true
   drive_form=latch and remain>float(plan.get("unfold_remaining",27))
  if plan.get("spread",false):drive_form=false
  var course:=atan2(-craft.velocity.x,-craft.velocity.z) if speed>1 else craft.rotation.y
  var steer:=clampf((error+float(plan.get("course_gain",0))*wrapf(wanted-course,-PI,PI))*float(plan.get("steer_gain",2)), -1,1)
  var desired:=float(plan.get("speed",30)) if drive_form else 12.0
  if remain<30 and (points.size()==2 or index>points.size()-180):desired=maxf(0,(remain-2)*.42)
  var seconds_now:=tick/60.0
  for maneuver in plan.get("maneuvers",[]):
   if seconds_now>=float(maneuver.start) and seconds_now<float(maneuver.end):
    drive_form=bool(maneuver.drive);steer=float(maneuver.steer);desired=float(maneuver.get("speed",30))
  if (plan.has("hop_distance") and remain<float(plan.hop_distance) and remain>float(plan.hop_distance)-2) or (seconds_now>=float(plan.get("hop_start_s",999)) and seconds_now<float(plan.get("hop_end_s",999))):Input.action_press("hop")
  else:Input.action_release("hop")
  Input.action_press("steer_left",maxf(steer,0));Input.action_press("steer_right",maxf(-steer,0))
  if drive_form:Input.action_press("transform")
  else:Input.action_release("transform")
  if speed<desired and (absf(error)<.8 or drive_form):Input.action_press("throttle");Input.action_release("brake")
  else:Input.action_release("throttle");Input.action_press("brake")
  await fence.tail
  cargo.sample(craft,1.0/60)
  var expression:=Brrr.step(craft.velocity,-craft.global_basis.z,craft.regime_name()=="DRIVE",1.0/60,brrr,streak)
  var earned: float=expression.brrr-brrr
  slip_points+=earned*float(expression.split_degrees)/(30.0+float(expression.split_degrees))
  brrr=expression.brrr;streak=expression.streak_s;longest=maxf(longest,streak);peak_split=maxf(peak_split,float(expression.split_degrees));seconds=(tick+1)/60.0
  settled=settled+1.0/60 if remain<8 and speed<6 and craft.probe_hit_count>=2 else 0.0
  if tick%6==0:trace.append({"tick":tick,"position":[craft.global_position.x,craft.global_position.y,craft.global_position.z],"speed":speed,"form":craft.regime_name(),"split":expression.split_degrees,"streak":streak,"brrr":brrr,"slip_points":slip_points,"condition":cargo.condition_units,"closing":craft.last_impact_closing_speed,"impact":craft.impact_count,"hop":craft.hop_count})
  if settled>=.5:completed=true;break
  if craft.reset_count!=initial_resets:break
 var row:={"plan":plan,"completed":completed,"seconds":seconds,"brrr":brrr,"slip_points":slip_points,"longest_streak":longest,"peak_split":peak_split,"condition":cargo.condition_units,"episodes":cargo.episodes,"trace":trace}
 records.append(row);FileAccess.open(out.path_join(String(plan.id)+".json"),FileAccess.WRITE).store_string(JSON.stringify(row,"  "));print("CALIBRATION ",plan.id," ",completed," time=",seconds," slip=",slip_points," streak=",longest," cargo=",cargo.condition_units)
