extends Node3D
## Builds the Hem Loop yard: floor, walls, loading dock, markings, gantry,
## lamps and Depot sheds. Every collider is on the shared World layer (1),
## so the unchanged craft probes and camera obstruction ray treat it like the
## Basin. Decorative buildings sit behind the walls and have no collision.

const Course = preload("res://rink/rink_course.gd")
const PALETTE_PATH := "res://world/world_polish_v1.json"
const WORLD_LAYER := 1

var course: Course
var palette: Dictionary = {}
var tess_anchor: Node3D
var chalkboard_label: Label3D
var gate_light: MeshInstance3D
var hard_bodies: Array[StaticBody3D] = []
var _materials: Dictionary = {}
var _static_meshes: Array[MeshInstance3D] = []


func build(source: Course) -> void:
	course = source
	var cfg: Variant = JSON.parse_string(FileAccess.get_file_as_string(PALETTE_PATH))
	palette = (cfg as Dictionary).get("palette", {}) if typeof(cfg) == TYPE_DICTIONARY else {}
	_build_floor()
	_build_track_surface()
	_build_walls()
	_build_dock()
	_build_markings()
	_build_gantry()
	_build_hem_apex()
	_build_crane()
	_build_lamps()
	_build_sheds()


func color(key: String, fallback: Color = Color(0.5, 0.5, 0.5)) -> Color:
	if not palette.has(key):
		return fallback
	var c: Array = palette[key]
	return Color(c[0], c[1], c[2])


func material(key: String, albedo: Color = Color(0.5, 0.5, 0.5), roughness: float = 0.85, emission: Color = Color.BLACK, energy: float = 0.0) -> StandardMaterial3D:
	if _materials.has(key):
		return _materials[key]
	var m := StandardMaterial3D.new()
	m.albedo_color = albedo
	m.roughness = roughness
	if energy > 0.0:
		m.emission_enabled = true
		m.emission = emission
		m.emission_energy_multiplier = energy
	_materials[key] = m
	return m


func static_meshes() -> Array[MeshInstance3D]:
	return _static_meshes


## Same contract as the Basin's P1AWorldBuilder: walls and the Hop buffer are
## hard geometry the craft can strike or slide along, never hover support.
func exclude_hard_geometry_from_support(craft: CraftController) -> void:
	for probe_name in ["ProbeLeft", "ProbeRight", "ProbeRear"]:
		var probe := craft.get_node(probe_name) as RayCast3D
		for body in hard_bodies:
			probe.add_exception(body)


## Wall collision as a chain of convex prisms (like the Basin's exact wall prisms).
func _wall_prisms(side: float, height: float, thickness: float, node_name: String) -> StaticBody3D:
	var body := StaticBody3D.new()
	body.name = node_name
	body.collision_layer = WORLD_LAYER
	body.collision_mask = 0
	add_child(body)
	hard_bodies.append(body)
	var s := 0.0
	while s < course.length - 0.001:
		var pose := course.pose_at(s)
		var step := 6.0 if absf(float(pose.k)) < 0.0001 and absf(float(course.pose_at(s + 6.0).k)) < 0.0001 else 1.0
		var s1 := minf(s + step, course.length)
		var pts := PackedVector3Array()
		for at in [s, s1]:
			var p := course.pose_at(at)
			var lf := Course.left_of(p.f)
			var lateral := float(p.wl) if side > 0.0 else -float(p.wr)
			var face: Vector2 = p.p + lf * lateral
			var back: Vector2 = face + lf * side * thickness
			for y in [0.0, height]:
				pts.append(Vector3(face.x, y, face.y))
				pts.append(Vector3(back.x, y, back.y))
		var shape := ConvexPolygonShape3D.new()
		shape.points = pts
		var cs := CollisionShape3D.new()
		cs.shape = shape
		body.add_child(cs)
		s = s1
	return body


# --- mesh helpers -----------------------------------------------------------

func _add_mesh(mesh: Mesh, mat: Material, node_name: String, parent: Node3D = self) -> MeshInstance3D:
	var mi := MeshInstance3D.new()
	mi.name = node_name
	mi.mesh = mesh
	mi.material_override = mat
	parent.add_child(mi)
	_static_meshes.append(mi)
	return mi


