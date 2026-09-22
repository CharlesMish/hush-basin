extends SceneTree
const Profile = preload("res://scripts/courier/trail_ribbon_profile.gd")
const Trail = preload("res://scripts/courier/slip_trail.gd")
var checks: Dictionary = {}
var cfg: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://presentation/default_trail_v1.json"))

func _initialize() -> void:
	call_deferred("run")

func row(p: Vector3, age: float, slip: float, broken: bool = false) -> Dictionary:
	return {"p": p, "right": Vector3.RIGHT, "age": age, "slip": slip, "streak": slip, "break_before": broken}

func run() -> void:
	var history: Array = []
	for i in range(18):
		history.append(row(Vector3(sin(i * .07) * 8, .5, -i), (17 - i) / 30.0, 1.0, i == 0))
	var frame := Profile.frames(history, 1.0, cfg)
	var finite := true
	var bounded := true
	for point in frame:
		finite = finite and point.center.is_finite() and point.right.is_finite() and is_finite(point.alpha) and is_finite(point.width)
		bounded = bounded and point.alpha >= 0 and point.alpha <= float(cfg.drift_alpha) and point.width >= 0 and point.width <= float(cfg.drift_half_width_m)
	checks["finite_curved_geometry"] = finite
	checks["bounded_width_and_alpha"] = bounded
	checks["old_tail_point_and_transparent"] = frame[0].width == 0 and frame[0].alpha == 0
	checks["continuous_age_fade"] = frame[1].alpha < frame[8].alpha and frame[8].alpha < frame[17].alpha
	var straight := history.duplicate(true)
	for point in straight:
		point.slip = 0.0
		point.streak = 0.0
	var straight_frame := Profile.frames(straight, 1.0, cfg)
	checks["qualifying_drift_wider_and_brighter"] = frame[17].width > straight_frame[17].width * 4 and frame[17].alpha > straight_frame[17].alpha * 4
	var broken := history.duplicate(true)
	broken[9].break_before = true
	var broken_frame := Profile.frames(broken, 1.0, cfg)
	checks["non_emitting_interval_starts_new_tail"] = broken_frame[9].width == 0 and broken_frame[9].break_before
	# Inspect real generated geometry; shared seam vertices must match exactly.
	var trail := Trail.new()
	trail.cfg = cfg
	trail.history = history
	trail.rebuild()
	var arrays := trail.trail_mesh.surface_get_arrays(0)
	var vertices: PackedVector3Array = arrays[Mesh.ARRAY_VERTEX]
	var colors: PackedColorArray = arrays[Mesh.ARRAY_COLOR]
	checks["one_surface_bounded_vertices"] = trail.trail_mesh.get_surface_count() == 1 and vertices.size() == 408
	checks["native_feather_edges_transparent"] = colors[121].a == 0 and colors[122].a == 0 and colors[125].a > 0
	checks["adjacent_ribbon_shared_center"] = vertices[5] == vertices[12]
	checks["adjacent_ribbon_shared_edge"] = vertices[2] == vertices[13]
	trail.history = broken
	trail.rebuild()
	checks["gap_not_bridged"] = trail.trail_mesh.surface_get_arrays(0)[Mesh.ARRAY_VERTEX].size() == 384
	trail.history = [row(Vector3.ZERO, .1, 0, true), row(Vector3.ZERO, 0, 0, true)]
	trail.rebuild()
	checks["no_empty_render_surface"] = trail.trail_mesh.get_surface_count() == 0
	trail.history = history
	trail.rebuild()
	trail.clear()
	checks["clear_removes_history_and_mesh"] = trail.history.is_empty() and trail.trail_mesh.get_surface_count() == 0 and trail.next_break
	trail.free()
	var good := true
	for value in checks.values():
		good = good and value
	var result := {"status": "PASS" if good else "FAIL", "checks": checks, "maximum_vertices": 408}
	var args := OS.get_cmdline_user_args()
	if "--result" in args:
		FileAccess.open(args[args.find("--result") + 1], FileAccess.WRITE).store_string(JSON.stringify(result, "  "))
	print("DEFAULT_TRAIL_PROBE " + JSON.stringify(result))
	quit(0 if good else 1)
