extends SceneTree
const Store=preload("res://scripts/courier/narrative_store.gd")
var checks: Dictionary={}
func _initialize() -> void:call_deferred("run")
func run() -> void:
	var args:=OS.get_cmdline_user_args();var path: String=args[args.find("--save")+1]
	var s:=Store.new(path)
	checks.fresh=s.load_state().ok and s.stage()==0
	s.record.seen.append("market")
	checks.seen_persists=s.commit()
	var reopened:=Store.new(path);checks.seen_reopens=reopened.load_state().ok and "market" in reopened.record.seen
	s.record.pending="works";var result: Dictionary=s.contribute("relay_stock")
	checks.stock_atomic=result.ok and result.changed and s.stage()==1
	reopened=Store.new(path);checks.works_reopens=reopened.load_state().ok and reopened.record.pending=="works" and reopened.stage()==1
	s.record.pending="";s.record.parcel="relay_receiver";s.record.checkpoint={"x":90.123456789,"y":2.2,"z":-55.0,"yaw":.23,"condition":537,"elapsed":18.6666666666667}
	checks.aboard_commit=s.commit();reopened=Store.new(path)
	checks.aboard_reopens=reopened.load_state().ok and reopened.record.parcel=="relay_receiver" and reopened.record.checkpoint.condition==537
	var before:=FileAccess.get_file_as_bytes(path)
	s.record.pending="nonsense";checks.invalid_write_rejected=not s.commit()
	checks.failed_write_preserves_bytes=before==FileAccess.get_file_as_bytes(path)
	s.record.pending="";s.record.parcel="";s.record.checkpoint={}
	checks.receiver=s.contribute("relay_receiver").changed and s.outbound_available()
	s.record.quarry_done=true;s.record.seen.append("relay");checks.done_commit=s.commit()
	checks.reset=s.reset_project().ok and s.record.seen.is_empty() and s.record.parcel.is_empty() and not s.record.quarry_done and s.stage()==0
	var f:=FileAccess.open(path,FileAccess.WRITE);f.store_string("bad data");f.close()
	reopened=Store.new(path);checks.corruption_visible=not reopened.load_state().ok
	checks.corruption_blocks_contribution=not reopened.contribute("relay_stock").ok
	checks.explicit_reset_recovers=reopened.reset_project().ok
	var bad:=Store.new(path+"/no-parent/save.json");bad.load_state()
	checks.io_failure=not bad.contribute("relay_stock").ok and bad.stage()==0
	var report:={"status":"PASS" if not checks.values().has(false) else "FAIL","checks":checks}
	FileAccess.open(args[args.find("--result")+1],FileAccess.WRITE).store_string(JSON.stringify(report,"  "))
	print("NARRATIVE_STORE_RESULT "+JSON.stringify(report));quit(0 if report.status=="PASS" else 1)
