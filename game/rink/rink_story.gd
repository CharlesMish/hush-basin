extends Node3D
## Crew run: one short Hush Basin encounter on the Hem Loop.
##
## Tess's borrowed table stood on the inside of the Hem for the year she sewed
## at Depot. Tonight the night crew is short one mended jacket, and Tess is back
## at her old spot holding it out over the wall. Taking it means unfolding early
## and running the tight inside line — the opposite of the fast wall-ride. Sail
## past and she is still holding it next lap. Whatever happens to the jacket on
## the way to the line (first pass or fifth, clean or scuffed on a wall) is what
## the crew and Tess answer. Lines are one short sentence and never pause play.

const Text = preload("res://rink/rink_story_text.gd")
const TESS_PORTRAIT := "res://presentation/narrative/tess.png"
const JACKET := Color(0.93, 0.5, 0.1)
const REFLECT := Color(0.9, 0.92, 0.85)
const SCUFF := Color(0.24, 0.24, 0.23)

var game: Node3D
var course
var state := "OFF"
var catch_point := Vector2.ZERO
var apex_s := 0.0
var attempts := 0
var misses := 0
var scuffs := 0
var catch_record: Dictionary = {}
var delivered_record: Dictionary = {}
var _queue: Array = []
var _line_until := 0.0
var _clock := 0.0
var _approach_called := false
var _impact_seen := 0
var _post_hem_called := false
var _prev_s := 0.0
var _tess_portrait: Texture2D

var tess: Node3D
var tess_arm: Node3D
var held_jacket: Node3D
var miss_ring: MeshInstance3D
var chalk_hints: Node3D
var craft_jacket: Node3D
var craft_scuffs: Array[MeshInstance3D] = []
var crew: Node3D
var crew_driver_jacket: Node3D
var _ring_pulse := 0.0


func configure(owner_game: Node3D) -> void:
	game = owner_game
	course = game.course
	process_mode = Node.PROCESS_MODE_PAUSABLE
	if ResourceLoader.exists(TESS_PORTRAIT):
		_tess_portrait = load(TESS_PORTRAIT)
	var spec: Dictionary = course.data.story
	apex_s = course.piece_s(String(spec.tess_piece), -1.0, float(spec.tess_fraction))
	var pose: Dictionary = course.pose_at(apex_s)
	var lf: Vector2 = course.left_of(pose.f)
	catch_point = pose.p + lf * (float(pose.wl) - float(spec.hand_reach_m))
	_build_tess(game.builder.tess_anchor, float(spec.hand_reach_m))
	_build_miss_marks(pose, lf)
	_build_crew()
	_build_craft_jacket()
	end()


# --- lifecycle -----------------------------------------------------------------

func begin() -> void:
	state = "WAITING"
	attempts = 1
	misses = 0
	scuffs = 0
	catch_record = {}
	delivered_record = {}
	_queue.clear()
	_line_until = 0.0
	_approach_called = false
	_post_hem_called = false
	_impact_seen = game.craft.impact_count
	tess.visible = true
	_set_holding(true)
	miss_ring.visible = false
	chalk_hints.visible = false
	crew.visible = true
	crew_driver_jacket.visible = false
	_show_craft_jacket(false)
	_prev_s = game.progress_s
	for line in Text.BRIEF:
		_say(line[0], line[1])
	game.log_event("story_begin")


func end() -> void:
	state = "OFF"
	_queue.clear()
	if tess != null:
		tess.visible = false
		miss_ring.visible = false
		chalk_hints.visible = false
		crew.visible = false
		_show_craft_jacket(false)


func on_reset(_reason: String) -> void:
	# Back to the grid keeps the run's story: a jacket aboard stays strapped on.
	_approach_called = false
	_prev_s = game.progress_s
	_impact_seen = game.craft.impact_count


# --- per-step observation ----------------------------------------------------------

