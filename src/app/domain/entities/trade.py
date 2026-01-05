from dataclasses import dataclass
from decimal import Decimal

from src.app.domain.value_objects.order_id import OrderId
from src.app.domain.value_objects.side import Side
from src.app.domain.value_objects.symbol import Symbol
from src.app.domain.value_objects.timestamp import Timestamp
from src.app.domain.value_objects.trade_id import TradeId


@dataclass
class Trade:
    """Trade fill record."""

    trade_id: TradeId
    order_id: OrderId
    symbol: Symbol
    side: Side
    price: Decimal
    quantity: Decimal
    fee: Decimal | None
    fee_asset: str | None
    timestamp: Timestamp
