from fastapi import APIRouter

from src.app.interfaces.http.schemas import AllocationResponse
from src.app.interfaces.tasks import entrypoints

router = APIRouter()


@router.post("/allocation", response_model=AllocationResponse, tags=["tasks"])
async def trigger_allocation() -> AllocationResponse:
    """Endpoint for Cloud Scheduler to trigger an allocation run."""
    result = await entrypoints.run_allocation()
    return AllocationResponse.model_validate(result)
