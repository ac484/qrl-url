from src.app.application.ports.exchange_service import ExchangeServiceFactory, GetOrderRequest
from src.app.application.trading.use_cases.place_order import _serialize_order
from src.app.domain.value_objects.symbol import Symbol


class GetQrlOrder:
    """Fetch single QRL/USDT order details."""

    def __init__(self, exchange_factory: ExchangeServiceFactory):
        self._exchange_factory = exchange_factory

    async def execute(self, *, order_id: str | None = None, client_order_id: str | None = None) -> dict:
        request = GetOrderRequest(
            symbol=Symbol("QRLUSDT"), order_id=order_id, client_order_id=client_order_id
        )
        async with self._exchange_factory() as exchange:
            order = await exchange.get_order(request)
        return _serialize_order(order)
