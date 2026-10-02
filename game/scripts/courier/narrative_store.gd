extends "res://scripts/courier/relay_project.gd"
## Same two project flags, with a bounded resume envelope. Old saves are read-only.
const PATH := "user://narrative_presence_v01.json"
const VERSION := "hush-basin-narrative-presence-v0.1"
var record: Dictionary={"seen":[],"parcel":"","pending":"","quarry_done":false,"checkpoint":{}}

func _init(path: String=PATH) -> void:
	super(path)

func load_state() -> Dictionary:
	if _save_path==PATH and not FileAccess.file_exists(PATH):
		var legacy=load("res://scripts/courier/relay_project.gd").new()
		var previous: Dictionary=legacy.load_state()
		if not previous.ok:return _failure(previous.status,previous.error)
		if legacy.stage()>0:
			record.seen=["market","works"] if legacy.stage()==1 else ["market","works","relay"]
			var copied:=_write_document(true,legacy.stage()==2)
			if not copied.ok:return _failure(copied.status,copied.error)
	var result: Dictionary=super.load_state()
	if result.ok and FileAccess.file_exists(_save_path):record=_read_document(_save_path).document.narrative.duplicate(true)
	return result

func commit() -> bool:
	if not _loaded:return false
	var result:=_write_document(_fabrication_stock,_dispatch_receiver)
	last_error="" if result.ok else String(result.error)
	return result.ok

func reset_project() -> Dictionary:
	var previous:=record.duplicate(true)
	record={"seen":[],"parcel":"","pending":"","quarry_done":false,"checkpoint":{}}
	var result: Dictionary=super.reset_project()
	if not result.ok:record=previous
	return result

func _read_document(path: String) -> Dictionary:
	var file:=FileAccess.open(path,FileAccess.READ)
	if file==null or file.get_length()>16384:return _bad()
	var parser:=JSON.new()
	if parser.parse(file.get_as_text())!=OK:return _bad()
	var value: Variant=parser.data
	if not value is Dictionary or value.size()!=4 or value.get("format")!=VERSION or typeof(value.get("fabrication_stock"))!=TYPE_BOOL or typeof(value.get("dispatch_receiver"))!=TYPE_BOOL:return _bad()
	if value.dispatch_receiver and not value.fabrication_stock:return _bad()
	var r: Variant=value.get("narrative")
	if not r is Dictionary or r.size()!=5 or not r.get("seen") is Array or not r.get("checkpoint") is Dictionary or typeof(r.get("quarry_done"))!=TYPE_BOOL:return _bad()
	if not r.get("parcel") in ["","relay_stock","relay_receiver","relay_quarry"] or not r.get("pending") in ["","works","relay"]:return _bad()
	if r.parcel=="relay_receiver" and not value.fabrication_stock:return _bad()
	if (r.parcel=="relay_quarry" or r.quarry_done) and not value.dispatch_receiver:return _bad()
	if r.pending=="works" and (not value.fabrication_stock or value.dispatch_receiver or r.parcel!=""):return _bad()
	if r.pending=="relay" and (not value.fabrication_stock or value.dispatch_receiver or r.parcel!="relay_receiver"):return _bad()
	if not r.parcel.is_empty() and r.checkpoint.is_empty():return _bad()
	for id in r.seen:
		if not id in ["market","works","relay","quarry_offer"]:return _bad()
	if not r.checkpoint.is_empty():
		if r.checkpoint.size()!=6:return _bad()
		for key in ["x","y","z","yaw","condition","elapsed"]:
			if not (r.checkpoint.get(key) is float or r.checkpoint.get(key) is int) or not is_finite(float(r.checkpoint[key])):return _bad()
		if r.checkpoint.condition<0 or r.checkpoint.condition>1000 or r.checkpoint.elapsed<0:return _bad()
	return {"ok":true,"document":value}

func _bad() -> Dictionary:
	return {"ok":false,"status":"invalid_save","error":"Narrative save is invalid. Reset Narrative Experiment explicitly to start fresh."}

func _write_document(stock: bool, receiver: bool) -> Dictionary:
	if not _persistent_storage_available():return {"ok":false,"status":"storage_unavailable","error":"Persistent storage is unavailable."}
	var document:={"format":VERSION,"fabrication_stock":stock,"dispatch_receiver":receiver,"narrative":record.duplicate(true)}
	var encoded:=JSON.stringify(document)
	var temporary:=_save_path+".tmp"
	var file:=FileAccess.open(temporary,FileAccess.WRITE)
	if file==null:return {"ok":false,"status":"write_failed","error":"Cannot write narrative save."}
	file.store_string(encoded);file.flush()
	var error:=file.get_error();file.close()
	var verified:=_read_document(temporary)
	if error!=OK or not verified.ok or verified.document!=JSON.parse_string(encoded):return {"ok":false,"status":"write_failed","error":"Narrative save verification failed; prior save is intact."}
	if DirAccess.rename_absolute(temporary,_save_path)!=OK:return {"ok":false,"status":"write_failed","error":"Cannot replace narrative save; prior save is intact."}
	return {"ok":true}
