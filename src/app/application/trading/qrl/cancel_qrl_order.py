from src.app.application.ports.exchange_service import CancelOrderRequest, ExchangeServiceFactory
from src.app.domain.value_objects.symbol import Symbol


class CancelQrlOrder:
    """Cancel QRL/USDT order."""

    def __init__(self, exchange_factory: ExchangeServiceFactory):
        self._exchange_factory = exchange_factory

    async def execute(self, *, order_id: str | None = None, client_order_id: str | None = None) -> dict:
        request = CancelOrderRequest(
            symbol=Symbol("QRLUSDT"), order_id=order_id, client_order_id=client_order_id
        )
        async with self._exchange_factory() as exchange:
            order = await exchange.cancel_order(request)
        return {
            "orderId": order.order_id.value,
            "symbol": order.symbol.value,
            "status": order.status.value,
        }
