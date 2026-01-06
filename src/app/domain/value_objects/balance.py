from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class Balance:
    """Asset balance with free and locked amounts."""

    asset: str
    free: Decimal
    locked: Decimal

    def __post_init__(self):
        if not self.asset:
            raise ValueError("Asset symbol cannot be empty")
        if self.free < 0 or self.locked < 0:
            raise ValueError("Balance amounts cannot be negative")
