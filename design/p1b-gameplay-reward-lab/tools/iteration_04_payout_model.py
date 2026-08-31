#!/usr/bin/env python3
"""Pure duration-valued payout and anti-farming model for iteration 04.

This design-lab model cannot read actual distance, routes, Flow, cosmetics, or
grade.  It does not import Godot and does not modify R7.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, ROUND_CEILING, ROUND_FLOOR, ROUND_HALF_UP
import hashlib
import json


D = Decimal
SCORING_VERSION = "DZ_P1B_50_35_15_REFERENCE_RATIO_V1"
ALLOWED_COMPLEXITY_REASONS = {
    0: {"NONE"},
    1: {"MACHINE_ENFORCED_FRAGILE", "MACHINE_ENFORCED_SEALED_ROUTE", "MACHINE_ENFORCED_MULTI_STOP"},
    2: {"MACHINE_ENFORCED_FRAGILE_SEALED", "MACHINE_ENFORCED_MULTI_STOP_FRAGILE"},
}
PACE_ANCHORS = (
    (D("0.85"), D("1.00")),
    (D("1.00"), D("0.75")),
    (D("1.25"), D("0.40")),
    (D("1.75"), D("0.00")),
)


class LedgerConflict(ValueError):
    """One attempt identity was reused with a materially different terminal."""


def _positive_int(value: int, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise ValueError(f"{name} must be a positive integer")
    return value


def _nonnegative_int(value: int, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError(f"{name} must be a nonnegative integer")
    return value


def _finite_decimal(value: int | float | str | Decimal, name: str) -> Decimal:
    try:
        result = D(str(value))
    except Exception as exc:  # pragma: no cover - defensive conversion
        raise ValueError(f"{name} must be numeric") from exc
    if not result.is_finite():
        raise ValueError(f"{name} must be finite")
    return result


def round_half_up(value: Decimal) -> int:
    if value < 0:
        raise ValueError("credit values cannot be negative")
    return int(value.quantize(D("1"), rounding=ROUND_HALF_UP))


def round_half_up_to_tenth_ms(value_ms: int) -> int:
    """Round integer milliseconds to the nearest 100 ms, ties upward."""
    value_ms = _positive_int(value_ms, "value_ms")
    return int((D(value_ms) / D(100)).quantize(D("1"), rounding=ROUND_HALF_UP)) * 100


def ceil_110_percent_to_tenth_ms(value_ms: int) -> int:
    value_ms = _positive_int(value_ms, "value_ms")
    candidate = D(value_ms) * D("1.10") / D(100)
    return int(candidate.quantize(D("1"), rounding=ROUND_CEILING)) * 100


def pace_factor_ms(elapsed_ms: int, reference_ms: int) -> Decimal:
    elapsed_ms = _nonnegative_int(elapsed_ms, "elapsed_ms")
    reference_ms = _positive_int(reference_ms, "reference_ms")
    ratio = D(elapsed_ms) / D(reference_ms)
    if ratio <= PACE_ANCHORS[0][0]:
        return D("1")
    if ratio >= PACE_ANCHORS[-1][0]:
        return D("0")
    for (left_r, left_t), (right_r, right_t) in zip(PACE_ANCHORS, PACE_ANCHORS[1:]):
        if ratio <= right_r:
            alpha = (ratio - left_r) / (right_r - left_r)
            return left_t + alpha * (right_t - left_t)
    raise AssertionError("pace interval was not found")


@dataclass(frozen=True)
class ContractTerms:
    contract_id: str
    valuation_ms: int
    reference_ms: int
    base_credits: int
    complexity_class: int
    complexity_reason: str
    global_rate_per_minute: Decimal
    cadence_allowance_ms: int
    scoring_version: str
    definition_hash: str


def derive_contract_terms(
    *,
    contract_id: str,
    learned_median_ms: int,
    complexity_class: int = 0,
    complexity_reason: str = "NONE",
    global_rate_per_minute: int | float | str | Decimal = 100,
    cadence_allowance_ms: int = 12_000,
) -> ContractTerms:
    """Create reviewable catalog literals from a human learned-run cohort.

    Valuation duration V and generous pace reference P are deliberately
    separate: changing P later cannot silently mint a larger base value.
    """
    if not isinstance(contract_id, str) or not contract_id.strip():
        raise ValueError("contract_id must be nonempty")
    learned_median_ms = _positive_int(learned_median_ms, "learned_median_ms")
    cadence_allowance_ms = _nonnegative_int(cadence_allowance_ms, "cadence_allowance_ms")
    if complexity_class not in ALLOWED_COMPLEXITY_REASONS:
        raise ValueError("complexity_class must be 0, 1, or 2")
    if complexity_reason not in ALLOWED_COMPLEXITY_REASONS[complexity_class]:
        raise ValueError("complexity reason is not authorized for its class")
    rate = _finite_decimal(global_rate_per_minute, "global_rate_per_minute")
    if rate <= 0:
        raise ValueError("global_rate_per_minute must be positive")

    valuation_ms = round_half_up_to_tenth_ms(learned_median_ms)
    reference_ms = ceil_110_percent_to_tenth_ms(learned_median_ms)
    complexity_multiplier = D("1") + D("0.075") * D(complexity_class)
    raw_base = rate * D(valuation_ms + cadence_allowance_ms) / D(60_000) * complexity_multiplier
    base_credits = round_half_up(raw_base)
    if base_credits <= 0:
        raise ValueError("global economy scale produces a zero-Credit contract")

    identity_fields = {
        "contract_id": contract_id,
        "valuation_ms": valuation_ms,
        "reference_ms": reference_ms,
        "base_credits": base_credits,
        "complexity_class": complexity_class,
        "complexity_reason": complexity_reason,
        "global_rate_per_minute": str(rate),
        "cadence_allowance_ms": cadence_allowance_ms,
        "scoring_version": SCORING_VERSION,
    }
    canonical = json.dumps(identity_fields, sort_keys=True, separators=(",", ":"))
    definition_hash = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    return ContractTerms(
        contract_id,
        valuation_ms,
        reference_ms,
        base_credits,
        complexity_class,
        complexity_reason,
        rate,
        cadence_allowance_ms,
        SCORING_VERSION,
        definition_hash,
    )


@dataclass(frozen=True)
class ScoringSnapshot:
    """Complete payout whitelist frozen from ContractTerms at Accept."""

    terminal: str
    contract_id: str
    definition_hash: str
    base_credits: int
    integrity_units: int
    elapsed_ms: int
    reference_ms: int
    scoring_version: str

    def validate(self) -> None:
        if self.terminal not in {"DELIVERED", "ABORTED", "OBSERVER_INVALID"}:
            raise ValueError("unregistered terminal")
        if not self.contract_id or not self.contract_id.strip():
            raise ValueError("contract_id must be nonempty")
        if len(self.definition_hash) != 64 or any(character not in "0123456789abcdef" for character in self.definition_hash):
            raise ValueError("definition_hash must be lowercase SHA-256")
        _positive_int(self.base_credits, "base_credits")
        _nonnegative_int(self.integrity_units, "integrity_units")
        if self.integrity_units > 1000:
            raise ValueError("integrity_units must be in [0,1000]")
        _nonnegative_int(self.elapsed_ms, "elapsed_ms")
        _positive_int(self.reference_ms, "reference_ms")
        if self.scoring_version != SCORING_VERSION:
            raise ValueError("scoring version mismatch")


def snapshot_from_terms(
    terms: ContractTerms,
    *,
    terminal: str,
    integrity_units: int,
    elapsed_ms: int,
) -> ScoringSnapshot:
    return ScoringSnapshot(
        terminal,
        terms.contract_id,
        terms.definition_hash,
        terms.base_credits,
        integrity_units,
        elapsed_ms,
        terms.reference_ms,
        terms.scoring_version,
    )


@dataclass(frozen=True)
class Receipt:
    terminal: str
    contract_id: str
    definition_hash: str
    base_credits: int
    credits: int
    delivery_line: int
    condition_line: int
    pace_line: int
    integrity_units: int
    elapsed_ms: int
    reference_ms: int
    pace_factor: Decimal | None
    scoring_version: str

    @property
    def lines_sum(self) -> int:
        return self.delivery_line + self.condition_line + self.pace_line

    @property
    def fingerprint(self) -> str:
        payload = {
            "terminal": self.terminal,
            "contract_id": self.contract_id,
            "definition_hash": self.definition_hash,
            "base_credits": self.base_credits,
            "credits": self.credits,
            "lines": [self.delivery_line, self.condition_line, self.pace_line],
            "integrity_units": self.integrity_units,
            "elapsed_ms": self.elapsed_ms,
            "reference_ms": self.reference_ms,
            "pace_factor": None if self.pace_factor is None else str(self.pace_factor),
            "scoring_version": self.scoring_version,
        }
        canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()

    def validate_canonical(self) -> None:
        snapshot = ScoringSnapshot(
            self.terminal,
            self.contract_id,
            self.definition_hash,
            self.base_credits,
            self.integrity_units,
            self.elapsed_ms,
            self.reference_ms,
            self.scoring_version,
        )
        expected = evaluate_receipt(snapshot)
        if self != expected:
            raise LedgerConflict("receipt is not the canonical evaluator output")


def evaluate_receipt(snapshot: ScoringSnapshot) -> Receipt:
    snapshot.validate()
    if snapshot.terminal != "DELIVERED":
        return Receipt(
            snapshot.terminal,
            snapshot.contract_id,
            snapshot.definition_hash,
            snapshot.base_credits,
            0,
            0,
            0,
            0,
            snapshot.integrity_units,
            snapshot.elapsed_ms,
            snapshot.reference_ms,
            None,
            snapshot.scoring_version,
        )
    pace = pace_factor_ms(snapshot.elapsed_ms, snapshot.reference_ms)
    integrity = D(snapshot.integrity_units) / D(1000)
    raw = {
        "delivery": D(snapshot.base_credits) * D("0.50"),
        "condition": D(snapshot.base_credits) * D("0.35") * integrity,
        "pace": D(snapshot.base_credits) * D("0.15") * pace,
    }
    credits = round_half_up(sum(raw.values(), D("0")))
    lines = {name: int(value.to_integral_value(rounding=ROUND_FLOOR)) for name, value in raw.items()}
    remainder = credits - sum(lines.values())
    stable_tie_order = {"delivery": 0, "condition": 1, "pace": 2}
    order = sorted(raw, key=lambda name: (-(raw[name] - D(lines[name])), stable_tie_order[name]))
    for name in order[:remainder]:
        lines[name] += 1
    return Receipt(
        "DELIVERED",
        snapshot.contract_id,
        snapshot.definition_hash,
        snapshot.base_credits,
        credits,
        lines["delivery"],
        lines["condition"],
        lines["pace"],
        snapshot.integrity_units,
        snapshot.elapsed_ms,
        snapshot.reference_ms,
        pace,
        snapshot.scoring_version,
    )


@dataclass(frozen=True)
class AwardCommit:
    attempt_id: str
    receipt_fingerprint: str
    status: str
    credits_delta: int
    balance_after: int


@dataclass(frozen=True)
class AttemptKey:
    session_epoch: str
    sequence: int

    def validate(self) -> None:
        if not isinstance(self.session_epoch, str) or not self.session_epoch.strip():
            raise ValueError("session_epoch must be nonempty")
        _positive_int(self.sequence, "attempt sequence")
        if self.sequence > 9_223_372_036_854_775_807:
            raise ValueError("attempt sequence overflow")

    @property
    def canonical(self) -> str:
        self.validate()
        return f"{self.session_epoch}:{self.sequence}"


class AwardLedger:
    """Atomic per-attempt award ledger; genuine repeats pay genuine receipts."""

    def __init__(self, authorized_definition_hashes: set[str], *, maximum_balance: int = 9_223_372_036_854_775_807) -> None:
        if not authorized_definition_hashes:
            raise ValueError("at least one authorized contract identity is required")
        for identity in authorized_definition_hashes:
            if len(identity) != 64 or any(character not in "0123456789abcdef" for character in identity):
                raise ValueError("authorized identities must be lowercase SHA-256")
        self._authorized_definition_hashes = frozenset(authorized_definition_hashes)
        self.maximum_balance = _positive_int(maximum_balance, "maximum_balance")
        self.balance = 0
        self._attempts: dict[str, AwardCommit] = {}
        self._highest_sequence_by_epoch: dict[str, int] = {}

    def commit(self, attempt_key: AttemptKey, receipt: Receipt) -> AwardCommit:
        attempt_id = attempt_key.canonical
        receipt.validate_canonical()
        if receipt.definition_hash not in self._authorized_definition_hashes:
            raise LedgerConflict("receipt contract identity is not authorized")
        if attempt_id in self._attempts:
            original = self._attempts[attempt_id]
            if original.receipt_fingerprint != receipt.fingerprint:
                raise LedgerConflict("attempt identity was reused with altered terminal evidence")
            return AwardCommit(attempt_id, receipt.fingerprint, "DUPLICATE_NOOP", 0, self.balance)
        highest = self._highest_sequence_by_epoch.get(attempt_key.session_epoch, 0)
        if attempt_key.sequence != highest + 1:
            raise LedgerConflict("attempt sequence was skipped, reused, wrapped, or committed out of order")
        delta = receipt.credits if receipt.terminal == "DELIVERED" else 0
        if self.balance + delta > self.maximum_balance:
            raise LedgerConflict("credit balance overflow")
        self.balance += delta
        status = "AWARDED" if delta > 0 else "NO_AWARD_TERMINAL"
        commit = AwardCommit(attempt_id, receipt.fingerprint, status, delta, self.balance)
        self._attempts[attempt_id] = commit
        self._highest_sequence_by_epoch[attempt_key.session_epoch] = attempt_key.sequence
        return commit


class FirstClearLedger:
    """Separate one-shot entitlement ledger; never part of ordinary Credits."""

    def __init__(self) -> None:
        self._claimed_entitlements: set[str] = set()

    def claim(self, entitlement_id: str, *, delivered: bool) -> bool:
        if not isinstance(entitlement_id, str) or not entitlement_id.strip():
            raise ValueError("entitlement_id must be nonempty")
        if not delivered or entitlement_id in self._claimed_entitlements:
            return False
        self._claimed_entitlements.add(entitlement_id)
        return True


def credit_rate_per_minute(credits: int, cycle_ms: int) -> Decimal:
    _nonnegative_int(credits, "credits")
    _positive_int(cycle_ms, "cycle_ms")
    return D(credits) * D(60_000) / D(cycle_ms)
