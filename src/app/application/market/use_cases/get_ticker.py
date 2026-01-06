"""
Market use case: get ticker for QRL/USDT.
"""

from dataclasses import dataclass

from src.app.infrastructure.exchange.mexc.qrl.qrl_rest_client import QrlRestClient
from src.app.infrastructure.exchange.mexc.qrl.qrl_settings import QrlSettings


@dataclass
class GetTickerInput:
    include_timestamp: bool = True


class GetTickerUseCase:
    """Fetch 24h ticker for the fixed QRL/USDT symbol."""

    def __init__(self, settings: QrlSettings | None = None):
        self._settings = settings or QrlSettings()

    async def execute(self, data: GetTickerInput | None = None) -> dict:
        client = QrlRestClient(self._settings)
        async with client as cli:
            return await cli.ticker_24h()
