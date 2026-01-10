from fastapi import APIRouter, Depends, Query

from src.app.application.market.use_cases.get_depth import GetDepthInput, GetDepthUseCase
from src.app.application.market.use_cases.get_kline import GetKlineInput, GetKlineUseCase
from src.app.application.market.use_cases.get_market_trades import GetMarketTradesInput, GetMarketTradesUseCase
from src.app.application.market.use_cases.get_stats24h import GetStats24hUseCase
from src.app.application.market.use_cases.get_ticker import GetTickerUseCase
from src.app.application.ports.exchange_service import ExchangeServiceFactory
from src.app.interfaces.http.dependencies import get_exchange_factory

router = APIRouter()


@router.get("/depth")
async def get_depth(
    limit: int = Query(default=50, ge=5, le=1000),
    exchange_factory: ExchangeServiceFactory = Depends(get_exchange_factory),
):
    """Get order book depth for QRL/USDT."""
    usecase = GetDepthUseCase(exchange_factory)
    return await usecase.execute(data=GetDepthInput(limit=limit))


@router.get("/ticker")
async def get_ticker(exchange_factory: ExchangeServiceFactory = Depends(get_exchange_factory)):
    """Get ticker for QRL/USDT."""
    usecase = GetTickerUseCase(exchange_factory)
    return await usecase.execute()


@router.get("/kline")
async def get_kline(
    interval: str = Query(default="1m"),
    limit: int = Query(default=50, ge=1, le=500),
    exchange_factory: ExchangeServiceFactory = Depends(get_exchange_factory),
):
    """Get kline data for QRL/USDT."""
    usecase = GetKlineUseCase(exchange_factory)
    return await usecase.execute(data=GetKlineInput(interval=interval, limit=limit))


@router.get("/stats24h")
async def get_stats_24h(exchange_factory: ExchangeServiceFactory = Depends(get_exchange_factory)):
    """Get 24h statistics for QRL/USDT."""
    usecase = GetStats24hUseCase(exchange_factory)
    return await usecase.execute()


@router.get("/trades")
async def get_market_trades(
    limit: int = Query(default=50, ge=1, le=500),
    exchange_factory: ExchangeServiceFactory = Depends(get_exchange_factory),
):
    """Get recent public trades for QRL/USDT."""
    usecase = GetMarketTradesUseCase(exchange_factory)
    return await usecase.execute(data=GetMarketTradesInput(limit=limit))
