from app.algorithms.bfs import breadth_first_search
from app.algorithms.dfs import depth_first_search
from app.algorithms.dijkstra_array import dijkstra_array
from app.algorithms.dijkstra_heap import dijkstra_heap
from app.algorithms.reconstruction import reconstruct_path
from app.graph.adjacency_list import WeightedDiGraph
from app.graph.generators import MAX_RANDOM_EDGES, generate_random_graph


def sample_graph() -> WeightedDiGraph:
    graph = WeightedDiGraph("sample")
    graph.add_edge("warehouse_a", "hub_1", cost=5, distance=10, travel_time=20)
    graph.add_edge("warehouse_a", "hub_2", cost=2, distance=20, travel_time=10)
    graph.add_edge("hub_2", "hub_1", cost=1, distance=2, travel_time=3)
    graph.add_edge("hub_1", "customer_17", cost=4, distance=4, travel_time=5)
    graph.add_edge("hub_2", "customer_17", cost=10, distance=1, travel_time=2)
    return graph


def test_bfs_uses_queue_order() -> None:
    order, predecessors = breadth_first_search(sample_graph(), "warehouse_a")
    assert order == ["warehouse_a", "hub_1", "hub_2", "customer_17"]
    assert predecessors["customer_17"] == "hub_1"


def test_dfs_visits_reachable_vertices() -> None:
    order, predecessors = depth_first_search(sample_graph(), "warehouse_a")
    assert order == ["warehouse_a", "hub_1", "customer_17", "hub_2"]
    assert predecessors["hub_1"] == "warehouse_a"


def test_dijkstra_array_finds_cheapest_path() -> None:
    distances, predecessors, visited = dijkstra_array(sample_graph(), "warehouse_a", "cost")
    assert distances["customer_17"] == 7
    assert reconstruct_path(predecessors, "warehouse_a", "customer_17") == [
        "warehouse_a",
        "hub_2",
        "hub_1",
        "customer_17",
    ]
    assert visited[0] == "warehouse_a"


def test_dijkstra_heap_matches_array_for_all_metrics() -> None:
    graph = sample_graph()
    for metric in ("cost", "distance", "travel_time"):
        array_distances, _, _ = dijkstra_array(graph, "warehouse_a", metric)
        heap_distances, _, _ = dijkstra_heap(graph, "warehouse_a", metric)
        assert heap_distances == array_distances


def test_cycle_and_components() -> None:
    graph = sample_graph()
    assert graph.has_cycle() is False
    graph.add_edge("customer_17", "warehouse_a", cost=1, distance=1, travel_time=1)
    graph.add_vertex("isolated")
    assert graph.has_cycle() is True
    assert graph.weakly_connected_components() == [
        ["customer_17", "hub_1", "hub_2", "warehouse_a"],
        ["isolated"],
    ]


def test_zero_weight_edges_are_supported() -> None:
    graph = WeightedDiGraph("zero")
    graph.add_edge("a", "b", cost=0, distance=0, travel_time=0)
    distances, predecessors, _ = dijkstra_heap(graph, "a", "cost")
    assert distances["b"] == 0
    assert reconstruct_path(predecessors, "a", "b") == ["a", "b"]


def test_random_generator_rejects_oversized_requests() -> None:
    try:
        generate_random_graph(vertices=1_000, edges=MAX_RANDOM_EDGES + 1)
    except ValueError as exc:
        assert "capped" in str(exc)
    else:
        raise AssertionError("oversized random graph should have been rejected")


def test_random_generator_creates_requested_edge_count_without_self_loops() -> None:
    graph = generate_random_graph(vertices=200, edges=1_000, seed=42)
    assert len(graph.vertices()) == 200
    assert graph.edge_count() == 1_000
    assert all(edge.source != edge.destination for edge in graph.edges())
