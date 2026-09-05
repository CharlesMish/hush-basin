extends Node
## Presentation observer in a separate comparison entry point.
## The current controller continues to own all game state and the live rig.

const REFERENCE_SCENE := preload("res://review/quarto_vehicle_v1/r7_visual.tscn")

var _current: Node3D
var _reference: Node3D
var _craft: CraftController
var _label: Label
var _original := false


func _ready() -> void:
	# Observe after the controller and RunLayer (priority 200) finish their tick.
	process_physics_priority = 300
	var world := $Game/DistrictZeroP1A as P1AWorldGate
	_craft = world.craft
	_current = _craft.get_node("VisualRoot") as Node3D
	_reference = REFERENCE_SCENE.instantiate() as Node3D
	_reference.name = "ComparisonReferenceVisual"
	_craft.add_child(_reference)
	_craft.reset_performed.connect(_on_craft_reset)
	_sync_reference()
	_reference.reset_physics_interpolation()
	var layer := CanvasLayer.new()
	layer.layer = 20
	add_child(layer)
	var panel := PanelContainer.new()
	layer.add_child(panel)
	panel.set_anchors_and_offsets_preset(Control.PRESET_TOP_RIGHT)
	panel.offset_left = -380.0
	panel.offset_right = -14.0
	panel.offset_top = 12.0
	var column := VBoxContainer.new()
	panel.add_child(column)
	_label = Label.new()
	column.add_child(_label)
	var row := HBoxContainer.new()
	column.add_child(row)
	var old_button := Button.new()
	old_button.text = "Original R7"
	old_button.pressed.connect(func(): _original = true)
	row.add_child(old_button)
	var new_button := Button.new()
	new_button.text = "Quarto v1"
	new_button.pressed.connect(func(): _original = false)
	row.add_child(new_button)
	_update_comparison()


func _process(_delta: float) -> void:
	_update_comparison()


func _physics_process(_delta: float) -> void:
	_sync_reference()


func _sync_reference() -> void:
	_reference.transform = _current.transform
	_reference.call("set_form_amount", _craft.fold_amount)
	_reference.call("set_energy_state", _craft.clearance_state)


func _on_craft_reset(_count: int, _reason: String) -> void:
	_sync_reference()
	_reference.reset_physics_interpolation()


func _update_comparison() -> void:
	_reference.visible = _original
	_current.visible = not _original
	_label.text = "Vehicle comparison · %s\nF6 switches visuals; normal game controls" % (
		"Original R7" if _original else "Quarto v1 candidate"
	)


func _unhandled_key_input(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed and not event.echo:
		if event.physical_keycode == KEY_F6:
			_original = not _original
