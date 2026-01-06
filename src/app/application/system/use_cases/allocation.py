"""System use case to expose an allocation trigger for schedulers."""

from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal
from typing import Callable
from uuid import uuid4

from pydantic import ValidationError

from src.app.application.exchange.mexc_service import MexcService, PlaceOrderRequest, build_mexc_service
from src.app.domain.entities.account import Account
from src.app.domain.value_objects.order_type import OrderType
from src.app.domain.value_objects.price import Price
from src.app.domain.value_objects.quantity import Quantity
from src.app.domain.value_objects.side import Side
from src.app.domain.value_objects.symbol import Symbol
from src.app.domain.value_objects.time_in_force import TimeInForce
from src.app.infrastructure.exchange.mexc.settings import MexcSettings


@dataclass(frozen=True)
class AllocationResult:
    """Outcome returned when an allocation task is triggered."""

    request_id: str
    status: str
    executed_at: datetime
    action: str
    order_id: str


class AllocationUseCase:
    """Check QRL:USDT balance ratio and place a 1-unit limit order at price 1."""

    def __init__(
        self,
        service_factory: Callable[[], MexcService] | None = None,
    ):
        self._service_factory = service_factory or (lambda: build_mexc_service(MexcSettings()))

    async def execute(self) -> AllocationResult:
        """Compare balances and submit a balancing order."""
        request_id = str(uuid4())
        executed_at = datetime.now(timezone.utc)

        try:
            service = self._service_factory()
        except ValidationError:
            return AllocationResult(
                request_id=request_id,
                status="skipped_missing_credentials",
                executed_at=executed_at,
                action="SKIP",
                order_id="N/A",
            )

        try:
            async with service as svc:
                account = await svc.get_account()
                qrl_free, usdt_free = _extract_balances(account)
                side = Side("SELL") if qrl_free > usdt_free else Side("BUY")
                order = await svc.place_order(
                    PlaceOrderRequest(
                        symbol=Symbol("QRLUSDT"),
                        side=side,
                        order_type=OrderType("LIMIT"),
                        quantity=Quantity(Decimal("1")),
                        price=Price.from_single(Decimal("1")),
                        time_in_force=TimeInForce("GTC"),
                    )
                )
        except Exception:
            return AllocationResult(
                request_id=request_id,
                status="error",
                executed_at=executed_at,
                action="FAILED",
                order_id="N/A",
            )

        return AllocationResult(
            request_id=request_id,
            status="ok",
            executed_at=executed_at,
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
