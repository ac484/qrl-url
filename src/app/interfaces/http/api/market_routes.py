from fastapi import APIRouter, Query

from src.app.application.market.use_cases.get_depth import GetDepthUseCase
from src.app.application.market.use_cases.get_kline import GetKlineUseCase
from src.app.application.market.use_cases.get_stats24h import GetStats24hUseCase
from src.app.application.market.use_cases.get_ticker import GetTickerUseCase

router = APIRouter()


@router.get("/depth")
async def get_depth(limit: int = Query(default=50, ge=5, le=1000)):
    """Get order book depth for QRL/USDT."""
    usecase = GetDepthUseCase()
    from src.app.application.market.use_cases.get_depth import GetDepthInput

    return await usecase.execute(data=GetDepthInput(limit=limit))


@router.get("/ticker")
async def get_ticker():
    """Get ticker for QRL/USDT."""
    usecase = GetTickerUseCase()
    return await usecase.execute()


@router.get("/kline")
async def get_kline(interval: str = Query(default="1m"), limit: int = Query(default=50, ge=1, le=500)):
    """Get kline data for QRL/USDT."""
    usecase = GetKlineUseCase()
    from src.app.application.market.use_cases.get_kline import GetKlineInput

    return await usecase.execute(data=GetKlineInput(interval=interval, limit=limit))


@router.get("/stats24h")
async def get_stats_24h():
    """Get 24h statistics for QRL/USDT."""
    usecase = GetStats24hUseCase()
    return await usecase.execute()
