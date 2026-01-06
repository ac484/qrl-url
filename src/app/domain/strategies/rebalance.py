from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal, ROUND_DOWN, getcontext
from typing import List

from src.app.domain.value_objects.price import Price
from src.app.domain.value_objects.qrl_price import QrlPrice
from src.app.domain.value_objects.qrl_quantity import QrlQuantity
from src.app.domain.value_objects.side import Side

getcontext().prec = 28


@dataclass(frozen=True)
class RebalanceConfig:
    """Strategy knobs for QRL/USDT rebalance."""

    target_ratio_qrl: Decimal = Decimal("0.5")  # portion of portfolio value in QRL
    tolerance: Decimal = Decimal("0.02")  # acceptable drift before trading
    min_notional_usdt: Decimal = Decimal("1")  # skip if trade value below this
    max_notional_usdt: Decimal = Decimal("2")  # cap per order to protect size
    replay_ttl_seconds: int = 300


@dataclass(frozen=True)
class DecisionContext:
    """Current portfolio snapshot required for sizing."""

    price: Price
    qrl_free: Decimal
    usdt_free: Decimal

    @property
    def qrl_value(self) -> Decimal:
        return (self.qrl_free * self.price.last).quantize(Decimal("0.00000001"))

    @property
    def total_value(self) -> Decimal:
        return (self.qrl_value + self.usdt_free).quantize(Decimal("0.00000001"))


@dataclass(frozen=True)
class PlannedOrder:
    """Single planned order for rebalance."""

    side: Side
    quantity: QrlQuantity
    price: QrlPrice
    reason: str = "rebalance"


@dataclass
class RebalancePlan:
    """Plan outcome with delta and orders."""

    target_ratio_qrl: Decimal
    current_ratio_qrl: Decimal
    delta_value_usdt: Decimal
    orders: List[PlannedOrder] = field(default_factory=list)

    @property
    def has_action(self) -> bool:
        return len(self.orders) > 0


def _within_band(current: Decimal, target: Decimal, tolerance: Decimal) -> bool:
    lower = target * (Decimal("1") - tolerance)
    upper = target * (Decimal("1") + tolerance)
    return lower <= current <= upper


def build_rebalance_plan(config: RebalanceConfig, context: DecisionContext) -> RebalancePlan:
    """
    Compute a rebalance plan:
    - If current ratio within tolerance, return empty plan.
    - Otherwise size a single market order to move toward target ratio.
    """
    if context.total_value <= 0:
        return RebalancePlan(
            target_ratio_qrl=config.target_ratio_qrl,
            current_ratio_qrl=Decimal("0"),
            delta_value_usdt=Decimal("0"),
            orders=[],
        )

    current_ratio = (context.qrl_value / context.total_value).quantize(
        Decimal("0.00000001")
    )

    if _within_band(current_ratio, config.target_ratio_qrl, config.tolerance):
        return RebalancePlan(
            target_ratio_qrl=config.target_ratio_qrl,
            current_ratio_qrl=current_ratio,
            delta_value_usdt=Decimal("0"),
            orders=[],
        )

    desired_qrl_value = (config.target_ratio_qrl * context.total_value).quantize(
        Decimal("0.00000001")
    )
    delta_value = (desired_qrl_value - context.qrl_value).quantize(Decimal("0.00000001"))

    abs_delta = delta_value.copy_abs()
    if abs_delta < config.min_notional_usdt:
        return RebalancePlan(
            target_ratio_qrl=config.target_ratio_qrl,
            current_ratio_qrl=current_ratio,
            delta_value_usdt=delta_value,
            orders=[],
        )

    capped_notional = min(abs_delta, config.max_notional_usdt)
    qty_decimal = (capped_notional / context.price.last).quantize(
        QrlQuantity.STEP_SIZE, rounding=ROUND_DOWN
    )

    # Enforce QRL quantity safety bounds
    try:
        qrl_qty = QrlQuantity(qty_decimal)
    except ValueError:
        return RebalancePlan(
            target_ratio_qrl=config.target_ratio_qrl,
            current_ratio_qrl=current_ratio,
            delta_value_usdt=delta_value,
            orders=[],
        )
    if qrl_qty.value <= 0:
        return RebalancePlan(
            target_ratio_qrl=config.target_ratio_qrl,
            current_ratio_qrl=current_ratio,
            delta_value_usdt=delta_value,
            orders=[],
        )

    side = Side("BUY") if delta_value > 0 else Side("SELL")
    planned_order = PlannedOrder(
        side=side,
        quantity=qrl_qty,
        price=QrlPrice(context.price.last),
        reason="rebalance_to_target",
    )

    return RebalancePlan(
        target_ratio_qrl=config.target_ratio_qrl,
        current_ratio_qrl=current_ratio,
        delta_value_usdt=delta_value,
        orders=[planned_order],
    )
