from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

WeightMetric = Literal["cost", "distance", "travel_time"]


@dataclass(frozen=True)
class Edge:
    source: str
    destination: str
    cost: float
    distance: float
    travel_time: float

    def weight(self, metric: WeightMetric) -> float:
        return getattr(self, metric)

