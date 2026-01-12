from datetime import datetime, timezone
from decimal import Decimal

import pytest

from src.app.application.trading.qrl.place_qrl_order import PlaceQrlOrder
from src.app.domain.entities.order import Order
from src.app.domain.value_objects.order_id import OrderId
from src.app.domain.value_objects.order_status import OrderStatus
from src.app.domain.value_objects.order_type import OrderType
from src.app.domain.value_objects.qrl_price import QrlPrice
from src.app.domain.value_objects.quantity import Quantity
from src.app.domain.value_objects.side import Side
from src.app.domain.value_objects.symbol import Symbol
from src.app.domain.value_objects.time_in_force import TimeInForce
from src.app.domain.value_objects.timestamp import Timestamp


class FakeExchange:
    def __init__(self):
        self.requests: list = []

    async def __aenter__(self) -> "FakeExchange":
        return self

    async def __aexit__(self, exc_type, exc, tb) -> bool:
        return False

    async def place_order(self, request):
        self.requests.append(request)
        return Order(
            order_id=OrderId("123"),
            symbol=request.symbol,
            side=request.side,
            order_type=request.order_type,
            status=OrderStatus("NEW"),
            price=QrlPrice(request.price.bid) if request.price else None,
            quantity=request.quantity,
            created_at=Timestamp(datetime.now(timezone.utc)),
            time_in_force=request.time_in_force,
            client_order_id=request.client_order_id,
        )


@pytest.mark.asyncio
async def test_place_qrl_order_accepts_primitives() -> None:
    exchange = FakeExchange()
    usecase = PlaceQrlOrder(lambda: exchange)

    result = await usecase.execute(
        side="BUY",
        order_type="LIMIT",
        price=Decimal("1.23456"),
        quantity=Decimal("10"),
        time_in_force="GTC",
        client_order_id="abc",
    )

    assert len(exchange.requests) == 1
    request = exchange.requests[0]
    assert request.symbol == Symbol("QRLUSDT")
    assert request.side == Side("BUY")
    assert request.price is not None
    assert request.price.bid == Decimal("1.2345")
    assert isinstance(request.quantity, Quantity)
    assert request.quantity.value == Decimal("10")

    assert result["price"] == "1.2345"
    assert result["quantity"] == "10"
    assert result["client_order_id"] == "abc"
