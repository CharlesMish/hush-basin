# Reproducing V1.1 checks

Use the exact installed Godot `4.7.1.stable.official.a13da4feb` and the accepted
single-thread Web template. No installation or dependency change is required.
Run from this source root. Replace ENGINE, SOURCE and OUT with absolute paths;
OUT must be outside `game/`. Always supply an absolute Godot log path. Inspect
both logs and JSON: Godot can return zero even after a script parse failure.

```sh
python3 tools/launch.py --verify-engine
python3 tools/launch.py --prepare-only
python3 tools/verify_range_v11.py
```

The 612-file V1 inventory explicitly permits only six bound existing-file edits.
It leaves historical inventories intact. Old three-job assertions are historical;
`range_v11_probe.gd` supplies successor expectations for the five-job loop.

```sh
ENGINE --headless --path SOURCE/game --log-file OUT/predicates.log --script res://tests/range_v11_predicates.gd -- --result OUT/predicates.json
ENGINE --headless --fixed-fps 60 --path SOURCE/game --log-file OUT/c1.log --script res://tests/mechanics_c1.gd -- --output OUT/c1.jsonl
ENGINE --path SOURCE/game --fixed-fps 60 --log-file OUT/native.log --script res://tests/range_v11_native.gd -- --result OUT/native.json --captures OUT/views --cargo-log OUT/cargo.jsonl
ENGINE --headless --fixed-fps 60 --path SOURCE/game --log-file OUT/calibration.log --script res://tests/range_v11_calibration.gd -- --plans SOURCE/docs/range_v11_final_calibration_plans.json --output OUT/calibration --geometry
```

Compare all 1,260 C1 JSONL rows with accepted V1, including a second run with
`--protected`. Separate existing scripts cover `alpha_cargo_matrix.gd` (both
protection states), `quarto_vehicle_v1.gd`, `run_v0_probe.gd`,
`paused_retry_addendum.gd`, `world_polish_runtime.gd` and
`quiet_surface_weather.gd`. Each takes `--result` after the engine's `--`.

```sh
python3 tools/export_web.py --output OUT/web-full
python3 tools/export_web.py --range-v11-smoke --output OUT/web-five-job
python3 tools/export_web.py --smoke --output OUT/web-run
```

Serve locally over HTTP and open each `web/index.html`. The full artifact is
playable. The other two are diagnostics, never owner/deployment artifacts.
The five-job diagnostic emits `RANGE_V11_SMOKE_RESULT`; allow up to 15 minutes
for the full sequence. The Run diagnostic emits `WEB_SMOKE_RESULT`. Runtime
success requires a PASS result and no script, shader, browser or loading errors.
Do not conflate successful export with browser execution.

Normal-input fixtures and initial-condition declarations are retained in source.
Exploratory plans are intentionally preserved; final plans and matrices live in
`docs/range_v11_*`. Synthetic receipt/reset/contact assertions are separately
labelled in the native/Web probe. Owner comfort, gamepad feel and balance cannot
be certified by these automated runs.

Raw commands, engine/browser logs, clips, per-frame performance samples and
development failures are in the adjacent delivery evidence directory, outside
the source ZIP. They are not runtime assets. No command here deploys or pushes.
