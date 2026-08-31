#!/usr/bin/env python3
"""Pure interaction-state model for overnight iteration 01."""

from __future__ import annotations

from dataclasses import dataclass
import math


NEUTRAL_ACTIONS = (
    "throttle",
    "brake",
    "steer_left",
    "steer_right",
    "transform",
    "hop",
    "reset",
    "pause",
    "interact",
    "accept",
    "cancel",
)


def dispatch_eligible(
    *,
    distance_to_pad_m: float,
    support_probe_count: int,
    measured_height_m: float,
    tangential_speed_mps: float,
    radius_m: float = 8.0,
    speed_ceiling_mps: float = 4.0,
) -> bool:
    values = (distance_to_pad_m, measured_height_m, tangential_speed_mps, radius_m, speed_ceiling_mps)
    return (
        all(math.isfinite(value) for value in values)
        and distance_to_pad_m <= radius_m
        and support_probe_count >= 2
        and measured_height_m >= 0.0
        and tangential_speed_mps <= speed_ceiling_mps
    )


def delivery_feedback(
    *,
    destination_label: str,
    distance_to_pad_m: float,
    support_probe_count: int,
    measured_height_m: float,
    tangential_speed_mps: float,
    cargo_loss_increment: float,
    settle_fraction: float,
    radius_m: float = 8.0,
    speed_ceiling_mps: float = 6.0,
) -> str:
    values = (
        distance_to_pad_m,
        measured_height_m,
        tangential_speed_mps,
        cargo_loss_increment,
        settle_fraction,
    )
    if not all(math.isfinite(value) for value in values) or distance_to_pad_m > radius_m:
        return f"REACH {destination_label}"
    if support_probe_count < 2 or measured_height_m < 0.0:
        return "TOUCH DOWN"
    if cargo_loss_increment > 0.0:
        return "CARGO MOVING — STABILIZE"
    if tangential_speed_mps > speed_ceiling_mps:
        return f"SLOW · {tangential_speed_mps:.1f} / {speed_ceiling_mps:.1f} m/s"
    percent = round(max(0.0, min(1.0, settle_fraction)) * 100.0)
    return f"UNLOADING {percent}%"


@dataclass
class LoopModel:
    settle_required_s: float = 0.50
    state: str = "FREE_ROAM"
    paused: bool = False
    elapsed_s: float = 0.0
    settle_s: float = 0.0
    result_commits: int = 0
    award_commits: int = 0
    terminal: str | None = None
    _resume_target: str | None = None
    _paused_gameplay_state: str | None = None
    _neutral_frames: int = 0
    _resume_on_next_physics: bool = False

    def open_board(self, *, eligible: bool, fresh_edge: bool = True) -> bool:
        if self.state != "FREE_ROAM" or not eligible or not fresh_edge:
            return False
        self.state = "BOARD_OPEN"
        self.paused = True
        return True

    def accept(self, *, fresh_edge: bool = True) -> bool:
        if self.state != "BOARD_OPEN" or not fresh_edge:
            return False
        self._wait_for_neutral("ACTIVE")
        return True

    def cancel_board(self, *, fresh_edge: bool = True) -> bool:
        if self.state != "BOARD_OPEN" or not fresh_edge:
            return False
        self._wait_for_neutral("FREE_ROAM")
        return True

    def continue_results(self, *, fresh_edge: bool = True) -> bool:
        if self.state != "RESULTS" or not fresh_edge:
            return False
        self._wait_for_neutral("FREE_ROAM")
        return True

    def open_pause(self, *, fresh_edge: bool = True) -> bool:
        if self.state not in {"ACTIVE", "DELIVERY_SETTLE"} or not fresh_edge:
            return False
        self._paused_gameplay_state = self.state
        self.state = "PAUSE_OPEN"
        self.paused = True
        return True

    def close_pause(self, *, fresh_edge: bool = True) -> bool:
        if self.state != "PAUSE_OPEN" or not fresh_edge:
            return False
        target = str(self._paused_gameplay_state)
        self._paused_gameplay_state = None
        self._wait_for_neutral(target)
        return True

    def consume_modal_reset(self) -> bool:
        """UI owns reset while paused; R7 must not receive it."""
        return self.state in {"BOARD_OPEN", "WAITING_FOR_NEUTRAL", "PAUSE_OPEN", "RESULTS"}

    def _wait_for_neutral(self, target: str) -> None:
        self.state = "WAITING_FOR_NEUTRAL"
        self.paused = True
        self._resume_target = target
        self._neutral_frames = 0
        self._resume_on_next_physics = False

    def sample_neutral(self, action_strengths: dict[str, float]) -> None:
        if self.state != "WAITING_FOR_NEUTRAL":
            return
        neutral = all(abs(float(action_strengths.get(action, 0.0))) < 0.01 for action in NEUTRAL_ACTIONS)
        self._neutral_frames = self._neutral_frames + 1 if neutral else 0
        if self._neutral_frames >= 2:
            self.paused = False
            self._resume_on_next_physics = True

    def physics_tick(
        self,
        delta: float,
        *,
        delivery_valid: bool = False,
        cargo_loss_impact: bool = False,
        reset: bool = False,
    ) -> None:
        if not math.isfinite(delta) or delta <= 0.0:
            raise ValueError("delta must be finite and positive")
        if self.paused:
            return

        resumed_this_tick = False
        if self.state == "WAITING_FOR_NEUTRAL" and self._resume_on_next_physics:
            self.state = str(self._resume_target)
            self._resume_target = None
            self._resume_on_next_physics = False
            resumed_this_tick = True

        if self.state not in {"ACTIVE", "DELIVERY_SETTLE"}:
            return

        # Reset/abort owns the terminal race. An impact would be sampled before
        # this in product code, but neither result nor award can survive abort.
        if reset:
            self.state = "ABORTED"
            self.terminal = "ABORTED"
            self.settle_s = 0.0
            return

        # The timer's first charge is this same ordinary physics tick; there is
        # no input-only arming detector and no wall-clock catch-up.
        self.elapsed_s += delta
        # A zero-loss contact is preserved in the receipt but is not allowed to
        # create confusing unload flicker. Only a positive cargo-loss increment
        # breaks the settle streak.
        valid = delivery_valid and not cargo_loss_impact
        if not valid:
            self.state = "ACTIVE"
            self.settle_s = 0.0
            return

        if self.state == "ACTIVE":
            self.state = "DELIVERY_SETTLE"
            self.settle_s = delta
        else:
            self.settle_s += delta
        if self.settle_s + 1.0e-9 >= self.settle_required_s:
            self._commit_delivered()

        # This name makes the intended first-tick behavior reviewable in tests.
        _ = resumed_this_tick

    def _commit_delivered(self) -> None:
        if self.terminal is not None:
            return
        self.terminal = "DELIVERED"
        self.result_commits += 1
        self.award_commits += 1
        self.state = "RESULTS"
        self.paused = True