func _collide(mesh: ArrayMesh, node_name: String) -> StaticBody3D:
	var body := StaticBody3D.new()
	body.name = node_name
	body.collision_layer = WORLD_LAYER
	body.collision_mask = 0
	var shape_node := CollisionShape3D.new()
	var shape := mesh.create_trimesh_shape() as ConcavePolygonShape3D
	shape.backface_collision = true
	shape_node.shape = shape
	body.add_child(shape_node)
	add_child(body)
	return body


func _box(parent: Node3D, center: Vector3, size: Vector3, mat: Material, yaw: float = 0.0, solid: bool = false, hard: bool = false) -> MeshInstance3D:
	var mesh := BoxMesh.new()
	mesh.size = size
	var mi := MeshInstance3D.new()
	mi.mesh = mesh
	mi.material_override = mat
	mi.transform = Transform3D(Basis(Vector3.UP, yaw), center)
	parent.add_child(mi)
	_static_meshes.append(mi)
	if solid:
		var body := StaticBody3D.new()
		body.collision_layer = WORLD_LAYER
		body.collision_mask = 0
		var cs := CollisionShape3D.new()
		var shape := BoxShape3D.new()
		shape.size = size
		cs.shape = shape
		body.add_child(cs)
		body.transform = mi.transform
		parent.add_child(body)
		if hard:
			hard_bodies.append(body)
	return mi


func _label(parent: Node3D, text: String, at: Vector3, yaw: float, pixel: float, tint: Color, font_size: int = 64) -> Label3D:
	var label := Label3D.new()
	label.text = text
	label.font_size = font_size
	label.pixel_size = pixel
	label.modulate = tint
	label.outline_size = 0
	label.double_sided = false
	label.transform = Transform3D(Basis(Vector3.UP, yaw), at)
	parent.add_child(label)
	return label


## Quad strip between two lateral offsets along the course, at height y.
func _ribbon(s0: float, s1: float, lat_a: Callable, lat_b: Callable, y: float, step: float = 1.0, closed: bool = false) -> ArrayMesh:
	var st := SurfaceTool.new()
	st.begin(Mesh.PRIMITIVE_TRIANGLES)
	var count := maxi(1, int(ceil((s1 - s0) / step)))
	var prev_a := Vector3.ZERO
	var prev_b := Vector3.ZERO
	for i in count + 1:
		var s := s0 + (s1 - s0) * float(i) / float(count)
		if closed and i == count:
			s = s0
		var pa: Vector2 = course.edge_point(s, float(lat_a.call(s)))
		var pb: Vector2 = course.edge_point(s, float(lat_b.call(s)))
		var a := Vector3(pa.x, y, pa.y)
		var b := Vector3(pb.x, y, pb.y)
		if i > 0:
			st.set_normal(Vector3.UP)
			st.set_uv(Vector2(0, s)); st.add_vertex(prev_a)
			st.set_uv(Vector2(1, s)); st.add_vertex(b)
			st.set_uv(Vector2(1, s)); st.add_vertex(prev_b)
			st.set_uv(Vector2(0, s)); st.add_vertex(prev_a)
			st.set_uv(Vector2(0, s)); st.add_vertex(a)
			st.set_uv(Vector2(1, s)); st.add_vertex(b)
		prev_a = a
		prev_b = b
	return st.commit()


# --- floor and track ----------------------------------------------------------

func _build_floor() -> void:
	var plane := PlaneMesh.new()
	plane.size = Vector2(1400, 1400)
	var floor_mi := _add_mesh(plane, material("yard", color("yard", Color(0.40, 0.32, 0.22)), 0.86), "YardFloor")
	floor_mi.position = Vector3(110, 0, -80)
	var body := StaticBody3D.new()
	body.name = "YardFloorCollision"
	body.collision_layer = WORLD_LAYER
	body.collision_mask = 0
	var cs := CollisionShape3D.new()
	var shape := BoxShape3D.new()
	shape.size = Vector3(1400, 2, 1400)
	cs.shape = shape
	cs.position = Vector3(110, -1, -80)
	body.add_child(cs)
	add_child(body)


func _wl(s: float) -> float:
	return float(course.pose_at(s).wl)


