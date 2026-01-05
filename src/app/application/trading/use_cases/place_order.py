"""Trading use case: place order for QRL/USDT."""

from dataclasses import dataclass
from decimal import Decimal

from src.app.application.exchange.mexc_service import MexcService, PlaceOrderRequest, build_mexc_service
from src.app.domain.entities.order import Order
from src.app.domain.value_objects.order_type import OrderType
from src.app.domain.value_objects.price import Price
from src.app.domain.value_objects.quantity import Quantity
from src.app.domain.value_objects.side import Side
from src.app.domain.value_objects.symbol import Symbol
from src.app.domain.value_objects.time_in_force import TimeInForce
from src.app.infrastructure.exchange.mexc.settings import MexcSettings


def _serialize_order(order: Order) -> dict:
    return {
        "order_id": order.order_id.value,
        "symbol": order.symbol.value,
        "side": order.side.value,
        "type": order.order_type.value,
        "status": order.status.value,
        "price": str(order.price),
        "quantity": str(order.quantity.value),
        "executed_quantity": str(order.executed_quantity) if order.executed_quantity else None,
        "cumulative_quote_quantity": str(order.cumulative_quote_quantity)
        if order.cumulative_quote_quantity
        else None,
        "time_in_force": order.time_in_force.value if order.time_in_force else None,
        "client_order_id": order.client_order_id,
        "created_at": order.created_at.value.isoformat(),
        "updated_at": order.updated_at.value.isoformat() if order.updated_at else None,
    }


@dataclass
class PlaceOrderInput:
    symbol: str
    side: str
    quantity: Decimal
    price: Decimal | None
    order_type: str = "LIMIT"
    time_in_force: str = "GTC"
    client_order_id: str | None = None


class PlaceOrderUseCase:
    settings: MexcSettings | None = None

    def __init__(self, settings: MexcSettings | None = None):
        self.settings = settings

    async def execute(self, data: PlaceOrderInput) -> dict:
        request = PlaceOrderRequest(
            symbol=Symbol(data.symbol),
            side=Side(data.side),
            order_type=OrderType(data.order_type),
            quantity=Quantity(data.quantity),
            price=Price(data.price) if data.price is not None else None,
            time_in_force=TimeInForce(data.time_in_force) if data.time_in_force else None,
            client_order_id=data.client_order_id,
        )
        service = build_mexc_service(self.settings or MexcSettings())
        async with service as svc:
            order = await svc.place_order(request)
        return _serialize_order(order)
