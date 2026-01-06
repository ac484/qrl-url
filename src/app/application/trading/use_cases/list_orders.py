"""Trading use case: list open/closed orders."""

from src.app.application.exchange.mexc_service import MexcService, build_mexc_service
from src.app.application.trading.use_cases.place_order import _serialize_order
from src.app.domain.value_objects.symbol import Symbol
from src.app.infrastructure.exchange.mexc.settings import MexcSettings


class ListOrdersUseCase:
    settings: MexcSettings | None = None

    def __init__(self, settings: MexcSettings | None = None):
        self.settings = settings

    async def execute(self, symbol: str | None = None) -> list[dict]:
        service = build_mexc_service(self.settings or MexcSettings())
        async with service as svc:
            orders = await svc.list_open_orders(Symbol(symbol) if symbol else None)
        return [_serialize_order(order) for order in orders]
