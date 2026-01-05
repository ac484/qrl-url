from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class Quantity:
    """Positive trade quantity."""

    value: Decimal

    def __post_init__(self):
        if self.value <= 0:
            raise ValueError("Quantity must be positive")
