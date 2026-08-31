extends SceneTree

const MAIN_SCENE := preload("res://scenes/district_zero_p1a.tscn")
const BASELINE_PATH := "res://tests/fixtures/v1_2_6_ray_classification_baseline.json"
const EXACT_ENGINE := "4.7.1.stable.official.a13da4feb"

var output_dir := ""

func _initialize() -> void:
    call_deferred("_run")

func _run() -> void:
    output_dir = _arg("--output-dir")
    if output_dir.is_empty():
        _finish({"status":"BLOCKED/NOT TESTABLE","blocker":"--output-dir required"}, 2)
        return
    DirAccess.make_dir_recursive_absolute(output_dir)
    var engine := _engine_identity()
    if engine != EXACT_ENGINE:
        _finish({"status":"BLOCKED/NOT TESTABLE","blocker":"exact engine mismatch","required":EXACT_ENGINE,"observed":engine}, 2)
        return
    var parsed = JSON.parse_string(FileAccess.get_file_as_string(BASELINE_PATH))
    if not parsed is Dictionary:
        _finish({"status":"BLOCKED/NOT TESTABLE","blocker":"ray baseline unreadable"}, 2)
        return
    var baseline: Dictionary = parsed
    var results := {}
    results["FREE_ROAM"] = await _capture_view("FREE_ROAM", baseline["free_roam"])
    results["A1_FAMILIARIZATION"] = await _capture_view("A1_FAMILIARIZATION", baseline["a1"])
    var mismatches: Array = []
    for view in results:
        for item in results[view].get("ray_mismatches", []):
            mismatches.append(item)
    var result := {
        "schema":"district_zero.p1a.v1_2_7.visual_probe_result.v1",
        "status":"PASS" if mismatches.is_empty() else "FAIL",
        "engine_identity":engine,
        "viewport_size_px":[1280,720],
        "views":results,
        "ray_result":{
            "schema":"district_zero.p1a.v1_2_7.ray_classification_comparison.v1",
            "status":"PASS" if mismatches.is_empty() else "FAIL",
            "sample_count":14,
            "mismatch_count":mismatches.size(),
            "mismatches":mismatches,
        },
    }
    _finish(result, 0 if mismatches.is_empty() else 1)

func _capture_view(view: String, expected: Dictionary) -> Dictionary:
    var gate := MAIN_SCENE.instantiate() as P1AWorldGate
    get_root().add_child(gate)
    await process_frame
    gate.craft.set_physics_process(false)
    gate.telemetry.set_physics_process(false)
    gate.get_node("UI").visible = false
    gate.craft.velocity = Vector3.ZERO
    gate.craft.clear_pending_hop()
    if view == "FREE_ROAM":
        gate.craft.global_transform = Transform3D(Basis.IDENTITY.rotated(Vector3.UP, -1.989022), Vector3(0.0, 1.5713321685791, 20.0))
        gate.craft.fold_amount = 0.0
    else:
        gate.craft.global_transform = Transform3D(Basis.IDENTITY.rotated(Vector3.UP, -0.045422), Vector3(-170.0, 1.55, 35.0))
        gate.craft.fold_amount = 1.0
    gate.craft.reset_physics_interpolation()
    gate.camera_rig.snap_to_target()
    await process_frame
    await process_frame
    var camera := gate.get_node("CameraRig/Camera") as Camera3D
    var sun := gate.get_node("Sun") as DirectionalLight3D
    var prefix := "free-roam" if view == "FREE_ROAM" else "a1"
    var on_path := output_dir.path_join(prefix + "-after-native.png")
    var off_path := output_dir.path_join(prefix + "-after-shadow-off-reference.png")
    var image := get_root().get_viewport().get_texture().get_image()
    image.save_png(on_path)
    var records := _ray_records(gate, camera, expected.get("records", {}), view)
    sun.shadow_enabled = false
    await process_frame
    await process_frame
    image = get_root().get_viewport().get_texture().get_image()
    image.save_png(off_path)
    sun.shadow_enabled = true
    var mismatches: Array = []
    for rid in records:
        var current: Dictionary = records[rid]
        var wanted: Dictionary = expected.get("records", {}).get(rid, {})
        for key in ["classification","collision_node","collision_source_geometry_id","render_node"]:
            if current.get(key) != wanted.get(key):
                mismatches.append({"view":view,"record_id":rid,"field":key,"expected":wanted.get(key),"observed":current.get(key)})
    var cp := camera.global_position
    var result := {
        "camera":{"global_position_xyz_m":[cp.x,cp.y,cp.z],"fov_degrees":camera.fov,"near_m":camera.near,"far_m":camera.far},
        "images":{"shadow_on":on_path,"shadow_off":off_path},
        "records":records,
        "ray_mismatches":mismatches,
    }
    gate.queue_free()
    await process_frame
    return result

