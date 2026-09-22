extends Control
## A cargo schematic, not a new world prop. Finished/installed forms use the
## very same front-facing parts and palette as the existing Relay receiver.
var installed:=false
var definition: Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://presentation/relay_annex_v0_1.json"))
func _ready() -> void:
	custom_minimum_size=Vector2(620,62)
	mouse_filter=Control.MOUSE_FILTER_IGNORE
func show_installation(value: bool) -> void:
	installed=value;queue_redraw()
func _draw() -> void:
	var left:=Vector2(242,31);var right:=Vector2(370,31)
	if installed:_receiver(left,false)
	else:
		for i in 3:
			draw_rect(Rect2(left+Vector2(-22+i*15,-15+i*5),Vector2(11,25)),Color(definition.palette.panel))
			draw_rect(Rect2(left+Vector2(-27,17),Vector2(58,5)),Color(definition.palette.relay))
	draw_line(Vector2(293,31),Vector2(321,31),Color(definition.palette.warm),2,true)
	draw_line(Vector2(315,25),Vector2(321,31),Color(definition.palette.warm),2,true)
	draw_line(Vector2(315,37),Vector2(321,31),Color(definition.palette.warm),2,true)
	_receiver(right,installed)
func _receiver(center: Vector2, mount: bool) -> void:
	for part in definition.parts:
		var role: String=part.role
		if not (role.begins_with("receiver_") or role=="status_strip" or (mount and role in ["mount_upright","mount_header","mount_sill"])):continue
		var size:=Vector2(float(part.size[0]),float(part.size[1]))*6.0
		var offset:=Vector2(float(part.p[0]),-(float(part.p[1])-10.0))*6.0
		draw_rect(Rect2(center+offset-size*.5,size),Color(definition.palette[part.color]))
