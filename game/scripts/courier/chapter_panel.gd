extends "res://scripts/courier/narrative_panel.gd"
const Chapter=preload("res://scripts/courier/chapter_text.gd")
func display(id: String,index: int,summary: bool,reviewing: bool,receipt: String,armed: bool) -> void:
	show()
	var speaker: String=Chapter.SPEAKER.get(id,"")
	portrait.visible=not speaker.is_empty()
	if portrait.visible:portrait.texture=load("res://presentation/narrative/"+speaker+".png")
	heading.text={"ren":"REN · Relay operator","ivo":"IVO · Fabrication","tess":"TESS · Mending"}.get(speaker,Chapter.PLACES[Chapter.HOME[id]].to_upper())+(" / Review" if reviewing else "")
	caption.text="You pass on Ivo’s invitation." if id=="relay" and index==1 else Chapter.SOCK_TICKET if id=="quarry_offer" else Chapter.TICKET if id=="coda" else ""
	caption.visible=not caption.text.is_empty()
	speech.text=Chapter.SUMMARIES.get(id,"Exchange complete.") if summary else Chapter.LINES[id][index]
	if summary and id in Chapter.OFFERS:
		speech.text+="\n"+Chapter.pickup_label(Chapter.job(Chapter.OFFERS[id]))
	speech.add_theme_font_size_override("font_size",19 if summary else 22)
	footer.text=receipt if summary or not receipt.is_empty() else "%d / %d" % [index+1,Chapter.LINES[id].size()]
	next_button.visible=not summary;back_button.visible=not summary and index>0;skip_button.visible=not summary
	accept_button.visible=summary and not reviewing and id in Chapter.OFFERS;accept_button.disabled=not armed
	accept_button.text=Chapter.ACCEPT.get(id,"Accept")+" · Enter / B"
	decline_button.visible=summary;decline_button.text=("Close" if reviewing or not id in Chapter.OFFERS else Chapter.DECLINE[id])+" · Esc"
