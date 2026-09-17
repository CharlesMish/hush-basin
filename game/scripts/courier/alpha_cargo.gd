extends "res://scripts/courier/cargo_observer.gd"
## Preserve v1.1 attribution verbatim. Only the accepted cargo bill is reduced.
const Catalog = preload("res://scripts/courier/alpha_contracts.gd")
var protected := false
var raw_total := 0
var saved_total := 0
var committed_total := 0
var loss_receipt: Dictionary={}

func begin(craft: CraftController) -> void:
	super.begin(craft)
	raw_total=0;saved_total=0;committed_total=0;loss_receipt={}

func reduce(delta: float, fresh_obstacle: bool, severity: float, wall_touch: bool) -> int:
	var before:=condition_units
	var previous_episode:=episodes
	var original_loss:=super.reduce(delta,fresh_obstacle,severity,wall_touch)
	if episodes==previous_episode:return original_loss
	# The original episode peak is preserved, including when remaining condition
	# caps loss. Apply protection before that cap; never repair past damage.
	var raw_nominal:=_charged_peak
	var protected_nominal:=int(floorf(raw_nominal*(100-Catalog.LINER_PERCENT)/100.0+0.5)) if protected else raw_nominal
	var raw_capped:=mini(before,raw_nominal)
	var committed:=mini(before,protected_nominal)
	condition_units=before-committed
	raw_total+=raw_capped;saved_total+=raw_capped-committed;committed_total+=committed
	loss_receipt={"cargo_episode":episodes,"raw_episode_loss_units":raw_nominal,"raw_capped_loss_units":raw_capped,"protection_percent":Catalog.LINER_PERCENT if protected else 0,"protection_nominal_reduction_units":raw_nominal-protected_nominal,"protection_actual_reduction_units":raw_capped-committed,"committed_loss_units":committed,"condition_before_units":before,"condition_after_units":condition_units}
	loss_receipt.make_read_only()
	return committed
