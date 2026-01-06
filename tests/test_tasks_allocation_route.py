import asyncio
from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient

from main import create_app
from src.app.application.system.use_cases.allocation import AllocationResult
from src.app.interfaces.tasks import entrypoints


@pytest.fixture(autouse=True)
def mock_allocation(monkeypatch):
    async def _mock_run_allocation() -> AllocationResult:
        return AllocationResult(
            request_id="mock-req",
            status="ok",
            executed_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
            action="BUY",
            order_id="mock-order",
        )

    monkeypatch.setattr(entrypoints, "run_allocation", _mock_run_allocation)


def test_allocation_endpoint_allows_get_and_returns_payload():
    app = create_app()
    client = TestClient(app)

    resp = client.get("/tasks/allocation")

    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert data["action"] == "BUY"
    assert data["order_id"] == "mock-order"
    assert data["request_id"] == "mock-req"


def test_allocation_endpoint_returns_504_on_timeout(monkeypatch):
    app = create_app()
    client = TestClient(app)

    async def _timeout_allocation() -> AllocationResult:
        raise asyncio.TimeoutError()

    monkeypatch.setattr(entrypoints, "run_allocation", _timeout_allocation)

    resp = client.get("/tasks/allocation")

    assert resp.status_code == 504
    assert resp.json()["detail"] == "Allocation task exceeded timeout"
