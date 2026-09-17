extends SceneTree
const Cargo = preload("res://scripts/courier/cargo_observer.gd")
class Fence:
	extends Node
	signal tail
	func _ready() -> void: process_physics_priority=1000
	func _physics_process(_delta: float) -> void: tail.emit()
var craft: CraftController
var fence: Fence
var checks: Array = []
var traces: Array = []

func _initialize() -> void: call_deferred("run")
func check(id: String, passed: bool, detail: Variant=null) -> void:
	checks.append({"id":id,"pass":passed,"detail":detail})
func release() -> void:
	for a in ["throttle","brake","steer_left","steer_right","hop","transform"]: Input.action_release(a)
func box(parent: Node3D, position: Vector3, size: Vector3, id: String) -> void:
	var body := StaticBody3D.new()
	body.position=position
	body.set_meta("source_geometry_id",id)
	var shape := CollisionShape3D.new()
	var data := BoxShape3D.new()
	data.size=size
	shape.shape=data
	body.add_child(shape)
	parent.add_child(body)
func run() -> void:
	var stage := Node3D.new()
	root.add_child(stage)
	box(stage,Vector3(0,-.5,0),Vector3(1000,1,1000),"HEIGHTFIELD_SUPPORT")
	box(stage,Vector3(0,10,-80),Vector3(1000,20,1),"TEST_WALL")
	craft=load("res://scenes/craft.tscn").instantiate()
	stage.add_child(craft)
	fence=Fence.new();root.add_child(fence)
	await process_frame
	for name in ["clean_drift","transform_brake","hop_landing","brush","glance","strike","pressure"]:
		release()
		var z := 60.0 if name in ["clean_drift","transform_brake","hop_landing"] else -77.5
		craft.set_spawn_transform(Transform3D(Basis.IDENTITY,Vector3(0,1.65,z)))
		craft.reset_craft("cargo-probe")
		for i in 60: await fence.tail
		var cargo := Cargo.new();cargo.begin(craft)
		var hops := craft.hop_count
		if name in ["brush","glance","strike"]:
			craft.velocity=Vector3(8,0,-({"brush":2.0,"glance":5.0,"strike":12.0}[name]))
		var valid := true
		var loss := 0
		for i in 480:
			if name=="clean_drift":
				Input.action_press("throttle");Input.action_press("transform");Input.action_press("steer_left")
			elif name=="transform_brake":
				if i<90: Input.action_press("throttle");Input.action_press("transform")
				else: release();Input.action_press("brake")
			elif name=="hop_landing":
				if i==15: Input.action_press("hop")
				if i==16: Input.action_release("hop")
			elif name=="pressure": Input.action_press("throttle");Input.action_press("transform")
			await fence.tail
			var sample: Dictionary=cargo.sample(craft,1.0/60.0)
			valid=valid and sample.valid
			loss += int(sample.loss)
		var record := {"id":name,"condition":cargo.condition_units,"loss":loss,"impacts":cargo.impact_samples,"episodes":cargo.episodes,"ignored":cargo.ignored_samples,"hops":craft.hop_count-hops,"supported":craft.probe_hit_count}
		traces.append(record)
		check(name+"_valid",valid,record)
		if name in ["clean_drift","transform_brake","hop_landing"]: check(name+"_no_damage",loss==0,record)
		if name=="hop_landing":check("supported_hop_exercised",craft.hop_count-hops==1 and craft.probe_hit_count==3)
		if name=="strike":check("strike_separates",loss>0)
		if name=="pressure":check("pressure_one_bounded_episode",cargo.episodes==1 and loss>0 and loss<=240,record)
	check("brush_glance_strike_order",traces[3].loss<traces[4].loss and traces[4].loss<traces[5].loss)
	var baseline_units := -1
	for hz in [30,60,120]:
		var c := Cargo.new()
		for i in hz*3:c.reduce(1.0/hz,true,.75,true)
		if baseline_units<0:baseline_units=c.condition_units
		check("rate_equivalent_"+str(hz),c.condition_units==baseline_units and c.episodes==1)
	var rising := Cargo.new()
	for severity in [.3,.5,.75,.5]:rising.reduce(1.0/60,true,severity,true)
	check("rising_peak_only",rising.condition_units==baseline_units)
	var zero := Cargo.new()
	for i in 5:
		zero.reduce(.3,false,0,false);zero.reduce(1.0/60,true,1,true)
	check("condition_clamps_at_zero",zero.condition_units==0)
	var failures: Array=[]
	for c in checks:
		if not c.pass:failures.append(c.id)
	var args:=OS.get_cmdline_user_args()
	FileAccess.open(args[args.find("--result")+1],FileAccess.WRITE).store_string(JSON.stringify({"status":"PASS" if failures.is_empty() else "FAIL","checks":checks,"failures":failures,"traces":traces},"  "))
	print("CARGO_PROBE ",JSON.stringify(traces)," FAILURES ",failures)
	quit(0 if failures.is_empty() else 1)
