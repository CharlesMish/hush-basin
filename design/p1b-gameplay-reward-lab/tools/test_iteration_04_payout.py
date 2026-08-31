#!/usr/bin/env python3
"""Deterministic duration valuation, payout, and anti-farming vectors."""

from __future__ import annotations

import argparse
from dataclasses import fields, replace
from decimal import Decimal
import hashlib
import json
from pathlib import Path

from iteration_04_payout_model import (
    AttemptKey,
    AwardLedger,
    FirstClearLedger,
    LedgerConflict,
    ScoringSnapshot,
    credit_rate_per_minute,
    derive_contract_terms,
    evaluate_receipt,
    pace_factor_ms,
    snapshot_from_terms,
)


PASS_RECORDS: list[dict] = []


def check(condition: bool, label: str) -> None:
    if not condition:
        raise AssertionError(label)
    PASS_RECORDS.append({"id": label, "status": "PASS"})
    print(f"PASS {label}")


def expect_error(callable_, label: str, error_type: type[Exception] = ValueError) -> None:
    try:
        callable_()
    except error_type:
        check(True, label)
    else:
        check(False, label)


def delivered(terms, integrity_units: int, elapsed_ms: int):
    return evaluate_receipt(snapshot_from_terms(terms, terminal="DELIVERED", integrity_units=integrity_units, elapsed_ms=elapsed_ms))


