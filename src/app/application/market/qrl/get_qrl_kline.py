from src.app.domain.value_objects.qrl_usdt_pair import QrlUsdtPair
from src.app.infrastructure.exchange.mexc.qrl.qrl_rest_client import QrlRestClient


class GetQrlKline:
    """Fetch QRL/USDT kline data."""

    def __init__(self, rest_client: QrlRestClient, interval: str = "1m", limit: int = 100):
        self._client = rest_client
        self._interval = interval
        self._limit = limit

    async def execute(self) -> list:
        async with self._client as client:
            return await client.klines(interval=self._interval, limit=self._limit)
