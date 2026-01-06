from fastapi import APIRouter, Query

from src.app.application.trading.use_cases.get_kline import GetKlineUseCase
from src.app.application.trading.use_cases.get_price import GetPriceUseCase


router = APIRouter()


@router.get("/api/price/{symbol}")
async def get_price(symbol: str):
    usecase = GetPriceUseCase()
    return await usecase.execute(symbol)


@router.get("/api/kline/{symbol}/{interval}")
async def get_kline(symbol: str, interval: str, limit: int = Query(default=60, ge=1, le=500)):
    usecase = GetKlineUseCase()
    return await usecase.execute(symbol, interval, limit)
