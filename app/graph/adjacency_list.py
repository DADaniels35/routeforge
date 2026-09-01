from __future__ import annotations

from collections import defaultdict

from app.graph.models import Edge, WeightMetric


class GraphValidationError(ValueError):
    """Raised when a graph operation receives invalid input."""


class WeightedDiGraph:
    """Weighted directed graph backed by an adjacency list."""

    def __init__(self, name: str | None = None) -> None:
        self.name = name or "untitled"
        self._adjacency: dict[str, list[Edge]] = defaultdict(list)

    def add_vertex(self, vertex_id: str) -> None:
        vertex_id = self._normalise_vertex(vertex_id)
        self._adjacency.setdefault(vertex_id, [])

    def add_edge(
        self,
        source: str,
        destination: str,
        *,
        cost: float,
        distance: float,
        travel_time: float,
    ) -> None:
        source = self._normalise_vertex(source)
        destination = self._normalise_vertex(destination)
        self._validate_weight("cost", cost)
        self._validate_weight("distance", distance)
        self._validate_weight("travel_time", travel_time)

        self.add_vertex(source)
        self.add_vertex(destination)
        replacement = Edge(source, destination, cost, distance, travel_time)
        edges = self._adjacency[source]
        for index, edge in enumerate(edges):
            if edge.destination == destination:
                edges[index] = replacement
                return
        edges.append(replacement)

    def vertices(self) -> list[str]:
        return sorted(self._adjacency)

    def edges(self) -> list[Edge]:
        return [edge for source in self.vertices() for edge in self._adjacency[source]]

    def neighbours(self, vertex_id: str) -> list[Edge]:
        self.require_vertex(vertex_id)
        return list(self._adjacency[vertex_id])

    def edge_count(self) -> int:
        return sum(len(edges) for edges in self._adjacency.values())

    def require_vertex(self, vertex_id: str) -> None:
        if vertex_id not in self._adjacency:
            raise GraphValidationError(f"Vertex '{vertex_id}' does not exist")

    def weight(self, source: str, destination: str, metric: WeightMetric) -> float:
        for edge in self.neighbours(source):
            if edge.destination == destination:
                return edge.weight(metric)
        raise GraphValidationError(f"Edge '{source}' -> '{destination}' does not exist")

    def has_cycle(self) -> bool:
        visiting: set[str] = set()
        visited: set[str] = set()

        def visit(vertex: str) -> bool:
            if vertex in visiting:
                return True
            if vertex in visited:
                return False
            visiting.add(vertex)
            for edge in self._adjacency[vertex]:
                if visit(edge.destination):
                    return True
            visiting.remove(vertex)
            visited.add(vertex)
            return False

        return any(visit(vertex) for vertex in self.vertices())

    def weakly_connected_components(self) -> list[list[str]]:
        undirected: dict[str, set[str]] = {vertex: set() for vertex in self.vertices()}
        for edge in self.edges():
            undirected[edge.source].add(edge.destination)
            undirected[edge.destination].add(edge.source)

        seen: set[str] = set()
        components: list[list[str]] = []
        for start in self.vertices():
            if start in seen:
                continue
            stack = [start]
            component: list[str] = []
            seen.add(start)
            while stack:
                vertex = stack.pop()
                component.append(vertex)
                for neighbour in sorted(undirected[vertex], reverse=True):
                    if neighbour not in seen:
                        seen.add(neighbour)
                        stack.append(neighbour)
            components.append(sorted(component))
        return components

    @staticmethod
    def _normalise_vertex(vertex_id: str) -> str:
        if not vertex_id or not vertex_id.strip():
            raise GraphValidationError("Vertex id must not be blank")
        return vertex_id.strip()

    @staticmethod
    def _validate_weight(name: str, value: float) -> None:
        if value < 0:
            raise GraphValidationError(f"{name} must be non-negative for Dijkstra's algorithm")

