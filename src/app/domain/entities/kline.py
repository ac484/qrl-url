from dataclasses import dataclass
from decimal import Decimal

from src.app.domain.value_objects.kline_interval import KlineInterval
from src.app.domain.value_objects.symbol import Symbol
from src.app.domain.value_objects.timestamp import Timestamp


@dataclass
class Kline:
    """Kline entity for QRL/USDT spot."""

    symbol: Symbol
    interval: KlineInterval
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: Decimal
    open_time: Timestamp
    close_time: Timestamp | None = None
