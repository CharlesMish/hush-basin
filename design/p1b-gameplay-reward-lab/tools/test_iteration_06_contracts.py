#!/usr/bin/env python3
"""Deterministic contract-breadth vectors for iteration 06."""

from __future__ import annotations

import argparse
from dataclasses import replace
from decimal import Decimal
import hashlib
import json
from pathlib import Path

from iteration_04_payout_model import ALLOWED_COMPLEXITY_REASONS
from iteration_06_contract_model import (
    CARGO_RESPONSE_AXIS,
    DECISION_ID,
    DESTINATION_NODES,
    FORGIVING_CARGO,
    FRAGILE_CARGO,
    GATE_B,
    HOP_OBJECTIVE,
    K0_REASON,
    K1_FRAGILE_REASON,
    K1_TRANSIT_REASON,
    MORE_CARGO_STAKES,
    MORE_ROUTE_CHOICE,
    NO_MISSING_SIGNAL,
    OPEN_ENDPOINT,
    PAYOUT_PROFILE,
    ROUTE_CONTEXT_AXIS,
    SCORING_PROFILE,
    SETTLE_PROFILE,
    TRANSIT_HANDOFF,
    TRANSIT_TOPOLOGY_AXIS,
    ContractConflict,
    DirectorSelectionRequired,
    DirectedLeg,
    RouteDefinition,
    RouteOption,
    authoritative_routes,
    build_catalog,
    challenger_contracts,
    contract_report,
    gate_b_contracts,
    route_registry_hash,
    scoring_inputs,
    select_challenger,
    suggested_route_union,
    validate_authoritative_route_registry,
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


def route_lengths(contracts, routes) -> dict[tuple[str, str], Decimal]:
    return {
        (contract.contract_id, option.option_id): option.length_m(routes)
        for contract in contracts
        for option in contract.route_options
    }


def run(r7_root: Path) -> dict:
    routes = authoritative_routes()
    catalog = build_catalog(routes)
    catalog.validate(routes)

    check(DECISION_ID == "ONE_AXIS_CONTENT_LADDER_V1", "decision identity is exact")
    check(len(routes) == 17, "authoritative route registry contains seventeen routes")
    check(set(routes) == {"A0", "A1", "A2", "DOG", "HOP", "L0", "L1", "L2", "L3", "L4", "L5", "L6", "L7", "R0", "S0", "S1", "X0"}, "route registry IDs match R7")
    check(all(route.length_m > 0 for route in routes.values()), "all route lengths are positive")
    check(all(route.from_node != route.to_node for route in routes.values()), "all route endpoints differ")
    check(len(route_registry_hash(routes)) == 64, "route registry has stable SHA-256 identity")

    manifest = json.loads((r7_root / "world/p1a_world_manifest.json").read_text())
    bake = json.loads((r7_root / "world/generated/route_bake.json").read_text())
    check(set(manifest["routes"]) == set(routes), "model route IDs match live R7 manifest")
    check(set(bake["routes"]) == set(routes), "model route IDs match live R7 route bake")
    for route_id, route in routes.items():
        live_manifest = manifest["routes"][route_id]
        check((live_manifest["from_node"], live_manifest["to_node"]) == (route.from_node, route.to_node), f"R7 endpoints match {route_id}")
        check(Decimal(str(bake["routes"][route_id]["baked_polyline_length_m"])) == route.length_m, f"R7 length matches {route_id}")

    gate = catalog.gate_b
    challengers = catalog.challengers
    check(tuple(item.contract_id for item in gate) == ("C01", "C02", "C03"), "Gate-B contract order is frozen")
    check(tuple((item.origin, item.destination) for item in gate) == (("MRK", "DEP"), ("DEP", "RLY"), ("RLY", "CLN")), "Gate-B forms a spatially continuous three-job chain")
    check(all(item.stage == GATE_B for item in gate), "all proof contracts remain Gate-B")
    check({item.family for item in gate} == {OPEN_ENDPOINT}, "three proof journeys are one mechanical family")
    check({item.cargo_profile for item in gate} == {FORGIVING_CARGO}, "all proof contracts use one cargo profile")
    check({item.settle_profile for item in gate} == {SETTLE_PROFILE}, "all proof contracts use one settle profile")
    check({item.scoring_profile for item in gate} == {SCORING_PROFILE}, "all proof contracts use one scoring profile")
    check({item.payout_profile for item in gate} == {PAYOUT_PROFILE}, "all proof contracts use one payout profile")
    check({item.complexity_class for item in gate} == {0}, "all proof contracts remain K0")
    check({item.complexity_reason for item in gate} == {K0_REASON}, "all proof contracts share the K0 reason")
    check(all(not item.changed_axes for item in gate), "proof copy does not imply hidden modifier axes")
    check(all(not item.required_transit_nodes for item in gate), "proof contracts require no route or transit nodes")
    check(all(not item.hard_failure for item in gate), "proof contracts have no hard-fail rule")
    check(all(not item.pays_actual_distance for item in gate), "proof contracts never pay actual distance")
    check(all(item.origin in DESTINATION_NODES and item.destination in DESTINATION_NODES for item in gate), "proof endpoints are destination pads")

    lengths = route_lengths(gate + challengers, routes)
    exact_lengths = {
        ("C01", "MARKET_DIRECT"): Decimal("129.429845"),
        ("C02", "LONG_WEST_SWEEP"): Decimal("394.186048"),
        ("C03", "INNER_CLINIC"): Decimal("377.225159"),
        ("C03", "OUTER_EASTLINE"): Decimal("514.603795"),
        ("GC_QRY_CHOICE", "DIRECT_X0"): Decimal("499.881048"),
        ("GC_QRY_CHOICE", "WEST_A0_A1"): Decimal("398.374130"),
        ("GC_SOUTH_HANDOFF", "SOUTH_HOP"): Decimal("304.355164"),
        ("GC_SOUTH_HANDOFF", "SOUTH_BENT"): Decimal("338.869245"),
        ("GC_WORKS_FRAGILE", "WORKS_DIRECT"): Decimal("118.070808"),
    }
    for key, expected in exact_lengths.items():
        check(lengths[key] == expected, f"route-option length is exact for {key[0]} {key[1]}")
    c02_audit_comparator = routes["L1"].length_m + routes["L5"].length_m + routes["L4"].length_m
    check(c02_audit_comparator == Decimal("377.225159"), "C02 inner path remains an audit comparator")
    check(c02_audit_comparator < lengths[("C02", "LONG_WEST_SWEEP")], "C02 long sweep is not falsely called shortest")
    check(tuple(option.option_id for option in gate[1].route_options) == ("LONG_WEST_SWEEP",), "C02 does not reopen an unselected advertised option")
    check(lengths[("C03", "OUTER_EASTLINE")] > lengths[("C03", "INNER_CLINIC")], "C03 outer alternative remains a legitimate longer choice")
    check(lengths[("GC_QRY_CHOICE", "DIRECT_X0")] > lengths[("GC_QRY_CHOICE", "WEST_A0_A1")], "Quarry challenger does not hide X0 distance tradeoff")
    check(lengths[("GC_SOUTH_HANDOFF", "SOUTH_HOP")] < lengths[("GC_SOUTH_HANDOFF", "SOUTH_BENT")], "South challenger preserves HOP/DOG length distinction")

    gate_routes = suggested_route_union(gate)
    check(len(gate_routes) == 8, "Gate-B suggestions cover eight of seventeen route IDs")
    check(gate_routes == frozenset({"A1", "A2", "L0", "L1", "L2", "L3", "L4", "L5"}), "Gate-B suggested-route set is exact")
    check(set(routes) - gate_routes == {"A0", "DOG", "HOP", "L6", "L7", "R0", "S0", "S1", "X0"}, "Gate-B route noncoverage is explicit")
    check("HOP" not in gate_routes and "DOG" not in gate_routes and "X0" not in gate_routes, "proof cannot claim HOP DOG or X0 coverage")

    check(tuple(item.contract_id for item in challengers) == ("GC_QRY_CHOICE", "GC_SOUTH_HANDOFF", "GC_WORKS_FRAGILE"), "challenger registry order is frozen")
    check(all(item.stage != GATE_B for item in challengers), "challengers cannot silently enter Gate-B")
    check(all(len(item.changed_axes) == 1 for item in challengers), "every challenger changes exactly one axis")
    check(tuple(item.changed_axes[0] for item in challengers) == (ROUTE_CONTEXT_AXIS, TRANSIT_TOPOLOGY_AXIS, CARGO_RESPONSE_AXIS), "challenger axes are distinct and ordered")
    check(challengers[0].family == OPEN_ENDPOINT and challengers[0].cargo_profile == FORGIVING_CARGO, "Quarry challenger changes route context only")
    check(challengers[0].complexity_class == 0 and challengers[0].complexity_reason == K0_REASON, "route-choice breadth remains K0")
    check(challengers[0].required_transit_nodes == (), "Quarry route choices remain unenforced")
    check(challengers[1].family == TRANSIT_HANDOFF and challengers[1].cargo_profile == FORGIVING_CARGO, "South challenger changes topology only")
    check(challengers[1].complexity_class == 1 and challengers[1].complexity_reason == K1_TRANSIT_REASON, "machine-enforced handoff is the declared K1 burden")
    check(challengers[1].required_transit_nodes == ("HJW", "HJE"), "South handoff binds exactly two junctions")
    check(challengers[2].family == OPEN_ENDPOINT and challengers[2].cargo_profile == FRAGILE_CARGO, "Works challenger changes cargo response only")
    check(challengers[2].complexity_class == 1 and challengers[2].complexity_reason == K1_FRAGILE_REASON, "fragile response is the declared K1 burden")
    check(challengers[2].required_transit_nodes == (), "fragile challenger adds no route requirement")
    check(all(not item.hard_failure and not item.pays_actual_distance for item in challengers), "challengers add neither hard failure nor distance pay")
    check(K0_REASON in ALLOWED_COMPLEXITY_REASONS[0], "Gate-B K0 reason composes with settled payout authority")
    check(K1_TRANSIT_REASON in ALLOWED_COMPLEXITY_REASONS[1], "South K1 reason composes with settled payout authority")
    check(K1_FRAGILE_REASON in ALLOWED_COMPLEXITY_REASONS[1], "Works K1 reason composes with settled payout authority")
    check("base_credits" not in challengers[1].__dataclass_fields__ and "reference_ms" not in challengers[1].__dataclass_fields__, "K1 challenger registry does not mint price or pace literals")

    check(select_challenger(catalog, "PASS", ()) is None, "no missing signal selects no expansion")
    check(select_challenger(catalog, "PASS", (NO_MISSING_SIGNAL,)) is None, "explicit NONE selects no expansion")
    check(select_challenger(catalog, "PASS", (MORE_ROUTE_CHOICE,)) == "GC_QRY_CHOICE", "route-choice feedback selects Quarry challenger")
    check(select_challenger(catalog, "PASS", (HOP_OBJECTIVE,)) == "GC_SOUTH_HANDOFF", "Hop-objective feedback selects South challenger")
    check(select_challenger(catalog, "PASS", (MORE_CARGO_STAKES,)) == "GC_WORKS_FRAGILE", "cargo-stakes feedback selects Works challenger")
    check(select_challenger(catalog, "PASS", (MORE_ROUTE_CHOICE, MORE_ROUTE_CHOICE)) == "GC_QRY_CHOICE", "duplicate same signal is idempotent")
    expect_error(lambda: select_challenger(catalog, "NOT PERFORMED", (MORE_ROUTE_CHOICE,)), "selection before Gate-B review rejected", ContractConflict)
    expect_error(lambda: select_challenger(replace(catalog, catalog_hash="f" * 64), "PASS", (MORE_ROUTE_CHOICE,)), "selection with forged catalog rejected", ContractConflict)
    expect_error(lambda: select_challenger(catalog, "PASS", (NO_MISSING_SIGNAL, MORE_ROUTE_CHOICE)), "NONE cannot coexist with missing signal", ContractConflict)
    expect_error(lambda: select_challenger(catalog, "PASS", ("MORE_SPEED",)), "unregistered raw-speed signal rejected", ContractConflict)
    expect_error(lambda: select_challenger(catalog, "PASS", (MORE_ROUTE_CHOICE, HOP_OBJECTIVE)), "two missing signals require director selection", DirectorSelectionRequired)
    expect_error(lambda: select_challenger(catalog, "PASS", (MORE_ROUTE_CHOICE, HOP_OBJECTIVE, MORE_CARGO_STAKES)), "all challenger axes cannot auto-stack", DirectorSelectionRequired)

    base_contract = gate[0]
    score_a = scoring_inputs(catalog, base_contract, integrity_units=900, pace_units=750, actual_distance_m=Decimal("129.429845"), observed_route_ids=("L1",), hop_count=0)
    score_b = scoring_inputs(catalog, base_contract, integrity_units=900, pace_units=750, actual_distance_m=Decimal("9999"), observed_route_ids=("X0", "DOG"), hop_count=99)
    check(score_a == score_b, "actual distance route trace and Hop count cannot alter scoring inputs")
    check(set(score_a) == {"contract_identity", "integrity_units", "pace_units", "scoring_profile", "payout_profile", "complexity_class"}, "scoring whitelist excludes route facts")
    expect_error(lambda: scoring_inputs(catalog, base_contract, integrity_units=-1, pace_units=0, actual_distance_m=Decimal(0), observed_route_ids=(), hop_count=0), "negative integrity units rejected")
    expect_error(lambda: scoring_inputs(catalog, base_contract, integrity_units=True, pace_units=0, actual_distance_m=Decimal(0), observed_route_ids=(), hop_count=0), "boolean integrity units rejected")
    expect_error(lambda: scoring_inputs(catalog, base_contract, integrity_units=0, pace_units=1001, actual_distance_m=Decimal(0), observed_route_ids=(), hop_count=0), "excess pace units rejected")
    expect_error(lambda: scoring_inputs(catalog, base_contract, integrity_units=0, pace_units=False, actual_distance_m=Decimal(0), observed_route_ids=(), hop_count=0), "boolean pace units rejected")
    expect_error(lambda: scoring_inputs(catalog, base_contract, integrity_units=0, pace_units=0, actual_distance_m=Decimal("NaN"), observed_route_ids=(), hop_count=0), "nonfinite actual distance rejected")
    expect_error(lambda: scoring_inputs(catalog, base_contract, integrity_units=0, pace_units=0, actual_distance_m=Decimal(0), observed_route_ids=("NOPE",), hop_count=0), "unknown observed route rejected")
    expect_error(lambda: scoring_inputs(catalog, base_contract, integrity_units=0, pace_units=0, actual_distance_m=Decimal(0), observed_route_ids=(), hop_count=-1), "negative Hop count rejected")
    expect_error(lambda: scoring_inputs(catalog, base_contract, integrity_units=0, pace_units=0, actual_distance_m=Decimal(0), observed_route_ids=(), hop_count=True), "boolean Hop count rejected")
    unauthorized_contract = replace(base_contract, title="FORGED")
    expect_error(lambda: scoring_inputs(catalog, unauthorized_contract, integrity_units=0, pace_units=0, actual_distance_m=Decimal(0), observed_route_ids=(), hop_count=0), "unauthorized contract object rejected", ContractConflict)

    expect_error(lambda: replace(gate[0], title="Express Parcel").validate(routes), "copy mutation with stale contract hash rejected", ContractConflict)
    expect_error(lambda: replace(gate[1], complexity_class=1).validate(routes), "hidden proof premium with stale hash rejected", ContractConflict)
    expect_error(lambda: replace(gate[2], cargo_profile=FRAGILE_CARGO).validate(routes), "hidden fragile proof copy with stale hash rejected", ContractConflict)
    expect_error(lambda: replace(gate[0], hard_failure=True).validate(routes), "hard-fail mutation rejected", ContractConflict)
    expect_error(lambda: replace(gate[0], pays_actual_distance=True).validate(routes), "distance-pay mutation rejected", ContractConflict)
    expect_error(lambda: replace(challengers[0], changed_axes=(ROUTE_CONTEXT_AXIS, CARGO_RESPONSE_AXIS)).validate(routes), "stacked challenger axes rejected", ContractConflict)
    forged_qry_cargo = replace(challengers[0], cargo_profile=FRAGILE_CARGO)
    forged_qry_cargo = replace(forged_qry_cargo, identity_hash=__import__("iteration_06_contract_model")._canonical_hash(forged_qry_cargo.identity_payload()))
    expect_error(lambda: forged_qry_cargo.validate(routes), "rehashed Quarry cargo override still rejected", ContractConflict)
    forged_south_payout = replace(challengers[1], payout_profile="BONUS_PER_HOP")
    forged_south_payout = replace(forged_south_payout, identity_hash=__import__("iteration_06_contract_model")._canonical_hash(forged_south_payout.identity_payload()))
    expect_error(lambda: forged_south_payout.validate(routes), "rehashed South payout override still rejected", ContractConflict)
    forged_works_topology = replace(challengers[2], family=TRANSIT_HANDOFF, required_transit_nodes=("HJW", "HJE"))
    forged_works_topology = replace(forged_works_topology, identity_hash=__import__("iteration_06_contract_model")._canonical_hash(forged_works_topology.identity_payload()))
    expect_error(lambda: forged_works_topology.validate(routes), "rehashed Works topology stack still rejected", ContractConflict)
    expect_error(lambda: replace(challengers[1], required_transit_nodes=("HJW",)).validate(routes), "partial transit authority rejected", ContractConflict)
    expect_error(lambda: replace(challengers[2], complexity_class=0).validate(routes), "fragile K0 downgrade rejected", ContractConflict)
    rehashed_origin = replace(challengers[0], origin="MRK")
    rehashed_origin = replace(rehashed_origin, identity_hash=__import__("iteration_06_contract_model")._canonical_hash(rehashed_origin.identity_payload()))
    expect_error(lambda: replace(catalog, challengers=(rehashed_origin,) + challengers[1:], catalog_hash=__import__("iteration_06_contract_model")._canonical_hash({**catalog.payload(), "challengers": [(rehashed_origin.contract_id, rehashed_origin.identity_hash)] + [(item.contract_id, item.identity_hash) for item in challengers[1:]]})).validate(routes), "rehashed challenger origin mutation rejected", ContractConflict)
    expect_error(lambda: replace(catalog, decision_id="SPEED_UPGRADES").validate(routes), "forged decision ID rejected", ContractConflict)
    expect_error(lambda: replace(catalog, route_registry_hash="a" * 64).validate(routes), "forged route-registry binding rejected", ContractConflict)
    expect_error(lambda: replace(catalog, catalog_hash="b" * 64).validate(routes), "forged catalog hash rejected", ContractConflict)

    bad_option = RouteOption("BAD", (DirectedLeg("L1", "MRK", "DEP"), DirectedLeg("A1", "GW", "RLY")))
    expect_error(lambda: bad_option.validate(routes, "MRK", "RLY"), "disconnected route option rejected", ContractConflict)
    unknown_option = RouteOption("UNKNOWN", (DirectedLeg("NOPE", "MRK", "DEP"),))
    expect_error(lambda: unknown_option.validate(routes, "MRK", "DEP"), "unknown route ID rejected", ContractConflict)
    wrong_direction = RouteOption("WRONG", (DirectedLeg("L1", "MRK", "CLN"),))
    expect_error(lambda: wrong_direction.validate(routes, "MRK", "CLN"), "leg endpoints must match route authority", ContractConflict)
    reverse_ok = RouteOption("REVERSE", (DirectedLeg("L1", "MRK", "DEP"),))
    reverse_ok.validate(routes, "MRK", "DEP")
    check(True, "authored route reversal is accepted")
    enforced_option = RouteOption("SEALED", (DirectedLeg("L1", "MRK", "DEP"),), False)
    expect_error(lambda: enforced_option.validate(routes, "MRK", "DEP"), "route option cannot become a seal", ContractConflict)
    repeated_leg_option = RouteOption("LOOP", (DirectedLeg("L1", "MRK", "DEP"), DirectedLeg("L1", "DEP", "MRK")))
    expect_error(lambda: repeated_leg_option.validate(routes, "MRK", "MRK"), "route option cannot loop over one route twice", ContractConflict)
    duplicate_option_contract = replace(gate[0], route_options=(gate[0].route_options[0], gate[0].route_options[0]))
    expect_error(lambda: duplicate_option_contract.validate(routes), "duplicate route-option IDs rejected", ContractConflict)

    future_routes = dict(routes)
    future_routes["FUTURE"] = RouteDefinition("FUTURE", "DEP", "CLN", Decimal("200"))
    future_routes["FUTURE"].validate()
    check(catalog.catalog_hash == build_catalog(routes).catalog_hash, "catalog rebuild is deterministic")
    expect_error(lambda: catalog.validate(future_routes), "future route registry cannot mutate frozen catalog", ContractConflict)

    report = contract_report()
    check(report["gate_b"]["mechanical_family_count"] == 1, "report names one proof family")
    check(report["gate_b"]["suggested_context_route_id_count"] == 8, "report names bounded proof suggestion context")
    check(report["gate_b"]["executed_route_coverage"] == "NOT PERFORMED", "report does not turn suggestions into executed coverage")
    check(report["registry_context_only"]["suggested_route_id_count"] == 15, "full registry context names fifteen of seventeen routes")
    check(report["registry_context_only"]["unrepresented_route_ids"] == ["L7", "R0"], "registry context honestly leaves L7 and R0 unrepresented")
    check(report["registry_context_only"]["destination_nodes_touched"] == sorted(DESTINATION_NODES), "registry context touches all six destination pads")
    check(len(report["challengers"]) == 3, "report registers exactly three mutually exclusive challengers")
    check(all(row["status"].startswith("REGISTERED —") for row in report["challengers"]), "report does not authorize challenger product work")
    check("BLOCKED PENDING TRANSIT-HANDOFF" in report["challengers"][1]["status"], "report exposes South observer blocker")
    check("BLOCKED PENDING BASE-OBSERVER" in report["challengers"][2]["status"], "report exposes fragile observer blocker")
    check(report["product_source_modified"] is False, "report records no product source modification")
    check(report["human_world_gate"] == "NOT PERFORMED", "report records no Human World Gate")
    check(report["P1B_product_implementation"] == "NOT STARTED", "report records no P1B product implementation")

    report["checks"] = {
        "passed": len(PASS_RECORDS),
        "failed": 0,
        "total": len(PASS_RECORDS),
        "status": "PASS WITH NATIVE AND HUMAN FALSIFIERS REMAINING",
        "records": PASS_RECORDS,
    }
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--r7-root", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    report = run(args.r7_root.resolve())
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(f"RESULT {report['checks']['passed']}/{report['checks']['total']} PASS WITH NATIVE AND HUMAN FALSIFIERS REMAINING")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
