from __future__ import annotations

from app.algorithms.containers import Stack
from app.graph.adjacency_list import WeightedDiGraph


def depth_first_search(
    graph: WeightedDiGraph, start: str
) -> tuple[list[str], dict[str, str | None]]:
    graph.require_vertex(start)
    stack: Stack[str] = Stack()
    stack.push(start)
    seen: set[str] = set()
    order: list[str] = []
    predecessors: dict[str, str | None] = {start: None}

    while stack:
        vertex = stack.pop()
        if vertex in seen:
            continue
        seen.add(vertex)
        order.append(vertex)
        for edge in reversed(graph.neighbours(vertex)):
            if edge.destination not in seen:
                predecessors.setdefault(edge.destination, vertex)
                stack.push(edge.destination)

    return order, predecessors