func _wr(s: float) -> float:
	return float(course.pose_at(s).wr)


func _build_track_surface() -> void:
	var asphalt := color("paving", Color(0.16, 0.2, 0.2)) * 0.93
	asphalt.a = 1.0
	var mesh := _ribbon(0.0, course.length, func(s): return _wl(s) + 0.4, func(s): return -_wr(s) - 0.4, 0.012, 1.0, true)
	_add_mesh(mesh, material("asphalt", asphalt, 0.56), "TrackSurface")
	# Wet patches: darker, glossier puddles where the yard dips.
	var puddle := material("puddle", asphalt * 0.62, 0.06)
	var rng := RandomNumberGenerator.new()
	rng.seed = 4407
	for i in 22:
		var s := rng.randf_range(0.0, course.length)
		var lat := rng.randf_range(-0.7, 0.7) * _wr(s)
		var size := rng.randf_range(2.0, 5.5)
		_add_mesh(_ribbon(s, s + size * 1.6, func(_x): return lat + size * 0.5, func(_x): return lat - size * 0.5, 0.018, 0.8), puddle, "Puddle%d" % i)


# --- walls ------------------------------------------------------------------

func _wall_mesh(side: float, height: float, thickness: float, band: bool) -> ArrayMesh:
	## side +1 = left (inner) edge, -1 = right (outer) edge. Thickness grows away
	## from the track so the racing face sits exactly on the edge line.
	var st := SurfaceTool.new()
	st.begin(Mesh.PRIMITIVE_TRIANGLES)
	var step := 1.0
	var count := int(ceil(course.length / step))
	var y0 := 0.0 if not band else height * 0.48
	var y1 := height if not band else height * 0.62
	var inset := 0.0 if not band else -0.02
	var pts: Array[Vector2] = []
	var outs: Array[Vector2] = []
	for i in count + 1:
		var s := fposmod(course.length * float(i) / float(count), course.length)
		var pose := course.pose_at(s)
		var lf := Course.left_of(pose.f)
		var lateral := (float(pose.wl) if side > 0.0 else -float(pose.wr)) + side * inset
		pts.append(pose.p + lf * lateral)
		outs.append(lf * side)
	for i in count:
		var a := pts[i]
		var b := pts[i + 1]
		var oa := outs[i]
		var ob := outs[i + 1]
		var inward_a := Vector3(-oa.x, 0, -oa.y)
		_quad(st, Vector3(a.x, y0, a.y), Vector3(b.x, y0, b.y), Vector3(b.x, y1, b.y), Vector3(a.x, y1, a.y), inward_a)
		if band:
			continue
		var ta := a + oa * thickness
		var tb := b + ob * thickness
		_quad(st, Vector3(a.x, y1, a.y), Vector3(b.x, y1, b.y), Vector3(tb.x, y1, tb.y), Vector3(ta.x, y1, ta.y), Vector3.UP)
		_quad(st, Vector3(tb.x, y0, tb.y), Vector3(ta.x, y0, ta.y), Vector3(ta.x, y1, ta.y), Vector3(tb.x, y1, tb.y), Vector3(oa.x, 0, oa.y))
	return st.commit()


func _quad(st: SurfaceTool, a: Vector3, b: Vector3, c: Vector3, d: Vector3, n: Vector3) -> void:
	# Winding is irrelevant for the unlit-backface-safe materials below;
	# both triangles share the supplied normal.
	for v in [a, b, c, a, c, d]:
		st.set_normal(n)
		st.add_vertex(v)


