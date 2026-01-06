"""
Market use case: 24h stats for QRL/USDT.
"""

from dataclasses import dataclass

from src.app.infrastructure.exchange.mexc.qrl.qrl_rest_client import QrlRestClient
from src.app.infrastructure.exchange.mexc.qrl.qrl_settings import QrlSettings


@dataclass
class GetStats24hInput:
    include_timestamp: bool = True


class GetStats24hUseCase:
    """Fetch 24h statistics for the fixed QRL/USDT symbol."""

    def __init__(self, settings: QrlSettings | None = None):
        self._settings = settings or QrlSettings()

    async def execute(self, data: GetStats24hInput | None = None) -> dict:
        client = QrlRestClient(self._settings)
        async with client as cli:
            return await cli.ticker_24h()
