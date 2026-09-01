from __future__ import annotations

from collections import deque
from typing import Generic, TypeVar

T = TypeVar("T")


class Queue(Generic[T]):
    def __init__(self) -> None:
        self._items: deque[T] = deque()

    def push(self, item: T) -> None:
        self._items.append(item)

    def pop(self) -> T:
        return self._items.popleft()

    def __bool__(self) -> bool:
        return bool(self._items)


class Stack(Generic[T]):
    def __init__(self) -> None:
        self._items: list[T] = []

    def push(self, item: T) -> None:
        self._items.append(item)

    def pop(self) -> T:
        return self._items.pop()

    def __bool__(self) -> bool:
        return bool(self._items)

