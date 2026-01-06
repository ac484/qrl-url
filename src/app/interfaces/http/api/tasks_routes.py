import asyncio

from fastapi import APIRouter, HTTPException

from src.app.interfaces.http.schemas import AllocationResponse
from src.app.interfaces.tasks import entrypoints

router = APIRouter()


@router.api_route("/allocation", methods=["POST", "GET"], response_model=AllocationResponse, tags=["tasks"])
async def trigger_allocation() -> AllocationResponse:
    """Endpoint for Cloud Scheduler to trigger an allocation run."""
    try:
        result = await entrypoints.run_allocation()
    except asyncio.TimeoutError:
        raise HTTPException(status_code=504, detail="Allocation task exceeded timeout")
    return AllocationResponse.model_validate(result)
