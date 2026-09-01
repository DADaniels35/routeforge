from __future__ import annotations

from time import perf_counter
from uuid import uuid4

from fastapi import APIRouter, HTTPException, status

from app.algorithms.bfs import breadth_first_search
from app.algorithms.dfs import depth_first_search
from app.algorithms.dijkstra_array import dijkstra_array
from app.algorithms.dijkstra_heap import dijkstra_heap
from app.algorithms.reconstruction import reconstruct_path
from app.benchmarks.runner import benchmark_graph
from app.graph.adjacency_list import WeightedDiGraph
from app.graph.generators import generate_random_graph
from app.schemas.graphs import (
    BenchmarkRequest,
    BenchmarkResponse,
    CreateGraphRequest,
    EdgeRequest,
    GraphResponse,
    RouteRequest,
    RouteResponse,
    TraversalRequest,
    TraversalResponse,
    VertexRequest,
)
from app.storage.sqlite import SQLiteGraphStore

router = APIRouter()
GRAPHS: dict[str, WeightedDiGraph] = {}
STORE = SQLiteGraphStore()


def get_graph_or_404(graph_id: str) -> WeightedDiGraph:
    graph = GRAPHS.get(graph_id)
    if graph is None:
        graph = STORE.load_graph(graph_id)
        if graph is None:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND,
                detail=f"Graph '{graph_id}' was not found",
            )
        GRAPHS[graph_id] = graph
    return graph


@router.post("/graphs", status_code=status.HTTP_201_CREATED, response_model=GraphResponse)
def create_graph(request: CreateGraphRequest) -> GraphResponse:
    graph_id = str(uuid4())
    if request.random:
        try:
            graph = generate_random_graph(
                vertices=request.random.vertices,
                edges=request.random.edges,
                seed=request.random.seed,
                dense=request.random.dense,
            )
        except ValueError as exc:
            raise HTTPException(422, detail=str(exc)) from exc
    else:
        graph = WeightedDiGraph(name=request.name)
    GRAPHS[graph_id] = graph
    STORE.save_graph(graph_id, graph)
    return GraphResponse.from_graph(graph_id, graph)


@router.post("/graphs/{graph_id}/vertices", response_model=GraphResponse)
def add_vertex(graph_id: str, request: VertexRequest) -> GraphResponse:
    graph = get_graph_or_404(graph_id)
    graph.add_vertex(request.id)
    STORE.save_graph(graph_id, graph)
    return GraphResponse.from_graph(graph_id, graph)


@router.post("/graphs/{graph_id}/edges", response_model=GraphResponse)
def add_edge(graph_id: str, request: EdgeRequest) -> GraphResponse:
    graph = get_graph_or_404(graph_id)
    graph.add_edge(
        request.source,
        request.destination,
        cost=request.cost,
        distance=request.distance,
        travel_time=request.travel_time,
    )
    STORE.save_graph(graph_id, graph)
    return GraphResponse.from_graph(graph_id, graph)


@router.get("/graphs/{graph_id}", response_model=GraphResponse)
def get_graph(graph_id: str) -> GraphResponse:
    return GraphResponse.from_graph(graph_id, get_graph_or_404(graph_id))


@router.post("/graphs/{graph_id}/routes/shortest", response_model=RouteResponse)
def shortest_route(graph_id: str, request: RouteRequest) -> RouteResponse:
    graph = get_graph_or_404(graph_id)
    algorithm = dijkstra_array if request.algorithm == "dijkstra_array" else dijkstra_heap
    started = perf_counter()
    distances, predecessors, visited_order = algorithm(graph, request.source, request.optimise_for)
    elapsed_ms = (perf_counter() - started) * 1000

    if request.destination not in distances or distances[request.destination] == float("inf"):
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            detail=f"No route from '{request.source}' to '{request.destination}'",
        )

    return RouteResponse(
        path=reconstruct_path(predecessors, request.source, request.destination),
        total_weight=distances[request.destination],
        visited_vertices=len(visited_order),
        visited_order=visited_order,
        algorithm=request.algorithm,
        optimise_for=request.optimise_for,
        execution_time_ms=round(elapsed_ms, 4),
    )


@router.post("/graphs/{graph_id}/traverse/bfs", response_model=TraversalResponse)
def traverse_bfs(graph_id: str, request: TraversalRequest) -> TraversalResponse:
    graph = get_graph_or_404(graph_id)
    started = perf_counter()
    order, predecessors = breadth_first_search(graph, request.start)
    return TraversalResponse(
        algorithm="bfs",
        start=request.start,
        order=order,
        predecessors=predecessors,
        visited_vertices=len(order),
        execution_time_ms=round((perf_counter() - started) * 1000, 4),
    )


@router.post("/graphs/{graph_id}/traverse/dfs", response_model=TraversalResponse)
def traverse_dfs(graph_id: str, request: TraversalRequest) -> TraversalResponse:
    graph = get_graph_or_404(graph_id)
    started = perf_counter()
    order, predecessors = depth_first_search(graph, request.start)
    return TraversalResponse(
        algorithm="dfs",
        start=request.start,
        order=order,
        predecessors=predecessors,
        visited_vertices=len(order),
        execution_time_ms=round((perf_counter() - started) * 1000, 4),
    )


@router.post("/graphs/{graph_id}/benchmarks", response_model=BenchmarkResponse)
def run_benchmark(graph_id: str, request: BenchmarkRequest) -> BenchmarkResponse:
    graph = get_graph_or_404(graph_id)
    return benchmark_graph(
        graph,
        source=request.source,
        destination=request.destination,
        optimise_for=request.optimise_for,
        runs=request.runs,
        include_networkx=request.include_networkx,
    )


@router.delete("/graphs/{graph_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_graph(graph_id: str) -> None:
    get_graph_or_404(graph_id)
    GRAPHS.pop(graph_id, None)
    STORE.delete_graph(graph_id)
