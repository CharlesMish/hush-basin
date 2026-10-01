extends "res://scripts/courier/relay_project.gd"
## Atomic record for the preserved opening plus the authored successor slices.
const Slice=preload("res://scripts/courier/slices_text.gd")
var delivery_destination:=""
const Text=preload("res://scripts/courier/chapter_text.gd")
const PATH="user://narrative_chapters_v01.json"
const VERSION="hush-basin-narrative-chapters-v0.1"
var record: Dictionary=fresh_record()

static func fresh_record() -> Dictionary:
	return {"step":0,"seen":[],"parcel":"","pending":"","checkpoint":{},"patch":false,"after_arc1":false,"after_arc2":false,"slices":{"done":[],"installed":false,"bedded":false}}
func _init(path: String=PATH) -> void:super(path)
func load_state() -> Dictionary:
	var r: Dictionary=super.load_state()
	if r.ok and FileAccess.file_exists(_save_path):record=_read_document(_save_path).document.chapter.duplicate(true)
	return r
func commit() -> bool:
	if not _loaded:return false
	var r:=_write_document(record.step>=2,record.step>=3)
	last_error="" if r.ok else r.error
	return r.ok
func contribute(id: String,delivered: bool=true) -> Dictionary:
	if not _loaded:return _failure("not_loaded","Chapter progress must load or be explicitly reset.")
	if not delivered:return _result("not_delivered")
	var previous:=record.duplicate(true)
	var step_before:=int(record.step)
	if step_before>=4:record.after_arc1=true
	if step_before>=7 and record.patch:record.after_arc2=true
	var changed: bool=step_before<8 and Text.ORDER[step_before]==id
	if changed:record.step+=1
	elif step_before==8:
		if not id in Slice.JOBS and delivery_destination=="QRY" and "quarry_later" in record.slices.done and not "groove_return" in record.slices.done:record.slices.done.append("groove_return")
		if id in Slice.available(previous):record.slices.done.append(id);changed=true
		if not id in Slice.JOBS and delivery_destination=="CLN" and "new_threshold" in record.slices.done and record.slices.installed and not "clinic_release" in record.slices.done:
			record.slices.done.append("clinic_release");changed=true
		if not id in Slice.JOBS and delivery_destination=="QRY" and "old_threshold" in record.slices.done and record.slices.bedded and not "quarry_later" in record.slices.done:
			record.slices.done.append("quarry_later");changed=true
	if not commit():
		record=previous;return _failure("write_failed",last_error)
	_fabrication_stock=record.step>=2;_dispatch_receiver=record.step>=3
	return _result("contributed" if changed else "ordinary",changed)
func reset_project() -> Dictionary:
	var previous:=record.duplicate(true);record=fresh_record()
	var r: Dictionary=super.reset_project()
	if not r.ok:record=previous
	return r
