"""Trading use case: cancel existing order for QRL/USDT."""

from dataclasses import dataclass

from src.app.application.ports.exchange_service import (
    CancelOrderRequest,
    ExchangeServiceFactory,
)
from src.app.application.trading.use_cases.place_order import _serialize_order
from src.app.domain.value_objects.symbol import Symbol


@dataclass(frozen=True)
class CancelOrderInput:
    symbol: str
    order_id: str | None = None
    client_order_id: str | None = None


class CancelOrderUseCase:
    def __init__(self, exchange_factory: ExchangeServiceFactory):
        self._exchange_factory = exchange_factory

    async def execute(self, data: CancelOrderInput) -> dict:
        request = CancelOrderRequest(
            symbol=Symbol(data.symbol),
            order_id=data.order_id,
            client_order_id=data.client_order_id,
        )
        async with self._exchange_factory() as exchange:
            order = await exchange.cancel_order(request)
        return _serialize_order(order)
