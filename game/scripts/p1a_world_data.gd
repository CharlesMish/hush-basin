class_name P1AWorldData
extends RefCounted

const AUTHORITY_VERSION := "1.2.3"
const MANIFEST_PATH := "res://world/p1a_world_manifest.json"
const ROUTES_PATH := "res://world/generated/route_bake.json"
const GEOMETRY_PATH := "res://world/generated/geometry_polygons.json"
const SOLIDS_PATH := "res://world/generated/solid_meshes.json"
const TERRAIN_META_PATH := "res://world/generated/terrain_metadata.json"
const HEIGHT_PATH := "res://world/generated/heightfield_i16le.bin"
const SURFACE_PATH := "res://world/generated/surface_classes_u8.bin"
const DIAGNOSTIC_PATH := "res://tests/fixtures/diagnostic_harness.json"

const EXPECTED_HASHES := {
	HEIGHT_PATH: "f377a1034406ee2f35232c01f6cb80be8dd43d13267e3821d1edcab9a9735b88",
	SURFACE_PATH: "3d7466384a52bb8033e5fad5acd014a2daedec76475d5ad21ff13a94cee73949",
	ROUTES_PATH: "d2acb912bcebc35a325971bed2b8b33854e44d1833517423d5f52d846cf094a6",
	GEOMETRY_PATH: "ed1ea320431655fb36292fc4e9cbdf7a708e08841ddcf8fb819dfe8df9062766",
	SOLIDS_PATH: "72f36973cde5e6f9c53a09086f7decbb3c4e7f56cfcff7925e9f8de4b8380201",
	TERRAIN_META_PATH: "1843bd1dc20fb5d488170774437ae32839c5e117b298d22753a82a3f276bc486",
	DIAGNOSTIC_PATH: "e01a2750c38902b2127d3c5ed7f6c2171d6338b186a217804d8fc6ae0d86d7bf",
}

var manifest: Dictionary
var routes: Dictionary
var geometries: Dictionary
var solids: Dictionary
var terrain_meta: Dictionary
var diagnostic: Dictionary
var height_bytes: PackedByteArray
var surface_bytes: PackedByteArray


func load_all() -> bool:
	for path in EXPECTED_HASHES:
		if not FileAccess.file_exists(path):
			push_error("P1A required artifact missing: %s" % path)
			return false
		if FileAccess.get_sha256(path) != EXPECTED_HASHES[path]:
			push_error("P1A artifact identity mismatch: %s" % path)
			return false
	manifest = _load_json(MANIFEST_PATH)
	routes = _load_json(ROUTES_PATH).get("routes", {})
	geometries = _load_json(GEOMETRY_PATH).get("geometries", {})
	solids = _load_json(SOLIDS_PATH).get("meshes", {})
	terrain_meta = _load_json(TERRAIN_META_PATH)
	diagnostic = _load_json(DIAGNOSTIC_PATH)
	height_bytes = FileAccess.get_file_as_bytes(HEIGHT_PATH)
	surface_bytes = FileAccess.get_file_as_bytes(SURFACE_PATH)
	var grid: Dictionary = terrain_meta.get("grid", {})
	var expected_samples := int(grid.get("vertex_count_x", 0)) * int(grid.get("vertex_count_z", 0))
	if height_bytes.size() != expected_samples * 2 or surface_bytes.size() != expected_samples:
		push_error("P1A terrain byte count does not match metadata")
		return false
	return true


func height_at_index(index: int) -> float:
	return float(height_bytes.decode_s16(index * 2)) * 0.001


