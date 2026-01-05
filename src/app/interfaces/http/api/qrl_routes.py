from decimal import Decimal

from fastapi import APIRouter, Query

from src.app.application.market.qrl.get_qrl_depth import GetQrlDepth
from src.app.application.market.qrl.get_qrl_kline import GetQrlKline
from src.app.application.market.qrl.get_qrl_price import GetQrlPrice
from src.app.application.trading.qrl.cancel_qrl_order import CancelQrlOrder
from src.app.application.trading.qrl.get_qrl_order import GetQrlOrder
from src.app.application.trading.qrl.place_qrl_order import PlaceQrlOrder
from src.app.domain.value_objects.qrl_price import QrlPrice
from src.app.domain.value_objects.qrl_quantity import QrlQuantity
from src.app.infrastructure.exchange.mexc.qrl.qrl_rest_client import QrlRestClient
from src.app.infrastructure.exchange.mexc.qrl.qrl_settings import QrlSettings
from src.app.interfaces.http.schemas import PlaceOrderRequest

router = APIRouter()


def _client() -> QrlRestClient:
    return QrlRestClient(QrlSettings())


@router.get("/price")
async def qrl_price():
    usecase = GetQrlPrice(_client())
    data = await usecase.execute()
    data["timestamp"] = data.get("timestamp") or None
    return data


@router.get("/kline")
async def qrl_kline(interval: str = Query(default="1m"), limit: int = Query(default=50, ge=1, le=500)):
    usecase = GetQrlKline(_client(), interval=interval, limit=limit)
    raw = await usecase.execute()
    normalized = [
        {"timestamp": item[0], "open": item[1], "high": item[2], "low": item[3], "close": item[4], "volume": item[5]}
        for item in raw
    ]
    return normalized


@router.get("/depth")
async def qrl_depth(limit: int = Query(default=50, ge=5, le=1000)):
    usecase = GetQrlDepth(_client(), limit=limit)
    return await usecase.execute()


@router.post("/orders")
async def qrl_place_order(request: PlaceOrderRequest):
    usecase = PlaceQrlOrder(_client())
    price_vo = QrlPrice(request.price) if request.price is not None else None
    qty_vo = QrlQuantity(request.quantity)
    return await usecase.execute(
        side=request.side,
        order_type=request.order_type,
        price=price_vo,
        quantity=qty_vo,
        time_in_force=request.time_in_force,
        client_order_id=request.client_order_id,
    )


@router.post("/orders/{order_id}/cancel")
async def qrl_cancel_order(order_id: str):
    usecase = CancelQrlOrder(_client())
    return await usecase.execute(order_id=order_id, client_order_id=None)


@router.get("/orders/{order_id}")
async def qrl_get_order(order_id: str):
    usecase = GetQrlOrder(_client())
    return await usecase.execute(order_id=order_id, client_order_id=None)
