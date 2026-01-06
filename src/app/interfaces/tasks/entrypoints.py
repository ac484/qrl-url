"""HTTP/Scheduler entrypoints for background tasks."""

from src.app.application.system.use_cases.allocation import AllocationResult, AllocationUseCase


async def run_allocation() -> AllocationResult:
    """Trigger the allocation use case for Cloud Scheduler."""
    usecase = AllocationUseCase()
    return await usecase.execute()
