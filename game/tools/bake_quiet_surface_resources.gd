extends SceneTree
## Offline conversion only: ship native textures with their complete mip chains.
func _initialize() -> void:
	var args := OS.get_cmdline_user_args()
	var folder := args[args.find("--folder") + 1]
	for item in [["albedo", Image.FORMAT_RGBA8], ["roughness", Image.FORMAT_R8]]:
		var image := Image.load_from_file(folder.path_join("quiet_surfaces_" + item[0] + ".png"))
		assert(image != null and image.get_size() == Vector2i(2048, 2048))
		image.convert(item[1])
		assert(image.generate_mipmaps() == OK)
		image.resource_scene_unique_id = "QuietSurface" + item[0]
		# A root Image avoids auto-assigned nested resource IDs. Its complete
		# mip chain is uploaded unchanged by the presentation loader.
		assert(ResourceSaver.save(image, folder.path_join("quiet_surfaces_" + item[0] + ".res"), ResourceSaver.FLAG_COMPRESS) == OK)
		assert(ResourceSaver.set_uid(folder.path_join("quiet_surfaces_" + item[0] + ".res"), 91837001 if item[0] == "albedo" else 91837002) == OK)
	quit()
