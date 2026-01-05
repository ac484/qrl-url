from fastapi import APIRouter

router = APIRouter()


@router.get("/dashboard")
async def dashboard():
    """Dashboard page controller placeholder."""
    return {"message": "dashboard placeholder"}

