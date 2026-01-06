from dataclasses import dataclass
from typing import List

from src.app.application.exchange.mexc_service import MexcService, build_mexc_service
from src.app.domain.value_objects.kline import KLine
from src.app.domain.value_objects.symbol import Symbol
from src.app.infrastructure.exchange.mexc.settings import MexcSettings


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
    settings: MexcSettings | None = None

    async def execute(self, symbol: str, interval: str, limit: int = 100) -> List[dict]:
        service = build_mexc_service(self.settings or MexcSettings())
        async with service as svc:
            klines = await svc.get_kline(Symbol(symbol), interval=interval, limit=limit)
        return [_serialize_kline(k) for k in klines]
