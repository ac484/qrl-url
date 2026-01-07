from datetime import datetime, timezone
from decimal import Decimal, ROUND_DOWN
import pytest

from src.app.application.exchange.mexc_service import PlaceOrderRequest, SymbolFilters
from src.app.application.system.use_cases.allocation import AllocationUseCase
from src.app.domain.entities.account import Account
from src.app.domain.entities.order import Order
from src.app.domain.value_objects.balance import Balance
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
    def __init__(self, qrl_free: str, usdt_free: str, price: Price):
        self._qrl_free = Decimal(qrl_free)
        self._usdt_free = Decimal(usdt_free)
        self._price = price
        self.last_order_request: PlaceOrderRequest | None = None
        self.filters = SymbolFilters(
            tick_size=Decimal("0.0001"),
            step_size=Decimal("0.000001"),
            min_qty=Decimal("0.000001"),
            min_notional=Decimal("1"),
        )

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

    async def get_price(self, symbol: Symbol) -> Price:  # pragma: no cover - simple passthrough
        return self._price

    async def get_symbol_filters(self, symbol: Symbol) -> SymbolFilters:  # pragma: no cover
        return self.filters

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


def _make_price(bid: str, ask: str, last: str | None = None) -> Price:
    ts = Timestamp(datetime(2026, 1, 1, tzinfo=timezone.utc))
    last_value = Decimal(last) if last is not None else Decimal(ask)
    return Price(bid=Decimal(bid), ask=Decimal(ask), last=last_value, timestamp=ts)


@pytest.mark.asyncio
async def test_allocation_sells_when_qrl_exceeds_usdt():
    price = _make_price(bid="0.09876", ask="0.10123")
    service = FakeService(qrl_free="2", usdt_free="1", price=price)
    usecase = AllocationUseCase(service_factory=lambda: service)

    result = await usecase.execute()

    assert result.status == "ok"
    assert result.action == "SELL"
    assert result.order_id == "test-order"
    assert service.last_order_request is not None
    assert service.last_order_request.side.value == "SELL"
    limit_price = Decimal("0.09876").quantize(Decimal("0.0001"), rounding=ROUND_DOWN)
    expected_qty = (Decimal("1") / limit_price).quantize(Decimal("0.000001"), rounding=ROUND_DOWN)
    assert service.last_order_request.price is not None
    assert service.last_order_request.price.last == limit_price
    assert service.last_order_request.quantity.value == expected_qty


@pytest.mark.asyncio
async def test_allocation_buys_when_usdt_exceeds_qrl():
    price = _make_price(bid="0.12000", ask="0.12345")
    service = FakeService(qrl_free="0.5", usdt_free="5", price=price)
    usecase = AllocationUseCase(service_factory=lambda: service)

    result = await usecase.execute()

    assert result.status == "ok"
    assert result.action == "BUY"
    assert result.order_id == "test-order"
    assert service.last_order_request is not None
    assert service.last_order_request.side.value == "BUY"
    limit_price = Decimal("0.12345").quantize(Decimal("0.0001"), rounding=ROUND_DOWN)
    expected_qty = (Decimal("1") / limit_price).quantize(Decimal("0.000001"), rounding=ROUND_DOWN)
    assert service.last_order_request.price is not None
    assert service.last_order_request.price.last == limit_price
    assert service.last_order_request.quantity.value == expected_qty


@pytest.mark.asyncio
async def test_allocation_falls_back_to_last_price_when_top_of_book_missing():
    price = _make_price(bid="0.00000005", ask="0.00000005", last="0.25")
    service = FakeService(qrl_free="0.1", usdt_free="1.5", price=price)
    usecase = AllocationUseCase(service_factory=lambda: service)

    result = await usecase.execute()

    assert result.status == "ok"
    assert result.action == "BUY"
    assert service.last_order_request is not None
    limit_price = Decimal("0.25").quantize(Decimal("0.0001"), rounding=ROUND_DOWN)
    expected_qty = (Decimal("1") / limit_price).quantize(Decimal("0.000001"), rounding=ROUND_DOWN)
    assert service.last_order_request.price is not None
    assert service.last_order_request.price.last == limit_price
    assert service.last_order_request.quantity.value == expected_qty
