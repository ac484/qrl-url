"""
Market use case: get order book depth for QRL/USDT.
"""

from dataclasses import dataclass

from src.app.infrastructure.exchange.mexc.qrl.qrl_rest_client import QrlRestClient
from src.app.infrastructure.exchange.mexc.qrl.qrl_settings import QrlSettings


@dataclass
class GetDepthInput:
    limit: int = 50


class GetDepthUseCase:
    """Fetch aggregated depth for the fixed QRL/USDT symbol."""

    def __init__(self, settings: QrlSettings | None = None):
        self._settings = settings or QrlSettings()

    async def execute(self, data: GetDepthInput | None = None) -> dict:
        payload = data or GetDepthInput()
        client = QrlRestClient(self._settings)
        async with client as cli:
            return await cli.depth(limit=payload.limit)
