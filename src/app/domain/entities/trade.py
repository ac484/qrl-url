from dataclasses import dataclass
from decimal import Decimal

from src.app.domain.value_objects.order_id import OrderId
from src.app.domain.value_objects.side import Side
from src.app.domain.value_objects.symbol import Symbol
from src.app.domain.value_objects.timestamp import Timestamp
from src.app.domain.value_objects.trade_id import TradeId
from src.app.domain.value_objects.qrl_price import QrlPrice
from src.app.domain.value_objects.quantity import Quantity


@dataclass
class Trade:
    """Trade fill record."""

    trade_id: TradeId
    order_id: OrderId
    symbol: Symbol
    side: Side
    price: QrlPrice
    quantity: Quantity
    fee: Decimal | None
    fee_asset: str | None
    timestamp: Timestamp
