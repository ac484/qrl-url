"""System use case to expose an allocation trigger for schedulers."""

from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal, ROUND_DOWN
from typing import Callable
from uuid import uuid4

from src.app.application.exchange.mexc_service import (
    MexcService,
    PlaceOrderRequest,
    SymbolFilters,
    build_mexc_service,
)
from src.app.domain.entities.account import Account
from src.app.domain.value_objects.order_type import OrderType
from src.app.domain.value_objects.price import Price
from src.app.domain.value_objects.quantity import Quantity
from src.app.domain.value_objects.side import Side
from src.app.domain.value_objects.symbol import Symbol
from src.app.domain.value_objects.time_in_force import TimeInForce
from src.app.infrastructure.exchange.mexc.settings import MexcSettings

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
            filters = await svc.get_symbol_filters(ALLOCATION_SYMBOL)
            limit_price = _select_limit_price(quote, side, filters)
            quantity = _size_for_notional(limit_price, filters)
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


def _select_limit_price(quote: Price, side: Side, filters: SymbolFilters) -> Decimal:
    """Choose a limit price from the top-of-book, falling back to last price when needed."""
    raw = quote.ask if side.value == "BUY" else quote.bid
    candidate = raw if raw > 0 else quote.last
    try:
        return _normalize_price(candidate, filters.tick_size)
    except ValueError as exc:
        if candidate == quote.last:
            raise ValueError("Allocation cannot proceed without a usable bid/ask/last price") from exc
        return _normalize_price(quote.last, filters.tick_size)


def _size_for_notional(limit_price: Decimal, filters: SymbolFilters) -> Quantity:
    """Size the order to approximately 1 USDT notional, rounded down."""
    raw_qty = filters.min_notional / limit_price
    qty = max(raw_qty, filters.min_qty)
    qty = qty.quantize(filters.step_size, rounding=ROUND_DOWN)
    if qty <= 0:
        raise ValueError("Computed allocation size is non-positive")
    return Quantity(qty)


def _normalize_price(value: Decimal, tick_size: Decimal) -> Decimal:
    """Align price to tick size and ensure it remains usable for order placement."""
    if value <= 0:
        raise ValueError("Allocation cannot proceed without a positive quote")
    normalized = value.quantize(tick_size, rounding=ROUND_DOWN)
    if normalized <= 0:
        raise ValueError("Allocation cannot proceed without a positive quote")
    return normalized
