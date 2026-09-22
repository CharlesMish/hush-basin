extends RefCounted
## RGB only. Qualification, ribbon geometry, alpha and lifetime stay in SlipTrail.
## Root integration may opt into this helper after reviewing native captures.
const STANDARD_BASE := Color("69c9b9")
const STANDARD_HIGHLIGHT := Color("d7c18d")
const AMBER_BASE := Color("d5b579")
const AMBER_HIGHLIGHT := Color("d5b986")

static func color_for(style_name: String, slip: float) -> Color:
	var base := AMBER_BASE if style_name == "lantern_amber" else STANDARD_BASE
	var highlight := AMBER_HIGHLIGHT if style_name == "lantern_amber" else STANDARD_HIGHLIGHT
	return base.lerp(highlight, clampf(slip, 0.0, 1.0) * 0.35)
