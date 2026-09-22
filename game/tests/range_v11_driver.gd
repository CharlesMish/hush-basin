extends "res://tests/alpha_input_driver.gd"
const OldDriver=preload("res://tests/alpha_input_driver.gd")
static func drive(probe: Node, points: Array[Vector2], cautious: bool=false, home: bool=false) -> Dictionary:
 var plans: Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://tests/fixtures/range_v11_lines.json"))
 if not plans.has(probe.route_id):return await OldDriver.drive(probe,points,cautious,home)
 var plan: Dictionary=plans[probe.route_id]
 var craft: CraftController=probe.craft
 # Organize the craft at Market with ordinary Spread steering/braking. This
 # explicitly includes setup time and avoids relying on a synthetic launch yaw.
 var initial: Vector2=(points[1]-points[0]).normalized()
 var heading:=atan2(-initial.x,-initial.y)+deg_to_rad(float(plan.get("heading_offset",0)))
 for setup in 150:
  release();Input.action_press("brake")
  var turn:=wrapf(heading-craft.rotation.y,-PI,PI)
  Input.action_press("steer_left",clampf(turn*3,0,1));Input.action_press("steer_right",clampf(-turn*3,0,1))
  await probe.tail
  if absf(turn)<.015 and craft.velocity.length()<.2:break
 release()
 var index:=0;var settled:=0.0;var completed:=false;var trace: Array=[];var seconds:=0.0;var initial_resets:=craft.reset_count;var latch:=false
 for tick in int(plan.get("ticks",4200)):
  if probe.job.state!="ACTIVE":break
  if craft.get("_input_locked_until_release"):
   release();await probe.tail;await probe.tail;continue
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
  for phase in plan.get("phases",[]):
   if index>=int(phase.start_index) and index<int(phase.end_index):
    drive_form=bool(phase.drive)
    if phase.has("look"):
     target=points[mini(index+int(float(phase.look)/.25),points.size()-1)];wanted=atan2(-(target-p).x,-(target-p).y);error=wrapf(wanted-craft.rotation.y,-PI,PI)
  var course:=atan2(-craft.velocity.x,-craft.velocity.z) if speed>1 else craft.rotation.y
  var steer:=clampf((error+float(plan.get("course_gain",0))*wrapf(wanted-course,-PI,PI))*float(plan.get("steer_gain",2)), -1,1)
  var desired:=float(plan.get("speed",30)) if drive_form else float(plan.get("spread_speed",12.0))
  if remain<30 and (points.size()==2 or index>points.size()-180):desired=maxf(0,(remain-2)*.42)
  for phase in plan.get("phases",[]):
   if index>=int(phase.start_index) and index<int(phase.end_index):desired=float(phase.get("speed",desired))
  var seconds_now:=tick/60.0
  for maneuver in plan.get("maneuvers",[]):
   if seconds_now>=float(maneuver.start) and seconds_now<float(maneuver.end):
    drive_form=bool(maneuver.drive);steer=float(maneuver.steer);desired=float(maneuver.get("speed",30))
  var south_center: Vector2=(probe.job.lines.thread_west+probe.job.lines.thread_east)*.5
  var south_trigger: float=south_center.x-speed*craft.tuning.hop_tangential_retention*craft.tuning.hop_normal_speed/craft.tuning.gravity-.15
  if (plan.get("south_hop",false) and p.x>=south_trigger and p.x<south_center.x-1.85 and absf(p.y-south_center.y)<4) or (plan.has("hop_distance") and remain<float(plan.hop_distance) and remain>float(plan.hop_distance)-2) or (seconds_now>=float(plan.get("hop_start_s",999)) and seconds_now<float(plan.get("hop_end_s",999))):Input.action_press("hop")
  else:Input.action_release("hop")
  Input.action_press("steer_left",maxf(steer,0));Input.action_press("steer_right",maxf(-steer,0))
  if drive_form:Input.action_press("transform")
  else:Input.action_release("transform")
  if speed<desired and (absf(error)<.8 or drive_form):Input.action_press("throttle");Input.action_release("brake")
  else:Input.action_release("throttle");Input.action_press("brake")
  await probe.tail
  if tick%30==0:trace.append({"tick":tick,"position":[craft.global_position.x,craft.global_position.y,craft.global_position.z],"speed":speed,"condition":probe.job.cargo.condition_units,"streak":probe.job.streak,"slip_brrr":probe.job.slip_brrr,"lines":probe.job.lines.snapshot.duplicate(),"route_index":index})
  if probe.clip_frames and tick%12==0:await probe.capture("route_%s_%04d" % [probe.route_id,tick/12])
  if craft.reset_count!=initial_resets:break
 release()
 return {"delivered":probe.job.state=="RESULTS" and probe.job.last_result.get("delivered",false),"arrived_home":false,"focus_recoveries":0,"reset_delta":craft.reset_count-initial_resets,"trace":trace,"receipt":probe.job.last_result}
