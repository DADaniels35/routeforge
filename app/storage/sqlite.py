from __future__ import annotations

import os
import sqlite3
from pathlib import Path

from app.graph.adjacency_list import WeightedDiGraph


class SQLiteGraphStore:
    def __init__(self, db_path: str | None = None) -> None:
        self.db_path = Path(db_path or os.getenv("ROUTEFORGE_DB_PATH", "routeforge.db"))
        self.initialise()

    def connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.db_path)
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    def initialise(self) -> None:
        with self.connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS graphs (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS vertices (
                    graph_id TEXT NOT NULL,
                    id TEXT NOT NULL,
                    PRIMARY KEY (graph_id, id),
                    FOREIGN KEY (graph_id) REFERENCES graphs(id) ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS edges (
                    graph_id TEXT NOT NULL,
                    source TEXT NOT NULL,
                    destination TEXT NOT NULL,
                    cost REAL NOT NULL,
                    distance REAL NOT NULL,
                    travel_time REAL NOT NULL,
                    PRIMARY KEY (graph_id, source, destination),
                    FOREIGN KEY (graph_id) REFERENCES graphs(id) ON DELETE CASCADE
                );
                """
            )

    def save_graph(self, graph_id: str, graph: WeightedDiGraph) -> None:
        with self.connect() as connection:
            connection.execute(
                "INSERT INTO graphs(id, name) VALUES(?, ?) "
                "ON CONFLICT(id) DO UPDATE SET name = excluded.name",
                (graph_id, graph.name),
            )
            connection.execute("DELETE FROM vertices WHERE graph_id = ?", (graph_id,))
            connection.execute("DELETE FROM edges WHERE graph_id = ?", (graph_id,))
            connection.executemany(
                "INSERT INTO vertices(graph_id, id) VALUES(?, ?)",
                [(graph_id, vertex) for vertex in graph.vertices()],
            )
            connection.executemany(
                """
                INSERT INTO edges(graph_id, source, destination, cost, distance, travel_time)
                VALUES(?, ?, ?, ?, ?, ?)
                """,
                [
                    (
                        graph_id,
                        edge.source,
                        edge.destination,
                        edge.cost,
                        edge.distance,
                        edge.travel_time,
                    )
                    for edge in graph.edges()
                ],
            )

    def load_graph(self, graph_id: str) -> WeightedDiGraph | None:
        with self.connect() as connection:
            graph_row = connection.execute(
                "SELECT name FROM graphs WHERE id = ?", (graph_id,)
            ).fetchone()
            if graph_row is None:
                return None

            graph = WeightedDiGraph(name=graph_row[0])
            for (vertex_id,) in connection.execute(
                "SELECT id FROM vertices WHERE graph_id = ? ORDER BY id", (graph_id,)
            ):
                graph.add_vertex(vertex_id)
            for row in connection.execute(
                """
                SELECT source, destination, cost, distance, travel_time
                FROM edges
                WHERE graph_id = ?
                ORDER BY source, destination
                """,
                (graph_id,),
            ):
                graph.add_edge(
                    row[0],
                    row[1],
                    cost=row[2],
                    distance=row[3],
                    travel_time=row[4],
                )
            return graph

    def delete_graph(self, graph_id: str) -> bool:
        with self.connect() as connection:
            cursor = connection.execute("DELETE FROM graphs WHERE id = ?", (graph_id,))
            return cursor.rowcount > 0

    def clear(self) -> None:
        with self.connect() as connection:
            connection.execute("DELETE FROM graphs")

