from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
import sys

import pytest
from pydantic import ValidationError

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.app.application.exchange.mexc_service import PlaceOrderRequest
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
    def __init__(self, qrl_free: str, usdt_free: str):
        self._qrl_free = Decimal(qrl_free)
        self._usdt_free = Decimal(usdt_free)
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
async def test_allocation_sells_when_qrl_exceeds_usdt():
    service = FakeService(qrl_free="2", usdt_free="1")
    usecase = AllocationUseCase(service_factory=lambda: service)

    result = await usecase.execute()

    assert result.status == "ok"
    assert result.action == "SELL"
    assert result.order_id == "test-order"
    assert service.last_order_request is not None
    assert service.last_order_request.side.value == "SELL"
    assert service.last_order_request.price is not None
    assert service.last_order_request.price.last == Decimal("1")
    assert service.last_order_request.quantity.value == Decimal("1")


@pytest.mark.asyncio
async def test_allocation_buys_when_usdt_exceeds_qrl():
    service = FakeService(qrl_free="0.5", usdt_free="5")
    usecase = AllocationUseCase(service_factory=lambda: service)

    result = await usecase.execute()

    assert result.status == "ok"
    assert result.action == "BUY"
    assert result.order_id == "test-order"
    assert service.last_order_request is not None
    assert service.last_order_request.side.value == "BUY"
    assert service.last_order_request.price is not None
    assert service.last_order_request.price.last == Decimal("1")
    assert service.last_order_request.quantity.value == Decimal("1")


@pytest.mark.asyncio
async def test_allocation_skips_when_credentials_missing():
    validation_error = ValidationError.from_exception_data(
        title="MexcSettings",
        line_errors=[
            {
                "type": "missing",
                "loc": ("MEXC_API_KEY",),
                "msg": "Field required",
                "input": {},
            }
        ],
    )

    def _raising_factory():
        raise validation_error

    usecase = AllocationUseCase(service_factory=_raising_factory)

    result = await usecase.execute()

    assert result.status == "skipped_missing_credentials"
    assert result.action == "SKIP"
    assert result.order_id == "N/A"


class FailingService:
    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return None

    async def get_account(self):
        raise RuntimeError("boom")


@pytest.mark.asyncio
async def test_allocation_returns_error_when_service_raises():
    usecase = AllocationUseCase(service_factory=lambda: FailingService())

    result = await usecase.execute()

    assert result.status == "error"
    assert result.action == "FAILED"
    assert result.order_id == "N/A"
