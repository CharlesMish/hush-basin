extends RefCounted
## Approved slice text. One portrait state per person; no branching dialogue.
const LINES := {
 "market": ["I’m Ren, from Relay. I told Quarry we’d be taking requests today.", "The last parts just came in. Ivo’s got the receiver core. He doesn’t know I said today.", "Could you run these to Works? And maybe mention the today part."],
 "works": ["Ren promised today? She used to book my whole afternoon with that word.", "That finishes it. I made the dial bigger, since she won’t take those gloves off.", "Tell her I’ll clear off her chair, if she has time for tea."],
 "relay": ["Look at that dial. He remembered the gloves. Thanks for bringing this.", "Tell him I’ll—no. I’ll go over after close."],
 "quarry_offer": ["Six pairs. I’ve got those on the rack. Want the Quarry run?"]
}
const TICKET := "QUARRY STORES\nSix pairs of dry socks, please. The old ones are drying on the kettle."
const RECEIPT := "Six pairs received. We can have the kettle back."
const SUMMARY := {
 "market": "Receiver kit → Ivo · Works\nLast parts for Ren’s receiver.",
 "works": "Receiver kit → Finished receiver\nLarger dial for Ren’s work gloves. Ivo’s invitation travels with it.\n\nFinished receiver → Ren · Relay\nRestores Relay dispatch.",
 "quarry_offer": "Dry socks → Quarry Stores\nRelay’s first answered request."
}
const ACCEPT := {"market":"Take kit to Works", "works":"Take receiver", "quarry_offer":"Take Quarry parcel"}
const DECLINE := {"market":"Not now", "works":"Leave it here", "quarry_offer":"Later"}

static func job(id: String) -> Dictionary:
	var old=preload("res://scripts/courier/relay_contracts.gd")
	var c: Dictionary=old.project_job(0 if id=="relay_stock" else 1) if id!="relay_quarry" else old.outbound()
	if id=="relay_stock":
		c.purpose=SUMMARY.market;c.dispatch="Last parts for Ren’s receiver.";c.reaction="Receiver kit received."
	elif id=="relay_receiver":
		c.purpose="Finished receiver → Ren · Relay\nRestores Relay dispatch.";c.dispatch="Ivo’s finished receiver and invitation for Ren.";c.reaction="Receiver delivered."
	else:
		c.merge({"id":"relay_quarry","destination":"QRY","place":"Quarry","name":"Dry socks","character":"To Quarry Stores","routes":["-A1","-A0"],"purpose":SUMMARY.quarry_offer,"dispatch":"Six pairs of dry socks for Quarry.","reaction":RECEIPT},true)
	return c
