extends Node3D
## The Basin's warm-overcast drizzle, using the shared warm_overcast_v1 config.
## Same particle recipe as scripts/overcast_weather.gd, wired to the rink's own
## camera and static meshes. Cosmetic only: no body collision or gameplay.

const Resources = preload("res://scripts/overcast_resources.gd")
const STATIC_WEATHER_LAYER := 1 << 1

var camera: Camera3D
var rain: GPUParticles3D


func configure(target_camera: Camera3D, static_meshes: Array[MeshInstance3D], centre: Vector3) -> void:
	process_mode = Node.PROCESS_MODE_PAUSABLE
	camera = target_camera
	var cfg: Dictionary = Resources.config().rain
	for visual in static_meshes:
		visual.layers |= STATIC_WEATHER_LAYER
	var floor_collision := GPUParticlesCollisionHeightField3D.new()
	floor_collision.name = "StaticPrecipitationFloor"
	floor_collision.size = Vector3(700, 60, 600)
	floor_collision.position = centre + Vector3(0, 20, 0)
	floor_collision.resolution = int(cfg.heightfield_resolution)
	floor_collision.heightfield_mask = STATIC_WEATHER_LAYER
	floor_collision.follow_camera_enabled = false
	floor_collision.update_mode = GPUParticlesCollisionHeightField3D.UPDATE_MODE_WHEN_MOVED
	add_child(floor_collision)
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
	var mat := StandardMaterial3D.new()
	var c: Array = cfg.color
	mat.albedo_color = Color(c[0], c[1], c[2], c[3])
	mat.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	mat.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	mat.cull_mode = BaseMaterial3D.CULL_DISABLED
	mesh.material = mat
	rain.draw_pass_1 = mesh
	add_child(rain)
	_follow()


func restart() -> void:
	if rain != null:
		rain.restart(true)


func _follow() -> void:
	if camera != null and rain != null:
		rain.global_position = camera.global_position + Vector3.UP * float(Resources.config().rain.height_above_camera_m)


func _process(_delta: float) -> void:
	_follow()
