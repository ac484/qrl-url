"""HTTP/Scheduler entrypoints for background tasks."""

import asyncio
import os

from src.app.application.system.use_cases.allocation import AllocationResult, AllocationUseCase


def _allocation_timeout_seconds() -> float:
    """Read the scheduler task timeout from the environment."""
    raw: str | None = os.getenv("TASK_TIMEOUT_SECONDS", "20")
    try:
        return float(raw)
    except ValueError:
        return 20.0


_allocation_singleflight_lock = asyncio.Lock()
_inflight_allocation: asyncio.Task[AllocationResult] | None = None


def _clear_inflight(task: asyncio.Task[AllocationResult]) -> None:
    """Clear the cached task when it completes."""
    global _inflight_allocation
    if task is _inflight_allocation and task.done():
        _inflight_allocation = None


async def _run_allocation_once(timeout_seconds: float) -> AllocationResult:
    """Execute the allocation use case once with timeout enforcement."""
    usecase = AllocationUseCase()
    return await asyncio.wait_for(usecase.execute(), timeout=timeout_seconds)


async def run_allocation(timeout_seconds: float | None = None) -> AllocationResult:
    """Trigger allocation with a single-flight guard to avoid duplicate runs."""
    global _inflight_allocation
    timeout = timeout_seconds or _allocation_timeout_seconds()

    async with _allocation_singleflight_lock:
        if _inflight_allocation is None or _inflight_allocation.done():
            _inflight_allocation = asyncio.create_task(_run_allocation_once(timeout))
            _inflight_allocation.add_done_callback(_clear_inflight)
        task = _inflight_allocation

    return await asyncio.wait_for(asyncio.shield(task), timeout=timeout)


def _reset_allocation_singleflight() -> None:
    """Reset cached allocation state (primarily for tests)."""
    global _inflight_allocation
    _inflight_allocation = None
