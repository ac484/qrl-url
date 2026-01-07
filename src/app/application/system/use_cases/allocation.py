"""System use case to expose an allocation trigger for schedulers."""

from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal
from typing import Callable
from uuid import uuid4

from src.app.application.exchange.mexc_service import MexcService, PlaceOrderRequest, build_mexc_service
from src.app.domain.entities.account import Account
from src.app.domain.services.balance_comparison_rule import BalanceComparisonRule
from src.app.domain.services.depth_calculator import DepthCalculator
from src.app.domain.services.slippage_analyzer import SlippageAnalyzer
from src.app.domain.value_objects.balance_comparison_result import BalanceComparisonResult
from src.app.domain.value_objects.normalized_balances import NormalizedBalances
from src.app.domain.value_objects.order_command import OrderCommand
from src.app.domain.value_objects.order_type import OrderType
from src.app.domain.value_objects.price import Price
from src.app.domain.value_objects.quantity import Quantity
from src.app.domain.value_objects.side import Side
from src.app.domain.value_objects.slippage import SlippageAssessment
from src.app.domain.value_objects.symbol import Symbol
from src.app.domain.value_objects.time_in_force import TimeInForce
from src.app.infrastructure.exchange.mexc.settings import MexcSettings


class AllocationConfig:
    """Default configuration values for the allocation flow."""

    SYMBOL = Symbol("QRLUSDT")
    TIME_IN_FORCE = TimeInForce("GTC")
    LIMIT_PRICE = Decimal("1")
    TARGET_QUANTITY = Quantity(Decimal("1"))
    DEPTH_LIMIT = 20
    SLIPPAGE_THRESHOLD_PCT = Decimal("5")


@dataclass(frozen=True)
class AllocationResult:
    """Outcome returned when an allocation task is triggered."""

    request_id: str
    status: str
    executed_at: datetime
    action: str
    order_id: str | None
    reason: str | None = None
    slippage_pct: Decimal | None = None
    expected_fill: Decimal | None = None


class AllocationUseCase:
    """Check QRL:USDT balance ratio and place a limit order when slippage is acceptable."""

    def __init__(
        self,
        service_factory: Callable[[], MexcService] | None = None,
        *,
        depth_limit: int = AllocationConfig.DEPTH_LIMIT,
        slippage_threshold_pct: Decimal = AllocationConfig.SLIPPAGE_THRESHOLD_PCT,
        target_quantity: Quantity | None = None,
        limit_price: Decimal = AllocationConfig.LIMIT_PRICE,
    ):
        self._service_factory = service_factory or (lambda: build_mexc_service(MexcSettings()))
        self._comparison_rule = BalanceComparisonRule()
        self._depth_calculator = DepthCalculator()
        self._slippage_analyzer = SlippageAnalyzer(slippage_threshold_pct)
        self._depth_limit = depth_limit
        self._target_quantity = target_quantity or AllocationConfig.TARGET_QUANTITY
        self._limit_price = Decimal(limit_price)

    async def execute(self) -> AllocationResult:
        """Compare balances, evaluate depth/slippage, and submit a balancing order."""
        request_id = str(uuid4())
        executed_at = datetime.now(timezone.utc)
        async with self._service_factory() as svc:
            account = await svc.get_account()
            balances = _normalize_balances(account)
            comparison = self._comparison_rule.evaluate(balances)
            if comparison.action == "skip" or comparison.preferred_side is None:
                return _result_from_skip(request_id, executed_at, comparison)

            order_book = await svc.get_depth(AllocationConfig.SYMBOL, limit=self._depth_limit)
            filled, weighted_price = self._depth_calculator.compute(
                order_book, comparison.preferred_side, self._target_quantity
            )
            slippage = self._slippage_analyzer.assess(
                side=comparison.preferred_side,
                desired_price=self._limit_price,
                target_quantity=self._target_quantity,
                fill_quantity=filled,
                weighted_price=weighted_price,
            )
            if not slippage.is_acceptable:
                return _result_from_slippage(request_id, executed_at, slippage)

            command = _build_order_command(
                side=comparison.preferred_side, quantity=self._target_quantity, limit_price=self._limit_price
            )
            order = await svc.place_order(
                PlaceOrderRequest(
                    symbol=command.symbol,
                    side=command.side,
                    order_type=OrderType("LIMIT"),
                    quantity=command.quantity,
                    price=command.price,
                    time_in_force=command.time_in_force,
                )
            )

        return _result_from_success(
            request_id=request_id,
            executed_at=executed_at,
            slippage=slippage,
            side=command.side,
            order_id=order.order_id.value,
        )


def _normalize_balances(account: Account) -> NormalizedBalances:
    """Return normalized QRL/USDT balances with sane defaults."""
    qrl = Decimal("0")
    usdt = Decimal("0")
    for bal in account.balances:
        if bal.asset.upper() == "QRL":
            qrl = bal.free
        if bal.asset.upper() == "USDT":
            usdt = bal.free
    return NormalizedBalances(qrl_free=qrl, usdt_free=usdt)


def _build_order_command(*, side: Side, quantity: Quantity, limit_price: Decimal) -> OrderCommand:
    return OrderCommand(
        symbol=AllocationConfig.SYMBOL,
        side=side,
        quantity=quantity,
        price=Price.from_single(limit_price),
        time_in_force=AllocationConfig.TIME_IN_FORCE,
    )


def _result_from_skip(
    request_id: str, executed_at: datetime, comparison: BalanceComparisonResult
) -> AllocationResult:
    return AllocationResult(
        request_id=request_id,
        status="skipped",
        executed_at=executed_at,
        action="SKIP",
        order_id=None,
        reason=comparison.reason,
        slippage_pct=None,
        expected_fill=None,
    )


def _result_from_slippage(
    request_id: str, executed_at: datetime, slippage: SlippageAssessment
) -> AllocationResult:
    return AllocationResult(
        request_id=request_id,
        status="rejected",
        executed_at=executed_at,
        action="REJECTED",
        order_id=None,
        reason=slippage.reason,
        slippage_pct=slippage.slippage_pct,
        expected_fill=slippage.expected_fill,
    )


def _result_from_success(
    *,
    request_id: str,
    executed_at: datetime,
    slippage: SlippageAssessment,
    side: Side,
    order_id: str,
) -> AllocationResult:
    return AllocationResult(
        request_id=request_id,
        status="ok",
        executed_at=executed_at,
        action=side.value,
        order_id=order_id,
        reason=None,
        slippage_pct=slippage.slippage_pct,
        expected_fill=slippage.expected_fill,
    )
