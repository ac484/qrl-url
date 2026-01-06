import asyncio
import sys
import unittest
from decimal import Decimal
from pathlib import Path
from typing import Any
from unittest import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock

try:
    import httpx  # noqa: F401
except ImportError:
    raise unittest.SkipTest("httpx not installed")

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.append(str(SRC))

from src.app.application.trading.use_cases.rebalance_qrl import (
    RebalanceQrlUseCase,
    RebalanceRequest,
)
from src.app.domain.entities.account import Account
from src.app.domain.value_objects.balance import Balance
from src.app.domain.value_objects.price import Price
from src.app.domain.value_objects.side import Side
from src.app.domain.value_objects.symbol import Symbol
from src.app.domain.value_objects.timestamp import Timestamp


class DummyMexcService:
    def __init__(self, price: Price, account: Account):
        self._price = price
        self._account = account
        self.place_order = AsyncMock(return_value=_fake_order())

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return None

    async def get_price(self, symbol: Symbol) -> Price:  # noqa: ARG002
        return self._price

    async def get_account(self) -> Account:
        return self._account


def _fake_order():
    from src.app.domain.value_objects.order_id import OrderId
    from src.app.domain.value_objects.order_status import OrderStatus
    from src.app.domain.value_objects.order_type import OrderType
    from src.app.domain.value_objects.quantity import Quantity
    from src.app.domain.value_objects.time_in_force import TimeInForce

    from src.app.domain.entities.order import Order

    return Order(
        order_id=OrderId("1"),
        symbol=Symbol("QRL/USDT"),
        side=Side("BUY"),
        order_type=OrderType("MARKET"),
        status=OrderStatus("NEW"),
        price=Decimal("1"),
        quantity=Quantity(Decimal("1")),
        created_at=Timestamp.from_epoch_ms(0),
        time_in_force=TimeInForce("IOC"),
    )


class TestRebalanceUseCase(IsolatedAsyncioTestCase):
    async def test_dry_run_returns_plan(self):
        price = Price.from_single(Decimal("1"))
        account = Account(
            can_trade=True,
            update_time=Timestamp.from_epoch_ms(0),
            balances=[Balance(asset="USDT", free=Decimal("100"), locked=Decimal("0")), Balance(asset="QRL", free=Decimal("0"), locked=Decimal("0"))],
        )

        def factory(_settings: Any):
            return DummyMexcService(price, account)

        use_case = RebalanceQrlUseCase(service_factory=factory)
        response = await use_case.execute(RebalanceRequest(dry_run=True))

        self.assertTrue(response.plan.target_ratio_qrl > 0)
        self.assertTrue(response.dry_run)

    async def test_live_executes_order(self):
        price = Price.from_single(Decimal("1"))
        account = Account(
            can_trade=True,
            update_time=Timestamp.from_epoch_ms(0),
            balances=[Balance(asset="USDT", free=Decimal("100"), locked=Decimal("0")), Balance(asset="QRL", free=Decimal("0"), locked=Decimal("0"))],
        )

        dummy_service = DummyMexcService(price, account)

        def factory(_settings: Any):
            return dummy_service

        use_case = RebalanceQrlUseCase(service_factory=factory)
        response = await use_case.execute(RebalanceRequest(dry_run=False))

        self.assertFalse(response.dry_run)
        dummy_service.place_order.assert_awaited()


if __name__ == "__main__":
    asyncio.run(unittest.main())
