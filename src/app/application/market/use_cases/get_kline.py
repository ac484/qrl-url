"""
Market use case: get kline data for QRL/USDT.
"""

from dataclasses import dataclass

from src.app.infrastructure.exchange.mexc.qrl.qrl_rest_client import QrlRestClient
from src.app.infrastructure.exchange.mexc.qrl.qrl_settings import QrlSettings


@dataclass
class GetKlineInput:
    interval: str = "1m"
    limit: int = 50


class GetKlineUseCase:
    """Fetch klines for the fixed QRL/USDT symbol."""

    def __init__(self, settings: QrlSettings | None = None):
        self._settings = settings or QrlSettings()

    async def execute(self, data: GetKlineInput | None = None) -> list:
        payload = data or GetKlineInput()
        client = QrlRestClient(self._settings)
        async with client as cli:
            return await cli.klines(interval=payload.interval, limit=payload.limit)
