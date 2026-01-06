"""
Market use case: recent public trades for QRL/USDT.
"""

from dataclasses import dataclass

from src.app.infrastructure.exchange.mexc.qrl.qrl_rest_client import QrlRestClient
from src.app.infrastructure.exchange.mexc.qrl.qrl_settings import QrlSettings


@dataclass
class GetMarketTradesInput:
    limit: int = 50


class GetMarketTradesUseCase:
    """Fetch recent public trades for the fixed QRL/USDT symbol."""

    def __init__(self, settings: QrlSettings | None = None):
        self._settings = settings or QrlSettings()

    async def execute(self, data: GetMarketTradesInput | None = None) -> list:
        payload = data or GetMarketTradesInput()
        client = QrlRestClient(self._settings)
        async with client as cli:
            return await cli.market_trades(limit=payload.limit)
