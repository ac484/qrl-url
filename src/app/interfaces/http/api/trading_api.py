from fastapi import APIRouter, Depends, Query

from src.app.application.ports.exchange_service import ExchangeServiceFactory
from src.app.application.trading.use_cases.get_kline import GetKlineUseCase
from src.app.application.trading.use_cases.get_price import GetPriceUseCase
from src.app.interfaces.http.dependencies import get_exchange_factory


router = APIRouter()


@router.get("/api/price/{symbol}")
async def get_price(symbol: str, exchange_factory: ExchangeServiceFactory = Depends(get_exchange_factory)):
    usecase = GetPriceUseCase(exchange_factory)
    return await usecase.execute(symbol)


@router.get("/api/kline/{symbol}/{interval}")
async def get_kline(
    symbol: str,
    interval: str,
    limit: int = Query(default=60, ge=1, le=500),
    exchange_factory: ExchangeServiceFactory = Depends(get_exchange_factory),
):
    usecase = GetKlineUseCase(exchange_factory)
    return await usecase.execute(symbol, interval, limit)
