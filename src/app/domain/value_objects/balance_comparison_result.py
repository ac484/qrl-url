from dataclasses import dataclass
from decimal import Decimal

from src.app.domain.value_objects.side import Side


@dataclass(frozen=True)
class BalanceComparisonResult:
    """Outcome of balance comparison deciding whether to trade."""

    qrl_free: Decimal
    usdt_free: Decimal
    diff: Decimal
    action: str
    preferred_side: Side | None
    reason: str | None = None
