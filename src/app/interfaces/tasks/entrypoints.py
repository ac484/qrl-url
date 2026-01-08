"""HTTP/Scheduler entrypoints for background tasks."""

import asyncio
import os
from contextlib import asynccontextmanager

from src.app.application.system.use_cases.allocation import AllocationResult, AllocationUseCase


class AllocationInProgressError(Exception):
    """Raised when an allocation run is already in flight."""


_allocation_state_lock = asyncio.Lock()
_allocation_running = False


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
    global _allocation_running
    if not _allow_parallel_allocation():
        async with _allocation_state_lock:
            if _allocation_running:
                raise AllocationInProgressError("Allocation is already running")
            _allocation_running = True
    try:
        yield
    finally:
        if not _allow_parallel_allocation():
            async with _allocation_state_lock:
                _allocation_running = False


async def run_allocation(timeout_seconds: float | None = None) -> AllocationResult:
    """Trigger the allocation use case for Cloud Scheduler with a bounded runtime."""
    usecase = AllocationUseCase()
    timeout = timeout_seconds or _allocation_timeout_seconds()
    async with _singleflight_allocation():
        return await asyncio.wait_for(usecase.execute(), timeout=timeout)