func _build_walls() -> void:
	var h := float(course.data.wall.height_m)
	var t := float(course.data.wall.thickness_m)
	var concrete := material("wall", color("concrete", Color(0.5, 0.43, 0.32)), 0.8)
	concrete.cull_mode = BaseMaterial3D.CULL_DISABLED
	var band := material("wall_band", color("teal", Color(0.08, 0.43, 0.4)), 0.7)
	band.cull_mode = BaseMaterial3D.CULL_DISABLED
	for side in [1.0, -1.0]:
		var mesh := _wall_mesh(side, h, t, false)
		_add_mesh(mesh, concrete, "Wall" + ("Inner" if side > 0 else "Outer"))
		_wall_prisms(side, h, t, "WallCollision" + ("Inner" if side > 0 else "Outer"))
		_add_mesh(_wall_mesh(side, h, t, true), band, "WallBand" + ("Inner" if side > 0 else "Outer"))
	# Pale cap so the wall line reads from the chase camera in drizzle.
	var cap := material("wall_cap", color("trim", Color(0.68, 0.59, 0.43)) * 1.15, 0.75)
	_add_mesh(_ribbon(0.0, course.length, func(s): return _wl(s), func(s): return _wl(s) + t, h + 0.01, 1.0, true), cap, "CapInner")
	_add_mesh(_ribbon(0.0, course.length, func(s): return -_wr(s) - t, func(s): return -_wr(s), h + 0.01, 1.0, true), cap, "CapOuter")


# --- loading dock (Spread / Hop shortcut) ------------------------------------

func dock_range() -> Vector2:
	var d: Dictionary = course.data.dock
	var r: Vector2 = course.piece_ranges[String(d.piece)]
	var s0 := r.x - float(d.lead_in_m) + (r.y - r.x) * float(d.from_fraction)
	var s1 := r.x + (r.y - r.x) * float(d.to_fraction)
	return Vector2(s0, s1)


func _build_dock() -> void:
	var d: Dictionary = course.data.dock
	var r := dock_range()
	var h := float(d.height_m)
	var width := float(d.width_m)
	var inner := func(s): return _wl(s) - float(d.inner_m)
	var outer := func(s): return _wl(s) - float(d.inner_m) - width
	var concrete := material("dock", color("concrete", Color(0.5, 0.43, 0.32)) * 0.92, 0.82)
	concrete.cull_mode = BaseMaterial3D.CULL_DISABLED
	# Top, outer face, lead face and tail face share one collider.
	var st := SurfaceTool.new()
	st.begin(Mesh.PRIMITIVE_TRIANGLES)
	var step := 0.5
	var count := int(ceil((r.y - r.x) / step))
	for i in count:
		var sa := r.x + (r.y - r.x) * float(i) / float(count)
		var sb := r.x + (r.y - r.x) * float(i + 1) / float(count)
		var ia: Vector2 = course.edge_point(sa, inner.call(sa))
		var ib: Vector2 = course.edge_point(sb, inner.call(sb))
		var oa: Vector2 = course.edge_point(sa, outer.call(sa))
		var ob: Vector2 = course.edge_point(sb, outer.call(sb))
		_quad(st, Vector3(ia.x, h, ia.y), Vector3(ib.x, h, ib.y), Vector3(ob.x, h, ob.y), Vector3(oa.x, h, oa.y), Vector3.UP)
		_quad(st, Vector3(oa.x, 0, oa.y), Vector3(ob.x, 0, ob.y), Vector3(ob.x, h, ob.y), Vector3(oa.x, h, oa.y), Vector3((oa - ia).normalized().x, 0, (oa - ia).normalized().y))
	for s in [r.x, r.y]:
		var i_p: Vector2 = course.edge_point(s, inner.call(s))
		var o_p: Vector2 = course.edge_point(s, outer.call(s))
		var f: Vector2 = course.pose_at(s).f * (-1.0 if s == r.x else 1.0)
		_quad(st, Vector3(i_p.x, 0, i_p.y), Vector3(o_p.x, 0, o_p.y), Vector3(o_p.x, h, o_p.y), Vector3(i_p.x, h, i_p.y), Vector3(f.x, 0, f.y))
	var mesh := st.commit()
	_add_mesh(mesh, concrete, "LoadingDock")
	_collide(mesh, "LoadingDockCollision")
	# Yellow edge paint on the dock lip so Drive drivers read it as a step.
	var lip := material("dock_lip", Color(0.86, 0.66, 0.12), 0.6)
	_add_mesh(_ribbon(r.x + 0.4, r.y, func(s): return outer.call(s) + 0.45, outer, h + 0.012, 0.5), lip, "DockLip")
	# Buffer beam across the lead face: Spread must Hop it to take the dock.
	var bh := float(d.buffer_height_m)
	var depth := float(d.buffer_depth_m)
	var buffer_mat := material("buffer", Color(0.62, 0.13, 0.08), 0.55)
	var stripe_mat := material("buffer_stripe", Color(0.92, 0.88, 0.78), 0.55)
	var a: Vector2 = course.edge_point(r.x + depth * 0.5, inner.call(r.x))
	var b: Vector2 = course.edge_point(r.x + depth * 0.5, outer.call(r.x))
	var mid := (a + b) * 0.5
	var len := a.distance_to(b)
	var yaw := atan2(-(b - a).y, (b - a).x)
	var beam := _box(self, Vector3(mid.x, h + (bh - h) * 0.5, mid.y), Vector3(len, bh - h, depth), buffer_mat, yaw, true, true)
	beam.name = "DockBuffer"
	# The buffer is also solid below the dock top along its lead face.
	for k in 5:
		var u := (float(k) + 0.5) / 5.0
		var p := a.lerp(b, u)
		_box(self, Vector3(p.x, bh + 0.005, p.y), Vector3(len / 10.0, 0.01, depth + 0.01), stripe_mat, yaw)


