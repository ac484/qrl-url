from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class NormalizedBalances:
    """Normalized balances for QRL and USDT with non-negative constraints."""

    qrl_free: Decimal
    usdt_free: Decimal

    def __post_init__(self) -> None:
        if self.qrl_free < 0 or self.usdt_free < 0:
            raise ValueError("Balances cannot be negative")
