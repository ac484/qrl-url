from dataclasses import dataclass

from app.domain.value_objects.order_id import OrderId
from app.domain.value_objects.order_status import OrderStatus
from app.domain.value_objects.price import Price
from app.domain.value_objects.quantity import Quantity
from app.domain.value_objects.symbol import Symbol


@dataclass(frozen=True)
class OrderEvent:
    """Private order update event."""

    order_id: OrderId
    symbol: Symbol
    price: Price
    quantity: Quantity
    status: OrderStatus
    timestamp: int
