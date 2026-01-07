"""System use case to expose an allocation trigger for schedulers."""

from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal
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
from src.app.infrastructure.exchange.mexc.qrl.qrl_rest_client import QrlRestClient


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
            best_bid, best_ask = await _top_of_book()
            quote_notional = Decimal("1")
            if side.value == "BUY":
                limit_price = best_ask
            else:
                limit_price = best_bid
            quantity = quote_notional / limit_price
            order = await svc.place_order(
                PlaceOrderRequest(
                    symbol=Symbol("QRLUSDT"),
                    side=side,
                    order_type=OrderType("LIMIT"),
                    quantity=Quantity(quantity),
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


async def _top_of_book() -> tuple[Decimal, Decimal]:
    """Fetch best bid/ask for QRL/USDT from the REST depth endpoint."""
    settings = MexcSettings()
    async with QrlRestClient(settings) as client:
        depth = await client.depth(limit=5)
    asks = depth.get("asks") or []
    bids = depth.get("bids") or []
    if not asks or not bids:
        raise ValueError("Depth is empty; cannot derive top-of-book price")
    best_ask = Decimal(asks[0][0])
    best_bid = Decimal(bids[0][0])
    return best_bid, best_ask
