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


async def run_allocation(timeout_seconds: float | None = None) -> AllocationResult:
    """Trigger the allocation use case for Cloud Scheduler with a bounded runtime."""
    usecase = AllocationUseCase()
    timeout = timeout_seconds or _allocation_timeout_seconds()
    return await asyncio.wait_for(usecase.execute(), timeout=timeout)
