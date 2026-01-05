from fastapi import APIRouter

from src.app.application.market.use_cases.get_depth import GetDepthUseCase
from src.app.application.market.use_cases.get_kline import GetKlineUseCase
from src.app.application.market.use_cases.get_stats24h import GetStats24HUseCase
from src.app.application.market.use_cases.get_ticker import GetTickerUseCase

router = APIRouter()


@router.get("/depth")
async def get_depth():
    """Get order book depth for QRL/USDT."""
    usecase = GetDepthUseCase()
    return await usecase.execute()


@router.get("/ticker")
async def get_ticker():
    """Get ticker for QRL/USDT."""
    usecase = GetTickerUseCase()
    return await usecase.execute()


@router.get("/kline")
async def get_kline():
    """Get kline data for QRL/USDT."""
    usecase = GetKlineUseCase()
    return await usecase.execute()


@router.get("/stats24h")
async def get_stats_24h():
    """Get 24h statistics for QRL/USDT."""
    usecase = GetStats24HUseCase()
    return await usecase.execute()

