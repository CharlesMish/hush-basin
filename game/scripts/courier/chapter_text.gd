extends RefCounted
## Opening Chapter v0.1 only. No campaign graph or remote portraits.
const ORDER=["relay_mail","relay_stock","relay_receiver","relay_quarry","tess_jackets","tess_aprons","tess_repairs","tess_patches"]
const ORIGINS={"relay_mail":"MRK","relay_stock":"RLY","relay_receiver":"WRK","relay_quarry":"RLY","tess_jackets":"TES","tess_aprons":"DEP","tess_repairs":"CLN","tess_patches":"TES"}
const PLACES={"MRK":"Market","RLY":"Relay","WRK":"Works","QRY":"Quarry Stores","DEP":"Depot","CLN":"Clinic","TES":"South counter"}
const HOME={"market":"MRK","ren_intro":"RLY","works":"WRK","relay":"RLY","quarry_offer":"RLY","tess_intro":"TES","depot":"DEP","clinic":"CLN","tess_final":"TES","coda":"TES","ticket":"RLY","ren_return":"RLY","ivo_return":"WRK"}
const SPEAKER={"ren_intro":"ren","works":"ivo","relay":"ren","quarry_offer":"ren","tess_intro":"tess","tess_final":"tess","coda":"tess","ren_return":"ren","ivo_return":"ivo"}
const OFFERS={"market":"relay_mail","ren_intro":"relay_stock","works":"relay_receiver","quarry_offer":"relay_quarry","tess_intro":"tess_jackets","depot":"tess_aprons","clinic":"tess_repairs","coda":"tess_patches"}
const LINES={
 "market":["For Relay. Their receiver’s down, so it’s all been landing here."],
 "ren_intro":["I’m Ren. That’s a week of requests this desk couldn’t hear.","I told Quarry we’d be answering again today. Ivo’s got the receiver—he doesn’t know I said today.","These are the last parts. Could you run them to Works? And maybe mention the today part."],
 "works":["Ren promised today? She used to book my whole afternoon with that word.","That finishes it. I made the dial bigger, since she won’t take those gloves off.","Tell her I’ll clear off her chair, if she has time for tea."],
 "relay":["Look at that dial. He remembered the gloves. Thanks for bringing this.","Tell him I’ll—no. I’ll go over after close."],
 "quarry_offer":["Six pairs. I’ve got those on the rack. Want the Quarry run?"],
 "tess_intro":["You’re the courier? I’m Tess. First day at my own counter.","Depot lent me a table for a year. Their jackets are mended—call it rent.","Clinic’s aprons are waiting there too. I’m not leaving this counter on day one."],
 "depot":["Jackets received. Yard’s quieter without her."],
 "clinic":["Aprons received. Shorter ties this time—no more catching on the cupboard.","Three for mending. Blue thread marks the torn pockets."],
 "tess_final":["You’ve brought my first order in. Clinic, of course.","Your rear panel’s scuffed along the edge. You take every corner like that?","Pull in. This’ll take a minute."],
 "coda":["Strong thread. And tell them rope isn’t a repair."],
 "ticket":["QUARRY STORES — Tarp’s split again. Strong thread and patches, please. It’s held together with rope.","RELAY — Ivo says there’s a new mender down south. Try Tess. —R."],
 "ren_return":["Went over to Ivo’s. He talked about hinges for an hour."],
 "ivo_return":["She came by after close. Sat an hour and reorganized my shelves."]
}
const TICKET="QUARRY STORES — Tarp’s split again. Strong thread and patches, please. It’s held together with rope.\nRELAY — Ivo says there’s a new mender down south. Try Tess. —R."
const SOCK_TICKET="QUARRY STORES\nSix pairs of dry socks, please. The old ones are drying on the kettle."
const SUMMARIES={
 "market":"Relay mail → Ren · Relay\nA week of requests that couldn’t reach her desk.",
 "ren_intro":"Receiver kit → Ivo · Works\nLast parts for Ren’s receiver.",
 "works":"Receiver kit → Finished receiver\n\nFinished receiver → Ren · Relay\nRestores Relay dispatch. Ivo’s invitation travels with it.",
 "quarry_offer":"Dry socks → Quarry Stores\nRelay’s first answered request.",
 "tess_intro":"Mended jackets → Depot\nThe freight crew’s jackets. Tess’s rent for a borrowed table.",
 "depot":"Clinic’s aprons → Clinic\nFinished before the move; never collected.\nSouth Cut: S0 → DOG or HOP → S1. Any legal route.",
 "clinic":"Clinic repairs → Tess · South counter\nFirst order to her new address.",
 "tess_final":"Tess’s counter is open.\nHer stitched protective patch is fitted to your rear panel.",
 "coda":"Patch kit → Quarry Stores\nStrong thread and patches, from Tess’s counter.",
 "ticket":"Patch kit → Quarry Stores\nPick up at Tess’s counter. No cargo accepted here."
}
const ACCEPT={"market":"Take Relay mail","ren_intro":"Take kit to Works","works":"Take receiver","quarry_offer":"Take Quarry parcel","tess_intro":"Take jackets","depot":"Take aprons","clinic":"Take repair bag","coda":"Take patch kit"}
const DECLINE={"market":"Not now","ren_intro":"Not now","works":"Leave it here","quarry_offer":"Later","tess_intro":"Not now","depot":"Leave them here","clinic":"Later","coda":"Later"}

