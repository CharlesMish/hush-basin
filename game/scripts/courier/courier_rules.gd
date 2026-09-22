extends RefCounted
## One job, provisional condition only. No economy, route rules or deadline.
const VERSION := "courier-slice-v1.1-cargo-feel"
const ORIGIN := "MRK"
const DESTINATION := "DEP"
const DISPATCH_SPEED := 4.0
const ARRIVAL_SPEED := 6.0
const ARRIVAL_NORMAL_SPEED := 0.75
const SETTLE_SECONDS := 0.5
const CONDITION_UNITS := 1000
const SEVERITY_DEAD_ZONE := 0.20
const EPISODE_MAX_LOSS := 240
const EPISODE_EXPONENT := 1.5
const CONTACT_QUIET_SECONDS := 0.25
const EPISODE_CLEARANCE_M := 0.25
const OBSTACLE_NORMAL_Y_MAX := 0.5

static func loss_for_severity(severity: float) -> int:
	var quantized := floorf(clampf(severity,0,1)*1000.0+0.5)/1000.0
	var amount := clampf((quantized-SEVERITY_DEAD_ZONE)/(1.0-SEVERITY_DEAD_ZONE),0,1)
	return int(floorf(EPISODE_MAX_LOSS*pow(amount,EPISODE_EXPONENT)+0.5))