# --- painted markings ---------------------------------------------------------

func _build_markings() -> void:
	var white := material("paint_white", Color(0.86, 0.84, 0.78), 0.6)
	var amber := material("paint_amber", Color(0.86, 0.55, 0.12), 0.6)
	var black := material("paint_black", Color(0.05, 0.06, 0.06), 0.6)
	# Edge lines.
	_add_mesh(_ribbon(0.0, course.length, func(s): return _wl(s) - 0.9, func(s): return _wl(s) - 1.15, 0.022, 1.0, true), white, "EdgeLineLeft")
	_add_mesh(_ribbon(0.0, course.length, func(s): return -_wr(s) + 1.15, func(s): return -_wr(s) + 0.9, 0.022, 1.0, true), white, "EdgeLineRight")
	# Amber skim stripe at the foot of the Hem's outer wall: the wall-ride line.
	var hem: Vector2 = course.piece_ranges["HEM"]
	_add_mesh(_ribbon(hem.x - 10.0, hem.y + 6.0, func(s): return -_wr(s) + 0.55, func(s): return -_wr(s) + 0.1, 0.024, 1.0), amber, "HemSkimStripe")
	# Start / finish checker.
	var line_s := float(course.gates[0].s)
	var cells := 12
	for row in 2:
		for c in cells:
			var lat0 := lerpf(_wl(line_s), -_wr(line_s), float(c) / cells)
			var lat1 := lerpf(_wl(line_s), -_wr(line_s), float(c + 1) / cells)
			var mat := white if (row + c) % 2 == 0 else black
			_add_mesh(_ribbon(line_s - 1.6 + row * 1.6, line_s + row * 1.6, func(_s): return lat0, func(_s): return lat1, 0.026, 1.6), mat, "Checker%d_%d" % [row, c])
	# Grid box.
	var grid_s := float(course.data.grid_s)
	for edge in [grid_s - 3.0, grid_s + 3.0]:
		_add_mesh(_ribbon(edge - 0.15, edge + 0.15, func(_s): return 2.2, func(_s): return -2.2, 0.026, 0.3), white, "GridBox")
	for lat in [2.2, -2.2]:
		_add_mesh(_ribbon(grid_s - 3.0, grid_s + 3.0, func(_s): return lat + 0.15, func(_s): return lat - 0.15, 0.026, 1.0), white, "GridBoxSide")
	# Direction chevrons: after the grid, and on approach to each major corner.
	for spec in [[grid_s + 8.0, 3], [course.piece_ranges["HEM"].x - 55.0, 3], [course.piece_ranges["CRANE"].x - 60.0, 2], [course.piece_ranges["GATE"].x - 20.0, 2]]:
		for k in int(spec[1]):
			_chevron(float(spec[0]) + k * 6.0, amber)


func _chevron(s: float, mat: Material) -> void:
	for side in [1.0, -1.0]:
		var mesh := _ribbon(s, s + 3.2,
			func(x): return side * (0.35 + (x - s) * 1.05),
			func(x): return side * (0.35 + (x - s) * 1.05) + side * 0.9, 0.026, 0.4)
		_add_mesh(mesh, mat, "Chevron")


