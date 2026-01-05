"""
Trading use case: get single order.
"""

from dataclasses import dataclass
from src.app.domain.entities.order import Order
from src.app.domain.value_objects.order_id import OrderId


@dataclass
class GetOrderInput:
    order_id: OrderId


@dataclass
class GetOrderOutput:
    order: Order | None = None


class GetOrderUseCase:
    def execute(self, data: GetOrderInput) -> GetOrderOutput:
        # TODO: fetch from port and map to domain
        return GetOrderOutput()
