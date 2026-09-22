# One parcel, one observation layer

`district_zero_courier.tscn` composes the unchanged world with a priority-200
`CourierLayer`. `CraftController` remains the sole movement authority. Run v0
keeps its original scene and code. The only edited accepted product file is the
main-scene selection in `project.godot`; the other existing-file edit extends
the disposable Web export helper's diagnostic entry selection.

Market and Depot centers and inner radii come from
`P1AWorldData.manifest.destination_pads`. There are no route tests, checkpoints,
world triggers, added colliders or position-dependent handling effects.
Arrival requires the existing inner Depot pad, two support probes, a current
height within the existing support reacquisition distance, speed ≤6 m/s,
normal speed ≤0.75 m/s, no newly started Hop, no damage that tick, and 0.5 seconds
of continuous eligibility. The current transform/velocity are untouched when
Results opens or Continue is pressed. Continue updates only the future reset
anchor to the reached position.

`courier_rules.gd` holds the small slice's parameters. `cargo_observer.gd` reads
the fresh impact counter and the just-completed native slide contacts. It does
not reconstruct collision response or infer impacts from deceleration/slip.
Because the controller exposes its strongest severity without the winning
contact index, attribution is permitted only when **every** slide contact is a
named, non-terrain obstacle with |normal.y| ≤0.5. Terrain, support-facing and
mixed ambiguous contacts are forgiven. This intentionally misses some genuine
mixed/angled impacts rather than penalizing a landing incorrectly.

Condition starts at 1,000 units (100.0%). Quantize severity to 0.001, ignore the
first 0.20, then round `240 × ((severity − .20) / .80)^1.5` to units. An episode
charges only increases in its maximum severity. Continuing obstacle contact
keeps it open, even without new strong samples. More than .25 active seconds
without wall contact closes it. No elapsed-time or frame-count pressure tax.
Clamp condition at zero; never fail delivery because of condition.

The elapsed clock and cargo reducer advance only on active unpaused physics
ticks. BRRR calls the existing `run/brrr_seed.gd` unchanged. No condition value
enters BRRR, no BRRR value enters condition, and neither feeds an economy.
Terminal evidence is a read-only dictionary. Reset-epoch and counter
discontinuities stop the parcel attempt rather than fabricating impact evidence.

Dispatch, Results and pause use SceneTree pause. Input ownership clears pending
Hop through the existing public method and waits for neutral controls on exit;
the controller and weather implementations remain byte-identical. Manual/fall/
diagnostic resets cancel the parcel once, using the reset that already occurred.
No second reset or success teleport is issued.

Native and Web diagnostic placement tests are explicitly synthetic. The same
integration lane also drives one complete Market–Depot shortcut using only
ordinary input actions after acceptance. The driver belongs only to tests;
the shipped courier layer never steers, throttles or brakes.
