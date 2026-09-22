extends RefCounted
## One finite project, independent of money, mastery, cargo and craft telemetry.
## Call load_state() before contribution. Only reset_project() may replace a bad save.

const SAVE_PATH := "user://relay_annex_project_v01.json"
const FORMAT := "hush-basin-relay-annex-v0.1"
const STOCK_JOB := "relay_stock"
const RECEIVER_JOB := "relay_receiver"
const MAX_SAVE_BYTES := 1024

var _save_path: String
var _fabrication_stock := false
var _dispatch_receiver := false
var _loaded := false
var last_error := ""

func _init(save_path: String = SAVE_PATH) -> void:
	_save_path = save_path

func stage() -> int:
	return 2 if _dispatch_receiver else (1 if _fabrication_stock else 0)

func outbound_available() -> bool:
	return _dispatch_receiver

func snapshot() -> Dictionary:
	return {"fabrication_stock": _fabrication_stock, "dispatch_receiver": _dispatch_receiver,
		"stage": stage(), "outbound_available": outbound_available(), "loaded": _loaded}

func load_state() -> Dictionary:
	_loaded = false
	if not _persistent_storage_available():
		return _failure("storage_unavailable", "Browser storage is unavailable; Relay progress cannot be remembered.")
	if DirAccess.dir_exists_absolute(_save_path):
		return _failure("read_failed", "Relay save path is a directory.")
	if not FileAccess.file_exists(_save_path):
		_fabrication_stock = false
		_dispatch_receiver = false
		_loaded = true
		return _result("fresh")
	var read := _read_document(_save_path)
	if not read.ok:
		return _failure(read.status, read.error)
	_fabrication_stock = read.document.fabrication_stock
	_dispatch_receiver = read.document.dispatch_receiver
	_loaded = true
	return _result("loaded")

func contribute(job_id: String, delivered: bool = true) -> Dictionary:
	if not _loaded:
		return _failure("not_loaded", "Relay progress must load successfully or be explicitly reset before contribution.")
	if not delivered:
		return _result("not_delivered")
	if job_id != STOCK_JOB and job_id != RECEIVER_JOB:
		return _result("unrelated")
	var need := "fabrication_stock" if job_id == STOCK_JOB else "dispatch_receiver"
	if (job_id == STOCK_JOB and _fabrication_stock) or (job_id == RECEIVER_JOB and _dispatch_receiver):
		return _result("already_complete", false, need)
	if job_id == RECEIVER_JOB and not _fabrication_stock:
		return _result("prerequisite_missing", false, need)
	var write := _write_document(true, job_id == RECEIVER_JOB)
	if not write.ok:
		return _failure(write.status, write.error, need)
	_fabrication_stock = true
	_dispatch_receiver = job_id == RECEIVER_JOB
	return _result("contributed", true, need)

func reset_project() -> Dictionary:
	var write := _write_document(false, false)
	if not write.ok:
		return _failure(write.status, write.error)
	var changed := stage() != 0
	_fabrication_stock = false
	_dispatch_receiver = false
	_loaded = true
	return _result("reset", changed)

func _persistent_storage_available() -> bool:
	return not OS.has_feature("web") or OS.is_userfs_persistent()

func _read_document(path: String) -> Dictionary:
	var file := FileAccess.open(path, FileAccess.READ)
	if file == null:
		return {"ok": false, "status": "read_failed", "error": "Cannot read Relay save (%s)." % error_string(FileAccess.get_open_error())}
	if file.get_length() <= 0 or file.get_length() > MAX_SAVE_BYTES:
		file.close()
		return {"ok": false, "status": "invalid_save", "error": "Relay save is empty or exceeds its small fixed format."}
	var contents := file.get_as_text()
	var read_error := file.get_error()
	file.close()
	if read_error != OK and read_error != ERR_FILE_EOF:
		return {"ok": false, "status": "read_failed", "error": "Cannot finish reading Relay save (%s)." % error_string(read_error)}
	var parser := JSON.new()
	if parser.parse(contents) != OK:
		return {"ok": false, "status": "invalid_save", "error": "Relay save is not valid JSON."}
	var value: Variant = parser.data
	if not value is Dictionary or value.size() != 3 or value.get("format") != FORMAT or typeof(value.get("fabrication_stock")) != TYPE_BOOL or typeof(value.get("dispatch_receiver")) != TYPE_BOOL:
		return {"ok": false, "status": "invalid_save", "error": "Relay save does not match this experiment's two-need format."}
	if value.dispatch_receiver and not value.fabrication_stock:
		return {"ok": false, "status": "invalid_save", "error": "Relay receiver cannot precede its fabrication stock."}
	return {"ok": true, "document": value}

func _write_document(stock: bool, receiver: bool) -> Dictionary:
	if not _persistent_storage_available():
		return {"ok": false, "status": "storage_unavailable", "error": "Browser storage is unavailable; Relay progress cannot be remembered."}
	var document := {"format": FORMAT, "fabrication_stock": stock, "dispatch_receiver": receiver}
	var temporary := _save_path + ".tmp"
	var file := FileAccess.open(temporary, FileAccess.WRITE)
	if file == null:
		return {"ok": false, "status": "write_failed", "error": "Cannot prepare Relay save (%s)." % error_string(FileAccess.get_open_error())}
	file.store_string(JSON.stringify(document, "\t", true) + "\n")
	file.flush()
	var write_error := file.get_error()
	file.close()
	if write_error != OK:
		DirAccess.remove_absolute(temporary)
		return {"ok": false, "status": "write_failed", "error": "Cannot finish Relay save (%s)." % error_string(write_error)}
	var verified := _read_document(temporary)
	if not verified.ok or verified.document != document:
		DirAccess.remove_absolute(temporary)
		return {"ok": false, "status": "write_failed", "error": "Relay save verification failed; previous project state remains intact."}
	# Same-directory replacement never deletes the previous complete document first.
	var replace_error := DirAccess.rename_absolute(temporary, _save_path)
	if replace_error != OK:
		DirAccess.remove_absolute(temporary)
		return {"ok": false, "status": "write_failed", "error": "Cannot replace Relay save (%s)." % error_string(replace_error)}
	return {"ok": true}

func _result(status: String, changed: bool = false, need: String = "") -> Dictionary:
	last_error = ""
	return {"ok": true, "status": status, "changed": changed, "need": need,
		"stage": stage(), "outbound_available": outbound_available(), "error": ""}

func _failure(status: String, message: String, need: String = "") -> Dictionary:
	last_error = message
	return {"ok": false, "status": status, "changed": false, "need": need,
		"stage": stage(), "outbound_available": outbound_available(), "error": message}
