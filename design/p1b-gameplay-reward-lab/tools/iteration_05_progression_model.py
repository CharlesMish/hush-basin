#!/usr/bin/env python3
"""Pure session progression and reward-cadence model for iteration 05.

The Gate-B proof exposes only a first-clear paint issue and a labelled session
Credit balance.  A paid clear-set catalog is modeled as a separate post-Gate-B
challenger.  This module imports the canonical iteration-04 receipt/award
types; it does not import Godot, write a save, or modify R7.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, ROUND_CEILING
import hashlib
import json
from typing import Mapping

from iteration_04_payout_model import (
    ALLOWED_COMPLEXITY_REASONS,
    SCORING_VERSION,
    AttemptKey,
    AwardLedger,
    ContractTerms,
    LedgerConflict,
    Receipt,
    ceil_110_percent_to_tenth_ms,
    round_half_up,
    round_half_up_to_tenth_ms,
)


D = Decimal
GATE_B_PROOF = "GATE_B_PROOF"
POST_GATE_B_CLEAR_SET = "POST_GATE_B_CLEAR_SET"
CATALOG_VERSION = "DZ_P1B_SESSION_CLEAR_SET_CATALOG_V1"
SESSION_LABEL = "SESSION PROTOTYPE — CREDITS AND FINISHES RESET WHEN THE APP CLOSES"
DEFAULT_PAINT = "DISTRICT_STANDARD"
DEFAULT_TRAIL = "TRAIL_OFF"
PROOF_PAINTS = ("PROOF_PAINT_A", "PROOF_PAINT_B")
PROOF_TRAIL = "PROOF_TRAIL_A"
FIRST_ISSUE_ID = "C01_FIRST_CLEAR_PROOF_PAINT_ISSUE"
REQUIRED_CONTRACTS = ("C01", "C02", "C03")


class ProgressionConflict(ValueError):
    """Identity reuse or a profile mutation that must stop rather than clamp."""


class ProgressionBlocked(ValueError):
    """A valid request is unavailable without mutating the profile."""


def _nonempty(value: str, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be nonempty")
    return value


def _sha256(value: str, name: str) -> str:
    _nonempty(value, name)
    if len(value) != 64 or any(character not in "0123456789abcdef" for character in value):
        raise ValueError(f"{name} must be lowercase SHA-256")
    return value


def _positive_rate(value: int | float | str | Decimal) -> Decimal:
    try:
        rate = D(str(value))
    except Exception as exc:  # pragma: no cover - defensive conversion
        raise ValueError("catalog rate must be numeric") from exc
    if not rate.is_finite() or rate <= 0:
        raise ValueError("catalog rate must be finite and positive")
    return rate


def ceil_to_ten(value: Decimal) -> int:
    if not value.is_finite() or value <= 0:
        raise ValueError("price input must be finite and positive")
    return int((value / D(10)).to_integral_value(rounding=ROUND_CEILING)) * 10


def validate_contract_terms(terms: ContractTerms) -> None:
    """Recompute every frozen ContractTerms authority field and its identity."""
    _nonempty(terms.contract_id, "contract ID")
    if isinstance(terms.valuation_ms, bool) or not isinstance(terms.valuation_ms, int) or terms.valuation_ms <= 0:
        raise ProgressionConflict("valuation duration must be a positive integer")
    if isinstance(terms.reference_ms, bool) or not isinstance(terms.reference_ms, int) or terms.reference_ms <= 0:
        raise ProgressionConflict("pace reference must be a positive integer")
    if terms.valuation_ms % 100 != 0 or terms.reference_ms % 100 != 0:
        raise ProgressionConflict("valuation and reference must use 100 ms catalog quantum")
    possible_references = {
        ceil_110_percent_to_tenth_ms(candidate)
        for candidate in range(max(1, terms.valuation_ms - 50), terms.valuation_ms + 50)
        if round_half_up_to_tenth_ms(candidate) == terms.valuation_ms
    }
    if terms.reference_ms not in possible_references:
        raise ProgressionConflict("pace reference cannot derive from the frozen valuation cohort")
    if terms.complexity_class not in ALLOWED_COMPLEXITY_REASONS:
        raise ProgressionConflict("unregistered complexity class")
    if terms.complexity_reason not in ALLOWED_COMPLEXITY_REASONS[terms.complexity_class]:
        raise ProgressionConflict("complexity reason is not authorized for its class")
    rate = _positive_rate(terms.global_rate_per_minute)
    if isinstance(terms.cadence_allowance_ms, bool) or not isinstance(terms.cadence_allowance_ms, int) or terms.cadence_allowance_ms < 0:
        raise ProgressionConflict("cadence allowance must be a nonnegative integer")
    if terms.scoring_version != SCORING_VERSION:
        raise ProgressionConflict("contract scoring version mismatch")
    expected_base = round_half_up(
        rate
        * D(terms.valuation_ms + terms.cadence_allowance_ms)
        / D(60_000)
        * (D("1") + D("0.075") * D(terms.complexity_class))
    )
    if terms.base_credits != expected_base:
        raise ProgressionConflict("base Credits do not derive from frozen valuation terms")
    identity = {
        "contract_id": terms.contract_id,
        "valuation_ms": terms.valuation_ms,
        "reference_ms": terms.reference_ms,
        "base_credits": terms.base_credits,
        "complexity_class": terms.complexity_class,
        "complexity_reason": terms.complexity_reason,
        "global_rate_per_minute": str(rate),
        "cadence_allowance_ms": terms.cadence_allowance_ms,
        "scoring_version": terms.scoring_version,
    }
    canonical = json.dumps(identity, sort_keys=True, separators=(",", ":"))
    expected_hash = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    if terms.definition_hash != expected_hash:
        raise ProgressionConflict("contract terms definition hash mismatch")


@dataclass(frozen=True)
class PriceTerms:
    catalog_rate_per_minute: Decimal
    paint_target_minutes: Decimal
    trail_target_minutes: Decimal
    paint_price: int
    trail_price: int
    identity_hash: str

    def validate(self) -> None:
        rate = _positive_rate(self.catalog_rate_per_minute)
        paint_target = D(str(self.paint_target_minutes))
        trail_target = D(str(self.trail_target_minutes))
        if not paint_target.is_finite() or paint_target <= 0:
            raise ValueError("paint target must be finite and positive")
        if not trail_target.is_finite() or trail_target <= paint_target:
            raise ValueError("trail target must be finite and greater than paint target")
        expected_paint = ceil_to_ten(rate * paint_target)
        expected_trail = ceil_to_ten(rate * trail_target)
        if self.paint_price != expected_paint or self.trail_price != expected_trail:
            raise ProgressionConflict("price literals do not match their frozen authoring terms")
        identity = {
            "catalog_rate_per_minute": str(rate),
            "paint_target_minutes": str(paint_target),
            "trail_target_minutes": str(trail_target),
            "paint_price": expected_paint,
            "trail_price": expected_trail,
        }
        canonical = json.dumps(identity, sort_keys=True, separators=(",", ":"))
        expected_hash = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
        if self.identity_hash != expected_hash:
            raise ProgressionConflict("price-terms identity hash mismatch")


def author_price_terms(
    catalog_rate_per_minute: int | float | str | Decimal = 100,
    *,
    paint_target_minutes: int | float | str | Decimal = D("0.8"),
    trail_target_minutes: int | float | str | Decimal = D("1.6"),
) -> PriceTerms:
    """Turn one calibrated global rate into frozen whole-shelf literals."""
    rate = _positive_rate(catalog_rate_per_minute)
    paint_target = D(str(paint_target_minutes))
    trail_target = D(str(trail_target_minutes))
    if not paint_target.is_finite() or paint_target <= 0:
        raise ValueError("paint target must be finite and positive")
    if not trail_target.is_finite() or trail_target <= paint_target:
        raise ValueError("trail target must be finite and greater than paint target")
    paint_price = ceil_to_ten(rate * paint_target)
    trail_price = ceil_to_ten(rate * trail_target)
    identity = {
        "catalog_rate_per_minute": str(rate),
        "paint_target_minutes": str(paint_target),
        "trail_target_minutes": str(trail_target),
        "paint_price": paint_price,
        "trail_price": trail_price,
    }
    canonical = json.dumps(identity, sort_keys=True, separators=(",", ":"))
    result = PriceTerms(
        rate,
        paint_target,
        trail_target,
        paint_price,
        trail_price,
        hashlib.sha256(canonical.encode("utf-8")).hexdigest(),
    )
    result.validate()
    return result


@dataclass(frozen=True)
class ProgressionCatalog:
    phase: str
    contract_hashes: tuple[tuple[str, str], ...]
    price_terms: PriceTerms
    choice_set_hash: str
    catalog_hash: str

    @property
    def purchase_enabled(self) -> bool:
        return self.phase == POST_GATE_B_CLEAR_SET

    @property
    def contract_hash_map(self) -> dict[str, str]:
        return dict(self.contract_hashes)

    def validate(self) -> None:
        if self.phase not in {GATE_B_PROOF, POST_GATE_B_CLEAR_SET}:
            raise ProgressionConflict("unregistered catalog phase")
        if tuple(contract_id for contract_id, _ in self.contract_hashes) != REQUIRED_CONTRACTS:
            raise ProgressionConflict("catalog contract order/IDs differ from frozen proof set")
        hashes = []
        for _, identity in self.contract_hashes:
            hashes.append(_sha256(identity, "definition hash"))
        if len(set(hashes)) != len(hashes):
            raise ProgressionConflict("catalog contract identities are not unique")
        self.price_terms.validate()
        choice_payload = json.dumps(list(PROOF_PAINTS), separators=(",", ":"))
        expected_choice_hash = hashlib.sha256(choice_payload.encode("utf-8")).hexdigest()
        if self.choice_set_hash != expected_choice_hash:
            raise ProgressionConflict("catalog choice-set identity mismatch")
        identity = _catalog_identity(self.phase, self.contract_hashes, self.price_terms)
        canonical = json.dumps(identity, sort_keys=True, separators=(",", ":"))
        expected_catalog_hash = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
        if self.catalog_hash != expected_catalog_hash:
            raise ProgressionConflict("catalog identity hash mismatch")

    def paid_stock(self, clear_set: frozenset[str], issued_paint: str | None) -> dict[str, int]:
        self.validate()
        if not self.purchase_enabled:
            return {}
        stock: dict[str, int] = {}
        if issued_paint is not None:
            if issued_paint not in PROOF_PAINTS:
                raise ProgressionConflict("issued paint is outside the frozen choice set")
            if frozenset(("C01", "C02")).issubset(clear_set):
                other = PROOF_PAINTS[1] if issued_paint == PROOF_PAINTS[0] else PROOF_PAINTS[0]
                stock[other] = self.price_terms.paint_price
        if frozenset(REQUIRED_CONTRACTS).issubset(clear_set):
            stock[PROOF_TRAIL] = self.price_terms.trail_price
        return stock


def _catalog_identity(
    phase: str,
    contract_hashes: tuple[tuple[str, str], ...],
    price_terms: PriceTerms,
) -> dict:
    return {
        "catalog_version": CATALOG_VERSION,
        "phase": phase,
        "contract_hashes": list(contract_hashes),
        "defaults": [DEFAULT_PAINT, DEFAULT_TRAIL],
        "proof_paints": list(PROOF_PAINTS),
        "proof_trail": PROOF_TRAIL,
        "first_issue_id": FIRST_ISSUE_ID,
        "price_terms_hash": price_terms.identity_hash,
        "paint_reveal": ["C01", "C02"],
        "trail_reveal": ["C01", "C02", "C03"],
    }


def build_catalog(
    terms_by_contract: Mapping[str, ContractTerms],
    *,
    phase: str,
    catalog_rate_per_minute: int | float | str | Decimal = 100,
) -> ProgressionCatalog:
    if phase not in {GATE_B_PROOF, POST_GATE_B_CLEAR_SET}:
        raise ValueError("unregistered progression phase")
    if set(terms_by_contract) != set(REQUIRED_CONTRACTS):
        raise ValueError("catalog must bind exactly C01, C02, and C03")
    contract_hashes: list[tuple[str, str]] = []
    for contract_id in REQUIRED_CONTRACTS:
        terms = terms_by_contract[contract_id]
        validate_contract_terms(terms)
        if terms.contract_id != contract_id:
            raise ValueError("catalog key and contract terms ID differ")
        contract_hashes.append((contract_id, _sha256(terms.definition_hash, "definition hash")))
    if len({identity for _, identity in contract_hashes}) != len(contract_hashes):
        raise ValueError("contract definition hashes must be unique")
    price_terms = author_price_terms(catalog_rate_per_minute)
    choice_payload = json.dumps(list(PROOF_PAINTS), separators=(",", ":"))
    choice_set_hash = hashlib.sha256(choice_payload.encode("utf-8")).hexdigest()
    frozen_contract_hashes = tuple(contract_hashes)
    identity = _catalog_identity(phase, frozen_contract_hashes, price_terms)
    canonical = json.dumps(identity, sort_keys=True, separators=(",", ":"))
    catalog_hash = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    result = ProgressionCatalog(phase, frozen_contract_hashes, price_terms, choice_set_hash, catalog_hash)
    result.validate()
    return result


@dataclass(frozen=True)
class ProgressionCommit:
    attempt_id: str
    status: str
    credits_delta: int
    available_balance: int
    new_clear: str | None
    entitlement_created: bool


@dataclass(frozen=True)
class ClaimCommit:
    status: str
    paint_id: str
    available_balance: int


@dataclass(frozen=True)
class PurchaseCommit:
    purchase_id: str
    status: str
    item_id: str
    price: int
    available_balance: int


@dataclass(frozen=True)
class PurchaseRequestRecord:
    fingerprint: str
    item_id: str
    status: str
    price: int
    reason: str | None


class SessionProgression:
    """Session-only profile reducer downstream of canonical payout receipts."""

    def __init__(self, catalog: ProgressionCatalog, terms_by_contract: Mapping[str, ContractTerms], session_epoch: str) -> None:
        self.catalog = catalog
        self.catalog.validate()
        self.session_epoch = _nonempty(session_epoch, "session epoch")
        for terms in terms_by_contract.values():
            validate_contract_terms(terms)
        if catalog.contract_hash_map != {key: value.definition_hash for key, value in terms_by_contract.items()}:
            raise ValueError("catalog and contract terms are not identity-bound")
        self._terms_by_contract = dict(terms_by_contract)
        self._award_ledger = AwardLedger(set(catalog.contract_hash_map.values()))
        self._clear_set: set[str] = set()
        self._entitlement_available = False
        self._issued_paint: str | None = None
        self._owned_paints: set[str] = {DEFAULT_PAINT}
        self._owned_trails: set[str] = {DEFAULT_TRAIL}
        self._equipped_paint = DEFAULT_PAINT
        self._equipped_trail = DEFAULT_TRAIL
        self._credits_spent = 0
        self._purchases: dict[str, PurchaseRequestRecord] = {}

    @property
    def total_awarded(self) -> int:
        return self._award_ledger.balance

    @property
    def available_balance(self) -> int:
        return self.total_awarded - self._credits_spent

    @property
    def clear_set(self) -> frozenset[str]:
        return frozenset(self._clear_set)

    @property
    def entitlement_available(self) -> bool:
        return self._entitlement_available

    @property
    def issued_paint(self) -> str | None:
        return self._issued_paint

    @property
    def owned_paints(self) -> frozenset[str]:
        return frozenset(self._owned_paints)

    @property
    def owned_trails(self) -> frozenset[str]:
        return frozenset(self._owned_trails)

    @property
    def equipped_paint(self) -> str:
        return self._equipped_paint

    @property
    def equipped_trail(self) -> str:
        return self._equipped_trail

    @property
    def paid_stock(self) -> dict[str, int]:
        return self.catalog.paid_stock(self.clear_set, self.issued_paint)

    def snapshot(self) -> dict:
        return {
            "schema": "district_zero.p1b.session_progression_snapshot.v1",
            "label": SESSION_LABEL,
            "session_epoch": self.session_epoch,
            "catalog_hash": self.catalog.catalog_hash,
            "total_awarded": self.total_awarded,
            "credits_spent": self._credits_spent,
            "available_balance": self.available_balance,
            "clear_set": sorted(self._clear_set),
            "entitlement_available": self._entitlement_available,
            "issued_paint": self._issued_paint,
            "owned_paints": sorted(self._owned_paints),
            "owned_trails": sorted(self._owned_trails),
            "equipped_paint": self._equipped_paint,
            "equipped_trail": self._equipped_trail,
        }

    def commit_attempt(self, attempt_key: AttemptKey, receipt: Receipt) -> ProgressionCommit:
        if attempt_key.session_epoch != self.session_epoch:
            raise ProgressionConflict("attempt belongs to a different session epoch")
        receipt.validate_canonical()
        terms = self._terms_by_contract.get(receipt.contract_id)
        if terms is None or terms.definition_hash != receipt.definition_hash:
            raise ProgressionConflict("receipt is not an authorized frozen contract")
        frozen_receipt_fields = (
            receipt.contract_id,
            receipt.definition_hash,
            receipt.base_credits,
            receipt.reference_ms,
            receipt.scoring_version,
        )
        frozen_terms_fields = (
            terms.contract_id,
            terms.definition_hash,
            terms.base_credits,
            terms.reference_ms,
            terms.scoring_version,
        )
        if frozen_receipt_fields != frozen_terms_fields:
            raise ProgressionConflict("receipt payout authority differs from frozen contract terms")
        award = self._award_ledger.commit(attempt_key, receipt)
        if award.status == "DUPLICATE_NOOP":
            return ProgressionCommit(award.attempt_id, award.status, 0, self.available_balance, None, False)
        new_clear: str | None = None
        entitlement_created = False
        if receipt.terminal == "DELIVERED" and receipt.contract_id not in self._clear_set:
            self._clear_set.add(receipt.contract_id)
            new_clear = receipt.contract_id
            if receipt.contract_id == "C01" and self._issued_paint is None:
                self._entitlement_available = True
                entitlement_created = True
        return ProgressionCommit(
            award.attempt_id,
            award.status,
            award.credits_delta,
            self.available_balance,
            new_clear,
            entitlement_created,
        )

    def claim_first_issue(self, entitlement_id: str, choice_set_hash: str, paint_id: str) -> ClaimCommit:
        if entitlement_id != FIRST_ISSUE_ID:
            raise ProgressionBlocked("unknown entitlement")
        if choice_set_hash != self.catalog.choice_set_hash:
            raise ProgressionConflict("entitlement choice-set identity mismatch")
        if paint_id not in PROOF_PAINTS:
            raise ProgressionBlocked("paint is not in the frozen issue choice")
        if self._issued_paint is not None:
            if self._issued_paint == paint_id:
                return ClaimCommit("DUPLICATE_NOOP", paint_id, self.available_balance)
            raise ProgressionConflict("one entitlement was reused for a different paint")
        if not self._entitlement_available:
            raise ProgressionBlocked("first-clear paint issue is not available")
        self._issued_paint = paint_id
        self._entitlement_available = False
        self._owned_paints.add(paint_id)
        self._equipped_paint = paint_id
        return ClaimCommit("GRANTED_AND_EQUIPPED", paint_id, self.available_balance)

    def purchase(self, purchase_id: str, catalog_hash: str, item_id: str, *, equip: bool = True) -> PurchaseCommit:
        purchase_id = _nonempty(purchase_id, "purchase id")
        _nonempty(item_id, "item id")
        _sha256(catalog_hash, "catalog hash")
        fingerprint_payload = json.dumps(
            {"catalog_hash": catalog_hash, "item_id": item_id, "equip": bool(equip)},
            sort_keys=True,
            separators=(",", ":"),
        )
        fingerprint = hashlib.sha256(fingerprint_payload.encode("utf-8")).hexdigest()
        if purchase_id in self._purchases:
            prior = self._purchases[purchase_id]
            if prior.fingerprint != fingerprint:
                raise ProgressionConflict("purchase identity was reused with altered content")
            if prior.status == "PURCHASED":
                return PurchaseCommit(purchase_id, "DUPLICATE_NOOP", prior.item_id, 0, self.available_balance)
            if prior.status == "ALREADY_OWNED_NOOP":
                return PurchaseCommit(purchase_id, prior.status, prior.item_id, 0, self.available_balance)
            raise ProgressionBlocked(prior.reason or "purchase request was previously blocked")
        if not self.catalog.purchase_enabled:
            reason = "paid stock is not authorized in the Gate-B proof"
            self._purchases[purchase_id] = PurchaseRequestRecord(fingerprint, item_id, "BLOCKED_PHASE", 0, reason)
            raise ProgressionBlocked(reason)
        if catalog_hash != self.catalog.catalog_hash:
            raise ProgressionConflict("purchase uses a stale or foreign catalog")
        if item_id in self._owned_paints or item_id in self._owned_trails:
            self._purchases[purchase_id] = PurchaseRequestRecord(fingerprint, item_id, "ALREADY_OWNED_NOOP", 0, None)
            return PurchaseCommit(purchase_id, "ALREADY_OWNED_NOOP", item_id, 0, self.available_balance)
        stock = self.paid_stock
        if item_id not in stock:
            reason = "item is unknown or its exact clear predicate is locked"
            self._purchases[purchase_id] = PurchaseRequestRecord(fingerprint, item_id, "BLOCKED_STOCK", 0, reason)
            raise ProgressionBlocked(reason)
        price = stock[item_id]
        if self.available_balance < price:
            reason = "insufficient session Credits"
            self._purchases[purchase_id] = PurchaseRequestRecord(fingerprint, item_id, "BLOCKED_FUNDS", price, reason)
            raise ProgressionBlocked(reason)
        self._credits_spent += price
        if item_id in PROOF_PAINTS:
            self._owned_paints.add(item_id)
            if equip:
                self._equipped_paint = item_id
        elif item_id == PROOF_TRAIL:
            self._owned_trails.add(item_id)
            if equip:
                self._equipped_trail = item_id
        else:  # pragma: no cover - paid_stock is the closed whitelist
            raise AssertionError("catalog exposed an unknown item")
        self._purchases[purchase_id] = PurchaseRequestRecord(fingerprint, item_id, "PURCHASED", price, None)
        return PurchaseCommit(purchase_id, "PURCHASED", item_id, price, self.available_balance)

    def equip(self, item_id: str) -> str:
        if item_id in self._owned_paints:
            self._equipped_paint = item_id
            return "EQUIPPED_PAINT"
        if item_id in self._owned_trails:
            self._equipped_trail = item_id
            return "EQUIPPED_TRAIL"
        raise ProgressionBlocked("only an owned/default cosmetic may be equipped")

    def new_session(self, session_epoch: str) -> "SessionProgression":
        if session_epoch == self.session_epoch:
            raise ProgressionConflict("new session epoch must differ from the active epoch")
        return SessionProgression(self.catalog, self._terms_by_contract, session_epoch)


def progression_field_whitelist() -> frozenset[str]:
    """Fields allowed in the reviewable session snapshot; notably no Rep/XP."""
    return frozenset(
        {
            "schema",
            "label",
            "session_epoch",
            "catalog_hash",
            "total_awarded",
            "credits_spent",
            "available_balance",
            "clear_set",
            "entitlement_available",
            "issued_paint",
            "owned_paints",
            "owned_trails",
            "equipped_paint",
            "equipped_trail",
        }
    )
