from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class SlippageAssessment:
    """Result of pre-trade slippage analysis."""

    expected_fill: Decimal
    slippage_pct: Decimal
    is_acceptable: bool
    reason: str | None = None
