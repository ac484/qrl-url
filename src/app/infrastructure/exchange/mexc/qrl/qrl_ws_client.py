from src.app.infrastructure.exchange.mexc.ws.mexc_ws_client import MexcWsClient
from src.app.domain.value_objects.qrl_usdt_pair import QrlUsdtPair


class QrlWsClient(MexcWsClient):
    """QRL/USDT專用 WS client，封裝訂閱 symbol。"""

    def __init__(self, base_ws_url: str):
        super().__init__(base_ws_url)

    async def subscribe_depth(self) -> None:
        await self.subscribe({"op": "sub.limit.depth", "symbol": QrlUsdtPair.symbol()})

    async def subscribe_trades(self) -> None:
        await self.subscribe({"op": "sub.personal.deals.v3", "symbol": QrlUsdtPair.symbol()})

    async def subscribe_orders(self) -> None:
        await self.subscribe({"op": "sub.personal.order.v3", "symbol": QrlUsdtPair.symbol()})
