from decimal import Decimal

from src.app.domain.services.balance_comparison_rule import BalanceComparisonRule
from src.app.domain.services.slippage_analyzer import SlippageAnalyzer
from src.app.domain.value_objects.normalized_balances import NormalizedBalances
from src.app.domain.value_objects.quantity import Quantity
from src.app.domain.value_objects.side import Side


def test_balance_comparison_skips_within_tolerance():
    rule = BalanceComparisonRule(tolerance_pct=Decimal("1"))
    balances = NormalizedBalances(qrl_value=Decimal("1.0"), usdt_value=Decimal("1.02"))

    result = rule.evaluate(balances)

    assert result.action == "skip"
    assert result.preferred_side is None
    assert "tolerance" in (result.reason or "").lower()


def test_balance_comparison_prefers_sell_when_qrl_higher():
    rule = BalanceComparisonRule(target_ratio=Decimal("0.5"), tolerance_pct=Decimal("1"))

    result = rule.evaluate(NormalizedBalances(qrl_value=Decimal("3"), usdt_value=Decimal("1")))

    assert result.action == "trade"
    assert result.preferred_side == Side("SELL")
    assert result.diff > 0


def test_slippage_analyzer_allows_better_price():
    analyzer = SlippageAnalyzer(threshold_pct=Decimal("5"))

    assessment = analyzer.assess(
        side=Side("BUY"),
        desired_price=Decimal("1"),
        target_quantity=Quantity(Decimal("1")),
        fill_quantity=Decimal("1"),
        weighted_price=Decimal("0.9"),
    )

    assert assessment.is_acceptable
    assert assessment.slippage_pct < 0
    assert assessment.reason is None


def test_slippage_analyzer_rejects_insufficient_depth():
    analyzer = SlippageAnalyzer(threshold_pct=Decimal("5"))

    assessment = analyzer.assess(
        side=Side("SELL"),
        desired_price=Decimal("1"),
        target_quantity=Quantity(Decimal("1")),
        fill_quantity=Decimal("0.25"),
        weighted_price=Decimal("1"),
    )

    assert not assessment.is_acceptable
    assert assessment.reason is not None
    assert assessment.expected_fill == Decimal("0.25")
