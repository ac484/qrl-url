"""Trading use case: get single order."""

from dataclasses import dataclass

from src.app.application.exchange.mexc_service import GetOrderRequest, MexcService, build_mexc_service
from src.app.application.trading.use_cases.place_order import _serialize_order
from src.app.domain.value_objects.symbol import Symbol
from src.app.infrastructure.exchange.mexc.settings import MexcSettings


@dataclass
class GetOrderInput:
    symbol: str
    order_id: str | None = None
    client_order_id: str | None = None


class GetOrderUseCase:
    settings: MexcSettings | None = None

    def __init__(self, settings: MexcSettings | None = None):
        self.settings = settings

    async def execute(self, data: GetOrderInput) -> dict:
        request = GetOrderRequest(
            symbol=Symbol(data.symbol),
            order_id=data.order_id,
            client_order_id=data.client_order_id,
        )
        service = build_mexc_service(self.settings or MexcSettings())
        async with service as svc:
            order = await svc.get_order(request)
        return _serialize_order(order)
