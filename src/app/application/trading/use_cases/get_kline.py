from dataclasses import dataclass
from typing import List

from src.app.application.ports.exchange_service import ExchangeServiceFactory
from src.app.domain.value_objects.kline import KLine
from src.app.domain.value_objects.symbol import Symbol


def _serialize_kline(k: KLine) -> dict:
    return {
        "open": str(k.open),
        "high": str(k.high),
        "low": str(k.low),
        "close": str(k.close),
        "volume": str(k.volume),
        "interval": k.interval,
        "timestamp": k.timestamp.value.isoformat(),
    }


@dataclass
class GetKlineUseCase:
    exchange_factory: ExchangeServiceFactory

    async def execute(self, symbol: str, interval: str, limit: int = 100) -> List[dict]:
        async with self.exchange_factory() as exchange:
            klines = await exchange.get_kline(Symbol(symbol), interval=interval, limit=limit)
        return [_serialize_kline(k) for k in klines]
