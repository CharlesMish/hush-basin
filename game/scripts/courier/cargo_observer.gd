extends RefCounted
## Read-only native post-move observer. No movement or response reconstruction.
const Rules = preload("res://scripts/courier/courier_rules.gd")
var condition_units := Rules.CONDITION_UNITS
var impact_samples := 0
var episodes := 0
var ignored_samples := 0
var _last_impact := 0
var _reset_epoch := 0
var _episode_open := false
var _charged_peak := 0
var _quiet_s := 0.0
var _last_frame := -1
var entry_severity := 0.0
var _last_wall_position := Vector3.ZERO
var _last_wall_normal := Vector3.ZERO
var _have_wall_position := false
var observation_serial := 0

func begin(craft: CraftController) -> void:
	observation_serial += 1
	condition_units = Rules.CONDITION_UNITS
	impact_samples = 0
	episodes = 0
	ignored_samples = 0
	_last_impact = craft.impact_count
	_reset_epoch = craft.reset_count
	_episode_open = false
	_charged_peak = 0
	_quiet_s = 0
	_last_frame = -1
	entry_severity = 0
	_have_wall_position = false

func sample(craft: CraftController, delta: float) -> Dictionary:
	var frame := Engine.get_physics_frames()
	if frame == _last_frame or ( _last_frame >= 0 and frame < _last_frame):
		return {"valid":false,"reason":"duplicate physics observation","loss":0}
	_last_frame = frame
	if craft.reset_count != _reset_epoch:
		return {"valid":false,"reason":"craft reset","loss":0}
	var advance := craft.impact_count-_last_impact
	if advance < 0 or advance > 1 or not is_finite(delta) or delta<=0:
		return {"valid":false,"reason":"impact counter discontinuity","loss":0}
	_last_impact = craft.impact_count
	var contact := contacts(craft)
	if contact.wall_touch:
		_last_wall_position = craft.global_position
		_last_wall_normal = contact.outward_normal
		_have_wall_position = true
	elif _have_wall_position and _episode_open:
		# Actual observed clearance, not inferred velocity or response. This
		# distinguishes rapid separate strikes without billing contact jitter.
		var outward := (craft.global_position-_last_wall_position).dot(_last_wall_normal)
		if outward>=Rules.EPISODE_CLEARANCE_M:
			_episode_open = false
	var severity := 0.0
	if advance == 1:
		impact_samples += 1
		severity = craft.last_impact_severity
		if not is_finite(severity) or severity<0 or severity>1:
			return {"valid":false,"reason":"invalid impact severity","loss":0}
		if not contact.eligible:
			ignored_samples += 1
	var loss := reduce(delta,advance==1 and contact.eligible,severity,contact.wall_touch)
	return {"valid":true,"loss":loss,"fresh":advance==1,"eligible":contact.eligible,"wall_touch":contact.wall_touch,"severity":severity}

static func contacts(craft: CraftController) -> Dictionary:
	var eligible := craft.get_slide_collision_count()>0
	var wall_touch := false
	var normals := Vector3.ZERO
	for i in craft.get_slide_collision_count():
		var hit := craft.get_slide_collision(i)
		var normal := hit.get_normal()
		var collider := hit.get_collider()
		var id := String(collider.get_meta("source_geometry_id","")) if collider != null else ""
		var obstacle := normal.is_finite() and absf(normal.y)<=Rules.OBSTACLE_NORMAL_Y_MAX and not id.is_empty() and id!="HEIGHTFIELD_SUPPORT"
		wall_touch = wall_touch or obstacle
		if obstacle:
			normals += Vector3(normal.x,0,normal.z).normalized()
		# The controller exposes the strongest severity, not its winning index.
		# Only attribute it when EVERY contact is an obstacle. Mixed contacts are
		# deliberately forgiven rather than assigning a landing's severity to a wall.
		eligible = eligible and obstacle
	return {"eligible":eligible,"wall_touch":wall_touch,"outward_normal":normals.normalized()}

func reduce(delta: float, fresh_obstacle: bool, severity: float, wall_touch: bool) -> int:
	if wall_touch:
		_quiet_s = 0
	else:
		_quiet_s += delta
		if _quiet_s > Rules.CONTACT_QUIET_SECONDS+0.000000001:
			_episode_open = false
	if not fresh_obstacle or not wall_touch or _episode_open:
		return 0
	# Latch the first fresh, unambiguous entry, even below the cargo dead zone.
	# Ambiguous/weak contact reports cannot pre-empt a genuine fresh impact.
	# Later pressure cannot turn this entry into a larger bill.
	_episode_open = true
	episodes += 1
	entry_severity = severity
	_charged_peak = Rules.loss_for_severity(entry_severity)
	var loss := mini(condition_units,_charged_peak)
	condition_units -= loss
	return loss
