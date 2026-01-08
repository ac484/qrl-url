"""HTTP/Scheduler entrypoints for background tasks."""

import asyncio
import os
from contextlib import asynccontextmanager

from src.app.application.system.use_cases.allocation import AllocationResult, AllocationUseCase


class AllocationInProgressError(Exception):
    """Raised when an allocation run is already in flight."""


class _AllocationGuard:
    def __init__(self) -> None:
        self._lock = asyncio.Lock()
        self._running = False

    async def acquire(self, allow_parallel: bool) -> bool:
        """Return True if a lock was taken and must be released."""
        if allow_parallel:
            return False
        async with self._lock:
            if self._running:
                raise AllocationInProgressError("Allocation is already running")
            self._running = True
        return True

    async def release(self, release_needed: bool) -> None:
        if not release_needed:
            return
        async with self._lock:
            self._running = False


_allocation_guard = _AllocationGuard()


def _allocation_timeout_seconds() -> float:
    """Read the scheduler task timeout from the environment."""
    raw: str | None = os.getenv("TASK_TIMEOUT_SECONDS", "20")
    try:
        return float(raw)
    except ValueError:
        return 20.0


def _allow_parallel_allocation() -> bool:
    """Return True when parallel allocation runs are explicitly allowed."""
    return os.getenv("ALLOW_PARALLEL_ALLOCATION", "0") == "1"


@asynccontextmanager
async def _singleflight_allocation():
    """Guard to prevent overlapping allocation runs on the same instance."""
    allow_parallel = _allow_parallel_allocation()
    release_needed = await _allocation_guard.acquire(allow_parallel)
    try:
        yield
    finally:
        await _allocation_guard.release(release_needed)


async def run_allocation(timeout_seconds: float | None = None) -> AllocationResult:
    """Trigger the allocation use case for Cloud Scheduler with a bounded runtime."""
    usecase = AllocationUseCase()
    timeout = timeout_seconds or _allocation_timeout_seconds()
    async with _singleflight_allocation():
        return await asyncio.wait_for(usecase.execute(), timeout=timeout)
