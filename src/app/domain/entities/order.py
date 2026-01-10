from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from src.app.domain.value_objects.order_id import OrderId
from src.app.domain.value_objects.order_status import OrderStatus
from src.app.domain.value_objects.order_type import OrderType
from src.app.domain.value_objects.quantity import Quantity
from src.app.domain.value_objects.side import Side
from src.app.domain.value_objects.symbol import Symbol
from src.app.domain.value_objects.time_in_force import TimeInForce
from src.app.domain.value_objects.timestamp import Timestamp
from src.app.domain.value_objects.qrl_price import QrlPrice


@dataclass
class Order:
    """Order entity limited to QRL/USDT spot."""

    order_id: OrderId
    symbol: Symbol
    side: Side
    order_type: OrderType
    status: OrderStatus
    price: QrlPrice | None
    quantity: Quantity
    created_at: Timestamp
    time_in_force: TimeInForce | None = None
    client_order_id: str | None = None
    executed_quantity: Decimal | None = None
    cumulative_quote_quantity: Decimal | None = None
    updated_at: Timestamp | None = None
