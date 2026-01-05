from src.app.domain.value_objects.qrl_price import QrlPrice
from src.app.domain.value_objects.qrl_quantity import QrlQuantity
from src.app.domain.value_objects.qrl_usdt_pair import QrlUsdtPair
from src.app.infrastructure.exchange.mexc.qrl.qrl_rest_client import QrlRestClient


class PlaceQrlOrder:
    """Place QRL/USDT order with fixed symbol and validated VOs."""

    def __init__(self, rest_client: QrlRestClient):
        self._client = rest_client

    async def execute(
        self,
        *,
        side: str,
        order_type: str,
        price: QrlPrice | None,
        quantity: QrlQuantity,
        time_in_force: str | None = "GTC",
        client_order_id: str | None = None,
    ) -> dict:
        async with self._client as client:
            return await client.create_order(
                side=side,
                order_type=order_type,
                price=str(price.value) if price else None,
                quantity=str(quantity.value),
                time_in_force=time_in_force,
                client_order_id=client_order_id,
            )