# --- landmarks ----------------------------------------------------------------

func _yaw_of(f: Vector2) -> float:
	return atan2(-f.x, -f.y)


func _build_gantry() -> void:
	var line_s := float(course.gates[0].s)
	var pose := course.pose_at(line_s)
	var lf := Course.left_of(pose.f)
	var yaw := _yaw_of(pose.f)
	var steel := material("steel", color("steel", Color(0.14, 0.21, 0.23)), 0.5)
	var sign_mat := material("sign", Color(0.05, 0.08, 0.09), 0.7)
	var root := Node3D.new()
	root.name = "StartGantry"
	add_child(root)
	var t := float(course.data.wall.thickness_m)
	for side in [1.0, -1.0]:
		var lat := (float(pose.wl) + t * 0.5 + 0.6) if side > 0 else -(float(pose.wr) + t * 0.5 + 0.6)
		var p: Vector2 = pose.p + lf * lat
		_box(root, Vector3(p.x, 4.0, p.y), Vector3(0.6, 8.0, 0.6), steel, yaw)
	var mid: Vector2 = pose.p + lf * ((float(pose.wl) - float(pose.wr)) * 0.5)
	var span := float(pose.wl) + float(pose.wr) + 3.0
	_box(root, Vector3(mid.x, 7.6, mid.y), Vector3(span, 0.7, 0.5), steel, yaw)
	_box(root, Vector3(mid.x, 6.3, mid.y), Vector3(11.0, 1.9, 0.25), sign_mat, yaw)
	# Facing approaching traffic: the sign's front looks back down the straight.
	var back := Vector3(-pose.f.x, 0, -pose.f.y) * 0.14
	_label(root, "HEM LOOP", Vector3(mid.x, 6.7, mid.y) + back, yaw, 0.019, Color(0.96, 0.82, 0.5), 96)
	_label(root, "DEPOT YARD · RACE THIS WAY", Vector3(mid.x, 5.68, mid.y) + back, yaw, 0.0075, Color(0.6, 0.78, 0.74), 96)
	var lamp_mat := material("gate_lamp", Color(0.1, 0.5, 0.3), 0.3, Color(0.25, 1.0, 0.55), 2.2)
	gate_light = _box(root, Vector3(mid.x, 7.6, mid.y) + back * 3.0 + Vector3(lf.x, 0, lf.y) * 6.5, Vector3(0.9, 0.5, 0.2), lamp_mat, yaw)
	_box(root, Vector3(mid.x, 7.6, mid.y) + back * 3.0 - Vector3(lf.x, 0, lf.y) * 6.5, Vector3(0.9, 0.5, 0.2), lamp_mat, yaw)
	# Crew chalkboard just beyond the outer wall, readable from the grid.
	var board_p: Vector2 = course.edge_point(float(course.data.grid_s) + 12.0, -float(pose.wr) - 3.2)
	var board_yaw := yaw - PI * 0.5 + 0.35
	_box(root, Vector3(board_p.x, 1.6, board_p.y), Vector3(4.2, 2.6, 0.18), material("board", Color(0.07, 0.1, 0.09), 0.95), board_yaw)
	_box(root, Vector3(board_p.x, 1.6, board_p.y) + Vector3(lf.x, 0, lf.y) * 0.0, Vector3(4.5, 2.9, 0.12), material("board_frame", Color(0.42, 0.3, 0.18), 0.8), board_yaw).position += Vector3(-lf.x, 0, -lf.y) * 0.08
	chalkboard_label = _label(root, "", Vector3(board_p.x, 1.62, board_p.y) + Vector3(lf.x, 0, lf.y) * 0.11, board_yaw, 0.0042, Color(0.92, 0.92, 0.86), 64)
	chalkboard_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_LEFT
	chalkboard_label.width = 900
	chalkboard_label.autowrap_mode = TextServer.AUTOWRAP_WORD
	set_chalkboard("HEM LOOP · TONIGHT\nno laps yet")


func set_chalkboard(text: String) -> void:
	if chalkboard_label != null:
		chalkboard_label.text = text


