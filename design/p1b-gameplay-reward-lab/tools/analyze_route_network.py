#!/usr/bin/env python3
"""Deterministic, read-only design analysis of District Zero's frozen route graph."""

from __future__ import annotations

import argparse
import heapq
import json
from pathlib import Path


NODES = {
    "CLN": "DESTINATION",
    "DEP": "DESTINATION",
    "GE": "GATE",
    "GN": "GATE",
    "GW": "GATE",
    "HJE": "JUNCTION",
    "HJW": "JUNCTION",
    "MRK": "DESTINATION",
    "QRY": "DESTINATION",
    "RLY": "DESTINATION",
    "WRK": "DESTINATION",
}

EDGES = {
    "A0": ("QRY", "GW", 76.509932),
    "A1": ("GW", "RLY", 321.864198),
    "A2": ("RLY", "GE", 442.281945),
    "DOG": ("HJW", "HJE", 124.514081),
    "HOP": ("HJW", "HJE", 90.0),
    "L0": ("GW", "DEP", 72.32185),
    "L1": ("DEP", "MRK", 129.429845),
    "L2": ("MRK", "CLN", 129.429845),
    "L3": ("CLN", "GE", 72.32185),
    "L4": ("RLY", "GN", 80.0),
    "L5": ("GN", "MRK", 167.795314),
    "L6": ("MRK", "WRK", 118.070808),
    "L7": ("WRK", "GE", 122.344392),
    "R0": ("GN", "WRK", 137.716327),
    "S0": ("DEP", "HJW", 107.177582),
    "S1": ("HJE", "CLN", 107.177582),
    "X0": ("QRY", "RLY", 499.881048),
}


def adjacency() -> dict[str, list[tuple[str, str, float]]]:
    graph: dict[str, list[tuple[str, str, float]]] = {node: [] for node in NODES}
    for route_id, (left, right, length) in EDGES.items():
        graph[left].append((right, route_id, length))
        graph[right].append((left, route_id, length))
    for choices in graph.values():
        choices.sort(key=lambda item: (item[1], item[0]))
    return graph


def shortest_path(start: str, end: str) -> tuple[float, list[str], list[str]]:
    graph = adjacency()
    queue: list[tuple[float, tuple[str, ...], str, tuple[str, ...]]] = [
        (0.0, tuple(), start, (start,))
    ]
    best: dict[str, float] = {}
    while queue:
        distance, routes, node, nodes = heapq.heappop(queue)
        if node in best and best[node] <= distance:
            continue
        best[node] = distance
        if node == end:
            return distance, list(routes), list(nodes)
        for neighbor, route_id, length in graph[node]:
            if neighbor in nodes:
                continue
            heapq.heappush(
                queue,
                (distance + length, routes + (route_id,), neighbor, nodes + (neighbor,)),
            )
    raise RuntimeError(f"No path from {start} to {end}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    destinations = sorted(node for node, kind in NODES.items() if kind == "DESTINATION")
    pairs = []
    for index, start in enumerate(destinations):
        for end in destinations[index + 1 :]:
            distance, routes, nodes = shortest_path(start, end)
            pairs.append(
                {
                    "from": start,
                    "to": end,
                    "shortest_distance_m": round(distance, 6),
                    "route_ids": routes,
                    "node_sequence": nodes,
                    "contains_hop": "HOP" in routes,
                    "contains_fast_route": any(route in {"A1", "A2", "X0"} for route in routes),
                }
            )

    report = {
        "schema": "district_zero.p1b.route_network_analysis.v1",
        "method": "undirected Dijkstra; route-id lexical tie-break; frozen v1.2.3 lengths",
        "design_warning": (
            "Endpoint-only contracts naturally collapse toward shortest paths. Authored route "
            "or gate conditions are needed when a contract should invite HOP, DOG, A1, A2, or X0."
        ),
        "destination_pair_count": len(pairs),
        "destination_pairs": pairs,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
