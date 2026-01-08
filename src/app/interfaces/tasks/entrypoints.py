"""HTTP/Scheduler entrypoints for background tasks."""

import asyncio
import os
from contextlib import asynccontextmanager

from src.app.application.system.use_cases.allocation import AllocationResult, AllocationUseCase


class AllocationInProgressError(Exception):
    """Raised when an allocation run is already in flight."""


_allocation_lock = asyncio.Lock()


def _lock_timeout_seconds() -> float:
    """Timeout for attempting to take the allocation lock (seconds)."""
    raw: str | None = os.getenv("ALLOCATION_LOCK_TIMEOUT_SECONDS", "0.1")
    try:
        return float(raw)
    except ValueError:
        return 0.1


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
    acquired = False
    if not _allow_parallel_allocation():
        try:
            acquired = await asyncio.wait_for(
                _allocation_lock.acquire(), timeout=_lock_timeout_seconds()
            )
        except asyncio.TimeoutError as exc:
            raise AllocationInProgressError("Allocation is already running") from exc
    try:
        yield
    finally:
        if acquired:
            _allocation_lock.release()


async def run_allocation(timeout_seconds: float | None = None) -> AllocationResult:
    """Trigger the allocation use case for Cloud Scheduler with a bounded runtime."""
    usecase = AllocationUseCase()
    timeout = timeout_seconds or _allocation_timeout_seconds()
    async with _singleflight_allocation():
        return await asyncio.wait_for(usecase.execute(), timeout=timeout)
