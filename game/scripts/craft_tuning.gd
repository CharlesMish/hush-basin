class_name CraftTuning
extends Resource

## Single source of provisional mechanical and presentation tuning.
## These values implement the Drive Lab hypothesis; owner feel remains untested.

@export_category("World")
@export var gravity: float = 18.0
@export var fall_reset_y: float = -12.0

@export_category("Spread Support")
@export var spread_target_height: float = 1.25
@export var spread_hover_omega: float = 8.0
@export var spread_hover_zeta: float = 1.0
@export var spread_hover_accel_up_max: float = 42.0
@export var spread_hover_accel_down_max: float = 24.0
@export var spread_gravity_compensation_ratio: float = 1.0

@export_category("Drive Support")
@export var drive_target_height: float = 0.82
@export var drive_hover_omega: float = 3.8
@export var drive_hover_zeta: float = 0.9
@export var drive_hover_accel_up_max: float = 22.0
@export var drive_hover_accel_down_max: float = 9.0
@export var drive_gravity_compensation_ratio: float = 1.0

@export_category("Spread Propulsion")
@export var spread_thrust_accel: float = 15.0
@export var spread_powered_speed_soft: float = 12.0
@export var spread_powered_speed_cap: float = 17.0
@export var spread_steer_rate: float = 1.9
@export var spread_drag: float = 0.62
@export var spread_brake_decel: float = 19.0

@export_category("Drive Propulsion")
@export var drive_thrust_accel: float = 29.0
@export var drive_powered_speed_soft: float = 25.0
@export var drive_powered_speed_cap: float = 35.0
@export var drive_steer_rate: float = 0.44
@export var drive_drag: float = 0.08
@export var drive_brake_decel: float = 4.5
@export var fold_duration: float = 0.24
@export var deploy_duration: float = 0.20

@export_category("Support Reacquisition")
@export var support_reacquire_duration: float = 0.30
@export var support_reacquire_max_distance: float = 2.45
@export var support_reacquire_max_slope_degrees: float = 42.0
@export var support_reacquire_max_departure_speed: float = 0.5

@export_category("Spread Hop")
@export var hop_normal_speed: float = 6.4
@export var hop_tangential_retention: float = 0.84
@export var hop_cooldown: float = 0.78
@export var hop_max_fold_amount: float = 0.20
@export var hop_max_support_distance: float = 1.55
@export var hop_input_buffer_seconds: float = 0.18
@export var hop_support_grace_seconds: float = 0.10

@export_category("Impact Response")
@export var impact_min_closing_speed: float = 1.0
@export var impact_full_closing_speed: float = 9.5
@export var spread_impact_max_speed_loss: float = 0.18
@export var drive_impact_max_speed_loss: float = 0.82
@export var impact_strike_cue_duration: float = 0.55

@export_category("Advisory Preview")
@export var preview_min_distance: float = 2.0
@export var preview_max_distance: float = 8.5
@export var preview_seconds_ahead: float = 0.24

@export_category("Presentation")
@export var visual_bank_degrees: float = 11.0
@export var visual_response: float = 8.0
@export var camera_distance: float = 8.5
@export var camera_height: float = 4.8
@export var camera_look_ahead: float = 3.2
@export var camera_look_height: float = 0.65
@export var camera_response: float = 7.0
@export var spread_camera_fov: float = 68.0
@export var drive_fov_increase: float = 5.5
