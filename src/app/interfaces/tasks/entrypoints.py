"""HTTP/Scheduler entrypoints for background tasks."""

import os
from typing import Any

from src.app.interfaces.tasks.trading_tasks import RebalanceTaskPayload, run_rebalance


async def trigger_rebalance(payload: dict[str, Any]) -> dict:
    """
    Entrypoint for scheduler/task trigger.

    Expected payload keys:
    - profile: strategy profile id (default "default-qrl")
    - dry_run: bool
    - request_id: optional execution UUID
    """
    rebalance_payload = RebalanceTaskPayload(
        profile=payload.get("profile", "default-qrl"),
        dry_run=bool(payload.get("dry_run", True)),
        request_id=payload.get("request_id"),
    )
    return await run_rebalance(rebalance_payload)
