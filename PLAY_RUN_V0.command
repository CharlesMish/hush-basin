#!/bin/zsh
set -u

launcher_root="${0:A:h}"
project_root="$launcher_root/game"
godot_binary="/opt/homebrew/bin/godot"
required_version="4.7.1.stable.official.a13da4feb"
run_scene="res://scenes/district_zero_run.tscn"

if [[ ! -f "$project_root/project.godot" ]] || [[ ! -f "$project_root/scenes/district_zero_run.tscn" ]]; then
	print -u2 "District Zero Run v0 was not found beneath:"
	print -u2 "$launcher_root"
	print -u2 "Keep this launcher at the repository root."
	read -r "?Press Return to close."
	exit 2
fi

if [[ ! -x "$godot_binary" ]]; then
	print -u2 "District Zero Run v0 could not find executable Godot at $godot_binary"
	read -r "?Press Return to close."
	exit 2
fi

observed_version="$($godot_binary --version 2>/dev/null)"
if [[ "$observed_version" != "$required_version" ]]; then
	print -u2 "District Zero Run v0 requires $required_version"
	print -u2 "Observed: $observed_version"
	read -r "?Press Return to close."
	exit 2
fi

log_path="${TMPDIR:-/tmp}/district-zero-run-v0.log"
import_log_path="${TMPDIR:-/tmp}/district-zero-run-v0-import.log"
parse_log_path="${TMPDIR:-/tmp}/district-zero-run-v0-parse.log"
class_cache="$project_root/.godot/global_script_class_cache.cfg"
lock_dir="${TMPDIR:-/tmp}/district-zero-p1a-vehicle-r7.lock"
pid_path="$lock_dir/launcher.pid"

cache_ready=false
if [[ -s "$class_cache" ]] && grep -Fq '"VehicleVisualRig"' "$class_cache"; then
	cache_ready=true
fi
if [[ "$cache_ready" != true ]]; then
	print "Preparing District Zero for its first Run v0 launch..."
	"$godot_binary" --headless --editor --path "$project_root" --import --quit --log-file "$import_log_path"
	import_status=$?
	if (( import_status != 0 )) || [[ ! -s "$class_cache" ]] || ! grep -Fq '"VehicleVisualRig"' "$class_cache"; then
		print -u2 "District Zero Run v0 could not prepare its Godot script cache."
		print -u2 "Import log: $import_log_path"
		read -r "?Press Return to close."
		exit 2
	fi
fi

# Always parse-check this overlay even when the inherited R7 cache was ready.
"$godot_binary" --headless --editor --path "$project_root" --quit-after 2 --log-file "$parse_log_path"
parse_status=$?
if (( parse_status != 0 )) || grep -Eq 'SCRIPT ERROR:|Parse Error:|Failed to load script|Could not resolve class|Cannot get class' "$parse_log_path"; then
	print -u2 "District Zero Run v0 did not pass its exact-engine script check."
	print -u2 "Parse log: $parse_log_path"
	read -r "?Press Return to close."
	exit 2
fi

if ! mkdir "$lock_dir" 2>/dev/null; then
	prior_pid=""
	if [[ -r "$pid_path" ]]; then
		prior_pid="$(<"$pid_path")"
	fi
	if [[ "$prior_pid" == <-> ]] && kill -0 "$prior_pid" 2>/dev/null; then
		print -u2 "District Zero is already running (launcher PID $prior_pid)."
		print -u2 "Close that game window before starting Run v0."
		read -r "?Press Return to close."
		exit 2
	fi
	rm -f "$pid_path"
	rmdir "$lock_dir" 2>/dev/null || true
	if ! mkdir "$lock_dir" 2>/dev/null; then
		print -u2 "District Zero Run v0 could not acquire its launch lock."
		read -r "?Press Return to close."
		exit 2
	fi
fi

print -r -- "$$" > "$pid_path"
cleanup_lock() {
	rm -f "$pid_path"
	rmdir "$lock_dir" 2>/dev/null || true
}
trap cleanup_lock EXIT INT TERM

godot_args=(--path "$project_root" --log-file "$log_path")
if [[ "${DISTRICT_ZERO_RUN_V0_SMOKE_FRAMES:-}" == <-> ]]; then
	godot_args+=(--headless --quit-after "$DISTRICT_ZERO_RUN_V0_SMOKE_FRAMES")
fi
godot_args+=("$run_scene")
"$godot_binary" "${godot_args[@]}" &
game_pid=$!
wait "$game_pid"
exit $?
