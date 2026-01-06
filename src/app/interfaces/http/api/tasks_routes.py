from __future__ import annotations

import os
from typing import Any

from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from pydantic import BaseModel, Field

from src.app.interfaces.tasks.entrypoints import trigger_rebalance

router = APIRouter(prefix="/tasks", tags=["tasks"])


class RebalanceBody(BaseModel):
    profile: str = Field(default="default-qrl", description="Strategy profile identifier")
    dry_run: bool = Field(default=True, description="If true, do not place live orders")
    request_id: str | None = Field(default=None, description="Execution UUID for replay protection")


async def _authorize_scheduler(
    authorization: str | None = Header(default=None, alias="Authorization"),
    scheduler_header: str | None = Header(default=None, alias="X-CloudScheduler"),
) -> None:
    expected_audience = os.getenv("SCHEDULER_AUDIENCE")
    if expected_audience is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Scheduler audience not configured",
        )
    if authorization is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing Authorization header")
    if scheduler_header is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing X-CloudScheduler header",
        )


def _rebalance_handler():
    return trigger_rebalance


@router.post("/rebalance")
async def post_rebalance(
    body: RebalanceBody,
    _auth: Any = Depends(_authorize_scheduler),
    handler=Depends(_rebalance_handler),
):
    """
    Cloud Scheduler / Cloud Tasks entrypoint for QRL/USDT rebalance.

    Validates basic scheduler headers then forwards payload to the task façade.
    """
    result = await handler(body.model_dump())
    return result
