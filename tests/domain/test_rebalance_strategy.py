import unittest
from decimal import Decimal
from datetime import datetime, timezone

from src.app.domain.strategies.rebalance import (
    DecisionContext,
    RebalanceConfig,
    build_rebalance_plan,
)
from src.app.domain.value_objects.price import Price


class RebalanceStrategyTests(unittest.TestCase):
    def test_within_tolerance_no_orders(self) -> None:
        price = Price(bid=Decimal("1"), ask=Decimal("1"), last=Decimal("1"), timestamp=self._ts())
        ctx = DecisionContext(price=price, qrl_free=Decimal("50"), usdt_free=Decimal("50"))
        cfg = RebalanceConfig(target_ratio_qrl=Decimal("0.5"), tolerance=Decimal("0.05"))

        plan = build_rebalance_plan(cfg, ctx)

        self.assertFalse(plan.has_action)
        self.assertEqual(plan.delta_value_usdt, Decimal("0"))

    def test_plan_buy_when_under_target(self) -> None:
        price = Price(bid=Decimal("1"), ask=Decimal("1"), last=Decimal("1"), timestamp=self._ts())
        ctx = DecisionContext(price=price, qrl_free=Decimal("10"), usdt_free=Decimal("90"))
        cfg = RebalanceConfig(target_ratio_qrl=Decimal("0.5"), tolerance=Decimal("0.01"), min_notional_usdt=Decimal("1"))

        plan = build_rebalance_plan(cfg, ctx)

        self.assertTrue(plan.has_action)
        self.assertEqual(plan.orders[0].side.value, "BUY")

    def test_skip_when_below_min_notional(self) -> None:
        price = Price(bid=Decimal("1"), ask=Decimal("1"), last=Decimal("1"), timestamp=self._ts())
        ctx = DecisionContext(price=price, qrl_free=Decimal("49"), usdt_free=Decimal("51"))
        cfg = RebalanceConfig(target_ratio_qrl=Decimal("0.5"), tolerance=Decimal("0.0"), min_notional_usdt=Decimal("5"))

        plan = build_rebalance_plan(cfg, ctx)

        self.assertFalse(plan.has_action)

    @staticmethod
    def _ts():
        from src.app.domain.value_objects.timestamp import Timestamp

        return Timestamp(datetime.now(timezone.utc))


if __name__ == "__main__":
    unittest.main()
