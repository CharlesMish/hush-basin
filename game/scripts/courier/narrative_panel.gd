extends CanvasLayer
signal advance
signal back
signal skip
signal accept
signal decline
const Text=preload("res://scripts/courier/narrative_text.gd")
var box: PanelContainer
var portrait: TextureRect
var heading: Label
var caption: Label
var speech: Label
var footer: Label
var next_button: Button
var back_button: Button
var skip_button: Button
var accept_button: Button
var decline_button: Button

func _ready() -> void:
	process_mode=Node.PROCESS_MODE_ALWAYS;layer=60
	box=PanelContainer.new();box.position=Vector2(32,376);box.size=Vector2(1216,312)
	var style:=StyleBoxFlat.new();style.bg_color=Color("202829");style.border_color=Color("9b987e");style.set_border_width_all(1);style.set_content_margin_all(18)
	box.add_theme_stylebox_override("panel",style);add_child(box)
	var row:=HBoxContainer.new();row.add_theme_constant_override("separation",22);box.add_child(row)
	portrait=TextureRect.new();portrait.custom_minimum_size=Vector2(238,260);portrait.expand_mode=TextureRect.EXPAND_IGNORE_SIZE;portrait.stretch_mode=TextureRect.STRETCH_KEEP_ASPECT_COVERED;row.add_child(portrait)
	var column:=VBoxContainer.new();column.size_flags_horizontal=Control.SIZE_EXPAND_FILL;column.add_theme_constant_override("separation",10);row.add_child(column)
	heading=_label(22,column);heading.add_theme_color_override("font_color",Color("efc07f"))
	caption=_label(16,column);caption.add_theme_color_override("font_color",Color("b1cbc5"))
	speech=_label(22,column);speech.custom_minimum_size=Vector2(840,92);speech.autowrap_mode=TextServer.AUTOWRAP_WORD_SMART;speech.size_flags_vertical=Control.SIZE_EXPAND_FILL
	footer=_label(15,column);footer.autowrap_mode=TextServer.AUTOWRAP_WORD_SMART
	var actions:=HBoxContainer.new();actions.add_theme_constant_override("separation",12);column.add_child(actions)
	back_button=_button("Back · ←",func():back.emit(),actions)
	next_button=_button("Advance · Enter / B",func():advance.emit(),actions)
	skip_button=_button("Skip conversation · X",func():skip.emit(),actions)
	accept_button=_button("",func():accept.emit(),actions)
	decline_button=_button("",func():decline.emit(),actions)
	hide()

func _label(size: int,parent: Node) -> Label:
	var l:=Label.new();l.add_theme_font_size_override("font_size",size);parent.add_child(l);return l

func _button(text: String,callback: Callable,parent: Node) -> Button:
	var b:=Button.new();b.text=text;b.focus_mode=Control.FOCUS_NONE;b.add_theme_font_size_override("font_size",17);b.custom_minimum_size.y=38;b.pressed.connect(callback);parent.add_child(b);return b

func display(id: String,index: int,summary: bool,reviewing: bool,receipt: String,armed: bool) -> void:
	show()
	var ivo:=id=="works"
	portrait.texture=preload("res://presentation/narrative/ivo.png") if ivo else preload("res://presentation/narrative/ren.png")
	heading.text=("IVO · Fabrication" if ivo else "REN · Relay operator")+("  /  Past exchange" if reviewing else "")
	caption.text="You pass on Ivo’s invitation." if id=="relay" and index==1 else Text.TICKET if id=="quarry_offer" else ""
	caption.visible=not caption.text.is_empty()
	speech.text=Text.SUMMARY.get(id,"") if summary else Text.LINES[id][index]
	speech.add_theme_font_size_override("font_size",19 if summary else 22)
	footer.text=receipt if summary or id=="quarry_offer" else "%d / %d" % [index+1,Text.LINES[id].size()]
	next_button.visible=not summary;back_button.visible=not summary and index>0;skip_button.visible=not summary
	accept_button.visible=summary and not reviewing;accept_button.disabled=not armed
	accept_button.text=Text.ACCEPT.get(id,"Accept")+" · Enter / B"
	decline_button.visible=summary;decline_button.text="Close review" if reviewing else Text.DECLINE.get(id,"Later")+" · Esc"

