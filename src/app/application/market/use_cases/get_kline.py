"""
Market use case: get kline data for QRL/USDT.
"""

from dataclasses import dataclass

from src.app.application.ports.exchange_service import ExchangeServiceFactory
from src.app.domain.value_objects.kline import KLine
from src.app.domain.value_objects.symbol import Symbol


@dataclass
class GetKlineInput:
    interval: str = "1m"
    limit: int = 50


class GetKlineUseCase:
    """Fetch klines for the fixed QRL/USDT symbol."""

    def __init__(self, exchange_factory: ExchangeServiceFactory):
        self._exchange_factory = exchange_factory

    async def execute(self, data: GetKlineInput | None = None) -> list:
        payload = data or GetKlineInput()
        async with self._exchange_factory() as exchange:
            klines = await exchange.get_kline(
                Symbol("QRLUSDT"), interval=payload.interval, limit=payload.limit
            )
        return [_serialize_kline(kline) for kline in klines]


def _serialize_kline(kline: KLine) -> dict:
    return {
        "open": str(kline.open),
        "high": str(kline.high),
        "low": str(kline.low),
        "close": str(kline.close),
        "volume": str(kline.volume),
        "interval": kline.interval,
        "timestamp": kline.timestamp.value.isoformat(),
    }
