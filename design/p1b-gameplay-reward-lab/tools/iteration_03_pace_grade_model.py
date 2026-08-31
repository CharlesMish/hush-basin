#!/usr/bin/env python3
"""Pure pace, grade, receipt, and results-cadence model for iteration 03.

This is design-lab evidence.  It does not import Godot or mutate the R7 player.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, ROUND_CEILING, ROUND_FLOOR, ROUND_HALF_UP
import math
import statistics


PACE_ANCHORS = (
    (0.85, 1.00),
    (1.00, 0.75),
    (1.25, 0.40),
    (1.75, 0.00),
)

GRADE_LABELS = {
    "S": "EXCEPTIONAL",
    "A": "STRONG",
    "B": "SOLID",
    "C": "COMPLETE",
    "D": "ROUGH",
}


def _finite(value: float, name: str) -> float:
    value = float(value)
    if not math.isfinite(value):
        raise ValueError(f"{name} must be finite")
    return value


def pace_ratio(elapsed_s: float, reference_s: float) -> float:
    elapsed_s = _finite(elapsed_s, "elapsed_s")
    reference_s = _finite(reference_s, "reference_s")
    if elapsed_s < 0.0 or reference_s <= 0.0:
        raise ValueError("elapsed_s must be nonnegative and reference_s positive")
    return elapsed_s / reference_s


def pace_factor_from_ratio(ratio: float) -> float:
    ratio = _finite(ratio, "ratio")
    if ratio < 0.0:
        raise ValueError("ratio must be nonnegative")
    if ratio <= PACE_ANCHORS[0][0]:
        return 1.0
    if ratio >= PACE_ANCHORS[-1][0]:
        return 0.0
    for (left_r, left_t), (right_r, right_t) in zip(PACE_ANCHORS, PACE_ANCHORS[1:]):
        if ratio <= right_r:
            alpha = (ratio - left_r) / (right_r - left_r)
            return left_t + alpha * (right_t - left_t)
    raise AssertionError("pace anchor interval was not found")


def pace_factor(elapsed_s: float, reference_s: float) -> float:
    return pace_factor_from_ratio(pace_ratio(elapsed_s, reference_s))


def pace_hud_label(elapsed_s: float, reference_s: float) -> str:
    ratio = pace_ratio(elapsed_s, reference_s)
    minutes, seconds = divmod(int(math.floor(elapsed_s + 1.0e-9)), 60)
    clock = f"{minutes:02d}:{seconds:02d}"
    if ratio <= 0.85:
        state = "FULL BONUS OPEN"
    elif ratio < 1.75:
        state = "BONUS EASING"
    else:
        state = "BONUS ENDED · DELIVERY CONTINUES"
    return f"PACE {clock} · {state}"


def grade_for(integrity: float, ratio: float) -> dict:
    integrity = _finite(integrity, "integrity")
    ratio = _finite(ratio, "ratio")
    if not 0.0 <= integrity <= 1.0 or ratio < 0.0:
        raise ValueError("integrity must be [0,1] and ratio nonnegative")
    pace = pace_factor_from_ratio(ratio)
    quality = 100.0 * (0.70 * integrity + 0.30 * pace)
    if quality >= 94.0 and integrity >= 0.95 and ratio <= 0.95:
        grade = "S"
    elif quality >= 82.0 and integrity >= 0.80:
        grade = "A"
    elif quality >= 65.0 and integrity >= 0.55:
        grade = "B"
    elif quality >= 45.0:
        grade = "C"
    else:
        grade = "D"
    return {
        "grade": grade,
        "label": GRADE_LABELS[grade],
        "quality": quality,
        "integrity": integrity,
        "ratio": ratio,
        "pace_factor": pace,
    }


def _round_half_up(value: Decimal) -> int:
    return int(value.quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def receipt(base_credits: int, integrity: float, ratio: float) -> dict:
    """Return additive first-slice money with exact-sum display lines.

    Largest-remainder reconciliation changes no weight or raw total.  It only
    guarantees the three integer lines displayed to the player add to the one
    atomically awarded integer total.
    """
    if isinstance(base_credits, bool) or int(base_credits) != base_credits or base_credits <= 0:
        raise ValueError("base_credits must be a positive integer")
    grade = grade_for(integrity, ratio)
    raw = {
        "delivery": Decimal(base_credits) * Decimal("0.50"),
        "condition": Decimal(base_credits) * Decimal("0.35") * Decimal(str(integrity)),
        "pace": Decimal(base_credits) * Decimal("0.15") * Decimal(str(grade["pace_factor"])),
    }
    total = _round_half_up(sum(raw.values(), Decimal("0")))
    lines = {name: int(value.to_integral_value(rounding=ROUND_FLOOR)) for name, value in raw.items()}
    remainder = total - sum(lines.values())
    priority = {"delivery": 0, "condition": 1, "pace": 2}
    order = sorted(raw, key=lambda name: (-(raw[name] - Decimal(lines[name])), priority[name]))
    for name in order[:remainder]:
        lines[name] += 1
    return {
        "terminal": "DELIVERED",
        "credits": total,
        "lines": lines,
        "grade": grade["grade"],
        "grade_label": grade["label"],
        "quality": grade["quality"],
        "pace_factor": grade["pace_factor"],
        "grade_modifies_money": False,
    }


def calibrate_reference(learned_times_s: list[float], learned_integrities: list[float]) -> dict:
    """Calibrate one build-locked reference from five consecutive valid runs."""
    if len(learned_times_s) != 5 or len(learned_integrities) != 5:
        raise ValueError("exactly five consecutive learned completions are required")
    times = [_finite(value, "learned_time") for value in learned_times_s]
    integrities = [_finite(value, "learned_integrity") for value in learned_integrities]
    if any(value <= 0.0 for value in times) or any(not 0.0 <= value <= 1.0 for value in integrities):
        raise ValueError("learned completions must be positive and integrity must be [0,1]")
    if sum(value >= 0.90 for value in integrities) < 3:
        raise ValueError("route/cargo calibration must precede pace calibration")
    median = statistics.median(times)
    candidate = Decimal(str(median)) * Decimal("1.10")
    reference = float((candidate * Decimal("10")).to_integral_value(rounding=ROUND_CEILING) / Decimal("10"))
    return {
        "warmups_required": 2,
        "measured_runs": 5,
        "median_s": median,
        "reference_s": reference,
        "high_condition_runs": sum(value >= 0.90 for value in integrities),
        "version_locked": True,
    }


@dataclass(frozen=True)
class BestReceipt:
    ordinary_credits: int
    integrity_units: int
    elapsed_tenths: int

    @property
    def rank(self) -> tuple[int, int, int]:
        return (self.ordinary_credits, self.integrity_units, -self.elapsed_tenths)


def compare_session_best(current: BestReceipt | None, candidate: BestReceipt, *, delivered: bool = True) -> tuple[str, BestReceipt | None]:
    if not delivered:
        return ("NO SESSION BEST CHANGE", current)
    if current is None:
        return ("FIRST SESSION RESULT", candidate)
    if candidate.rank > current.rank:
        return ("NEW SESSION BEST RECEIPT", candidate)
    if candidate.rank == current.rank:
        return ("MATCHED SESSION BEST RECEIPT", current)
    return ("NO SESSION BEST CHANGE", current)


@dataclass
class ResultsCadence:
    """Reviewable continuation/restart semantics; never an R7 implementation."""

    origin: tuple[float, float, float]
    destination: tuple[float, float, float]
    balance: int = 0
    state: str = "ACTIVE"
    position: tuple[float, float, float] | None = None
    recovery_anchor: tuple[float, float, float] | None = None
    terminal: str | None = None
    board_open: bool = False
    relocations: int = 0
    award_commits: int = 0
    _exit_target: str | None = None
    _neutral_frames: int = 0
    _resume_ready: bool = False

    def __post_init__(self) -> None:
        if self.position is None:
            self.position = self.origin
        if self.recovery_anchor is None:
            self.recovery_anchor = self.origin

    def commit_delivery(self, credits: int) -> bool:
        if self.state != "ACTIVE" or self.terminal is not None:
            return False
        self.terminal = "DELIVERED"
        self.state = "RESULTS"
        self.position = self.destination
        self.balance += int(credits)
        self.award_commits += 1
        return True

    def active_reset_abort(self) -> bool:
        if self.state != "ACTIVE" or self.terminal is not None:
            return False
        self.terminal = "ABORTED"
        self.state = "ABORTED_ACK"
        self.position = self.origin
        self.recovery_anchor = self.origin
        self.relocations += 1
        return True

    def choose_continue(self, *, fresh_edge: bool = True) -> bool:
        return self._choose("CONTINUE", fresh_edge)

    def choose_restart_at_origin(self, *, fresh_edge: bool = True, relocation_authorized: bool = True) -> bool:
        if not relocation_authorized:
            return False
        return self._choose("RESTART", fresh_edge)

    def _choose(self, target: str, fresh_edge: bool) -> bool:
        if self.state != "RESULTS" or not fresh_edge:
            return False
        self.state = "WAITING_FOR_NEUTRAL"
        self._exit_target = target
        self._neutral_frames = 0
        self._resume_ready = False
        return True

    def sample_neutral(self, neutral: bool) -> None:
        if self.state != "WAITING_FOR_NEUTRAL":
            return
        self._neutral_frames = self._neutral_frames + 1 if neutral else 0
        self._resume_ready = self._neutral_frames >= 2

    def physics_tick(self) -> None:
        if self.state != "WAITING_FOR_NEUTRAL" or not self._resume_ready:
            return
        if self._exit_target == "CONTINUE":
            self.position = self.destination
            self.recovery_anchor = self.destination
        elif self._exit_target == "RESTART":
            self.position = self.origin
            self.recovery_anchor = self.origin
            self.relocations += 1
        else:
            raise AssertionError("invalid results target")
        self.state = "FREE_ROAM"
        self.board_open = False
        self._exit_target = None
        self._resume_ready = False

