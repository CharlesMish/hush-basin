extends SceneTree
## Disposable route sampling: fixture placement only before each drive.
const Cargo = preload("res://scripts/courier/cargo_observer.gd")
const Brrr = preload("res://scripts/run/brrr_seed.gd")
class Fence:
	extends Node
	signal tail
	func _ready() -> void: process_physics_priority=1000
	func _physics_process(_delta: float) -> void: tail.emit()
var gate: P1AWorldGate
var craft: CraftController
var fence: Fence
var out := ""
var records: Array=[]
func _initialize() -> void: call_deferred("run")
func release() -> void:
	for a in ["throttle","brake","steer_left","steer_right","transform","hop"]: Input.action_release(a)
func ticks(n: int) -> void:
	for i in n: await fence.tail
func road(ids: Array) -> Array[Vector2]:
	var points: Array[Vector2]=[]
	for entry in ids:
		var reverse: bool=String(entry).begins_with("-")
		var id: String=String(entry).trim_prefix("-")
		var part: Array=gate.data.routes[id].points_xz_m.duplicate()
		if reverse: part.reverse()
		for p in part: points.append(P1AWorldData.xz(p))
	return points
func run() -> void:
	var args:=OS.get_cmdline_user_args()
	out=args[args.find("--output")+1]
	DirAccess.make_dir_recursive_absolute(out)
	gate=load("res://scenes/district_zero_p1a.tscn").instantiate()
	root.add_child(gate)
	fence=Fence.new();root.add_child(fence)
	await process_frame
	craft=gate.craft
	gate.get_node("UI").hide()
	gate.telemetry.set_physics_process(false)
	if "--views" in args:
		if "--landmark" in args:
			var lantern:=preload("res://scripts/courier/market_lantern.gd").new()
			lantern.manifest=gate.data.manifest;gate.world.add_child(lantern)
		await views()
	else:
		var pads: Dictionary=gate.data.manifest.destination_pads
		var mrk:=P1AWorldData.xz(pads.MRK.center_xz_m)
		var dep:=P1AWorldData.xz(pads.DEP.center_xz_m)
		var direct: Array[Vector2]=[mrk,dep]
		await drive("DEP_direct",direct)
		await drive("DEP_road",road(["-L1"]))
		await drive("RLY_spine",road(["-L5","-L4"]))
		await drive("RLY_west_sweep",road(["-L1","-L0","A1"]))
		await drive("WRK_works_way",road(["L6"]))
		await drive("WRK_east_approach",road(["L2","L3","-L7"]))
	FileAccess.open(out.path_join("study.json"),FileAccess.WRITE).store_string(JSON.stringify({"records":records,"method":"Unchanged craft; synthetic start, then ordinary input actions only. Driver is diagnostic, never shipped as control logic."},"  "))
	release();quit()
