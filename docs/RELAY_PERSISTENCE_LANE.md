# Relay Annex v0.1 — finite persistence lane

Isolated baseline: `66b4c228264d6c2966a8af68243898fc21c6573d`, the delivered
Mastery Alpha v1 source. Branch: `lane/relay-persistence-v01`. This lane changes
no existing file. The September 20 owner commission expressly authorizes the
two-need Relay experiment and its minimum local persistence; the historical
no-save boundaries remain truthful for their older builds.

## API and state

Preload `res://scripts/courier/relay_project.gd`, instantiate with an optional
test path, and call `load_state()` before using `contribute(job_id, delivered)`.
The default path is `user://relay_annex_project_v01.json`.

- `relay_stock` contributes `fabrication_stock`.
- `relay_receiver` contributes `dispatch_receiver`, only after stock.
- Every other job is unrelated. A canceled delivery contributes nothing.
- Repeated completed needs return `already_complete` and do not write or
  downgrade the project. The receipt/payment system remains independent.
- `stage()` derives 0/1/2. `outbound_available()` derives only from the second
  need. Neither derivative is separately stored.
- `snapshot()` returns a detached dictionary of both flags, stage, outbound
  availability and load status. Render and Dispatch should both use this state.
- `reset_project()` explicitly writes a fresh state, including after a corrupt
  save. It does not reset money, cargo, mastery or movement.

Operations return `{ok, status, changed, need, stage, outbound_available, error}`.
I/O failures return `ok=false`, preserve the previous committed memory and
document, and expose `last_error`. A bad load blocks further contribution until
successful reload or deliberate reset. The caller must show a save error rather
than claim that a contribution was remembered. Valid delivery is established by
the existing courier layer before calling this store; the store deliberately
never reads cargo, optional objectives, mastery, time, score or vehicle data.

The on-disk document has exactly a fixed format string and two booleans. There
are no Credits, timestamps, generic project registry, migrations, account IDs,
profiles, slots or telemetry. Wrong types, extra fields, unknown format,
out-of-order flags, invalid JSON and files over 1 KiB are rejected. A missing
file is fresh; a directory at the save path is an error. Corrupt data is never
silently overwritten by a delivery.

Writes use a same-directory `.tmp`, flush/close, validated readback and rename
over the old complete file. The old file is never deleted first. Memory advances
only after successful replacement. A leftover temporary file is not treated as
a completed need. This is one local application store, not concurrent-writer or
power-loss transaction infrastructure.

## Observed verification

Exact installed engine: `4.7.1.stable.official.a13da4feb`.

```sh
python3 tools/test_relay_persistence.py --output NEW_EMPTY_EVIDENCE_DIRECTORY
```

Result: **56/56 checks, nine distinct real Godot processes**. The sequence is
fresh → stock → process exit/reopen → stage 1 with no outbound → receiver →
exit/reopen → stage 2 with outbound → replay → reset → exit/reopen → fresh.
Additional checks cover both failed writes and failed rename, a failed reset,
strict corruption rejection and explicit recovery, ordering, canceling,
unrelated freight, replay idempotence and detached snapshots. The runner retains
every command, engine/console log and per-process result. The lane's initial
evidence is in the sibling `persistence-evidence-01` directory.
The subsequent UID/import preparation had no script/parse errors, but sandbox
access prevented saving the host's editor settings; the usual host CA-certificate
warning was also present. Neither error changed the tested save path or source.

These are state/store checks. Integration must separately show that restored
stage 1/2 actually reconstruct the matching world meshes and usable Relay board.
It must also prove valid zero-condition delivery contributes through the actual
courier receipt path.

## Web boundary

The same native `FileAccess`/`DirAccess` APIs serve Web `user://`. No JavaScript
save adapter, library or external service is added. The class reports an explicit
failure when the Web engine says persistent user storage is unavailable.

Godot documents that Web persistence depends on IndexedDB and that
`OS.is_userfs_persistent()` can give false positives. Its Web engine marks closed
writable user files dirty and initiates synchronization on a following main-loop
iteration. Therefore the synchronous operation result proves a committed Godot
filesystem document, not completion of browser backing-store synchronization.
The integrated browser lane must allow ordinary frames and then close/reopen or
reload the same origin to demonstrate durability; it must not equate an in-memory
readback with that proof. Clearing site data removes the experiment.

Primary references inspected for this narrow behavior:
[Godot Web persistence documentation](https://docs.godotengine.org/en/4.5/tutorials/export/exporting_for_web.html#using-cookies-for-data-persistence)
and [Godot Web file-close/main-loop synchronization source](https://github.com/godotengine/godot/blob/master/platform/web/os_web.cpp).
The source reference supports the API reasoning; the installed/exported engine
still requires direct native/browser verification.