func terrain_height_at(world_x: float, world_z: float) -> float:
	var grid: Dictionary = terrain_meta.grid
	var origin: Array = grid.origin_xz_m
	var spacing := float(grid.spacing_m)
	var width := int(grid.vertex_count_x)
	var depth := int(grid.vertex_count_z)
	var fx := clampf((world_x - float(origin[0])) / spacing, 0.0, float(width - 1))
	var fz := clampf((world_z - float(origin[1])) / spacing, 0.0, float(depth - 1))
	var ix := mini(int(floor(fx)), width - 2)
	var iz := mini(int(floor(fz)), depth - 2)
	var tx := fx - float(ix)
	var tz := fz - float(iz)
	var h00 := height_at_index(iz * width + ix)
	var h10 := height_at_index(iz * width + ix + 1)
	var h01 := height_at_index((iz + 1) * width + ix)
	var h11 := height_at_index((iz + 1) * width + ix + 1)
	# Frozen diagonal is (ix,iz) -> (ix+1,iz+1).
	if tz <= tx:
		return h00 + tx * (h10 - h00) + tz * (h11 - h10)
	return h00 + tz * (h01 - h00) + tx * (h11 - h01)


func geometry_contains(geometry_id: String, point: Vector2) -> bool:
	var geometry: Dictionary = geometries.get(geometry_id, {})
	for component_value in geometry.get("components", []):
		var component: Dictionary = component_value
		if not _ring_contains(component.get("exterior_ccw_xz_m", []), point):
			continue
		var in_hole := false
		for hole in component.get("holes_cw_xz_m", []):
			if _ring_contains(hole, point):
				in_hole = true
				break
		if not in_hole:
			return true
	return false


func geometry_boundary_distance(geometry_id: String, point: Vector2) -> float:
	var result := INF
	var geometry: Dictionary = geometries.get(geometry_id, {})
	for component_value in geometry.get("components", []):
		var component: Dictionary = component_value
		result = minf(result, _ring_distance(component.get("exterior_ccw_xz_m", []), point))
		for hole in component.get("holes_cw_xz_m", []):
			result = minf(result, _ring_distance(hole, point))
	return result


func nearest_route_sample(route_id: String, point: Vector2) -> Dictionary:
	var route: Dictionary = routes.get(route_id, {})
	var points: Array = route.get("points_xz_m", [])
	var best_d2 := INF
	var best_index := 0
	var best_t := 0.0
	var chainage := 0.0
	var best_chainage := 0.0
	for index in maxi(0, points.size() - 1):
		var a := Vector2(float(points[index][0]), float(points[index][1]))
		var b := Vector2(float(points[index + 1][0]), float(points[index + 1][1]))
		var segment := b - a
		var length_squared := segment.length_squared()
		var t := clampf((point - a).dot(segment) / length_squared, 0.0, 1.0) if length_squared > 0.0 else 0.0
		var d2 := point.distance_squared_to(a + segment * t)
		var segment_length := sqrt(length_squared)
		if d2 < best_d2:
			best_d2 = d2
			best_index = index
			best_t = t
			best_chainage = chainage + segment_length * t
		chainage += segment_length
	return {
		"distance_m": sqrt(best_d2),
		"segment_index": best_index,
		"segment_t": best_t,
		"chainage_m": best_chainage,
		"route_length_m": float(route.get("baked_polyline_length_m", chainage)),
	}


static func xz(value: Array) -> Vector2:
	return Vector2(float(value[0]), float(value[1]))


static func _load_json(path: String) -> Dictionary:
	var parsed = JSON.parse_string(FileAccess.get_file_as_string(path))
	if parsed is Dictionary:
		return parsed
	push_error("P1A JSON parse failed: %s" % path)
	return {}


static func _ring_contains(ring: Array, point: Vector2) -> bool:
	var inside := false
	var count := ring.size()
	if count < 3:
		return false
	var previous := xz(ring[count - 1])
	for value in ring:
		var current := xz(value)
		if ((current.y > point.y) != (previous.y > point.y)):
			var cross_x := (previous.x - current.x) * (point.y - current.y) / (previous.y - current.y) + current.x
			if point.x < cross_x:
				inside = not inside
		previous = current
	return inside


static func _ring_distance(ring: Array, point: Vector2) -> float:
	var result := INF
	if ring.size() < 2:
		return result
	var previous := xz(ring[ring.size() - 1])
	for value in ring:
		var current := xz(value)
		var segment := current - previous
		var length_squared := segment.length_squared()
		var t := clampf((point - previous).dot(segment) / length_squared, 0.0, 1.0) if length_squared > 0.0 else 0.0
		result = minf(result, point.distance_to(previous + segment * t))
		previous = current
	return result
