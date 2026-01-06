from dataclasses import dataclass, field

from src.app.domain.entities.order import Order
from src.app.domain.entities.trade import Trade
from src.app.domain.value_objects.symbol import Symbol
from src.app.domain.value_objects.timestamp import Timestamp


@dataclass
class TradingSession:
    """Session-level aggregate for managing open and historical activity."""

    symbol: Symbol
    open_orders: list[Order] = field(default_factory=list)
    trades: list[Trade] = field(default_factory=list)
    started_at: Timestamp | None = None
    last_activity_at: Timestamp | None = None
