extends RefCounted
## Fine Ground v1: near-range ground detail over the unchanged Quiet Surfaces
## macro maps, plus bounded ambient occlusion and distance haze. Presentation
## only; no geometry, collision, scene objects or gameplay state.
const CONFIG := "res://presentation/fine_ground_v1.json"
const MACRO := "res://presentation/generated/"
const DETAIL := "res://presentation/fine_ground/fine_ground_detail.png"

const SHADER_CODE := """
shader_type spatial;
render_mode cull_disabled;

uniform sampler2D macro_albedo : source_color, filter_linear_mipmap_anisotropic, repeat_disable;
uniform sampler2D macro_roughness : filter_linear_mipmap_anisotropic, repeat_disable;
uniform sampler2D detail_map : filter_linear_mipmap_anisotropic, repeat_enable;
uniform float near_tile_m = 3.0;
uniform float far_tile_m = 11.3;
uniform float far_weight = 0.4;
uniform float mineral_albedo = 0.22;
uniform float asphalt_albedo = 0.16;
uniform float mineral_relief = 0.3;
uniform float asphalt_relief = 0.12;
uniform float fade_start_m = 28.0;
uniform float fade_end_m = 85.0;
uniform vec2 asphalt_roughness_range = vec2(0.7, 0.8);

void fragment() {
	vec3 base = texture(macro_albedo, UV).rgb;
	float rough = texture(macro_roughness, UV).r;
	vec3 world_pos = (INV_VIEW_MATRIX * vec4(VERTEX, 1.0)).xyz;
	// The second, larger layer is rotated and offset so the tile never lines up.
	mat2 turn = mat2(vec2(0.7986, 0.6018), vec2(-0.6018, 0.7986));
	vec4 near_detail = texture(detail_map, world_pos.xz / near_tile_m);
	vec4 far_detail = texture(detail_map, turn * world_pos.xz / far_tile_m + vec2(0.37, 0.61));
	float fade = 1.0 - smoothstep(fade_start_m, fade_end_m, length(VERTEX));
	// Smooth paving already carries lower macro roughness than mineral ground.
	float asphalt = 1.0 - smoothstep(asphalt_roughness_range.x, asphalt_roughness_range.y, rough);
	vec2 grain = mix(near_detail.ba, far_detail.ba, far_weight) * 2.0 - 1.0;
	float tone = mix(grain.x * mineral_albedo, grain.y * asphalt_albedo, asphalt);
	ALBEDO = base * max(0.0, 1.0 + tone * fade);
	ROUGHNESS = rough;
	METALLIC = 0.0;
	vec2 slope = mix(near_detail.rg * 2.0 - 1.0, transpose(turn) * (far_detail.rg * 2.0 - 1.0), far_weight);
	float relief = mix(mineral_relief, asphalt_relief, asphalt) * fade;
	vec3 up = normalize((INV_VIEW_MATRIX * vec4(NORMAL, 0.0)).xyz);
	vec3 bent = normalize(up + vec3(-slope.x, 0.0, -slope.y) * relief);
	NORMAL = normalize((VIEW_MATRIX * vec4(bent, 0.0)).xyz);
}
"""


static func config() -> Dictionary:
	return JSON.parse_string(FileAccess.get_file_as_string(CONFIG))


static func detail_texture() -> ImageTexture:
	# The folder is .gdignore'd: decode directly so a pre-existing editor cache
	# never needs a reimport. Mipmaps of the 256-square tile are cheap and local.
	var image := Image.new()
	var error := image.load_png_from_buffer(FileAccess.get_file_as_bytes(DETAIL))
	if error != OK:
		push_error("Fine Ground detail could not be decoded: %s" % error_string(error))
	image.convert(Image.FORMAT_RGBA8)
	image.generate_mipmaps()
	return ImageTexture.create_from_image(image)


static func material() -> ShaderMaterial:
	var shader := Shader.new()
	shader.code = SHADER_CODE
	var m := ShaderMaterial.new()
	m.shader = shader
	m.set_shader_parameter("macro_albedo", ImageTexture.create_from_image(load(MACRO + "quiet_surfaces_albedo.res") as Image))
	m.set_shader_parameter("macro_roughness", ImageTexture.create_from_image(load(MACRO + "quiet_surfaces_roughness.res") as Image))
	m.set_shader_parameter("detail_map", detail_texture())
	var cfg: Dictionary = config().shader
	for key in cfg:
		var value = cfg[key]
		m.set_shader_parameter(key, Vector2(value[0], value[1]) if value is Array else float(value))
	return m


static func atmosphere(gate: Node3D) -> void:
	var cfg: Dictionary = config().atmosphere
	var env: Environment = gate.get_node("WorldEnvironment").environment
	var ssao: Dictionary = cfg.ssao
	env.ssao_enabled = bool(ssao.enabled)
	env.ssao_radius = float(ssao.radius)
	env.ssao_intensity = float(ssao.intensity)
	env.ssao_power = float(ssao.power)
	env.ssao_detail = float(ssao.detail)
	env.ssao_horizon = float(ssao.horizon)
	env.ssao_sharpness = float(ssao.sharpness)
	var fog: Dictionary = cfg.fog
	env.fog_enabled = bool(fog.enabled)
	env.fog_density = float(fog.density)
	env.fog_light_color = Color(fog.light_color[0], fog.light_color[1], fog.light_color[2])
	env.fog_light_energy = float(fog.light_energy)
	env.fog_aerial_perspective = float(fog.aerial_perspective)
	env.fog_sky_affect = float(fog.sky_affect)
