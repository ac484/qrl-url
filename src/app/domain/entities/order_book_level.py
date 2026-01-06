from dataclasses import dataclass
from decimal import Decimal

from src.app.domain.value_objects.order_side import OrderSide


@dataclass
class OrderBookLevel:
    """Single depth level for the QRL/USDT order book."""

    price: Decimal
    quantity: Decimal
    side: OrderSide
