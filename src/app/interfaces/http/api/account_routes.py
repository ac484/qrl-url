from fastapi import APIRouter, HTTPException

from src.app.application.account.use_cases.get_balance import GetBalanceUseCase

router = APIRouter()


@router.get("/balance")
async def get_balance():
    """Get subaccount balance for QRL/USDT."""
    usecase = GetBalanceUseCase()
    try:
        return await usecase.execute()
    except Exception as exc:
        # Surface a clear error to the dashboard instead of a generic 500
        raise HTTPException(status_code=502, detail=f"Failed to fetch balance: {exc}") from exc
