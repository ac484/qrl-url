from datetime import datetime, timezone
from decimal import Decimal
from typing import Any, Iterable

from src.app.domain.entities.trading_pair import TradingPair
from src.app.domain.value_objects.kline import KLine
from src.app.domain.value_objects.price import Price
from src.app.domain.value_objects.timestamp import Timestamp
from src.app.infrastructure.exchange.mexc.rest_client import MexcRestClient


class MexcApiClient:
    """High-level client that maps REST responses to domain value objects."""

    def __init__(self, rest_client: MexcRestClient):
        self._rest_client = rest_client

    async def __aenter__(self) -> "MexcApiClient":
        await self._rest_client.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        await self._rest_client.__aexit__(exc_type, exc, tb)

    async def get_price(self, pair: TradingPair) -> Price:
        payload = await self._rest_client.ticker_24h(symbol=pair.symbol)
        bid = Decimal(payload.get("bidPrice", "0"))
        ask = Decimal(payload.get("askPrice", "0"))
        last = Decimal(payload.get("lastPrice", payload.get("last", "0")))
        ts_value = payload.get("closeTime") or payload.get("close_time") or int(datetime.now(tz=timezone.utc).timestamp() * 1000)
        timestamp = Timestamp(datetime.fromtimestamp(int(ts_value) / 1000, tz=timezone.utc))
        return Price(bid=bid, ask=ask, last=last, timestamp=timestamp)

    async def get_klines(self, pair: TradingPair, interval: str, limit: int = 100) -> list[KLine]:
        raw_list = await self._rest_client.klines(symbol=pair.symbol, interval=interval, limit=limit)
        klines: list[KLine] = []
        for item in raw_list:
            if not isinstance(item, Iterable):
                continue
            open_time = int(item[0])
            open_price = Decimal(item[1])
            high = Decimal(item[2])
            low = Decimal(item[3])
            close = Decimal(item[4])
            volume = Decimal(item[5])
            klines.append(KLine.from_raw(open_price, high, low, close, volume, interval, open_time))
        return klines
