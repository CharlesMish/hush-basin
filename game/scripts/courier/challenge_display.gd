extends RefCounted
## Directional rounding: displayed maximum-time success cannot conceal a miss.
static func maximum_time(value: float) -> String:
	if value<0:return "not recorded"
	return "%.2f" % (ceilf((value-0.000000001)*100.0)/100.0)
static func minimum_duration(value: float) -> String:
	return "%.2f" % (floorf((value+0.000000001)*100.0)/100.0)
