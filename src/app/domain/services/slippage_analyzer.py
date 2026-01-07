from decimal import Decimal

from src.app.domain.value_objects.quantity import Quantity
from src.app.domain.value_objects.side import Side
from src.app.domain.value_objects.slippage import SlippageAssessment


class SlippageAnalyzer:
    """Evaluate slippage against a threshold for the chosen side."""

    def __init__(self, threshold_pct: Decimal):
        if threshold_pct < 0:
            raise ValueError("Slippage threshold must be non-negative")
        self._threshold_pct = threshold_pct

    def assess(
        self,
        *,
        side: Side,
        desired_price: Decimal,
        target_quantity: Quantity,
        fill_quantity: Decimal,
        weighted_price: Decimal,
    ) -> SlippageAssessment:
        if fill_quantity <= 0:
            return SlippageAssessment(
                expected_fill=Decimal("0"),
                slippage_pct=Decimal("100"),
                is_acceptable=False,
                reason="No executable depth",
            )

        if fill_quantity < target_quantity.value:
            return SlippageAssessment(
                expected_fill=fill_quantity,
                slippage_pct=Decimal("100"),
                is_acceptable=False,
                reason="Insufficient depth for target quantity",
            )

        if desired_price <= 0:
            raise ValueError("Desired price must be positive")

        delta = weighted_price - desired_price if side.value == "BUY" else desired_price - weighted_price
        slippage_pct = (delta / desired_price) * Decimal("100")

        if delta <= 0:
            return SlippageAssessment(
                expected_fill=fill_quantity,
                slippage_pct=slippage_pct,
                is_acceptable=True,
                reason=None,
            )

        is_acceptable = slippage_pct <= self._threshold_pct
        reason = None if is_acceptable else "Slippage exceeds threshold"
        return SlippageAssessment(
            expected_fill=fill_quantity,
            slippage_pct=slippage_pct,
            is_acceptable=is_acceptable,
            reason=reason,
        )
