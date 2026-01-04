from fastapi import APIRouter

from src.app.application.account.get_balance import GetBalanceUseCase

router = APIRouter()


@router.get("/balance")
async def get_balance():
    """Get subaccount balance for QRL/USDT."""
    usecase = GetBalanceUseCase()
    return await usecase.execute()
