from __future__ import annotations

from app.algorithms.containers import Queue
from app.graph.adjacency_list import WeightedDiGraph


def breadth_first_search(
    graph: WeightedDiGraph, start: str
) -> tuple[list[str], dict[str, str | None]]:
    graph.require_vertex(start)
    queue: Queue[str] = Queue()
    queue.push(start)
    seen = {start}
    order: list[str] = []
    predecessors: dict[str, str | None] = {start: None}

    while queue:
        vertex = queue.pop()
        order.append(vertex)
        for edge in graph.neighbours(vertex):
            if edge.destination not in seen:
                seen.add(edge.destination)
                predecessors[edge.destination] = vertex
                queue.push(edge.destination)

    return order, predecessors
