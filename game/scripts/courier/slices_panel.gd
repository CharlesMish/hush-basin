extends "res://scripts/courier/chapter_panel.gd"
const Slice=preload("res://scripts/courier/slices_text.gd")
func display(id: String,index: int,summary: bool,reviewing: bool,receipt: String,armed: bool) -> void:
	if not id in Slice.SCENES:super.display(id,index,summary,reviewing,receipt,armed);return
	show();var scene: Dictionary=Slice.SCENES[id];var speaker: String=scene.speaker
	portrait.visible=not speaker.is_empty() and not summary
	if portrait.visible:portrait.texture=load("res://presentation/narrative/"+speaker+".png")
	heading.text=Slice.HEADINGS.get(speaker,Chapter.PLACES[scene.home].to_upper())+(" / Review" if reviewing else "")
	caption.text=scene.get("caption","");caption.visible=not caption.text.is_empty() and not summary
	speech.text=Slice.summary(id) if summary else scene.lines[index]
	if summary and scene.offer.is_empty() and not receipt.is_empty():speech.text=receipt
	speech.add_theme_font_size_override("font_size",18 if summary else 22)
	footer.text=receipt.get_slice("\n",0) if not receipt.is_empty() else "%d / %d" % [index+1,scene.lines.size()] if not summary else "No work accepted"
	next_button.visible=not summary;back_button.visible=not summary and index>0;skip_button.visible=not summary
	accept_button.visible=summary and not reviewing and not scene.offer.is_empty();accept_button.disabled=not armed
	accept_button.text="Accept delivery · Enter / B"
	decline_button.visible=summary;decline_button.text=("Not now" if accept_button.visible else "Close")+" · Esc"
