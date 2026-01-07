"""System use case to expose an allocation trigger for schedulers."""

from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal, ROUND_DOWN
from typing import Callable
from uuid import uuid4

from src.app.application.exchange.mexc_service import MexcService, PlaceOrderRequest, build_mexc_service
from src.app.domain.entities.account import Account
from src.app.domain.value_objects.order_type import OrderType
from src.app.domain.value_objects.price import Price
from src.app.domain.value_objects.quantity import Quantity
from src.app.domain.value_objects.side import Side
from src.app.domain.value_objects.symbol import Symbol
from src.app.domain.value_objects.time_in_force import TimeInForce
from src.app.infrastructure.exchange.mexc.settings import MexcSettings

TICK_SIZE = Decimal("0.0001")
QTY_PRECISION = Decimal("0.000001")
NOTIONAL_USDT = Decimal("1")
MIN_ORDER_QUANTITY = Decimal("0")
ALLOCATION_SYMBOL = Symbol("QRLUSDT")


@dataclass(frozen=True)
class AllocationResult:
    """Outcome returned when an allocation task is triggered."""

    request_id: str
    status: str
    executed_at: datetime
    action: str
    order_id: str


class AllocationUseCase:
    """Check QRL:USDT balance ratio and place a 1 USDT notional limit order at top-of-book."""

    def __init__(
        self,
        service_factory: Callable[[], MexcService] | None = None,
    ):
        self._service_factory = service_factory or (lambda: build_mexc_service(MexcSettings()))

    async def execute(self) -> AllocationResult:
        """Compare balances and submit a balancing order."""
        request_id = str(uuid4())
        async with self._service_factory() as svc:
            account = await svc.get_account()
            qrl_free, usdt_free = _extract_balances(account)
            side = Side("SELL") if qrl_free > usdt_free else Side("BUY")
            quote = await svc.get_price(ALLOCATION_SYMBOL)
            limit_price = _select_limit_price(quote, side)
            quantity = _size_for_notional(limit_price)
            order = await svc.place_order(
                PlaceOrderRequest(
                    symbol=ALLOCATION_SYMBOL,
                    side=side,
                    order_type=OrderType("LIMIT"),
                    quantity=quantity,
                    price=Price.from_single(limit_price),
                    time_in_force=TimeInForce("GTC"),
                )
            )

        return AllocationResult(
            request_id=request_id,
            status="ok",
            executed_at=datetime.now(timezone.utc),
            action=side.value,
            order_id=order.order_id.value,
        )


def _extract_balances(account: Account) -> tuple[Decimal, Decimal]:
    """Return (qrl, usdt) free balances with sane defaults."""
    qrl = Decimal("0")
    usdt = Decimal("0")
    for bal in account.balances:
        if bal.asset.upper() == "QRL":
            qrl = bal.free
        if bal.asset.upper() == "USDT":
            usdt = bal.free
    return qrl, usdt


def _select_limit_price(quote: Price, side: Side) -> Decimal:
    """Choose a limit price from the top-of-book, falling back to last price when needed."""
    raw = quote.ask if side.value == "BUY" else quote.bid
    candidate = raw if raw > 0 else quote.last
    try:
        return _normalize_price(candidate)
    except ValueError as exc:
        if candidate == quote.last:
            raise ValueError("Allocation cannot proceed without a usable bid/ask/last price") from exc
        return _normalize_price(quote.last)


def _size_for_notional(limit_price: Decimal) -> Quantity:
    """Size the order to approximately 1 USDT notional, rounded down."""
    qty = (NOTIONAL_USDT / limit_price).quantize(QTY_PRECISION, rounding=ROUND_DOWN)
    if qty <= MIN_ORDER_QUANTITY:
        raise ValueError("Computed allocation size is non-positive")
    return Quantity(qty)


def _normalize_price(value: Decimal) -> Decimal:
    """Align price to tick size and ensure it remains usable for order placement."""
    if value <= 0:
        raise ValueError("Allocation cannot proceed without a positive quote")
    normalized = value.quantize(TICK_SIZE, rounding=ROUND_DOWN)
    if normalized <= 0:
        raise ValueError("Allocation cannot proceed without a positive quote")
    return normalized
