from fastapi import APIRouter, WebSocket

from src.app.application.market.use_cases.get_ticker import GetTickerUseCase
from src.app.application.trading.use_cases.list_orders import ListOrdersUseCase
from src.app.interfaces.http.dependencies import build_exchange_factory

router = APIRouter()


@router.websocket("/market/ticker")
async def ticker_stream(websocket: WebSocket):
    """WebSocket ticker stream placeholder."""
    await websocket.accept()
    exchange_factory = build_exchange_factory()
    usecase = GetTickerUseCase(exchange_factory)
    await usecase.execute()  # TODO: stream data
    await websocket.close()


@router.websocket("/trading/orders")
async def order_stream(websocket: WebSocket):
    """WebSocket order stream placeholder."""
    await websocket.accept()
    exchange_factory = build_exchange_factory()
    usecase = ListOrdersUseCase(exchange_factory)
    await usecase.execute()  # TODO: stream data
    await websocket.close()
