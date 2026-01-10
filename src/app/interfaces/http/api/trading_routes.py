from decimal import Decimal

from fastapi import APIRouter, Depends, Query
from src.app.application.ports.exchange_service import ExchangeServiceFactory
from src.app.application.trading.use_cases.cancel_order import CancelOrderInput, CancelOrderUseCase
from src.app.application.trading.use_cases.get_order import GetOrderInput, GetOrderUseCase
from src.app.application.trading.use_cases.list_orders import ListOrdersUseCase
from src.app.application.trading.use_cases.list_trades import ListTradesUseCase
from src.app.application.trading.use_cases.place_order import PlaceOrderInput, PlaceOrderUseCase
from src.app.interfaces.http.dependencies import get_exchange_factory
from src.app.interfaces.http.schemas import (
    PlaceOrderRequest,
)


router = APIRouter()


@router.post("/orders")
async def place_order(
    request: PlaceOrderRequest, exchange_factory: ExchangeServiceFactory = Depends(get_exchange_factory)
):
    """Place spot order for QRL/USDT (subaccount)."""
    usecase = PlaceOrderUseCase(exchange_factory)
    data = PlaceOrderInput(
        symbol=request.symbol,
        side=request.side,
        quantity=Decimal(request.quantity),
        price=Decimal(request.price) if request.price is not None else None,
        order_type=request.order_type,
        time_in_force=request.time_in_force if request.time_in_force else "GTC",
        client_order_id=request.client_order_id,
    )
    return await usecase.execute(data)


@router.post("/orders/{order_id}/cancel")
async def cancel_order(
    order_id: str,
    symbol: str = Query(default="QRLUSDT"),
    exchange_factory: ExchangeServiceFactory = Depends(get_exchange_factory),
):
    """Cancel an existing order."""
    usecase = CancelOrderUseCase(exchange_factory)
    data = CancelOrderInput(symbol=symbol, order_id=order_id, client_order_id=None)
    return await usecase.execute(data)


@router.get("/orders/{order_id}")
async def get_order(
    order_id: str,
    symbol: str = Query(default="QRLUSDT"),
    exchange_factory: ExchangeServiceFactory = Depends(get_exchange_factory),
):
    """Get order status."""
    usecase = GetOrderUseCase(exchange_factory)
    data = GetOrderInput(symbol=symbol, order_id=order_id, client_order_id=None)
    return await usecase.execute(data)


@router.get("/orders")
async def list_orders(
    symbol: str = Query(default="QRLUSDT"),
    exchange_factory: ExchangeServiceFactory = Depends(get_exchange_factory),
):
    """List recent orders."""
    usecase = ListOrdersUseCase(exchange_factory)
    return await usecase.execute(symbol=symbol)


@router.get("/trades")
async def list_trades(
    symbol: str = Query(default="QRLUSDT"),
    exchange_factory: ExchangeServiceFactory = Depends(get_exchange_factory),
):
    """List recent trades."""
    usecase = ListTradesUseCase(exchange_factory)
    return await usecase.execute(symbol)
