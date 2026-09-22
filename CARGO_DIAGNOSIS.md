# Cargo diagnosis before calibration

Accepted v1 source: 90d2c3ee7e3286dc82001daf7be4149f158387f8. No controller,
motion-math, tuning or collision-response change is authorized or made.

The original curve is deterministic and nondecreasing over all 1,001 quantized
severity values. Same-wall/same-angle physical cases also preserve ordering.
The controller derives severity from normal-closing speed and opposition to the
contact normal. A 12 m/s 60° glance therefore costs about 2.1–2.3%, whereas a
6 m/s head-on contact costs about 7.9–8.1%. World speed alone cannot rank these.
Head-on severity saturates at 9.5 m/s; full cargo loss is 24% per episode.

Fresh-counter observations contain same-frame, directly captured pre-move
velocity. Stale telemetry after a strike produces no new charge. The review
hook captures the existing impact method's argument and immediately delegates
to the unchanged superclass. Its 1,260-tick movement trace equals the accepted
trace exactly. The script-owned velocity, collision-resolved displacement and
post-response speed are recorded separately; none is silently substituted for
another.

Two actual v1 attribution problems were reproduced before calibration:

1. Starting only 5 cm clear of the wall, from rest with held throttle, Spread
   accumulated 1.4% damage across rising severity peaks. This was one contact
   episode, not repeated separated arrivals. The first charged event appeared
   at tick 13 and the last increment at tick 43. Drive's corresponding case
   charged zero. The response differs by form, allowing stored attempted speed
   and severity to evolve differently while continuing pressure against a wall.
2. Three 12 m/s contacts with 0.5 s clearance produced three episodes and 72%
   total loss. With 0.1 s clearance and a deliberate 3.5 m gap, v1 merged them
   into one episode and charged only 24%. The time-only debounce masked genuinely
   separated contacts. These placement cases isolate grouping, not player routes.

These findings **do not establish the cause of Charlie's unrecorded near-stop
Spread hit**. A fresh sub-2 m/s head-on case produces zero, not 22%. A previously
charged episode can make a later increment look smaller; angle, pre/post-contact
timing, the early severity cap and cumulative-versus-incremental readings can
also change comparisons. The new owner receipts are necessary to identify the
specific event rather than retroactively invent it.

## Narrow v1.1 correction

Keep the severity curve, cap and condition scale unchanged. Latch cargo charge
at the first fresh, unambiguous controller impact of an episode, including an
entry below the cargo dead zone. Ambiguous/nonfresh contacts cannot pre-empt
that entry. Later pressure cannot raise that episode's bill. A genuinely separated
contact may rearm either after the existing .25 s quiet interval, or after an
observed .25 m outward separation from the last wall-contact position while no
wall contact exists. This is read-only contact grouping, not a force, velocity
correction, distance-based damage formula or hidden movement simulation.

Continuously touching connected walls remains one conservative episode; it may
forgive a secondary corner strike until there is clear separation. Do not expand
into a new collision solver. Keep poor/zero cargo deliverable. Review receipts
must distinguish the episode's billed entry severity from later controller peaks.
