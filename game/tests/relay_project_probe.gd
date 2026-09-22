extends SceneTree
const Project = preload("res://scripts/courier/relay_project.gd")
var checks: Dictionary = {}

func _initialize() -> void:
	call_deferred("run")

func option(name: String, fallback: String = "") -> String:
	var args := OS.get_cmdline_user_args()
	return args[args.find(name) + 1] if args.has(name) else fallback

func write_text(path: String, contents: String) -> void:
	var file := FileAccess.open(path, FileAccess.WRITE)
	file.store_string(contents)
	file.close()

func run() -> void:
	var path := option("--save")
	if path.is_empty():
		push_error("Use an explicit disposable --save path.")
		quit(2)
		return
	var project := Project.new(path)
	var loaded := project.load_state()
	var action := option("--operation", "inspect")
	var event: Dictionary = {}
	match action:
		"stock": event = project.contribute(Project.STOCK_JOB)
		"receiver": event = project.contribute(Project.RECEIVER_JOB)
		"reset": event = project.reset_project()
		"unit": unit_checks(path)
	var passed := true
	for value in checks.values(): passed = passed and value
	var result := {"status": "PASS" if passed else "FAIL", "operation": action,
		"load": loaded, "event": event, "state": project.snapshot(),
		"checks": checks, "count": checks.size(), "engine": Engine.get_version_info().string,
		"pid": OS.get_process_id(), "persistent_userfs": OS.is_userfs_persistent()}
	var output := option("--result")
	if not output.is_empty(): write_text(output, JSON.stringify(result, "  "))
	print("RELAY_PROJECT_RESULT " + JSON.stringify(result))
	quit(0 if passed else 1)

func unit_checks(path: String) -> void:
	var project := Project.new(path)
	checks["cannot_overwrite_without_load"] = project.contribute(Project.STOCK_JOB).status == "not_loaded"
	checks["explicit_reset_bootstraps"] = project.reset_project().ok and project.stage() == 0
	checks["fresh_derived_state"] = project.snapshot() == {"fabrication_stock": false, "dispatch_receiver": false, "stage": 0, "outbound_available": false, "loaded": true}
	checks["receiver_cannot_precede_stock"] = project.contribute(Project.RECEIVER_JOB).status == "prerequisite_missing" and project.stage() == 0
	checks["unrelated_freight_not_a_substitute"] = project.contribute("works_instruments").status == "unrelated" and project.stage() == 0
	checks["cancelled_leg_never_contributes"] = project.contribute(Project.STOCK_JOB, false).status == "not_delivered" and project.stage() == 0
	var first := project.contribute(Project.STOCK_JOB)
	checks["valid_stock_awards_named_need"] = first.ok and first.changed and first.need == "fabrication_stock" and first.stage == 1
	checks["stock_does_not_open_outbound"] = not project.outbound_available()
	var disk_before := FileAccess.get_file_as_string(path)
	checks["save_only_format_and_two_flags"] = JSON.parse_string(disk_before) == {"format": Project.FORMAT, "fabrication_stock": true, "dispatch_receiver": false}
	checks["stock_replay_idempotent"] = project.contribute(Project.STOCK_JOB).status == "already_complete" and FileAccess.get_file_as_string(path) == disk_before
	var detached := project.snapshot()
	detached.fabrication_stock = false
	detached.dispatch_receiver = true
	checks["snapshot_cannot_mutate_project"] = project.stage() == 1 and not project.outbound_available()
	DirAccess.make_dir_absolute(path + ".tmp")
	var blocked := project.contribute(Project.RECEIVER_JOB)
	checks["write_failure_reported"] = not blocked.ok and blocked.status == "write_failed" and not project.last_error.is_empty()
	checks["write_failure_keeps_memory_and_previous_file"] = project.stage() == 1 and FileAccess.get_file_as_string(path) == disk_before
	var reset_blocked := project.reset_project()
	checks["failed_reset_keeps_memory_and_previous_file"] = not reset_blocked.ok and project.stage() == 1 and FileAccess.get_file_as_string(path) == disk_before
	DirAccess.remove_absolute(path + ".tmp")
	var second := project.contribute(Project.RECEIVER_JOB)
	checks["valid_receiver_opens_annex"] = second.ok and second.changed and second.need == "dispatch_receiver" and project.stage() == 2 and project.outbound_available()
	checks["successful_retry_clears_io_error"] = project.last_error.is_empty()
	checks["receiver_replay_idempotent"] = not project.contribute(Project.RECEIVER_JOB).changed and project.stage() == 2
	checks["stock_replay_never_downgrades_final"] = not project.contribute(Project.STOCK_JOB).changed and project.stage() == 2
	checks["temporary_file_gone_after_commit"] = not FileAccess.file_exists(path + ".tmp")
	var restored := Project.new(path)
	checks["new_object_reproduces_flags_and_derived_world_stage"] = restored.load_state().ok and restored.snapshot() == project.snapshot()

	var valid_document := FileAccess.get_file_as_string(path)
	var invalid_documents := ["", "{", "[]", "null", "{}",
		JSON.stringify({"format": Project.FORMAT, "fabrication_stock": 1, "dispatch_receiver": false}),
		JSON.stringify({"format": Project.FORMAT, "fabrication_stock": false, "dispatch_receiver": true}),
		JSON.stringify({"format": "future-or-unrelated", "fabrication_stock": true, "dispatch_receiver": true}),
		JSON.stringify({"format": Project.FORMAT, "fabrication_stock": true, "dispatch_receiver": false, "credits": 9999}),
		"x".repeat(Project.MAX_SAVE_BYTES + 1)]
	for index in invalid_documents.size():
		write_text(path, invalid_documents[index])
		var rejected := project.load_state()
		checks["invalid_document_%02d_rejected_without_erasing_memory" % index] = not rejected.ok and rejected.status == "invalid_save" and project.stage() == 2
		checks["invalid_document_%02d_not_silently_replaced" % index] = project.contribute(Project.STOCK_JOB).status == "not_loaded" and FileAccess.get_file_as_string(path) == invalid_documents[index]
	write_text(path, valid_document)
	checks["valid_document_can_reload_after_failure"] = project.load_state().ok and project.stage() == 2
	write_text(path, "broken")
	project.load_state()
	checks["explicit_reset_repairs_bad_document"] = project.reset_project().ok and project.stage() == 0
	var reset_restored := Project.new(path)
	checks["reset_persists_instead_of_only_clearing_memory"] = reset_restored.load_state().ok and reset_restored.stage() == 0

	var rename_path := path + ".directory-target"
	var rename_project := Project.new(rename_path)
	checks["rename_fixture_fresh"] = rename_project.load_state().ok
	DirAccess.make_dir_absolute(rename_path)
	var rename_failed := rename_project.contribute(Project.STOCK_JOB)
	checks["rename_failure_does_not_commit_memory"] = not rename_failed.ok and rename_failed.status == "write_failed" and rename_project.stage() == 0
	checks["directory_cannot_masquerade_as_missing_save"] = not rename_project.load_state().ok
	checks["failed_replacement_cleans_temporary_file"] = not FileAccess.file_exists(rename_path + ".tmp")
	DirAccess.remove_absolute(rename_path)
