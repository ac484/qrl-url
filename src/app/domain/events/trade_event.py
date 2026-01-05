from dataclasses import dataclass

from app.domain.value_objects.price import Price
from app.domain.value_objects.quantity import Quantity
from app.domain.value_objects.symbol import Symbol
from app.domain.value_objects.trade_id import TradeId


@dataclass(frozen=True)
class TradeEvent:
    """Public trade tick."""

    trade_id: TradeId
    symbol: Symbol
    price: Price
    quantity: Quantity
    is_buyer_maker: bool
    timestamp: int
