from dataclasses import asdict, dataclass
from typing import Any

from src.app.domain.value_objects.qrl_price import QrlPrice
from src.app.domain.value_objects.qrl_usdt_pair import QrlUsdtPair
from src.app.infrastructure.exchange.mexc.qrl.qrl_rest_client import QrlRestClient


@dataclass(frozen=True)
class QrlPriceSnapshot:
    bid: str | None
    ask: str | None
    last: str
    timestamp: int | None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class GetQrlPrice:
    """Fetch QRL/USDT price using the dedicated REST client."""

    def __init__(self, rest_client: QrlRestClient):
        self._client = rest_client

    async def execute(self) -> QrlPriceSnapshot:
        async with self._client as client:
            ticker = await client.ticker_24h()
        bid = ticker.get("bidPrice") or ticker.get("bid")
        ask = ticker.get("askPrice") or ticker.get("ask")
        last = ticker.get("lastPrice") or ticker.get("last")
        if last is None:
            raise ValueError("QRL price unavailable")
        price_vo = QrlPrice(last)
        timestamp = (
            ticker.get("time")
            or ticker.get("timestamp")
            or ticker.get("closeTime")
            or ticker.get("t")  # some SDKs return shorthand
        )
        return QrlPriceSnapshot(
            bid=str(bid) if bid is not None else None,
            ask=str(ask) if ask is not None else None,
            last=str(price_vo.value),
            timestamp=timestamp,
        )