func _build_hem_apex() -> void:
	## The bend's name is painted on its inside wall at the apex. Behind the wall
	## stands the spot where Tess's borrowed table used to be.
	var story: Dictionary = course.data.story
	var s := course.piece_s(String(story.tess_piece), -1.0, float(story.tess_fraction))
	var pose := course.pose_at(s)
	var lf := Course.left_of(pose.f)
	var h := float(course.data.wall.height_m)
	var t := float(course.data.wall.thickness_m)
	var face_yaw := _yaw_of(-lf)
	for offset in [-26.0, 0.0, 26.0]:
		var label_s: float = s + float(offset)
		var lp := course.pose_at(label_s)
		var lpos: Vector2 = lp.p + Course.left_of(lp.f) * (float(lp.wl) - 0.03)
		var lbl := _label(self, "THE HEM", Vector3(lpos.x, h * 0.72, lpos.y), _yaw_of(-Course.left_of(lp.f)) + PI, 0.02, Color(0.95, 0.86, 0.62), 96)
		lbl.name = "HemPaint"
	tess_anchor = Node3D.new()
	tess_anchor.name = "TessSpot"
	var wall_p: Vector2 = pose.p + lf * float(pose.wl)
	tess_anchor.transform = Transform3D(Basis(Vector3.UP, face_yaw + PI), Vector3(wall_p.x, 0, wall_p.y))
	add_child(tess_anchor)
	# Raised standing step and the old table, just behind the wall.
	var step_mat := material("table_wood", Color(0.46, 0.31, 0.18), 0.8)
	_box(tess_anchor, Vector3(0, 0.45, -1.1 - t), Vector3(3.6, 0.9, 1.8), material("step", color("concrete") * 0.8, 0.9))
	_box(tess_anchor, Vector3(1.6, 1.35, -2.6 - t), Vector3(2.6, 0.08, 1.2), step_mat)
	for x in [0.45, 2.75]:
		_box(tess_anchor, Vector3(x, 0.66, -2.6 - t), Vector3(0.08, 1.32, 1.0), step_mat)
	# Awning post and lamp over the spot so it reads from the turn-in.
	_box(tess_anchor, Vector3(-1.9, 2.1, -2.0 - t), Vector3(0.14, 4.2, 0.14), material("steel"))
	_box(tess_anchor, Vector3(0.0, 4.15, -2.0 - t), Vector3(4.4, 0.08, 2.6), material("awning", Color(0.58, 0.2, 0.12), 0.8))
	var lamp := material("lamp_head", Color(1.0, 0.8, 0.5), 0.4, Color(1.0, 0.72, 0.38), 3.0)
	_box(tess_anchor, Vector3(0.0, 3.95, -1.0 - t), Vector3(0.5, 0.2, 0.3), lamp)
	var light := OmniLight3D.new()
	light.light_color = Color(1.0, 0.78, 0.5)
	light.light_energy = 2.2
	light.omni_range = 11.0
	light.position = Vector3(0.0, 3.6, -1.2)
	tess_anchor.add_child(light)


func _build_crane() -> void:
	## Overhead gantry crane straddling Crane Corner: a landmark you aim under.
	var r: Vector2 = course.piece_ranges["CRANE"]
	var s := lerpf(r.x, r.y, 0.45)
	var pose := course.pose_at(s)
	var lf := Course.left_of(pose.f)
	var yaw := _yaw_of(pose.f)
	var crane := material("crane", Color(0.78, 0.52, 0.12), 0.6)
	var t := float(course.data.wall.thickness_m)
	var left_p: Vector2 = pose.p + lf * (float(pose.wl) + t + 7.0)
	var right_p: Vector2 = pose.p - lf * (float(pose.wr) + t + 11.0)
	for p in [left_p, right_p]:
		_box(self, Vector3(p.x, 6.0, p.y), Vector3(0.9, 12.0, 0.9), crane, yaw)
	var mid := (left_p + right_p) * 0.5
	_box(self, Vector3(mid.x, 12.3, mid.y), Vector3(left_p.distance_to(right_p) + 1.5, 1.0, 1.4), crane, yaw)
	_box(self, Vector3(mid.x, 9.6, mid.y), Vector3(0.08, 5.2, 0.08), material("steel"))
	_box(self, Vector3(mid.x, 6.9, mid.y), Vector3(1.2, 0.5, 0.8), crane)


