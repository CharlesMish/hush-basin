#!/usr/bin/env python3
"""Deterministic Results/loadout and cosmetic-review vectors."""

from __future__ import annotations

import argparse
from dataclasses import replace
from decimal import Decimal
import hashlib
import inspect
import json
from pathlib import Path

from iteration_04_payout_model import AttemptKey, derive_contract_terms, evaluate_receipt, snapshot_from_terms
from iteration_05_progression_model import (
    DEFAULT_PAINT,
    DEFAULT_TRAIL,
    FIRST_ISSUE_ID,
    GATE_B_PROOF,
    POST_GATE_B_CLEAR_SET,
    PROOF_PAINTS,
    PROOF_TRAIL,
    ProgressionBlocked,
    ProgressionConflict,
    SessionProgression,
    build_catalog,
)
from iteration_07_reward_surface_model import (
    CARD_FREE_ISSUE,
    CARD_PAID_PAINT,
    CARD_PAID_TRAIL,
    DECISION_ID,
    FREE_ROAM,
    ISSUE_DRAWER,
    LOADOUT_DRAWER,
    PAINT_REVIEW_FRAMES,
    RESULTS,
    TRAIL_REVIEW_SCENES,
    WAITING_FOR_NEUTRAL,
    CosmeticReviewEvidence,
    RewardSurface,
    SurfaceBlocked,
    SurfaceConflict,
    build_result_view,
    cosmetic_review_status,
    loadout_cards,
    report_summary,
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


def terms_for() -> dict:
    return {
        contract_id: derive_contract_terms(contract_id=contract_id, learned_median_ms=median)
        for contract_id, median in zip(("C01", "C02", "C03"), (30_000, 60_000, 90_000))
    }


def delivered(terms, integrity_units=900, ratio=Decimal("1.25")):
    return evaluate_receipt(
        snapshot_from_terms(
            terms,
            terminal="DELIVERED",
            integrity_units=integrity_units,
            elapsed_ms=int(ratio * terms.reference_ms),
        )
    )


def aborted(terms):
    return evaluate_receipt(snapshot_from_terms(terms, terminal="ABORTED", integrity_units=1000, elapsed_ms=0))


def profile_for(phase: str, epoch: str):
    terms = terms_for()
    return terms, SessionProgression(build_catalog(terms, phase=phase), terms, epoch)


def evidence(category: str, **overrides) -> CosmeticReviewEvidence:
    required = frozenset(PAINT_REVIEW_FRAMES if category == "PAINT" else TRAIL_REVIEW_SCENES)
    values = {
        "candidate_id": f"TEST_{category}",
        "category": category,
        "static_contract_pass": True,
        "completed_native_cases": required,
        "movement_max_delta": Decimal("0"),
        "wall_occlusion_pass": True,
        "reduced_motion_pass": True,
        "added_frame_median_ms": Decimal("0.20"),
        "added_frame_p95_ms": Decimal("0.45"),
        "allocation_growth": 0,
        "owner_reads_as_reward": True,
        "owner_would_equip": True,
    }
    values.update(overrides)
    return CosmeticReviewEvidence(**values)


def run() -> dict:
    check(DECISION_ID == "RECEIPT_FIRST_SESSION_REWARD_SURFACE_V1", "decision identity is exact")
    check(len(PAINT_REVIEW_FRAMES) == 14 and len(set(PAINT_REVIEW_FRAMES)) == 14, "paint review requires fourteen unique native cases")
    check(len(TRAIL_REVIEW_SCENES) == 10 and len(set(TRAIL_REVIEW_SCENES)) == 10, "trail review requires ten unique native scenarios")
    check(cosmetic_review_status(evidence("PAINT")) == "FINALIST — NATIVE AND OWNER REVIEW PASS", "complete paint evidence may become finalist")
    check(cosmetic_review_status(evidence("TRAIL")) == "FINALIST — NATIVE AND OWNER REVIEW PASS", "complete trail evidence may become finalist")
    check(cosmetic_review_status(evidence("PAINT", static_contract_pass=False)) == "REJECTED — STATIC CONTRACT", "static paint failure rejects")
    check(cosmetic_review_status(evidence("TRAIL", static_contract_pass=False)) == "REJECTED — STATIC CONTRACT", "static trail failure rejects")
    check(cosmetic_review_status(evidence("PAINT", completed_native_cases=frozenset())) == "NOT TESTABLE — NATIVE REVIEW INCOMPLETE", "missing paint captures cannot be finalist")
    check(cosmetic_review_status(evidence("TRAIL", completed_native_cases=frozenset(TRAIL_REVIEW_SCENES[:-1]))) == "NOT TESTABLE — NATIVE REVIEW INCOMPLETE", "partial trail matrix cannot be finalist")
    check(cosmetic_review_status(evidence("PAINT", movement_max_delta=None)) == "REJECTED — MOVEMENT EQUIVALENCE", "missing paint movement proof rejects")
    check(cosmetic_review_status(evidence("TRAIL", movement_max_delta=Decimal("0.000001"))) == "REJECTED — MOVEMENT EQUIVALENCE", "nonzero trail movement delta rejects")
    check(cosmetic_review_status(evidence("TRAIL", wall_occlusion_pass=False)) == "REJECTED — OCCLUSION", "wall-through trail rejects")
    check(cosmetic_review_status(evidence("TRAIL", reduced_motion_pass=False)) == "REJECTED — REDUCED MOTION", "missing reduced-motion trail rejects")
    check(cosmetic_review_status(evidence("TRAIL", added_frame_median_ms=Decimal("0.251"))) == "REJECTED — PERFORMANCE", "trail above median frame budget rejects")
    check(cosmetic_review_status(evidence("TRAIL", added_frame_p95_ms=Decimal("0.551"))) == "REJECTED — PERFORMANCE", "trail above p95 frame budget rejects")
    check(cosmetic_review_status(evidence("TRAIL", allocation_growth=1)) == "REJECTED — RESOURCE GROWTH", "trail allocation growth rejects")
    check(cosmetic_review_status(evidence("PAINT", owner_reads_as_reward=None)) == "NOT TESTABLE — OWNER REVIEW INCOMPLETE", "automation cannot invent paint desirability")
    check(cosmetic_review_status(evidence("TRAIL", owner_would_equip=None)) == "NOT TESTABLE — OWNER REVIEW INCOMPLETE", "automation cannot invent trail equip desire")
    check(cosmetic_review_status(evidence("PAINT", owner_reads_as_reward=False)) == "REJECTED — OWNER DESIRABILITY", "non-reward paint fails owner gate")
    check(cosmetic_review_status(evidence("TRAIL", owner_would_equip=False)) == "REJECTED — OWNER DESIRABILITY", "unwanted trail fails owner gate")
    expect_error(lambda: cosmetic_review_status(replace(evidence("PAINT"), candidate_id="")), "empty candidate ID rejected")
    expect_error(lambda: cosmetic_review_status(replace(evidence("PAINT"), category="UPGRADE")), "mechanical upgrade cannot enter cosmetic review")
    expect_error(lambda: cosmetic_review_status(replace(evidence("PAINT"), static_contract_pass=1)), "truthy nonboolean static result rejected")
    expect_error(lambda: cosmetic_review_status(replace(evidence("TRAIL"), movement_max_delta=Decimal("NaN"))), "nonfinite movement evidence rejected")
    expect_error(lambda: cosmetic_review_status(replace(evidence("TRAIL"), added_frame_median_ms=Decimal("Infinity"))), "nonfinite performance evidence rejected")
    expect_error(lambda: cosmetic_review_status(replace(evidence("TRAIL"), added_frame_p95_ms=Decimal("-0.01"))), "negative performance evidence rejected")
    expect_error(lambda: cosmetic_review_status(replace(evidence("TRAIL"), allocation_growth=True)), "boolean allocation growth rejected")
    expect_error(lambda: cosmetic_review_status(replace(evidence("PAINT"), owner_would_equip=1)), "truthy nonboolean owner result rejected")

    terms_b, gate_b = profile_for(GATE_B_PROOF, "gate-b-ui")
    pre_stock: dict[str, int] = {}
    receipt_c01 = delivered(terms_b["C01"])
    commit_c01 = gate_b.commit_attempt(AttemptKey("gate-b-ui", 1), receipt_c01)
    view_c01 = build_result_view(receipt_c01, commit_c01, gate_b, grade_label="B", pre_paid_stock=pre_stock)
    check(view_c01.lines_sum == view_c01.credits, "result receipt lines reconcile exactly")
    check(view_c01.balance_after == 61, "result shows already-committed C01 balance")
    check(view_c01.reward_card is not None and view_c01.reward_card.card_id == CARD_FREE_ISSUE, "C01 result shows one free issue card")
    check("free" in view_c01.reward_card.detail.lower(), "free issue copy names zero-cost choice")
    check("SESSION PROTOTYPE" in view_c01.session_label, "result carries exact session prototype disclosure")

    presentation_ledger: set[str] = set()
    surface = RewardSurface(view_c01, gate_b, presented_card_events=presentation_ledger)
    check(surface.state == RESULTS and surface.default_focus == "CONTINUE", "Results opens receipt-first with Continue focused")
    check(surface.receipt_visible and surface.preview_item is None, "cosmetic drawer never auto-opens")
    original_snapshot = gate_b.snapshot()
    expect_error(lambda: surface.open_issue(fresh_edge=False), "held Results input cannot open issue", SurfaceBlocked)
    check(gate_b.snapshot() == original_snapshot, "blocked issue open cannot mutate profile")
    check(surface.open_issue(fresh_edge=True) == ISSUE_DRAWER, "fresh issue action opens finish drawer")
    check(surface.preview_item == DEFAULT_PAINT, "issue drawer begins on District Standard")
    preview_before = gate_b.snapshot()
    check(surface.preview(PROOF_PAINTS[0], fresh_edge=True) == "PREVIEW_ONLY_NO_PROFILE_MUTATION", "proof paint preview is presentation-only")
    check(gate_b.snapshot() == preview_before, "preview cannot claim equip or spend")
    expect_error(lambda: surface.preview("RAW_SPEED_UPGRADE", fresh_edge=True), "preview rejects item outside cosmetic catalog", SurfaceBlocked)
    check(surface.keep_standard(fresh_edge=True) == "ISSUE SAVED · DISTRICT STANDARD KEPT", "Keep Standard defers issue without modal")
    check(gate_b.entitlement_available and gate_b.equipped_paint == DEFAULT_PAINT, "Keep Standard preserves entitlement and default equip")
    check(surface.visible_reward_card is None, "deferred issue card is dismissed only for current Results")
    reopened = RewardSurface(view_c01, gate_b, presented_card_events=presentation_ledger)
    check(reopened.visible_reward_card is None, "same reward event cannot replay its ceremony")
    check(reopened.open_loadout(fresh_edge=True) == LOADOUT_DRAWER, "Gate-B deferred issue remains reachable in shallow loadout")
    gate_b_cards = loadout_cards(gate_b)
    check(tuple(card.item_id for card in gate_b_cards) == (DEFAULT_PAINT, PROOF_PAINTS[0], PROOF_PAINTS[1], DEFAULT_TRAIL), "Gate-B loadout contains defaults and exact free choice only")
    check(all(card.status != "LOCKED" and card.price == 0 for card in gate_b_cards), "Gate-B loadout has no paid or locked tease")
    gate_b_before_purchase = gate_b.snapshot()
    expect_error(lambda: reopened.purchase_and_equip("gate-b-forged-buy", PROOF_PAINTS[0], fresh_edge=True), "Gate-B drawer exposes no paid purchase action", SurfaceBlocked)
    check(gate_b.snapshot() == gate_b_before_purchase, "blocked Gate-B purchase action cannot mutate profile")
    reopened.close_drawer(fresh_edge=True)
    check(surface.consume_reset() == "RESET_CONSUMED_NO_PROFILE_OR_R7_MUTATION", "Results reset is consumed")
    check(gate_b.snapshot() == preview_before, "modal reset cannot mutate R7-facing profile")
    expect_error(lambda: surface.continue_at_destination(fresh_edge=False), "held Continue cannot exit Results", SurfaceBlocked)
    profile_before_continue = gate_b.snapshot()
    receipt_before_continue = surface.result
    check(surface.continue_at_destination(fresh_edge=True) == WAITING_FOR_NEUTRAL, "fresh Continue enters neutral barrier")
    check(surface.neutral_sample(all_actions_neutral=True) == WAITING_FOR_NEUTRAL, "one neutral frame cannot resume")
    check(surface.neutral_sample(all_actions_neutral=False) == WAITING_FOR_NEUTRAL, "nonneutral sample resets release streak")
    check(surface.neutral_sample(all_actions_neutral=True) == WAITING_FOR_NEUTRAL, "neutral streak restarts at one")
    check(surface.neutral_sample(all_actions_neutral=True) == FREE_ROAM, "two neutral frames resume free roam")
    check(gate_b.snapshot() == profile_before_continue and surface.result == receipt_before_continue, "Continue changes neither profile nor receipt")
    expect_error(lambda: surface.consume_reset(), "reset returns to R7 ownership only after free roam", SurfaceBlocked)

    terms_claim, gate_b_claim = profile_for(GATE_B_PROOF, "gate-b-claim")
    receipt_claim = delivered(terms_claim["C01"])
    commit_claim = gate_b_claim.commit_attempt(AttemptKey("gate-b-claim", 1), receipt_claim)
    view_claim = build_result_view(receipt_claim, commit_claim, gate_b_claim, grade_label="B", pre_paid_stock={})
    claim_surface = RewardSurface(view_claim, gate_b_claim)
    claim_surface.open_issue(fresh_edge=True)
    claim_balance = gate_b_claim.available_balance
    claim_commit = claim_surface.claim_and_equip(PROOF_PAINTS[0], fresh_edge=True)
    check(claim_commit.status == "GRANTED_AND_EQUIPPED", "free issue claims and equips atomically")
    check(gate_b_claim.available_balance == claim_balance, "free issue never debits session Credits")
    check(PROOF_PAINTS[0] in gate_b_claim.owned_paints and gate_b_claim.equipped_paint == PROOF_PAINTS[0], "claimed proof paint is owned and equipped")
    check(claim_surface.state == RESULTS and claim_surface.visible_reward_card is None, "claim returns to same receipt without another card")
    check(claim_surface.result == view_claim, "claim cannot rewrite committed receipt")

    terms_defer, gate_b_defer = profile_for(GATE_B_PROOF, "gate-b-defer")
    receipt_defer = delivered(terms_defer["C01"])
    commit_defer = gate_b_defer.commit_attempt(AttemptKey("gate-b-defer", 1), receipt_defer)
    view_defer = build_result_view(receipt_defer, commit_defer, gate_b_defer, grade_label="B", pre_paid_stock={})
    defer_events: set[str] = set()
    defer_surface = RewardSurface(view_defer, gate_b_defer, presented_card_events=defer_events)
    defer_surface.open_issue(fresh_edge=True)
    defer_surface.keep_standard(fresh_edge=True)
    later_surface = RewardSurface(view_defer, gate_b_defer, presented_card_events=defer_events)
    later_surface.open_loadout(fresh_edge=True)
    deferred_claim = later_surface.claim_and_equip(PROOF_PAINTS[1], fresh_edge=True)
    check(deferred_claim.status == "GRANTED_AND_EQUIPPED", "deferred issue can be claimed later from shallow loadout")
    check(not gate_b_defer.entitlement_available and gate_b_defer.equipped_paint == PROOF_PAINTS[1], "late claim consumes one issue and equips one paint")
    check(tuple(card.item_id for card in loadout_cards(gate_b_defer)) == (DEFAULT_PAINT, PROOF_PAINTS[1], DEFAULT_TRAIL), "Gate-B hides unchosen paint after issue claim")

    terms_c, gate_c = profile_for(POST_GATE_B_CLEAR_SET, "gate-c-ui")
    c01 = delivered(terms_c["C01"])
    pre = dict(gate_c.paid_stock)
    c01_commit = gate_c.commit_attempt(AttemptKey("gate-c-ui", 1), c01)
    gate_c.claim_first_issue(FIRST_ISSUE_ID, gate_c.catalog.choice_set_hash, PROOF_PAINTS[0])
    c02 = delivered(terms_c["C02"])
    pre_c02 = dict(gate_c.paid_stock)
    c02_commit = gate_c.commit_attempt(AttemptKey("gate-c-ui", 2), c02)
    c02_view = build_result_view(c02, c02_commit, gate_c, grade_label="B", pre_paid_stock=pre_c02)
    check(c02_view.reward_card is not None and c02_view.reward_card.card_id == CARD_PAID_PAINT, "C02 reveals at most one paid paint card")
    c02_surface = RewardSurface(c02_view, gate_c)
    check(c02_surface.open_loadout(fresh_edge=True) == LOADOUT_DRAWER, "post-gate Results may open optional loadout")
    cards = loadout_cards(gate_c)
    check(tuple(card.item_id for card in cards) == (DEFAULT_PAINT, PROOF_PAINTS[0], PROOF_PAINTS[1], DEFAULT_TRAIL, PROOF_TRAIL), "loadout card order is stable")
    paid_paint_card = next(card for card in cards if card.item_id == PROOF_PAINTS[1])
    check(paid_paint_card.status == "BUY_AND_EQUIP" and paid_paint_card.price == 80, "revealed paint shows exact literal Buy and Equip action")
    check("resets when app closes" in paid_paint_card.disclosure, "paid paint repeats session-loss disclosure")
    check(c02_surface.default_focus == "CONTINUE", "opening loadout never changes Results default action")
    c02_receipt_frozen = c02_surface.result
    purchase = c02_surface.purchase_and_equip("paint-buy-1", PROOF_PAINTS[1], fresh_edge=True)
    check(purchase.status == "PURCHASED" and purchase.price == 80, "fresh exact paint purchase commits once")
    check(gate_c.equipped_paint == PROOF_PAINTS[1] and gate_c.available_balance == 86, "paint purchase equips and reconciles balance")
    check(c02_surface.result == c02_receipt_frozen, "purchase cannot rewrite receipt")
    duplicate = c02_surface.purchase_and_equip("paint-buy-1", PROOF_PAINTS[1], fresh_edge=True)
    check(duplicate.status == "DUPLICATE_NOOP" and gate_c.available_balance == 86, "purchase replay cannot debit twice")
    expect_error(lambda: c02_surface.purchase_and_equip("paint-buy-1", PROOF_TRAIL, fresh_edge=True), "altered purchase identity conflicts", ProgressionConflict)
    expect_error(lambda: c02_surface.purchase_and_equip("held-purchase", PROOF_TRAIL, fresh_edge=False), "held input cannot purchase", SurfaceBlocked)
    check(c02_surface.close_drawer(fresh_edge=True) == RESULTS, "loadout closes back to same Results")

    c03 = delivered(terms_c["C03"])
    pre_c03 = dict(gate_c.paid_stock)
    c03_commit = gate_c.commit_attempt(AttemptKey("gate-c-ui", 3), c03)
    c03_view = build_result_view(c03, c03_commit, gate_c, grade_label="B", pre_paid_stock=pre_c03)
    check(c03_view.reward_card is not None and c03_view.reward_card.card_id == CARD_PAID_TRAIL, "C03 reveals at most one trail card")
    trail_surface = RewardSurface(c03_view, gate_c)
    trail_surface.open_loadout(fresh_edge=True)
    trail_card = next(card for card in loadout_cards(gate_c) if card.item_id == PROOF_TRAIL)
    check(trail_card.status == "BUY_AND_EQUIP" and trail_card.price == 160, "trail card shows exact literal price")
    trail_purchase = trail_surface.purchase_and_equip("trail-buy-1", PROOF_TRAIL, fresh_edge=True)
    check(trail_purchase.status == "PURCHASED" and gate_c.equipped_trail == PROOF_TRAIL, "trail purchase equips atomically")
    check(gate_c.available_balance == 75, "typical chain paint plus trail leaves seventy-five Credits")
    check(trail_surface.result == c03_view, "trail purchase leaves receipt immutable")
    check(trail_surface.equip_owned(DEFAULT_TRAIL, fresh_edge=True) == "EQUIPPED_TRAIL", "Trail Off remains freely equipable")
    check(gate_c.available_balance == 75, "free equip cannot change balance")

    terms_floor, floor_profile = profile_for(POST_GATE_B_CLEAR_SET, "floor-ui")
    floor_receipts = {
        key: evaluate_receipt(snapshot_from_terms(value, terminal="DELIVERED", integrity_units=0, elapsed_ms=value.reference_ms * 3))
        for key, value in terms_floor.items()
    }
    floor_profile.commit_attempt(AttemptKey("floor-ui", 1), floor_receipts["C01"])
    floor_profile.claim_first_issue(FIRST_ISSUE_ID, floor_profile.catalog.choice_set_hash, PROOF_PAINTS[0])
    floor_profile.commit_attempt(AttemptKey("floor-ui", 2), floor_receipts["C02"])
    floor_profile.purchase("floor-paint", floor_profile.catalog.catalog_hash, PROOF_PAINTS[1])
    floor_c03_pre = dict(floor_profile.paid_stock)
    floor_c03_commit = floor_profile.commit_attempt(AttemptKey("floor-ui", 3), floor_receipts["C03"])
    floor_view = build_result_view(floor_receipts["C03"], floor_c03_commit, floor_profile, grade_label="D", pre_paid_stock=floor_c03_pre)
    floor_surface = RewardSurface(floor_view, floor_profile)
    floor_surface.open_loadout(fresh_edge=True)
    floor_trail = next(card for card in loadout_cards(floor_profile) if card.item_id == PROOF_TRAIL)
    check(floor_profile.available_balance == 100, "completion-floor chain after paint retains one hundred Credits")
    check(floor_trail.status == "NEED_SESSION_CREDITS" and "Need 60 more" in floor_trail.disclosure, "shortfall copy is exact and non-punitive")
    floor_before = floor_profile.snapshot()
    expect_error(lambda: floor_surface.purchase_and_equip("floor-trail", PROOF_TRAIL, fresh_edge=True), "insufficient trail purchase is blocked", ProgressionBlocked)
    check(floor_profile.snapshot() == floor_before, "insufficient purchase cannot mutate profile")

    terms_lock, locked_profile = profile_for(POST_GATE_B_CLEAR_SET, "locked-ui")
    locked_receipt = delivered(terms_lock["C01"])
    locked_commit = locked_profile.commit_attempt(AttemptKey("locked-ui", 1), locked_receipt)
    locked_view = build_result_view(locked_receipt, locked_commit, locked_profile, grade_label="B", pre_paid_stock={})
    locked_cards = loadout_cards(locked_profile)
    check(sum(card.status == "FREE_ISSUE" for card in locked_cards) == 2, "pending issue shows exactly the two frozen free choices")
    check(next(card for card in locked_cards if card.item_id == PROOF_TRAIL).disclosure == "Clear C01 + C02 + C03", "locked trail names exact clear predicate")
    check(all("GRADE" not in card.disclosure.upper() and "REP" not in card.disclosure.upper() for card in locked_cards), "stock copy excludes grade and Reputation")

    aborted_receipt = aborted(terms_lock["C02"])
    aborted_commit = locked_profile.commit_attempt(AttemptKey("locked-ui", 2), aborted_receipt)
    aborted_view = build_result_view(aborted_receipt, aborted_commit, locked_profile, grade_label="ABORTED", pre_paid_stock=dict(locked_profile.paid_stock))
    check(aborted_view.credits == 0 and aborted_view.reward_card is None and locked_profile.entitlement_available, "abort creates no reward card while pending issue remains separately available")

    forged_view = replace(view_c01, balance_after=view_c01.balance_after + 1)
    expect_error(lambda: RewardSurface(forged_view, gate_b), "forged result balance rejected", SurfaceConflict)
    bad_lines = replace(view_c01, pace_line=view_c01.pace_line + 1)
    expect_error(lambda: bad_lines.validate(), "mismatched receipt lines rejected", SurfaceConflict)
    bad_grade = replace(view_c01, grade_label="LEGENDARY")
    expect_error(lambda: bad_grade.validate(), "unregistered grade label rejected", SurfaceConflict)
    bad_fingerprint = replace(view_c01, receipt_fingerprint="z" * 64)
    expect_error(lambda: bad_fingerprint.validate(), "nonhex receipt fingerprint rejected", SurfaceConflict)
    bad_terminal = replace(view_c01, terminal="S", grade_label="S")
    expect_error(lambda: bad_terminal.validate(), "unregistered terminal rejected", SurfaceConflict)
    check("client_price" not in inspect.signature(RewardSurface.purchase_and_equip).parameters, "UI purchase accepts no client price")
    check("grade" not in inspect.signature(loadout_cards).parameters, "loadout availability accepts no grade")
    check("distance" not in inspect.signature(loadout_cards).parameters, "loadout availability accepts no distance")
    check("route" not in inspect.signature(loadout_cards).parameters, "loadout availability accepts no route")

    summary = report_summary()
    check(summary["default_focus"] == "CONTINUE", "report preserves Continue priority")
    check(summary["gate_b_surface"] == "FREE FINISH ISSUE + SHALLOW FREE-ONLY LOADOUT — NO PAID SHOP OR TRAIL STOCK", "report keeps Gate-B surface bounded")
    check(summary["post_gate_surface"].endswith("NOT AUTHORIZED"), "report does not authorize paid shelf")
    check(summary["product_source_modified"] is False, "report records no product source modification")
    check(summary["human_world_gate"] == "NOT PERFORMED", "report records no Human World Gate")
    check(summary["P1B_product_implementation"] == "NOT STARTED", "report records no P1B implementation")

    summary["checks"] = {
        "passed": len(PASS_RECORDS),
        "failed": 0,
        "total": len(PASS_RECORDS),
        "status": "PASS WITH NATIVE AND OWNER COSMETIC GATES REMAINING",
        "records": PASS_RECORDS,
    }
    return summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    report = run()
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(f"RESULT {report['checks']['passed']}/{report['checks']['total']} PASS WITH NATIVE AND OWNER COSMETIC GATES REMAINING")
    print(f"REPORT_SHA256 {hashlib.sha256(args.report.read_bytes()).hexdigest()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
