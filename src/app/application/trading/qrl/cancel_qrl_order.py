from src.app.infrastructure.exchange.mexc.qrl.qrl_rest_client import QrlRestClient


class CancelQrlOrder:
    """Cancel QRL/USDT order."""

    def __init__(self, rest_client: QrlRestClient):
        self._client = rest_client

    async def execute(self, *, order_id: str | None = None, client_order_id: str | None = None) -> dict:
        async with self._client as client:
            return await client.cancel_order(order_id=order_id, client_order_id=client_order_id)
