import asyncio
from datetime import datetime, timezone

import pytest

from src.app.application.system.use_cases.allocation import AllocationResult
from src.app.interfaces.tasks import entrypoints


@pytest.mark.asyncio
async def test_run_allocation_coalesces_concurrent_calls(monkeypatch):
    entrypoints._reset_allocation_singleflight()
    calls: list[str] = []

    class DummyAllocationUseCase:
        async def execute(self) -> AllocationResult:
            calls.append("run")
            await asyncio.sleep(0.01)
            return AllocationResult(
                request_id="single-flight",
                status="ok",
                executed_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
                action="BUY",
                order_id="mock-order",
            )

    monkeypatch.setattr(entrypoints, "AllocationUseCase", DummyAllocationUseCase)

    result_one, result_two = await asyncio.gather(
        entrypoints.run_allocation(timeout_seconds=0.5),
        entrypoints.run_allocation(timeout_seconds=0.5),
    )

    assert calls == ["run"]
    assert result_one.request_id == result_two.request_id == "single-flight"
    entrypoints._reset_allocation_singleflight()
