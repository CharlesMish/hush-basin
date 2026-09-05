extends RefCounted
## Loads offline-baked native textures. No surface generation or scene objects.
const ROOT := "res://presentation/generated/"
static func material() -> StandardMaterial3D:
	var m := StandardMaterial3D.new()
	m.albedo_color = Color.WHITE
	m.albedo_texture = ImageTexture.create_from_image(load(ROOT + "quiet_surfaces_albedo.res") as Image)
	m.metallic = 0.0
	m.roughness = 1.0
	m.roughness_texture = ImageTexture.create_from_image(load(ROOT + "quiet_surfaces_roughness.res") as Image)
	m.roughness_texture_channel = BaseMaterial3D.TEXTURE_CHANNEL_RED
	m.texture_filter = BaseMaterial3D.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS
	m.texture_repeat = false
	m.cull_mode = BaseMaterial3D.CULL_DISABLED
	return m
