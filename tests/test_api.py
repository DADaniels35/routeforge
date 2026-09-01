from fastapi.testclient import TestClient

from app.api.routes import GRAPHS, STORE
from app.main import app

client = TestClient(app)


def setup_function() -> None:
    GRAPHS.clear()
    STORE.clear()


def test_complete_graph_route_and_benchmark_workflow() -> None:
    response = client.post("/graphs", json={"name": "delivery"})
    assert response.status_code == 201
    graph_id = response.json()["id"]

    for vertex in ["warehouse_a", "hub_3", "hub_8", "customer_17"]:
        assert client.post(f"/graphs/{graph_id}/vertices", json={"id": vertex}).status_code == 200

    edges = [
        ("warehouse_a", "hub_3", 10, 7, 30),
        ("hub_3", "hub_8", 12, 6, 20),
        ("hub_8", "customer_17", 20.7, 8, 25),
        ("warehouse_a", "customer_17", 60, 4, 5),
    ]
    for source, destination, cost, distance, travel_time in edges:
        response = client.post(
            f"/graphs/{graph_id}/edges",
            json={
                "source": source,
                "destination": destination,
                "cost": cost,
                "distance": distance,
                "travel_time": travel_time,
            },
        )
        assert response.status_code == 200

    route = client.post(
        f"/graphs/{graph_id}/routes/shortest",
        json={
            "source": "warehouse_a",
            "destination": "customer_17",
            "optimise_for": "cost",
        },
    )
    assert route.status_code == 200
    body = route.json()
    assert body["path"] == ["warehouse_a", "hub_3", "hub_8", "customer_17"]
    assert body["total_weight"] == 42.7
    assert body["algorithm"] == "dijkstra_heap"
    assert body["visited_vertices"] >= 1

    traversal = client.post(f"/graphs/{graph_id}/traverse/bfs", json={"start": "warehouse_a"})
    assert traversal.status_code == 200
    assert traversal.json()["order"][0] == "warehouse_a"

    benchmark = client.post(
        f"/graphs/{graph_id}/benchmarks",
        json={
            "source": "warehouse_a",
            "destination": "customer_17",
            "optimise_for": "cost",
            "runs": 2,
        },
    )
    assert benchmark.status_code == 200
    algorithms = {result["algorithm"] for result in benchmark.json()["results"]}
    assert {"dijkstra_array", "dijkstra_heap"}.issubset(algorithms)


def test_random_graph_creation_validates_edge_count() -> None:
    response = client.post(
        "/graphs",
        json={"name": "bad", "random": {"vertices": 3, "edges": 99}},
    )
    assert response.status_code == 422


def test_graph_persists_after_memory_cache_is_cleared() -> None:
    graph = client.post("/graphs", json={"name": "persistent"}).json()
    graph_id = graph["id"]
    client.post(f"/graphs/{graph_id}/vertices", json={"id": "depot"})

    GRAPHS.clear()

    response = client.get(f"/graphs/{graph_id}")
    assert response.status_code == 200
    assert response.json()["vertices"] == ["depot"]


def test_invalid_start_vertex_returns_422() -> None:
    graph_id = client.post("/graphs", json={"name": "invalid"}).json()["id"]
    response = client.post(f"/graphs/{graph_id}/traverse/bfs", json={"start": "missing"})
    assert response.status_code == 422


def test_unreachable_destination_returns_404() -> None:
    graph_id = client.post("/graphs", json={"name": "split"}).json()["id"]
    client.post(f"/graphs/{graph_id}/vertices", json={"id": "a"})
    client.post(f"/graphs/{graph_id}/vertices", json={"id": "b"})

    response = client.post(
        f"/graphs/{graph_id}/routes/shortest",
        json={"source": "a", "destination": "b"},
    )
    assert response.status_code == 404


def test_edge_replacement_updates_weight() -> None:
    graph_id = client.post("/graphs", json={"name": "replace"}).json()["id"]
    payload = {"source": "a", "destination": "b", "cost": 5, "distance": 5, "travel_time": 5}
    client.post(f"/graphs/{graph_id}/edges", json=payload)
    client.post(f"/graphs/{graph_id}/edges", json={**payload, "cost": 2})

    response = client.get(f"/graphs/{graph_id}")
    assert response.json()["edge_count"] == 1
    assert response.json()["edges"][0]["cost"] == 2
