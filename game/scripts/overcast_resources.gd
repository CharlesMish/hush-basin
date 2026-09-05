extends RefCounted
## Visual resources only. World source arrays and all mechanics remain inputs.

const CONFIG_PATH := "res://presentation/warm_overcast_v1.json"
static var _config: Dictionary = {}
static var _sky: Sky
static var sky_image: Image

static func config() -> Dictionary:
	if _config.is_empty():
		_config = JSON.parse_string(FileAccess.get_file_as_string(CONFIG_PATH))
	return _config

static func rgb(values: Array) -> Color:
	return Color(values[0], values[1], values[2])

static func cloud_image() -> Image:
	var cfg: Dictionary = config().sky
	var noise := FastNoiseLite.new()
	noise.seed = int(cfg.seed)
	noise.noise_type = FastNoiseLite.TYPE_SIMPLEX_SMOOTH
	noise.frequency = float(cfg.frequency)
	noise.fractal_octaves = int(cfg.octaves)
	noise.fractal_type = FastNoiseLite.FRACTAL_FBM
	var result := Image.create(int(cfg.width), int(cfg.height), false, Image.FORMAT_RGB8)
	var dark := rgb(cfg.cloud_dark)
	var light := rgb(cfg.cloud_light)
	var horizon := rgb(cfg.horizon)
	var ground := rgb(cfg.ground)
	for y in result.get_height():
		var latitude := PI * (0.5 - float(y) / float(result.get_height() - 1))
		var elevation := sin(latitude)
		for x in result.get_width():
			var longitude := TAU * float(x) / float(result.get_width() - 1)
			# Spherical sampling closes longitude and poles without a texture seam.
			var direction := Vector3(cos(latitude) * cos(longitude), elevation, cos(latitude) * sin(longitude))
			var value := noise.get_noise_3dv(direction * Vector3(1.0, 2.2, 1.0)) * 0.5 + 0.5
			var cover := smoothstep(0.20, float(cfg.coverage), value)
			var clouds := dark.lerp(light, cover)
			var c := horizon.lerp(clouds, smoothstep(0.015, float(cfg.horizon_fade), maxf(0.0, elevation)))
			if elevation < 0.0:
				c = horizon.lerp(ground, smoothstep(0.0, 0.65, -elevation))
			result.set_pixel(x, y, c)
	# Canonicalize the duplicate longitude pixel for exact seam verification.
	for y in result.get_height():
		result.set_pixel(result.get_width() - 1, y, result.get_pixel(0, y))
	return result

static func sky() -> Sky:
	if _sky == null:
		sky_image = cloud_image()
		var material := PanoramaSkyMaterial.new()
		material.panorama = ImageTexture.create_from_image(sky_image)
		_sky = Sky.new()
		_sky.sky_material = material
		_sky.process_mode = Sky.PROCESS_MODE_QUALITY
	return _sky

static func terrain_color(base: Color, surface_class: int) -> Color:
	if config().damp.paved_classes.has(surface_class):
		return Color(base.r * float(config().damp.paving_value), base.g * float(config().damp.paving_value), base.b * float(config().damp.paving_value), base.a)
	return base

static func roughness_texture(width: int, height: int, classes: PackedByteArray) -> ImageTexture:
	var cfg: Dictionary = config().damp
	var image := Image.create(width, height, false, Image.FORMAT_L8)
	for y in height:
		for x in width:
			var roughness := float(cfg.paving_roughness) if cfg.paved_classes.has(int(classes[y * width + x])) else float(cfg.mineral_roughness)
			image.set_pixel(x, y, Color(roughness, roughness, roughness))
	return ImageTexture.create_from_image(image)

static func environment(gate: Node3D) -> void:
	var cfg: Dictionary = config().lighting
	var env: Environment = gate.get_node("WorldEnvironment").environment
	env.sky = sky()
	env.ambient_light_color = rgb(cfg.ambient_color)
	env.ambient_light_energy = float(cfg.ambient_energy)
	var sun: DirectionalLight3D = gate.get_node("Sun")
	sun.light_color = rgb(cfg.sun_color)
	sun.light_energy = float(cfg.sun_energy)
	sun.shadow_opacity = float(cfg.shadow_opacity)
	sun.light_angular_distance = float(cfg.sun_angular_distance)
