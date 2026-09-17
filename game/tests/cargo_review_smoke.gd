extends SceneTree
class Fence:
	extends Node
	signal tail
	func _ready() -> void:
		process_mode = Node.PROCESS_MODE_ALWAYS
		process_physics_priority = 1000
	func _physics_process(_delta: float) -> void: tail.emit()
var checks: Dictionary = {}
var fence: Fence
func _initialize() -> void: call_deferred("run")
func ticks(n: int) -> void:
	for i in n: await fence.tail
func key(code: Key) -> void:
	var event := InputEventKey.new()
	event.physical_keycode=code;event.keycode=code;event.pressed=true
	root.push_input(event)
	event=event.duplicate();event.pressed=false;root.push_input(event)
func run() -> void:
	var args := OS.get_cmdline_user_args()
	var out := args[args.find("--result")+1]
	var scene: Node = load("res://review/cargo_v1_1/cargo_review.tscn").instantiate()
	root.add_child(scene)
	fence=Fence.new();root.add_child(fence)
	await ticks(120)
	var job: Node=scene.job
	var craft: CraftController=scene.craft
	checks["review_ready"] = scene.initialized and job.can_dispatch()
	key(KEY_E);key(KEY_ENTER)
	await ticks(15)
	checks["review_accepts_same_job"] = job.state=="ACTIVE"
	# Explicit synthetic initial placement, then real wall contact and unchanged
	# controller. This is an audit/logger test, not a driven courier completion.
	craft.global_transform=Transform3D(Basis(Vector3.UP,PI/2),Vector3(-310,job.gate.data.terrain_height_at(-310,20)+1.65,20))
	craft.velocity=Vector3(-16,0,0)
	craft.reset_physics_interpolation()
	job.gate.camera_rig.snap_to_target()
	await ticks(120)
	checks["genuine_world_contact_recorded"] = not scene.last_loss.is_empty() and scene.last_loss.incremental_loss_units>0 and scene.last_loss.same_physics_frame
	if not scene.last_loss.is_empty():
		checks["receipt_matches_condition"] = scene.last_loss.cumulative_loss_units==1000-job.cargo.condition_units
		checks["record_has_required_evidence"] = scene.last_loss.has_all(["pre_impact_world_speed","impact_closing_speed","impact_severity","form","impact_counter","cargo_episode","episode_peak_units","incremental_loss_units","cumulative_loss_units"])
	key(KEY_F3)
	var lines := FileAccess.get_file_as_string(scene.log_path).strip_edges().split("\n")
	checks["bookmark_persisted"] = JSON.parse_string(lines[-1]).event=="owner_bookmark"
	key(KEY_ESCAPE)
	var units: int=job.cargo.condition_units
	await ticks(30)
	checks["pause_no_charge"] = paused and job.cargo.condition_units==units
	key(KEY_ESCAPE);await ticks(6)
	key(KEY_F2)
	checks["panel_toggle"] = not scene.panel.visible
	key(KEY_F2)
	if DisplayServer.get_name()!="headless":
		await process_frame
		await RenderingServer.frame_post_draw
		root.get_texture().get_image().save_png(out.get_base_dir().path_join("cargo-receipt.png"))
	var good:=true
	for value in checks.values():good=good and value
	FileAccess.open(out,FileAccess.WRITE).store_string(JSON.stringify({"status":"PASS" if good else "FAIL","checks":checks,"last_loss":scene.last_loss,"log_path":scene.log_path},"  "))
	print("CARGO_REVIEW_SMOKE ",checks)
	paused=false
	quit(0 if good else 1)
