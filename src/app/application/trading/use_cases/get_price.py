from dataclasses import dataclass

from src.app.application.ports.exchange_service import ExchangeServiceFactory
from src.app.domain.value_objects.price import Price
from src.app.domain.value_objects.symbol import Symbol


def _serialize_price(price: Price) -> dict:
    return {
        "bid": str(price.bid),
        "ask": str(price.ask),
        "last": str(price.last),
        "timestamp": price.timestamp.value.isoformat(),
    }


@dataclass
class GetPriceUseCase:
    exchange_factory: ExchangeServiceFactory

    async def execute(self, symbol: str) -> dict:
        async with self.exchange_factory() as exchange:
            price = await exchange.get_price(Symbol(symbol))
        return _serialize_price(price)
