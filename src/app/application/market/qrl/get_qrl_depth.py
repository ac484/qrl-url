from src.app.domain.value_objects.qrl_usdt_pair import QrlUsdtPair
from src.app.infrastructure.exchange.mexc.qrl.qrl_rest_client import QrlRestClient


class GetQrlDepth:
    """Fetch QRL/USDT order book snapshot."""

    def __init__(self, rest_client: QrlRestClient, limit: int = 50):
        self._client = rest_client
        self._limit = limit

    async def execute(self) -> dict:
        async with self._client as client:
            return await client.depth(limit=self._limit)
