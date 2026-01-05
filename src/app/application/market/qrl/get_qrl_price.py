from src.app.domain.value_objects.qrl_price import QrlPrice
from src.app.domain.value_objects.qrl_usdt_pair import QrlUsdtPair
from src.app.infrastructure.exchange.mexc.qrl.qrl_rest_client import QrlRestClient


class GetQrlPrice:
    """Fetch QRL/USDT price using the dedicated REST client."""

    def __init__(self, rest_client: QrlRestClient):
        self._client = rest_client

    async def execute(self) -> QrlPrice:
        async with self._client as client:
            ticker = await client.ticker_24h()
        last_price = ticker.get("lastPrice") or ticker.get("last")
        if last_price is None:
            raise ValueError("QRL price unavailable")
        return QrlPrice(last_price)
