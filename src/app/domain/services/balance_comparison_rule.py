from decimal import Decimal

from src.app.domain.value_objects.balance_comparison_result import BalanceComparisonResult
from src.app.domain.value_objects.normalized_balances import NormalizedBalances
from src.app.domain.value_objects.side import Side


class BalanceComparisonRule:
    """Decide whether to trade based on QRL vs USDT notional ratio."""

    def __init__(self, *, target_ratio: Decimal = Decimal("0.5"), tolerance_pct: Decimal = Decimal("1")):
        if target_ratio < 0 or target_ratio > 1:
            raise ValueError("target_ratio must be between 0 and 1")
        if tolerance_pct < 0:
            raise ValueError("tolerance_pct must be non-negative")
        self._target_ratio = target_ratio
        self._tolerance_pct = tolerance_pct

    def evaluate(self, balances: NormalizedBalances) -> BalanceComparisonResult:
        total_value = balances.total_value
        if total_value <= 0:
            return BalanceComparisonResult(
                qrl_free=balances.qrl_value,
                usdt_free=balances.usdt_value,
                diff=Decimal("0"),
                action="skip",
                preferred_side=None,
                reason="No balances to compare",
            )

        current_ratio = balances.qrl_value / total_value
        diff_pct = (current_ratio - self._target_ratio) * Decimal("100")
        if abs(diff_pct) <= self._tolerance_pct:
            return BalanceComparisonResult(
                qrl_free=balances.qrl_value,
                usdt_free=balances.usdt_value,
                diff=Decimal("0"),
                action="skip",
                preferred_side=None,
                reason=f"Within tolerance ({diff_pct:.4f}%)",
            )

        target_qrl_value = total_value * self._target_ratio
        diff_value = balances.qrl_value - target_qrl_value
        preferred_side = Side("SELL") if diff_value > 0 else Side("BUY")
        return BalanceComparisonResult(
            qrl_free=balances.qrl_value,
            usdt_free=balances.usdt_value,
            diff=diff_value,
            action="trade",
            preferred_side=preferred_side,
            reason=None,
        )
