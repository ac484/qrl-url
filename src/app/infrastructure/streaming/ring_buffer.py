from collections import deque
from typing import Deque, Generic, Iterable, TypeVar

T = TypeVar("T")


class RingBuffer(Generic[T]):
    """Fixed-size buffer for lightweight replay/debug."""

    def __init__(self, size: int = 1000):
        self._buffer: Deque[T] = deque(maxlen=size)

    def append(self, item: T) -> None:
        self._buffer.append(item)

    def replay(self) -> Iterable[T]:
        return list(self._buffer)
