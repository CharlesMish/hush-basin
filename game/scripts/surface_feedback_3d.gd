class_name SurfaceFeedback3D
extends Node3D

const EMISSION_SPEED_THRESHOLD := 2.5
const FULL_EMISSION_SPEED := 22.0
const PARTICLE_COUNT := 128
const PARTICLE_LIFETIME := 0.68

@export var craft_path: NodePath

@onready var craft: CraftController = get_node(craft_path) as CraftController

var emission_ratio: float = 0.0
var _emitter: GPUParticles3D


func _ready() -> void:
	_build_emitter()


func _physics_process(_delta: float) -> void:
	update_feedback()


func update_feedback() -> void:
	if craft == null or _emitter == null:
		emission_ratio = 0.0
		return
	var data := craft.telemetry()
	var speed := float(data.tangential_speed)
	var supported := int(data.probe_hits) > 0 and float(data.measured_height) >= 0.0
	var finite_sample := (
		is_finite(speed)
		and MotionMath.is_finite_vector(craft.global_position)
		and MotionMath.is_finite_vector(craft.support_normal)
	)
	if not supported or not finite_sample or speed <= EMISSION_SPEED_THRESHOLD:
		emission_ratio = 0.0
		_emitter.amount_ratio = 0.0
		_emitter.emitting = false
		return
	emission_ratio = clampf(
		(speed - EMISSION_SPEED_THRESHOLD) / (FULL_EMISSION_SPEED - EMISSION_SPEED_THRESHOLD),
		0.0,
		1.0
	)
	var normal := MotionMath.safe_normalize(craft.support_normal, Vector3.UP)
	var tangent := MotionMath.tangent_component(craft.velocity, normal)
	var spray_direction := MotionMath.safe_normalize(-tangent, -craft.global_transform.basis.z)
	var right := MotionMath.safe_normalize(normal.cross(spray_direction), Vector3.RIGHT)
	global_basis = Basis(right, normal, spray_direction).orthonormalized()
	global_position = craft.global_position - normal * float(data.measured_height) + normal * 0.10
	_emitter.amount_ratio = emission_ratio
	_emitter.emitting = emission_ratio > 0.0


func _build_emitter() -> void:
	_emitter = GPUParticles3D.new()
	_emitter.name = "ContinuousSpray"
	_emitter.amount = PARTICLE_COUNT
	_emitter.lifetime = PARTICLE_LIFETIME
	_emitter.fixed_fps = 30
	_emitter.local_coords = false
	_emitter.one_shot = false
	_emitter.emitting = false
	_emitter.amount_ratio = 0.0
	_emitter.visibility_aabb = AABB(Vector3(-6.0, -2.0, -6.0), Vector3(12.0, 8.0, 12.0))

	var process_material := ParticleProcessMaterial.new()
	process_material.direction = Vector3(0.0, 0.58, 1.0).normalized()
	process_material.spread = 34.0
	process_material.gravity = Vector3(0.0, -3.2, 0.0)
	process_material.initial_velocity_min = 1.2
	process_material.initial_velocity_max = 3.8
	process_material.scale_min = 0.55
	process_material.scale_max = 1.15
	process_material.color = Color(0.76, 0.82, 0.76, 0.58)
	_emitter.process_material = process_material

	var particle_mesh := QuadMesh.new()
	particle_mesh.size = Vector2(0.10, 0.10)
	var particle_material := StandardMaterial3D.new()
	particle_material.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	particle_material.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	particle_material.billboard_mode = BaseMaterial3D.BILLBOARD_ENABLED
	particle_material.albedo_color = Color(0.78, 0.84, 0.78, 0.62)
	particle_mesh.material = particle_material
	_emitter.draw_pass_1 = particle_mesh
	add_child(_emitter)