func _build_lamps() -> void:
	var post := material("steel")
	var head := material("lamp_head")
	var t := float(course.data.wall.thickness_m)
	var s := 6.0
	while s < course.length:
		var pose := course.pose_at(s)
		var lf := Course.left_of(pose.f)
		var p: Vector2 = pose.p - lf * (float(pose.wr) + t + 4.5)
		_box(self, Vector3(p.x, 3.2, p.y), Vector3(0.18, 6.4, 0.18), post)
		_box(self, Vector3(p.x, 6.45, p.y) + Vector3(lf.x, 0, lf.y) * 0.7, Vector3(1.6, 0.14, 0.32), post, _yaw_of(lf))
		_box(self, Vector3(p.x, 6.33, p.y) + Vector3(lf.x, 0, lf.y) * 1.3, Vector3(0.5, 0.12, 0.3), head, _yaw_of(lf))
		s += 32.0


func _build_sheds() -> void:
	## Deterministic Depot sheds behind both walls, kept clear of the course.
	var rng := RandomNumberGenerator.new()
	rng.seed = 91117
	var body_colors := [color("concrete"), color("shoulder"), color("quarry"), color("trim") * 0.82, Color(0.36, 0.25, 0.18)]
	var roof := material("roof", color("steel") * 0.9, 0.6)
	var window_mat := material("window", Color(0.95, 0.72, 0.42), 0.4, Color(1.0, 0.66, 0.32), 1.6)
	var dark_window := material("window_dark", Color(0.08, 0.12, 0.14), 0.25)
	var placed: Array[Rect2] = []
	var root := Node3D.new()
	root.name = "DepotSheds"
	add_child(root)
	var attempts := 0
	var count := 0
	while count < 46 and attempts < 900:
		attempts += 1
		var s := rng.randf_range(0.0, course.length)
		var side := 1.0 if rng.randf() < 0.42 else -1.0
		var pose := course.pose_at(s)
		var lf := Course.left_of(pose.f)
		var w := rng.randf_range(12.0, 30.0)
		var d := rng.randf_range(9.0, 18.0)
		var h := rng.randf_range(5.0, 13.0)
		var gap := rng.randf_range(9.0, 26.0)
		var lateral := (float(pose.wl) + gap + d * 0.5) if side > 0 else -(float(pose.wr) + gap + d * 0.5)
		var c: Vector2 = pose.p + lf * lateral
		# Reject anything that would crowd any part of the lap.
		var clear := true
		for k in range(0, course.samples.size(), 8):
			var sp: Dictionary = course.samples[k]
			var reach := maxf(float(sp.wl), float(sp.wr)) + 7.0 + maxf(w, d) * 0.5
			if c.distance_to(sp.p) < reach:
				clear = false
				break
		if not clear:
			continue
		var rect := Rect2(c - Vector2(maxf(w, d), maxf(w, d)) * 0.55, Vector2(maxf(w, d), maxf(w, d)) * 1.1)
		var overlap := false
		for other in placed:
			if other.intersects(rect):
				overlap = true
				break
		if overlap:
			continue
		placed.append(rect)
		count += 1
		var yaw := _yaw_of(pose.f)
		var body_mat := material("shed_%d" % (count % body_colors.size()), body_colors[count % body_colors.size()], 0.86)
		_box(root, Vector3(c.x, h * 0.5, c.y), Vector3(d, h, w), body_mat, yaw)
		_box(root, Vector3(c.x, h + 0.25, c.y), Vector3(d + 1.2, 0.5, w + 1.2), roof, yaw)
		# A row of lit windows on the face toward the track.
		var face := -side
		var rows := 1 if h < 8.0 else 2
		for row in rows:
			var n := int(w / 4.0)
			for k in n:
				var u := (float(k) + 0.5) / float(n) - 0.5
				var lit := rng.randf() < 0.55
				var wp: Vector2 = c + pose.f * (u * w) + lf * (face * (d * 0.5 + 0.03))
				_box(root, Vector3(wp.x, 2.6 + row * 3.6, wp.y), Vector3(0.06, 1.3, 1.6), window_mat if lit else dark_window, yaw)
