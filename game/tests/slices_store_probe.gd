extends SceneTree
const Store=preload("res://scripts/courier/slices_store.gd")
const Text=preload("res://scripts/courier/chapter_text.gd")
func _initialize() -> void:call_deferred("run")
func run() -> void:
	var args:=OS.get_cmdline_user_args();var path:=args[args.find("--save")+1];var checks: Dictionary={}
	var store=Store.new(path);checks.fresh=store.load_state().ok;checks.reset=store.reset_project().ok
	for i in 8:
		if i==7:
			store.record.patch=true;checks.patch_commit=store.commit();checks.other_job=store.contribute("mending_pickup",true).ok
		checks["leg_"+str(i)]=store.contribute(Text.ORDER[i],true).ok and store.record.step==i+1
		var reopen=Store.new(path);checks["reopen_"+str(i)]=reopen.load_state().ok and reopen.record==JSON.parse_string(JSON.stringify(store.record))
	checks.one_other_job_gates=store.record.after_arc1 and store.record.after_arc2
	var bytes:=FileAccess.get_file_as_bytes(path);var step: int=store.record.step
	checks.cancel_keeps_step=store.contribute("local_MRK",false).ok and store.record.step==step
	store.record.step=999;checks.invalid_write_preserves=not store.commit() and FileAccess.get_file_as_bytes(path)==bytes
	store.record.step=step
	var bad=Store.new(path+".bad");FileAccess.open(path+".bad",FileAccess.WRITE).store_string("not JSON")
	checks.corrupt_visible=not bad.load_state().ok;checks.corrupt_blocks_contribution=not bad.contribute("relay_mail").ok;checks.explicit_reset_recovers=bad.reset_project().ok and bad.load_state().ok
	checks.full_reset=store.reset_project().ok and store.record==Store.fresh_record()
	store.record.parcel="relay_mail";store.record.checkpoint={"x":0.0,"y":1.3,"z":20.0,"yaw":0.234,"condition":672,"elapsed":135.123}
	checks.checkpoint_roundtrip=store.commit();var again=Store.new(path);checks.parcel_roundtrip=again.load_state().ok and again.record.parcel=="relay_mail" and again.record.checkpoint.condition==672
	store.record.checkpoint.condition=-1;checks.bad_condition_rejected=not store.commit()
	store.reset_project();store.record.step=8;store.record.patch=true;store.record.after_arc1=true;store.record.after_arc2=true
	store.record.slices.done=["new_threshold","nell_first_tray","clinic_release","old_threshold","quarry_later"]
	store.record.slices.installed=true;store.record.slices.bedded=true;checks.chapter_two_fixture=store.commit()
	bytes=FileAccess.get_file_as_bytes(path)
	for id in ["tray_two","ren_answer","thread_box","tagged_mending","ren_letter","kneeling_pads","relined_sleeve","red_return"]:
		store.record.slices.done.append(id)
		checks["reject_out_of_order_"+id]=not store.commit() and FileAccess.get_file_as_bytes(path)==bytes
		store.record.slices.done.erase(id)
	store.record.slices.relined=true;checks.reject_unearned_reline=not store.commit();store.record.slices.relined=false
	store.record.slices.shelf_label=true;checks.reject_unearned_label=not store.commit();store.record.slices.shelf_label=false
	store.record.pending="ren_letter";checks.reject_unearned_arrival=not store.commit();store.record.pending=""
	var old_doc: Dictionary=JSON.parse_string(FileAccess.get_file_as_string(path));old_doc.chapter.slices.erase("relined");old_doc.chapter.slices.erase("shelf_label")
	FileAccess.open(path+".checkpoint_a",FileAccess.WRITE).store_string(JSON.stringify(old_doc))
	var migrated=Store.new(path+".checkpoint_a");checks.checkpoint_a_migration=migrated.load_state().ok and migrated.record.slices.size()==5 and not migrated.record.slices.relined
	checks.migrated_can_commit=migrated.commit()
	store.reset_project();checks.future_flags_reset=store.record.slices.done.is_empty() and not store.record.slices.relined and not store.record.slices.shelf_label
	var result:={"status":"FAIL" if checks.values().has(false) else "PASS","checks":checks}
	FileAccess.open(args[args.find("--result")+1],FileAccess.WRITE).store_string(JSON.stringify(result,"  "));quit(1 if checks.values().has(false) else 0)
