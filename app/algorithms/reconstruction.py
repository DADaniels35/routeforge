from __future__ import annotations


def reconstruct_path(
    predecessors: dict[str, str | None], source: str, destination: str
) -> list[str]:
    if destination not in predecessors:
        return []
    path: list[str] = []
    current: str | None = destination
    while current is not None:
        path.append(current)
        if current == source:
            return list(reversed(path))
        current = predecessors[current]
    return []

