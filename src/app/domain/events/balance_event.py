from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class BalanceEvent:
    """Account balance snapshot/update."""

    asset: str
    free: Decimal
    locked: Decimal
    timestamp: int
