#!/usr/bin/env python3
"""Pure final-convergence model for the District Zero P1B design lab.

This module does not implement gameplay and never imports Godot.  It composes
the already-tested iteration models into one bounded Gate-B recommendation,
keeps provisional tuning visibly provisional, and exposes the remaining
native/owner blockers instead of converting desk evidence into a pass.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Mapping

from iteration_04_payout_model import (
    ContractTerms,
    Receipt,
    derive_contract_terms,
    evaluate_receipt,
    pace_factor_ms,
    snapshot_from_terms,
)
from iteration_06_contract_model import authoritative_routes, build_catalog
from iteration_03_pace_grade_model import grade_for as legacy_float_grade_for


D = Decimal

DECISION_ID = "THREE_JOB_MOMENTUM_COURIER_VERTICAL_SLICE_V1"
AUTHORITY = "PURE DESIGN-LAB CONVERGENCE — NOT GODOT, BALANCE, OR HUMAN EVIDENCE"
FINAL_STATUS = "DESIGN LAB COMPLETE — AWAITING EXPLICIT P1B IMPLEMENTATION AUTHORITY"
SESSION_WARNING = "SESSION PROTOTYPE — CREDITS AND FINISHES RESET WHEN THE APP CLOSES"
NO_SHOP_LABEL = "SESSION CREDITS · NO SHOP IN THIS PROOF"
EXACT_ENGINE = "4.7.1.stable.official.a13da4feb"

INHERITED_CHECK_COUNTS = (33, 41, 64, 83, 105, 142, 154, 112)

PROOF_CONTRACT_IDS = ("C01", "C02", "C03")
PROOF_TITLES = ("Market Parcel", "Relay Window", "Clinic Glass")
DESK_PAINTS = ("ORCHID_STATIC", "SALTGLASS", "EMBER_RELAY")
DESK_PAINT_RESERVES = ("VESPER_CERAMIC", "MOSS_CIRCUIT")
DESK_TRAILS = ("TWIN_VECTOR", "COURIER_PULSE", "COMET_LEDGER")
DESK_TRAIL_RESERVES = ("ONE_WAKE", "TIDE_SCRIPT")
GATE_B_COSMETIC_SCOPE = ("DISTRICT_STANDARD", "TWO_NATIVE_APPROVED_PROOF_PAINTS", "TRAIL_OFF")

HARD_INVARIANTS = (
    "R7_MOVEMENT_WORLD_CAMERA_VEHICLE_BYTES_UNCHANGED",
    "NEW_P1B_SIBLING_OR_WRAPPER_ONLY",
    "THREE_OPEN_ENDPOINT_K0_CONTRACTS",
    "ONE_SHARED_FORGIVING_CARGO_PROFILE",
    "CLEAN_DRIFT_HOP_LANDING_ROUGH_TRAVEL_ZERO_CARGO_LOSS",
    "RESET_ABORTS_ONCE_AND_AWARDS_ZERO",
    "NO_TIMEOUT_AND_DELIVERY_VALID_AT_ANY_INTEGRITY",
    "PAYOUT_50_35_15_ONLY",
    "ROUTE_DISTANCE_FLOW_GRADE_COSMETICS_REPEATS_NEVER_PAY",
    "FULL_PAY_FOR_EVERY_GENUINE_REPEAT",
    "CANONICAL_ATOMIC_ONE_ATTEMPT_ONE_TERMINAL_LEDGER",
    "ONE_SESSION_CREDIT_BALANCE_AND_ONE_C01_FREE_PAINT_ISSUE",
    "NO_SHOP_TRAIL_SAVE_REPUTATION_OR_MECHANICAL_UPGRADE",
    "RECEIPT_FIRST_CONTINUE_DEFAULT_EXACT_SESSION_WARNING",
)

PROVISIONAL_SEEDS = {
    "cargo_integrity_units": 1000,
    "cargo_dead_zone": "0.20",
    "cargo_max_episode_loss": "0.24",
    "cargo_exponent": "1.50",
    "cargo_quiet_window_s": "0.25",
    "pickup_speed_ceiling_mps": "4.0",
    "delivery_speed_ceiling_mps": "6.0",
    "delivery_settle_s": "0.50",
    "pace_anchors": (("0.85", "1.00"), ("1.00", "0.75"), ("1.25", "0.40"), ("1.75", "0.00")),
    "grade_weights": ("0.70", "0.30"),
    "authoring_rate_credits_per_minute": "100",
    "authoring_cadence_allowance_s": "12",
}

DEFERRED = (
    "PAID_SHOP",
    "ANY_TRAIL_STOCK",
    "DURABLE_SAVE",
    "REPUTATION_XP_LEVELS",
    "POST_GATE_B_QRY_SOUTH_OR_WORKS_CHALLENGER",
    "RESULTS_RESTART_RELOCATION",
    "SEALED_ROUTE_OR_DIRECTION_ADAPTER",
    "FRAGILE_EXPRESS_MULTISTOP_OR_STACKED_MODIFIERS",
    "PHYSICAL_CARGO",
)

REJECTED_FOR_GATE_B = (
    "RAW_SPEED_BRAKE_INTEGRITY_OR_HANDLING_UPGRADES",
    "ACTUAL_DISTANCE_ROUTE_EFFICIENCY_FLOW_DRIFT_HOP_OR_GRADE_MONEY",
    "REPEAT_DECAY_COOLDOWN_DAILY_CAP_OR_RESET_FEE",
    "HARD_TIMER_OR_LATE_FAILURE",
    "AUTO_OPEN_NEXT_OFFER_OR_PICKUP_DWELL",
    "PROCEDURAL_ROTATING_OR_RANDOM_CONTRACTS",
    "FOURTH_GATE_B_CONTRACT",
)


@dataclass(frozen=True)
class PaintRefinement:
    candidate_id: str
    colors: Mapping[str, str]
    emission_ceilings: Mapping[str, Decimal]
    copy: str
    status: str = "DESK REFINEMENT — NATIVE AND OWNER REVIEW NOT PERFORMED"

    def validate(self) -> None:
        expected_roles = {"frame", "shell", "lift", "underlay", "trim", "drive_can", "joint"}
        if set(self.colors) != expected_roles or set(self.emission_ceilings) != expected_roles:
            raise ValueError("paint refinement must account for all seven presentation roles")
        for role in expected_roles:
            color = self.colors[role]
            if len(color) != 7 or color[0] != "#" or any(char not in "0123456789ABCDEF" for char in color[1:]):
                raise ValueError("paint colors must be uppercase six-digit hex")
            ceiling = self.emission_ceilings[role]
            if not isinstance(ceiling, Decimal) or not ceiling.is_finite() or not D("0") <= ceiling <= D("0.75"):
                raise ValueError("paint emission ceiling is invalid")
        if "no handling, cargo, or payout effect" not in self.copy.lower():
            raise ValueError("paint copy must state its gameplay neutrality")


ORCHID_STATIC_R1 = PaintRefinement(
    "ORCHID_STATIC",
    {
        "frame": "#241D30",
        "shell": "#5C3E73",
        "lift": "#9B68C4",
        "underlay": "#452F5A",
        "trim": "#F0B5EB",
        "drive_can": "#714D8F",
        "joint": "#3C2E44",
    },
    {
        "frame": D("0.14"),
        "shell": D("0.24"),
        "lift": D("0.38"),
        "underlay": D("0.20"),
        "trim": D("0.52"),
        "drive_can": D("0.26"),
        "joint": D("0.18"),
    },
    "A fixed violet finish. Visual only — no handling, cargo, or payout effect.",
)


@dataclass(frozen=True)
class TrailRefinement:
    candidate_id: str
    port_anchor: tuple[Decimal, Decimal, Decimal]
    starboard_anchor: tuple[Decimal, Decimal, Decimal]
    width_m: Decimal
    head_alpha: Decimal
    samples_per_rail: int
    total_vertices: int
    history_s: Decimal
    history_m: Decimal
    sample_hz: int
    sample_distance_m: Decimal
    reduced_samples_per_rail: int
    reduced_history_s: Decimal
    status: str = "DESK REFINEMENT — OUTSIDE GATE B; NATIVE/PERFORMANCE/OWNER REVIEW NOT PERFORMED"

    def validate(self) -> None:
        finite_decimals = (
            *self.port_anchor,
            *self.starboard_anchor,
            self.width_m,
            self.head_alpha,
            self.history_s,
            self.history_m,
            self.sample_distance_m,
            self.reduced_history_s,
        )
        if any(not isinstance(value, Decimal) or not value.is_finite() for value in finite_decimals):
            raise ValueError("trail profile must be finite")
        if self.port_anchor[0] >= 0 or self.starboard_anchor[0] <= 0:
            raise ValueError("trail anchors must remain mirrored behind the craft")
        if not D("0") < self.width_m <= D("0.052") or not D("0") < self.head_alpha <= D("0.50"):
            raise ValueError("trail width/alpha exceeds the refinement envelope")
        if not 1 <= self.samples_per_rail <= 32 or self.total_vertices > 128:
            raise ValueError("trail history geometry exceeds its cap")
        if self.history_s > D("0.58") or self.history_m > D("18"):
            raise ValueError("trail history exceeds time/distance cap")
        if self.sample_hz > 30 or self.sample_distance_m < D("0.30"):
            raise ValueError("trail sampling exceeds its bounded cadence")
        if self.reduced_samples_per_rail > 12 or self.reduced_history_s > D("0.24"):
            raise ValueError("reduced-motion trail exceeds its cap")


TWIN_VECTOR_R1 = TrailRefinement(
    "TWIN_VECTOR",
    (D("-0.24"), D("-0.04"), D("1.16")),
    (D("0.24"), D("-0.04"), D("1.16")),
    D("0.052"),
    D("0.50"),
    32,
    128,
    D("0.58"),
    D("18"),
    30,
    D("0.30"),
    12,
    D("0.24"),
)


@dataclass(frozen=True)
class TechnicalEvidence:
    implementation_authority: bool = False
    engine_identity: str | None = None
    r7_byte_identity: bool = False
    r7_regression_and_c1_zero: bool = False
    input_and_terminal_seam: bool = False
    cargo_observer_separation: bool = False
    recovery_anchor: bool = False
    two_native_paints: bool = False
    owner_gate_a: bool = False
    owner_gate_b: bool = False


def implementation_gate_status(evidence: TechnicalEvidence) -> str:
    """Return the first honest stop; never call the design or Gate B P1B PASS."""
    if not evidence.implementation_authority:
        return "NOT AUTHORIZED — DESIGN LAB ONLY"
    if evidence.engine_identity != EXACT_ENGINE:
        return "BLOCKED — EXACT ENGINE"
    if not evidence.r7_byte_identity or not evidence.r7_regression_and_c1_zero:
        return "BLOCKED — R7 PRESERVATION OR REGRESSION"
    if not evidence.input_and_terminal_seam:
        return "BLOCKED — INPUT OR TERMINAL SEAM"
    if not evidence.cargo_observer_separation:
        return "BLOCKED — CARGO OBSERVER"
    if not evidence.owner_gate_a:
        return "READY FOR OWNER GATE A — NOT PERFORMED"
    if not evidence.recovery_anchor:
        return "BLOCKED — RECOVERY ANCHOR; STOP AFTER C01"
    if not evidence.two_native_paints:
        return "BLOCKED — NATIVE PAINT QUALIFICATION"
    if not evidence.owner_gate_b:
        return "READY FOR OWNER GATE B — NOT PERFORMED"
    return "GATE B OWNER REVIEW COMPLETE — RETURN FOR A NEW DIRECTOR DECISION"


def proof_contract_snapshot() -> tuple[dict, ...]:
    routes = authoritative_routes()
    catalog = build_catalog(routes)
    rows: list[dict] = []
    for contract, title in zip(catalog.gate_b, PROOF_TITLES):
        rows.append(
            {
                "contract_id": contract.contract_id,
                "title": title,
                "origin": contract.origin,
                "destination": contract.destination,
                "family": contract.family,
                "cargo_profile": contract.cargo_profile,
                "complexity_class": contract.complexity_class,
                "complexity_reason": contract.complexity_reason,
                "route_options": tuple(
                    {
                        "option_id": option.option_id,
                        "route_ids": option.route_ids,
                        "suggested_distance_m": option.length_m(routes),
                        "advisory_only": option.advisory_only,
                    }
                    for option in contract.route_options
                ),
            }
        )
    return tuple(rows)


def illustrative_terms() -> dict[str, ContractTerms]:
    """Illustrative only: the final B/P literals require human calibration."""
    return {
        contract_id: derive_contract_terms(contract_id=contract_id, learned_median_ms=median_ms)
        for contract_id, median_ms in zip(PROOF_CONTRACT_IDS, (30_000, 60_000, 90_000))
    }


def _receipt(terms: ContractTerms, integrity_units: int, elapsed_ms: int) -> Receipt:
    return evaluate_receipt(
        snapshot_from_terms(
            terms,
            terminal="DELIVERED",
            integrity_units=integrity_units,
            elapsed_ms=elapsed_ms,
        )
    )


def exact_grade(receipt: Receipt) -> str:
    """Bind grade to canonical integer receipt evidence using Decimal only."""
    receipt.validate_canonical()
    if receipt.terminal != "DELIVERED":
        return receipt.terminal
    integrity = D(receipt.integrity_units) / D(1000)
    ratio = D(receipt.elapsed_ms) / D(receipt.reference_ms)
    pace = pace_factor_ms(receipt.elapsed_ms, receipt.reference_ms)
    quality = D(100) * (D("0.70") * integrity + D("0.30") * pace)
    if quality >= D("94") and integrity >= D("0.95") and ratio <= D("0.95"):
        return "S"
    if quality >= D("82") and integrity >= D("0.80"):
        return "A"
    if quality >= D("65") and integrity >= D("0.55"):
        return "B"
    if quality >= D("45"):
        return "C"
    return "D"


def _exact_pace_from_ratio(ratio: Decimal) -> Decimal:
    if ratio <= D("0.85"):
        return D("1")
    if ratio >= D("1.75"):
        return D("0")
    for left_r, left_t, right_r, right_t in (
        (D("0.85"), D("1.00"), D("1.00"), D("0.75")),
        (D("1.00"), D("0.75"), D("1.25"), D("0.40")),
        (D("1.25"), D("0.40"), D("1.75"), D("0.00")),
    ):
        if ratio <= right_r:
            alpha = (ratio - left_r) / (right_r - left_r)
            return left_t + alpha * (right_t - left_t)
    raise AssertionError("exact pace interval not found")


def _exact_grade_from_units(integrity_units: int, ratio_milli: int) -> str:
    integrity = D(integrity_units) / D(1000)
    ratio = D(ratio_milli) / D(1000)
    pace = _exact_pace_from_ratio(ratio)
    quality = D(100) * (D("0.70") * integrity + D("0.30") * pace)
    if quality >= D("94") and integrity >= D("0.95") and ratio <= D("0.95"):
        return "S"
    if quality >= D("82") and integrity >= D("0.80"):
        return "A"
    if quality >= D("65") and integrity >= D("0.55"):
        return "B"
    if quality >= D("45"):
        return "C"
    return "D"


def grade_float_boundary_audit() -> dict:
    """Reproduce the full 0.001-grid seam in the legacy design model."""
    mismatches: list[tuple[int, int, str, str]] = []
    for integrity_units in range(1001):
        for ratio_milli in range(3001):
            exact = _exact_grade_from_units(integrity_units, ratio_milli)
            legacy = legacy_float_grade_for(integrity_units / 1000, ratio_milli / 1000)["grade"]
            if legacy != exact:
                mismatches.append((integrity_units, ratio_milli, legacy, exact))
    requested_examples = ((215, 851), (575, 955), (835, 979))
    examples = [
        {
            "integrity_units": integrity_units,
            "ratio_milli": ratio_milli,
            "legacy_grade": legacy,
            "exact_grade": exact,
        }
        for integrity_units, ratio_milli, legacy, exact in mismatches
        if (integrity_units, ratio_milli) in requested_examples
    ]
    return {
        "grid": "integrity_units 0..1000 × ratio_milli 0..3000",
        "points_scanned": 1001 * 3001,
        "mismatch_count": len(mismatches),
        "examples": examples,
        "product_requirement": "derive grade with integer/Decimal/rational evidence and bind it to the canonical receipt",
    }


def economy_stress_report() -> dict:
    """Expose cadence sensitivity and wall-pressure risk; never declare balance."""
    terms = illustrative_terms()
    scenarios: dict[str, dict] = {}
    for name, integrity_units, elapsed_selector in (
        ("COMPLETION_FLOOR", 0, lambda item: item.reference_ms * 3),
        ("TYPICAL_LEARNER", 900, lambda item: item.reference_ms * 125 // 100),
        ("LEARNED_CLEAN", 950, lambda item: item.valuation_ms),
        ("CLEAN_REFERENCE", 950, lambda item: item.reference_ms),
        ("WALL_PRESSURE_SYNTHETIC", 760, lambda item: item.reference_ms * 85 // 100),
    ):
        receipts = {key: _receipt(item, integrity_units, elapsed_selector(item)) for key, item in terms.items()}
        scenarios[name] = {
            "credits": {key: receipt.credits for key, receipt in receipts.items()},
            "chain_total": sum(receipt.credits for receipt in receipts.values()),
            "elapsed_ms": {key: receipt.elapsed_ms for key, receipt in receipts.items()},
            "grade": {key: exact_grade(receipt) for key, receipt in receipts.items()},
        }

    cadence_rows: list[dict] = []
    learned = scenarios["LEARNED_CLEAN"]
    wall = scenarios["WALL_PRESSURE_SYNTHETIC"]
    for overhead_s in (4, 8, 12, 16, 20):
        rates = {
            contract_id: D(learned["credits"][contract_id]) * D(60_000)
            / D(learned["elapsed_ms"][contract_id] + overhead_s * 1000)
            for contract_id in PROOF_CONTRACT_IDS
        }
        spread = (max(rates.values()) - min(rates.values())) / min(rates.values()) * D(100)
        wall_rates = {
            contract_id: D(wall["credits"][contract_id]) * D(60_000)
            / D(wall["elapsed_ms"][contract_id] + overhead_s * 1000)
            for contract_id in PROOF_CONTRACT_IDS
        }
        cadence_rows.append(
            {
                "actual_overhead_s": overhead_s,
                "learned_clean_rates": {key: value.quantize(D("0.001")) for key, value in rates.items()},
                "learned_clean_rate_spread_percent": spread.quantize(D("0.001")),
                "wall_pressure_rates": {key: value.quantize(D("0.001")) for key, value in wall_rates.items()},
                "wall_pressure_dominates": tuple(
                    key for key in PROOF_CONTRACT_IDS if wall_rates[key] > rates[key]
                ),
            }
        )

    reduced_terms = {
        contract_id: derive_contract_terms(
            contract_id=contract_id,
            learned_median_ms=median_ms,
            global_rate_per_minute=90,
        )
        for contract_id, median_ms in zip(PROOF_CONTRACT_IDS, (30_000, 60_000, 90_000))
    }
    reduced_floor = {
        key: _receipt(item, 0, item.reference_ms * 3).credits
        for key, item in reduced_terms.items()
    }
    reduced_typical = {
        key: _receipt(item, 900, item.reference_ms * 125 // 100).credits
        for key, item in reduced_terms.items()
    }
    original_floor_total = scenarios["COMPLETION_FLOOR"]["chain_total"]
    original_typical_c01 = scenarios["TYPICAL_LEARNER"]["credits"]["C01"]
    reduced_floor_total = sum(reduced_floor.values())
    reduced_typical_total = sum(reduced_typical.values())

    return {
        "authority": "ILLUSTRATIVE V=30/60/90s, R=100, H=12s — NOT CATALOG AUTHORITY",
        "terms": {
            key: {
                "valuation_ms": item.valuation_ms,
                "reference_ms": item.reference_ms,
                "base_credits": item.base_credits,
                "complexity_class": item.complexity_class,
            }
            for key, item in terms.items()
        },
        "scenarios": scenarios,
        "cadence_sensitivity": cadence_rows,
        "acceptance_target": "respectable complete-cycle rate spread <=5%; stop above 15%",
        "wall_pressure_status": "OPEN NATIVE FALSIFIER — SYNTHETIC RATE CAN DOMINATE",
        "required_action": "measure overhead and hostile strategies; version R/H/B, never hide risk with prices or repeat decay",
        "conditional_price_sensitivity": {
            "authority": "OFFLINE -10% GLOBAL-RATE PERTURBATION — 80/160 SHELF REMAINS UNAUTHORIZED",
            "original_bases": {key: item.base_credits for key, item in terms.items()},
            "reduced_bases": {key: item.base_credits for key, item in reduced_terms.items()},
            "typical_chain_original": scenarios["TYPICAL_LEARNER"]["chain_total"],
            "typical_chain_reduced": reduced_typical_total,
            "floor_chain_original": original_floor_total,
            "floor_chain_reduced": reduced_floor_total,
            "floor_plus_typical_c01_after_240_original": original_floor_total + original_typical_c01 - 240,
            "floor_plus_typical_c01_after_240_reduced": reduced_floor_total + reduced_typical["C01"] - 240,
        },
    }


def report_summary() -> dict:
    ORCHID_STATIC_R1.validate()
    TWIN_VECTOR_R1.validate()
    contracts = proof_contract_snapshot()
    economy = economy_stress_report()
    return {
        "schema": "district_zero.p1b.iteration_08_final_convergence_report.v1",
        "decision": DECISION_ID,
        "status": FINAL_STATUS,
        "authority": AUTHORITY,
        "inherited_pure_checks": {
            "counts": INHERITED_CHECK_COUNTS,
            "total": sum(INHERITED_CHECK_COUNTS),
        },
        "proof_catalog": contracts,
        "hard_invariants": HARD_INVARIANTS,
        "provisional_seeds": PROVISIONAL_SEEDS,
        "economy": economy,
        "legacy_float_grade_audit": grade_float_boundary_audit(),
        "cosmetics": {
            "gate_b_scope": GATE_B_COSMETIC_SCOPE,
            "desk_paints": DESK_PAINTS,
            "desk_paint_reserves": DESK_PAINT_RESERVES,
            "desk_trails": DESK_TRAILS,
            "desk_trail_reserves": DESK_TRAIL_RESERVES,
            "paint_refinement": ORCHID_STATIC_R1.candidate_id,
            "trail_refinement": TWIN_VECTOR_R1.candidate_id,
            "native_selection": "NOT PERFORMED",
            "owner_selection": "NOT PERFORMED",
        },
        "deferred": DEFERRED,
        "rejected_for_gate_b": REJECTED_FOR_GATE_B,
        "implementation_gate_now": implementation_gate_status(TechnicalEvidence()),
        "session_warning": SESSION_WARNING,
        "no_shop_label": NO_SHOP_LABEL,
        "product_source_modified": False,
        "R7_source_modified": False,
        "godot_runtime": "NOT PERFORMED IN ITERATION 08",
        "human_world_gate": "NOT PERFORMED",
        "P1B_product_implementation": "NOT STARTED",
        "P1B_pass": False,
    }
