from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from src.app.domain.value_objects.order_id import OrderId
from src.app.domain.value_objects.order_status import OrderStatus
from src.app.domain.value_objects.quantity import Quantity
from src.app.domain.value_objects.side import Side
from src.app.domain.value_objects.symbol import Symbol
from src.app.domain.value_objects.timestamp import Timestamp


@dataclass
class Order:
    """Order entity limited to QRL/USDT spot."""

    order_id: OrderId
    symbol: Symbol
    side: Side
    status: OrderStatus
    price: Decimal
    quantity: Quantity
    created_at: Timestamp
    updated_at: Timestamp | None = None
