#!/usr/bin/env python3
"""Pure cargo-integrity observer/reducer for overnight iteration 02.

This is executable design evidence only.  It deliberately models the narrow
public seam already present on the read-only R7 craft: reset_count,
impact_count, last_impact_severity, and hop_count.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import math


INTEGRITY_UNITS_FULL = 1000  # tenths of one percent
SEVERITY_MILLI_FULL = 1000


class ObserverDiscontinuity(RuntimeError):
    """The observer missed or received an invalid authoritative sample."""


def round_half_up_nonnegative(value: float) -> int:
    if not math.isfinite(value) or value < 0.0:
        raise ValueError("rounding input must be finite and nonnegative")
    return int(math.floor(value + 0.5))


@dataclass(frozen=True)
class CargoProfile:
    id: str = "FORGIVING_PEAK_EPISODE_V1"
    dead_zone_milli: int = 200
    maximum_episode_loss_units: int = 240
    response_exponent: float = 1.50
    quiet_window_s: float = 0.250

    def validate(self) -> None:
        if not self.id:
            raise ValueError("profile id is required")
        if not 0 <= self.dead_zone_milli < SEVERITY_MILLI_FULL:
            raise ValueError("dead zone must be in [0, 1000)")
        if not 0 < self.maximum_episode_loss_units <= INTEGRITY_UNITS_FULL:
            raise ValueError("maximum loss must be in (0, 1000]")
        if not math.isfinite(self.response_exponent) or self.response_exponent <= 0.0:
            raise ValueError("response exponent must be finite and positive")
        if not math.isfinite(self.quiet_window_s) or self.quiet_window_s <= 0.0:
            raise ValueError("quiet window must be finite and positive")


def quantize_severity_milli(severity: float) -> int:
    if not math.isfinite(severity) or not 0.0 <= severity <= 1.0:
        raise ObserverDiscontinuity("impact severity must be finite and within [0, 1]")
    return min(SEVERITY_MILLI_FULL, round_half_up_nonnegative(severity * SEVERITY_MILLI_FULL))


def episode_loss_units(severity: float, profile: CargoProfile = CargoProfile()) -> int:
    """Return the cumulative tenths-of-a-percent loss for one episode peak."""
    profile.validate()
    severity_milli = quantize_severity_milli(severity)
    if severity_milli <= profile.dead_zone_milli:
        return 0
    denominator = SEVERITY_MILLI_FULL - profile.dead_zone_milli
    normalized = (severity_milli - profile.dead_zone_milli) / float(denominator)
    raw_units = profile.maximum_episode_loss_units * math.pow(normalized, profile.response_exponent)
    return min(profile.maximum_episode_loss_units, round_half_up_nonnegative(raw_units))


@dataclass(frozen=True)
class SampleResult:
    damage_units: int
    integrity_units: int
    impact_observed: bool
    hop_started: bool
    settle_interrupt: bool
    episode_id: int | None
    status: str


@dataclass
class CargoIntegrityTracker:
    """Late-priority, epoch-aware observer of R7's sticky public snapshot."""

    profile: CargoProfile = field(default_factory=CargoProfile)
    status: str = "IDLE"
    integrity_units: int = INTEGRITY_UNITS_FULL
    active_time_s: float = 0.0
    expected_sequence: int = 0
    last_impact_count: int = 0
    last_hop_count: int = 0
    reset_epoch: int = 0
    episode_id: int = 0
    episode_open: bool = False
    episode_peak_milli: int = 0
    episode_charged_units: int = 0
    last_impact_time_s: float | None = None
    episode_ledger: list[dict] = field(default_factory=list)

    def start(self, *, impact_count: int, hop_count: int, reset_count: int) -> None:
        self.profile.validate()
        try:
            self._require_counter(impact_count, "impact_count")
            self._require_counter(hop_count, "hop_count")
            self._require_counter(reset_count, "reset_count")
        except ObserverDiscontinuity as error:
            self._invalidate(str(error))
        self.status = "ACTIVE"
        self.integrity_units = INTEGRITY_UNITS_FULL
        self.active_time_s = 0.0
        self.expected_sequence = 0
        self.last_impact_count = impact_count
        self.last_hop_count = hop_count
        self.reset_epoch = reset_count
        self.episode_id = 0
        self.episode_open = False
        self.episode_peak_milli = 0
        self.episode_charged_units = 0
        self.last_impact_time_s = None
        self.episode_ledger = []

    def pause_frame(self, *, impact_count: int, hop_count: int, reset_count: int) -> None:
        """Prove that a paused modal/gameplay frame cannot advance the reducer."""
        if self.status != "ACTIVE":
            return
        if (
            impact_count != self.last_impact_count
            or hop_count != self.last_hop_count
            or reset_count != self.reset_epoch
        ):
            self._invalidate("controller counters changed while gameplay was paused")

    def sample(
        self,
        *,
        sequence: int,
        delta_s: float,
        impact_count: int,
        hop_count: int,
        reset_count: int,
        impact_severity: float | None = None,
    ) -> SampleResult:
        if self.status != "ACTIVE":
            return self._result(0, False, False)
        if sequence != self.expected_sequence + 1:
            self._invalidate("active sample sequence must advance exactly once")
        if not math.isfinite(delta_s) or delta_s <= 0.0:
            self._invalidate("active physics delta must be finite and positive")
        try:
            self._require_counter(impact_count, "impact_count")
            self._require_counter(hop_count, "hop_count")
            self._require_counter(reset_count, "reset_count")
        except ObserverDiscontinuity as error:
            self._invalidate(str(error))

        # Reset owns the entire terminal sample.  Cleared impact/Hop fields are
        # never misread as counter rewinds and no same-tick cargo result survives.
        if reset_count != self.reset_epoch:
            self._close_episode()
            self.status = "ABORTED"
            return self._result(0, False, False)

        impact_delta = impact_count - self.last_impact_count
        hop_delta = hop_count - self.last_hop_count
        if impact_delta not in (0, 1):
            self._invalidate("impact counter decreased or skipped an observer sample")
        if hop_delta not in (0, 1):
            self._invalidate("Hop counter decreased or skipped an observer sample")

        self.expected_sequence = sequence
        self.active_time_s += delta_s
        hop_started = hop_delta == 1
        damage_units = 0
        impact_observed = impact_delta == 1

        if impact_observed:
            if impact_severity is None:
                self._invalidate("new impact counter requires its matching severity snapshot")
            try:
                severity_milli = quantize_severity_milli(float(impact_severity))
            except (ObserverDiscontinuity, TypeError, ValueError) as error:
                self._invalidate(str(error))
            if (
                not self.episode_open
                or self.last_impact_time_s is None
                or self.active_time_s - self.last_impact_time_s > self.profile.quiet_window_s
            ):
                self._close_episode()
                self._open_episode()
            self.episode_peak_milli = max(self.episode_peak_milli, severity_milli)
            target_units = episode_loss_units(self.episode_peak_milli / 1000.0, self.profile)
            damage_units = max(0, target_units - self.episode_charged_units)
            self.episode_charged_units += damage_units
            self.integrity_units = max(0, self.integrity_units - damage_units)
            self.last_impact_time_s = self.active_time_s
        elif (
            self.episode_open
            and self.last_impact_time_s is not None
            and self.active_time_s - self.last_impact_time_s > self.profile.quiet_window_s
        ):
            # Sticky last_impact_severity is intentionally never read here.
            self._close_episode()

        self.last_impact_count = impact_count
        self.last_hop_count = hop_count
        return self._result(damage_units, impact_observed, hop_started)

    def seal_delivered(self) -> None:
        if self.status != "ACTIVE":
            return
        self._close_episode()
        self.status = "DELIVERED"

    def _open_episode(self) -> None:
        self.episode_id += 1
        self.episode_open = True
        self.episode_peak_milli = 0
        self.episode_charged_units = 0
        self.last_impact_time_s = None

    def _close_episode(self) -> None:
        if self.episode_open:
            self.episode_ledger.append(
                {
                    "episode_id": self.episode_id,
                    "peak_severity_milli": self.episode_peak_milli,
                    "charged_loss_units": self.episode_charged_units,
                }
            )
        self.episode_open = False
        self.episode_peak_milli = 0
        self.episode_charged_units = 0
        self.last_impact_time_s = None

    def _result(self, damage_units: int, impact_observed: bool, hop_started: bool) -> SampleResult:
        return SampleResult(
            damage_units=damage_units,
            integrity_units=self.integrity_units,
            impact_observed=impact_observed,
            hop_started=hop_started,
            # Damage and Hop are separate facts.  Either one invalidates a
            # would-be unloading sample; Hop never enters the damage curve.
            settle_interrupt=damage_units > 0 or hop_started,
            episode_id=self.episode_id if self.episode_open else None,
            status=self.status,
        )

    @staticmethod
    def _require_counter(value: int, label: str) -> None:
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            raise ObserverDiscontinuity(f"{label} must be a nonnegative integer")

    def _invalidate(self, detail: str) -> None:
        self._close_episode()
        self.status = "OBSERVER_INVALID"
        raise ObserverDiscontinuity(detail)


def simulate_pressure_stream(sample_rate_hz: int, peak_severity: float = 0.75) -> CargoIntegrityTracker:
    """Create equivalent 0.2-second wall-pressure streams at several rates."""
    if sample_rate_hz <= 0:
        raise ValueError("sample rate must be positive")
    tracker = CargoIntegrityTracker()
    tracker.start(impact_count=0, hop_count=0, reset_count=0)
    sample_count = round_half_up_nonnegative(0.2 * sample_rate_hz)
    for index in range(1, sample_count + 1):
        fraction = index / float(sample_count)
        tracker.sample(
            sequence=index,
            delta_s=1.0 / sample_rate_hz,
            impact_count=index,
            hop_count=0,
            reset_count=0,
            impact_severity=peak_severity * fraction,
        )
    return tracker