func physics(delta: float, curr: Vector2, proj: Dictionary) -> void:
	_clock += delta
	_pump_lines()
	var s := float(proj.s)
	var ds := wrapf(s - _prev_s, -course.length * 0.5, course.length * 0.5)
	var before_apex := wrapf(_prev_s - (apex_s + 3.0), -course.length * 0.5, course.length * 0.5)
	var crossed_apex := before_apex < 0.0 and before_apex + ds >= 0.0 and absf(ds) < 40.0
	var to_apex := wrapf(apex_s - s, 0.0, course.length)
	match state:
		"WAITING":
			if not _approach_called and to_apex < 150.0 and to_apex > 60.0 and ds > 0.0:
				_approach_called = true
				_say_now(Text.TESS, Text.APPROACH[mini(misses, Text.APPROACH.size() - 1)])
			var reach := _segment_distance(catch_point, game._prev, curr)
			if reach <= float(course.data.story.catch_radius_m):
				_caught(reach)
			elif crossed_apex:
				_missed(curr)
		"CARRYING":
			var craft: CraftController = game.craft
			if craft.impact_count != _impact_seen:
				_impact_seen = craft.impact_count
				if craft.last_impact_severity >= 0.15:
					scuffs += 1
					_update_scuffs()
					game.log_event("story_scuff", {"severity": snappedf(craft.last_impact_severity, 0.01), "scuffs": scuffs})
		"DELIVERED":
			if crossed_apex and not _post_hem_called:
				_post_hem_called = true
				_say_now(Text.TESS, Text.AFTER_CLEAN if scuffs == 0 else Text.AFTER_SCUFFED)
	_prev_s = s
	if miss_ring.visible:
		_ring_pulse += delta
		var k := 0.55 + 0.45 * sin(_ring_pulse * 6.0)
		(miss_ring.material_override as StandardMaterial3D).emission_energy_multiplier = 1.2 + 1.6 * k


static func _segment_distance(point: Vector2, a: Vector2, b: Vector2) -> float:
	var ab := b - a
	var t := 0.0
	if ab.length_squared() > 0.000001:
		t = clampf((point - a).dot(ab) / ab.length_squared(), 0.0, 1.0)
	return point.distance_to(a + ab * t)


func _caught(reach: float) -> void:
	var craft: CraftController = game.craft
	var speed := craft.velocity.length()
	var form := craft.regime_name()
	state = "CARRYING"
	catch_record = {"attempt": attempts, "speed": snappedf(speed, 0.1), "form": form, "reach": snappedf(reach, 0.01), "misses": misses}
	_impact_seen = craft.impact_count
	_set_holding(false)
	miss_ring.visible = false
	_show_craft_jacket(true)
	var line: String
	if speed < 7.0:
		line = Text.CATCH_SLOW
	elif form == "DRIVE":
		line = Text.CATCH_DRIVE
	elif misses == 0:
		line = Text.CATCH_FIRST
	else:
		line = Text.CATCH_AGAIN
	_say_now(Text.TESS, line)
	game.hud.flash("Jacket aboard", game.Hud.GOOD, 1.6)
	game.log_event("story_catch", catch_record)


func _missed(curr: Vector2) -> void:
	misses += 1
	attempts += 1
	_approach_called = false
	miss_ring.visible = true
	_ring_pulse = 0.0
	chalk_hints.visible = true
	var lateral_gap := catch_point.distance_to(curr)
	_say_now(Text.TESS, Text.MISS[mini(misses - 1, Text.MISS.size() - 1)])
	game.hud.flash("Handoff missed — she's still holding it", game.Hud.AMBER, 2.4)
	game.log_event("story_miss", {"misses": misses, "distance": snappedf(lateral_gap, 0.1), "speed": snappedf(game.craft.velocity.length(), 0.1)})


func on_line() -> void:
	if state != "CARRYING":
		return
	state = "DELIVERED"
	delivered_record = {"attempts": attempts, "misses": misses, "scuffs": scuffs, "catch": catch_record}
	_show_craft_jacket(false)
	crew_driver_jacket.visible = true
	var verdict: String
	if scuffs >= 2:
		verdict = Text.DELIVER_WALL
	elif scuffs == 1:
		verdict = Text.DELIVER_SCUFF
	elif misses == 0:
		verdict = Text.DELIVER_FIRST
	else:
		verdict = Text.DELIVER_AGAIN
	_queue.clear()
	_say_now(Text.CREW, verdict)
	for line in Text.REVEAL:
		_say(line[0], line[1])
	_say(Text.YARD, Text.DONE)
	game.log_event("story_delivered", delivered_record)


# --- dialogue (short, non-blocking) ----------------------------------------------

func _say(speaker: String, line: String) -> void:
	_queue.append([speaker, line])


func _say_now(speaker: String, line: String) -> void:
	_queue.push_front([speaker, line])
	_line_until = 0.0
	_pump_lines()


func _pump_lines() -> void:
	if _queue.is_empty() or _clock < _line_until:
		return
	var next: Array = _queue.pop_front()
	var seconds := clampf(1.6 + String(next[1]).length() * 0.045, 2.2, 4.2)
	var portrait: Texture2D = _tess_portrait if String(next[0]) == Text.TESS else null
	game.hud.say(String(next[0]), String(next[1]), portrait, seconds)
	_line_until = _clock + seconds + 0.15
	game.log_event("story_line", {"speaker": next[0], "line": next[1]})


