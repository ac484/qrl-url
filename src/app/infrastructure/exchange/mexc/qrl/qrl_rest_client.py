from src.app.domain.value_objects.qrl_usdt_pair import QrlUsdtPair
from src.app.infrastructure.exchange.mexc.rest_client import MexcRestClient
from src.app.infrastructure.exchange.mexc.settings import MexcSettings


class QrlRestClient:
    """Wrapper to freeze symbol to QRL/USDT for all REST calls."""

    def __init__(self, settings: MexcSettings):
        self._settings = settings
        self._client = MexcRestClient(settings)

    async def __aenter__(self) -> "QrlRestClient":
        await self._client.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        await self._client.__aexit__(exc_type, exc, tb)

    async def ticker_24h(self) -> dict:
        return await self._client.ticker_24h(symbol=QrlUsdtPair.symbol())

    async def klines(self, *, interval: str, limit: int) -> list:
        return await self._client.klines(symbol=QrlUsdtPair.symbol(), interval=interval, limit=limit)

    async def depth(self, *, limit: int = 50) -> dict:
        return await self._client.depth(symbol=QrlUsdtPair.symbol(), limit=limit)

    async def market_trades(self, *, limit: int = 50) -> list:
        return await self._client.trades(symbol=QrlUsdtPair.symbol(), limit=limit)

    async def create_order(
        self,
        *,
        side: str,
        order_type: str,
        quantity: str,
        price: str | None,
        time_in_force: str | None,
        client_order_id: str | None,
    ) -> dict:
        return await self._client.create_order(
            symbol=QrlUsdtPair.symbol(),
            side=side,
            order_type=order_type,
            quantity=quantity,
            price=price,
            time_in_force=time_in_force,
            client_order_id=client_order_id,
        )

    async def get_order(self, *, order_id: str | None, client_order_id: str | None) -> dict:
        return await self._client.get_order(
            symbol=QrlUsdtPair.symbol(), order_id=order_id, client_order_id=client_order_id
        )

    async def cancel_order(self, *, order_id: str | None, client_order_id: str | None) -> dict:
        return await self._client.cancel_order(
            symbol=QrlUsdtPair.symbol(), order_id=order_id, client_order_id=client_order_id
        )
