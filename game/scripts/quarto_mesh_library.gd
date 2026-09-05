@tool
extends RefCounted

## Builds immutable presentation meshes once, before normal scalar posing.
## The same explicit triangles are consumed by the portable comparison viewer.
static func assign_meshes(root: Node3D, asset: Dictionary) -> bool:
	var definitions: Dictionary = asset.get("meshes", {})
	var cache: Dictionary = {}
	for record: Dictionary in asset.get("nodes", []):
		if not record.has("mesh"):
			continue
		var mesh_id := String(record["mesh"])
		var instance := root.get_node_or_null(String(record["path"])) as MeshInstance3D
		if instance == null or not definitions.has(mesh_id):
			push_error("Quarto visual mesh binding missing: %s" % record.get("path", ""))
			return false
		if not cache.has(mesh_id):
			var definition: Dictionary = definitions[mesh_id]
			var vertices := PackedVector3Array()
			var normals := PackedVector3Array()
			var indices := PackedInt32Array()
			for point: Array in definition["vertices"]:
				vertices.append(Vector3(float(point[0]), float(point[1]), float(point[2])))
			for normal: Array in definition["normals"]:
				normals.append(Vector3(float(normal[0]), float(normal[1]), float(normal[2])))
			for index in definition["indices"]:
				indices.append(int(index))
			var arrays := []
			arrays.resize(Mesh.ARRAY_MAX)
			arrays[Mesh.ARRAY_VERTEX] = vertices
			arrays[Mesh.ARRAY_NORMAL] = normals
			arrays[Mesh.ARRAY_INDEX] = indices
			var mesh := ArrayMesh.new()
			mesh.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES, arrays)
			cache[mesh_id] = mesh
		instance.mesh = cache[mesh_id] as ArrayMesh
	return true
