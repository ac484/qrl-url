"""Kline (candlestick) value object."""

from dataclasses import dataclass
from decimal import Decimal
from datetime import datetime


@dataclass(frozen=True)
class Kline:
    """Kline/candlestick data for a specific time period."""
    
    open_time: datetime
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: Decimal
    close_time: datetime
    quote_volume: Decimal
    
    def __post_init__(self):
        """Validate kline data."""
        if self.high < self.low:
            raise ValueError("High price cannot be less than low price")
        if self.high < self.open or self.high < self.close:
            raise ValueError("High must be >= open and close")
        if self.low > self.open or self.low > self.close:
            raise ValueError("Low must be <= open and close")
        if self.volume < 0:
            raise ValueError("Volume cannot be negative")
