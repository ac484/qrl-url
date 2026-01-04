from fastapi import APIRouter

from src.app.application.trading.cancel_order import CancelOrderUseCase
from src.app.application.trading.get_order import GetOrderUseCase
from src.app.application.trading.list_orders import ListOrdersUseCase
from src.app.application.trading.list_trades import ListTradesUseCase
from src.app.application.trading.place_order import PlaceOrderUseCase

router = APIRouter()


@router.post("/orders")
async def place_order():
    """Place spot order for QRL/USDT (subaccount)."""
    usecase = PlaceOrderUseCase()
    return await usecase.execute()


@router.post("/orders/{order_id}/cancel")
async def cancel_order(order_id: str):
    """Cancel an existing order."""
    usecase = CancelOrderUseCase()
    return await usecase.execute(order_id=order_id)


@router.get("/orders/{order_id}")
async def get_order(order_id: str):
    """Get order status."""
    usecase = GetOrderUseCase()
    return await usecase.execute(order_id=order_id)


@router.get("/orders")
async def list_orders():
    """List recent orders."""
    usecase = ListOrdersUseCase()
    return await usecase.execute()


@router.get("/trades")
async def list_trades():
    """List recent trades."""
    usecase = ListTradesUseCase()
    return await usecase.execute()
