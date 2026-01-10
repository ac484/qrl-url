from fastapi import APIRouter, Depends, HTTPException

from src.app.application.account.use_cases.get_balance import GetBalanceUseCase
from src.app.application.ports.exchange_service import ExchangeServiceFactory
from src.app.interfaces.http.dependencies import get_exchange_factory

router = APIRouter()


@router.get("/balance")
async def get_balance(exchange_factory: ExchangeServiceFactory = Depends(get_exchange_factory)):
    """Get subaccount balance for QRL/USDT."""
    usecase = GetBalanceUseCase(exchange_factory)
    try:
        return await usecase.execute()
    except Exception as exc:
        # Surface a clear error to the dashboard instead of a generic 500
        raise HTTPException(status_code=502, detail=f"Failed to fetch balance: {exc}") from exc
