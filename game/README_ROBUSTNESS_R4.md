# District Zero P1A v1.2.8 — robustness R4

This successor retains the complete Visibility R3 project and its readable,
two-sided collidable solids. It makes one behavior-neutral robustness repair:
ordinary play no longer serializes every telemetry event into Godot's editor
console. Runtime vectors still opt into the exact JSONL stream they require;
human capture/replay still records the same structured telemetry through the
existing event signal.

For owner review on macOS, use the sibling
`District-Zero-P1A-v1.2.8-Robustness-R4-Play-Project` and double-click its
`PLAY_DISTRICT_ZERO_R4.command`. It requires the existing exact Godot
`4.7.1.stable.official.a13da4feb` at `/opt/homebrew/bin/godot` and launches the
project as a standalone game process, avoiding the editor's embedded-game host.

The complete source intentionally retains a frozen `.gd` builder fixture needed
by verification. Because that fixture shares the production builder's global
class name, it is not a runnable editor project; the established harness rule
excludes it from every runnable copy. The R4 player project applies exactly that
rule and is the folder intended for Play.

This is not P1A PASS or Human World Gate authorization. The visible in-game
identity remains `v1.2.8 VISIBILITY R3 · WORLD v1.2.3` because presentation and
the frozen runtime-vector identity gate are unchanged; the containing folder,
this document, and the launcher identify the R4 robustness successor.
