extends RefCounted
## Finite experiment catalog. Ordinary challenge definitions are inherited intact.
const Previous = preload("res://scripts/courier/alpha_contracts.gd")
const LINER_PRICE = Previous.LINER_PRICE
const PROJECT_JOBS := [
 {"id":"relay_stock","destination":"WRK","place":"Works","name":"Receiver kit","character":"To Ivo · Works fabrication","base":120,"bonus":0,"objective":"NONE","target":0,"objective_text":"No optional challenge · every valid delivery contributes","routes":["L6"],"dispatch":"Ren · Relay: Take this kit to Ivo at Works. He builds our receiver.","reaction":"Ivo · Works: I assembled the kit into a finished receiver. Take it to Ren at Relay.","purpose":"Take the receiver kit to Ivo at Works. He builds the finished receiver Ren needs to open local dispatch at Relay."},
 {"id":"relay_receiver","destination":"RLY","place":"Relay","name":"Finished receiver","character":"To Ren · Relay installation","base":140,"bonus":0,"objective":"NONE","target":0,"objective_text":"No optional challenge · every valid delivery contributes","routes":["-R0","-L4"],"dispatch":"Ivo · Works: Finished receiver for Ren. Relay can dispatch work once it is installed.","reaction":"Ren · Relay: Your receiver is installed. We can dispatch from here now. A Market return pouch is available if you want it.","purpose":"Carry Ivo's finished receiver to Ren at Relay. Ren installs it so local dispatch can begin."}
]
const OUTBOUND := {"id":"relay_return","destination":"MRK","place":"Market","name":"Market return pouch","character":"Relay > Market · open route","base":100,"bonus":0,"objective":"NONE","target":0,"objective_text":"Ordinary delivery · no mastery slot","routes":["L4","L5"],"dispatch":"Ren · Relay: This pouch is bound for Market. Thanks for getting our desk working.","reaction":"Market received the return pouch. Relay can send work now.","purpose":"Ren has a Market return pouch available. Accept only when ready; any legal route."}

static func ordinary(index: int) -> Dictionary:
	var c: Dictionary=Previous.job(index).duplicate(true)
	if index==0:
		c.merge({"character":"Market > Depot · basic delivery","bonus":0,"objective":"NONE","target":0,"objective_text":"Basic delivery · no mastery slot","dispatch":"Fresh seals for the freight office. Take any line you like."},true)
	return c

static func project_job(index: int, neutral: bool=false) -> Dictionary:
	var c: Dictionary=PROJECT_JOBS[index].duplicate(true)
	if neutral:
		c.name="Mounting stock" if index==0 else "Receiver shipment"
		c.character="Market > Works" if index==0 else "Works > Relay"
		c.purpose="Deliver to Works, then collect the Relay shipment here." if index==0 else "Deliver to Relay. Outbound work becomes available there."
		c.dispatch=c.purpose
		c.reaction="Received. Relay shipment available here." if index==0 else "Received. Outbound work available here."
	return c

static func outbound(neutral: bool=false) -> Dictionary:
	var c: Dictionary=OUTBOUND.duplicate(true)
	if neutral:c.dispatch="Market is expecting this pouch.";c.reaction="Return pouch received."
	return c
