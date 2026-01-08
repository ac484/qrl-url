from dataclasses import dataclass

from src.app.domain.value_objects.price import Price
from src.app.domain.value_objects.quantity import Quantity
from src.app.domain.value_objects.side import Side
from src.app.domain.value_objects.symbol import Symbol
from src.app.domain.value_objects.time_in_force import TimeInForce


@dataclass(frozen=True)
class OrderCommand:
    """Order parameters selected after allocation analysis."""

    symbol: Symbol
    side: Side
    quantity: Quantity
    price: Price
    time_in_force: TimeInForce
