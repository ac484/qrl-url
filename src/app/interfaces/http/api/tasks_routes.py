import asyncio
import logging

from fastapi import APIRouter, HTTPException
import httpx
from pydantic import ValidationError

from src.app.interfaces.http.schemas import AllocationResponse
from src.app.interfaces.tasks import entrypoints

router = APIRouter()
api_router = APIRouter()
logger = logging.getLogger(__name__)


async def _trigger_allocation() -> AllocationResponse:
    """Run the allocation task and normalize the response."""
    try:
        result = await entrypoints.run_allocation()
    except asyncio.TimeoutError:
        raise HTTPException(status_code=504, detail="Allocation task exceeded timeout")
    except (ValidationError, httpx.HTTPError, ValueError) as exc:
        logger.exception("Allocation failed due to configuration or upstream API error")
        raise HTTPException(status_code=502, detail=str(exc))
    except Exception:
        logger.exception("Unexpected allocation failure")
        raise HTTPException(status_code=500, detail="Allocation task failed")
    return AllocationResponse.model_validate(result)


@router.api_route(
    "/allocation",
    methods=["POST", "GET"],
    response_model=AllocationResponse,
    tags=["tasks"],
    name="tasks_allocation_trigger",
)
async def trigger_allocation() -> AllocationResponse:
    """Endpoint for Cloud Scheduler to trigger an allocation run."""
    return await _trigger_allocation()


@api_router.api_route(
    "/allocation",
    methods=["POST", "GET"],
    response_model=AllocationResponse,
    tags=["tasks"],
    name="api_tasks_allocation_trigger",
)
async def trigger_allocation_api() -> AllocationResponse:
    """API-aligned alias to trigger allocation under the /api/tasks namespace."""
    return await _trigger_allocation()
