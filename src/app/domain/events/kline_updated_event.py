from dataclasses import dataclass
from typing import Iterable

from src.app.domain.entities.trading_pair import TradingPair
from src.app.domain.value_objects.kline import KLine


@dataclass(frozen=True)
class KLineUpdatedEvent:
    trading_pair: TradingPair
    klines: Iterable[KLine]
