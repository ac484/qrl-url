"""
Market use case: recent public trades for QRL/USDT.
"""

from dataclasses import dataclass

from src.app.application.ports.exchange_service import ExchangeServiceFactory
from src.app.domain.value_objects.symbol import Symbol


@dataclass
class GetMarketTradesInput:
    limit: int = 50


class GetMarketTradesUseCase:
    """Fetch recent public trades for the fixed QRL/USDT symbol."""

    def __init__(self, exchange_factory: ExchangeServiceFactory):
        self._exchange_factory = exchange_factory

    async def execute(self, data: GetMarketTradesInput | None = None) -> list:
        payload = data or GetMarketTradesInput()
        async with self._exchange_factory() as exchange:
            return await exchange.get_market_trades(Symbol("QRLUSDT"), limit=payload.limit)