static func job(id: String) -> Dictionary:
	var c: Dictionary=preload("res://scripts/courier/relay_contracts.gd").outbound()
	var spec: Dictionary={
	 "relay_mail":{"destination":"RLY","name":"Relay mail","base":100,"routes":["-L5","-L4"],"reaction":"Relay mail received."},
	 "relay_stock":{"destination":"WRK","name":"Receiver kit","base":120,"routes":["L4","R0"],"reaction":"Receiver kit received."},
	 "relay_receiver":{"destination":"RLY","name":"Finished receiver","base":140,"routes":["L7","-A2"],"reaction":"Receiver delivered."},
	 "relay_quarry":{"destination":"QRY","name":"Dry socks","base":100,"routes":["-A1","-A0"],"reaction":"Six pairs received. We can have the kettle back."},
	 "tess_jackets":{"destination":"DEP","name":"Mended jackets","base":100,"routes":["-L2","-L1"],"reaction":LINES.depot[0]},
	 "tess_aprons":{"destination":"CLN","name":"Clinic’s aprons","base":120,"routes":["S0","DOG","S1"],"reaction":LINES.clinic[0]},
	 "tess_repairs":{"destination":"TES","name":"Clinic repairs","base":100,"routes":["-L2"],"reaction":"First order received at Tess’s counter."},
	 "tess_patches":{"destination":"QRY","name":"Patch kit","base":120,"routes":["-L2","-L1","-L0","-A0"],"reaction":"Patches received. Rope’s back on its hook. Come out when you’re not working—we’ll put the kettle on. —B."}
	}[id]
	c.merge(spec,true);c.id=id;c.place=PLACES[c.destination];c.character="To "+String(c.place);c.objective_text="Paid delivery · no timer or quality gate"
	var exchange: String=OFFERS.find_key(id)
	c.purpose=SUMMARIES[exchange];c.dispatch=c.purpose
	return c

static func local_work(hub: String) -> Dictionary:
	var c: Dictionary=preload("res://scripts/courier/relay_contracts.gd").outbound()
	c.id="mending_pickup" if hub=="TES" else "local_"+hub
	c.name="Mended work" if hub=="TES" else "Market post pouch"
	c.destination="DEP" if hub=="TES" else "MRK";c.place=PLACES[c.destination];c.character=PLACES[hub]+" → "+c.place
	c.purpose=c.name+" → "+c.place+"\nOrdinary paid work.";c.dispatch=c.purpose;c.reaction="Mended work received." if hub=="TES" else "Post received at Market.";c.routes=[]
	return c
