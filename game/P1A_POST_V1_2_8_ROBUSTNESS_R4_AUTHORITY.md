# District Zero P1A — post-v1.2.8 robustness repair R4

## Trigger

During owner free-roam review on macOS, the Godot editor crashed while its
embedded game child remained alive. The surviving child continued emitting a
full `COLLISION_SAMPLE` JSON record on every physics tick during sustained
`CORE_WALL` contact. This produced hundreds of megabytes of logs and continuous
remote-debug output pressure. No gameplay-script, physics, parse, or renderer
failure preceded the editor crash.

## Narrow R4 authority

R4 may only:

1. preserve every telemetry event, serial, physics tick, bounded queue entry,
   dropped count, and `event_emitted` signal while making JSONL console
   serialization opt-in;
2. enable that serialization for the authoritative runtime-vector harness,
   whose evidence parser consumes stdout, and for the explicit
   `--p1a-telemetry-jsonl` diagnostic argument;
3. keep console serialization disabled during ordinary free-roam and human
   capture/replay, which consume telemetry through the existing signal and
   structured artifact writer; and
4. add a one-click standalone launcher that verifies the exact installed engine
   and runs the project outside Godot's embedded game view.

The crash evidence supports an editor/embedded-game fault and a project-side
output-pressure amplifier. It does not prove that telemetry caused the engine
fault. This repair therefore claims reduced trigger surface and bounded normal
play output, not a guaranteed engine-crash cure.

## Frozen without exception

Movement, tuning, input, craft and world collision, support, terrain, geometry,
materials, culling, camera, lighting, shadows, routes, nodes, spawns, HOP,
gameplay thresholds, runtime-vector telemetry semantics, capture/replay
artifacts, visual checks, ray checks, Human World Gate, and P1B remain frozen.
R3 wall visibility remains unchanged.
