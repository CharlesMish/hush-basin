extends MeshInstance3D
## Bounded world-space visual observer. Never writes craft or BRRR state.
const Metric = preload("res://scripts/run/brrr_seed.gd")
const Palette = preload("res://scripts/courier/mastery_trail_palette.gd")
const Profile = preload("res://scripts/courier/trail_ribbon_profile.gd")
var trail_style := "standard"
var craft: CraftController
var cfg: Dictionary
var history: Array = []
var metric_streak := 0.0
var sample_clock := 0.0
var trail_mesh := ImmediateMesh.new()
var last_sample: Dictionary = {}
var feedback = preload("res://scripts/courier/line_evidence.gd").new()
var next_break := true

func _ready() -> void:
	name = "SlipFeedbackTrail"
	process_physics_priority = 260
	process_mode = Node.PROCESS_MODE_PAUSABLE
	cfg = JSON.parse_string(FileAccess.get_file_as_string("res://presentation/default_trail_v1.json"))
	mesh = trail_mesh
	cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	var material := StandardMaterial3D.new()
	material.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	material.vertex_color_use_as_albedo = true
	material.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	material.cull_mode = BaseMaterial3D.CULL_DISABLED
	material.no_depth_test = false
	material_override = material
	feedback.begin(craft)
	craft.reset_performed.connect(func(_n, _reason): clear())

func clear() -> void:
	history.clear()
	trail_mesh.clear_surfaces()
	metric_streak = 0
	sample_clock = 0
	next_break = true
	if is_instance_valid(craft):
		feedback.begin(craft)

func _physics_process(delta: float) -> void:
	if not is_instance_valid(craft) or not craft.is_physics_processing():
		return
	last_sample = Metric.step(craft.velocity, -craft.global_basis.z, craft.regime_name() == "DRIVE", delta, 0, metric_streak)
	var signal_state := feedback.sample(craft, delta)
	if signal_state.impact or feedback.reason == "relocation":
		history.clear()
		next_break = true
	metric_streak = last_sample.streak_s
	for point in history:
		point.age += delta
	while not history.is_empty() and float(history[0].age) > float(cfg.history_seconds):
		history.pop_front()
	# An unfolded/slow interval never joins two separate tracks. Earlier light
	# simply fades where it was emitted; it cannot extend a qualifying chain.
	if not last_sample.qualifying:
		next_break = true
	sample_clock += delta
	if sample_clock >= 1.0 / float(cfg.sample_hz):
		sample_clock = fmod(sample_clock, 1.0 / float(cfg.sample_hz))
		if last_sample.qualifying and not signal_state.impact:
			var position_sample := craft.global_position + craft.global_basis.z * float(cfg.stern_offset_m) - Vector3.UP * float(cfg.vertical_offset_m)
			if not history.is_empty() and position_sample.distance_to(history[-1].p) > float(cfg.maximum_join_m):
				history.clear()
				next_break = true
			var strength := 1.0 if feedback.qualifying else 0.0
			history.append({"p": position_sample, "right": craft.global_basis.x, "age": 0.0,
				"slip": clampf(float(last_sample.split_degrees) / 45.0, 0, 1) * strength,
				"streak": clampf(feedback.drift_s / 3.5, 0, 1), "break_before": next_break})
			next_break = false
	while history.size() > int(cfg.max_samples):
		history.pop_front()
	rebuild()

func rebuild() -> void:
	trail_mesh.clear_surfaces()
	if history.size() < 2:
		return
	var surface_open := false
	for side in [-1.0, 1.0]:
		var frames := Profile.frames(history, side, cfg)
		for i in range(1, frames.size()):
			var a: Dictionary = frames[i - 1]
			var b: Dictionary = frames[i]
			if b.break_before or a.center.distance_squared_to(b.center) < 0.0001:
				continue
			if not surface_open:
				trail_mesh.surface_begin(Mesh.PRIMITIVE_TRIANGLES)
				surface_open = true
			# Two feathered halves share their center and all adjacent-section
			# vertices. Native vertex alpha supplies the soft edge: no shader,
			# texture, second render pass or camera-facing billboard is needed.
			for band in [-1.0, 1.0]:
				for entry in [[a.center, a, 1.0], [a.center + a.right * a.width * band, a, 0.0],
					[b.center + b.right * b.width * band, b, 0.0], [a.center, a, 1.0],
					[b.center + b.right * b.width * band, b, 0.0], [b.center, b, 1.0]]:
					var row: Dictionary = entry[1]
					var color := Palette.color_for(trail_style, float(row.slip))
					color.a = float(row.alpha) * float(entry[2])
					trail_mesh.surface_set_color(color)
					trail_mesh.surface_add_vertex(entry[0])
	if surface_open:
		trail_mesh.surface_end()