def run() -> dict:
    expected_pace = {0: Decimal("1"), 850: Decimal("1"), 1000: Decimal("0.75"), 1250: Decimal("0.40"), 1750: Decimal("0"), 3000: Decimal("0")}
    for elapsed, expected in expected_pace.items():
        check(pace_factor_ms(elapsed, 1000) == expected, f"fixed-point pace anchor {elapsed}/1000")
    check(pace_factor_ms(925, 1000) == Decimal("0.875"), "fixed-point first pace segment")
    check(pace_factor_ms(1125, 1000) == Decimal("0.575"), "fixed-point second pace segment")
    check(pace_factor_ms(1500, 1000) == Decimal("0.20"), "fixed-point third pace segment")
    grid = [pace_factor_ms(index, 1000) for index in range(3001)]
    check(all(left >= right for left, right in zip(grid, grid[1:])), "pace factor globally monotone")
    check(all(0 <= value <= 1 for value in grid), "pace factor globally bounded")
    expect_error(lambda: pace_factor_ms(-1, 1000), "negative elapsed rejected")
    expect_error(lambda: pace_factor_ms(1, 0), "zero reference rejected")

    examples = {
        "V30": derive_contract_terms(contract_id="V30", learned_median_ms=30_000),
        "V60": derive_contract_terms(contract_id="V60", learned_median_ms=60_000),
        "V90": derive_contract_terms(contract_id="V90", learned_median_ms=90_000),
    }
    expected = {"V30": (30_000, 33_000, 70), "V60": (60_000, 66_000, 120), "V90": (90_000, 99_000, 170)}
    for label, terms in examples.items():
        check((terms.valuation_ms, terms.reference_ms, terms.base_credits) == expected[label], f"{label} duration valuation vector")
        check(terms.complexity_class == 0 and terms.complexity_reason == "NONE", f"{label} initial proof complexity is zero")
        check(len(terms.definition_hash) == 64, f"{label} terms have SHA-256 identity")

    half_up = derive_contract_terms(contract_id="HALF", learned_median_ms=31_500)
    check(half_up.valuation_ms == 31_500 and half_up.base_credits == 73, "base uses half-up Credit rounding sentinel")
    k0 = derive_contract_terms(contract_id="K0", learned_median_ms=60_000)
    k1 = derive_contract_terms(contract_id="K1", learned_median_ms=60_000, complexity_class=1, complexity_reason="MACHINE_ENFORCED_FRAGILE")
    k2 = derive_contract_terms(contract_id="K2", learned_median_ms=60_000, complexity_class=2, complexity_reason="MACHINE_ENFORCED_FRAGILE_SEALED")
    check((k0.base_credits, k1.base_credits, k2.base_credits) == (120, 129, 138), "complexity classes apply bounded visible premiums")
    expect_error(lambda: derive_contract_terms(contract_id="BAD", learned_median_ms=60_000, complexity_class=1), "complexity premium requires machine-enforced reason")
    expect_error(lambda: derive_contract_terms(contract_id="BAD", learned_median_ms=60_000, complexity_class=3, complexity_reason="NONE"), "unregistered complexity class rejected")
    expect_error(lambda: derive_contract_terms(contract_id="", learned_median_ms=60_000), "blank contract id rejected")
    expect_error(lambda: derive_contract_terms(contract_id="BAD", learned_median_ms=0), "zero median rejected")
    expect_error(lambda: derive_contract_terms(contract_id="BAD", learned_median_ms=60_000, global_rate_per_minute=float("nan")), "nonfinite global rate rejected")
    expect_error(lambda: derive_contract_terms(contract_id="BAD", learned_median_ms=60_000, cadence_allowance_ms=-1), "negative cadence allowance rejected")

    p_generous = derive_contract_terms(contract_id="P", learned_median_ms=60_000)
    check(p_generous.reference_ms == 66_000 and p_generous.valuation_ms == 60_000, "pace reference and valuation duration are separate")
    check(replace(p_generous, reference_ms=72_000).base_credits == p_generous.base_credits, "later generosity change cannot recalculate base")
    terms_copy = p_generous
    mutated_registry = derive_contract_terms(contract_id="P", learned_median_ms=90_000)
    check(terms_copy.base_credits == 120 and mutated_registry.base_credits == 170, "accepted immutable terms survive later catalog mutation")
    check(terms_copy.definition_hash != mutated_registry.definition_hash, "catalog mutation changes identity")

    whitelist = {field.name for field in fields(ScoringSnapshot)}
    check(whitelist == {"terminal", "contract_id", "definition_hash", "base_credits", "integrity_units", "elapsed_ms", "reference_ms", "scoring_version"}, "scoring snapshot has exact frozen whitelist")
    for forbidden in ("actual_distance_m", "route_id", "flow", "paint_id", "trail_id", "odometer", "grade", "completion_count"):
        check(forbidden not in whitelist, f"scoring excludes {forbidden}")
    expect_error(
        lambda: ScoringSnapshot("DELIVERED", "X", "a" * 64, 100, 1000, 1000, 1000, "DZ_P1B_50_35_15_REFERENCE_RATIO_V1", actual_distance_m=99),
        "distance cannot enter evaluator constructor",
        TypeError,
    )

    for base in (1, 7, 70, 73, 120, 138, 170, 999):
        terms = replace(examples["V60"], base_credits=base)
        receipt = delivered(terms, 923, 75_042)
        check(receipt.lines_sum == receipt.credits, f"three lines exactly reconcile at base {base}")
        check((base + 1) // 2 <= receipt.credits <= base, f"delivered payout bounded at base {base}")
    floor_terms = replace(examples["V60"], base_credits=101)
    floor = delivered(floor_terms, 0, floor_terms.reference_ms * 3)
    perfect = delivered(floor_terms, 1000, 0)
    check(floor.credits == 51, "worst successful record receives rounded fifty-percent floor")
    check(perfect.credits == 101, "perfect record receives base and never more")
    check(floor.lines_sum == floor.credits and perfect.lines_sum == perfect.credits, "receipt lines match both extrema")

    for terminal in ("ABORTED", "OBSERVER_INVALID"):
        receipt = evaluate_receipt(snapshot_from_terms(examples["V60"], terminal=terminal, integrity_units=1000, elapsed_ms=0))
        check(receipt.credits == 0 and receipt.lines_sum == 0, f"{terminal} has zero award")
    expect_error(lambda: evaluate_receipt(snapshot_from_terms(examples["V60"], terminal="UNKNOWN", integrity_units=1000, elapsed_ms=0)), "unknown terminal rejected")
    expect_error(lambda: delivered(examples["V60"], 1001, 0), "integrity overflow rejected")
    expect_error(lambda: delivered(examples["V60"], -1, 0), "negative integrity rejected")

    integrity_values = [delivered(examples["V60"], units, examples["V60"].reference_ms).credits for units in range(1001)]
    check(all(left <= right for left, right in zip(integrity_values, integrity_values[1:])), "Credits monotone over every integrity unit")
    elapsed_values = [delivered(examples["V60"], 900, elapsed).credits for elapsed in range(0, 200_001, 100)]
    check(all(left >= right for left, right in zip(elapsed_values, elapsed_values[1:])), "Credits never rise with extra elapsed time")
    check(delivered(examples["V60"], 900, 0).credits == delivered(examples["V60"], 900, int(0.85 * examples["V60"].reference_ms)).credits, "shortcut pace saturates at full share")
    check(delivered(examples["V60"], 900, int(1.75 * examples["V60"].reference_ms)).credits == delivered(examples["V60"], 900, 999_999).credits, "late completion creates no debt")

    learned_rates = {}
    par_awards = {}
    learner_awards = {}
    wall_rates = {}
    for label, terms in examples.items():
        learned = delivered(terms, 950, terms.valuation_ms)
        par = delivered(terms, 950, terms.reference_ms)
        learner = delivered(terms, 900, int(Decimal("1.25") * terms.reference_ms))
        wall = delivered(terms, 760, int(Decimal("0.85") * terms.reference_ms))
        learned_rates[label] = credit_rate_per_minute(learned.credits, terms.valuation_ms + terms.cadence_allowance_ms)
        wall_rates[label] = credit_rate_per_minute(wall.credits, wall.elapsed_ms + terms.cadence_allowance_ms)
        par_awards[label] = par.credits
        learner_awards[label] = learner.credits
    check({key: delivered(examples[key], 950, examples[key].valuation_ms).credits for key in examples} == {"V30": 68, "V60": 116, "V90": 165}, "learned-clean award vectors")
    check(par_awards == {"V30": 66, "V60": 113, "V90": 161}, "clean-at-par award vectors")
    check(learner_awards == {"V30": 61, "V60": 105, "V90": 149}, "typical learner award vectors")
    learned_spread = max(learned_rates.values()) / min(learned_rates.values()) - 1
    check(learned_spread < Decimal("0.05"), "illustrative learned-clean rates fit target five-percent band")
    check(all(abs(rate - Decimal("100")) < Decimal("5") for rate in learned_rates.values()), "illustrative learned-clean rates stay near global scale")

    grid_rates = []
    for median_ms in range(20_000, 180_001, 100):
        terms = derive_contract_terms(contract_id=f"G{median_ms}", learned_median_ms=median_ms)
        receipt = delivered(terms, 950, terms.valuation_ms)
        grid_rates.append(credit_rate_per_minute(receipt.credits, terms.valuation_ms + terms.cadence_allowance_ms))
    check(min(grid_rates) >= Decimal("95") and max(grid_rates) <= Decimal("99"), "wide duration grid remains rate normalized")
    check(max(grid_rates) / min(grid_rates) - 1 < Decimal("0.04"), "wide duration grid spread remains under four percent")

    wall_advantages = {label: wall_rates[label] - learned_rates[label] for label in examples}
    check(any(value > 0 for value in wall_advantages.values()), "static model truthfully exposes plausible wall-rate vulnerability")
    check(max(wall_advantages.values()) < Decimal("2"), "illustrative wall-rate vulnerability is bounded but unresolved")

    ledger = AwardLedger({examples["V60"].definition_hash})
    first_receipt = delivered(examples["V60"], 950, examples["V60"].valuation_ms)
    first = ledger.commit(AttemptKey("session-1", 1), first_receipt)
    check(first.status == "AWARDED" and first.credits_delta == first_receipt.credits, "new delivered attempt pays full receipt")
    balance = ledger.balance
    duplicate = ledger.commit(AttemptKey("session-1", 1), first_receipt)
    check(duplicate.status == "DUPLICATE_NOOP" and duplicate.credits_delta == 0, "identical duplicate result is idempotent")
    check(ledger.balance == balance, "duplicate result cannot change balance")
    expect_error(lambda: ledger.commit(AttemptKey("session-1", 1), delivered(examples["V60"], 1000, 0)), "altered duplicate payload raises ledger conflict", LedgerConflict)
    second_receipt = delivered(examples["V60"], 900, examples["V60"].reference_ms)
    second = ledger.commit(AttemptKey("session-1", 2), second_receipt)
    check(second.credits_delta == second_receipt.credits, "genuinely new repeat pays full ordinary receipt")
    check(ledger.balance == first_receipt.credits + second_receipt.credits, "distinct attempt awards add exactly once")
    aborted_receipt = evaluate_receipt(snapshot_from_terms(examples["V60"], terminal="ABORTED", integrity_units=900, elapsed_ms=1000))
    aborted = ledger.commit(AttemptKey("session-1", 3), aborted_receipt)
    check(aborted.status == "NO_AWARD_TERMINAL" and aborted.credits_delta == 0, "aborted attempt commits zero-award terminal")
    expect_error(lambda: ledger.commit(AttemptKey("session-1", 3), second_receipt), "aborted attempt cannot later become delivered", LedgerConflict)
    expect_error(lambda: ledger.commit(AttemptKey("session-1", 5), second_receipt), "skipped attempt sequence is a ledger conflict", LedgerConflict)
    expect_error(lambda: AttemptKey("session-1", 9_223_372_036_854_775_808).validate(), "attempt sequence overflow rejected")
    expect_error(lambda: AttemptKey("", 1).validate(), "blank session epoch rejected")

    forged_lines = replace(second_receipt, delivery_line=second_receipt.delivery_line + 1)
    expect_error(lambda: ledger.commit(AttemptKey("session-1", 4), forged_lines), "forged receipt lines rejected", LedgerConflict)
    forged_value = replace(second_receipt, credits=second_receipt.credits + 1)
    expect_error(lambda: ledger.commit(AttemptKey("session-1", 4), forged_value), "forged receipt total rejected", LedgerConflict)
    foreign_terms = derive_contract_terms(contract_id="FOREIGN", learned_median_ms=60_000)
    foreign_receipt = delivered(foreign_terms, 950, foreign_terms.valuation_ms)
    expect_error(lambda: ledger.commit(AttemptKey("session-1", 4), foreign_receipt), "unauthorized contract identity rejected", LedgerConflict)
    overflow_ledger = AwardLedger({examples["V60"].definition_hash}, maximum_balance=first_receipt.credits)
    overflow_ledger.commit(AttemptKey("overflow", 1), first_receipt)
    expect_error(lambda: overflow_ledger.commit(AttemptKey("overflow", 2), second_receipt), "balance overflow rejects transaction atomically", LedgerConflict)
    check(overflow_ledger.balance == first_receipt.credits, "overflow rejection preserves prior balance")

    grants = FirstClearLedger()
    check(not grants.claim("C01_FIRST_FINISH_PAINT_CHOICE", delivered=False), "abort cannot claim first-clear entitlement")
    check(grants.claim("C01_FIRST_FINISH_PAINT_CHOICE", delivered=True), "first delivered clear claims entitlement once")
    check(not grants.claim("C01_FIRST_FINISH_PAINT_CHOICE", delivered=True), "repeat cannot duplicate first-clear entitlement")
    check(ledger.balance == first_receipt.credits + second_receipt.credits, "first-clear ledger is separate from ordinary Credits")

    detour = delivered(examples["V60"], 950, examples["V60"].reference_ms * 2)
    direct = delivered(examples["V60"], 950, examples["V60"].reference_ms)
    shortcut = delivered(examples["V60"], 950, examples["V60"].reference_ms // 2)
    check(detour.credits <= direct.credits <= shortcut.credits <= examples["V60"].base_credits, "detour cannot increase and shortcut cannot exceed base")
    check(first_receipt.base_credits == examples["V60"].base_credits, "actual route cannot mutate accepted base")

    low_overhead_rates = {
        label: credit_rate_per_minute(delivered(terms, 950, terms.valuation_ms).credits, terms.valuation_ms + 4_000)
        for label, terms in examples.items()
    }
    low_overhead_spread = max(low_overhead_rates.values()) / min(low_overhead_rates.values()) - 1
    check(low_overhead_spread > Decimal("0.10"), "four-second overhead exposes short-job farming sensitivity")
    check(low_overhead_spread < Decimal("0.15"), "illustrative four-second sensitivity remains just inside stop band")

    return {
        "selected_decision": "VERSIONED_DURATION_RATE_BASE_V1",
        "global_seed_rate_per_minute": 100,
        "cadence_allowance_seed_ms": 12000,
        "example_terms": {
            key: {
                "valuation_ms": value.valuation_ms,
                "reference_ms": value.reference_ms,
                "base_credits": value.base_credits,
                "definition_hash": value.definition_hash,
            }
            for key, value in examples.items()
        },
        "learned_clean_rates_per_minute": {key: str(value) for key, value in learned_rates.items()},
        "wall_rate_advantage_per_minute": {key: str(value) for key, value in wall_advantages.items()},
        "four_second_overhead_rate_spread": str(low_overhead_spread),
        "static_wall_rate_status": "REQUIRES_EXACT_ENGINE_HOSTILE_STRATEGY_CAPTURE",
        "human_rate_authority": "NOT CLAIMED",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    evidence = run()
    ids = [record["id"] for record in PASS_RECORDS]
    if len(ids) != len(set(ids)):
        raise AssertionError("iteration 04 check IDs must be unique")
    report = {
        "schema": "district_zero.p1b.iteration_04_payout_report.v1",
        "status": "PASS_WITH_NATIVE_RATE_FALSIFIERS_REMAINING",
        "decision": "VERSIONED_DURATION_RATE_BASE_V1",
        "checks": PASS_RECORDS,
        "check_count": len(PASS_RECORDS),
        "evidence": evidence,
        "product_source_modified": False,
    }
    payload = json.dumps(report, indent=2, sort_keys=True) + "\n"
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(payload, encoding="utf-8")
    print(f"REPORT_SHA256 {hashlib.sha256(payload.encode('utf-8')).hexdigest()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
