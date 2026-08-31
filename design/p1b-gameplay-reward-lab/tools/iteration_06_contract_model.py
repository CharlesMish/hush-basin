#!/usr/bin/env python3
"""Pure contract-breadth model for overnight iteration 06.

This is a design-lab model, not Godot product code.  It freezes the three-job
Gate-B proof as one open-endpoint family, then registers three mutually
exclusive post-gate challengers.  Each challenger changes exactly one design
axis so a later playtest can teach us something rather than mixing causes.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from decimal import Decimal
import hashlib
import json
from typing import Iterable, Mapping, Sequence


D = Decimal

DECISION_ID = "ONE_AXIS_CONTENT_LADDER_V1"
GATE_B = "GATE_B_PROOF"
POST_GATE_B = "POST_GATE_B_CHALLENGER"
OPEN_ENDPOINT = "OPEN_ENDPOINT_V1"
TRANSIT_HANDOFF = "TRANSIT_HANDOFF_V1"
FORGIVING_CARGO = "R7_COUNTER_EPOCH_FORGIVING_PEAK_EPISODE_V1"
FRAGILE_CARGO = "FRAGILE_PEAK_RESPONSE_CHALLENGER_V1"
SETTLE_PROFILE = "PAD_8M_SUPPORT_6MPS_SETTLE_050_V1"
SCORING_PROFILE = "REFERENCE_RATIO_CONDITION_PACE_GRADE_V1"
PAYOUT_PROFILE = "VERSIONED_DURATION_RATE_BASE_V1_50_35_15"

K0_REASON = "NONE"
K1_TRANSIT_REASON = "MACHINE_ENFORCED_MULTI_STOP"
K1_FRAGILE_REASON = "MACHINE_ENFORCED_FRAGILE"

ROUTE_CONTEXT_AXIS = "ROUTE_CONTEXT_BREADTH"
TRANSIT_TOPOLOGY_AXIS = "TRANSIT_HANDOFF_TOPOLOGY"
CARGO_RESPONSE_AXIS = "CARGO_RESPONSE"

NO_MISSING_SIGNAL = "NONE"
MORE_ROUTE_CHOICE = "MORE_ROUTE_CHOICE"
HOP_OBJECTIVE = "HOP_OBJECTIVE"
MORE_CARGO_STAKES = "MORE_CARGO_STAKES"

DESTINATION_NODES = frozenset({"MRK", "DEP", "CLN", "QRY", "RLY", "WRK"})
JUNCTION_NODES = frozenset({"GE", "GN", "GW", "HJW", "HJE"})


class ContractConflict(ValueError):
    """An authored identity or invariant differs from its frozen record."""


class DirectorSelectionRequired(ValueError):
    """Evidence names multiple gaps, so no challenger may be auto-combined."""


def _canonical_hash(payload: object) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def _require_text(value: str, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ContractConflict(f"{name} must be nonempty")
    return value


@dataclass(frozen=True)
class RouteDefinition:
    route_id: str
    from_node: str
    to_node: str
    length_m: Decimal

    def payload(self) -> dict:
        return {
            "route_id": self.route_id,
            "from_node": self.from_node,
            "to_node": self.to_node,
            "length_m": str(self.length_m),
        }

    def validate(self) -> None:
        _require_text(self.route_id, "route ID")
        _require_text(self.from_node, "route from-node")
        _require_text(self.to_node, "route to-node")
        if self.from_node == self.to_node:
            raise ContractConflict("route endpoints must differ")
        if not isinstance(self.length_m, Decimal) or not self.length_m.is_finite() or self.length_m <= 0:
            raise ContractConflict("route length must be a positive finite Decimal")


@dataclass(frozen=True)
class DirectedLeg:
    route_id: str
    from_node: str
    to_node: str

    def payload(self) -> dict:
        return {
            "route_id": self.route_id,
            "from_node": self.from_node,
            "to_node": self.to_node,
        }


@dataclass(frozen=True)
class RouteOption:
    option_id: str
    legs: tuple[DirectedLeg, ...]
    advisory_only: bool = True

    def payload(self) -> dict:
        return {
            "option_id": self.option_id,
            "legs": [leg.payload() for leg in self.legs],
            "advisory_only": self.advisory_only,
        }

    @property
    def route_ids(self) -> tuple[str, ...]:
        return tuple(leg.route_id for leg in self.legs)

    def validate(self, routes: Mapping[str, RouteDefinition], origin: str, destination: str) -> None:
        _require_text(self.option_id, "route-option ID")
        if not self.legs:
            raise ContractConflict("route option must contain at least one leg")
        if self.legs[0].from_node != origin or self.legs[-1].to_node != destination:
            raise ContractConflict("route option endpoints differ from contract")
        cursor = origin
        seen_routes: set[str] = set()
        for leg in self.legs:
            if leg.from_node != cursor:
                raise ContractConflict("route option is disconnected")
            route = routes.get(leg.route_id)
            if route is None:
                raise ContractConflict("route option references an unknown route")
            if leg.route_id in seen_routes:
                raise ContractConflict("route option cannot loop over the same route twice")
            seen_routes.add(leg.route_id)
            legal = {route.from_node, route.to_node} == {leg.from_node, leg.to_node}
            if not legal:
                raise ContractConflict("directed leg does not match authored route endpoints")
            cursor = leg.to_node
        if cursor != destination:
            raise ContractConflict("route option does not terminate at destination")
        if not self.advisory_only:
            raise ContractConflict("Gate-B and route-context options must remain advisory")

    def length_m(self, routes: Mapping[str, RouteDefinition]) -> Decimal:
        return sum((routes[leg.route_id].length_m for leg in self.legs), D("0"))


@dataclass(frozen=True)
class ContractDefinition:
    contract_id: str
    title: str
    stage: str
    origin: str
    destination: str
    family: str
    cargo_profile: str
    settle_profile: str
    scoring_profile: str
    payout_profile: str
    complexity_class: int
    complexity_reason: str
    changed_axes: tuple[str, ...]
    route_options: tuple[RouteOption, ...]
    required_transit_nodes: tuple[str, ...]
    hard_failure: bool
    pays_actual_distance: bool
    identity_hash: str

    def identity_payload(self) -> dict:
        return {
            "contract_id": self.contract_id,
            "title": self.title,
            "stage": self.stage,
            "origin": self.origin,
            "destination": self.destination,
            "family": self.family,
            "cargo_profile": self.cargo_profile,
            "settle_profile": self.settle_profile,
            "scoring_profile": self.scoring_profile,
            "payout_profile": self.payout_profile,
            "complexity_class": self.complexity_class,
            "complexity_reason": self.complexity_reason,
            "changed_axes": list(self.changed_axes),
            "route_options": [option.payload() for option in self.route_options],
            "required_transit_nodes": list(self.required_transit_nodes),
            "hard_failure": self.hard_failure,
            "pays_actual_distance": self.pays_actual_distance,
        }

    def validate(self, routes: Mapping[str, RouteDefinition]) -> None:
        for value, name in (
            (self.contract_id, "contract ID"),
            (self.title, "title"),
            (self.stage, "stage"),
            (self.origin, "origin"),
            (self.destination, "destination"),
            (self.family, "family"),
            (self.cargo_profile, "cargo profile"),
            (self.settle_profile, "settle profile"),
            (self.scoring_profile, "scoring profile"),
            (self.payout_profile, "payout profile"),
            (self.complexity_reason, "complexity reason"),
        ):
            _require_text(value, name)
        if self.origin not in DESTINATION_NODES or self.destination not in DESTINATION_NODES:
            raise ContractConflict("contract endpoints must be destination pads")
        if self.origin == self.destination:
            raise ContractConflict("contract endpoints must differ")
        if self.stage not in {GATE_B, POST_GATE_B}:
            raise ContractConflict("unregistered contract stage")
        if self.complexity_class not in {0, 1}:
            raise ContractConflict("only K0/K1 are registered in this study")
        allowed_reason = {
            0: {K0_REASON},
            1: {K1_TRANSIT_REASON, K1_FRAGILE_REASON},
        }
        if self.complexity_reason not in allowed_reason[self.complexity_class]:
            raise ContractConflict("complexity reason does not match class")
        if self.hard_failure:
            raise ContractConflict("hard failure is not authorized")
        if self.pays_actual_distance:
            raise ContractConflict("actual distance may not enter payout")
        if self.settle_profile != SETTLE_PROFILE:
            raise ContractConflict("settle profile differs from the proof authority")
        if self.scoring_profile != SCORING_PROFILE:
            raise ContractConflict("scoring profile differs from the proof authority")
        if self.payout_profile != PAYOUT_PROFILE:
            raise ContractConflict("payout profile differs from the proof authority")
        if len(set(self.changed_axes)) != len(self.changed_axes):
            raise ContractConflict("changed axes must be unique")
        if self.stage == GATE_B and self.changed_axes:
            raise ContractConflict("Gate-B proof contracts share one mechanical family")
        if self.stage == GATE_B:
            if self.family != OPEN_ENDPOINT or self.cargo_profile != FORGIVING_CARGO:
                raise ContractConflict("Gate-B family/cargo profile differs from the shared proof")
            if self.complexity_class != 0 or self.complexity_reason != K0_REASON:
                raise ContractConflict("Gate-B contracts must remain K0")
        if self.stage == POST_GATE_B and len(self.changed_axes) != 1:
            raise ContractConflict("post-gate challenger must change exactly one axis")
        if not self.route_options:
            raise ContractConflict("contract must expose at least one advisory route option")
        option_ids = tuple(option.option_id for option in self.route_options)
        if len(set(option_ids)) != len(option_ids):
            raise ContractConflict("route-option IDs must be unique within a contract")
        for option in self.route_options:
            option.validate(routes, self.origin, self.destination)
        if self.family == OPEN_ENDPOINT and self.required_transit_nodes:
            raise ContractConflict("open endpoint contract cannot require transit nodes")
        if self.family == TRANSIT_HANDOFF:
            if self.changed_axes != (TRANSIT_TOPOLOGY_AXIS,):
                raise ContractConflict("transit family must be the sole topology-axis challenger")
            if self.required_transit_nodes != ("HJW", "HJE"):
                raise ContractConflict("south handoff must bind the two declared junctions")
        elif self.required_transit_nodes:
            raise ContractConflict("only the transit challenger may require intermediate nodes")
        challenger_signatures = {
            "GC_QRY_CHOICE": (
                OPEN_ENDPOINT,
                FORGIVING_CARGO,
                0,
                K0_REASON,
                (ROUTE_CONTEXT_AXIS,),
                (),
            ),
            "GC_SOUTH_HANDOFF": (
                TRANSIT_HANDOFF,
                FORGIVING_CARGO,
                1,
                K1_TRANSIT_REASON,
                (TRANSIT_TOPOLOGY_AXIS,),
                ("HJW", "HJE"),
            ),
            "GC_WORKS_FRAGILE": (
                OPEN_ENDPOINT,
                FRAGILE_CARGO,
                1,
                K1_FRAGILE_REASON,
                (CARGO_RESPONSE_AXIS,),
                (),
            ),
        }
        if self.stage == POST_GATE_B:
            expected_signature = challenger_signatures.get(self.contract_id)
            observed_signature = (
                self.family,
                self.cargo_profile,
                self.complexity_class,
                self.complexity_reason,
                self.changed_axes,
                self.required_transit_nodes,
            )
            if expected_signature is None or observed_signature != expected_signature:
                raise ContractConflict("challenger behavior differs from its one-axis signature")
        expected = _canonical_hash(self.identity_payload())
        if self.identity_hash != expected:
            raise ContractConflict("contract identity hash mismatch")


def _route(route_id: str, from_node: str, to_node: str, length: str) -> RouteDefinition:
    result = RouteDefinition(route_id, from_node, to_node, D(length))
    result.validate()
    return result


def authoritative_routes() -> dict[str, RouteDefinition]:
    rows = (
        ("A0", "QRY", "GW", "76.509932"),
        ("A1", "GW", "RLY", "321.864198"),
        ("A2", "RLY", "GE", "442.281945"),
        ("DOG", "HJW", "HJE", "124.514081"),
        ("HOP", "HJW", "HJE", "90.0"),
        ("L0", "GW", "DEP", "72.32185"),
        ("L1", "DEP", "MRK", "129.429845"),
        ("L2", "MRK", "CLN", "129.429845"),
        ("L3", "CLN", "GE", "72.32185"),
        ("L4", "RLY", "GN", "80.0"),
        ("L5", "GN", "MRK", "167.795314"),
        ("L6", "MRK", "WRK", "118.070808"),
        ("L7", "WRK", "GE", "122.344392"),
        ("R0", "GN", "WRK", "137.716327"),
        ("S0", "DEP", "HJW", "107.177582"),
        ("S1", "HJE", "CLN", "107.177582"),
        ("X0", "QRY", "RLY", "499.881048"),
    )
    return {row[0]: _route(*row) for row in rows}


def route_registry_hash(routes: Mapping[str, RouteDefinition]) -> str:
    return _canonical_hash([routes[key].payload() for key in sorted(routes)])


def validate_authoritative_route_registry(routes: Mapping[str, RouteDefinition]) -> None:
    expected = authoritative_routes()
    if set(routes) != set(expected):
        raise ContractConflict("route registry IDs differ from exact R7 authority")
    for route_id in sorted(expected):
        route = routes[route_id]
        route.validate()
        if route != expected[route_id]:
            raise ContractConflict(f"route authority differs for {route_id}")


def leg(route_id: str, from_node: str, to_node: str) -> DirectedLeg:
    return DirectedLeg(route_id, from_node, to_node)


def option(option_id: str, *legs: DirectedLeg) -> RouteOption:
    return RouteOption(option_id, tuple(legs), True)


def _contract(**values) -> ContractDefinition:
    provisional = ContractDefinition(identity_hash="", **values)
    return replace(provisional, identity_hash=_canonical_hash(provisional.identity_payload()))


def gate_b_contracts() -> tuple[ContractDefinition, ...]:
    shared = {
        "stage": GATE_B,
        "family": OPEN_ENDPOINT,
        "cargo_profile": FORGIVING_CARGO,
        "settle_profile": SETTLE_PROFILE,
        "scoring_profile": SCORING_PROFILE,
        "payout_profile": PAYOUT_PROFILE,
        "complexity_class": 0,
        "complexity_reason": K0_REASON,
        "changed_axes": (),
        "required_transit_nodes": (),
        "hard_failure": False,
        "pays_actual_distance": False,
    }
    return (
        _contract(
            contract_id="C01",
            title="Market Parcel",
            origin="MRK",
            destination="DEP",
            route_options=(option("MARKET_DIRECT", leg("L1", "MRK", "DEP")),),
            **shared,
        ),
        _contract(
            contract_id="C02",
            title="Relay Window",
            origin="DEP",
            destination="RLY",
            route_options=(
                option("LONG_WEST_SWEEP", leg("L0", "DEP", "GW"), leg("A1", "GW", "RLY")),
            ),
            **shared,
        ),
        _contract(
            contract_id="C03",
            title="Clinic Glass",
            origin="RLY",
            destination="CLN",
            route_options=(
                option("INNER_CLINIC", leg("L4", "RLY", "GN"), leg("L5", "GN", "MRK"), leg("L2", "MRK", "CLN")),
                option("OUTER_EASTLINE", leg("A2", "RLY", "GE"), leg("L3", "GE", "CLN")),
            ),
            **shared,
        ),
    )


def challenger_contracts() -> tuple[ContractDefinition, ...]:
    common = {
        "stage": POST_GATE_B,
        "settle_profile": SETTLE_PROFILE,
        "scoring_profile": SCORING_PROFILE,
        "payout_profile": PAYOUT_PROFILE,
        "hard_failure": False,
        "pays_actual_distance": False,
    }
    return (
        _contract(
            contract_id="GC_QRY_CHOICE",
            title="Quarry Choice",
            origin="QRY",
            destination="RLY",
            family=OPEN_ENDPOINT,
            cargo_profile=FORGIVING_CARGO,
            complexity_class=0,
            complexity_reason=K0_REASON,
            changed_axes=(ROUTE_CONTEXT_AXIS,),
            route_options=(
                option("DIRECT_X0", leg("X0", "QRY", "RLY")),
                option("WEST_A0_A1", leg("A0", "QRY", "GW"), leg("A1", "GW", "RLY")),
            ),
            required_transit_nodes=(),
            **common,
        ),
        _contract(
            contract_id="GC_SOUTH_HANDOFF",
            title="South Handoff",
            origin="DEP",
            destination="CLN",
            family=TRANSIT_HANDOFF,
            cargo_profile=FORGIVING_CARGO,
            complexity_class=1,
            complexity_reason=K1_TRANSIT_REASON,
            changed_axes=(TRANSIT_TOPOLOGY_AXIS,),
            route_options=(
                option("SOUTH_HOP", leg("S0", "DEP", "HJW"), leg("HOP", "HJW", "HJE"), leg("S1", "HJE", "CLN")),
                option("SOUTH_BENT", leg("S0", "DEP", "HJW"), leg("DOG", "HJW", "HJE"), leg("S1", "HJE", "CLN")),
            ),
            required_transit_nodes=("HJW", "HJE"),
            **common,
        ),
        _contract(
            contract_id="GC_WORKS_FRAGILE",
            title="Works Fragile",
            origin="MRK",
            destination="WRK",
            family=OPEN_ENDPOINT,
            cargo_profile=FRAGILE_CARGO,
            complexity_class=1,
            complexity_reason=K1_FRAGILE_REASON,
            changed_axes=(CARGO_RESPONSE_AXIS,),
            route_options=(option("WORKS_DIRECT", leg("L6", "MRK", "WRK")),),
            required_transit_nodes=(),
            **common,
        ),
    )


@dataclass(frozen=True)
class ContractCatalog:
    decision_id: str
    route_registry_hash: str
    gate_b: tuple[ContractDefinition, ...]
    challengers: tuple[ContractDefinition, ...]
    catalog_hash: str

    def payload(self) -> dict:
        return {
            "decision_id": self.decision_id,
            "route_registry_hash": self.route_registry_hash,
            "gate_b": [(item.contract_id, item.identity_hash) for item in self.gate_b],
            "challengers": [(item.contract_id, item.identity_hash) for item in self.challengers],
        }

    def validate(self, routes: Mapping[str, RouteDefinition]) -> None:
        validate_authoritative_route_registry(routes)
        if self.decision_id != DECISION_ID:
            raise ContractConflict("catalog decision ID mismatch")
        if self.route_registry_hash != route_registry_hash(routes):
            raise ContractConflict("catalog route registry identity mismatch")
        if tuple(item.contract_id for item in self.gate_b) != ("C01", "C02", "C03"):
            raise ContractConflict("Gate-B order/IDs differ from frozen proof")
        if tuple(item.contract_id for item in self.challengers) != (
            "GC_QRY_CHOICE",
            "GC_SOUTH_HANDOFF",
            "GC_WORKS_FRAGILE",
        ):
            raise ContractConflict("challenger order/IDs differ from frozen registry")
        seen: set[str] = set()
        for item in self.gate_b + self.challengers:
            if item.contract_id in seen:
                raise ContractConflict("duplicate contract ID")
            seen.add(item.contract_id)
            item.validate(routes)
        expected_gate = gate_b_contracts()
        expected_challengers = challenger_contracts()
        if tuple((item.contract_id, item.identity_hash) for item in self.gate_b) != tuple(
            (item.contract_id, item.identity_hash) for item in expected_gate
        ):
            raise ContractConflict("Gate-B child definitions differ from exact frozen authority")
        if tuple((item.contract_id, item.identity_hash) for item in self.challengers) != tuple(
            (item.contract_id, item.identity_hash) for item in expected_challengers
        ):
            raise ContractConflict("challenger child definitions differ from exact frozen authority")
        if self.catalog_hash != _canonical_hash(self.payload()):
            raise ContractConflict("contract catalog identity hash mismatch")


def build_catalog(routes: Mapping[str, RouteDefinition] | None = None) -> ContractCatalog:
    routes = authoritative_routes() if routes is None else routes
    validate_authoritative_route_registry(routes)
    provisional = ContractCatalog(
        DECISION_ID,
        route_registry_hash(routes),
        gate_b_contracts(),
        challenger_contracts(),
        "",
    )
    result = replace(provisional, catalog_hash=_canonical_hash(provisional.payload()))
    result.validate(routes)
    return result


def select_challenger(
    catalog: ContractCatalog,
    gate_b_review_status: str,
    missing_signals: Iterable[str],
) -> str | None:
    catalog.validate(authoritative_routes())
    if gate_b_review_status != "PASS":
        raise ContractConflict("challenger selection requires an exact Gate-B owner-review PASS")
    signals = frozenset(missing_signals)
    if not signals or signals == {NO_MISSING_SIGNAL}:
        return None
    if NO_MISSING_SIGNAL in signals:
        raise ContractConflict("NONE cannot coexist with a missing signal")
    unknown = signals - {MORE_ROUTE_CHOICE, HOP_OBJECTIVE, MORE_CARGO_STAKES}
    if unknown:
        raise ContractConflict("unregistered owner-feedback signal")
    if len(signals) != 1:
        raise DirectorSelectionRequired("multiple gaps require an explicit director choice")
    return {
        MORE_ROUTE_CHOICE: "GC_QRY_CHOICE",
        HOP_OBJECTIVE: "GC_SOUTH_HANDOFF",
        MORE_CARGO_STAKES: "GC_WORKS_FRAGILE",
    }[next(iter(signals))]


def scoring_inputs(
    catalog: ContractCatalog,
    contract: ContractDefinition,
    *,
    integrity_units: int,
    pace_units: int,
    actual_distance_m: Decimal,
    observed_route_ids: Sequence[str],
    hop_count: int,
) -> dict:
    """Return the exact terminal inputs; route facts are intentionally absent."""
    routes = authoritative_routes()
    catalog.validate(routes)
    authorized = {
        item.contract_id: item.identity_hash
        for item in catalog.gate_b + catalog.challengers
    }
    if authorized.get(contract.contract_id) != contract.identity_hash:
        raise ContractConflict("contract is not authorized by the frozen catalog")
    contract.validate(routes)
    if isinstance(integrity_units, bool) or not isinstance(integrity_units, int):
        raise ValueError("integrity units must be an integer")
    if isinstance(pace_units, bool) or not isinstance(pace_units, int):
        raise ValueError("pace units must be an integer")
    if not 0 <= integrity_units <= 1000 or not 0 <= pace_units <= 1000:
        raise ValueError("integrity and pace units must be in 0..1000")
    if not isinstance(actual_distance_m, Decimal) or not actual_distance_m.is_finite() or actual_distance_m < 0:
        raise ValueError("actual distance must be finite and nonnegative")
    if isinstance(hop_count, bool) or not isinstance(hop_count, int) or hop_count < 0:
        raise ValueError("Hop count must be nonnegative")
    # Validate observational details without importing them into the result.
    for route_id in observed_route_ids:
        _require_text(route_id, "observed route ID")
        if route_id not in routes:
            raise ValueError("observed route ID is not in the R7 registry")
    return {
        "contract_identity": contract.identity_hash,
        "integrity_units": integrity_units,
        "pace_units": pace_units,
        "scoring_profile": contract.scoring_profile,
        "payout_profile": contract.payout_profile,
        "complexity_class": contract.complexity_class,
    }


def suggested_route_union(contracts: Iterable[ContractDefinition]) -> frozenset[str]:
    return frozenset(
        route_id
        for contract in contracts
        for route_option in contract.route_options
        for route_id in route_option.route_ids
    )


def contract_report() -> dict:
    routes = authoritative_routes()
    catalog = build_catalog(routes)
    lengths = {
        contract.contract_id: {
            route_option.option_id: str(route_option.length_m(routes))
            for route_option in contract.route_options
        }
        for contract in catalog.gate_b + catalog.challengers
    }
    gate_routes = suggested_route_union(catalog.gate_b)
    registry_routes = suggested_route_union(catalog.gate_b + catalog.challengers)
    return {
        "schema": "district_zero.p1b.iteration_06_contract_breadth_report.v1",
        "decision": DECISION_ID,
        "authority": "PURE DESIGN-LAB MODEL — NOT GODOT OR HUMAN EVIDENCE",
        "route_registry": {
            "count": len(routes),
            "sha256": catalog.route_registry_hash,
            "all_route_ids": sorted(routes),
        },
        "gate_b": {
            "contracts": [item.contract_id for item in catalog.gate_b],
            "mechanical_family_count": len({item.family for item in catalog.gate_b}),
            "suggested_context_route_id_count": len(gate_routes),
            "suggested_context_route_ids": sorted(gate_routes),
            "unrepresented_suggestion_route_ids": sorted(set(routes) - gate_routes),
            "executed_route_coverage": "NOT PERFORMED",
        },
        "challengers": [
            {
                "contract_id": item.contract_id,
                "changed_axis": item.changed_axes[0],
                "complexity_class": item.complexity_class,
                "complexity_reason": item.complexity_reason,
                "status": {
                    "GC_QRY_CHOICE": "REGISTERED — OWNER SIGNAL AND ORIGIN-ACCESS UX REVIEW REQUIRED",
                    "GC_SOUTH_HANDOFF": "REGISTERED — BLOCKED PENDING TRANSIT-HANDOFF OBSERVER PROOF",
                    "GC_WORKS_FRAGILE": "REGISTERED — BLOCKED PENDING BASE-OBSERVER AND FRAGILE-SEPARATION PROOF",
                }[item.contract_id],
            }
            for item in catalog.challengers
        ],
        "registry_context_only": {
            "suggested_route_id_count": len(registry_routes),
            "suggested_route_ids": sorted(registry_routes),
            "unrepresented_route_ids": sorted(set(routes) - registry_routes),
            "destination_nodes_touched": sorted(
                {item.origin for item in catalog.gate_b + catalog.challengers}
                | {item.destination for item in catalog.gate_b + catalog.challengers}
            ),
            "executed_route_coverage": "NOT PERFORMED",
        },
        "route_option_lengths_m": lengths,
        "selector": {
            "required_gate_b_review": "PASS",
            NO_MISSING_SIGNAL: None,
            MORE_ROUTE_CHOICE: select_challenger(catalog, "PASS", (MORE_ROUTE_CHOICE,)),
            HOP_OBJECTIVE: select_challenger(catalog, "PASS", (HOP_OBJECTIVE,)),
            MORE_CARGO_STAKES: select_challenger(catalog, "PASS", (MORE_CARGO_STAKES,)),
            "multiple": "DIRECTOR_SELECTION_REQUIRED",
        },
        "catalog_sha256": catalog.catalog_hash,
        "product_source_modified": False,
        "human_world_gate": "NOT PERFORMED",
        "P1B_product_implementation": "NOT STARTED",
    }
