from dataclasses import dataclass
from decimal import Decimal
from datetime import datetime, timezone

from src.app.domain.value_objects.symbol import Symbol


@dataclass(frozen=True)
class Ticker:
    """Minimal ticker snapshot for QRL/USDT."""

    symbol: Symbol
    last_price: Decimal
    bid_price: Decimal
    ask_price: Decimal
    ts: datetime

    def __post_init__(self):
        if self.last_price <= 0 or self.bid_price <= 0 or self.ask_price <= 0:
            raise ValueError("Ticker prices must be positive")
        if self.bid_price > self.ask_price:
            raise ValueError("Bid price cannot exceed ask price")
        if self.ts.tzinfo is None:
            object.__setattr__(self, "ts", self.ts.replace(tzinfo=timezone.utc))
