extends RefCounted
## Crew run text. One short sentence per beat so it can be read at speed.
## Tess is the established mender (opening chapter); Depot is where her borrowed
## table stood ("Yard's quieter without her"). The night crew are unnamed Depot
## voices, like the Depot receiver in the opening.

const TESS := "TESS · Mending"
const CREW := "DEPOT · Night crew"
const YARD := "HEM LOOP"

const BRIEF := [
	[CREW, "Night run's short one jacket. Tess has it at the Hem."],
	[CREW, "She'll hold it over the inside wall. Don't stop for it."],
]
const APPROACH := [
	"Inside wall. I'll hold it out.",
	"Unfold before the lamp. Come in tight.",
	"Tighter. Right along the wall.",
]
const MISS := [
	"Too wide. I'm not leaning out any further.",
	"Still got it. Unfold early, hug the wall.",
	"Round again. I've got all evening.",
]
const CATCH_FIRST := "That's it. First time, too."
const CATCH_AGAIN := "There. Go on, they're waiting."
const CATCH_SLOW := "You can keep moving, you know. Everyone did."
const CATCH_DRIVE := "Folded, at that speed? Show-off."

const DELIVER_FIRST := "First pass, and not a mark on it. Ta."
const DELIVER_AGAIN := "Took a few goes. Not a mark on it, though."
const DELIVER_SCUFF := "Bit of wall on the sleeve. She'll spot that."
const DELIVER_WALL := "You've brought half the yard wall back on it."
const REVEAL := [
	[CREW, "Her table sat on the inside of that bend for a year."],
	[CREW, "You took your mending off her tight, or went round again."],
	[CREW, "That's why it's the Hem."],
]
const DONE := "Crew run done · T time trial · C run it again"
const AFTER_CLEAN := "Clean all the way round. Now I've seen everything."
const AFTER_SCUFFED := "Saw the sleeve. Leave it on the hook Tuesday."
