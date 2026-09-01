from __future__ import annotations

from app.graph.adjacency_list import WeightedDiGraph
from app.graph.models import WeightMetric


def dijkstra_array(
    graph: WeightedDiGraph, source: str, metric: WeightMetric
) -> tuple[dict[str, float], dict[str, str | None], list[str]]:
    graph.require_vertex(source)
    vertices = graph.vertices()
    distances = {vertex: float("inf") for vertex in vertices}
    predecessors: dict[str, str | None] = {vertex: None for vertex in vertices}
    unvisited = set(vertices)
    visited_order: list[str] = []
    distances[source] = 0.0

    while unvisited:
        current = min(unvisited, key=lambda vertex: distances[vertex])
        if distances[current] == float("inf"):
            break
        unvisited.remove(current)
        visited_order.append(current)
        for edge in graph.neighbours(current):
            if edge.destination not in unvisited:
                continue
            candidate = distances[current] + edge.weight(metric)
            if candidate < distances[edge.destination]:
                distances[edge.destination] = candidate
                predecessors[edge.destination] = current

    return distances, predecessors, visited_order