func _ray_records(gate: P1AWorldGate, camera: Camera3D, expected_records: Dictionary, view: String) -> Dictionary:
    var out := {}
    var viewport := Vector2(1280.0,720.0)
    for rid in expected_records:
        var expected: Dictionary = expected_records[rid]
        var nxy: Array = expected.get("normalized_screen_xy", [0.5,0.5])
        var screen := Vector2(float(nxy[0])*viewport.x, float(nxy[1])*viewport.y)
        var origin := camera.project_ray_origin(screen)
        var direction := camera.project_ray_normal(screen).normalized()
        var endpoint := origin + direction * camera.far
        var query := PhysicsRayQueryParameters3D.create(origin, endpoint)
        query.exclude = [gate.craft.get_rid()]
        var hit := gate.get_world_3d().direct_space_state.intersect_ray(query)
        var collision_node = null
        var collision_source = null
        if not hit.is_empty():
            var collider = hit.get("collider")
            if collider is Node:
                collision_node = String(collider.get_path())
                if collider.has_meta("source_geometry_id"):
                    collision_source = String(collider.get_meta("source_geometry_id"))
        var render_node = _nearest_render_node(gate.world, origin, endpoint)
        var classification := "GENUINE_EMPTY_SPACE" if collision_node == null and render_node == null else "RENDERED_AND_COLLIDABLE_SURFACE" if collision_node != null and render_node != null else "CLASSIFICATION_MISMATCH"
        out[rid] = {
            "normalized_screen_xy":nxy,
            "classification":classification,
            "collision_node":collision_node,
            "collision_source_geometry_id":collision_source,
            "render_node":render_node,
        }
    return out

func _nearest_render_node(world: Node3D, origin: Vector3, endpoint: Vector3):
    var best_distance := INF
    var best_node = null
    for child in world.get_children():
        if not child is MeshInstance3D:
            continue
        var instance := child as MeshInstance3D
        if not instance.visible or instance.mesh == null:
            continue
        var faces: PackedVector3Array = instance.mesh.get_faces()
        var xf := instance.global_transform
        for i in range(0, faces.size(), 3):
            var a := xf * faces[i]
            var b := xf * faces[i+1]
            var c := xf * faces[i+2]
            var hit = Geometry3D.segment_intersects_triangle(origin, endpoint, a, b, c)
            if hit == null:
                continue
            var distance := origin.distance_to(hit)
            if distance < best_distance:
                best_distance = distance
                best_node = String(instance.get_path())
    return best_node

func _engine_identity() -> String:
    var info := Engine.get_version_info()
    return "%d.%d.%d.%s.%s.%s" % [int(info.get("major",0)),int(info.get("minor",0)),int(info.get("patch",0)),String(info.get("status","")),String(info.get("build","")),String(info.get("hash","")).substr(0,9)]

func _arg(name: String) -> String:
    var args := OS.get_cmdline_user_args()
    for i in args.size():
        if args[i] == name and i + 1 < args.size():
            return args[i+1]
    return ""

func _finish(value: Dictionary, code: int) -> void:
    var path := output_dir.path_join("probe_result.json") if not output_dir.is_empty() else ""
    if not path.is_empty():
        var file := FileAccess.open(path, FileAccess.WRITE)
        if file:
            file.store_string(JSON.stringify(value, "  ") + "\n")
            file.close()
    print(JSON.stringify(value))
    quit(code)
