"""
Market use case: get order book depth for QRL/USDT.
"""

from dataclasses import dataclass

from src.app.application.ports.exchange_service import ExchangeServiceFactory
from src.app.domain.value_objects.order_book import OrderBook
from src.app.domain.value_objects.symbol import Symbol


@dataclass
class GetDepthInput:
    limit: int = 50


class GetDepthUseCase:
    """Fetch aggregated depth for the fixed QRL/USDT symbol."""

    def __init__(self, exchange_factory: ExchangeServiceFactory):
        self._exchange_factory = exchange_factory

    async def execute(self, data: GetDepthInput | None = None) -> dict:
        payload = data or GetDepthInput()
        async with self._exchange_factory() as exchange:
            depth = await exchange.get_depth(Symbol("QRLUSDT"), limit=payload.limit)
        return _serialize_depth(depth)


def _serialize_depth(book: OrderBook) -> dict:
    return {
        "bids": [[str(level.price), str(level.quantity)] for level in book.bids],
        "asks": [[str(level.price), str(level.quantity)] for level in book.asks],
    }
