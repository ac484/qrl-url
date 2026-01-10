from src.app.application.ports.exchange_service import ExchangeServiceFactory
from src.app.application.market.use_cases.get_depth import _serialize_depth
from src.app.domain.value_objects.symbol import Symbol


class GetQrlDepth:
    """Fetch QRL/USDT order book snapshot."""

    def __init__(self, exchange_factory: ExchangeServiceFactory, limit: int = 50):
        self._exchange_factory = exchange_factory
        self._limit = limit

    async def execute(self) -> dict:
        async with self._exchange_factory() as exchange:
            book = await exchange.get_depth(Symbol("QRLUSDT"), limit=self._limit)
        return _serialize_depth(book)
