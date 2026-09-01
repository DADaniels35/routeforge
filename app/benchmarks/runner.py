from __future__ import annotations

from statistics import mean
from time import perf_counter

from app.algorithms.dijkstra_array import dijkstra_array
from app.algorithms.dijkstra_heap import dijkstra_heap
from app.algorithms.reconstruction import reconstruct_path
from app.graph.adjacency_list import WeightedDiGraph
from app.graph.models import WeightMetric
from app.schemas.graphs import BenchmarkResponse, BenchmarkResult


def benchmark_graph(
    graph: WeightedDiGraph,
    *,
    source: str,
    destination: str,
    optimise_for: WeightMetric,
    runs: int,
    include_networkx: bool,
) -> BenchmarkResponse:
    graph.require_vertex(source)
    graph.require_vertex(destination)
    results = [
        _time_algorithm(
            "dijkstra_array", dijkstra_array, graph, source, destination, optimise_for, runs
        ),
        _time_algorithm(
            "dijkstra_heap", dijkstra_heap, graph, source, destination, optimise_for, runs
        ),
    ]
    if include_networkx:
        networkx_result = _time_networkx(graph, source, destination, optimise_for, runs)
        if networkx_result is not None:
            results.append(networkx_result)
    return BenchmarkResponse(
        vertex_count=len(graph.vertices()),
        edge_count=graph.edge_count(),
        optimise_for=optimise_for,
        runs=runs,
        results=results,
    )


def _time_algorithm(
    name: str,
    algorithm,
    graph: WeightedDiGraph,
    source: str,
    destination: str,
    metric: WeightMetric,
    runs: int,
) -> BenchmarkResult:
    timings: list[float] = []
    distances: dict[str, float] = {}
    predecessors: dict[str, str | None] = {}
    for _ in range(runs):
        started = perf_counter()
        distances, predecessors, _ = algorithm(graph, source, metric)
        timings.append((perf_counter() - started) * 1000)
    path = reconstruct_path(predecessors, source, destination)
    return BenchmarkResult(
        algorithm=name,
        mean_ms=round(mean(timings), 4),
        min_ms=round(min(timings), 4),
        max_ms=round(max(timings), 4),
        path_cost=None if distances[destination] == float("inf") else distances[destination],
        path=path,
    )


def _time_networkx(
    graph: WeightedDiGraph,
    source: str,
    destination: str,
    metric: WeightMetric,
    runs: int,
) -> BenchmarkResult | None:
    try:
        import networkx as nx
    except ImportError:
        return None

    nx_graph = nx.DiGraph()
    nx_graph.add_nodes_from(graph.vertices())
    for edge in graph.edges():
        nx_graph.add_edge(edge.source, edge.destination, weight=edge.weight(metric))

    timings: list[float] = []
    path: list[str] | None = None
    path_cost: float | None = None
    for _ in range(runs):
        started = perf_counter()
        try:
            path = nx.shortest_path(nx_graph, source, destination, weight="weight")
            path_cost = nx.shortest_path_length(nx_graph, source, destination, weight="weight")
        except nx.NetworkXNoPath:
            path = []
            path_cost = None
        timings.append((perf_counter() - started) * 1000)

    return BenchmarkResult(
        algorithm="networkx",
        mean_ms=round(mean(timings), 4),
        min_ms=round(min(timings), 4),
        max_ms=round(max(timings), 4),
        path_cost=path_cost,
        path=path,
    )
