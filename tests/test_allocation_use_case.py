from datetime import datetime, timezone
from decimal import Decimal

import pytest

from src.app.application.exchange.mexc_service import PlaceOrderRequest
from src.app.application.system.use_cases.allocation import AllocationUseCase
from src.app.domain.entities.account import Account
from src.app.domain.entities.order import Order
from src.app.domain.value_objects.balance import Balance
from src.app.domain.value_objects.order_book import DepthLevel, OrderBook
from src.app.domain.value_objects.order_id import OrderId
from src.app.domain.value_objects.order_status import OrderStatus
from src.app.domain.value_objects.order_type import OrderType
from src.app.domain.value_objects.price import Price
from src.app.domain.value_objects.quantity import Quantity
from src.app.domain.value_objects.side import Side
from src.app.domain.value_objects.symbol import Symbol
from src.app.domain.value_objects.time_in_force import TimeInForce
from src.app.domain.value_objects.timestamp import Timestamp


class FakeService:
    def __init__(
        self,
        qrl_free: str,
        usdt_free: str,
        *,
        bids: list[DepthLevel] | None = None,
        asks: list[DepthLevel] | None = None,
    ):
        self._qrl_free = Decimal(qrl_free)
        self._usdt_free = Decimal(usdt_free)
        self._book = OrderBook(bids=bids or [], asks=asks or [])
        self.last_order_request: PlaceOrderRequest | None = None

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return None

    async def get_account(self) -> Account:
        return Account(
            can_trade=True,
            update_time=Timestamp(datetime.now(timezone.utc)),
            balances=[
                Balance(asset="QRL", free=self._qrl_free, locked=Decimal("0")),
                Balance(asset="USDT", free=self._usdt_free, locked=Decimal("0")),
            ],
        )

    async def get_depth(self, symbol: Symbol, limit: int = 50) -> OrderBook:
        return self._book

    async def place_order(self, request: PlaceOrderRequest) -> Order:
        self.last_order_request = request
        return Order(
            order_id=OrderId("test-order"),
            symbol=request.symbol,
            side=request.side,
            order_type=request.order_type,
            status=OrderStatus("NEW"),
            price=request.price.last if request.price else Decimal("0"),
            quantity=request.quantity,
            created_at=Timestamp(datetime.now(timezone.utc)),
            time_in_force=request.time_in_force,
        )


@pytest.mark.asyncio
async def test_allocation_skips_when_balances_even():
    service = FakeService(qrl_free="1", usdt_free="1")
    usecase = AllocationUseCase(service_factory=lambda: service)

    result = await usecase.execute()

    assert result.status == "skipped"
    assert result.action == "SKIP"
    assert result.order_id is None
    assert service.last_order_request is None


@pytest.mark.asyncio
async def test_allocation_rejects_on_slippage():
    service = FakeService(
        qrl_free="0.1",
        usdt_free="5",
        asks=[DepthLevel(price=Decimal("2"), quantity=Decimal("1"))],
    )
    usecase = AllocationUseCase(service_factory=lambda: service, slippage_threshold_pct=Decimal("5"))

    result = await usecase.execute()

    assert result.status == "rejected"
    assert result.action == "REJECTED"
    assert result.order_id is None
    assert result.reason is not None
    assert service.last_order_request is None


@pytest.mark.asyncio
async def test_allocation_places_order_when_slippage_ok():
    service = FakeService(
        qrl_free="2",
        usdt_free="1",
        bids=[DepthLevel(price=Decimal("1.01"), quantity=Decimal("1.5"))],
    )
    usecase = AllocationUseCase(service_factory=lambda: service)

    result = await usecase.execute()

    assert result.status == "ok"
    assert result.action == "SELL"
    assert result.order_id == "test-order"
    assert result.expected_fill == Decimal("1")
    assert service.last_order_request is not None
    assert service.last_order_request.side.value == "SELL"
    assert service.last_order_request.price is not None
    assert service.last_order_request.price.last == Decimal("1")
    assert service.last_order_request.quantity.value == Decimal("1")
    assert service.last_order_request.time_in_force == TimeInForce("GTC")
