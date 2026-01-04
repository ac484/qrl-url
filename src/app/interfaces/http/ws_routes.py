from fastapi import APIRouter, WebSocket

from src.app.application.market.get_ticker import GetTickerUseCase
from src.app.application.trading.list_orders import ListOrdersUseCase

router = APIRouter()


@router.websocket("/market/ticker")
async def ticker_stream(websocket: WebSocket):
    """WebSocket ticker stream placeholder."""
    await websocket.accept()
    usecase = GetTickerUseCase()
    await usecase.execute()  # TODO: stream data
    await websocket.close()


@router.websocket("/trading/orders")
async def order_stream(websocket: WebSocket):
    """WebSocket order stream placeholder."""
    await websocket.accept()
    usecase = ListOrdersUseCase()
    await usecase.execute()  # TODO: stream data
    await websocket.close()
