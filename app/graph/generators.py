from __future__ import annotations

from random import Random

from app.graph.adjacency_list import WeightedDiGraph

MAX_RANDOM_EDGES = 200_000


def generate_random_graph(
    *,
    vertices: int,
    edges: int | None = None,
    seed: int | None = None,
    dense: bool = False,
) -> WeightedDiGraph:
    if vertices < 1:
        raise ValueError("vertices must be at least 1")
    max_edges = vertices * (vertices - 1)
    target_edges = (
        edges
        if edges is not None
        else (max_edges // 2 if dense else max(vertices - 1, vertices * 2))
    )
    if target_edges < 0 or target_edges > max_edges:
        raise ValueError(f"edges must be between 0 and {max_edges}")
    if target_edges > MAX_RANDOM_EDGES:
        raise ValueError(
            f"random graph generation is capped at {MAX_RANDOM_EDGES} edges; "
            "request fewer edges for an API benchmark"
        )

    rng = Random(seed)
    graph = WeightedDiGraph(name=f"random-{vertices}v-{target_edges}e")
    vertex_ids = [f"v{i}" for i in range(vertices)]
    for vertex in vertex_ids:
        graph.add_vertex(vertex)

    for edge_index in rng.sample(range(max_edges), target_edges):
        source, destination = _edge_index_to_pair(edge_index, vertex_ids)
        distance = round(rng.uniform(1, 500), 2)
        travel_time = round(distance / rng.uniform(25, 75), 2)
        cost = round(distance * rng.uniform(0.7, 2.4), 2)
        graph.add_edge(source, destination, cost=cost, distance=distance, travel_time=travel_time)
    return graph


def _edge_index_to_pair(edge_index: int, vertex_ids: list[str]) -> tuple[str, str]:
    vertex_count = len(vertex_ids)
    source_index = edge_index // (vertex_count - 1)
    destination_index = edge_index % (vertex_count - 1)
    if destination_index >= source_index:
        destination_index += 1
    return vertex_ids[source_index], vertex_ids[destination_index]
