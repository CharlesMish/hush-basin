extends RefCounted
## Test-only racing lines for the Hem Loop bot (see rink_bot.gd for the format).

const CENTRE_SPREAD := [
	["YARD", 0.0, 0.0, "S", 15.0],
	["HEM", 0.0, 0.0, "S", 15.0],
	["SIDING", 0.0, 0.0, "S", 15.0],
	["CRANE", 0.0, -3.0, "S", 12.0],
	["SOUTH", 0.0, 0.0, "S", 15.0],
	["GATE", 0.0, 0.0, "S", 15.0],
]

## Fast solo line: Drive drift through the Hem (nose in, thrust bending the
## velocity), unfold for Crane Corner outside the dock, Drive through the Gate.
const DRIFT := [
	["YARD", 0.0, 0.0, "D", 34.0],
	["YARD", 0.7, -6.0, "D", 34.0],
	["HEM", -60.0, -6.0, "D", 28.0],
	["HEM", 0.0, -3.0, "D", 28.5],
	["HEM", 0.5, 0.0, "D", 28.5],
	["HEM", 0.95, -3.0, "D", 30.0],
	["POINTS", 0.5, -5.0, "D", 34.0],
	["SIDING", 0.5, 0.0, "D", 34.0],
	["CRANE", -40.0, -6.0, "S", 15.0],
	["CRANE", 0.0, -5.0, "S", 15.0],
	["CRANE", 0.6, -6.0, "S", 16.0],
	["CRANE", 1.0, -2.0, "D", 34.0],
	["SOUTH", 0.6, -5.0, "D", 24.0],
	["GATE", 0.0, -3.0, "D", 22.0],
	["GATE", 1.0, -3.0, "D", 30.0],
	["YARD", 30.0, -4.0, "D", 34.0],
]

## Same drift line with a Spread flick at the Hem turn-in (rotate fast, scrub).
const FLICK := [
	["YARD", 0.0, 0.0, "D", 34.0],
	["YARD", 0.6, -7.0, "D", 34.0],
	["HEM", -30.0, -6.0, "S", 30.0],
	["HEM", -22.0, -5.0, "D", 28.5],
	["HEM", 0.5, 0.0, "D", 28.5],
	["HEM", 0.95, -3.0, "D", 30.0],
	["POINTS", 0.5, -5.0, "D", 34.0],
	["SIDING", 0.5, 0.0, "D", 34.0],
	["CRANE", -40.0, -6.0, "S", 15.0],
	["CRANE", 0.0, -5.0, "S", 15.0],
	["CRANE", 0.6, -6.0, "S", 16.0],
	["CRANE", 1.0, -2.0, "D", 34.0],
	["SOUTH", 0.6, -5.0, "D", 24.0],
	["GATE", -10.0, -4.0, "S", 22.0],
	["GATE", 0.0, -3.0, "D", 22.0],
	["GATE", 1.0, -3.0, "D", 30.0],
	["YARD", 30.0, -4.0, "D", 34.0],
]

## Flick line plus the dock shortcut: Spread, Hop the buffer, cut the corner.
const DOCK_HOP := [
	["YARD", 0.0, 0.0, "D", 34.0],
	["YARD", 0.6, -7.0, "D", 34.0],
	["HEM", -30.0, -6.0, "S", 30.0],
	["HEM", -22.0, -5.0, "D", 28.5],
	["HEM", 0.5, 0.0, "D", 28.5],
	["HEM", 0.95, -3.0, "D", 30.0],
	["POINTS", 0.5, -5.0, "D", 34.0],
	["SIDING", 0.5, 2.0, "D", 34.0],
	["CRANE", -44.0, 6.5, "S", 16.0],
	["CRANE", -19.5, 7.8, "S", 16.0, true],
	["CRANE", 0.0, 8.6, "S", 16.0],
	["CRANE", 0.6, 8.6, "S", 16.0],
	["CRANE", 1.0, 3.0, "D", 34.0],
	["SOUTH", 0.6, -5.0, "D", 24.0],
	["GATE", -10.0, -4.0, "S", 22.0],
	["GATE", 0.0, -3.0, "D", 22.0],
	["GATE", 1.0, -3.0, "D", 30.0],
	["YARD", 30.0, -4.0, "D", 34.0],
]

## Crew-run line: unfold early and run the Hem's inside wall in Spread.
const INSIDE_HEM := [
	["YARD", 0.0, 0.0, "D", 34.0],
	["YARD", 0.55, 4.0, "D", 34.0],
	["HEM", -45.0, 6.0, "S", 16.0],
	["HEM", 0.08, "W+3.0", "S", 15.0],
	["HEM", 0.5, "W+2.2", "S", 15.0],
	["HEM", 0.9, "W+3.0", "S", 15.0],
	["HEMX", 0.5, 0.0, "D", 34.0],
	["POINTS", 0.5, -5.0, "D", 34.0],
	["SIDING", 0.5, 0.0, "D", 34.0],
	["CRANE", -40.0, -6.0, "S", 15.0],
	["CRANE", 0.0, -5.0, "S", 15.0],
	["CRANE", 0.6, -6.0, "S", 16.0],
	["CRANE", 1.0, -2.0, "D", 34.0],
	["SOUTH", 0.6, -5.0, "D", 24.0],
	["GATE", -10.0, -4.0, "S", 22.0],
	["GATE", 0.0, -3.0, "D", 22.0],
	["GATE", 1.0, -3.0, "D", 30.0],
	["YARD", 30.0, -4.0, "D", 34.0],
]

## Crew run, careful: inside the Hem in Spread, then Spread all the way home.
const INSIDE_CLEAN := [
	["YARD", 0.0, 0.0, "D", 34.0],
	["YARD", 0.55, 4.0, "D", 34.0],
	["HEM", -45.0, 6.0, "S", 16.0],
	["HEM", 0.08, "W+3.0", "S", 15.0],
	["HEM", 0.5, "W+2.2", "S", 15.0],
	["HEM", 0.9, "W+3.0", "S", 15.0],
	["HEMX", 0.5, 0.0, "S", 15.0],
	["SIDING", 0.0, 0.0, "S", 15.0],
	["CRANE", 0.0, -3.0, "S", 12.0],
	["SOUTH", 0.0, 0.0, "S", 15.0],
	["GATE", 0.0, 0.0, "S", 15.0],
]
