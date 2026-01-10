"""
Market use case: get ticker for QRL/USDT.
"""

from dataclasses import dataclass

from src.app.application.ports.exchange_service import ExchangeServiceFactory
from src.app.domain.value_objects.symbol import Symbol


@dataclass
class GetTickerInput:
    include_timestamp: bool = True


class GetTickerUseCase:
    """Fetch 24h ticker for the fixed QRL/USDT symbol."""

    def __init__(self, exchange_factory: ExchangeServiceFactory):
        self._exchange_factory = exchange_factory

    async def execute(self, data: GetTickerInput | None = None) -> dict:
        async with self._exchange_factory() as exchange:
            return await exchange.get_ticker_24h(Symbol("QRLUSDT"))
