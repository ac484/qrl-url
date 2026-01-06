from dataclasses import dataclass
from src.app.domain.entities.trading_pair import TradingPair
from src.app.domain.value_objects.price import Price


@dataclass(frozen=True)
class PriceUpdatedEvent:
    trading_pair: TradingPair
    price: Price
