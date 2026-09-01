from __future__ import annotations

from heapq import heappop, heappush

from app.graph.adjacency_list import WeightedDiGraph
from app.graph.models import WeightMetric


def dijkstra_heap(
    graph: WeightedDiGraph, source: str, metric: WeightMetric
) -> tuple[dict[str, float], dict[str, str | None], list[str]]:
    graph.require_vertex(source)
    distances = {vertex: float("inf") for vertex in graph.vertices()}
    predecessors: dict[str, str | None] = {vertex: None for vertex in graph.vertices()}
    distances[source] = 0.0
    heap: list[tuple[float, str]] = [(0.0, source)]
    visited: set[str] = set()
    visited_order: list[str] = []

    while heap:
        current_distance, current = heappop(heap)
        if current in visited:
            continue
        if current_distance > distances[current]:
            continue
        visited.add(current)
        visited_order.append(current)

        for edge in graph.neighbours(current):
            candidate = current_distance + edge.weight(metric)
            if candidate < distances[edge.destination]:
                distances[edge.destination] = candidate
                predecessors[edge.destination] = current
                heappush(heap, (candidate, edge.destination))

    return distances, predecessors, visited_order