func drive(id: String, points: Array[Vector2]) -> void:
	release()
	var direction: Vector2=(points[1]-points[0]).normalized()
	var start:=points[0]
	craft.set_spawn_transform(Transform3D(Basis(Vector3.UP,atan2(-direction.x,-direction.y)),Vector3(start.x,gate.data.terrain_height_at(start.x,start.y)+1.65,start.y)))
	craft.reset_craft("alpha_route_initial_condition")
	gate.camera_rig.snap_to_target()
	await ticks(90)
	var cargo:=Cargo.new();cargo.begin(craft)
	var index:=0
	var elapsed:=0.0
	var brrr:=0.0
	var streak:=0.0
	var longest:=0.0
	var peak:=0.0
	var driven:=0.0
	var settled:=0.0
	var trace: Array=[]
	var initial_resets:=craft.reset_count
	var previous:=craft.global_position
	var finished:=false
	for tick in 7200:
		var p:=Vector2(craft.global_position.x,craft.global_position.z)
		var speed:=craft.velocity.length()
		# Ordered nearest sample, then look ahead along the unchanged road.
		if points.size()>2:
			var best:=INF
			for i in range(index,mini(index+200,points.size())):
				var d:=p.distance_squared_to(points[i])
				if d<best: best=d;index=i
		var ahead:=mini(index+int((8+speed*.4)/.25),points.size()-1)
		var far:=mini(index+int(42/.25),points.size()-1)
		var target:=points[ahead] if points.size()>2 else points[-1]
		var wanted:=atan2(-(target-p).x,-(target-p).y)
		var error:=wrapf(wanted-craft.rotation.y,-PI,PI)
		var distant_heading:=atan2(-(points[far]-p).x,-(points[far]-p).y)
		var bend:=absf(wrapf(distant_heading-wanted,-PI,PI))
		var remain:=p.distance_to(points[-1])
		var drive_form:=remain>60 and absf(error)<.14 and bend<.10
		var desired:=29.0 if drive_form else 12.0
		if remain<30 and index>points.size()-180: desired=maxf(0,(remain-2)*.42)
		if points.size()==2 and remain<30: desired=maxf(0,(remain-2)*.42)
		Input.action_press("steer_left",clampf(error*2,0,1))
		Input.action_press("steer_right",clampf(-error*2,0,1))
		if drive_form: Input.action_press("transform")
		else: Input.action_release("transform")
		if speed<desired and absf(error)<.8:
			Input.action_press("throttle");Input.action_release("brake")
		else:
			Input.action_release("throttle");Input.action_press("brake")
		await fence.tail
		cargo.sample(craft,1.0/60)
		elapsed+=1.0/60
		var expression:=Brrr.step(craft.velocity,-craft.global_basis.z,craft.regime_name()=="DRIVE",1.0/60,brrr,streak)
		brrr=expression.brrr;streak=expression.streak_s;longest=maxf(longest,streak);peak=maxf(peak,expression.speed)
		driven+=craft.global_position.distance_to(previous);previous=craft.global_position
		settled=settled+1.0/60 if remain<8 and speed<6 and craft.probe_hit_count>=2 else 0.0
		if tick%30==0: trace.append({"tick":tick,"position":[previous.x,previous.y,previous.z],"speed":speed,"drive":craft.regime_name()=="DRIVE","condition":cargo.condition_units})
		if settled>=.5: finished=true;break
		if craft.reset_count!=initial_resets:break
	var length:=0.0
	for i in range(1,points.size()):length+=points[i-1].distance_to(points[i])
	var row:={"id":id,"completed":finished,"elapsed":elapsed,"path_length":length,"driven_length":driven,"condition":cargo.condition_units,"brrr":brrr,"longest_streak":longest,"peak_speed":peak,"episodes":cargo.episodes,"trace":trace}
	records.append(row);print("ROUTE_STUDY ",id," finished=",finished," seconds=",elapsed," condition=",cargo.condition_units," streak=",longest)
	FileAccess.open(out.path_join(id+".json"),FileAccess.WRITE).store_string(JSON.stringify(row,"  "))
func views() -> void:
	craft.set_physics_process(false)
	var center:=Vector2.ZERO
	for landmark in gate.data.manifest.landmarks:
		if landmark.id=="MRK_FIN_N":center=P1AWorldData.xz(landmark.center_xz_m)
	var positions: Dictionary={}
	for id in ["MRK","DEP","RLY","WRK","CLN","QRY"]:positions[id]=P1AWorldData.xz(gate.data.manifest.destination_pads[id].center_xz_m)
	for id in ["A1","A2"]:
		var points: Array=gate.data.routes[id].points_xz_m
		positions[id]=P1AWorldData.xz(points[int(points.size()*.55)])
	for id in positions:
		var p: Vector2=positions[id]
		var d: Vector2=(center-p).normalized()
		craft.set_spawn_transform(Transform3D(Basis(Vector3.UP,atan2(-d.x,-d.y)),Vector3(p.x,gate.data.terrain_height_at(p.x,p.y)+1.65,p.y)))
		craft.reset_craft("market_landmark_view")
		gate.camera_rig.snap_to_target()
		for i in 30:await process_frame
		RenderingServer.force_draw(false)
		print("MARKET_VIEW ",id," visible=",root.visible)
		root.get_texture().get_image().save_png(out.path_join(id+".png"))
		records.append({"id":id,"craft":craft.global_position,"camera":gate.camera_rig.get_node("Camera").global_position})
