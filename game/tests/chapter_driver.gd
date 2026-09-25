extends RefCounted
## Chapter fixture only: the free-roam target is a coordinate, not any nearby hub.
## Test-only ordinary-input driver; no pose/velocity writes while driving.
static func road(gate: P1AWorldGate, ids: Array) -> Array[Vector2]:
	var points: Array[Vector2]=[]
	for entry in ids:
		var part: Array=gate.data.routes[String(entry).trim_prefix("-")].points_xz_m.duplicate()
		if String(entry).begins_with("-"):part.reverse()
		for p in part:points.append(P1AWorldData.xz(p))
	return points
static func release() -> void:
	for a in ["throttle","brake","steer_left","steer_right","transform","hop"]:Input.action_release(a)
static func drive(probe: Node, points: Array[Vector2], cautious: bool=false, home: bool=false) -> Dictionary:
	var craft: CraftController=probe.craft
	var index:=0
	var initial_resets:=craft.reset_count
	var trace: Array=[]
	var settled:=0.0
	var focus_recoveries:=0
	for tick in 6000:
		if probe.job.state!=("FREE_ROAM" if home else "ACTIVE"):break
		# Respect the unchanged controller's focus-loss neutral-input gate.
		# A diagnostic must release like a player, never clear the lock itself.
		if craft.get("_input_locked_until_release"):
			release();await probe.tail;await probe.tail
			focus_recoveries+=1
			continue
		var p:=Vector2(craft.global_position.x,craft.global_position.z)
		var speed:=craft.velocity.length()
		if points.size()>2:
			var best:=INF
			for i in range(index,mini(index+200,points.size())):
				var d:=p.distance_squared_to(points[i])
				if d<best:best=d;index=i
		var lookahead:=4+speed*.3 if cautious else 8+speed*.4
		var ahead:=mini(index+int(lookahead/.25),points.size()-1)
		var far:=mini(index+168,points.size()-1)
		var target:=points[ahead] if points.size()>2 else points[-1]
		var wanted:=atan2(-(target-p).x,-(target-p).y)
		var error:=wrapf(wanted-craft.rotation.y,-PI,PI)
		var distant:=atan2(-(points[far]-p).x,-(points[far]-p).y)
		var bend:=absf(wrapf(distant-wanted,-PI,PI))
		var remain:=p.distance_to(points[-1])
		var drive_form:=not cautious and remain>60 and absf(error)<.14 and bend<.10
		var desired:=29.0 if drive_form else 8.0 if cautious else 12.0
		if remain<30 and (points.size()==2 or index>points.size()-180):desired=maxf(0,(remain-2)*.42)
		Input.action_press("steer_left",clampf(error*2,0,1));Input.action_press("steer_right",clampf(-error*2,0,1))
		if drive_form:Input.action_press("transform")
		else:Input.action_release("transform")
		if speed<desired and absf(error)<.8:
			Input.action_press("throttle");Input.action_release("brake")
		else:Input.action_release("throttle");Input.action_press("brake")
		await probe.tail
		if home:
			settled=settled+1.0/60 if p.distance_to(points[-1])<3.5 and speed<2.0 and probe.job._supported() else 0.0
			if settled>=.5:break
		if tick%30==0:trace.append({"tick":tick,"position":[craft.global_position.x,craft.global_position.y,craft.global_position.z],"speed":speed,"condition":probe.job.cargo.condition_units,"drive":craft.regime_name()=="DRIVE"})
		if probe.clip_frames and probe.route_id in ["DEP_direct","DEP_home","RLY_spine"] and tick%12==0:await probe.capture("route_%s_%04d" % [probe.route_id,tick/12])
		if craft.reset_count!=initial_resets:break
	release()
	return {"delivered":probe.job.state=="RESULTS" and probe.job.last_result.get("delivered",false),"arrived_home":home and settled>=.5,"reset_delta":craft.reset_count-initial_resets,"focus_recoveries":focus_recoveries,"trace":trace,"receipt":probe.job.last_result}
