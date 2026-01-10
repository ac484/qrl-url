from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class NormalizedBalances:
    """Normalized (USDT-denominated) balances for QRL and USDT including locked amounts."""

    qrl_value: Decimal
    usdt_value: Decimal

    def __post_init__(self) -> None:
        if self.qrl_value < 0 or self.usdt_value < 0:
            raise ValueError("Balances cannot be negative")

    @property
    def total_value(self) -> Decimal:
        """Aggregate notional value across QRL and USDT."""
        return self.qrl_value + self.usdt_value
