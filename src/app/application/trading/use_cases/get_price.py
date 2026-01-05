from dataclasses import dataclass

from src.app.application.exchange.mexc_service import MexcService, build_mexc_service
from src.app.domain.value_objects.price import Price
from src.app.domain.value_objects.symbol import Symbol
from src.app.infrastructure.exchange.mexc.settings import MexcSettings


def _serialize_price(price: Price) -> dict:
    return {
        "bid": str(price.bid),
        "ask": str(price.ask),
        "last": str(price.last),
        "timestamp": price.timestamp.value.isoformat(),
    }


@dataclass
class GetPriceUseCase:
    settings: MexcSettings | None = None

    async def execute(self, symbol: str) -> dict:
        service = build_mexc_service(self.settings or MexcSettings())
        async with service as svc:
            price = await svc.get_price(Symbol(symbol))
        return _serialize_price(price)
