"""Trading use case: list open/closed orders."""

from src.app.application.ports.exchange_service import ExchangeServiceFactory
from src.app.application.trading.use_cases.place_order import _serialize_order
from src.app.domain.value_objects.symbol import Symbol


class ListOrdersUseCase:
    def __init__(self, exchange_factory: ExchangeServiceFactory):
        self._exchange_factory = exchange_factory

    async def execute(self, symbol: str | None = None) -> list[dict]:
        async with self._exchange_factory() as exchange:
            orders = await exchange.list_open_orders(Symbol(symbol) if symbol else None)
        return [_serialize_order(order) for order in orders]