func status_line() -> String:
	match state:
		"WAITING":
			return "Jacket: Tess, inside of the Hem" + ("  ·  missed %d" % misses if misses > 0 else "")
		"CARRYING":
			return "Jacket: aboard · " + ("clean" if scuffs == 0 else "scuffed ×%d" % scuffs) + " → the line"
		"DELIVERED":
			return "Delivered · " + ("clean" if scuffs == 0 else "scuffed ×%d" % scuffs) + " · T time trial · C again"
	return ""


func map_marks() -> Array:
	if state == "WAITING":
		return [[catch_point, Color(1.0, 0.55, 0.15)]]
	if state == "CARRYING":
		return [[course.gates[0].a.lerp(course.gates[0].b, 0.85), Color(0.3, 0.95, 0.85)]]
	return []


# --- figures and props -------------------------------------------------------------

func _mat(c: Color, rough: float = 0.8, glow: float = 0.0) -> StandardMaterial3D:
	var m := StandardMaterial3D.new()
	m.albedo_color = c
	m.roughness = rough
	if glow > 0.0:
		m.emission_enabled = true
		m.emission = c
		m.emission_energy_multiplier = glow
	return m


func _part(parent: Node3D, at: Vector3, size: Vector3, c: Material, sphere: bool = false) -> MeshInstance3D:
	var mi := MeshInstance3D.new()
	if sphere:
		var m := SphereMesh.new()
		m.radius = size.x * 0.5
		m.height = size.y
		m.radial_segments = 12
		m.rings = 6
		mi.mesh = m
	else:
		var b := BoxMesh.new()
		b.size = size
		mi.mesh = b
	mi.material_override = c
	mi.position = at
	parent.add_child(mi)
	return mi


func _person(parent: Node3D, at: Vector3, jacket: Color, trousers: Color, skin: Color, hair: Color) -> Node3D:
	var p := Node3D.new()
	p.position = at
	parent.add_child(p)
	for x in [-0.12, 0.12]:
		_part(p, Vector3(x, 0.42, 0), Vector3(0.17, 0.84, 0.2), _mat(trousers))
	_part(p, Vector3(0, 1.12, 0), Vector3(0.5, 0.62, 0.28), _mat(jacket))
	_part(p, Vector3(0, 1.58, 0), Vector3(0.24, 0.27, 0.24), _mat(skin), true)
	_part(p, Vector3(0, 1.69, -0.03), Vector3(0.26, 0.14, 0.26), _mat(hair), true)
	return p


func _build_tess(anchor: Node3D, reach: float) -> void:
	tess = Node3D.new()
	tess.name = "Tess"
	anchor.add_child(tess)
	var t := float(course.data.wall.thickness_m)
	# Local +Z leans out toward the track; the step top is 0.9 m.
	var body := _person(tess, Vector3(0, 0.9, -0.5 - t), Color(0.48, 0.17, 0.11), Color(0.2, 0.2, 0.22), Color(0.86, 0.68, 0.55), Color(0.24, 0.15, 0.1))
	body.rotation.x = deg_to_rad(16.0)
	# Tape measure across the shoulders, as in her portrait.
	_part(body, Vector3(0, 1.3, 0.15), Vector3(0.05, 0.4, 0.02), _mat(Color(0.86, 0.75, 0.32)))
	tess_arm = Node3D.new()
	tess_arm.position = Vector3(0.22, 2.25, -0.4 - t)
	tess.add_child(tess_arm)
	var arm_len := reach + 0.4 + t
	_part(tess_arm, Vector3(0, 0, arm_len * 0.5), Vector3(0.12, 0.12, arm_len), _mat(Color(0.48, 0.17, 0.11)))
	held_jacket = Node3D.new()
	held_jacket.position = Vector3(0, -0.22, arm_len)
	tess_arm.add_child(held_jacket)
	_jacket_bundle(held_jacket, 1.0)


func _jacket_bundle(parent: Node3D, scale_k: float) -> void:
	_part(parent, Vector3.ZERO, Vector3(0.62, 0.34, 0.5) * scale_k, _mat(JACKET, 0.7, 0.35))
	_part(parent, Vector3(0, 0.02, 0) * scale_k, Vector3(0.64, 0.07, 0.52) * scale_k, _mat(REFLECT, 0.3, 0.6))
	_part(parent, Vector3(0, -0.21, 0) * scale_k, Vector3(0.66, 0.08, 0.12) * scale_k, _mat(Color(0.3, 0.24, 0.16)))


