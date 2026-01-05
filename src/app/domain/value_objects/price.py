from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal

from src.app.domain.value_objects.timestamp import Timestamp


@dataclass(frozen=True)
class Price:
    """Quote for a trading pair with bid/ask/last and timestamp."""

    bid: Decimal
    ask: Decimal
    last: Decimal
    timestamp: Timestamp

    def __post_init__(self):
        if self.bid <= 0 or self.ask <= 0 or self.last <= 0:
            raise ValueError("Price values must be positive")

    @classmethod
    def from_single(cls, value: Decimal, ts: datetime | None = None) -> "Price":
        """Construct a Price when only a single quote is available."""
        stamp = Timestamp(ts or datetime.now(timezone.utc))
        return cls(bid=value, ask=value, last=value, timestamp=stamp)
