# Network Design Findings

This analysis uses the frozen v1.2.3 route endpoints and baked lengths. It does
not propose any world change.

## The important result

The route graph should shape contract design, but endpoint distance alone is
not enough. Across all 15 unordered pairs of the six destination nodes:

- `HOP` is never on the natural shortest path;
- `DOG` is never on the natural shortest path;
- `X0` is not the shortest path from QRY to RLY (`499.881 m` versus
  `398.374 m` through A0+A1);
- `A2` is not on a natural shortest destination-to-destination path; and
- only A1 appears on one natural shortest path.

An endpoint-only delivery system would therefore leave several of the most
characterful routes economically irrational. Raising their generic pay would
not solve the problem cleanly, because a player could accept the nominal job
and take a different path.

## Recommended contract geometry

Use two explicit job forms:

1. **Open courier** — only origin and destination are required. The player may
   choose any route. Payout is based on the authored contract distance, never
   the player's accumulated odometer.
2. **Sealed route** — origin, one or more named route/gate conditions, and
   destination are required. A fixed premium pays for taking HOP, DOG, X0, A2,
   or another intentionally featured path.

This preserves genuine route choice while giving the unusual roads a reason to
exist. It also yields clear contract text: "Open delivery to Works" versus
"Relay seal: X0 required."

## Natural scale bands from the actual graph

The 15 shortest destination-pair distances span roughly `118–408 m`:

- neighborhood: `118–150 m`;
- cross-district: `195–279 m`;
- long: `377–408 m`.

Those bands should inform offer variety and estimated duration, but they are
not difficulty tiers by themselves. Required fast-route, Hop, cargo, and
arrival constraints define risk separately.

## Reproducibility

`tools/analyze_route_network.py` regenerates
`analysis/ROUTE_NETWORK_ANALYSIS.json` deterministically. Its warning against
endpoint-only design is part of the report so later iterations cannot silently
forget this constraint.
