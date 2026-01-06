from dataclasses import dataclass, field

from src.app.domain.entities.order_book_level import OrderBookLevel
from src.app.domain.entities.trade import Trade
from src.app.domain.value_objects.symbol import Symbol
from src.app.domain.value_objects.ticker import Ticker
from src.app.domain.value_objects.timestamp import Timestamp


@dataclass
class MarketSnapshot:
    """Combined market view for depth, trades, and ticker."""

    symbol: Symbol
    bids: list[OrderBookLevel] = field(default_factory=list)
    asks: list[OrderBookLevel] = field(default_factory=list)
    trades: list[Trade] = field(default_factory=list)
    ticker: Ticker | None = None
    updated_at: Timestamp | None = None