func _set_holding(holding: bool) -> void:
	held_jacket.visible = holding
	tess_arm.rotation.x = 0.0 if holding else deg_to_rad(-62.0)


func _build_miss_marks(pose: Dictionary, lf: Vector2) -> void:
	var ring := TorusMesh.new()
	ring.inner_radius = 2.6
	ring.outer_radius = 3.0
	miss_ring = MeshInstance3D.new()
	miss_ring.name = "MissedHandoffRing"
	miss_ring.mesh = ring
	miss_ring.material_override = _mat(Color(1.0, 0.55, 0.15), 0.5, 2.0)
	miss_ring.position = Vector3(catch_point.x, 0.08, catch_point.y)
	add_child(miss_ring)
	# Chalk arrows along the inside line, shown once a pass has gone wide.
	chalk_hints = Node3D.new()
	chalk_hints.name = "ChalkInsideLine"
	add_child(chalk_hints)
	var chalk := _mat(Color(0.92, 0.9, 0.82), 0.9, 0.25)
	for k in range(-9, 3):
		var s := apex_s + k * 6.0
		var p: Dictionary = course.pose_at(s)
		var l: Vector2 = course.left_of(p.f)
		var c: Vector2 = p.p + l * (float(p.wl) - 3.2)
		var mark := _part(chalk_hints, Vector3(c.x, 0.03, c.y), Vector3(0.35, 0.02, 2.2), chalk)
		mark.rotation.y = atan2(-p.f.x, -p.f.y)


func _build_crew() -> void:
	## Night crew on the outside walkway at the line, where the jacket goes.
	crew = Node3D.new()
	crew.name = "NightCrew"
	add_child(crew)
	var line_s: float = course.gates[0].s
	var pose: Dictionary = course.pose_at(line_s - 6.0)
	var lf: Vector2 = course.left_of(pose.f)
	var t := float(course.data.wall.thickness_m)
	var base: Vector2 = pose.p - lf * (float(pose.wr) + t + 1.6)
	var yaw := atan2(lf.x, lf.y)
	var walk := _part(crew, Vector3(base.x, 0.6, base.y), Vector3(2.6, 1.2, 9.0), _mat(Color(0.3, 0.3, 0.28)))
	walk.rotation.y = atan2(-pose.f.x, -pose.f.y)
	var offsets := [-2.4, 0.0, 2.6]
	var jackets := [Color(0.18, 0.26, 0.3), Color(0.32, 0.3, 0.27), Color(0.2, 0.3, 0.24)]
	for i in offsets.size():
		var p: Vector2 = base + pose.f * float(offsets[i])
		var person := _person(crew, Vector3(p.x, 1.2, p.y), jackets[i], Color(0.15, 0.16, 0.18), Color(0.7, 0.52, 0.4), Color(0.12, 0.1, 0.08))
		person.rotation.y = yaw
		if i == 1:
			# The night driver: in shirtsleeves until the jacket arrives.
			crew_driver_jacket = Node3D.new()
			person.add_child(crew_driver_jacket)
			_part(crew_driver_jacket, Vector3(0, 1.12, 0), Vector3(0.56, 0.66, 0.32), _mat(JACKET, 0.7, 0.35))
			_part(crew_driver_jacket, Vector3(0, 1.0, 0), Vector3(0.58, 0.07, 0.34), _mat(REFLECT, 0.3, 0.6))


func _build_craft_jacket() -> void:
	## Strapped to the craft's rear deck so the chase camera always sees it.
	var visual: Node3D = game.craft.get_node("VisualRoot")
	craft_jacket = Node3D.new()
	craft_jacket.name = "CarriedJacket"
	craft_jacket.position = Vector3(0, 0.62, 0.72)
	visual.add_child(craft_jacket)
	_jacket_bundle(craft_jacket, 1.0)
	for i in 3:
		var smudge := _part(craft_jacket, Vector3(-0.2 + i * 0.2, 0.175, -0.08 + i * 0.07), Vector3(0.16, 0.012, 0.11), _mat(SCUFF, 0.95))
		smudge.visible = false
		craft_scuffs.append(smudge)


func _show_craft_jacket(on: bool) -> void:
	craft_jacket.visible = on
	_update_scuffs()


func _update_scuffs() -> void:
	for i in craft_scuffs.size():
		craft_scuffs[i].visible = i < scuffs
