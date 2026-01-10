from dataclasses import asdict, dataclass
from typing import Any

from src.app.application.ports.exchange_service import ExchangeServiceFactory
from src.app.domain.value_objects.qrl_price import QrlPrice
from src.app.domain.value_objects.qrl_usdt_pair import QrlUsdtPair
from src.app.domain.value_objects.symbol import Symbol


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

    def __init__(self, exchange_factory: ExchangeServiceFactory):
        self._exchange_factory = exchange_factory

    async def execute(self) -> QrlPriceSnapshot:
        async with self._exchange_factory() as exchange:
            ticker = await exchange.get_ticker_24h(Symbol(QrlUsdtPair.symbol()))
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
