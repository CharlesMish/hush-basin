#!/usr/bin/env python3
"""Deterministic clear-ledger, entitlement, purchase, and cadence vectors."""

from __future__ import annotations

import argparse
from dataclasses import replace
from decimal import Decimal
import hashlib
import inspect
import json
from itertools import permutations
from pathlib import Path

from iteration_04_payout_model import (
    AttemptKey,
    LedgerConflict,
    derive_contract_terms,
    evaluate_receipt,
    snapshot_from_terms,
)
from iteration_05_progression_model import (
    DEFAULT_PAINT,
    DEFAULT_TRAIL,
    FIRST_ISSUE_ID,
    GATE_B_PROOF,
    POST_GATE_B_CLEAR_SET,
    PROOF_PAINTS,
    PROOF_TRAIL,
    SESSION_LABEL,
    ProgressionBlocked,
    ProgressionConflict,
    SessionProgression,
    author_price_terms,
    build_catalog,
    progression_field_whitelist,
    validate_contract_terms,
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


def terms_for(medians: tuple[int, int, int] = (30_000, 60_000, 90_000)) -> dict:
    return {
        contract_id: derive_contract_terms(contract_id=contract_id, learned_median_ms=median)
        for contract_id, median in zip(("C01", "C02", "C03"), medians)
    }


def delivered(terms, integrity_units: int, elapsed_ms: int):
    return evaluate_receipt(
        snapshot_from_terms(
            terms,
            terminal="DELIVERED",
            integrity_units=integrity_units,
            elapsed_ms=elapsed_ms,
        )
    )


def aborted(terms):
    return evaluate_receipt(
        snapshot_from_terms(
            terms,
            terminal="ABORTED",
            integrity_units=1000,
            elapsed_ms=0,
        )
    )


def typical_receipts(terms: dict) -> dict:
    return {
        contract_id: delivered(value, 900, int(Decimal("1.25") * value.reference_ms))
        for contract_id, value in terms.items()
    }


def learned_receipts(terms: dict) -> dict:
    return {
        contract_id: delivered(value, 950, value.valuation_ms)
        for contract_id, value in terms.items()
    }


def par_receipts(terms: dict) -> dict:
    return {
        contract_id: delivered(value, 950, value.reference_ms)
        for contract_id, value in terms.items()
    }


def floor_receipts(terms: dict) -> dict:
    return {
        contract_id: delivered(value, 0, value.reference_ms * 3)
        for contract_id, value in terms.items()
    }


def commit_three(profile: SessionProgression, receipts: dict, order=("C01", "C02", "C03"), start_sequence: int = 1) -> int:
    sequence = start_sequence
    for contract_id in order:
        profile.commit_attempt(AttemptKey(profile.session_epoch, sequence), receipts[contract_id])
        if contract_id == "C01" and profile.issued_paint is None:
            profile.claim_first_issue(FIRST_ISSUE_ID, profile.catalog.choice_set_hash, PROOF_PAINTS[0])
        sequence += 1
    return sequence


def run() -> dict:
    price_terms = author_price_terms(100)
    check(price_terms.paint_price == 80, "provisional global rate authors eighty-Credit paint")
    check(price_terms.trail_price == 160, "provisional global rate authors one-sixty trail")
    check(price_terms.paint_target_minutes == Decimal("0.8"), "paint target is eight-tenths reward minute")
    check(price_terms.trail_target_minutes == Decimal("1.6"), "trail target is one-point-six reward minutes")
    check(len(price_terms.identity_hash) == 64, "price terms carry stable SHA-256 identity")
    ceiling = author_price_terms(101)
    check((ceiling.paint_price, ceiling.trail_price) == (90, 170), "whole shelf uses explicit upward ten-Credit quantization")
    expect_error(lambda: author_price_terms(0), "zero catalog rate rejected")
    expect_error(lambda: author_price_terms(float("nan")), "nonfinite catalog rate rejected")
    expect_error(lambda: author_price_terms(100, paint_target_minutes=0), "zero paint target rejected")
    expect_error(lambda: author_price_terms(100, trail_target_minutes=Decimal("0.8")), "trail target must exceed paint target")
    expect_error(lambda: author_price_terms(100, grade="S"), "grade cannot enter price authoring", TypeError)
    expect_error(lambda: author_price_terms(100, player_balance=9999), "player balance cannot enter price authoring", TypeError)

    terms = terms_for()
    gate_b = build_catalog(terms, phase=GATE_B_PROOF)
    gate_c = build_catalog(terms, phase=POST_GATE_B_CLEAR_SET)
    check(not gate_b.purchase_enabled, "Gate-B catalog disables every paid purchase")
    check(gate_c.purchase_enabled, "post-Gate-B challenger explicitly enables paid stock")
    check(gate_b.catalog_hash != gate_c.catalog_hash, "proof and expansion catalogs have distinct identities")
    check(gate_b.contract_hash_map == {key: value.definition_hash for key, value in terms.items()}, "catalog binds all three exact contract identities")
    check(len(gate_c.choice_set_hash) == 64, "free issue choice set is hash-bound")
    expect_error(lambda: build_catalog({"C01": terms["C01"], "C02": terms["C02"]}, phase=GATE_B_PROOF), "missing proof contract rejected")
    expect_error(lambda: build_catalog({**terms, "C04": terms["C03"]}, phase=GATE_B_PROOF), "extra contract cannot enter frozen proof catalog")
    expect_error(lambda: build_catalog({**terms, "C01": terms["C02"]}, phase=GATE_B_PROOF), "catalog key and terms mismatch rejected")
    duplicate_hashes = {**terms, "C02": replace(terms["C02"], definition_hash=terms["C01"].definition_hash)}
    expect_error(lambda: build_catalog(duplicate_hashes, phase=GATE_B_PROOF), "duplicate contract identities rejected")
    expect_error(lambda: build_catalog(terms, phase="UNKNOWN"), "unregistered progression phase rejected")
    forged_price_terms = replace(gate_b.price_terms, paint_price=1)
    expect_error(lambda: forged_price_terms.validate(), "forged price literal with stale identity rejected", ProgressionConflict)
    forged_price_hash = replace(gate_b.price_terms, identity_hash="a" * 64)
    expect_error(lambda: forged_price_hash.validate(), "forged price-terms hash rejected", ProgressionConflict)
    forged_phase_catalog = replace(gate_b, phase=POST_GATE_B_CLEAR_SET)
    expect_error(lambda: forged_phase_catalog.validate(), "phase bit flip with stale catalog hash rejected", ProgressionConflict)
    forged_price_catalog = replace(gate_b, price_terms=forged_price_terms)
    expect_error(lambda: forged_price_catalog.validate(), "one-Credit shelf with stale catalog hash rejected", ProgressionConflict)
    forged_choice_catalog = replace(gate_b, choice_set_hash="b" * 64)
    expect_error(lambda: forged_choice_catalog.validate(), "forged choice-set hash rejected", ProgressionConflict)
    expect_error(lambda: SessionProgression(forged_phase_catalog, terms, "forged-phase"), "profile construction rejects forged phase catalog", ProgressionConflict)
    expect_error(lambda: SessionProgression(forged_price_catalog, terms, "forged-price"), "profile construction rejects forged price catalog", ProgressionConflict)
    forged_base_terms = {**terms, "C01": replace(terms["C01"], base_credits=700_000_000)}
    expect_error(lambda: validate_contract_terms(forged_base_terms["C01"]), "stale-hash forged ContractTerms base rejected", ProgressionConflict)
    expect_error(lambda: build_catalog(forged_base_terms, phase=GATE_B_PROOF), "catalog build rejects forged ContractTerms base", ProgressionConflict)
    expect_error(lambda: SessionProgression(gate_b, forged_base_terms, "forged-terms-base"), "profile construction rejects forged ContractTerms base", ProgressionConflict)
    forged_reference_terms = {**terms, "C01": replace(terms["C01"], reference_ms=terms["C01"].reference_ms + 100)}
    expect_error(lambda: validate_contract_terms(forged_reference_terms["C01"]), "stale-hash forged ContractTerms reference rejected", ProgressionConflict)
    expect_error(lambda: build_catalog(forged_reference_terms, phase=GATE_B_PROOF), "catalog build rejects forged ContractTerms reference", ProgressionConflict)
    expect_error(lambda: SessionProgression(gate_b, forged_reference_terms, "forged-terms-reference"), "profile construction rejects forged ContractTerms reference", ProgressionConflict)

    profile = SessionProgression(gate_b, terms, "gate-b")
    initial = profile.snapshot()
    check(initial["label"] == SESSION_LABEL, "session-only loss is explicit in profile label")
    check(initial["available_balance"] == 0 and initial["clear_set"] == [], "new proof session begins economically empty")
    check(profile.owned_paints == frozenset({DEFAULT_PAINT}), "District Standard is the sole initial paint")
    check(profile.owned_trails == frozenset({DEFAULT_TRAIL}), "Trail Off is the sole initial trail")
    check(profile.equipped_paint == DEFAULT_PAINT and profile.equipped_trail == DEFAULT_TRAIL, "free defaults begin equipped")
    whitelist = progression_field_whitelist()
    check(set(initial) == set(whitelist), "session snapshot uses exact progression whitelist")
    for forbidden in ("reputation", "rep", "xp", "level", "grade", "condition", "pace", "route", "distance", "upgrade"):
        check(forbidden not in whitelist, f"progression snapshot excludes {forbidden}")

    before_purchase = profile.snapshot()
    expect_error(
        lambda: profile.purchase("blocked", gate_b.catalog_hash, PROOF_PAINTS[1]),
        "Gate-B purchase attempt is blocked",
        ProgressionBlocked,
    )
    check(profile.snapshot() == before_purchase, "blocked Gate-B purchase cannot mutate economic profile snapshot")
    expect_error(
        lambda: profile.purchase("blocked", gate_b.catalog_hash, PROOF_TRAIL),
        "blocked purchase identity cannot be reused with changed item",
        ProgressionConflict,
    )
    abort_commit = profile.commit_attempt(AttemptKey("gate-b", 1), aborted(terms["C01"]))
    check(abort_commit.credits_delta == 0, "C01 abort awards zero session Credits")
    check(profile.clear_set == frozenset(), "C01 abort creates no clear fact")
    check(not profile.entitlement_available, "C01 abort creates no paint issue")

    c01_typical = typical_receipts(terms)["C01"]
    delivered_commit = profile.commit_attempt(AttemptKey("gate-b", 2), c01_typical)
    check(delivered_commit.credits_delta == 61 and profile.available_balance == 61, "first C01 delivery commits its ordinary receipt")
    check(profile.clear_set == frozenset({"C01"}), "first C01 delivery records one exact clear")
    check(delivered_commit.entitlement_created and profile.entitlement_available, "first C01 delivery creates one free issue")
    duplicate = profile.commit_attempt(AttemptKey("gate-b", 2), c01_typical)
    check(duplicate.status == "DUPLICATE_NOOP" and duplicate.credits_delta == 0, "identical terminal replay is progression no-op")
    check(profile.available_balance == 61, "terminal replay cannot duplicate balance")
    expect_error(
        lambda: profile.commit_attempt(AttemptKey("gate-b", 2), delivered(terms["C01"], 1000, 0)),
        "altered terminal reuse raises ledger conflict",
        LedgerConflict,
    )
    repeat = profile.commit_attempt(AttemptKey("gate-b", 3), c01_typical)
    check(repeat.credits_delta == 61 and profile.available_balance == 122, "genuine C01 repeat receives full ordinary pay")
    check(repeat.new_clear is None and not repeat.entitlement_created, "repeat cannot duplicate clear or issue")
    forged_base = evaluate_receipt(
        replace(
            snapshot_from_terms(terms["C01"], terminal="DELIVERED", integrity_units=1000, elapsed_ms=0),
            base_credits=700_000_000,
        )
    )
    forged_profile = SessionProgression(gate_b, terms, "forged-receipt")
    expect_error(
        lambda: forged_profile.commit_attempt(AttemptKey("forged-receipt", 1), forged_base),
        "canonical forged-base receipt cannot mint Credits or clear",
        ProgressionConflict,
    )
    check(forged_profile.available_balance == 0 and forged_profile.clear_set == frozenset(), "forged-base rejection is progression atomic")
    forged_reference = evaluate_receipt(
        replace(
            snapshot_from_terms(terms["C01"], terminal="DELIVERED", integrity_units=1000, elapsed_ms=0),
            reference_ms=terms["C01"].reference_ms + 100,
        )
    )
    expect_error(
        lambda: forged_profile.commit_attempt(AttemptKey("forged-receipt", 1), forged_reference),
        "canonical forged-reference receipt cannot mint Credits or clear",
        ProgressionConflict,
    )
    check(forged_profile.available_balance == 0 and not forged_profile.entitlement_available, "forged-reference rejection creates no issue")

    preclaim = SessionProgression(gate_b, terms, "preclaim")
    expect_error(
        lambda: preclaim.claim_first_issue(FIRST_ISSUE_ID, gate_b.choice_set_hash, PROOF_PAINTS[0]),
        "free issue cannot be claimed before C01 delivery",
        ProgressionBlocked,
    )
    expect_error(
        lambda: profile.claim_first_issue("UNKNOWN", gate_b.choice_set_hash, PROOF_PAINTS[0]),
        "unknown entitlement rejected",
        ProgressionBlocked,
    )
    expect_error(
        lambda: profile.claim_first_issue(FIRST_ISSUE_ID, "a" * 64, PROOF_PAINTS[0]),
        "stale choice-set hash rejected",
        ProgressionConflict,
    )
    expect_error(
        lambda: profile.claim_first_issue(FIRST_ISSUE_ID, gate_b.choice_set_hash, "UNREGISTERED_PAINT"),
        "unregistered issue choice rejected",
        ProgressionBlocked,
    )
    balance_before_claim = profile.available_balance
    claim = profile.claim_first_issue(FIRST_ISSUE_ID, gate_b.choice_set_hash, PROOF_PAINTS[0])
    check(claim.status == "GRANTED_AND_EQUIPPED", "first valid issue grants and equips chosen paint")
    check(profile.available_balance == balance_before_claim, "free issue never debits Credits")
    check(PROOF_PAINTS[0] in profile.owned_paints and profile.equipped_paint == PROOF_PAINTS[0], "issued paint is owned and equipped atomically")
    same_claim = profile.claim_first_issue(FIRST_ISSUE_ID, gate_b.choice_set_hash, PROOF_PAINTS[0])
    check(same_claim.status == "DUPLICATE_NOOP", "same free-issue replay is idempotent")
    expect_error(
        lambda: profile.claim_first_issue(FIRST_ISSUE_ID, gate_b.choice_set_hash, PROOF_PAINTS[1]),
        "same entitlement cannot choose a second paint",
        ProgressionConflict,
    )
    check(profile.equip(DEFAULT_PAINT) == "EQUIPPED_PAINT" and profile.available_balance == balance_before_claim, "re-equipping District Standard is free")
    expect_error(lambda: profile.equip(PROOF_PAINTS[1]), "unowned cosmetic cannot be equipped", ProgressionBlocked)

    defer = SessionProgression(gate_b, terms, "defer")
    defer.commit_attempt(AttemptKey("defer", 1), c01_typical)
    check(defer.entitlement_available and defer.equipped_paint == DEFAULT_PAINT, "Keep Standard defers rather than consumes free issue")
    reset = profile.new_session("fresh-session")
    check(reset.snapshot()["available_balance"] == 0 and reset.clear_set == frozenset(), "new app session clears balance and clear ledger together")
    check(reset.owned_paints == frozenset({DEFAULT_PAINT}) and reset.owned_trails == frozenset({DEFAULT_TRAIL}), "new app session restores default-only ownership")
    check(not reset.entitlement_available and reset.issued_paint is None, "new app session clears issue claim state")
    check(profile.available_balance == balance_before_claim, "ordinary profile remains intact until explicit new epoch")
    expect_error(lambda: profile.new_session("gate-b"), "new session must use a distinct epoch", ProgressionConflict)

    floor = floor_receipts(terms)
    typical = typical_receipts(terms)
    learned = learned_receipts(terms)
    par = par_receipts(terms)
    check([floor[key].credits for key in ("C01", "C02", "C03")] == [35, 60, 85], "completion-floor cadence vector")
    check([typical[key].credits for key in ("C01", "C02", "C03")] == [61, 105, 149], "typical-learner cadence vector")
    check([learned[key].credits for key in ("C01", "C02", "C03")] == [68, 116, 165], "learned-clean cadence vector")
    check([par[key].credits for key in ("C01", "C02", "C03")] == [66, 113, 161], "clean-at-par cadence vector")

    post = SessionProgression(gate_c, terms, "post")
    check(post.paid_stock == {}, "post-Gate-B shelf starts locked without clear facts")
    post.commit_attempt(AttemptKey("post", 1), typical["C01"])
    post.claim_first_issue(FIRST_ISSUE_ID, gate_c.choice_set_hash, PROOF_PAINTS[0])
    check(post.paid_stock == {}, "one clear reveals no paid stock")
    post.commit_attempt(AttemptKey("post", 2), typical["C02"])
    check(post.paid_stock == {PROOF_PAINTS[1]: 80}, "two distinct clears reveal only unchosen proof paint")
    paint_purchase = post.purchase("paint-1", gate_c.catalog_hash, PROOF_PAINTS[1])
    check(paint_purchase.price == 80 and paint_purchase.available_balance == 86, "typical first two jobs afford remaining paint with room")
    post.commit_attempt(AttemptKey("post", 3), typical["C03"])
    check(post.paid_stock[PROOF_TRAIL] == 160, "three distinct clears reveal first trail")
    trail_purchase = post.purchase("trail-1", gate_c.catalog_hash, PROOF_TRAIL)
    check(trail_purchase.price == 160 and trail_purchase.available_balance == 75, "typical three-job chain buys paint and trail with seventy-five left")
    check(post.available_balance == post.total_awarded - 240, "balance equals ordinary awards minus literal committed prices")
    check(PROOF_PAINTS[1] in post.owned_paints and PROOF_TRAIL in post.owned_trails, "purchases atomically add exact ownership")
    check(post.equipped_paint == PROOF_PAINTS[1] and post.equipped_trail == PROOF_TRAIL, "successful purchases may equip without extra charge")
    duplicate_purchase = post.purchase("trail-1", gate_c.catalog_hash, PROOF_TRAIL)
    check(duplicate_purchase.status == "DUPLICATE_NOOP" and post.available_balance == 75, "same purchase replay cannot debit twice")
    already_owned = post.purchase("trail-2", gate_c.catalog_hash, PROOF_TRAIL)
    check(already_owned.status == "ALREADY_OWNED_NOOP" and post.available_balance == 75, "fresh owned-item request cannot debit again")
    expect_error(
        lambda: post.purchase("trail-2", gate_c.catalog_hash, PROOF_PAINTS[0]),
        "already-owned request identity cannot later buy changed content",
        ProgressionConflict,
    )
    expect_error(
        lambda: post.purchase("paint-1", gate_c.catalog_hash, PROOF_TRAIL),
        "purchase identity reuse with changed item conflicts",
        ProgressionConflict,
    )
    expect_error(
        lambda: post.purchase("stale", gate_b.catalog_hash, PROOF_TRAIL),
        "stale catalog purchase conflicts",
        ProgressionConflict,
    )
    expect_error(
        lambda: post.purchase("forged", gate_c.catalog_hash, "FORGED_ITEM"),
        "unknown item cannot debit profile",
        ProgressionBlocked,
    )
    expect_error(
        lambda: post.purchase("forged", gate_c.catalog_hash, PROOF_PAINTS[0]),
        "blocked unknown request identity cannot later buy changed content",
        ProgressionConflict,
    )
    check("client_price" not in inspect.signature(SessionProgression.purchase).parameters, "purchase request cannot supply its own price")
    expect_error(
        lambda: post.purchase("client-price", gate_c.catalog_hash, PROOF_TRAIL, client_price=1),
        "client-supplied price is structurally rejected",
        TypeError,
    )

    expected_stock = {PROOF_PAINTS[1]: 80, PROOF_TRAIL: 160}
    for index, order in enumerate(permutations(("C01", "C02", "C03")), start=1):
        candidate = SessionProgression(gate_c, terms, f"perm-{index}")
        commit_three(candidate, typical, order)
        check(candidate.paid_stock == expected_stock, f"clear permutation {index} yields identical final stock")
    check(gate_c.paid_stock(frozenset(("C01", "C04")), PROOF_PAINTS[0]) == {}, "future contract cannot substitute for frozen C02 predicate")
    check(gate_c.paid_stock(frozenset(("C01", "C02", "C04")), PROOF_PAINTS[0]) == {PROOF_PAINTS[1]: 80}, "future contract cannot substitute for frozen C03 predicate")

    low_quality = SessionProgression(gate_c, terms, "low-quality")
    commit_three(low_quality, floor)
    high_quality = SessionProgression(gate_c, terms, "high-quality")
    commit_three(high_quality, {key: delivered(value, 1000, 0) for key, value in terms.items()})
    check(low_quality.clear_set == high_quality.clear_set, "quality extremes create identical distinct-clear facts")
    check(low_quality.paid_stock == high_quality.paid_stock, "grade integrity and pace cannot alter stock availability")

    repeat_only = SessionProgression(gate_c, terms, "repeat-only")
    repeat_only.commit_attempt(AttemptKey("repeat-only", 1), typical["C01"])
    repeat_only.claim_first_issue(FIRST_ISSUE_ID, gate_c.choice_set_hash, PROOF_PAINTS[0])
    for sequence in range(2, 102):
        repeat_only.commit_attempt(AttemptKey("repeat-only", sequence), typical["C01"])
    check(repeat_only.clear_set == frozenset({"C01"}), "one hundred repeats cannot counterfeit breadth")
    check(repeat_only.paid_stock == {}, "one hundred shortest repeats reveal no later stock")
    check(repeat_only.total_awarded == 101 * 61, "repeats still receive full ordinary Credits")

    floor_profile = SessionProgression(gate_c, terms, "floor")
    floor_profile.commit_attempt(AttemptKey("floor", 1), floor["C01"])
    floor_profile.claim_first_issue(FIRST_ISSUE_ID, gate_c.choice_set_hash, PROOF_PAINTS[0])
    floor_profile.commit_attempt(AttemptKey("floor", 2), floor["C02"])
    floor_profile.purchase("floor-paint", gate_c.catalog_hash, PROOF_PAINTS[1])
    floor_profile.commit_attempt(AttemptKey("floor", 3), floor["C03"])
    check(floor_profile.available_balance == 100, "floor chain after paint has transparent one-hundred balance")
    floor_before = floor_profile.snapshot()
    expect_error(
        lambda: floor_profile.purchase("floor-trail", gate_c.catalog_hash, PROOF_TRAIL),
        "floor chain cannot overspend on trail",
        ProgressionBlocked,
    )
    check(floor_profile.snapshot() == floor_before, "insufficient purchase leaves every economic profile field unchanged")
    floor_profile.commit_attempt(AttemptKey("floor", 4), typical["C01"])
    expect_error(
        lambda: floor_profile.purchase("floor-trail", gate_c.catalog_hash, PROOF_TRAIL),
        "insufficient request ID remains terminal after later funding",
        ProgressionBlocked,
    )
    floor_trail = floor_profile.purchase("floor-trail-retry", gate_c.catalog_hash, PROOF_TRAIL)
    check(floor_trail.available_balance == 1, "one ordinary shortest repeat completes worst-chain shelf")

    clean_profile = SessionProgression(gate_c, terms, "clean")
    commit_three(clean_profile, learned)
    clean_profile.purchase("clean-paint", gate_c.catalog_hash, PROOF_PAINTS[1])
    clean_profile.purchase("clean-trail", gate_c.catalog_hash, PROOF_TRAIL)
    check(clean_profile.available_balance == 109, "learned-clean chain buys full paid shelf with one-oh-nine left")
    par_profile = SessionProgression(gate_c, terms, "par")
    commit_three(par_profile, par)
    par_profile.purchase("par-paint", gate_c.catalog_hash, PROOF_PAINTS[1])
    par_profile.purchase("par-trail", gate_c.catalog_hash, PROOF_TRAIL)
    check(par_profile.available_balance == 100, "clean-at-par chain buys full paid shelf with one hundred left")

    exact_paint_terms = terms_for((36_000, 36_000, 90_000))
    exact_paint_catalog = build_catalog(exact_paint_terms, phase=POST_GATE_B_CLEAR_SET)
    exact_paint = SessionProgression(exact_paint_catalog, exact_paint_terms, "exact-paint")
    exact_paint_floor = floor_receipts(exact_paint_terms)
    exact_paint.commit_attempt(AttemptKey("exact-paint", 1), exact_paint_floor["C01"])
    exact_paint.claim_first_issue(FIRST_ISSUE_ID, exact_paint_catalog.choice_set_hash, PROOF_PAINTS[0])
    exact_paint.commit_attempt(AttemptKey("exact-paint", 2), exact_paint_floor["C02"])
    check(exact_paint.available_balance == 80, "exact paint boundary setup reaches eighty Credits")
    check(exact_paint.purchase("exact", exact_paint_catalog.catalog_hash, PROOF_PAINTS[1]).available_balance == 0, "exact paint funds succeed to zero")

    below_paint_terms = terms_for((30_000, 40_800, 90_000))
    below_paint_catalog = build_catalog(below_paint_terms, phase=POST_GATE_B_CLEAR_SET)
    below_paint = SessionProgression(below_paint_catalog, below_paint_terms, "below-paint")
    below_paint_floor = floor_receipts(below_paint_terms)
    below_paint.commit_attempt(AttemptKey("below-paint", 1), below_paint_floor["C01"])
    below_paint.claim_first_issue(FIRST_ISSUE_ID, below_paint_catalog.choice_set_hash, PROOF_PAINTS[0])
    below_paint.commit_attempt(AttemptKey("below-paint", 2), below_paint_floor["C02"])
    check(below_paint.available_balance == 79, "one-below paint boundary setup reaches seventy-nine")
    below_snapshot = below_paint.snapshot()
    expect_error(lambda: below_paint.purchase("below", below_paint_catalog.catalog_hash, PROOF_PAINTS[1]), "one below paint price fails", ProgressionBlocked)
    check(below_paint.snapshot() == below_snapshot, "one-below paint failure is atomic")

    exact_trail_terms = terms_for((48_000, 48_000, 60_000))
    exact_trail_catalog = build_catalog(exact_trail_terms, phase=POST_GATE_B_CLEAR_SET)
    exact_trail = SessionProgression(exact_trail_catalog, exact_trail_terms, "exact-trail")
    commit_three(exact_trail, floor_receipts(exact_trail_terms))
    check(exact_trail.available_balance == 160, "exact trail boundary setup reaches one-sixty Credits")
    check(exact_trail.purchase("exact-trail", exact_trail_catalog.catalog_hash, PROOF_TRAIL).available_balance == 0, "exact trail funds succeed to zero")

    below_trail_terms = terms_for((48_000, 48_000, 58_800))
    below_trail_catalog = build_catalog(below_trail_terms, phase=POST_GATE_B_CLEAR_SET)
    below_trail = SessionProgression(below_trail_catalog, below_trail_terms, "below-trail")
    commit_three(below_trail, floor_receipts(below_trail_terms))
    check(below_trail.available_balance == 159, "one-below trail boundary setup reaches one-fifty-nine")
    below_trail_snapshot = below_trail.snapshot()
    expect_error(lambda: below_trail.purchase("below-trail", below_trail_catalog.catalog_hash, PROOF_TRAIL), "one below trail price fails", ProgressionBlocked)
    check(below_trail.snapshot() == below_trail_snapshot, "one-below trail failure is atomic")

    reset_post = post.new_session("post-reset")
    check(reset_post.total_awarded == 0 and reset_post.available_balance == 0, "full session reset clears award and purchase value together")
    check(reset_post.clear_set == frozenset() and reset_post.issued_paint is None, "full session reset clears breadth and issue state together")
    check(reset_post.owned_paints == frozenset({DEFAULT_PAINT}) and reset_post.owned_trails == frozenset({DEFAULT_TRAIL}), "full session reset clears paid ownership together")
    check(reset_post.equipped_paint == DEFAULT_PAINT and reset_post.equipped_trail == DEFAULT_TRAIL, "full session reset restores free equipment together")

    return {
        "selected_decision": "SESSION_CLEAR_LEDGER_REWARD_BRIDGE_V1",
        "gate_b": {
            "credits": "SESSION_ONLY_LABELLED",
            "first_clear_issue": FIRST_ISSUE_ID,
            "paid_purchase": "NOT AUTHORIZED",
            "reputation": "NOT PRESENT",
        },
        "post_gate_b_challenger": {
            "catalog": "CLEAR_SET_CATALOG_V1",
            "paint_price": price_terms.paint_price,
            "trail_price": price_terms.trail_price,
            "paint_reveal": ["C01", "C02"],
            "trail_reveal": ["C01", "C02", "C03"],
        },
        "illustrative_awards": {
            "completion_floor": [floor[key].credits for key in REQUIRED_ORDER],
            "typical_learner": [typical[key].credits for key in REQUIRED_ORDER],
            "learned_clean": [learned[key].credits for key in REQUIRED_ORDER],
            "clean_at_par": [par[key].credits for key in REQUIRED_ORDER],
        },
        "typical_balance_after_paid_paint_and_trail": 75,
        "floor_balance_after_paid_paint_then_trail_and_one_typical_short_repeat": 1,
        "human_authority": "NOT CLAIMED",
    }


REQUIRED_ORDER = ("C01", "C02", "C03")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    evidence = run()
    ids = [record["id"] for record in PASS_RECORDS]
    if len(ids) != len(set(ids)):
        raise AssertionError("iteration 05 check IDs must be unique")
    report = {
        "schema": "district_zero.p1b.iteration_05_progression_report.v1",
        "status": "PASS_WITH_POST_GATE_B_AND_NATIVE_FALSIFIERS_REMAINING",
        "decision": "SESSION_CLEAR_LEDGER_REWARD_BRIDGE_V1",
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
