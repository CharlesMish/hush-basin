extends Node3D
## Separate presentation entry point. No gameplay controller or physics nodes.

const CURRENT_SCENE := preload("res://scenes/vehicle_visual.tscn")
const REFERENCE_SCENE := preload("res://review/quarto_vehicle_v1/r7_visual.tscn")

var _current: Node3D
var _reference: Node3D
var _camera: Camera3D
var _slider: HSlider
var _status: Label
var _amount := 0.0
var _target := 0.0
var _playing := false
var _slow := true
var _original := false
var _energy := "CLEAR"
var _camera_mode := "Orbit"
var _azimuth := 0.72
var _elevation := 0.40
var _distance := 4.7


func _ready() -> void:
	# This isolated studio animates on render frames, outside gameplay physics.
	physics_interpolation_mode = Node.PHYSICS_INTERPOLATION_MODE_OFF
	_current = CURRENT_SCENE.instantiate() as Node3D
	_reference = REFERENCE_SCENE.instantiate() as Node3D
	add_child(_current)
	add_child(_reference)
	_camera = Camera3D.new()
	add_child(_camera)
	_camera.current = true
	_build_stage()
	_build_ui()
	_apply_pose()


func _process(delta: float) -> void:
	if _playing:
		var duration := 3.0 if _slow else (0.24 if _target > _amount else 0.20)
		_amount = move_toward(_amount, _target, delta / duration)
		if is_equal_approx(_amount, _target):
			_playing = false
	_apply_pose()


func _apply_pose() -> void:
	_current.call("set_form_amount", _amount)
	_reference.call("set_form_amount", _amount)
	_current.call("set_energy_state", _energy)
	_reference.call("set_energy_state", _energy)
	_current.visible = not _original
	_reference.visible = _original
	_slider.set_value_no_signal(_amount)
	_status.text = "%s  ·  %s  ·  %d%%  ·  %s" % [
		"Original R7" if _original else "Quarto v1 candidate",
		"Slow inspection" if _slow else "Game cadence: 0.24 / 0.20 s",
		roundi(_amount * 100.0), _energy,
	]
	_update_camera()


func _update_camera() -> void:
	var target := Vector3(0.0, 0.12, 0.0)
	_camera.fov = 43.0
	if _camera_mode == "Game angle":
		_camera.position = Vector3(0.0, 4.8, 8.5)
		target = Vector3(0.0, 0.65, -3.2)
		_camera.fov = lerpf(68.0, 73.5, _amount)
	elif _camera_mode == "Stern":
		_camera.position = Vector3(0.95, 0.75, 3.1)
		target = Vector3(0.0, 0.05, 0.65)
	else:
		_camera.position = target + Vector3(
			sin(_azimuth) * cos(_elevation), sin(_elevation),
			cos(_azimuth) * cos(_elevation)
		) * _distance
	_camera.look_at(target, Vector3.UP)


func _build_stage() -> void:
	var environment := Environment.new()
	environment.background_mode = Environment.BG_COLOR
	environment.background_color = Color(0.12, 0.15, 0.17)
	environment.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	environment.ambient_light_color = Color(0.73, 0.78, 0.82)
	environment.ambient_light_energy = 0.7
	var world_environment := WorldEnvironment.new()
	world_environment.environment = environment
	add_child(world_environment)
	var light := DirectionalLight3D.new()
	light.rotation_degrees = Vector3(-48.0, -32.0, 0.0)
	light.light_color = Color(1.0, 0.91, 0.77)
	light.light_energy = 1.2
	light.shadow_enabled = true
	add_child(light)
	var floor_mesh := PlaneMesh.new()
	floor_mesh.size = Vector2(24.0, 24.0)
	var material := StandardMaterial3D.new()
	material.albedo_color = Color(0.30, 0.265, 0.20)
	material.roughness = 0.90
	var floor_instance := MeshInstance3D.new()
	floor_instance.mesh = floor_mesh
	floor_instance.material_override = material
	floor_instance.position.y = -0.46
	add_child(floor_instance)


func _build_ui() -> void:
	var layer := CanvasLayer.new()
	add_child(layer)
	var margin := MarginContainer.new()
	layer.add_child(margin)
	margin.set_anchors_and_offsets_preset(Control.PRESET_TOP_WIDE)
	margin.add_theme_constant_override("margin_left", 18)
	margin.add_theme_constant_override("margin_right", 18)
	margin.add_theme_constant_override("margin_top", 14)
	var panel := PanelContainer.new()
	margin.add_child(panel)
	var column := VBoxContainer.new()
	column.add_theme_constant_override("separation", 8)
	panel.add_child(column)
	_status = Label.new()
	column.add_child(_status)
	var row := HFlowContainer.new()
	column.add_child(row)
	_button(row, "Original R7", func(): _original = true)
	_button(row, "Quarto v1", func(): _original = false)
	_button(row, "Spread", func(): _target = 0.0; _playing = true)
	_button(row, "Drive", func(): _target = 1.0; _playing = true)
	_button(row, "Pause", func(): _playing = false)
	_button(row, "Slow / game cadence", func(): _slow = not _slow)
	for mode in ["Orbit", "Game angle", "Stern"]:
		_button(row, mode, _select_camera.bind(mode))
	for state in ["CLEAR", "CAUTION", "STRIKE"]:
		_button(row, state.capitalize(), _select_energy.bind(state))
	_slider = HSlider.new()
	_slider.min_value = 0.0
	_slider.max_value = 1.0
	_slider.step = 0.001
	_slider.value_changed.connect(_scrub)
	column.add_child(_slider)
	var help := Label.new()
	help.text = "Space: reverse  ·  Right-drag: orbit  ·  Wheel: zoom  ·  Esc: exit  |  Neutral studio lighting; use the world comparison for the game."
	help.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	column.add_child(help)


func _button(parent: Control, title: String, callback: Callable) -> void:
	var button := Button.new()
	button.text = title
	button.pressed.connect(callback)
	parent.add_child(button)


func _select_camera(mode: String) -> void:
	_camera_mode = mode


func _select_energy(state: String) -> void:
	_energy = state


func _scrub(value: float) -> void:
	_amount = value
	_target = value
	_playing = false


func _unhandled_input(event: InputEvent) -> void:
	if event is InputEventMouseMotion and event.button_mask & MOUSE_BUTTON_MASK_RIGHT:
		_camera_mode = "Orbit"
		_azimuth -= event.relative.x * 0.008
		_elevation = clampf(_elevation + event.relative.y * 0.008, -0.2, 1.4)
	elif event is InputEventMouseButton and event.pressed:
		if event.button_index == MOUSE_BUTTON_WHEEL_UP:
			_distance = maxf(1.4, _distance * 0.90)
		elif event.button_index == MOUSE_BUTTON_WHEEL_DOWN:
			_distance = minf(15.0, _distance / 0.90)
	elif event is InputEventKey and event.pressed and not event.echo:
		if event.physical_keycode == KEY_SPACE:
			_target = 0.0 if _target > 0.5 else 1.0
			_playing = true
		elif event.physical_keycode == KEY_ESCAPE:
			get_tree().quit()
