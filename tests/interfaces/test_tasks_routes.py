import sys
import unittest
from pathlib import Path

try:
    from fastapi import FastAPI
    from fastapi.testclient import TestClient
except ImportError:
    raise unittest.SkipTest("fastapi not installed")

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.append(str(SRC))

from src.app.interfaces.http.api import tasks_routes


def _app() -> FastAPI:
    app = FastAPI()
    app.include_router(tasks_routes.router)
    return app


def test_rebalance_requires_auth_headers(monkeypatch):
    monkeypatch.setenv("SCHEDULER_AUDIENCE", "test-audience")
    client = TestClient(_app())

    res = client.post("/tasks/rebalance", json={"profile": "p1"})

    assert res.status_code == 401


def test_rebalance_accepts_valid_headers(monkeypatch):
    monkeypatch.setenv("SCHEDULER_AUDIENCE", "test-audience")
    app = _app()

    async def fake_handler(payload):
        return {"request_id": "r1", "dry_run": payload.get("dry_run", True)}

    app.dependency_overrides[tasks_routes._rebalance_handler] = lambda: fake_handler

    client = TestClient(app)

    res = client.post(
        "/tasks/rebalance",
        headers={"Authorization": "Bearer token", "X-CloudScheduler": "true"},
        json={"profile": "default-qrl", "dry_run": True},
    )

    assert res.status_code == 200
    body = res.json()
    assert "request_id" in body
    assert body["dry_run"] is True
