from dataclasses import dataclass
from typing import List, Tuple

from app.domain.value_objects.price import Price
from app.domain.value_objects.quantity import Quantity
from app.domain.value_objects.symbol import Symbol


@dataclass(frozen=True)
class MarketDepthEvent:
    """
    Order book depth snapshot/update at a point in time.

    Notes:
        - Bids/asks are sorted by price on the exchange side.
        - Versions allow consumers to detect gaps and request replay.
    """

    symbol: Symbol
    bids: List[Tuple[Price, Quantity]]
    asks: List[Tuple[Price, Quantity]]
    event_type: str | None
    from_version: str | None
    to_version: str | None
