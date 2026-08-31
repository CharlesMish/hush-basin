#!/usr/bin/env python3
"""Pure Results/loadout and cosmetic-review model for iteration 07.

The model consumes already-committed receipts and the iteration-05 session
profile.  It cannot calculate money, steer the craft, or make a cosmetic
beautiful.  It proves a receipt-first optional UI, fresh-edge mutations, and a
strict evidence boundary between static concepts and native/owner selection.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Iterable, Mapping

from iteration_04_payout_model import Receipt
from iteration_05_progression_model import (
    DEFAULT_PAINT,
    DEFAULT_TRAIL,
    FIRST_ISSUE_ID,
    POST_GATE_B_CLEAR_SET,
    PROOF_PAINTS,
    PROOF_TRAIL,
    SESSION_LABEL,
    ClaimCommit,
    ProgressionCommit,
    ProgressionBlocked,
    ProgressionCatalog,
    PurchaseCommit,
    SessionProgression,
)


DECISION_ID = "RECEIPT_FIRST_SESSION_REWARD_SURFACE_V1"

RESULTS = "RESULTS"
ISSUE_DRAWER = "ISSUE_DRAWER"
LOADOUT_DRAWER = "LOADOUT_DRAWER"
WAITING_FOR_NEUTRAL = "WAITING_FOR_NEUTRAL"
FREE_ROAM = "FREE_ROAM"

CARD_FREE_ISSUE = "FREE_PAINT_ISSUE"
CARD_PAID_PAINT = "PAID_PAINT_STOCK"
CARD_PAID_TRAIL = "PAID_TRAIL_STOCK"

GRADE_LABELS = frozenset({"S", "A", "B", "C", "D", "ABORTED", "OBSERVER_INVALID"})

PAINT_REVIEW_FRAMES = (
    "SPREAD_BRIGHT",
    "SPREAD_DARK",
    "MIDPOINT_BRIGHT",
    "MIDPOINT_DARK",
    "DRIVE_BRIGHT",
    "DRIVE_DARK",
    "ORANGE_CUE_BRIGHT",
    "ORANGE_CUE_DARK",
    "CYAN_CUE_BRIGHT",
    "CYAN_CUE_DARK",
    "AMBER_CUE_BRIGHT",
    "AMBER_CUE_DARK",
    "RED_CUE_BRIGHT",
    "RED_CUE_DARK",
)

TRAIL_REVIEW_SCENES = (
    "STRAIGHT_DRIVE",
    "LONG_DRIFT",
    "BRAKE_AND_SETTLE",
    "HOP_AND_LANDING",
    "WALL_OCCLUSION",
    "PAUSE_FREEZE",
    "RESET_CLEAR",
    "RELOCATION_CLEAR",
    "REDUCED_MOTION",
    "MAX_SURFACE_SPRAY_SOAK",
)


class SurfaceConflict(ValueError):
    """A record or action differs from the frozen Results authority."""


class SurfaceBlocked(ValueError):
    """A valid UI action is unavailable and must not mutate state."""


@dataclass(frozen=True)
class RewardCard:
    event_id: str
    card_id: str
    item_id: str | None
    headline: str
    detail: str


def reward_card_for(
    profile: SessionProgression,
    commit: ProgressionCommit,
    pre_paid_stock: Mapping[str, int],
) -> RewardCard | None:
    """Select at most one stable card; issue > paint stock > trail stock."""
    if commit.entitlement_created:
        return RewardCard(
            f"{commit.attempt_id}:{CARD_FREE_ISSUE}",
            CARD_FREE_ISSUE,
            None,
            "FREE FINISH CHOICE READY",
            "C01 FIRST CLEAR · FREE · SESSION ONLY",
        )
    if commit.status == "DUPLICATE_NOOP":
        return None
    new_stock = set(profile.paid_stock) - set(pre_paid_stock)
    for paint_id in PROOF_PAINTS:
        if paint_id in new_stock:
            return RewardCard(
                f"{commit.attempt_id}:{CARD_PAID_PAINT}:{paint_id}",
                CARD_PAID_PAINT,
                paint_id,
                "FINISH NOW AVAILABLE TO BUY",
                f"{profile.paid_stock[paint_id]} SESSION CREDITS · resets when app closes",
            )
    if PROOF_TRAIL in new_stock:
        return RewardCard(
            f"{commit.attempt_id}:{CARD_PAID_TRAIL}:{PROOF_TRAIL}",
            CARD_PAID_TRAIL,
            PROOF_TRAIL,
            "TRAIL NOW AVAILABLE TO BUY",
            f"{profile.paid_stock[PROOF_TRAIL]} SESSION CREDITS · resets when app closes",
        )
    return None


@dataclass(frozen=True)
class CommittedResultView:
    attempt_id: str
    receipt_fingerprint: str
    terminal: str
    grade_label: str
    credits: int
    delivery_line: int
    condition_line: int
    pace_line: int
    integrity_units: int
    elapsed_ms: int
    reference_ms: int
    balance_after: int
    session_label: str
    reward_card: RewardCard | None

    @property
    def lines_sum(self) -> int:
        return self.delivery_line + self.condition_line + self.pace_line

    def validate(self) -> None:
        if not self.attempt_id or not self.attempt_id.strip():
            raise SurfaceConflict("result attempt ID must be nonempty")
        if len(self.receipt_fingerprint) != 64 or any(char not in "0123456789abcdef" for char in self.receipt_fingerprint):
            raise SurfaceConflict("result must bind a receipt SHA-256")
        if self.terminal not in {"DELIVERED", "ABORTED", "OBSERVER_INVALID"}:
            raise SurfaceConflict("result terminal is not registered")
        if self.grade_label not in GRADE_LABELS:
            raise SurfaceConflict("result grade label is not registered")
        if self.terminal == "DELIVERED" and self.grade_label not in {"S", "A", "B", "C", "D"}:
            raise SurfaceConflict("delivered result requires a delivery grade")
        if self.terminal != "DELIVERED" and self.grade_label != self.terminal:
            raise SurfaceConflict("non-delivery result label must match terminal")
        if self.lines_sum != self.credits:
            raise SurfaceConflict("three receipt lines must sum to committed Credits")
        if self.balance_after < 0:
            raise SurfaceConflict("available balance cannot be negative")
        if self.session_label != SESSION_LABEL:
            raise SurfaceConflict("session-loss disclosure must be exact")


def build_result_view(
    receipt: Receipt,
    commit: ProgressionCommit,
    profile: SessionProgression,
    *,
    grade_label: str,
    pre_paid_stock: Mapping[str, int],
) -> CommittedResultView:
    receipt.validate_canonical()
    if commit.attempt_id == "" or commit.attempt_id is None:
        raise SurfaceConflict("progression commit lacks attempt identity")
    if commit.available_balance != profile.available_balance:
        raise SurfaceConflict("result balance differs from committed profile")
    if commit.credits_delta not in {0, receipt.credits}:
        raise SurfaceConflict("result commit delta differs from receipt")
    result = CommittedResultView(
        commit.attempt_id,
        receipt.fingerprint,
        receipt.terminal,
        grade_label,
        receipt.credits,
        receipt.delivery_line,
        receipt.condition_line,
        receipt.pace_line,
        receipt.integrity_units,
        receipt.elapsed_ms,
        receipt.reference_ms,
        profile.available_balance,
        SESSION_LABEL,
        reward_card_for(profile, commit, pre_paid_stock),
    )
    result.validate()
    return result


@dataclass(frozen=True)
class LoadoutCard:
    item_id: str
    category: str
    status: str
    price: int
    disclosure: str
    equipped: bool


def loadout_cards(profile: SessionProgression) -> tuple[LoadoutCard, ...]:
    """Return one stable, non-rotating shelf; no grade/Rep/routing inputs."""
    cards: list[LoadoutCard] = [
        LoadoutCard(DEFAULT_PAINT, "PAINT", "OWNED", 0, "Always free", profile.equipped_paint == DEFAULT_PAINT)
    ]
    visible_paints = PROOF_PAINTS
    if profile.catalog.phase != POST_GATE_B_CLEAR_SET and not profile.entitlement_available:
        visible_paints = tuple(paint_id for paint_id in PROOF_PAINTS if paint_id in profile.owned_paints)
    for paint_id in visible_paints:
        if paint_id in profile.owned_paints:
            status = "OWNED"
            price = 0
            disclosure = "Owned in this session"
        elif profile.entitlement_available:
            status = "FREE_ISSUE"
            price = 0
            disclosure = "One free issue · choosing consumes the issue"
        elif paint_id in profile.paid_stock:
            price = profile.paid_stock[paint_id]
            status = "BUY_AND_EQUIP" if profile.available_balance >= price else "NEED_SESSION_CREDITS"
            short = max(0, price - profile.available_balance)
            disclosure = (
                f"{price} SESSION CREDITS · resets when app closes"
                if short == 0
                else f"Need {short} more SESSION CREDITS · resets when app closes"
            )
        else:
            status = "LOCKED"
            price = profile.catalog.price_terms.paint_price
            disclosure = "Clear C01 + C02 · free issue claimed"
        cards.append(LoadoutCard(paint_id, "PAINT", status, price, disclosure, profile.equipped_paint == paint_id))
    cards.append(LoadoutCard(DEFAULT_TRAIL, "TRAIL", "OWNED", 0, "Always free", profile.equipped_trail == DEFAULT_TRAIL))
    if profile.catalog.phase != POST_GATE_B_CLEAR_SET:
        return tuple(cards)
    if PROOF_TRAIL in profile.owned_trails:
        trail_status = "OWNED"
        trail_price = 0
        trail_disclosure = "Owned in this session"
    elif PROOF_TRAIL in profile.paid_stock:
        trail_price = profile.paid_stock[PROOF_TRAIL]
        trail_status = "BUY_AND_EQUIP" if profile.available_balance >= trail_price else "NEED_SESSION_CREDITS"
        trail_short = max(0, trail_price - profile.available_balance)
        trail_disclosure = (
            f"{trail_price} SESSION CREDITS · resets when app closes"
            if trail_short == 0
            else f"Need {trail_short} more SESSION CREDITS · resets when app closes"
        )
    else:
        trail_status = "LOCKED"
        trail_price = profile.catalog.price_terms.trail_price
        trail_disclosure = "Clear C01 + C02 + C03"
    cards.append(
        LoadoutCard(
            PROOF_TRAIL,
            "TRAIL",
            trail_status,
            trail_price,
            trail_disclosure,
            profile.equipped_trail == PROOF_TRAIL,
        )
    )
    return tuple(cards)


class RewardSurface:
    """Paused receipt-first UI; every mutation requires one fresh edge."""

    def __init__(
        self,
        result: CommittedResultView,
        profile: SessionProgression,
        *,
        presented_card_events: set[str] | None = None,
    ) -> None:
        result.validate()
        if result.balance_after != profile.available_balance:
            raise SurfaceConflict("surface profile differs from committed result")
        self.result = result
        self.profile = profile
        self.state = RESULTS
        self.default_focus = "CONTINUE"
        self.receipt_visible = True
        self.preview_item: str | None = None
        self.confirmation: str | None = None
        self._dismissed_card = False
        self._neutral_frames = 0
        self._presented_card_events = presented_card_events if presented_card_events is not None else set()
        if result.reward_card is not None:
            if result.reward_card.event_id in self._presented_card_events:
                self._dismissed_card = True
            else:
                self._presented_card_events.add(result.reward_card.event_id)

    @property
    def visible_reward_card(self) -> RewardCard | None:
        return None if self._dismissed_card else self.result.reward_card

    def _fresh(self, fresh_edge: bool) -> None:
        if not isinstance(fresh_edge, bool) or not fresh_edge:
            raise SurfaceBlocked("action requires a fresh released input edge")

    def _require_state(self, expected: str) -> None:
        if self.state != expected:
            raise SurfaceConflict(f"action requires {expected}")

    def open_issue(self, *, fresh_edge: bool) -> str:
        self._require_state(RESULTS)
        self._fresh(fresh_edge)
        if self.visible_reward_card is None or self.visible_reward_card.card_id != CARD_FREE_ISSUE:
            raise SurfaceBlocked("no free issue card is available on this result")
        if not self.profile.entitlement_available:
            raise SurfaceConflict("result issue card differs from profile entitlement")
        self.state = ISSUE_DRAWER
        self.preview_item = DEFAULT_PAINT
        return self.state

    def open_loadout(self, *, fresh_edge: bool) -> str:
        self._require_state(RESULTS)
        self._fresh(fresh_edge)
        self.state = LOADOUT_DRAWER
        self.preview_item = self.profile.equipped_paint
        return self.state

    def preview(self, item_id: str, *, fresh_edge: bool) -> str:
        if self.state not in {ISSUE_DRAWER, LOADOUT_DRAWER}:
            raise SurfaceConflict("preview requires an open cosmetic drawer")
        self._fresh(fresh_edge)
        allowed = {card.item_id for card in loadout_cards(self.profile)}
        if item_id not in allowed:
            raise SurfaceBlocked("preview item is outside the frozen cosmetic catalog")
        self.preview_item = item_id
        return "PREVIEW_ONLY_NO_PROFILE_MUTATION"

    def keep_standard(self, *, fresh_edge: bool) -> str:
        self._require_state(ISSUE_DRAWER)
        self._fresh(fresh_edge)
        self.state = RESULTS
        self.preview_item = None
        self._dismissed_card = True
        self.confirmation = "ISSUE SAVED · DISTRICT STANDARD KEPT"
        return self.confirmation

    def claim_and_equip(self, paint_id: str, *, fresh_edge: bool) -> ClaimCommit:
        if self.state not in {ISSUE_DRAWER, LOADOUT_DRAWER}:
            raise SurfaceConflict("claim requires an open cosmetic drawer")
        self._fresh(fresh_edge)
        before_balance = self.profile.available_balance
        commit = self.profile.claim_first_issue(FIRST_ISSUE_ID, self.profile.catalog.choice_set_hash, paint_id)
        if self.profile.available_balance != before_balance:
            raise SurfaceConflict("free issue changed Credit balance")
        self.state = RESULTS
        self.preview_item = None
        self._dismissed_card = True
        self.confirmation = f"{paint_id} · CLAIMED AND EQUIPPED"
        return commit

    def purchase_and_equip(self, purchase_id: str, item_id: str, *, fresh_edge: bool) -> PurchaseCommit:
        self._require_state(LOADOUT_DRAWER)
        self._fresh(fresh_edge)
        if self.profile.catalog.phase != POST_GATE_B_CLEAR_SET:
            raise SurfaceBlocked("Gate-B proof has no paid purchase action")
        commit = self.profile.purchase(purchase_id, self.profile.catalog.catalog_hash, item_id, equip=True)
        self.preview_item = item_id
        self.confirmation = f"{item_id} · PURCHASED AND EQUIPPED"
        return commit

    def equip_owned(self, item_id: str, *, fresh_edge: bool) -> str:
        self._require_state(LOADOUT_DRAWER)
        self._fresh(fresh_edge)
        result = self.profile.equip(item_id)
        self.preview_item = item_id
        self.confirmation = f"{item_id} · EQUIPPED"
        return result

    def close_drawer(self, *, fresh_edge: bool) -> str:
        if self.state not in {ISSUE_DRAWER, LOADOUT_DRAWER}:
            raise SurfaceConflict("close requires an open drawer")
        self._fresh(fresh_edge)
        self.state = RESULTS
        self.preview_item = None
        return self.state

    def continue_at_destination(self, *, fresh_edge: bool) -> str:
        self._require_state(RESULTS)
        self._fresh(fresh_edge)
        self.state = WAITING_FOR_NEUTRAL
        self._neutral_frames = 0
        return self.state

    def neutral_sample(self, *, all_actions_neutral: bool) -> str:
        self._require_state(WAITING_FOR_NEUTRAL)
        if not isinstance(all_actions_neutral, bool):
            raise SurfaceConflict("neutral sample must be boolean")
        if all_actions_neutral:
            self._neutral_frames += 1
        else:
            self._neutral_frames = 0
        if self._neutral_frames >= 2:
            self.state = FREE_ROAM
        return self.state

    def consume_reset(self) -> str:
        if self.state not in {RESULTS, ISSUE_DRAWER, LOADOUT_DRAWER, WAITING_FOR_NEUTRAL}:
            raise SurfaceBlocked("reset is no longer modal-owned")
        return "RESET_CONSUMED_NO_PROFILE_OR_R7_MUTATION"


@dataclass(frozen=True)
class CosmeticReviewEvidence:
    candidate_id: str
    category: str
    static_contract_pass: bool
    completed_native_cases: frozenset[str]
    movement_max_delta: Decimal | None
    wall_occlusion_pass: bool | None
    reduced_motion_pass: bool | None
    added_frame_median_ms: Decimal | None
    added_frame_p95_ms: Decimal | None
    allocation_growth: int | None
    owner_reads_as_reward: bool | None
    owner_would_equip: bool | None


def cosmetic_review_status(evidence: CosmeticReviewEvidence) -> str:
    if not evidence.candidate_id or not evidence.candidate_id.strip():
        raise ValueError("candidate ID must be nonempty")
    if evidence.category not in {"PAINT", "TRAIL"}:
        raise ValueError("cosmetic category must be PAINT or TRAIL")
    if not isinstance(evidence.static_contract_pass, bool):
        raise ValueError("static contract result must be boolean")
    if not evidence.static_contract_pass:
        return "REJECTED — STATIC CONTRACT"
    required = frozenset(PAINT_REVIEW_FRAMES if evidence.category == "PAINT" else TRAIL_REVIEW_SCENES)
    if evidence.completed_native_cases != required:
        return "NOT TESTABLE — NATIVE REVIEW INCOMPLETE"
    if evidence.movement_max_delta is not None and (
        not isinstance(evidence.movement_max_delta, Decimal) or not evidence.movement_max_delta.is_finite()
    ):
        raise ValueError("movement delta must be a finite Decimal or null")
    if evidence.movement_max_delta != Decimal("0"):
        return "REJECTED — MOVEMENT EQUIVALENCE"
    if evidence.category == "TRAIL":
        for field_name, value in (
            ("wall occlusion", evidence.wall_occlusion_pass),
            ("reduced motion", evidence.reduced_motion_pass),
        ):
            if value is not None and not isinstance(value, bool):
                raise ValueError(f"{field_name} result must be boolean or null")
        if evidence.wall_occlusion_pass is not True:
            return "REJECTED — OCCLUSION"
        if evidence.reduced_motion_pass is not True:
            return "REJECTED — REDUCED MOTION"
        timings = (evidence.added_frame_median_ms, evidence.added_frame_p95_ms)
        if any(value is not None and (not isinstance(value, Decimal) or not value.is_finite()) for value in timings):
            raise ValueError("trail timings must be finite Decimals or null")
        if any(value is not None and value < 0 for value in timings):
            raise ValueError("trail timings cannot be negative")
        if (
            evidence.added_frame_median_ms is None
            or evidence.added_frame_p95_ms is None
            or evidence.added_frame_median_ms > Decimal("0.25")
            or evidence.added_frame_p95_ms > Decimal("0.55")
        ):
            return "REJECTED — PERFORMANCE"
        if evidence.allocation_growth is not None and (
            not isinstance(evidence.allocation_growth, int)
            or isinstance(evidence.allocation_growth, bool)
            or evidence.allocation_growth < 0
        ):
            raise ValueError("allocation growth must be a nonnegative integer or null")
        if evidence.allocation_growth != 0:
            return "REJECTED — RESOURCE GROWTH"
    for field_name, value in (
        ("owner reward", evidence.owner_reads_as_reward),
        ("owner equip", evidence.owner_would_equip),
    ):
        if value is not None and not isinstance(value, bool):
            raise ValueError(f"{field_name} result must be boolean or null")
    if evidence.owner_reads_as_reward is None or evidence.owner_would_equip is None:
        return "NOT TESTABLE — OWNER REVIEW INCOMPLETE"
    if not evidence.owner_reads_as_reward or not evidence.owner_would_equip:
        return "REJECTED — OWNER DESIRABILITY"
    return "FINALIST — NATIVE AND OWNER REVIEW PASS"


def report_summary() -> dict:
    return {
        "schema": "district_zero.p1b.iteration_07_reward_surface_report.v1",
        "decision": DECISION_ID,
        "authority": "PURE DESIGN-LAB MODEL — NOT GODOT OR HUMAN EVIDENCE",
        "results_hierarchy": ["IMMUTABLE_RECEIPT", "AT_MOST_ONE_REWARD_CARD", "OPTIONAL_ACTIONS"],
        "default_focus": "CONTINUE",
        "gate_b_surface": "FREE FINISH ISSUE + SHALLOW FREE-ONLY LOADOUT — NO PAID SHOP OR TRAIL STOCK",
        "post_gate_surface": "CONDITIONAL EXACT CLEAR-SET LOADOUT — NOT AUTHORIZED",
        "paint_native_case_count": len(PAINT_REVIEW_FRAMES),
        "trail_native_case_count": len(TRAIL_REVIEW_SCENES),
        "movement_required_max_delta": "0.0",
        "trail_added_frame_budget_ms": {"median": "0.25", "p95": "0.55"},
        "product_source_modified": False,
        "human_world_gate": "NOT PERFORMED",
        "P1B_product_implementation": "NOT STARTED",
    }
