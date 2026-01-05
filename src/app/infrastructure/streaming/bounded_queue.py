import asyncio
from typing import Generic, TypeVar

T = TypeVar("T")


class BoundedAsyncQueue(Generic[T]):
    """Async queue with backpressure for WS message ingestion."""

    def __init__(self, max_size: int = 1000):
        self._queue: asyncio.Queue[T] = asyncio.Queue(maxsize=max_size)

    async def push(self, item: T) -> None:
        await self._queue.put(item)

    async def pull(self) -> T:
        return await self._queue.get()
