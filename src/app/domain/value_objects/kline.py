from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal

from src.app.domain.value_objects.timestamp import Timestamp


@dataclass(frozen=True)
class KLine:
    """Single candlestick for a trading pair."""

    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: Decimal
    interval: str
    timestamp: Timestamp

    def __post_init__(self):
        if min(self.open, self.high, self.low, self.close) < 0:
            raise ValueError("KLine prices cannot be negative")
        if self.volume < 0:
            raise ValueError("KLine volume cannot be negative")
        if not self.interval:
            raise ValueError("KLine interval is required")

    @classmethod
    def from_raw(
        cls,
        open_price: Decimal,
        high: Decimal,
        low: Decimal,
        close: Decimal,
        volume: Decimal,
        interval: str,
        timestamp_ms: int,
    ) -> "KLine":
        ts = Timestamp(datetime.fromtimestamp(timestamp_ms / 1000, tz=timezone.utc))
        return cls(open=open_price, high=high, low=low, close=close, volume=volume, interval=interval, timestamp=ts)
