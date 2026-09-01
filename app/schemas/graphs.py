from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from app.graph.adjacency_list import WeightedDiGraph
from app.graph.models import WeightMetric

Algorithm = Literal["dijkstra_heap", "dijkstra_array"]


class RandomGraphRequest(BaseModel):
    vertices: int = Field(ge=1, le=10_000)
    edges: int | None = Field(default=None, ge=0)
    dense: bool = False
    seed: int | None = None


class CreateGraphRequest(BaseModel):
    name: str = Field(default="logistics-network", min_length=1, max_length=80)
    random: RandomGraphRequest | None = None


class VertexRequest(BaseModel):
    id: str = Field(min_length=1, max_length=80)


class EdgeRequest(BaseModel):
    source: str = Field(min_length=1, max_length=80)
    destination: str = Field(min_length=1, max_length=80)
    cost: float = Field(ge=0)
    distance: float = Field(ge=0)
    travel_time: float = Field(ge=0)


class EdgeResponse(EdgeRequest):
    pass


class GraphResponse(BaseModel):
    id: str
    name: str
    vertices: list[str]
    edges: list[EdgeResponse]
    vertex_count: int
    edge_count: int
    has_cycle: bool
    weakly_connected_components: list[list[str]]

    @classmethod
    def from_graph(cls, graph_id: str, graph: WeightedDiGraph) -> GraphResponse:
        edges = [
            EdgeResponse(
                source=edge.source,
                destination=edge.destination,
                cost=edge.cost,
                distance=edge.distance,
                travel_time=edge.travel_time,
            )
            for edge in graph.edges()
        ]
        return cls(
            id=graph_id,
            name=graph.name,
            vertices=graph.vertices(),
            edges=edges,
            vertex_count=len(graph.vertices()),
            edge_count=graph.edge_count(),
            has_cycle=graph.has_cycle(),
            weakly_connected_components=graph.weakly_connected_components(),
        )


class RouteRequest(BaseModel):
    source: str = Field(min_length=1)
    destination: str = Field(min_length=1)
    optimise_for: WeightMetric = "cost"
    algorithm: Algorithm = "dijkstra_heap"


class RouteResponse(BaseModel):
    path: list[str]
    total_weight: float
    visited_vertices: int
    visited_order: list[str]
    algorithm: Algorithm
    optimise_for: WeightMetric
    execution_time_ms: float


class TraversalRequest(BaseModel):
    start: str = Field(min_length=1)


class TraversalResponse(BaseModel):
    algorithm: Literal["bfs", "dfs"]
    start: str
    order: list[str]
    predecessors: dict[str, str | None]
    visited_vertices: int
    execution_time_ms: float


class BenchmarkRequest(BaseModel):
    source: str = Field(min_length=1)
    destination: str = Field(min_length=1)
    optimise_for: WeightMetric = "cost"
    runs: int = Field(default=5, ge=1, le=100)
    include_networkx: bool = True


class BenchmarkResult(BaseModel):
    algorithm: str
    mean_ms: float
    min_ms: float
    max_ms: float
    path_cost: float | None = None
    path: list[str] | None = None


class BenchmarkResponse(BaseModel):
    vertex_count: int
    edge_count: int
    optimise_for: WeightMetric
    runs: int
    results: list[BenchmarkResult]
