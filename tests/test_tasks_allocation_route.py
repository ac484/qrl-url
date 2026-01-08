import asyncio
from datetime import datetime, timezone
import httpx

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


def test_allocation_endpoint_available_under_api_prefix():
    app = create_app()
    client = TestClient(app)

    resp = client.get("/api/tasks/allocation")

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


def test_allocation_endpoint_returns_429_on_parallel_request(monkeypatch):
    app = create_app()
    client = TestClient(app)

    async def _busy():
        raise entrypoints.AllocationInProgressError("Allocation is already running")

    monkeypatch.setattr(entrypoints, "run_allocation", _busy)

    resp = client.get("/tasks/allocation")

    assert resp.status_code == 429
    assert resp.json()["detail"] == "Allocation is already running"


def test_allocation_endpoint_returns_502_on_upstream_error(monkeypatch):
    app = create_app()
    client = TestClient(app)

    async def _upstream_failure():
        raise httpx.HTTPError("mexc unreachable")

    monkeypatch.setattr(entrypoints, "run_allocation", _upstream_failure)

    resp = client.get("/tasks/allocation")

    assert resp.status_code == 502
    assert "mexc unreachable" in resp.json()["detail"]
