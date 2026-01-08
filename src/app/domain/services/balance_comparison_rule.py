from decimal import Decimal

from src.app.domain.value_objects.balance_comparison_result import BalanceComparisonResult
from src.app.domain.value_objects.normalized_balances import NormalizedBalances
from src.app.domain.value_objects.side import Side


class BalanceComparisonRule:
    """Decide whether to trade based on QRL vs USDT free balances."""

    def __init__(self, tolerance: Decimal = Decimal("0.01")):
        self._tolerance = tolerance

    def evaluate(self, balances: NormalizedBalances) -> BalanceComparisonResult:
        diff = balances.qrl_free - balances.usdt_free
        if abs(diff) <= self._tolerance:
            return BalanceComparisonResult(
                qrl_free=balances.qrl_free,
                usdt_free=balances.usdt_free,
                diff=diff,
                action="skip",
                preferred_side=None,
                reason="Balances within tolerance",
            )

        preferred_side = Side("SELL") if diff > 0 else Side("BUY")
        return BalanceComparisonResult(
            qrl_free=balances.qrl_free,
            usdt_free=balances.usdt_free,
            diff=diff,
            action="trade",
            preferred_side=preferred_side,
            reason=None,
        )
