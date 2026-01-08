import asyncio
import logging
import time
from typing import Mapping

from fastapi import APIRouter, HTTPException, Request
import httpx
from pydantic import ValidationError

from src.app.interfaces.http.schemas import AllocationResponse
from src.app.interfaces.tasks import entrypoints

router = APIRouter()
api_router = APIRouter()
logger = logging.getLogger(__name__)


def _scheduler_metadata(headers: Mapping[str, str] | None) -> dict[str, str | None]:
    """Extract Cloud Scheduler identifiers for observability."""
    headers = headers or {}
    return {
        "job_name": headers.get("X-CloudScheduler-JobName"),
        "retry_count": headers.get("X-CloudScheduler-JobRetryCount"),
        "execution_time": headers.get("X-CloudScheduler-ExecutionTime"),
    }


def _filter_none(data: dict[str, str | None]) -> dict[str, str]:
    return {k: v for k, v in data.items() if v is not None}


async def _trigger_allocation(request: Request | None = None) -> AllocationResponse:
    """Run the allocation task and normalize the response."""
    started = time.perf_counter()
    metadata = _scheduler_metadata(request.headers if request is not None else None)
    status = "error"
    try:
        result = await entrypoints.run_allocation()
        status = result.status
        return AllocationResponse.model_validate(result)
    except entrypoints.AllocationInProgressError as exc:
        raise HTTPException(status_code=429, detail=str(exc))
    except asyncio.TimeoutError:
        raise HTTPException(status_code=504, detail="Allocation task exceeded timeout")
    except (ValidationError, httpx.HTTPError) as exc:
        logger.exception("Allocation failed due to configuration or upstream API error")
        raise HTTPException(status_code=502, detail=str(exc))
    except Exception:
        logger.exception("Unexpected allocation failure")
        raise HTTPException(status_code=500, detail="Allocation task failed")
    finally:
        elapsed_ms = (time.perf_counter() - started) * 1000
        logger.info(
            "allocation.request.complete",
            extra={"elapsed_ms": round(elapsed_ms, 2), "status": status, **_filter_none(metadata)},
        )


@router.api_route(
    "/allocation",
    methods=["POST", "GET"],
    response_model=AllocationResponse,
    tags=["tasks"],
    name="tasks_allocation_trigger",
)
async def trigger_allocation(request: Request) -> AllocationResponse:
    """Endpoint for Cloud Scheduler to trigger an allocation run."""
    return await _trigger_allocation(request)


@api_router.api_route(
    "/allocation",
    methods=["POST", "GET"],
    response_model=AllocationResponse,
    tags=["tasks"],
    name="api_tasks_allocation_trigger",
)
async def trigger_allocation_api(request: Request) -> AllocationResponse:
    """API-aligned alias to trigger allocation under the /api/tasks namespace."""
    return await _trigger_allocation(request)
