from src.app.application.ports.exchange_service import ExchangeServiceFactory
from src.app.domain.value_objects.symbol import Symbol


class GetQrlKline:
    """Fetch QRL/USDT kline data."""

    def __init__(self, exchange_factory: ExchangeServiceFactory, interval: str = "1m", limit: int = 100):
        self._exchange_factory = exchange_factory
        self._interval = interval
        self._limit = limit

    async def execute(self) -> list:
        async with self._exchange_factory() as exchange:
            klines = await exchange.get_kline(
                Symbol("QRLUSDT"), interval=self._interval, limit=self._limit
            )
        return [
            [
                int(k.timestamp.value.timestamp() * 1000),
                str(k.open),
                str(k.high),
                str(k.low),
                str(k.close),
                str(k.volume),
            ]
            for k in klines
        ]
