extends Node3D
## Cosmetic observer. Particle collision is separate from Godot body collision.

const Resources = preload("res://scripts/overcast_resources.gd")
const STATIC_WEATHER_LAYER := 1 << 1
var camera: Camera3D
var rain: GPUParticles3D
var rain_collision: GPUParticlesCollisionHeightField3D
var reset_pending := false
var restart_count := 0
var active_time := 0.0

func configure(gate: P1AWorldGate) -> void:
	process_mode = Node.PROCESS_MODE_PAUSABLE
	camera = gate.camera_rig.get_node("Camera")
	var cfg: Dictionary = Resources.config().rain
	# Only static world meshes contribute to the once-built precipitation floor.
	for visual in gate.world.find_children("*", "MeshInstance3D", true, false):
		visual.layers |= STATIC_WEATHER_LAYER
	rain_collision = GPUParticlesCollisionHeightField3D.new()
	rain_collision.name = "StaticPrecipitationFloor"
	var size: Array = cfg.heightfield_size
	var center: Array = cfg.heightfield_center
	rain_collision.size = Vector3(size[0], size[1], size[2])
	rain_collision.position = Vector3(center[0], center[1], center[2])
	rain_collision.resolution = int(cfg.heightfield_resolution)
	rain_collision.heightfield_mask = STATIC_WEATHER_LAYER
	rain_collision.follow_camera_enabled = false
	rain_collision.update_mode = GPUParticlesCollisionHeightField3D.UPDATE_MODE_WHEN_MOVED
	add_child(rain_collision)
	rain = GPUParticles3D.new()
	rain.name = "FineDrizzle"
	rain.amount = int(cfg.amount)
	rain.lifetime = float(cfg.lifetime_s)
	rain.local_coords = false
	rain.use_fixed_seed = true
	rain.seed = int(cfg.seed)
	rain.fixed_fps = 60
	rain.visibility_aabb = AABB(Vector3(-100, -50, -100), Vector3(200, 100, 200))
	rain.transform_align = GPUParticles3D.TRANSFORM_ALIGN_Z_BILLBOARD_Y_TO_VELOCITY
	rain.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	var process := ParticleProcessMaterial.new()
	process.emission_shape = ParticleProcessMaterial.EMISSION_SHAPE_BOX
	process.emission_box_extents = Vector3(float(cfg.footprint_m) * 0.5, 1.0, float(cfg.footprint_m) * 0.5)
	var direction: Array = cfg.wind_direction
	process.direction = Vector3(direction[0], direction[1], direction[2]).normalized()
	process.spread = 1.0
	process.gravity = Vector3.ZERO
	process.initial_velocity_min = float(cfg.fall_speed_min)
	process.initial_velocity_max = float(cfg.fall_speed_max)
	process.collision_mode = ParticleProcessMaterial.COLLISION_HIDE_ON_CONTACT
	rain.process_material = process
	var mesh := QuadMesh.new()
	mesh.size = Vector2(float(cfg.streak_width_m), float(cfg.streak_length_m))
	var material := StandardMaterial3D.new()
	var c: Array = cfg.color
	material.albedo_color = Color(c[0], c[1], c[2], c[3])
	material.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	material.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	material.cull_mode = BaseMaterial3D.CULL_DISABLED
	mesh.material = material
	rain.draw_pass_1 = mesh
	add_child(rain)
	_follow_camera()
	gate.craft.reset_performed.connect(_on_reset)
	reset_pending = true

func _on_reset(_count: int, _reason: String) -> void:
	rain.emitting = false
	reset_pending = true

func _follow_camera() -> void:
	rain.global_position = camera.global_position + Vector3.UP * float(Resources.config().rain.height_above_camera_m)

func _process(delta: float) -> void:
	if camera == null:
		return
	_follow_camera()
	if reset_pending:
		rain.restart(true)
		rain.emitting = true
		reset_pending = false
		restart_count += 1
	active_time += delta