func _read_document(path: String) -> Dictionary:
	var f:=FileAccess.open(path,FileAccess.READ)
	if f==null or f.get_length()>32768:return _bad()
	var p:=JSON.new()
	if p.parse(f.get_as_text())!=OK:return _bad()
	var d: Variant=p.data
	if not d is Dictionary or d.size()!=4 or d.get("format")!=VERSION:return _bad()
	var r: Variant=d.get("chapter")
	if not r is Dictionary or r.size()!=9:return _bad()
	if not (r.get("step") is float or r.get("step") is int) or not is_finite(float(r.step)) or float(r.step)!=int(r.step) or r.step<0 or r.step>8:return _bad()
	if typeof(d.get("fabrication_stock"))!=TYPE_BOOL or typeof(d.get("dispatch_receiver"))!=TYPE_BOOL or d.fabrication_stock!=(r.step>=2) or d.dispatch_receiver!=(r.step>=3):return _bad()
	if not r.get("seen") is Array or not r.get("checkpoint") is Dictionary or not r.get("parcel") is String or not r.get("pending") is String:return _bad()
	for flag in ["patch","after_arc1","after_arc2"]:
		if typeof(r.get(flag))!=TYPE_BOOL:return _bad()
	if r.patch and r.step<7 or r.after_arc1 and r.step<4 or r.after_arc2 and (r.step<7 or not r.patch):return _bad()
	if r.step==8 and not r.after_arc2:return _bad()
	if not r.get("slices") is Dictionary or r.slices.size()!=3:return _bad()
	var s: Dictionary=r.slices
	if not s.get("done") is Array or typeof(s.get("installed"))!=TYPE_BOOL or typeof(s.get("bedded"))!=TYPE_BOOL:return _bad()
	var unique: Array=[]
	for id in s.done:
		if not id in ["new_threshold","nell_first_tray","clinic_release","old_threshold","quarry_later","groove_return"] or id in unique:return _bad()
		unique.append(id)
	if not s.done.is_empty() and r.step!=8:return _bad()
	if s.installed and not "new_threshold" in s.done:return _bad()
	if "clinic_release" in s.done and not s.installed:return _bad()
	if "old_threshold" in s.done and not "clinic_release" in s.done:return _bad()
	if s.bedded and not "old_threshold" in s.done:return _bad()
	if "quarry_later" in s.done and not s.bedded:return _bad()
	if "groove_return" in s.done and not "quarry_later" in s.done:return _bad()
	if "nell_first_tray" in s.done and not "new_threshold" in s.done:return _bad()
	for id in r.seen:
		if not id in Text.LINES and not id in Slice.SCENES:return _bad()
	if r.pending!="" and not r.pending in Text.LINES and not r.pending in Slice.SCENES:return _bad()
	if not r.parcel.is_empty():
		if r.parcel in Slice.JOBS:
			if not r.parcel in Slice.available(r) or r.checkpoint.is_empty():return _bad()
		else:
			if not r.parcel in Text.ORDER:return _bad()
			if r.step>=8 or Text.ORDER[int(r.step)]!=r.parcel or r.checkpoint.is_empty():return _bad()
	if r.pending in Slice.SCENES and (r.step!=8 or not r.parcel.is_empty()):return _bad()
	if r.pending=="relay" and (r.step!=2 or r.parcel!="relay_receiver"):return _bad()
	for id in {"ren_intro":1,"works":2,"quarry_offer":3,"depot":5,"clinic":6,"tess_final":7}:
		if r.pending==id and (r.step!={"ren_intro":1,"works":2,"quarry_offer":3,"depot":5,"clinic":6,"tess_final":7}[id] or r.parcel!=""):return _bad()
	if not r.checkpoint.is_empty():
		if r.checkpoint.size()!=6:return _bad()
		for key in ["x","y","z","yaw","condition","elapsed"]:
			if not (r.checkpoint.get(key) is float or r.checkpoint.get(key) is int) or not is_finite(float(r.checkpoint[key])):return _bad()
		if r.checkpoint.condition<0 or r.checkpoint.condition>1000 or r.checkpoint.elapsed<0:return _bad()
	return {"ok":true,"document":d}
func _bad() -> Dictionary:
	return {"ok":false,"status":"invalid_save","error":"Story save is invalid. Use Reset Story explicitly to start fresh."}
func _write_document(stock: bool,receiver: bool) -> Dictionary:
	if not _persistent_storage_available():return {"ok":false,"status":"storage_unavailable","error":"Persistent storage is unavailable."}
	var d:={"format":VERSION,"fabrication_stock":stock,"dispatch_receiver":receiver,"chapter":record.duplicate(true)}
	var encoded:=JSON.stringify(d);var temp:=_save_path+".tmp";var f:=FileAccess.open(temp,FileAccess.WRITE)
	if f==null:return {"ok":false,"status":"write_failed","error":"Cannot write chapter save."}
	f.store_string(encoded);f.flush();var error:=f.get_error();f.close()
	var checked:=_read_document(temp)
	if error!=OK or not checked.ok or checked.document!=JSON.parse_string(encoded):return {"ok":false,"status":"write_failed","error":"Chapter save verification failed; prior save is intact."}
	if DirAccess.rename_absolute(temp,_save_path)!=OK:return {"ok":false,"status":"write_failed","error":"Cannot replace chapter save; prior save is intact."}
	return {"ok":true}
