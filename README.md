# RouteForge

RouteForge is a FastAPI route optimisation service for weighted logistics
networks. It models delivery locations as a persisted directed graph, calculates
routes by cost, distance or travel time, and compares custom graph algorithms
under benchmark conditions.

## What This Demonstrates

- Backend API design with FastAPI, Pydantic validation and RESTful endpoints.
- Custom graph modelling with an adjacency-list weighted directed graph.
- Algorithm implementations for BFS, DFS and Dijkstra without relying on
  NetworkX for the core logic.
- SQLite persistence, benchmark reporting, Docker support and GitHub Actions CI.
- A lightweight browser dashboard for demonstrating the main workflow.

## Quick Start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000/docs` for the interactive API documentation.
Open `http://127.0.0.1:8000/dashboard/` for the dashboard.

Run tests:

```bash
pytest
```

Run linting:

```bash
ruff check .
```

## Project Structure

```text
app/
  algorithms/   BFS, DFS, Dijkstra and path reconstruction
  api/          FastAPI route handlers
  benchmarks/   Runtime comparison helpers
  graph/        Weighted directed graph model and random graph generation
  schemas/      Pydantic request and response models
  storage/      SQLite persistence layer
dashboard/      Small browser UI served by FastAPI
docs/           Architecture documentation
sample_data/    Example API payloads
tests/          Algorithm and API tests
```

## API Workflow

Create a graph:

```bash
curl -X POST http://127.0.0.1:8000/graphs \
  -H "Content-Type: application/json" \
  -d '{"name":"delivery"}'
```

Add vertices:

```bash
curl -X POST http://127.0.0.1:8000/graphs/$GRAPH_ID/vertices \
  -H "Content-Type: application/json" \
  -d '{"id":"warehouse_a"}'
```

Add an edge:

```bash
curl -X POST http://127.0.0.1:8000/graphs/$GRAPH_ID/edges \
  -H "Content-Type: application/json" \
  -d '{"source":"warehouse_a","destination":"hub_3","cost":10,"distance":7,"travel_time":30}'
```

Find an optimised route:

```bash
curl -X POST http://127.0.0.1:8000/graphs/$GRAPH_ID/routes/shortest \
  -H "Content-Type: application/json" \
  -d '{"source":"warehouse_a","destination":"customer_17","optimise_for":"cost"}'
```

Generate a random graph:

```bash
curl -X POST http://127.0.0.1:8000/graphs \
  -H "Content-Type: application/json" \
  -d '{"name":"random","random":{"vertices":100,"edges":300,"seed":7}}'
```

Benchmark:

```bash
curl -X POST http://127.0.0.1:8000/graphs/$GRAPH_ID/benchmarks \
  -H "Content-Type: application/json" \
  -d '{"source":"v0","destination":"v50","optimise_for":"travel_time","runs":10}'
```

## Persistence

Graphs are saved to SQLite in `routeforge.db` by default, so created networks
survive process restarts. Override the database path with:

```bash
export ROUTEFORGE_DB_PATH=/path/to/routeforge.db
```

## Endpoints

| Method | Path | Purpose |
| --- | --- | --- |
| `POST` | `/graphs` | Create an empty or random graph |
| `POST` | `/graphs/{id}/vertices` | Add a location |
| `POST` | `/graphs/{id}/edges` | Add or replace a directed connection |
| `GET` | `/graphs/{id}` | Inspect graph, cycles and components |
| `POST` | `/graphs/{id}/routes/shortest` | Run Dijkstra |
| `POST` | `/graphs/{id}/traverse/bfs` | Breadth-first traversal |
| `POST` | `/graphs/{id}/traverse/dfs` | Depth-first traversal |
| `POST` | `/graphs/{id}/benchmarks` | Compare Dijkstra variants and optional NetworkX |
| `DELETE` | `/graphs/{id}` | Delete graph |

## Algorithms

The core implementation does not depend on NetworkX.

- `WeightedDiGraph` uses an adjacency list: `dict[str, list[Edge]]`.
- BFS uses a project queue and runs in `O(V + E)`.
- DFS uses a project stack and runs in `O(V + E)`.
- Dijkstra with an array repeatedly scans unvisited vertices, giving `O(V^2 + E)`.
- Dijkstra with `heapq` uses a priority queue, giving `O((V + E) log V)`.
- Predecessor tables reconstruct the final path after traversal.
- Negative weights are rejected because Dijkstra assumes non-negative edges.

## Dashboard

The lightweight dashboard in `dashboard/` is served by FastAPI. It supports the
interactive workflow: create a graph, add locations, add weighted directed
connections, calculate an optimised route, and inspect the JSON response.

## Benchmarking Notes

The benchmark endpoint reports mean, minimum and maximum runtime across repeated
runs for both Dijkstra implementations. If NetworkX is installed, it is included
as an external validation reference, not as the main implementation.

Sparse graphs usually favour the heap implementation because fewer edge
relaxations compete with logarithmic queue operations. Dense graphs narrow the
gap because the edge count approaches `V^2`, making both implementations spend
more time relaxing edges.

## Docker

```bash
docker build -t route-forge .
docker run --rm -p 8000:8000 route-forge
```

Then open `http://127.0.0.1:8000/docs` or
`http://127.0.0.1:8000/dashboard/`.

## Quality Gates

Before pushing changes, run:

```bash
ruff check .
pytest
```

The GitHub Actions workflow runs the same checks on every push and pull request.

## Limitations

- The API is single-tenant and has no authentication.
- SQLite persistence is intentionally simple and designed for local demos rather
  than concurrent multi-user workloads.
- Benchmark timings are useful for comparison but are not a substitute for a
  controlled performance lab.
- Random graph generation creates synthetic edge weights; it does not model real
  traffic, driver availability or time windows.
