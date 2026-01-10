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
        qrl_locked: str = "0",
        usdt_locked: str = "0",
        bids: list[DepthLevel] | None = None,
        asks: list[DepthLevel] | None = None,
        price_bid: str = "1",
        price_ask: str = "1",
    ):
        self._qrl_free = Decimal(qrl_free)
        self._usdt_free = Decimal(usdt_free)
        self._qrl_locked = Decimal(qrl_locked)
        self._usdt_locked = Decimal(usdt_locked)
        self._book = OrderBook(bids=bids or [], asks=asks or [])
        self._price = Price(
            bid=Decimal(price_bid),
            ask=Decimal(price_ask),
            last=Decimal(price_bid),
            timestamp=Timestamp(datetime.now(timezone.utc)),
        )
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
                Balance(asset="QRL", free=self._qrl_free, locked=self._qrl_locked),
                Balance(asset="USDT", free=self._usdt_free, locked=self._usdt_locked),
            ],
        )

    async def get_depth(self, symbol: Symbol, limit: int = 50) -> OrderBook:
        return self._book

    async def get_price(self, symbol: Symbol) -> Price:
        return self._price

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
async def test_allocation_counts_locked_balances():
    # Locked QRL keeps ratio near target, so no new trade is placed.
    service = FakeService(qrl_free="0.1", qrl_locked="3", usdt_free="3")
    usecase = AllocationUseCase(service_factory=lambda: service)

    result = await usecase.execute()

    assert result.status == "skipped"
    assert result.order_id is None
    assert service.last_order_request is None


@pytest.mark.asyncio
async def test_allocation_rejects_on_slippage():
    service = FakeService(
        qrl_free="0.1",
        usdt_free="5",
        asks=[
            DepthLevel(price=Decimal("1"), quantity=Decimal("0.1")),
            DepthLevel(price=Decimal("2.5"), quantity=Decimal("1")),
        ],
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
        asks=[DepthLevel(price=Decimal("1.02"), quantity=Decimal("1.0"))],
        price_bid="1.01",
        price_ask="1.02",
    )
    usecase = AllocationUseCase(service_factory=lambda: service)

    result = await usecase.execute()

    assert result.status == "ok"
    assert result.action == "SELL"
    assert result.order_id == "test-order"
    assert result.expected_fill.quantize(Decimal("0.00000001")) == Decimal("0.50738916")
    assert service.last_order_request is not None
    assert service.last_order_request.side.value == "SELL"
    assert service.last_order_request.price is not None
    assert service.last_order_request.price.last == Decimal("1.02102")
    assert service.last_order_request.quantity.value.quantize(Decimal("0.00000001")) == Decimal("0.50738916")
    assert service.last_order_request.time_in_force == TimeInForce("GTC")


@pytest.mark.asyncio
async def test_allocation_skips_when_value_balanced_but_qty_not():
    # QRL qty > USDT qty, but price=0.5 makes values equal (1 USDT vs 1 USDT)
    service = FakeService(qrl_free="2", usdt_free="1", price_bid="0.5", price_ask="0.5")
    usecase = AllocationUseCase(service_factory=lambda: service)

    result = await usecase.execute()

    assert result.status == "skipped"
    assert service.last_order_request is None


@pytest.mark.asyncio
async def test_allocation_rejects_when_price_unavailable(monkeypatch):
    service = FakeService(qrl_free="0.5", usdt_free="1")

    async def raise_price(symbol: Symbol):
        raise RuntimeError("price failed")

    service.get_price = raise_price  # type: ignore
    usecase = AllocationUseCase(service_factory=lambda: service)

    result = await usecase.execute()

    assert result.status == "rejected"
    assert result.reason.startswith("Price unavailable")
    assert service.last_order_request is None
