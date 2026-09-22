extends Node3D
## Finite Relay equipment states. Presentation only; the project owns persistence.
## Configure after adding this node to the world, then set_stage(0, 1 or 2).
const CONFIG := "res://presentation/relay_annex_v0_1.json"
var stage := 0
var definition: Dictionary = {}
var occupied_plot := PackedVector2Array()
var equipment_bounds := AABB()
var _stages: Array[Node3D] = []

func configure(data: P1AWorldData) -> void:
	for child in get_children():
		remove_child(child)
		child.queue_free()
	_stages.clear()
	definition = JSON.parse_string(FileAccess.get_file_as_string(CONFIG))
	var owner: Dictionary = {}
	for item in data.manifest.landmarks:
		if item.id == definition.owner:
			owner = item
	assert(not owner.is_empty(), "Relay annex requires its authoritative mast")
	var architecture: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://presentation/generated/neighborhood_v1.json"))
	occupied_plot.clear()
	for item in architecture.owners:
		if item.id == definition.owner:
			for point in item.plot:
				occupied_plot.append(Vector2(point[0], point[1]))
	assert(occupied_plot.size() == 4)
	position = Vector3(owner.center_xz_m[0], owner.base_y_m, owner.center_xz_m[1])
	name = "RelayDispatchAnnex"
	set_meta("presentation_identity", definition.identity)
	set_meta("collision_free", true)
	set_meta("source_owner", definition.owner)
	var groups: Dictionary = {}
	var first := true
	for p in definition.parts:
		var origin := _v3(p.p)
		var size := _v3(p.size)
		var box := AABB(origin-size*0.5, size)
		equipment_bounds = box if first else equipment_bounds.merge(box)
		first = false
		var key := "%s_%s" % [p.stage, p.get("emissive", false)]
		if not groups.has(key): groups[key] = []
		groups[key].append(p)
	for key in groups:
		var rows: Array = groups[key]
		var unit := BoxMesh.new()
		unit.size = Vector3.ONE
		var mm := MultiMesh.new()
		mm.transform_format = MultiMesh.TRANSFORM_3D
		mm.use_colors = true
		mm.mesh = unit
		mm.instance_count = rows.size()
		for i in rows.size():
			mm.set_instance_transform(i, Transform3D(Basis.from_scale(_v3(rows[i].size)), _v3(rows[i].p)))
			mm.set_instance_color(i, Color(definition.palette[rows[i].color]))
		var material := StandardMaterial3D.new()
		material.vertex_color_use_as_albedo = true
		material.vertex_color_is_srgb = true
		material.roughness = float(definition.roughness)
		if rows[0].get("emissive", false):
			material.emission_enabled = true
			material.emission = Color(definition.palette.warm)
			material.emission_energy_multiplier = float(definition.emission_energy)
		var batch := MultiMeshInstance3D.new()
		batch.name = "Equipment_" + String(key)
		batch.multimesh = mm
		batch.material_override = material
		batch.layers = 3 # Existing particle-only rain mask; no new physics.
		batch.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		batch.set_meta("minimum_stage", int(rows[0].stage))
		add_child(batch)
		_stages.append(batch)
	var sign: Dictionary = definition.sign
	var label := Label3D.new()
	label.name = "DispatchHeader"
	label.text = sign.text
	label.font_size = 64
	label.pixel_size = minf(float(sign.height_m)/64.0, float(sign.width_m)/(String(sign.text).length()*40.0))
	label.outline_size = 0
	label.modulate = Color(definition.palette[sign.color])
	label.position = _v3(sign.p)
	label.set_meta("minimum_stage", int(sign.stage))
	add_child(label)
	_stages.append(label)
	set_stage(stage)

func set_stage(value: int) -> void:
	stage = clampi(value, 0, 2)
	for child in _stages:
		child.visible = stage >= int(child.get_meta("minimum_stage"))
	set_meta("project_stage", stage)

func visible_instance_count() -> int:
	var count := 0
	for child in _stages:
		if child.visible and child is MultiMeshInstance3D:
			count += child.multimesh.instance_count
	return count

static func _v3(value: Array) -> Vector3:
	return Vector3(value[0], value[1], value[2])
